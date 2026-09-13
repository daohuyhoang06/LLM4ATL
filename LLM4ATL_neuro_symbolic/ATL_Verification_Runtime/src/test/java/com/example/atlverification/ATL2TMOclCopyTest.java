package com.example.atlverification;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;

import java.nio.file.Path;
import java.util.Objects;

import org.eclipse.emf.ecore.EAnnotation;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EPackage;
import org.junit.jupiter.api.Test;

/**
 * Verifies that Pivot OCL embedded in input metamodels is retained in the
 * transformation model and classified by its source/target role.
 */
class ATL2TMOclCopyTest {

    private static final String ECORE = "http://www.eclipse.org/emf/2002/Ecore";
    private static final String PIVOT = "http://www.eclipse.org/emf/2002/Ecore/OCL/Pivot";
    private static final String PROVENANCE = "urn:llm4atl:provenance";

    @Test
    void classifiesEmbeddedSourceAndTargetPivotOcl() throws Exception {
        Path fixture = Path.of("src", "test", "resources", "ocl-copy-test");
        Path workDir = Path.of("target", "ocl-copy-test-work");
        Path output = workDir.resolve("ocl-copy-test_TM.ecore");
        Path atl2tm = Path.of(
                "..",
                "Neuro-Symbolic Pipeline",
                "pipeline",
                "formal_verification",
                "atl",
                "transformations",
                "ATL2TM.atl"
        );

        new ATL2TMRunner().run(
                fixture.resolve("OclCopyTest.atl"),
                fixture.resolve("src.ecore"),
                fixture.resolve("tgt.ecore"),
                atl2tm,
                workDir,
                output
        );

        EPackage model = new EcoreModelLoader().load(output);
        EClass source = assertInstanceOf(EClass.class, model.getEClassifier("A"));
        EClass target = assertInstanceOf(EClass.class, model.getEClassifier("B"));

        assertEquals("source", annotation(source, PROVENANCE).getDetails().get("origin"));
        assertEquals("positiveAge", annotation(source, PROVENANCE)
                .getDetails().get("preConstraints"));
        assertEquals("positiveAge match_A2B", annotation(source, ECORE)
                .getDetails().get("constraints"));
        assertEquals("self.age >= 0", annotation(source, PIVOT)
                .getDetails().get("positiveAge"));

        assertEquals("target", annotation(target, PROVENANCE).getDetails().get("origin"));
        assertEquals("nonEmptyName", annotation(target, PROVENANCE)
                .getDetails().get("postConstraints"));
        assertEquals("nonEmptyName create_B", annotation(target, ECORE)
                .getDetails().get("constraints"));
        assertEquals("self.name <> ''", annotation(target, PIVOT)
                .getDetails().get("nonEmptyName"));
        assertEquals(
                "(if self.A2B_b.oclIsUndefined() then 0 else 1 endif) = 1",
                annotation(target, PIVOT).getDetails().get("create_B")
        );
    }

    @Test
    void encodesMultipleScalarCreatorsAsDefinednessIndicators() throws Exception {
        Path fixture = Path.of("src", "test", "resources", "mutex-unrelated");
        Path workDir = Path.of("target", "scalar-creator-test-work");
        Path output = workDir.resolve("scalar-creator_TM.ecore");
        Path atl2tm = Path.of(
                "..",
                "Neuro-Symbolic Pipeline",
                "pipeline",
                "formal_verification",
                "atl",
                "transformations",
                "ATL2TM.atl"
        );

        new ATL2TMRunner().run(
                fixture.resolve("Mutex_Unrelated.atl"),
                fixture.resolve("src.ecore"),
                fixture.resolve("tgt.ecore"),
                atl2tm,
                workDir,
                output
        );

        EPackage model = new EcoreModelLoader().load(output);
        EClass target = assertInstanceOf(EClass.class, model.getEClassifier("T"));
        assertEquals(
                "(if self.A2T_t1.oclIsUndefined() then 0 else 1 endif)"
                        + " + (if self.C2T_t2.oclIsUndefined() then 0 else 1 endif) = 1",
                annotation(target, PIVOT).getDetails().get("create_T")
        );
    }

    private static EAnnotation annotation(
            org.eclipse.emf.ecore.EModelElement element,
            String source
    ) {
        return element.getEAnnotations().stream()
                .filter(annotation -> Objects.equals(source, annotation.getSource()))
                .findFirst()
                .orElseThrow(() -> new AssertionError(
                        "Missing annotation: " + source
                ));
    }
}
