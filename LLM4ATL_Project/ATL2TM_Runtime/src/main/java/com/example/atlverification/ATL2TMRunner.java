package com.example.atlverification;

import com.example.atlparser.ATLModelLoader;
import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EReference;
import org.eclipse.emf.ecore.EcorePackage;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.m2m.atl.core.IModel;
import org.eclipse.m2m.atl.core.IReferenceModel;
import org.eclipse.m2m.atl.core.emf.EMFExtractor;
import org.eclipse.m2m.atl.core.emf.EMFInjector;
import org.eclipse.m2m.atl.core.emf.EMFModel;
import org.eclipse.m2m.atl.core.ModelFactory;
import org.eclipse.m2m.atl.core.emf.EMFModelFactory;
import org.eclipse.m2m.atl.core.launch.ILauncher;
import org.eclipse.m2m.atl.engine.emfvm.launch.EMFVMLauncher;
import org.eclipse.emf.common.util.URI;

import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;


public final class ATL2TMRunner {

    /** Marker emitted by ATL2TM when helper inlining re-enters an active helper. */
    private static final String UNSUPPORTED_RECURSIVE_HELPER_MARKER =
            "__ATL2TM_UNSUPPORTED_RECURSIVE_HELPER__";

    /** Marker emitted by ATL2TM when an OCL expression cannot be rendered. */
    private static final String UNSUPPORTED_EXPRESSION_MARKER =
            "__ATL2TM_UNSUPPORTED_EXPRESSION__";

    private final ATLModelLoader atlModelLoader;

    public ATL2TMRunner() {
        this.atlModelLoader = new ATLModelLoader();
    }

    public void run(
            Path inputAtl,
            Path sourceEcore,
            Path targetEcore,
            Path atl2tmAtl,
            Path workDir,
            Path outputEcore
    ) throws Exception {

        Files.createDirectories(workDir);

        // 1. Load transformation cần verify thành ATL IModel
        IModel inputAtlModel =
                atlModelLoader.loadAsModel(inputAtl);

        // Fail closed before the HOT emits a partial invocation encoding.
        validateLazyRuleSubset(inputAtlModel, sourceEcore, targetEcore);

        System.out.println(
                "Loaded ATL input model: " + inputAtl
        );

        // 2. Compile ATL2TM.atl → ATL2TM.asm
        Path asmPath =
                workDir.resolve("ATL2TM.asm");

        compileAtlInSeparateJvm(atl2tmAtl, asmPath);

        System.out.println(
                "Compiled ATL2TM to: "
                        + asmPath
        );
        
        // 3. Chuẩn bị Ecore metamodel 
        ModelFactory modelFactory = new EMFModelFactory();

        IReferenceModel ecoreMetamodel =
                modelFactory.newReferenceModel();

        EMFInjector injector =
                new EMFInjector();

        EcorePackage.eINSTANCE.eClass();

        injector.inject(
                ecoreMetamodel,
                EcorePackage.eNS_URI
        );

        // 4. Load source and target Ecore metamodels as IModel
        IModel sourceEcoreModel =
                loadEcoreAsModel(
                        sourceEcore,
                        ecoreMetamodel,
                        modelFactory
                );

        IModel targetEcoreModel =
                loadEcoreAsModel(
                        targetEcore,
                        ecoreMetamodel,
                        modelFactory
                );

        System.out.println(
                "Loaded source and target Ecore metamodels"
        );

        // 5. Tạo ECORE output model
        IModel outputModel =
                modelFactory.newModel(ecoreMetamodel);

        System.out.println(
                "Created empty ECORE output model"
        );

        // 6. Configure EMFVMLauncher

        ILauncher launcher =
                new EMFVMLauncher();

        Map<String, Object> options =
                new HashMap<>();
                
        options.put("allowInterModelReferences", "true");

        launcher.initialize(options);

        // 7. add IN : ATL

        launcher.addInModel(
                inputAtlModel,
                "IN",
                "ATL"
        );

        // 8. add IN : ECORE source and target
        launcher.addInModel(
                sourceEcoreModel,
                "SRC",
                "ECORE"
        );

        launcher.addInModel(
                targetEcoreModel,
                "TGT",
                "ECORE"
        );


        // 9. add OUT : ECORE
        launcher.addOutModel(
            outputModel,
            "OUT",
            "ECORE"
        );

        // 10. launch ATL2TM.asm

        try (InputStream asmInput =
                    Files.newInputStream(
                            asmPath
                    )) {

            launcher.launch(
                    ILauncher.RUN_MODE,
                    null,
                    options,
                    asmInput
            );
        }

        System.out.println(
                "Executed ATL2TM successfully"
        );

        rejectUnsupportedRecursiveHelpers(outputModel);

        // 11. save TransformationModel.ecore

        Path normalizedOutput =
                outputEcore
                        .toAbsolutePath()
                        .normalize();

        if (normalizedOutput.getParent() != null) {
            Files.createDirectories(
                    normalizedOutput.getParent()
            );
        }

        EMFExtractor extractor =
                new EMFExtractor();

        String outputUri =
                URI.createFileURI(
                        normalizedOutput.toString()
                ).toString();

        extractor.extract(
                outputModel,
                outputUri
        );

        // The ATL2TM model contains source, target, and trace classifiers in
        // one EPackage. Make collisions explicit in the persisted artifact so
        // Pivot OCL never has to guess whether (for example) Transition means
        // the source class, target class, or the rule trace.
        TransformationModelRoleNormalizer.normalize(normalizedOutput);

        System.out.println(
                "Saved Transformation Model: "
                        + normalizedOutput
        );
    }

