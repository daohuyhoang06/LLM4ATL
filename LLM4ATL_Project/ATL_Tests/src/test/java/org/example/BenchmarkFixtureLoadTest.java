package org.example;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;
import org.junit.jupiter.api.Test;

/** Checks that benchmark data really loads against the copied Ecore packages. */
public class BenchmarkFixtureLoadTest {
    private static final Path RES = Path.of("src/main/resources");

    private ResourceSet resourceSet(String... metamodels) {
        ResourceSet rs = new ResourceSetImpl();
        rs.getResourceFactoryRegistry().getExtensionToFactoryMap().put("ecore", new EcoreResourceFactoryImpl());
        rs.getResourceFactoryRegistry().getExtensionToFactoryMap().put("xmi", new XMIResourceFactoryImpl());
        rs.getResourceFactoryRegistry().getExtensionToFactoryMap().put("aas", new XMIResourceFactoryImpl());
        for (String name : metamodels) {
            File file = RES.resolve("metamodels").resolve(name).toFile();
            Resource resource = rs.getResource(URI.createFileURI(file.getAbsolutePath()), true);
            assertFalse(resource.getContents().isEmpty(), name);
            EPackage pkg = (EPackage) resource.getContents().get(0);
            rs.getPackageRegistry().put(pkg.getNsURI(), pkg);
        }
        return rs;
    }

    private void loadTen(ResourceSet rs, Path directory, String suffix) throws Exception {
        try (Stream<Path> paths = Files.list(directory)) {
            Path[] files = paths.filter(p -> p.toString().endsWith(suffix)).sorted().toArray(Path[]::new);
            assertEquals(10, files.length, directory.toString());
            for (Path file : files) {
                Resource resource = rs.getResource(URI.createFileURI(file.toFile().getAbsolutePath()), true);
                assertFalse(resource.getContents().isEmpty(), file.toString());
                assertFalse(resource.getErrors().iterator().hasNext(), file + " " + resource.getErrors());
            }
        }
    }

    @Test
    public void umlInputsLoad() throws Exception {
        loadTen(resourceSet("UML.ecore", "java.ecore"), RES.resolve("models/uml2java"), ".xmi");
    }

    @Test
    public void sysmlInputsAndAasOraclesLoad() throws Exception {
        ResourceSet rs = resourceSet("SysMLv2.ecore", "AAS.ecore");
        loadTen(rs, RES.resolve("models/sysml2aas/xmi"), ".xmi");
        loadTen(rs, RES.resolve("oracles/sysml2aas"), ".aas");
    }
}
