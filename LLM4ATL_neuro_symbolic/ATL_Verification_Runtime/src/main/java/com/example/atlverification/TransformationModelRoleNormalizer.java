package com.example.atlverification;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Gives duplicate ATL2TM classifiers role-qualified names before the raw
 * Transformation Model is persisted. Ecore permits duplicate classifier names
 * through positional references such as {@code //Transition.2}; Pivot OCL
 * does not, because it resolves type names textually in one package.
 */
final class TransformationModelRoleNormalizer {
    private static final String PROVENANCE = "urn:llm4atl:provenance";
    private static final String ECORE = "http://www.eclipse.org/emf/2002/Ecore";
    private static final String PIVOT = "http://www.eclipse.org/emf/2002/Ecore/OCL/Pivot";
    private static final Set<String> COLLECTION_TYPES = Set.of(
            "Collection", "Set", "Bag", "Sequence", "OrderedSet");

    private TransformationModelRoleNormalizer() {
    }

    static void normalize(Path ecore) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(false);
        Document document = factory.newDocumentBuilder().parse(ecore.toFile());
        normalize(document);

        Transformer transformer = TransformerFactory.newInstance().newTransformer();
        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
        transformer.setOutputProperty(OutputKeys.ENCODING, "UTF-8");
        transformer.transform(new DOMSource(document), new StreamResult(ecore.toFile()));
    }

    private static void normalize(Document document) {
        NodeList classifierNodes = document.getElementsByTagName("eClassifiers");
        Map<String, List<Element>> byOriginalName = new LinkedHashMap<>();
        for (int i = 0; i < classifierNodes.getLength(); i++) {
            Element classifier = (Element) classifierNodes.item(i);
            byOriginalName.computeIfAbsent(classifier.getAttribute("name"), ignored -> new ArrayList<>())
                    .add(classifier);
        }

        Map<Element, String> renamed = new IdentityHashMap<>();
        for (Map.Entry<String, List<Element>> entry : byOriginalName.entrySet()) {
            List<Element> duplicates = entry.getValue();
            if ((duplicates.size() < 2 && !COLLECTION_TYPES.contains(entry.getKey()))
                    || entry.getKey().isBlank()) {
                continue;
            }
            Set<String> used = new LinkedHashSet<>();
            for (Element classifier : duplicates) {
                String suffix = switch (origin(classifier)) {
                    case "source" -> "__source";
                    case "target" -> "__target";
                    default -> "__trace";
                };
                String candidate = entry.getKey() + suffix;
                int serial = 2;
                while (!used.add(candidate)) candidate = entry.getKey() + suffix + serial++;
                renamed.put(classifier, candidate);
                classifier.setAttribute("name", candidate);
            }
        }

        if (!renamed.isEmpty()) {
            NodeList all = document.getElementsByTagName("*");
            for (int i = 0; i < all.getLength(); i++) {
                Element element = (Element) all.item(i);
                for (String attribute : List.of("eType", "eSuperTypes", "eOpposite")) {
                    if (element.hasAttribute(attribute)) {
                        element.setAttribute(attribute, rewriteTypeReferences(
                                element.getAttribute(attribute), byOriginalName, renamed));
                    }
                }
            }
            rewritePivotTypes(classifierNodes, byOriginalName, renamed);
        }
        dropUnsupportedPrimitiveNullFrames(document);
        setSchemaVersion(document, "2");
    }

    /**
     * USE/EFinder cannot soundly represent an ATL frame condition that says a
     * primitive target attribute was not assigned. The target metamodel copy
     * already relaxes its lower bound, so retaining {@code null_*} as a Sem
     * constraint would turn a backend limitation into a spurious UNSAT.
     *
     * <p>Reference-valued frames remain intact. Primitive target
     * multiplicities are reported by the wrapper as unsupported rather than
     * being sent to the solver.</p>
     */
    private static void dropUnsupportedPrimitiveNullFrames(Document document) {
        Map<String, Element> classifiers = classifiersByName(document);
        NodeList classifierNodes = document.getElementsByTagName("eClassifiers");
        for (int i = 0; i < classifierNodes.getLength(); i++) {
            Element trace = (Element) classifierNodes.item(i);
            if (!"trace".equals(origin(trace))) continue;
            Element pivot = annotation(trace, PIVOT);
            if (pivot == null) continue;
            String rule = detailValue(annotation(trace, PROVENANCE), "atlRule");
            if (rule.isBlank()) continue;
            for (Element output : children(trace, "eStructuralFeatures")) {
                if (!isReference(output)) continue;
                Element target = classifiers.get(typeName(output.getAttribute("eType")));
                if (target == null || !"target".equals(origin(target))) continue;

                String outputVariable = output.getAttribute("name");
                for (String attribute : targetAttributeNames(target, classifiers,
                        new LinkedHashSet<>())) {
                    removeConstraint(trace, pivot,
                            "null_" + rule + "_" + outputVariable + "_" + attribute);
                }
            }
        }
    }

    private static List<String> targetAttributeNames(Element target,
                                                     Map<String, Element> classifiers,
                                                     Set<String> visited) {
        String name = target.getAttribute("name");
        if (!visited.add(name)) return List.of();
        List<String> result = new ArrayList<>();
        for (Element feature : children(target, "eStructuralFeatures")) {
            if (isAttribute(feature)) result.add(feature.getAttribute("name"));
        }
        for (String supertype : target.getAttribute("eSuperTypes").trim().split("\\s+")) {
            if (supertype.isBlank()) continue;
            Element parent = classifiers.get(typeName(supertype));
            if (parent != null && "target".equals(origin(parent))) {
                result.addAll(targetAttributeNames(parent, classifiers, visited));
            }
        }
        return result;
    }

    private static Map<String, Element> classifiersByName(Document document) {
        Map<String, Element> result = new LinkedHashMap<>();
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element classifier = (Element) classifiers.item(i);
            result.put(classifier.getAttribute("name"), classifier);
        }
        return result;
    }

    private static boolean isAttribute(Element feature) {
        return feature.getAttribute("xsi:type").endsWith("EAttribute");
    }

    private static boolean isReference(Element feature) {
        return feature.getAttribute("xsi:type").endsWith("EReference");
    }

    private static String typeName(String reference) {
        if (reference == null || reference.isBlank()) return "";
        String token = reference.trim().split("\\s+")[0];
        int slash = token.lastIndexOf("//");
        String name = slash >= 0 ? token.substring(slash + 2) : token;
        int separator = name.indexOf('/');
        return separator >= 0 ? name.substring(0, separator) : name;
    }

    private static void removeConstraint(Element owner, Element pivot, String name) {
        Element body = detail(pivot, name);
        if (body == null) return;
        pivot.removeChild(body);
        removeWord(annotation(owner, ECORE), "constraints", name);
        removeWord(annotation(owner, PROVENANCE), "semConstraints", name);
    }

    private static void removeWord(Element annotation, String key, String value) {
        Element list = detail(annotation, key);
        if (list == null) return;
        List<String> words = new ArrayList<>(List.of(list.getAttribute("value").trim().split("\\s+")));
        words.removeIf(value::equals);
        list.setAttribute("value", String.join(" ", words));
    }

    private static void rewritePivotTypes(NodeList classifiers,
                                          Map<String, List<Element>> byOriginalName,
                                          Map<Element, String> renamed) {
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element classifier = (Element) classifiers.item(i);
            Element pivot = annotation(classifier, PIVOT);
            if (pivot == null) continue;

            String defaultRole = "target".equals(origin(classifier)) ? "target" : "source";
            boolean traceContext = "trace".equals(origin(classifier));
            Set<String> preconditions = new LinkedHashSet<>(words(detailValue(
                    annotation(classifier, PROVENANCE), "preConstraints")));
            for (Element detail : children(pivot, "details")) {
                String key = detail.getAttribute("key");
                String role = preconditions.contains(key) ? "source" : defaultRole;
                boolean matchConstraint = key.startsWith("match_");
                boolean generatedCounterexample = key.startsWith("__efinder_NOT_");
                detail.setAttribute("value", rewriteOclTypes(detail.getAttribute("value"),
                        byOriginalName, renamed, role, traceContext,
                        matchConstraint, generatedCounterexample));
            }
        }
    }

    private static String rewriteOclTypes(String expression,
                                          Map<String, List<Element>> byOriginalName,
                                          Map<Element, String> renamed,
                                          String role,
                                          boolean traceContext,
                                          boolean matchConstraint,
                                          boolean generatedCounterexample) {
        String rewritten = expression;
        for (Map.Entry<String, List<Element>> entry : byOriginalName.entrySet()) {
            if (entry.getValue().stream().noneMatch(renamed::containsKey)) continue;
            Pattern pattern = Pattern.compile("(?<![\\w.])" + Pattern.quote(entry.getKey()) + "(?![\\w])");
            Matcher matcher = pattern.matcher(rewritten);
            StringBuffer result = new StringBuffer();
            while (matcher.find()) {
                // Classifiers are renamed for OCL type resolution only.  A
                // matching token inside an OCL string is domain data, e.g.
                // ``self.e.name = 'Relationship'`` in an ATL rule guard.
                // Rewriting it to ``'Relationship__trace'`` changes the
                // rule's meaning and produces invalid counterexamples.
                if (insideOclStringLiteral(rewritten, matcher.start())
                        || collectionLiteral(rewritten, matcher)) {
                    matcher.appendReplacement(result, Matcher.quoteReplacement(matcher.group()));
                    continue;
                }
                boolean useTrace = matchConstraint
                        ? traceInMatch(rewritten, matcher)
                        : generatedCounterexample || (traceContext && traceOccurrence(rewritten, matcher));
                Element selected = selectByRole(entry.getValue(), role, useTrace);
                String replacement = selected == null ? null : renamed.get(selected);
                matcher.appendReplacement(result, Matcher.quoteReplacement(
                        replacement == null ? matcher.group() : replacement));
            }
            matcher.appendTail(result);
            rewritten = result.toString();
        }
        return rewritten;
    }

    /** Return whether {@code position} lies inside an OCL single-quoted string.
     * OCL escapes a quote by doubling it ({@code ''}).
     */
    private static boolean insideOclStringLiteral(String expression, int position) {
        boolean inside = false;
        for (int index = 0; index < position; index++) {
            if (expression.charAt(index) != '\'') continue;
            if (index + 1 < expression.length() && expression.charAt(index + 1) == '\'') {
                index++;
                continue;
            }
            inside = !inside;
        }
        return inside;
    }

    private static boolean traceInMatch(String expression, Matcher match) {
        String before = expression.substring(0, match.start());
        String after = expression.substring(match.end()).trim();
        if (after.matches("^\\.allInstances\\(\\)\\s*->\\s*one\\s*\\(.*")) return true;
        return before.matches("(?s).*->\\s*one\\s*\\(\\s*[A-Za-z_][A-Za-z0-9_]*\\s*:\\s*$");
    }

    private static boolean traceOccurrence(String expression, Matcher match) {
        String before = expression.substring(0, match.start()).trim();
        String after = expression.substring(match.end()).trim();
        boolean typeTest = before.endsWith("oclIsKindOf(") || before.endsWith("oclAsType(");
        return !typeTest && (after.startsWith(".allInstances(") || before.endsWith(":"));
    }

    private static Element selectByRole(List<Element> candidates, String role, boolean trace) {
        if (trace) {
            for (Element candidate : candidates) if ("trace".equals(origin(candidate))) return candidate;
        }
        for (Element candidate : candidates) if (role.equals(origin(candidate))) return candidate;
        for (Element candidate : candidates) if ("trace".equals(origin(candidate))) return candidate;
        return candidates.isEmpty() ? null : candidates.get(0);
    }

    private static boolean collectionLiteral(String expression, Matcher match) {
        int position = match.end();
        while (position < expression.length() && Character.isWhitespace(expression.charAt(position))) position++;
        return position < expression.length() && expression.charAt(position) == '{';
    }

    private static String rewriteTypeReferences(String value,
                                                Map<String, List<Element>> byOriginalName,
                                                Map<Element, String> renamed) {
        if (value == null || value.isBlank()) return value;
        String[] tokens = value.trim().split("\\s+");
        for (int i = 0; i < tokens.length; i++) tokens[i] = rewriteTypeReference(tokens[i], byOriginalName, renamed);
        return String.join(" ", tokens);
    }

    private static String rewriteTypeReference(String token,
                                               Map<String, List<Element>> byOriginalName,
                                               Map<Element, String> renamed) {
        String marker = token.startsWith("#//") ? "#//" : token.startsWith("//") ? "//" : null;
        if (marker == null) return token;
        String path = token.substring(marker.length());
        int slash = path.indexOf('/');
        String classifierReference = slash < 0 ? path : path.substring(0, slash);
        String rest = slash < 0 ? "" : path.substring(slash);
        int dot = classifierReference.lastIndexOf('.');
        int index = 0;
        String baseName = classifierReference;
        if (dot > 0 && classifierReference.substring(dot + 1).matches("\\d+")) {
            index = Integer.parseInt(classifierReference.substring(dot + 1));
            baseName = classifierReference.substring(0, dot);
        }
        List<Element> candidates = byOriginalName.get(baseName);
        if (candidates == null || index >= candidates.size()) return token;
        String replacement = renamed.get(candidates.get(index));
        return replacement == null ? token : marker + replacement + rest;
    }

    private static void setSchemaVersion(Document document, String version) {
        Element root = document.getDocumentElement();
        for (Element annotation : children(root, "eAnnotations")) {
            if (!PROVENANCE.equals(annotation.getAttribute("source"))) continue;
            for (Element detail : children(annotation, "details")) {
                if ("schemaVersion".equals(detail.getAttribute("key"))) detail.setAttribute("value", version);
            }
        }
    }

    private static String origin(Element classifier) {
        return detailValue(annotation(classifier, PROVENANCE), "origin");
    }

    private static Element annotation(Element owner, String source) {
        for (Element child : children(owner, "eAnnotations")) {
            if (source.equals(child.getAttribute("source"))) return child;
        }
        return null;
    }

    private static String detailValue(Element annotation, String key) {
        if (annotation == null) return "";
        for (Element detail : children(annotation, "details")) {
            if (key.equals(detail.getAttribute("key"))) return detail.getAttribute("value");
        }
        return "";
    }

    private static Element detail(Element annotation, String key) {
        if (annotation == null) return null;
        for (Element detail : children(annotation, "details")) {
            if (key.equals(detail.getAttribute("key"))) return detail;
        }
        return null;
    }

    private static List<String> words(String value) {
        return value == null || value.isBlank() ? List.of() : List.of(value.trim().split("\\s+"));
    }

    private static List<Element> children(Element parent, String name) {
        List<Element> result = new ArrayList<>();
        NodeList nodes = parent.getChildNodes();
        for (int i = 0; i < nodes.getLength(); i++) {
            Node node = nodes.item(i);
            if (node instanceof Element element && name.equals(element.getTagName())) result.add(element);
        }
        return result;
    }
}