    private static void validateLazyRuleSubset(IModel inputModel,
            Path sourceEcore, Path targetEcore)
            throws UnsupportedAtlConstructException {
        if (!(inputModel instanceof EMFModel emfModel)
                || emfModel.getResource() == null) {
            return;
        }

        Map<String, EObject> lazyRules = new HashMap<>();
        List<EObject> ruleCalls = new ArrayList<>();
        List<EObject> matchedRules = new ArrayList<>();
        TreeIterator<EObject> contents = emfModel.getResource().getAllContents();
        while (contents.hasNext()) {
            EObject element = contents.next();
            String type = element.eClass().getName();
            if ("LazyMatchedRule".equals(type)) {
                lazyRules.put(String.valueOf(feature(element, "name")), element);
            } else if ("MatchedRule".equals(type)) {
                matchedRules.add(element);
            } else if ("OperationCallExp".equals(type)) {
                ruleCalls.add(element);
            }
        }

        for (Map.Entry<String, EObject> entry : lazyRules.entrySet()) {
            EObject rule = entry.getValue();
            String name = entry.getKey();
            if (Boolean.TRUE.equals(feature(rule, "isUnique"))) {
                throw unsupportedLazy(name, "unique lazy rule semantics");
            }
            EObject inPattern = (EObject) feature(rule, "inPattern");
            EObject outPattern = (EObject) feature(rule, "outPattern");
            List<?> inputs = inPattern == null ? List.of()
                    : (List<?>) feature(inPattern, "elements");
            List<?> outputs = outPattern == null ? List.of()
                    : (List<?>) feature(outPattern, "elements");
            if (inputs.size() != 1 || outputs.size() != 1
                    || !"SimpleInPatternElement".equals(
                            ((EObject) inputs.get(0)).eClass().getName())
                    || !"SimpleOutPatternElement".equals(
                            ((EObject) outputs.get(0)).eClass().getName())) {
                throw unsupportedLazy(name, "expected one simple input and one simple output");
            }
            if (feature(inPattern, "filter") != null) {
                throw unsupportedLazy(name, "input filter");
            }
            if (feature(rule, "actionBlock") != null
                    || hasElements(feature(rule, "variables"))
                    || feature(rule, "superRule") != null) {
                throw unsupportedLazy(name, "action block, using variables, or rule inheritance");
            }
        }

        Set<EObject> checkedUnionBindings = new HashSet<>();
        for (EObject call : ruleCalls) {
            String name = String.valueOf(feature(call, "operationName"));
            if (!lazyRules.containsKey(name)) {
                continue;
            }
            EObject container = call.eContainer();
            EObject iterator = container != null
                    && "IteratorExp".equals(container.eClass().getName())
                    ? container : null;
            EObject binding = iterator == null ? container
                    : collectBinding(iterator);
            EObject output = binding == null ? null
                    : (EObject) feature(binding, "outPatternElement");
            EObject outPattern = output == null ? null
                    : (EObject) feature(output, "outPattern");
            EObject caller = outPattern == null ? null
                    : (EObject) feature(outPattern, "rule");
            Object args = feature(call, "arguments");
            boolean direct = binding != null && feature(binding, "value") == call;
            boolean collect = iterator != null && binding != null;
            if (binding == null || !"Binding".equals(binding.eClass().getName())
                    || (!direct && !collect)
                    || caller == null
                    || !"MatchedRule".equals(caller.eClass().getName())
                    || feature(caller, "actionBlock") != null
                    || hasElements(feature(caller, "variables"))
                    || feature(caller, "superRule") != null
                    || !(args instanceof List<?> arguments)
                    || arguments.size() != 1
                    || !isThisModule(feature(call, "source"))) {
                throw unsupportedLazy(name,
                        "only a direct call or a Set collect call in a matched-rule binding is supported");
            }
            if (collect) {
                validateSetCollectCall(name, call, iterator, binding, caller,
                        lazyRules.get(name), sourceEcore, targetEcore);
                if (feature(binding, "value") != iterator
                        && checkedUnionBindings.add(binding)) {
                    validateMixedUnionBinding(name, binding, caller, matchedRules,
                            lazyRules, sourceEcore, targetEcore);
                }
            }
        }
    }

