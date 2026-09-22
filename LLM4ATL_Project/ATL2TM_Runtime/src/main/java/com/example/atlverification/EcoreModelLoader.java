package com.example.atlverification;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EcorePackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;

import java.nio.file.Files;
import java.nio.file.Path;

public class EcoreModelLoader {

    private final ResourceSet resourceSet;

    public EcoreModelLoader() {
        resourceSet = new ResourceSetImpl();

        resourceSet
                .getResourceFactoryRegistry()
                .getExtensionToFactoryMap()
                .put(
                        "ecore",
                        new EcoreResourceFactoryImpl()
                );

        resourceSet
                .getPackageRegistry()
                .put(
                        EcorePackage.eNS_URI,
                        EcorePackage.eINSTANCE
                );
    }

    public EPackage load(Path ecorePath) {
        validate(ecorePath);

        URI uri = URI.createFileURI(
                ecorePath
                        .toAbsolutePath()
                        .normalize()
                        .toString()
        );

        Resource resource =
                resourceSet.getResource(uri, true);

        if (!resource.getErrors().isEmpty()) {
            throw new IllegalStateException(
                    "Failed to load Ecore file: "
                            + resource.getErrors()
            );
        }

        if (resource.getContents().isEmpty()) {
            throw new IllegalStateException(
                    "Empty Ecore file: " + ecorePath
            );
        }

        Object root =
                resource.getContents().get(0);

        if (!(root instanceof EPackage ePackage)) {
            throw new IllegalStateException(
                    "Root element is not EPackage: "
                            + ecorePath
            );
        }

        return ePackage;
    }

    public void resolveAll() {
        EcoreUtil.resolveAll(resourceSet);
    }

    public ResourceSet getResourceSet() {
        return resourceSet;
    }

    private void validate(Path path) {
        if (path == null) {
            throw new IllegalArgumentException(
                    "Ecore path must not be null"
            );
        }

        if (!Files.exists(path)) {
            throw new IllegalArgumentException(
                    "Ecore file not found: " + path
            );
        }

        if (!Files.isRegularFile(path)) {
            throw new IllegalArgumentException(
                    "Not a file: " + path
            );
        }

        if (!path.toString()
                .toLowerCase()
                .endsWith(".ecore")) {
            throw new IllegalArgumentException(
                    "Expected .ecore file: " + path
            );
        }
    }
}