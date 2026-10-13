package org.example;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.File;
import java.io.FileReader;
import java.io.InputStream;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Stream;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;
import org.eclipse.m2m.atl.core.IModel;
import org.eclipse.m2m.atl.core.IReferenceModel;
import org.eclipse.m2m.atl.core.ModelFactory;
import org.eclipse.m2m.atl.core.emf.EMFExtractor;
import org.eclipse.m2m.atl.core.emf.EMFInjector;
import org.eclipse.m2m.atl.core.emf.EMFModelFactory;
import org.eclipse.m2m.atl.engine.compiler.atl2006.Atl2006Compiler;
import org.eclipse.m2m.atl.engine.emfvm.launch.EMFVMLauncher;

/** Shared execution harness; deliberately does not embed a reference ATL. */
public final class BenchmarkExecutionSupport {
    private BenchmarkExecutionSupport() { }

    public static Path[] inputs(String folder) throws Exception {
        try (Stream<Path> stream = Files.list(Path.of("src/main/resources/models", folder))) {
            Path[] files = stream.filter(p -> p.toString().endsWith(".xmi")).sorted().toArray(Path[]::new);
            assertTrue(files.length == 10, "Expected exactly 10 inputs in " + folder);
            return files;
        }
    }

    public static File compile(String module) throws Exception {
        File source = new File("src/main/atl", module + ".atl");
        assertTrue(source.isFile(), "Generate/copy the ATL module first: " + source);
        File asm = Files.createTempFile(module, ".asm").toFile();
        asm.deleteOnExit();
        try (Reader reader = new FileReader(source)) {
            new Atl2006Compiler().compile(reader, asm.getAbsolutePath());
        }
        assertTrue(asm.length() > 0, "ATL compilation produced no ASM");
        return asm;
    }

    public static void execute(File asm, String sourceMM, String targetMM,
                               String sourceAlias, String targetAlias,
                               Path input, String caseName) throws Exception {
        Path output = Path.of("target/benchmark-results", caseName, input.getFileName().toString());
        Files.createDirectories(output.getParent());
        Files.deleteIfExists(output); // do not score a stale output after a failed run
        ResourceSet rs = new ResourceSetImpl();
        rs.getResourceFactoryRegistry().getExtensionToFactoryMap().put("ecore", new EcoreResourceFactoryImpl());
        rs.getResourceFactoryRegistry().getExtensionToFactoryMap().put("xmi", new XMIResourceFactoryImpl());
        for (String mm : new String[] {sourceMM, targetMM}) {
            File path = new File("src/main/resources/metamodels", mm);
            Resource r = rs.getResource(URI.createFileURI(path.getAbsolutePath()), true);
            EPackage pkg = (EPackage) r.getContents().get(0);
            EPackage.Registry.INSTANCE.put(pkg.getNsURI(), pkg);
        }

        ModelFactory factory = new EMFModelFactory();
        EMFInjector injector = new EMFInjector();
        IReferenceModel inMM = factory.newReferenceModel();
        IReferenceModel outMM = factory.newReferenceModel();
        injector.inject(inMM, URI.createFileURI(new File("src/main/resources/metamodels", sourceMM).getAbsolutePath()).toString());
        injector.inject(outMM, URI.createFileURI(new File("src/main/resources/metamodels", targetMM).getAbsolutePath()).toString());
        IModel inModel = factory.newModel(inMM);
        injector.inject(inModel, URI.createFileURI(input.toFile().getAbsolutePath()).toString());
        IModel outModel = factory.newModel(outMM);
        EMFVMLauncher launcher = new EMFVMLauncher();
        launcher.initialize(null);
        launcher.addInModel(inModel, "IN", sourceAlias);
        launcher.addOutModel(outModel, "OUT", targetAlias);
        Map<String, Object> options = new HashMap<>();
        try (InputStream stream = Files.newInputStream(asm.toPath())) {
            launcher.launch("run", null, options, stream);
        }

        new EMFExtractor().extract(outModel, URI.createFileURI(output.toFile().getAbsolutePath()).toString());
        Resource out = rs.getResource(URI.createFileURI(output.toFile().getAbsolutePath()), true);
        assertFalse(out.getContents().isEmpty(), "Empty output for " + input);
        assertTrue(out.getErrors().isEmpty(), "Invalid output for " + input + ": " + out.getErrors());
    }
}