    private static EObject collectBinding(EObject iterator) {
        EObject child = iterator;
        EObject parent = iterator.eContainer();
        while (parent != null && "CollectionOperationCallExp".equals(
                parent.eClass().getName())) {
            List<?> arguments = (List<?>) feature(parent, "arguments");
            if (!"union".equals(feature(parent, "operationName"))
                    || arguments.size() != 1
                    || (feature(parent, "source") != child
                            && arguments.get(0) != child)) {
                return null;
            }
            child = parent;
            parent = parent.eContainer();
        }
        return parent != null && "Binding".equals(parent.eClass().getName())
                && feature(parent, "value") == child ? parent : null;
    }

    private static void validateMixedUnionBinding(String lazyName, EObject binding,
            EObject caller, List<EObject> matchedRules,
            Map<String, EObject> lazyRules, Path sourceEcore, Path targetEcore)
            throws UnsupportedAtlConstructException {
        EPackage sourcePackage = new EcoreModelLoader().load(sourceEcore);
        EPackage targetPackage = new EcoreModelLoader().load(targetEcore);
        EObject output = (EObject) feature(binding, "outPatternElement");
        EReference targetSet = setReference(targetPackage, typeName(output),
                String.valueOf(feature(binding, "propertyName")));
        if (targetSet == null) {
            throw unsupportedLazy(lazyName,
                    "union with lazy collect requires an unordered, unique target Set");
        }
        validateMixedUnionBranch(lazyName, (EObject) feature(binding, "value"),
                caller, sourcePackage, targetSet.getEReferenceType(),
                matchedRules, lazyRules);
    }

    private static void validateMixedUnionBranch(String lazyName, EObject expression,
            EObject caller, EPackage sourcePackage, EClass targetElement,
            List<EObject> matchedRules, Map<String, EObject> lazyRules)
            throws UnsupportedAtlConstructException {
        if (expression != null && "CollectionOperationCallExp".equals(
                expression.eClass().getName())
                && "union".equals(feature(expression, "operationName"))) {
            List<?> arguments = (List<?>) feature(expression, "arguments");
            if (arguments.size() != 1) {
                throw unsupportedLazy(lazyName, "union requires one collection argument");
            }
            validateMixedUnionBranch(lazyName,
                    (EObject) feature(expression, "source"), caller,
                    sourcePackage, targetElement, matchedRules, lazyRules);
            validateMixedUnionBranch(lazyName, (EObject) arguments.get(0), caller,
                    sourcePackage, targetElement, matchedRules, lazyRules);
            return;
        }
        if (expression != null && "IteratorExp".equals(expression.eClass().getName())
                && "collect".equals(feature(expression, "name"))) {
            EObject body = (EObject) feature(expression, "body");
            if (body != null && "OperationCallExp".equals(body.eClass().getName())
                    && lazyRules.containsKey(String.valueOf(feature(body, "operationName")))) {
                return; // Each call site is checked by validateSetCollectCall.
            }
        }
        EClass sourceElement;
        try {
            sourceElement = PureOclSetTypeInferrer.inferCollection(
                    expression, sourcePackage, caller);
        } catch (IllegalArgumentException error) {
            throw unsupportedLazy(lazyName, error.getMessage());
        }
        List<EObject> resolvers = matchedRules.stream().filter(rule -> {
            EObject input = firstElement(feature((EObject) feature(rule, "inPattern"),
                    "elements"));
            EClass inputType = sourcePackage.getEClassifier(typeName(input)) instanceof EClass type
                    ? type : null;
            return inputType != null && ((List<?>) feature(
                    (EObject) feature(rule, "inPattern"), "elements")).size() == 1
                    && (sourceElement.isSuperTypeOf(inputType)
                            || inputType.isSuperTypeOf(sourceElement));
        }).toList();
        if (resolvers.isEmpty() || resolvers.stream().anyMatch(rule -> {
            EObject result = firstElement(feature((EObject) feature(rule, "outPattern"),
                    "elements"));
            return result == null || !targetElement.getName().equals(typeName(result));
        })) {
            throw unsupportedLazy(lazyName,
                    "union source branch requires compatible unary matched resolvers producing "
                            + targetElement.getName());
        }
    }

