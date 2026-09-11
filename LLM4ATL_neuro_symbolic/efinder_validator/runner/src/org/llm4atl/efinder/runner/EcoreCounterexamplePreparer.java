package org.llm4atl.efinder.runner;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.stream.Stream;

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
    static final String PROVENANCE_ANNOTATION = "urn:llm4atl:provenance";
    private static final Set<String> SUPPORTED_ECORE_DATA_TYPES = Set.of(
            "EString", "EBoolean", "EByte", "EShort", "EInt", "ELong",
            "EFloat", "EDouble");
    private static final Map<String, String> STANDARD_PRIMITIVE_URIS = Map.of(
            "String", "http://www.eclipse.org/emf/2002/Ecore#//EString",
            "Boolean", "http://www.eclipse.org/emf/2002/Ecore#//EBoolean",
            "Byte", "http://www.eclipse.org/emf/2002/Ecore#//EByte",
            "Short", "http://www.eclipse.org/emf/2002/Ecore#//EShort",
            "Integer", "http://www.eclipse.org/emf/2002/Ecore#//EInt",
            "Long", "http://www.eclipse.org/emf/2002/Ecore#//ELong",
            "Float", "http://www.eclipse.org/emf/2002/Ecore#//EFloat",
            "Double", "http://www.eclipse.org/emf/2002/Ecore#//EDouble");
    /**
     * Names reserved by the OCL type system.  An EClass with one of these
     * names is renamed only in the prepared verification copy; otherwise an
     * expression such as {@code Set { ... }} may resolve to the EClass named
     * Set instead of the OCL collection type Set(T).
     */
    private static final Set<String> OCL_COLLECTION_TYPE_NAMES = Set.of(
            "Collection", "Set", "Bag", "Sequence", "OrderedSet");

    /*
     * Deliberately small input format for the repository's verification
     * properties. The actual invariant body is still standard Pivot OCL; this
     * pattern only finds its context and name. One file may contain many
     * invariants, each beginning with "context <EClass> inv <name>:".
     * A source-pre file may also contain a global declaration of the form
     * "global inv <name>:". Global preconditions are attached to the selected
     * target context so they cannot become vacuous when source classes are
     * absent.
     */
    private static final Pattern EXTERNAL_INVARIANT = Pattern.compile(
            "(?ms)^\\s*context\\s+(?:[A-Za-z_][A-Za-z0-9_]*::)?([A-Za-z_][A-Za-z0-9_]*)"
                    + "\\s+inv\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*:\\s*(.*?)(?=^\\s*(?:context|global)\\s+|\\z)");
    private static final Pattern EXTERNAL_GLOBAL_INVARIANT = Pattern.compile(
            "(?ms)^\\s*global\\s+inv\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*:\\s*(.*?)(?=^\\s*(?:context|global)\\s+|\\z)");
    /*
     * Canonical ATL2TM rendering of a String-to-Integer binding.  The
     * preparer deliberately accepts only this shape: rewriting an arbitrary
     * String expression would silently change semantics when the expression
     * is not backed by an EString feature in the source metamodel.
     */
    private static final Pattern STRING_TO_INTEGER_CONVERSION = Pattern.compile(
            "(?s)\\(let\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*=\\s*(.*?)\\s+in\\s*"
                    + "\\(if\\s+\\1\\.oclIsUndefined\\(\\)\\s+then\\s+''\\s+else\\s+"
                    + "\\1\\.([A-Za-z_][A-Za-z0-9_]*)\\s+endif\\s*\\)\\s*\\)"
                    + "\\.toInteger\\(\\)");
    /* Direct navigation form, for example self.source.value.toInteger(). */
    private static final Pattern DIRECT_STRING_TO_INTEGER_CONVERSION = Pattern.compile(
            "(?<![A-Za-z0-9_.])((?:self|[A-Za-z_][A-Za-z0-9_]*)(?:\\.[A-Za-z_][A-Za-z0-9_]*)*)"
                    + "\\.([A-Za-z_][A-Za-z0-9_]*)\\.toInteger\\(\\)");
    private static final Pattern OCL_CAST_TYPE = Pattern.compile(
            "\\.oclAsType\\(([A-Za-z_][A-Za-z0-9_]*)\\)");

    record Check(String context, String constraint) {
        static Check parse(String value) {
            String[] pieces = value.split("::", 2);
            if (pieces.length != 2 || pieces[0].isBlank() || pieces[1].isBlank()) {
                throw new IllegalArgumentException("--check must have the form EClass::constraint");
            }
            return new Check(pieces[0], pieces[1]);
        }
    }

    record PreparedModel(Path ecore, String generatedConstraint, String verificationFormula,
                         List<String> normalizedFeatures, List<String> abstractedFeatures,
                         String verificationContext) {}

    /** Raised before solving when an unsupported datatype affects Sem, Pre, or Post. */
    static final class UnsupportedFeatureException extends IllegalArgumentException {
        UnsupportedFeatureException(String message) {
            super(message);
        }
    }

    private enum ConstraintRole { TARGET_POST, SOURCE_PRE }

    private record ExternalInvariant(ConstraintRole role, String context, String name, String body, Path source) {}

    private EcoreCounterexamplePreparer() {}

    static PreparedModel prepare(Path original, Path outputDir, Check check) throws Exception {
        return prepare(original, outputDir, check, null);
    }

    /**
     * Prepares a model while optionally importing target postconditions and
     * source preconditions from standalone OCL files. A file named
     * {@code source-pre.ocl} contributes Pre; all other {@code .ocl} files
     * contribute target Post. A {@code global inv} in source-pre.ocl is
     * attached to the selected target context, making the source-domain
     * assumption active even when no source classifier instance exists. The
     * original ATL2TM Ecore is never modified.
     */
    static PreparedModel prepare(Path original, Path outputDir, Check check,
                                 Path externalConstraints) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
        Document document = factory.newDocumentBuilder().parse(original.toFile());

        boolean atl2tm = hasAtl2tmProvenance(document);
        List<ExternalInvariant> externalInvariants = List.of();
        if (externalConstraints != null) {
            if (!atl2tm) {
                throw new IllegalArgumentException("--constraints requires an ATL2TM Ecore model with provenance");
            }
            externalInvariants = injectExternalConstraints(document, externalConstraints);
        }
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

        if (externalConstraints != null) {
            injectGlobalPreconditions(document, context, externalInvariants);
        }
        if (atl2tm) {
            removeDanglingConstraintNames(document);
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
        String generatedValue = atl2tm
                ? generatedCounterexampleQuery(document, context, property)
                : null;

        if (atl2tm) {
            rewriteAtl2tmConstraintLists(document, context, check, generated);
        } else {
            constraints.remove(check.constraint());
            constraints.add(generated);
            constraintsDetail.setAttribute("value", String.join(" ", constraints));
        }

        // Ecore2as reads every Pivot annotation detail, not only the names in
        // the Ecore "constraints" list. Retaining P here would solve P and
        // not(P) together and make every counterexample query UNSAT.
        if (!atl2tm) pivot.removeChild(propertyDetail);
        Element generatedDetail = document.createElement("details");
        generatedDetail.setAttribute("key", generated);
        generatedDetail.setAttribute("value", atl2tm ? generatedValue
                : context.getAttribute("name") + ".allInstances()->exists(x | not ("
                + bodyWithVariable + "))");
        pivot.appendChild(generatedDetail);

        Map<Element, String> normalizedNames = atl2tm
                ? normalizeDuplicateClassifierNames(document)
                : Map.of();
        String contextName = normalizedNames.getOrDefault(
                context, context.getAttribute("name"));

        List<String> normalizedFeatures = mapPrimitiveDataTypes(document);
        normalizedFeatures.addAll(normalizeStringToIntegerConversions(document));
        List<String> abstractedFeatures = abstractIrrelevantUnsupportedFeatures(document);

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
                atl2tm ? "Sem AND Pre AND NOT Post_i" : "NOT selected constraint with remaining constraints enabled",
                List.copyOf(normalizedFeatures), List.copyOf(abstractedFeatures), contextName);
    }

    private static boolean hasAtl2tmProvenance(Document document) {
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        for (int i = 0; i < classifiers.getLength(); i++) {
            if (annotation((Element) classifiers.item(i), PROVENANCE_ANNOTATION) != null) return true;
        }
        return false;
    }

    /**
     * Imports external properties into the in-memory ATL2TM model. In addition
     * to the Pivot OCL body, ATL2TM provenance is updated so the regular
     * Sem AND Pre AND NOT Post_i path keeps source assumptions and selects
     * target properties correctly.
     */
    private static List<ExternalInvariant> injectExternalConstraints(Document document, Path location) throws IOException {
        List<ExternalInvariant> invariants = readExternalInvariants(location);
        for (ExternalInvariant invariant : invariants) {
            if (invariant.context() == null) continue;
            Element classifier = findClassifierByRole(document, invariant.context(), invariant.role());
            if (classifier == null) {
                String role = invariant.role() == ConstraintRole.TARGET_POST ? "target" : "source";
                throw new IllegalArgumentException("No " + role + " EClass named " + invariant.context()
                        + " for invariant " + invariant.name() + " in " + invariant.source());
            }

            Element ecore = ensureAnnotation(document, classifier, ECORE_ANNOTATION);
            Element pivot = ensureAnnotation(document, classifier, PIVOT_ANNOTATION);
            Element provenance = annotation(classifier, PROVENANCE_ANNOTATION);
            if (provenance == null) {
                throw new IllegalArgumentException("Missing ATL2TM provenance on " + invariant.context());
            }
            Element constraints = ensureDetail(document, ecore, "constraints");
            String provenanceKey = invariant.role() == ConstraintRole.TARGET_POST
                    ? "postConstraints" : "preConstraints";
            Element roleConstraints = ensureDetail(document, provenance, provenanceKey);
            Element body = detail(pivot, invariant.name());

            if (body != null && !body.getAttribute("value").equals(invariant.body())) {
                throw new IllegalArgumentException("Invariant " + invariant.context() + "::"
                        + invariant.name() + " is already defined with a different body in the ATL2TM model");
            }
            if (body == null) {
                body = document.createElement("details");
                body.setAttribute("key", invariant.name());
                body.setAttribute("value", invariant.body());
                pivot.appendChild(body);
            }
            appendWord(constraints, invariant.name());
            appendWord(roleConstraints, invariant.name());
        }
        return invariants;
    }

    private static void injectGlobalPreconditions(Document document, Element selectedContext,
                                                  List<ExternalInvariant> invariants) {
        for (ExternalInvariant invariant : invariants) {
            if (invariant.role() != ConstraintRole.SOURCE_PRE || invariant.context() != null) continue;

            Element ecore = ensureAnnotation(document, selectedContext, ECORE_ANNOTATION);
            Element pivot = ensureAnnotation(document, selectedContext, PIVOT_ANNOTATION);
            Element provenance = annotation(selectedContext, PROVENANCE_ANNOTATION);
            if (provenance == null) {
                throw new IllegalArgumentException("Missing ATL2TM provenance on selected target context "
                        + selectedContext.getAttribute("name"));
            }
            Element constraints = ensureDetail(document, ecore, "constraints");
            Element preConstraints = ensureDetail(document, provenance, "preConstraints");
            Element body = detail(pivot, invariant.name());
            if (body != null && !body.getAttribute("value").equals(invariant.body())) {
                throw new IllegalArgumentException("Global invariant " + invariant.name()
                        + " is already defined with a different body in " + invariant.source());
            }
            if (body == null) {
                body = document.createElement("details");
                body.setAttribute("key", invariant.name());
                body.setAttribute("value", invariant.body());
                pivot.appendChild(body);
            }
            appendWord(constraints, invariant.name());
            appendWord(preConstraints, invariant.name());
        }
    }

    /**
     * A bounded solver can introduce target instances that do not belong to
     * ATL's OUT resource. Counterexamples must therefore range over the
     * output references of rule traces rather than Target.allInstances().
     */
    private static String generatedCounterexampleQuery(Document document,
                                                        Element context,
                                                        String property) {
        List<TraceOutput> outputs = traceOutputsFor(document, context);
        if (outputs.isEmpty()) {
            throw new IllegalArgumentException("No ATL trace output creates target context "
                    + context.getAttribute("name"));
        }
        List<String> alternatives = new ArrayList<>();
        for (TraceOutput output : outputs) {
            String instance = "r." + output.reference();
            String instantiated = Pattern.compile("\\bself\\b")
                    .matcher(property).replaceAll(instance);
            alternatives.add(output.trace() + ".allInstances()->exists(r | not ("
                    + instantiated + "))");
        }
        return alternatives.size() == 1 ? alternatives.get(0)
                : "(" + String.join(" or ", alternatives) + ")";
    }

    private record TraceOutput(String trace, String reference) {}

    private static List<TraceOutput> traceOutputsFor(Document document,
                                                      Element context) {
        List<TraceOutput> result = new ArrayList<>();
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        String contextName = context.getAttribute("name");
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element trace = (Element) classifiers.item(i);
            if (!"trace".equals(origin(trace))) continue;
            for (Element feature : children(trace, "eStructuralFeatures")) {
                if (!isReference(feature)) continue;
                Element outputType = classifierForTypeReference(document, typeReference(feature));
                if (outputType != null && "target".equals(origin(outputType))
                        && isTargetSubtypeOrSame(document, outputType, contextName)) {
                    result.add(new TraceOutput(trace.getAttribute("name"),
                            feature.getAttribute("name")));
                }
            }
        }
        return result;
    }

    private static boolean isReference(Element feature) {
        return feature.getAttribute("xsi:type").endsWith("EReference");
    }

    /** Resolve //Name and //Name.1 using the Ecore duplicate-classifier index. */
    private static Element classifierForTypeReference(Document document, String reference) {
        if (reference == null || reference.isBlank()) return null;
        int marker = reference.lastIndexOf("#//");
        if (marker < 0) marker = reference.lastIndexOf("//");
        if (marker < 0) return null;
        String path = reference.substring(marker + (reference.startsWith("#//", marker) ? 3 : 2));
        int slash = path.indexOf('/');
        String classifierReference = slash < 0 ? path : path.substring(0, slash);
        int dot = classifierReference.lastIndexOf('.');
        int index = 0;
        String name = classifierReference;
        if (dot > 0 && classifierReference.substring(dot + 1).matches("\\d+")) {
            index = Integer.parseInt(classifierReference.substring(dot + 1));
            name = classifierReference.substring(0, dot);
        }
        List<Element> candidates = new ArrayList<>();
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element candidate = (Element) classifiers.item(i);
            if (name.equals(candidate.getAttribute("name"))) candidates.add(candidate);
        }
        return index < candidates.size() ? candidates.get(index) : null;
    }

    private static boolean isTargetSubtypeOrSame(Document document, Element candidate,
                                                  String required) {
        if (required.equals(candidate.getAttribute("name"))) return true;
        return isTargetSubtypeOf(document, candidate, required,
                new LinkedHashSet<>());
    }

    private static boolean isTargetSubtypeOf(Document document, Element classifier,
                                             String required, Set<String> visited) {
        String name = classifier.getAttribute("name");
        if (!visited.add(name)) return false;
        for (String supertype : words(classifier.getAttribute("eSuperTypes"))) {
            String supertypeName = typeName(supertype);
            if (required.equals(supertypeName)) return true;
            Element parent = findClassifierByRole(document, supertypeName,
                    ConstraintRole.TARGET_POST);
            if (parent != null && isTargetSubtypeOf(document, parent, required, visited)) {
                return true;
            }
        }
        return false;
    }

    static List<Check> externalChecks(Path location) throws IOException {
        List<Check> checks = new ArrayList<>();
        for (ExternalInvariant invariant : readExternalInvariants(location)) {
            if (invariant.role() != ConstraintRole.TARGET_POST || invariant.context() == null) continue;
            Check check = new Check(invariant.context(), invariant.name());
            if (!checks.contains(check)) checks.add(check);
        }
        return checks;
    }

    private static List<ExternalInvariant> readExternalInvariants(Path location) throws IOException {
        if (!Files.exists(location)) {
            throw new IllegalArgumentException("Constraints path does not exist: " + location);
        }
        List<Path> files;
        if (Files.isDirectory(location)) {
            try (Stream<Path> entries = Files.walk(location)) {
                files = entries.filter(Files::isRegularFile)
                        .filter(path -> path.getFileName().toString().toLowerCase().endsWith(".ocl"))
                        .sorted(Comparator.comparing(Path::toString))
                        .toList();
            }
        } else {
            files = List.of(location);
        }
        if (files.isEmpty()) {
            throw new IllegalArgumentException("No .ocl files found in constraints path: " + location);
        }

        List<ExternalInvariant> invariants = new ArrayList<>();
        for (Path file : files) {
            ConstraintRole role = file.getFileName().toString().equalsIgnoreCase("source-pre.ocl")
                    ? ConstraintRole.SOURCE_PRE : ConstraintRole.TARGET_POST;
            String text = Files.readString(file, StandardCharsets.UTF_8);
            var matcher = EXTERNAL_INVARIANT.matcher(text);
            int count = 0;
            while (matcher.find()) {
                String body = matcher.group(3).trim();
                if (body.endsWith(";")) body = body.substring(0, body.length() - 1).trim();
                if (body.isEmpty()) {
                    throw new IllegalArgumentException("Empty body for invariant " + matcher.group(2)
                            + " in " + file);
                }
                invariants.add(new ExternalInvariant(role, matcher.group(1), matcher.group(2), body, file));
                count++;
            }
            var globalMatcher = EXTERNAL_GLOBAL_INVARIANT.matcher(text);
            while (globalMatcher.find()) {
                if (role != ConstraintRole.SOURCE_PRE) {
                    throw new IllegalArgumentException("global invariants are allowed only in source-pre.ocl: " + file);
                }
                String body = globalMatcher.group(2).trim();
                if (body.endsWith(";")) body = body.substring(0, body.length() - 1).trim();
                if (body.isEmpty()) {
                    throw new IllegalArgumentException("Empty body for global invariant " + globalMatcher.group(1)
                            + " in " + file);
                }
                invariants.add(new ExternalInvariant(role, null, globalMatcher.group(1), body, file));
                count++;
            }
            if (count == 0) {
                throw new IllegalArgumentException("No supported 'context <EClass> inv <name>:' or 'global inv <name>:' declaration in " + file);
            }
        }
        return invariants;
    }

    private static Element findClassifierByRole(Document document, String name, ConstraintRole role) {
        String expectedOrigin = role == ConstraintRole.TARGET_POST ? "target" : "source";
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element classifier = (Element) classifiers.item(i);
            if (name.equals(classifier.getAttribute("name")) && expectedOrigin.equals(origin(classifier))) {
                return classifier;
            }
        }
        return null;
    }

    private static Element ensureAnnotation(Document document, Element owner, String source) {
        Element annotation = annotation(owner, source);
        if (annotation != null) return annotation;
        annotation = document.createElement("eAnnotations");
        annotation.setAttribute("source", source);
        Node first = owner.getFirstChild();
        owner.insertBefore(annotation, first);
        return annotation;
    }

    private static Element ensureDetail(Document document, Element annotation, String key) {
        Element existing = detail(annotation, key);
        if (existing != null) return existing;
        Element created = document.createElement("details");
        created.setAttribute("key", key);
        created.setAttribute("value", "");
        annotation.appendChild(created);
        return created;
    }

    private static void appendWord(Element detail, String value) {
        List<String> values = words(detail.getAttribute("value"));
        if (!values.contains(value)) values.add(value);
        detail.setAttribute("value", String.join(" ", values));
    }

    /**
     * ATL2TM can advertise a generated constraint name even when its lazy
     * detail rule produced no body (for example a mutex with no concrete
     * overlap). Ecore2AS treats the name as an invariant and fails with
     * "Missing specification body". Remove only dangling names from the
     * temporary EFinder copy; constraints with a Pivot body are unchanged.
     */
    private static void removeDanglingConstraintNames(Document document) {
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element classifier = (Element) classifiers.item(i);
            Element pivot = annotation(classifier, PIVOT_ANNOTATION);
            if (pivot == null) continue;

            Set<String> pivotKeys = new LinkedHashSet<>();
            for (Element pivotDetail : children(pivot, "details")) {
                pivotKeys.add(pivotDetail.getAttribute("key"));
            }

            Element ecore = annotation(classifier, ECORE_ANNOTATION);
            removeDanglingWords(detail(ecore, "constraints"), pivotKeys);
            Element provenance = annotation(classifier, PROVENANCE_ANNOTATION);
            removeDanglingWords(detail(provenance, "semConstraints"), pivotKeys);
            removeDanglingWords(detail(provenance, "preConstraints"), pivotKeys);
            removeDanglingWords(detail(provenance, "postConstraints"), pivotKeys);
        }
    }

    private static void removeDanglingWords(Element list, Set<String> pivotKeys) {
        if (list == null) return;
        List<String> retained = new ArrayList<>();
        for (String name : words(list.getAttribute("value"))) {
            if (pivotKeys.contains(name)) retained.add(name);
        }
        list.setAttribute("value", String.join(" ", retained));
    }

    /**
     * Maps repository-local primitive aliases to standard Ecore datatypes in
     * the temporary copy. For example, a local PrimitiveTypes::String whose
     * instance class is java.lang.String becomes Ecore EString. This is a
     * representation normalization, not an abstraction: ATL bindings remain
     * active and their values are still constrained.
     */
    private static List<String> mapPrimitiveDataTypes(Document document) {
        Map<String, String> mappings = new LinkedHashMap<>();
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element classifier = (Element) classifiers.item(i);
            if (!isDataType(classifier)) continue;
            String name = classifier.getAttribute("name");
            String instanceClass = classifier.getAttribute("instanceClassName");
            String originalName = detailValue(
                    annotation(classifier, PROVENANCE_ANNOTATION), "originalName");
            String target = standardPrimitiveUri(
                    originalName.isBlank() ? name : originalName, instanceClass);
            if (target != null) mappings.put(name, target);
        }

        List<String> mapped = new ArrayList<>();
        if (mappings.isEmpty()) return mapped;
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element owner = (Element) classifiers.item(i);
            for (Element feature : children(owner, "eStructuralFeatures")) {
                if (!isAttribute(feature)) continue;
                String sourceType = typeName(typeReference(feature));
                String target = mappings.get(sourceType);
                if (target == null || target.equals(typeReference(feature))) continue;
                replaceWithType(feature, target);
                mapped.add(owner.getAttribute("name") + "."
                        + feature.getAttribute("name") + " : " + sourceType
                        + " mapped to " + typeName(target));
            }
        }
        return mapped;
    }

    /**
     * Replaces the small, well-defined subset of generated
     * {@code EString.toInteger()} expressions with an EInt projection in the
     * temporary verification model.  The original string feature remains in
     * the model, since it may be used by other ATL bindings.  A sibling
     * {@code <feature>__int : EInt} carries the numeric abstraction only for
     * the bindings that requested {@code toInteger()}.
     *
     * <p>There is no concrete XMI instance at this point: EFinder is about to
     * synthesize one.  Consequently Java cannot parse the eventual string.
     * Instead, this method proves statically that the conversion is from a
     * known EString feature, and adds a guard requiring the selected source
     * string to exist and be non-empty.  The EInt projection is then the
     * numeric-input profile supplied to the solver.  Expressions outside the
     * canonical ATL2TM shape are rejected rather than approximated.</p>
     */
    private static List<String> normalizeStringToIntegerConversions(Document document) {
        List<String> normalizations = new ArrayList<>();
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element owner = (Element) classifiers.item(i);
            Element pivot = annotation(owner, PIVOT_ANNOTATION);
            if (pivot == null) continue;

            for (Element detail : new ArrayList<>(children(pivot, "details"))) {
                String expression = detail.getAttribute("value");
                if (!expression.contains(".toInteger()")) continue;

                java.util.regex.Matcher conversion = STRING_TO_INTEGER_CONVERSION.matcher(expression);
                StringBuffer rewritten = new StringBuffer();
                int conversionNumber = 0;
                while (conversion.find()) {
                    conversionNumber++;
                    String variable = conversion.group(1);
                    String source = conversion.group(2).trim();
                    String sourceFeatureName = conversion.group(3);
                    Element sourceClass = sourceClassForIntegerConversion(document, source,
                            owner.getAttribute("name") + "::" + detail.getAttribute("key"));
                    LocatedFeature sourceFeature = findAttributeInHierarchy(document,
                            sourceClass, sourceFeatureName, new LinkedHashSet<>());
                    if (sourceFeature == null) {
                        throw new UnsupportedFeatureException("Cannot normalize "
                                + owner.getAttribute("name") + "::" + detail.getAttribute("key")
                                + ": " + sourceClass.getAttribute("name") + "."
                                + sourceFeatureName + " is not an EAttribute");
                    }
                    if (!"EString".equals(typeName(typeReference(sourceFeature.feature())))) {
                        throw new UnsupportedFeatureException("Cannot normalize "
                                + owner.getAttribute("name") + "::" + detail.getAttribute("key")
                                + ": " + sourceClass.getAttribute("name") + "."
                                + sourceFeatureName + " must be EString before toInteger()");
                    }

                    String numericFeature = ensureIntegerProjection(document, sourceFeature);
                    String replacement = "(let " + variable + " = " + source + " in (if "
                            + variable + ".oclIsUndefined() then 0 else " + variable + "."
                            + numericFeature + " endif))";
                    conversion.appendReplacement(rewritten,
                            java.util.regex.Matcher.quoteReplacement(replacement));

                    String guardName = uniqueName(pivot, "__efinder_numeric_input_"
                            + sanitize(detail.getAttribute("key")) + "_" + conversionNumber);
                    addNumericInputGuard(document, owner, pivot, guardName, variable,
                            source, sourceFeatureName);
                    normalizations.add(sourceFeature.owner().getAttribute("name") + "."
                            + sourceFeatureName + " -> " + numericFeature + " : EInt"
                            + " for " + owner.getAttribute("name") + "::"
                            + detail.getAttribute("key") + " (source string required)" );
                }
                conversion.appendTail(rewritten);
                if (conversionNumber == 0) {
                    DirectNormalizationResult direct = normalizeDirectStringToIntegerConversions(
                            document, owner, pivot, detail, rewritten.toString());
                    if (direct.normalizations().isEmpty()) {
                        throw new UnsupportedFeatureException("Unsupported String.toInteger() expression in "
                                + owner.getAttribute("name") + "::" + detail.getAttribute("key")
                                + "; receiver type could not be resolved");
                    }
                    normalizations.addAll(direct.normalizations());
                    detail.setAttribute("value", direct.expression());
                    continue;
                }
                detail.setAttribute("value", rewritten.toString());
            }
        }
        return normalizations;
    }

    private record DirectNormalizationResult(String expression, List<String> normalizations) {}

    /**
     * Handles a binding such as {@code self.source.value.toInteger()} after
     * ATL2TM has rendered the navigation directly instead of inlining a
     * helper into a let-expression.
     */
    private static DirectNormalizationResult normalizeDirectStringToIntegerConversions(
            Document document, Element owner, Element pivot, Element detail,
            String expression) {
        java.util.regex.Matcher direct = DIRECT_STRING_TO_INTEGER_CONVERSION.matcher(expression);
        StringBuffer rewritten = new StringBuffer();
        List<String> normalizations = new ArrayList<>();
        int conversionNumber = 0;
        while (direct.find()) {
            conversionNumber++;
            String receiver = direct.group(1);
            String sourceFeatureName = direct.group(2);
            LocatedFeature sourceFeature = resolveNavigationFeature(document, owner,
                    receiver, sourceFeatureName);
            if (sourceFeature == null) {
                throw new UnsupportedFeatureException("Cannot normalize "
                        + owner.getAttribute("name") + "::" + detail.getAttribute("key")
                        + ": cannot resolve " + receiver + "." + sourceFeatureName);
            }
            if (!"EString".equals(typeName(typeReference(sourceFeature.feature())))) {
                throw new UnsupportedFeatureException("Cannot normalize "
                        + owner.getAttribute("name") + "::" + detail.getAttribute("key")
                        + ": " + receiver + "." + sourceFeatureName
                        + " must be EString before toInteger()");
            }

            String numericFeature = ensureIntegerProjection(document, sourceFeature);
            direct.appendReplacement(rewritten, java.util.regex.Matcher.quoteReplacement(
                    receiver + "." + numericFeature));
            String guardName = uniqueName(pivot, "__efinder_numeric_input_"
                    + sanitize(detail.getAttribute("key")) + "_direct_" + conversionNumber);
            addDirectNumericInputGuard(document, owner, pivot, guardName,
                    receiver, sourceFeatureName);
            normalizations.add(sourceFeature.owner().getAttribute("name") + "."
                    + sourceFeatureName + " -> " + numericFeature + " : EInt"
                    + " for " + owner.getAttribute("name") + "::"
                    + detail.getAttribute("key") + " (direct source navigation)" );
        }
        direct.appendTail(rewritten);
        return new DirectNormalizationResult(rewritten.toString(), normalizations);
    }

    private static LocatedFeature resolveNavigationFeature(Document document, Element owner,
                                                            String receiver, String featureName) {
        String[] path = receiver.split("\\.");
        if (path.length == 0 || !"self".equals(path[0])) return null;
        Element current = owner;
        Set<String> visited = new LinkedHashSet<>();
        for (int i = 1; i < path.length; i++) {
            LocatedFeature navigation = findStructuralFeatureInHierarchy(document, current,
                    path[i], visited);
            if (navigation == null || !isReference(navigation.feature())) return null;
            current = classifierForTypeReference(document, typeReference(navigation.feature()));
            if (current == null) return null;
        }
        return findStructuralFeatureInHierarchy(document, current, featureName,
                new LinkedHashSet<>());
    }

    private static LocatedFeature findStructuralFeatureInHierarchy(Document document,
                                                                    Element classifier,
                                                                    String name,
                                                                    Set<String> visited) {
        if (classifier == null || !visited.add(classifier.getAttribute("name"))) return null;
        for (Element feature : children(classifier, "eStructuralFeatures")) {
            if (name.equals(feature.getAttribute("name"))
                    && (isAttribute(feature) || isReference(feature))) {
                return new LocatedFeature(classifier, feature);
            }
        }
        for (String supertype : words(classifier.getAttribute("eSuperTypes"))) {
            LocatedFeature inherited = findStructuralFeatureInHierarchy(document,
                    classifierForTypeReference(document, supertype), name, visited);
            if (inherited != null) return inherited;
        }
        return null;
    }

    /** Source class of {@code attr.value} is the final explicit OCL cast in the selector. */
    private static Element sourceClassForIntegerConversion(Document document, String source,
                                                            String constraint) {
        java.util.regex.Matcher cast = OCL_CAST_TYPE.matcher(source);
        String typeName = null;
        while (cast.find()) typeName = cast.group(1);
        if (typeName == null) {
            throw new UnsupportedFeatureException("Cannot normalize " + constraint
                    + ": source of toInteger() has no explicit oclAsType(EClass)");
        }
        Element sourceClass = findClassifierByName(document, typeName);
        if (sourceClass == null || !"source".equals(origin(sourceClass))) {
            throw new UnsupportedFeatureException("Cannot normalize " + constraint
                    + ": " + typeName + " is not a source EClass");
        }
        return sourceClass;
    }

    private record LocatedFeature(Element owner, Element feature) {}

    private static LocatedFeature findAttributeInHierarchy(Document document, Element classifier,
                                                           String name, Set<String> visited) {
        if (classifier == null || !visited.add(classifier.getAttribute("name"))) return null;
        for (Element feature : children(classifier, "eStructuralFeatures")) {
            if (isAttribute(feature) && name.equals(feature.getAttribute("name"))) {
                return new LocatedFeature(classifier, feature);
            }
        }
        for (String supertype : words(classifier.getAttribute("eSuperTypes"))) {
            LocatedFeature inherited = findAttributeInHierarchy(document,
                    classifierForTypeReference(document, supertype), name, visited);
            if (inherited != null) return inherited;
        }
        return null;
    }

    private static Element findClassifierByName(Document document, String name) {
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        Element first = null;
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element candidate = (Element) classifiers.item(i);
            if (!name.equals(candidate.getAttribute("name"))) continue;
            if (first == null) first = candidate;
            if ("source".equals(origin(candidate))) return candidate;
        }
        return first;
    }

    private static String ensureIntegerProjection(Document document, LocatedFeature sourceFeature) {
        String projectionName = sourceFeature.feature().getAttribute("name") + "__int";
        for (Element feature : children(sourceFeature.owner(), "eStructuralFeatures")) {
            if (!projectionName.equals(feature.getAttribute("name"))) continue;
            if (!isAttribute(feature) || !"EInt".equals(typeName(typeReference(feature)))) {
                throw new UnsupportedFeatureException("Numeric projection "
                        + sourceFeature.owner().getAttribute("name") + "." + projectionName
                        + " already exists but is not EInt");
            }
            return projectionName;
        }

        Element projection = document.createElement("eStructuralFeatures");
        projection.setAttribute("xsi:type", "ecore:EAttribute");
        projection.setAttribute("name", projectionName);
        projection.setAttribute("ordered", "false");
        projection.setAttribute("eType", "ecore:EDataType "
                + "http://www.eclipse.org/emf/2002/Ecore#//EInt");
        sourceFeature.owner().appendChild(projection);
        return projectionName;
    }

    /**
     * The original generated expression converts the empty fallback string.
     * Make that source-domain requirement explicit before replacing the
     * conversion with its EInt projection.  This prevents a counterexample
     * from relying on a missing or empty value that ATL would not convert.
     */
    private static void addNumericInputGuard(Document document, Element owner, Element pivot,
                                             String name, String variable, String source,
                                             String sourceFeature) {
        Element ecore = ensureAnnotation(document, owner, ECORE_ANNOTATION);
        Element guard = document.createElement("details");
        guard.setAttribute("key", name);
        guard.setAttribute("value", "let " + variable + " = " + source + " in if "
                + variable + ".oclIsUndefined() then false else not " + variable + "."
                + sourceFeature + ".oclIsUndefined() and " + variable + "."
                + sourceFeature + " <> '' endif");
        pivot.appendChild(guard);
        appendWord(ensureDetail(document, ecore, "constraints"), name);
        Element provenance = annotation(owner, PROVENANCE_ANNOTATION);
        if (provenance != null) {
            appendWord(ensureDetail(document, provenance, "semConstraints"), name);
        }
    }

    private static void addDirectNumericInputGuard(Document document, Element owner,
                                                   Element pivot, String name,
                                                   String receiver, String sourceFeature) {
        Element ecore = ensureAnnotation(document, owner, ECORE_ANNOTATION);
        Element guard = document.createElement("details");
        guard.setAttribute("key", name);
        guard.setAttribute("value", "if " + receiver + ".oclIsUndefined() then false else not "
                + receiver + "." + sourceFeature + ".oclIsUndefined() and " + receiver + "."
                + sourceFeature + " <> '' endif");
        pivot.appendChild(guard);
        appendWord(ensureDetail(document, ecore, "constraints"), name);
        Element provenance = annotation(owner, PROVENANCE_ANNOTATION);
        if (provenance != null) {
            appendWord(ensureDetail(document, provenance, "semConstraints"), name);
        }
    }

    private static boolean isDataType(Element classifier) {
        return "ecore:EDataType".equals(classifier.getAttribute("xsi:type"))
                || "EDataType".equals(classifier.getAttribute("xsi:type"));
    }

    private static String standardPrimitiveUri(String name, String instanceClass) {
        String target = STANDARD_PRIMITIVE_URIS.get(name);
        if (target == null || instanceClass == null || instanceClass.isBlank()) return null;
        String expected = switch (name) {
            case "String" -> "java.lang.String";
            case "Boolean" -> "java.lang.Boolean";
            case "Byte" -> "java.lang.Byte";
            case "Short" -> "java.lang.Short";
            case "Integer" -> "java.lang.Integer";
            case "Long" -> "java.lang.Long";
            case "Float" -> "java.lang.Float";
            case "Double" -> "java.lang.Double";
            default -> "";
        };
        return expected.equals(instanceClass) ? target : null;
    }

    /**
     * EFinder/USEMV supports a bounded subset of Ecore primitive datatypes.
     * A feature with an EDate, custom EDataType, EEnum, or another datatype
     * outside that subset can be abstracted in the temporary verification
     * copy only when it is not observable from the active Sem/Pre/negated-Post
     * formula. Generated null-frame constraints are the sole permitted
     * references: they describe an ATL output feature that was not bound and
     * become irrelevant once that feature is abstracted.
     */
    private static List<String> abstractIrrelevantUnsupportedFeatures(Document document) {
        List<String> abstractions = new ArrayList<>();
        NodeList classifiers = document.getElementsByTagName("eClassifiers");
        for (int i = 0; i < classifiers.getLength(); i++) {
            Element owner = (Element) classifiers.item(i);
            for (Element feature : children(owner, "eStructuralFeatures")) {
                if (!isAttribute(feature) || !isUnsupportedEcoreType(feature)) continue;

                String featureName = feature.getAttribute("name");
                if (featureName.isBlank()) continue;
                String unsupportedType = typeName(typeReference(feature));
                List<ConstraintDetail> generatedFrames = new ArrayList<>();
                List<String> dependencies = new ArrayList<>();
                for (int j = 0; j < classifiers.getLength(); j++) {
                    Element classifier = (Element) classifiers.item(j);
                    Element pivot = annotation(classifier, PIVOT_ANNOTATION);
                    if (pivot == null) continue;
                    for (Element detail : children(pivot, "details")) {
                        String body = detail.getAttribute("value");
                        if (!referencesFeature(body, featureName)) continue;
                        if (isGeneratedNullFrame(detail, featureName)) {
                            generatedFrames.add(new ConstraintDetail(classifier, pivot, detail));
                        } else {
                            dependencies.add(classifier.getAttribute("name") + "::"
                                    + detail.getAttribute("key"));
                        }
                    }
                }

                String descriptor = owner.getAttribute("name") + "." + featureName
                        + " : " + unsupportedType;
                if (!dependencies.isEmpty()) {
                    throw new UnsupportedFeatureException(descriptor
                            + " is used by active Sem/Pre/Post constraint(s): "
                            + String.join(", ", dependencies));
                }

                List<String> removed = new ArrayList<>();
                for (ConstraintDetail frame : generatedFrames) {
                    String name = frame.detail().getAttribute("key");
                    frame.pivot().removeChild(frame.detail());
                    removeConstraintName(frame.owner(), name);
                    removed.add(frame.owner().getAttribute("name") + "::" + name);
                }
                replaceWithType(feature,
                        "http://www.eclipse.org/emf/2002/Ecore#//EString");
                abstractions.add(descriptor + " abstracted to EString"
                        + (removed.isEmpty() ? "" : "; removed generated frame constraint(s): "
                        + String.join(", ", removed)));
            }
        }
        return abstractions;
    }

    private record ConstraintDetail(Element owner, Element pivot, Element detail) {}

    private static boolean isAttribute(Element feature) {
        String type = feature.getAttribute("xsi:type");
        return type.endsWith("EAttribute");
    }

    private static boolean isUnsupportedEcoreType(Element feature) {
        String name = typeName(typeReference(feature));
        return !name.isBlank() && !SUPPORTED_ECORE_DATA_TYPES.contains(name);
    }

    private static String typeReference(Element feature) {
        if (feature.hasAttribute("eType")) return feature.getAttribute("eType");
        for (Element child : children(feature, "eType")) {
            if (child.hasAttribute("href")) return child.getAttribute("href");
        }
        return "";
    }

    private static String typeName(String reference) {
        if (reference == null || reference.isBlank()) return "";
        String value = reference.trim();
        int marker = value.lastIndexOf("#//");
        if (marker >= 0) return value.substring(marker + 3);
        marker = value.lastIndexOf("//");
        if (marker >= 0) return value.substring(marker + 2);
        int whitespace = value.lastIndexOf(' ');
        return whitespace >= 0 ? value.substring(whitespace + 1) : value;
    }

    private static boolean referencesFeature(String expression, String featureName) {
        return Pattern.compile("(?<![A-Za-z0-9_])" + Pattern.quote(featureName)
                + "(?![A-Za-z0-9_])").matcher(expression).find();
    }

    private static boolean isGeneratedNullFrame(Element detail, String featureName) {
        String name = detail.getAttribute("key");
        return name.startsWith("null_") && name.endsWith("_" + featureName);
    }

    private static void removeConstraintName(Element classifier, String name) {
        Element ecore = annotation(classifier, ECORE_ANNOTATION);
        if (ecore != null) removeWord(detail(ecore, "constraints"), name);
        Element provenance = annotation(classifier, PROVENANCE_ANNOTATION);
        if (provenance != null) {
            removeWord(detail(provenance, "semConstraints"), name);
            removeWord(detail(provenance, "preConstraints"), name);
            removeWord(detail(provenance, "postConstraints"), name);
        }
    }

    private static void removeWord(Element detail, String value) {
        if (detail == null) return;
        List<String> values = words(detail.getAttribute("value"));
        values.removeIf(value::equals);
        detail.setAttribute("value", String.join(" ", values));
    }

    private static void replaceWithType(Element feature, String ecoreType) {
        if (feature.hasAttribute("eType")) {
            feature.setAttribute("eType", "ecore:EDataType " + ecoreType);
            return;
        }
        for (Element child : children(feature, "eType")) {
            child.setAttribute("href", ecoreType);
            return;
        }
        Element type = feature.getOwnerDocument().createElement("eType");
        type.setAttribute("href", ecoreType);
        type.setAttribute("xsi:type", "ecore:EDataType");
        feature.appendChild(type);
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
            Element provenance = annotation(classifier, PROVENANCE_ANNOTATION);
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
            // The generated existential negation is not part of the original
            // Ecore list. It must be enabled explicitly; retaining it only as
            // a Pivot detail lets Ecore2AS parse it but does not make it an
            // invariant enforced by EFinder.
            if (classifier == selectedContext) rewritten.add(generated);
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
        Element provenance = annotation(classifier, PROVENANCE_ANNOTATION);
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
            if ((duplicates.size() < 2
                    && !OCL_COLLECTION_TYPE_NAMES.contains(entry.getKey()))
                    || entry.getKey().isBlank()) continue;

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
            Element provenance = annotation(classifier, PROVENANCE_ANNOTATION);
            Set<String> preConstraints = new LinkedHashSet<>(words(
                    detailValue(provenance, "preConstraints")));
            Element pivot = annotation(classifier, PIVOT_ANNOTATION);
            if (pivot == null) continue;
            for (Element detail : children(pivot, "details")) {
                // A global source-precondition can be stored on the selected
                // target classifier so it is not vacuous. Its type names
                // still refer to source classifiers and must be normalized as
                // source names when source/target names collide.
                // Most preconditions describe source inputs. Target-coverage
                // premises are deliberately stored as Pre as well, but their
                // allInstances/type/reference names describe target objects.
                boolean targetCoverage = detail.getAttribute("key")
                        .startsWith("__efinder_TargetCoverage_");
                String detailRole = targetCoverage ? "target"
                        : preConstraints.contains(detail.getAttribute("key"))
                        ? "source" : role;
                boolean preferTrace = detail.getAttribute("key").startsWith("match_")
                        || detail.getAttribute("key").startsWith("__efinder_NOT_");
                boolean traceContext = "trace".equals(origin(classifier));
                detail.setAttribute("value", rewriteOclTypes(
                        detail.getAttribute("value"), byName, normalized, detailRole,
                        preferTrace, traceContext));
            }
        }
        return normalized;
    }

    private static String origin(Element classifier) {
        return detailValue(annotation(classifier, PROVENANCE_ANNOTATION), "origin");
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
        if (candidates == null || index >= candidates.size()) {
            return token;
        }
        String replacement = normalized.get(candidates.get(index));
        return replacement == null ? token : marker + replacement + rest;
    }

    private static String rewriteOclTypes(String value,
                                          Map<String, List<Element>> byName,
                                          Map<Element, String> normalized,
                                          String role,
                                          boolean preferTrace,
                                          boolean traceContext) {
        String rewritten = value;
        for (Map.Entry<String, List<Element>> entry : byName.entrySet()) {
            boolean hasRenamedClassifier = entry.getValue().stream()
                    .anyMatch(normalized::containsKey);
            if (!hasRenamedClassifier) continue;
            Pattern typePattern = Pattern.compile("(?<![\\w.])"
                    + Pattern.quote(entry.getKey()) + "(?![\\w])");
            java.util.regex.Matcher matcher = typePattern.matcher(rewritten);
            StringBuffer result = new StringBuffer();
            while (matcher.find()) {
                // Keep OCL collection literals such as Set { ... } intact.
                // The same identifier may also denote an EClass in
                // oclIsKindOf(Set), Set.allInstances(), or z : Set; those
                // type positions must still be renamed below.
                if (isOclCollectionLiteralType(rewritten, matcher)) {
                    matcher.appendReplacement(result,
                            java.util.regex.Matcher.quoteReplacement(matcher.group()));
                    continue;
                }
                boolean useTrace = preferTrace || (traceContext
                        && occurrenceUsesTrace(rewritten, matcher));
                Element selected = selectByOrigin(entry.getValue(), role, useTrace);
                String replacement = selected == null ? null : normalized.get(selected);
                if (replacement == null) {
                    matcher.appendReplacement(result,
                            java.util.regex.Matcher.quoteReplacement(matcher.group()));
                } else {
                    matcher.appendReplacement(result,
                            java.util.regex.Matcher.quoteReplacement(replacement));
                }
            }
            matcher.appendTail(result);
            rewritten = result.toString();
        }
        return rewritten;
    }

    private static boolean isOclCollectionLiteralType(String expression,
                                                       java.util.regex.Matcher match) {
        int position = match.end();
        while (position < expression.length()
                && Character.isWhitespace(expression.charAt(position))) {
            position++;
        }
        return position < expression.length() && expression.charAt(position) == '{';
    }

    /**
     * In trace OCL, allInstances and typed iterator declarations range over
     * trace objects, while oclIsKindOf/oclAsType inspect source objects used
     * by the binding expression. The distinction is essential when a source,
     * target, and trace classifier share one ATL name.
     */
    private static boolean occurrenceUsesTrace(String expression,
                                               java.util.regex.Matcher match) {
        String before = expression.substring(0, match.start()).trim();
        String after = expression.substring(match.end()).trim();
        boolean typeTest = before.endsWith("oclIsKindOf(")
                || before.endsWith("oclAsType(");
        boolean allInstances = after.startsWith(".allInstances(");
        boolean typedIterator = before.endsWith(":");
        return !typeTest && (allInstances || typedIterator);
    }

    private static Element selectByOrigin(List<Element> candidates, String role,
                                          boolean preferTrace) {
        if (preferTrace) {
            for (Element candidate : candidates) {
                if ("trace".equals(origin(candidate))) return candidate;
            }
        }
        for (Element candidate : candidates) {
            if (role.equals(origin(candidate))) return candidate;
        }
        // A generated ATL2TM match expression may refer to its trace class
        // even when the surrounding classifier has source/target role. This
        // occurs when the trace class shares its original name with the
        // target class (for example Grafcet). Prefer the trace classifier
        // before falling back to declaration order.
        for (Element candidate : candidates) {
            if ("trace".equals(origin(candidate))) return candidate;
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
