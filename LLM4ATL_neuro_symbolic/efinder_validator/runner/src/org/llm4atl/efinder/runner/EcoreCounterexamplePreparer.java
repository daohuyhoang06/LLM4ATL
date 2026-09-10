package org.llm4atl.efinder.runner;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Pattern;

import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

/**
 * Rewrites one embedded Ecore/Pivot invariant into its model-level negation.
 *
 * <p>The source Ecore is never changed. For a plain Ecore model EFinder
 * receives a copy with every original constraint except the selected one. For
 * an ATL2TM model, the copy contains the Sem/Pre premise and the negated
 * selected postcondition.</p>
 *
 * <p>For ATL2TM models carrying provenance, the rewrite implements the
 * verification query {@code Sem AND Pre AND NOT Post_i}: all semantic and
 * source-precondition constraints remain enabled, while target postconditions
 * other than the selected one are disabled.</p>
 */
final class EcoreCounterexamplePreparer {
    static final String ECORE_ANNOTATION = "http://www.eclipse.org/emf/2002/Ecore";
    static final String PIVOT_ANNOTATION = "http://www.eclipse.org/emf/2002/Ecore/OCL/Pivot";

    record Check(String context, String constraint) {
        static Check parse(String value) {
            String[] pieces = value.split("::", 2);
            if (pieces.length != 2 || pieces[0].isBlank() || pieces[1].isBlank()) {
                throw new IllegalArgumentException("--check must have the form EClass::constraint");
            }
            return new Check(pieces[0], pieces[1]);
        }
    }

    record PreparedModel(Path ecore, String generatedConstraint, String verificationFormula) {}

    private EcoreCounterexamplePreparer() {}

    static PreparedModel prepare(Path original, Path outputDir, Check check) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
        Document document = factory.newDocumentBuilder().parse(original.toFile());

        boolean atl2tm = hasAtl2tmProvenance(document);
        Element context = findClassifier(document, check.context(),
                atl2tm ? check.constraint() : null);
        if (context == null) {
            throw new IllegalArgumentException("EClass not found in Ecore: " + check.context());
        }
        Element ecore = annotation(context, ECORE_ANNOTATION);
        Element pivot = annotation(context, PIVOT_ANNOTATION);
        if (ecore == null || pivot == null) {
            throw new IllegalArgumentException("EClass " + check.context()
                    + " does not expose standard Ecore and Ecore/OCL/Pivot annotations");
        }

        Element propertyDetail = detail(pivot, check.constraint());
        Element constraintsDetail = detail(ecore, "constraints");
        if (constraintsDetail == null || propertyDetail == null) {
            throw new IllegalArgumentException("Constraint not found in " + check.context()
                    + ": " + check.constraint());
        }

        if (atl2tm && !isPostConstraint(context, check.constraint())) {
            throw new IllegalArgumentException("For Sem AND Pre AND NOT Post_i, --check must select a target postConstraints entry: "
                    + check.context() + "::" + check.constraint());
        }

        List<String> constraints = words(constraintsDetail.getAttribute("value"));
        if (!constraints.contains(check.constraint())) {
            throw new IllegalArgumentException("Constraint " + check.constraint()
                    + " is not enabled by the Ecore constraints annotation");
        }

        String generated = uniqueName(pivot, "__efinder_NOT_" + sanitize(check.constraint()));
        String property = propertyDetail.getAttribute("value");
        String bodyWithVariable = Pattern.compile("\\bself\\b").matcher(property).replaceAll("x");

        if (atl2tm) {
            rewriteAtl2tmConstraintLists(document, context, check, generated);
        } else {
            constraints.remove(check.constraint());
            constraints.add(generated);
            constraintsDetail.setAttribute("value", String.join(" ", constraints));
        }

        Map<Element, String> normalizedNames = atl2tm
                ? normalizeDuplicateClassifierNames(document)
                : Map.of();

        // Ecore2as reads every Pivot annotation detail, not only the names in
        // the Ecore "constraints" list. Retaining P here would solve P and
        // not(P) together and make every counterexample query UNSAT.
        if (!atl2tm) pivot.removeChild(propertyDetail);
        Element generatedDetail = document.createElement("details");
        generatedDetail.setAttribute("key", generated);
        String contextName = normalizedNames.getOrDefault(
                context, context.getAttribute("name"));
        generatedDetail.setAttribute("value", contextName
                + ".allInstances()->exists(x | not ("
                + bodyWithVariable + "))");
        pivot.appendChild(generatedDetail);

