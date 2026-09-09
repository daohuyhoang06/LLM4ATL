package com.example.atlparser;

import org.eclipse.emf.ecore.EObject;

import java.nio.file.Path;

public class ATLParserMain {

    public static void main(String[] args) {

        if (args.length < 1) {
            System.err.println(
                    "Usage: ATLParserMain <atl-file>"
            );
            System.exit(1);
        }

        Path atlPath = Path.of(args[0]);

        ATLModelLoader loader =
                new ATLModelLoader();

        try {
            EObject atlModel =
                    loader.load(atlPath);

            // System.out.println("=== MODULE FEATURES ===");

            // for (var feature : atlModel.eClass().getEAllStructuralFeatures()) {

            //     Object value = atlModel.eGet(feature);

            //     System.out.println(
            //         feature.getName()
            //         + " : "
            //         + feature.getEType().getName()
            //         + " many="
            //         + feature.isMany()
            //         + " value="
            //         + value
            //     );
            // }

            ATLModelInspector.print(atlModel);

            System.out.println("RESULT:OK:0");

            System.err.println(
                    "ATL root type: "
                    + atlModel.eClass().getName()
            );

        } catch (ATLParseException e) {

            System.out.println(
                    "RESULT:FAIL:"
                    + e.getProblemCount()
            );

            System.err.println(
                    "FAIL: "
                    + atlPath
            );

            System.err.println(
                    e.getMessage()
            );

            System.exit(1);
        }
    }
}