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
import java.util.HashMap;
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

        System.out.println(
                "Saved Transformation Model: "
                        + normalizedOutput
        );
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
