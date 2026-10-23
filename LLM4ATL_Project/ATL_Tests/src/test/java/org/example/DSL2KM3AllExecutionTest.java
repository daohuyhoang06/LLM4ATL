package org.example;

import static org.junit.jupiter.api.Assertions.*;

import java.io.File;
import java.io.FileReader;
import java.io.Reader;
import java.nio.file.Files;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.emf.common.util.EList;
import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;
import org.eclipse.m2m.atl.core.IExtractor;
import org.eclipse.m2m.atl.core.IInjector;
import org.eclipse.m2m.atl.core.IModel;
import org.eclipse.m2m.atl.core.IReferenceModel;
import org.eclipse.m2m.atl.core.ModelFactory;
import org.eclipse.m2m.atl.core.emf.EMFExtractor;
import org.eclipse.m2m.atl.core.emf.EMFInjector;
import org.eclipse.m2m.atl.core.emf.EMFModelFactory;
import org.eclipse.m2m.atl.engine.compiler.atl2006.Atl2006Compiler;
import org.eclipse.m2m.atl.engine.emfvm.launch.EMFVMLauncher;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

/**
 * Integration test for the DSL→KM3 transformation. The test
 * loads a concrete DSL model and verifies that the resulting
 * KM3 model contains the expected elements.
 */
public class DSL2KM3AllExecutionTest {

    private ResourceSet rs;
    private EPackage dslPkg;
    private EPackage km3Pkg;

    @BeforeEach
    // Initialize a new resource set and load the DSL and KM3 metamodels.
    public void initResourceSet() {
        rs = new ResourceSetImpl();
        dslPkg = loadAndRegisterEcore(rs, "src/main/resources/metamodels/DSL.ecore");
        km3Pkg = loadAndRegisterEcore(rs, "src/main/resources/metamodels/KM3.ecore");
    }
    
    @BeforeAll
    // Register resource factories for XMI and Ecore files once before all tests.
    public static void registerResourceFactories() {
        // Register the factories for XMI and Ecore files
        Resource.Factory.Registry reg = Resource.Factory.Registry.INSTANCE;
        Map<String, Object> extensionToFactoryMap = reg.getExtensionToFactoryMap();
        extensionToFactoryMap.put("xmi", new XMIResourceFactoryImpl());
        extensionToFactoryMap.put("ecore", new EcoreResourceFactoryImpl());
    }

    // Compile the given ATL file to a temporary ASM file and return it.
    private File compileAtl(String atlFileName) throws Exception {
        String atlOverride = System.getProperty("atl.test.file");
        File atlFile = atlOverride == null || atlOverride.isBlank()
                ? new File("src/main/atl", atlFileName)
                : new File(atlOverride);
        assertTrue(atlFile.exists(), "ATL file not found: " + atlFile.getAbsolutePath());
        File asmFile = Files.createTempFile("atltest", ".asm").toFile();
        asmFile.deleteOnExit();
        try (Reader reader = new FileReader(atlFile)) {
            new Atl2006Compiler().compile(reader, asmFile.getAbsolutePath());
        }
        assertTrue(asmFile.length() > 0, "Compiled ASM file is empty for " + atlFileName);
        return asmFile;
    }

    // Load an Ecore metamodel from the given path and register it in the
    // package registry of the given resource set.  Returns the loaded EPackage.
    private EPackage loadAndRegisterEcore(ResourceSet rs, String ecorePath) {
        URI uri = URI.createFileURI(new File(ecorePath).getAbsolutePath());
        Resource res = rs.getResource(uri, true);
        EPackage pkg = (EPackage) res.getContents().get(0);
        rs.getPackageRegistry().put(pkg.getNsURI(), pkg);
        return pkg;
    }

    // Execute the given ATL transformation and return the output resource.
    private Resource executeAtl(File asmFile, String inEcore, String outEcore, String inAlias, String outAlias, File inputXmi) throws Exception {
        ModelFactory factory = new EMFModelFactory();
        IInjector injector = new EMFInjector();
        IExtractor extractor = new EMFExtractor();
        IReferenceModel inMM = factory.newReferenceModel();
        injector.inject(inMM, URI.createFileURI(new File("src/main/resources/metamodels", inEcore).getAbsolutePath()).toString());
        IReferenceModel outMM = factory.newReferenceModel();
        injector.inject(outMM, URI.createFileURI(new File("src/main/resources/metamodels", outEcore).getAbsolutePath()).toString());
        IModel inModel = factory.newModel(inMM);
        injector.inject(inModel, URI.createFileURI(inputXmi.getAbsolutePath()).toString());
        IModel outModel = factory.newModel(outMM);
        EMFVMLauncher launcher = new EMFVMLauncher();
        launcher.initialize(null);
        launcher.addInModel(inModel, "IN", inAlias);
        launcher.addOutModel(outModel, "OUT", outAlias);
        Map<String,Object> options = new HashMap<>();
        try (java.io.InputStream is = new java.io.FileInputStream(asmFile)) {
            launcher.launch("run", null, options, is);
        }
        // Extract to temporary file
        File outFile = Files.createTempFile("atlOut", ".xmi").toFile();
        outFile.deleteOnExit();
        extractor.extract(outModel, URI.createFileURI(outFile.getAbsolutePath()).toString());
        // Load output resource into the test's resource set
        return rs.getResource(URI.createFileURI(outFile.getAbsolutePath()), true);
    }