    private static void validateSetCollectCall(String name, EObject call,
            EObject iterator, EObject binding, EObject caller, EObject lazyRule,
            Path sourceEcore, Path targetEcore)
            throws UnsupportedAtlConstructException {
        List<?> iterators = (List<?>) feature(iterator, "iterators");
        EObject inputCollection = (EObject) feature(iterator, "source");
        EObject argument = (EObject) ((List<?>) feature(call, "arguments")).get(0);
        if (!"collect".equals(feature(iterator, "name"))
                || iterators == null || iterators.size() != 1
                || feature(iterator, "body") != call
                || inputCollection == null
                || !"VariableExp".equals(argument.eClass().getName())
                || feature(argument, "referredVariable") != iterators.get(0)) {
            throw unsupportedLazy(name,
                    "collect must pass its iterator variable to the lazy rule");
        }

        EPackage sourcePackage = new EcoreModelLoader().load(sourceEcore);
        EPackage targetPackage = new EcoreModelLoader().load(targetEcore);
        EClass sourceElement;
        try {
            sourceElement = PureOclSetTypeInferrer.infer(
                    inputCollection, sourcePackage, caller);
        } catch (IllegalArgumentException error) {
            throw unsupportedLazy(name, error.getMessage());
        }
        EObject output = (EObject) feature(binding, "outPatternElement");
        EObject lazyInput = firstElement(feature((EObject) feature(lazyRule,
                "inPattern"), "elements"));
        EObject lazyOutput = firstElement(feature((EObject) feature(lazyRule,
                "outPattern"), "elements"));
        EReference targetSet = setReference(targetPackage,
                typeName(output), String.valueOf(feature(binding, "propertyName")));
        if (targetSet == null
                || !sourceElement.getName().equals(typeName(lazyInput))
                || !targetSet.getEReferenceType().getName().equals(typeName(lazyOutput))) {
            throw unsupportedLazy(name,
                    "collect requires a Set source and an unordered, unique, "
                            + "multivalued target reference with element types matching the lazy rule");
        }
    }

    private static EObject firstElement(Object value) {
        return value instanceof List<?> list && !list.isEmpty()
                ? (EObject) list.get(0) : null;
    }

    private static String typeName(EObject patternElement) {
        EObject type = patternElement == null ? null
                : (EObject) feature(patternElement, "type");
        return String.valueOf(feature(type, "name"));
    }

    private static EReference setReference(EPackage ecore, String className,
            String propertyName) {
        if (!(ecore.getEClassifier(className) instanceof EClass type)
                || !(type.getEStructuralFeature(propertyName) instanceof EReference ref)
                || !ref.isMany() || ref.isOrdered() || !ref.isUnique()) {
            return null;
        }
        return ref;
    }

    private static Object feature(EObject object, String name) {
        if (object == null) {
            return null;
        }
        EStructuralFeature feature = object.eClass().getEStructuralFeature(name);
        return feature == null ? null : object.eGet(feature);
    }

    private static boolean hasElements(Object value) {
        return value instanceof List<?> list && !list.isEmpty();
    }

    private static boolean isThisModule(Object source) {
        if (!(source instanceof EObject variable)
                || !"VariableExp".equals(variable.eClass().getName())) {
            return false;
        }
        Object declaration = feature(variable, "referredVariable");
        return declaration instanceof EObject declared
                && "thisModule".equals(feature(declared, "varName"));
    }

    private static UnsupportedAtlConstructException unsupportedLazy(
            String rule, String reason) {
        return new UnsupportedAtlConstructException(
                "ATL2TM does not support lazy rule " + rule + ": " + reason);
    }

