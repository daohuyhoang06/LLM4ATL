package com.example.atlverification;

import com.example.atlparser.ATLModelLoader;
import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.ecore.EObject;
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
import java.util.List;
import java.util.Map;


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

        // Only the direct scalar ordinary-lazy subset has an invocation
        // encoding. Reject other forms before the HOT can emit a partial TM.
        validateLazyRuleSubset(inputAtlModel);

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

    private static void validateLazyRuleSubset(IModel inputModel)
            throws UnsupportedAtlConstructException {
        if (!(inputModel instanceof EMFModel emfModel)
                || emfModel.getResource() == null) {
            return;
        }

        Map<String, EObject> lazyRules = new HashMap<>();
        List<EObject> ruleCalls = new ArrayList<>();
        TreeIterator<EObject> contents = emfModel.getResource().getAllContents();
        while (contents.hasNext()) {
            EObject element = contents.next();
            String type = element.eClass().getName();
            if ("LazyMatchedRule".equals(type)) {
                lazyRules.put(String.valueOf(feature(element, "name")), element);
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

        for (EObject call : ruleCalls) {
            String name = String.valueOf(feature(call, "operationName"));
            if (!lazyRules.containsKey(name)) {
                continue;
            }
            EObject binding = call.eContainer();
            EObject output = binding == null ? null
                    : (EObject) feature(binding, "outPatternElement");
            EObject outPattern = output == null ? null
                    : (EObject) feature(output, "outPattern");
            EObject caller = outPattern == null ? null
                    : (EObject) feature(outPattern, "rule");
            Object args = feature(call, "arguments");
            if (binding == null || !"Binding".equals(binding.eClass().getName())
                    || feature(binding, "value") != call
                    || caller == null
                    || !"MatchedRule".equals(caller.eClass().getName())
                    || feature(caller, "actionBlock") != null
                    || hasElements(feature(caller, "variables"))
                    || feature(caller, "superRule") != null
                    || !(args instanceof List<?> arguments)
                    || arguments.size() != 1
                    || !isThisModule(feature(call, "source"))) {
                throw unsupportedLazy(name,
                        "only a direct one-argument call in a matched-rule binding is supported");
            }
        }
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
