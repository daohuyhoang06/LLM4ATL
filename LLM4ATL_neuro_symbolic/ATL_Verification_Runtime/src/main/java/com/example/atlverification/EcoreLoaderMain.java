package com.example.atlverification;

import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EClassifier;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EReference;

import java.nio.file.Path;

public class EcoreLoaderMain {

    public static void main(String[] args) {

        if (args.length < 2) {
            System.err.println(
                    "Usage: EcoreLoaderMain "
                    + "<source.ecore> <target.ecore>"
            );

            System.exit(1);
        }

        try {
            EcoreModelLoader loader =
                    new EcoreModelLoader();

            EPackage source =
                    loader.load(Path.of(args[0]));

            EPackage target =
                    loader.load(Path.of(args[1]));

            loader.resolveAll();

            printPackage("SOURCE", source);
            printPackage("TARGET", target);

            System.out.println("RESULT:OK");

        } catch (Exception e) {

            System.out.println("RESULT:FAIL");

            System.err.println(
                    "ERROR: " + e.getMessage()
            );

            System.exit(1);
        }
    }

    private static void printPackage(
            String label,
            EPackage ePackage
    ) {
        System.out.println();
        System.out.println(
                label + " PACKAGE: "
                        + ePackage.getName()
        );

        System.out.println(
                "nsURI: " + ePackage.getNsURI()
        );

        for (EClassifier classifier
                : ePackage.getEClassifiers()) {

            System.out.println(
                    "- "
                    + classifier.eClass().getName()
                    + " "
                    + classifier.getName()
            );

            if (!(classifier instanceof EClass eClass)) {
                continue;
            }

            if (!eClass.getESuperTypes().isEmpty()) {
                System.out.println(
                        "    superTypes="
                                + eClass.getESuperTypes()
                                        .stream()
                                        .map(EClass::getName)
                                        .toList()
                );
            }

            eClass.getEStructuralFeatures()
                    .forEach(feature -> {

                        String upper =
                                feature.getUpperBound() == -1
                                        ? "*"
                                        : Integer.toString(
                                                feature.getUpperBound()
                                        );

                        System.out.println(
                                "    "
                                + feature.eClass().getName()
                                + " "
                                + feature.getName()
                                + " ["
                                + feature.getLowerBound()
                                + ".."
                                + upper
                                + "]"
                                + " type="
                                + feature.getEType().getName()
                        );

                        if (feature instanceof EReference ref) {

                            System.out.println(
                                    "        target="
                                    + ref.getEReferenceType()
                                         .getName()
                            );

                            System.out.println(
                                    "        containment="
                                    + ref.isContainment()
                            );

                            if (ref.getEOpposite() != null) {

                                System.out.println(
                                        "        opposite="
                                        + ref.getEOpposite()
                                             .getEContainingClass()
                                             .getName()
                                        + "."
                                        + ref.getEOpposite()
                                             .getName()
                                );
                            }
                        }
                    });
        }
    }
}