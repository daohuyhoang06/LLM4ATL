package com.example.atlverification;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Path;
import org.eclipse.emf.ecore.EAnnotation;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EPackage;
import org.junit.jupiter.api.Test;

class ATL2TMShapeVUnionTest {
    private static final Path FIXTURE = Path.of("src", "test", "resources");
    private static final Path ATL2TM = Path.of("..", "Neuro_Symbolic_Pipeline",
            "pipeline", "formal_verification", "hot-atl2tm", "ATL2TM.generated.atl");
    private static final String PIVOT = "http://www.eclipse.org/emf/2002/Ecore/OCL/Pivot";

    @Test
    void nestedCollectWithoutFlattenDoesNotDropTheUnionBranch() {
        Path work = Path.of("target", "shape-v-union-nested-unflattened");
        String message = assertThrows(ATL2TMRunner.UnsupportedAtlConstructException.class,
                () -> new ATL2TMRunner().run(
                        FIXTURE.resolve("shape-v/union-nested-unflattened.atl"),
                        FIXTURE.resolve("ordinary-lazy/collect-expression-src.ecore"),
                        FIXTURE.resolve("ordinary-lazy/collect-tgt.ecore"),
                        ATL2TM, work, work.resolve("tm.ecore")))
                .getMessage();
        assertTrue(message.contains("__ATL2TM_UNSUPPORTED_EXPRESSION__SHAPE_V_BRANCH__"), message);
    }

    @Test
    void flattenedNestedUnionResolvesBothMatchedBranches() throws Exception {
        Path work = Path.of("target", "shape-v-union-nested-flattened");
        Path output = work.resolve("tm.ecore");
        new ATL2TMRunner().run(
                FIXTURE.resolve("shape-v/union-nested-flattened.atl"),
                FIXTURE.resolve("ordinary-lazy/collect-expression-src.ecore"),
                FIXTURE.resolve("ordinary-lazy/collect-tgt.ecore"),
                ATL2TM, work, output);
        EPackage model = new EcoreModelLoader().load(output);
        EClass trace = assertInstanceOf(EClass.class, model.getEClassifier("Box2Box"));
        EAnnotation ocl = trace.getEAnnotation(PIVOT);
        String binding = ocl.getDetails().get("bind_Box2Box_t_tags");
        assertTrue(binding.contains("self.s.primary->collect"), binding);
        assertTrue(binding.contains("self.s.groups->collect(g | "
                + "g.items->select(i | i.isKey))->flatten()->asSet()->collect"), binding);
        assertTrue(binding.indexOf("Item2Tag.allInstances()")
                != binding.lastIndexOf("Item2Tag.allInstances()"), binding);
        assertFalse(binding.contains("__ATL2TM_UNSUPPORTED"), binding);
    }

    @Test
    void existingSimpleUnionAndScalarBindingsRemainTranslated() throws Exception {
        Path paper = FIXTURE.resolve("er2rel-paper");
        Path work = Path.of("target", "shape-v-er2rel-paper-regression");
        Path output = work.resolve("tm.ecore");
        new ATL2TMRunner().run(paper.resolve("ER2REL.atl"),
                paper.resolve("ER.ecore"), paper.resolve("REL.ecore"),
                ATL2TM, work, output);
        EPackage model = new EcoreModelLoader().load(output);
        EClass schemaTrace = assertInstanceOf(EClass.class, model.getEClassifier("S2S"));
        String union = schemaTrace.getEAnnotation(PIVOT).getDetails()
                .get("bind_S2S_t_relations");
        assertTrue(union.contains("E2R.allInstances()"), union);
        assertTrue(union.contains("R2R.allInstances()"), union);
        EClass attrTrace = assertInstanceOf(EClass.class, model.getEClassifier("EA2A"));
        assertTrue(attrTrace.getEAnnotation(PIVOT).getDetails()
                .get("bind_EA2A_t_name").contains("self.att.name"));
    }
}