    @ParameterizedTest
    @ValueSource(strings = {"dsl_input.xmi", "dsl_input_2.xmi"})
    public void testDSL2KM3(String inputFileName) throws Exception {
        // Compile the ATL module
        File asm = compileAtl("DSL2KM3_All.atl");
        // Use the provided DSL input model
        File input = new File("src/main/resources/models/DSL2KM3_All", inputFileName);
        assertTrue(input.exists(), inputFileName + " not found: " + input.getAbsolutePath());

        // Register the DSL metamodel in the global package registry.
        // The ATL injector will use this to resolve the namespace when loading the input XMI.
        EPackage.Registry.INSTANCE.put(dslPkg.getNsURI(), dslPkg);
        
        // Execute the transformation
        Resource outRes = executeAtl(asm, "DSL.ecore", "KM3.ecore", "DSL", "KM3", input);
        
        // Validate the resulting KM3 model.
        assertTrue(!outRes.getContents().isEmpty(), "Output model is empty");
        
        EClass metamodelCls = (EClass) km3Pkg.getEClassifier("Metamodel");
        EClass packageCls = (EClass) km3Pkg.getEClassifier("Package");
        
        int metamodelCount = 0;
        int packageCount = 0;
        EObject metamodel = null;
        
        for (TreeIterator<EObject> it = outRes.getAllContents(); it.hasNext(); ) {
            EObject obj = it.next();
            if (metamodelCls.isInstance(obj)) {
                metamodelCount++;
                metamodel = obj;
            }
            if (packageCls.isInstance(obj)) {
                packageCount++;
            }
        }
        
        assertEquals(1, metamodelCount, "Expected one KM3 Metamodel");
        assertTrue(packageCount >= 1, "Expected at least one Package (domain package and PrimitiveTypes)");
        assertNotNull(metamodel, "Metamodel is null");
        
        // Verify Metamodel contains packages
        @SuppressWarnings("unchecked")
        EList<EObject> packages = (EList<EObject>) metamodel.eGet(metamodelCls.getEStructuralFeature("contents"));
        assertTrue(packages.size() >= 1, "Metamodel should contain at least one package");
    }

    @Test
    public void counterexampleNamespacePrimitiveTypesStillHasDistinctMainPackage() throws Exception {
        File asm = compileAtl("DSL2KM3_All.atl");
        File input = new File(
                "src/main/resources/models/DSL2KM3_All",
                "dsl_input_1.xmi");
        assertTrue(input.exists(), "Counterexample input not found: " + input.getAbsolutePath());
        EPackage.Registry.INSTANCE.put(dslPkg.getNsURI(), dslPkg);

        Resource outRes = executeAtl(asm, "DSL.ecore", "KM3.ecore", "DSL", "KM3", input);
        assertFalse(outRes.getContents().isEmpty(), "Output model is empty");

        EClass metamodelCls = (EClass) km3Pkg.getEClassifier("Metamodel");
        EClass packageCls = (EClass) km3Pkg.getEClassifier("Package");
        EClass modelElementCls = (EClass) km3Pkg.getEClassifier("ModelElement");
        EObject metamodel = outRes.getContents().get(0);
        assertTrue(metamodelCls.isInstance(metamodel), "Expected one KM3 Metamodel root");

        @SuppressWarnings("unchecked")
        EList<EObject> contents = (EList<EObject>) metamodel.eGet(
                metamodelCls.getEStructuralFeature("contents"));
        long primitivePackages = 0;
        long mainPackages = 0;
        for (EObject content : contents) {
            if (!packageCls.isInstance(content)) {
                continue;
            }
            String name = (String) content.eGet(modelElementCls.getEStructuralFeature("name"));
            if ("PrimitiveTypes".equals(name)) {
                primitivePackages++;
            } else if (name != null && !name.isBlank()) {
                mainPackages++;
            }
        }

        assertEquals(2, contents.size(), "Metamodel must contain exactly the main and primitive packages");
        assertEquals(1, primitivePackages, "Expected exactly one PrimitiveTypes package");
        assertEquals(1, mainPackages, "Expected exactly one non-empty main package distinct from PrimitiveTypes");
    }

}