        Files.createDirectories(outputDir);
        Path rewritten = outputDir.resolve(original.getFileName().toString().replaceFirst(
                "(?i)\\.ecore$", "") + "__not_" + sanitize(check.context()) + "__"
                + sanitize(check.constraint()) + ".ecore");
        TransformerFactory transformers = TransformerFactory.newInstance();
        transformers.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
        Transformer transformer = transformers.newTransformer();
        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
        transformer.setOutputProperty(OutputKeys.ENCODING, "UTF-8");
        try (OutputStream stream = Files.newOutputStream(rewritten)) {
            transformer.transform(new DOMSource(document), new StreamResult(stream));
        }
        return new PreparedModel(rewritten, generated,
                atl2tm ? "Sem AND Pre AND NOT Post_i" : "NOT selected constraint with remaining constraints enabled");
    }

    private static boolean hasAtl2tmProvenance(Document document) {
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        for (int i = 0; i < classifiers.getLength(); i++) {
            if (annotation((Element) classifiers.item(i), "urn:llm4atl:provenance") != null) return true;
        }
        return false;
    }

    private static boolean isPostConstraint(Element classifier, String constraint) {
        return isTargetPostConstraint(classifier, constraint);
    }

    private static void rewriteAtl2tmConstraintLists(Document document, Element selectedContext,
                                                      Check check, String generated) {
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element classifier = (Element) classifiers.item(i);
            Element ecore = annotation(classifier, ECORE_ANNOTATION);
            Element pivot = annotation(classifier, PIVOT_ANNOTATION);
            Element constraintsDetail = ecore == null ? null : detail(ecore, "constraints");
            Element provenance = annotation(classifier, "urn:llm4atl:provenance");
            if (ecore == null || pivot == null || constraintsDetail == null || provenance == null) continue;

            List<String> original = words(constraintsDetail.getAttribute("value"));
            Set<String> allowed = new LinkedHashSet<>();
            allowed.addAll(words(detailValue(provenance, "semConstraints")));
            allowed.addAll(words(detailValue(provenance, "preConstraints")));
            if (classifier == selectedContext) allowed.add(generated);
            List<String> rewritten = new ArrayList<>();
            for (String name : original) {
                if (allowed.contains(name)) rewritten.add(name);
            }
            constraintsDetail.setAttribute("value", String.join(" ", rewritten));

            // Ecore2AS parses Pivot details even if they are absent from the
            // standard constraints list, so remove disabled postconditions too.
            for (Element detail : new ArrayList<>(children(pivot, "details"))) {
                if (original.contains(detail.getAttribute("key"))
                        && !allowed.contains(detail.getAttribute("key"))) {
                    pivot.removeChild(detail);
                }
            }
        }
    }

    private static String detailValue(Element annotation, String key) {
        Element detail = detail(annotation, key);
        return detail == null ? "" : detail.getAttribute("value");
    }

    /**
     * Resolve a classifier by its ATL2TM role when a postcondition is being
     * selected. Source and target metamodels commonly contain classifiers
     * with the same original name (for example Method and Parameter). A
     * name-only lookup returns the first one and can therefore select the
     * source classifier for a target postcondition.
     */
    private static Element findClassifier(Document document, String name,
                                          String postConstraint) {
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        Element firstMatch = null;
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element candidate = (Element) classifiers.item(i);
            if (name.equals(candidate.getAttribute("name"))) {
                if (firstMatch == null) {
                    firstMatch = candidate;
                }
                if (postConstraint != null
                        && isTargetPostConstraint(candidate, postConstraint)) {
                    return candidate;
                }
            }
        }
        return firstMatch;
    }

    private static boolean isTargetPostConstraint(Element classifier,
                                                  String constraint) {
        Element provenance = annotation(classifier, "urn:llm4atl:provenance");
        return provenance != null
                && "target".equals(detailValue(provenance, "origin"))
                && words(detailValue(provenance, "postConstraints"))
                        .contains(constraint);
    }

    /**
     * Ecore permits the serialized references {@code //Method} and
     * {@code //Method.1} for classifiers with the same name, but OCL/Pivot
     * resolves classifier names textually inside one package. Give duplicate
     * source/target classifiers internal names in the prepared copy and
     * update local Ecore references and Pivot OCL type references. The
     * originalName provenance detail remains unchanged for reporting.
     */
    private static Map<Element, String> normalizeDuplicateClassifierNames(
            Document document) {
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        Map<String, List<Element>> byName = new LinkedHashMap<>();
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element classifier = (Element) classifiers.item(i);
            byName.computeIfAbsent(classifier.getAttribute("name"),
                    ignored -> new ArrayList<>()).add(classifier);
        }

        Map<Element, String> normalized = new IdentityHashMap<>();
        for (Map.Entry<String, List<Element>> entry : byName.entrySet()) {
            List<Element> duplicates = entry.getValue();
            if (duplicates.size() < 2 || entry.getKey().isBlank()) continue;

            Set<String> used = new LinkedHashSet<>();
            for (Element classifier : duplicates) {
                String origin = origin(classifier);
                String suffix = "source".equals(origin) ? "__source"
                        : "target".equals(origin) ? "__target" : "__trace";
                String candidate = entry.getKey() + suffix;
                int serial = 2;
                while (!used.add(candidate)) {
                    candidate = entry.getKey() + suffix + serial++;
                }
                normalized.put(classifier, candidate);
                classifier.setAttribute("name", candidate);
            }
        }

        if (normalized.isEmpty()) return normalized;

        for (Map.Entry<String, List<Element>> entry : byName.entrySet()) {
            List<Element> candidates = entry.getValue();
            if (candidates.size() < 2) continue;
            for (int i = 0; i < candidates.size(); i++) {
                // The Ecore serializer uses //Name for the first classifier,
                // //Name.1 for the second, and so on.
                normalized.putIfAbsent(candidates.get(i),
                        candidates.get(i).getAttribute("name"));
            }
        }

        NodeList all = document.getElementsByTagName("*");
        for (int i = 0; i < all.getLength(); i++) {
            Element element = (Element) all.item(i);
            for (String attribute : List.of("eType", "eSuperTypes", "eOpposite")) {
                if (element.hasAttribute(attribute)) {
                    element.setAttribute(attribute,
                            rewriteTypeReferences(element.getAttribute(attribute), byName, normalized));
                }
            }
        }

        for (int i = 0; i < classifiers.getLength(); i++) {
            Element classifier = (Element) classifiers.item(i);
            String role = "target".equals(origin(classifier)) ? "target" : "source";
            Element pivot = annotation(classifier, PIVOT_ANNOTATION);
            if (pivot == null) continue;
            for (Element detail : children(pivot, "details")) {
                detail.setAttribute("value", rewriteOclTypes(
                        detail.getAttribute("value"), byName, normalized, role));
            }
        }
        return normalized;
    }

    private static String origin(Element classifier) {
        return detailValue(annotation(classifier, "urn:llm4atl:provenance"), "origin");
    }

    private static String rewriteTypeReferences(String value,
                                                Map<String, List<Element>> byName,
                                                Map<Element, String> normalized) {
        if (value == null || value.isBlank()) return value;
        String[] tokens = value.trim().split("\\s+");
        for (int i = 0; i < tokens.length; i++) {
            tokens[i] = rewriteTypeReference(tokens[i], byName, normalized);
        }
        return String.join(" ", tokens);
    }

    private static String rewriteTypeReference(String token,
                                               Map<String, List<Element>> byName,
                                               Map<Element, String> normalized) {
        String marker;
        if (token.startsWith("#//")) {
            marker = "#//";
        } else if (token.startsWith("//")) {
            marker = "//";
        } else {
            return token;
        }
        String path = token.substring(marker.length());
        int slash = path.indexOf('/');
        String classifierRef = slash < 0 ? path : path.substring(0, slash);
        String rest = slash < 0 ? "" : path.substring(slash);
        int dot = classifierRef.lastIndexOf('.');
        int index = 0;
        String baseName = classifierRef;
        if (dot > 0 && classifierRef.substring(dot + 1).matches("\\d+")) {
            index = Integer.parseInt(classifierRef.substring(dot + 1));
            baseName = classifierRef.substring(0, dot);
        }
        List<Element> candidates = byName.get(baseName);
        if (candidates == null || candidates.size() < 2 || index >= candidates.size()) {
            return token;
        }
        return marker + normalized.get(candidates.get(index)) + rest;
    }

    private static String rewriteOclTypes(String value,
                                          Map<String, List<Element>> byName,
                                          Map<Element, String> normalized,
                                          String role) {
        String rewritten = value;
        for (Map.Entry<String, List<Element>> entry : byName.entrySet()) {
            if (entry.getValue().size() < 2) continue;
            Element selected = selectByOrigin(entry.getValue(), role);
            if (selected == null) continue;
            String replacement = normalized.get(selected);
            if (replacement == null) continue;
            rewritten = rewritten.replaceAll("(?<![\\w.])"
                    + Pattern.quote(entry.getKey()) + "(?![\\w])",
                    replacement);
        }
        return rewritten;
    }

    private static Element selectByOrigin(List<Element> candidates, String role) {
        for (Element candidate : candidates) {
            if (role.equals(origin(candidate))) return candidate;
        }
        return candidates.isEmpty() ? null : candidates.get(0);
    }

    private static Element annotation(Element owner, String source) {
        for (Element child : children(owner, "eAnnotations")) {
            if (source.equals(child.getAttribute("source"))) {
                return child;
            }
        }
        return null;
    }

    private static Element detail(Element annotation, String key) {
        for (Element child : children(annotation, "details")) {
            if (key.equals(child.getAttribute("key"))) {
                return child;
            }
        }
        return null;
    }

    private static List<Element> children(Element parent, String name) {
        List<Element> result = new ArrayList<>();
        NodeList nodes = parent.getChildNodes();
        for (int i = 0; i < nodes.getLength(); i++) {
            Node node = nodes.item(i);
            if (node.getNodeType() == Node.ELEMENT_NODE && name.equals(node.getNodeName())) {
                result.add((Element) node);
            }
        }
        return result;
    }

    private static List<String> words(String value) {
        if (value == null || value.isBlank()) {
            return new ArrayList<>();
        }
        return new ArrayList<>(Arrays.asList(value.trim().split("\\s+")));
    }

    private static String uniqueName(Element pivot, String proposal) {
        String candidate = proposal;
        int suffix = 2;
        while (detail(pivot, candidate) != null) {
            candidate = proposal + "_" + suffix++;
        }
        return candidate;
    }

    static String sanitize(String value) {
        return Objects.requireNonNull(value).replaceAll("[^A-Za-z0-9_]", "_");
    }
}
