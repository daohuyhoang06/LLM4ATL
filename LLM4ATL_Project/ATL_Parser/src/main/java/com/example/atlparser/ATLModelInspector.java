package com.example.atlparser;

import org.eclipse.emf.ecore.EAttribute;
import org.eclipse.emf.ecore.EObject;

public final class ATLModelInspector {

    private ATLModelInspector() {
    }

    public static void print(EObject object) {
        print(object, 0);
    }

    private static void print(EObject object, int depth) {
        String indent = "  ".repeat(depth);

        StringBuilder line = new StringBuilder();
        line.append(indent)
            .append(object.eClass().getName());

        for (EAttribute attribute :
                object.eClass().getEAllAttributes()) {

            Object value = object.eGet(attribute);

            if (value != null) {
                line.append(" ")
                    .append(attribute.getName())
                    .append("=")
                    .append(value);
            }
        }

        System.out.println(line);

        for (EObject child : object.eContents()) {
            print(child, depth + 1);
        }
    }
}