    /**
     * Helper calls are inlined into generated OCL. Recursive helpers therefore
     * have no finite translation and must not be handed to the verifier as a
     * partially translated transformation model.
     */
    private static void rejectUnsupportedRecursiveHelpers(IModel outputModel)
            throws UnsupportedAtlConstructException {
        if (!(outputModel instanceof EMFModel emfModel)
                || emfModel.getResource() == null) {
            return;
        }

        TreeIterator<EObject> contents =
                emfModel.getResource().getAllContents();

        while (contents.hasNext()) {
            EObject element = contents.next();
            EStructuralFeature valueFeature = element.eClass()
                    .getEStructuralFeature("value");
            Object value = valueFeature == null
                    ? null
                    : element.eGet(valueFeature);
            if (value instanceof String text) {
                if (text.contains(UNSUPPORTED_RECURSIVE_HELPER_MARKER)) {
                    throw new UnsupportedAtlConstructException(
                            "Recursive ATL helper calls are unsupported by ATL2TM: "
                                    + text
                    );
                }
                if (text.contains(UNSUPPORTED_EXPRESSION_MARKER)) {
                    throw new UnsupportedAtlConstructException(
                            "Unsupported ATL/OCL expression encountered by ATL2TM: "
                                    + text
                    );
                }
            }
        }
    }

    public static final class UnsupportedAtlConstructException
            extends Exception {
        public UnsupportedAtlConstructException(String message) {
            super(message);
        }
    }

    private IModel loadEcoreAsModel(
                Path ecorePath,
                IReferenceModel ecoreMetamodel,
                ModelFactory modelFactory
    ) throws Exception {
        IModel ecoreModel =
                modelFactory.newModel(ecoreMetamodel);

        EMFInjector injector =
                new EMFInjector();

        String ecoreUri = URI.createFileURI(
                ecorePath.toAbsolutePath().normalize().toString()
        ).toString();

        injector.inject(ecoreModel, ecoreUri);

        return ecoreModel;
    }


    /**
     * Runs AtlCompiler in the ATL_Tests Maven project instead of loading its
     * Eclipse dependencies into this JVM. ATL's legacy Equinox bundles and
     * the newer Eclipse platform bundles otherwise produce signed
     * split-package conflicts on a flat classpath.
     */
    private static void compileAtlInSeparateJvm(
            Path atlPath,
            Path asmPath
    ) throws Exception {
        Path compilerPom = compilerPomPath();

        ProcessBuilder processBuilder = new ProcessBuilder(
                mavenCommand(),
                "-q",
                "-f", compilerPom.toString(),
                "exec:java",
                "-Dexec.mainClass=org.example.AtlCompilerCli"
        );
        processBuilder.environment().put(
                "ATL_COMPILER_INPUT",
                atlPath.toAbsolutePath().normalize().toString()
        );
        processBuilder.environment().put(
                "ATL_COMPILER_OUTPUT",
                asmPath.toAbsolutePath().normalize().toString()
        );
        processBuilder.redirectErrorStream(true);

        Process process = processBuilder.start();
        String output = new String(
                process.getInputStream().readAllBytes(),
                StandardCharsets.UTF_8
        );
        int exitCode = process.waitFor();

        if (exitCode != 0 || !Files.isRegularFile(asmPath)
                || Files.size(asmPath) == 0) {
            throw new IllegalStateException(
                    "ATL2TM compilation failed in separate compiler JVM "
                            + "(exit=" + exitCode + "): " + output
            );
        }
    }

    private static Path compilerPomPath() {
        String configuredProject = System.getProperty(
                "atl.compiler.project",
                System.getenv("ATL_COMPILER_PROJECT")
        );
        Path projectDirectory = configuredProject == null
                || configuredProject.isBlank()
                ? Path.of("..", "ATL_Tests")
                : Path.of(configuredProject);
        Path pom = projectDirectory
                .toAbsolutePath()
                .normalize()
                .resolve("pom.xml");

        if (!Files.isRegularFile(pom)) {
            throw new IllegalStateException(
                    "ATL compiler project not found. Set -Datl.compiler.project "
                            + "or ATL_COMPILER_PROJECT to the ATL_Tests directory: "
                            + pom
            );
        }
        return pom;
    }

    private static String mavenCommand() {
        return System.getProperty("os.name")
                .toLowerCase()
                .contains("win") ? "mvn.cmd" : "mvn";
    }
}
