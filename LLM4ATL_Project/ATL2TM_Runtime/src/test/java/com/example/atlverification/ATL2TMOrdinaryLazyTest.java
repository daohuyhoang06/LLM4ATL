package com.example.atlverification;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Path;
import org.eclipse.emf.ecore.EAnnotation;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EReference;
import org.junit.jupiter.api.Test;

class ATL2TMOrdinaryLazyTest {
    private static final String PIVOT = "http://www.eclipse.org/emf/2002/Ecore/OCL/Pivot";
    private static final String ECORE = "http://www.eclipse.org/emf/2002/Ecore";
    private static final Path FIXTURE = Path.of("src", "test", "resources", "ordinary-lazy");
    private static final Path ATL2TM = Path.of("..", "Neuro_Symbolic_Pipeline",
            "pipeline", "formal_verification", "ATL2TM.atl");

    @Test
    void twoDirectCallsToSameSourceProduceDistinctLazyExecutions() throws Exception {
        EPackage model = transform("two-calls.atl", "two-calls");
        EClass caller = assertInstanceOf(EClass.class, model.getEClassifier("Box2Box"));
        EClass lazy = assertInstanceOf(EClass.class, model.getEClassifier("Item2Tag"));
        EClass source = assertInstanceOf(EClass.class, model.getEClassifier("Item"));

        EReference call1 = assertInstanceOf(EReference.class,
                caller.getEStructuralFeature("__atl2tm_call_t_tag1"));
        EReference call2 = assertInstanceOf(EReference.class,
                caller.getEStructuralFeature("__atl2tm_call_t_tag2"));
        assertEquals(lazy, call1.getEType());
        assertEquals(lazy, call2.getEType());
        assertEquals(1, call1.getLowerBound());
        assertEquals(1, call2.getLowerBound());
        assertEquals(-1, ((EReference) source.getEStructuralFeature("Item2Tag_s"))
                .getUpperBound());

        String callerConstraints = annotation(caller, ECORE).getDetails().get("constraints");
        String lazyConstraints = annotation(lazy, ECORE).getDetails().get("constraints");
        assertTrue(callerConstraints.contains("call_Box2Box_t_tag1_argument"));
        assertTrue(callerConstraints.contains("call_Box2Box_t_tag2_argument"));
        assertTrue(lazyConstraints.contains("call_Item2Tag_owner"));
        assertEquals("(if self.__atl2tm_caller_Box2Box_t_tag1.oclIsUndefined() then 0 else 1 endif)"
                        + " + (if self.__atl2tm_caller_Box2Box_t_tag2.oclIsUndefined() then 0 else 1 endif) = 1",
                annotation(lazy, PIVOT).getDetails().get("call_Item2Tag_owner"));
        EAnnotation sourceConstraints = source.getEAnnotation(ECORE);
        assertFalse(sourceConstraints != null
                && String.valueOf(sourceConstraints.getDetails().get("constraints"))
                        .contains("match_Item2Tag"));
    }

    @Test
    void unusedLazyRuleCannotCreateAnUncalledTrace() throws Exception {
        EPackage model = transform("zero-calls.atl", "zero-calls");
        EClass lazy = assertInstanceOf(EClass.class, model.getEClassifier("Item2Tag"));
        assertEquals("false", annotation(lazy, PIVOT)
                .getDetails().get("call_Item2Tag_owner"));
    }

    @Test
    void oneDirectCallGetsOneMandatoryLazySlot() throws Exception {
        EPackage model = transform("one-call.atl", "one-call");
        EClass caller = assertInstanceOf(EClass.class, model.getEClassifier("Box2Box"));
        EClass lazy = assertInstanceOf(EClass.class, model.getEClassifier("Item2Tag"));
        assertInstanceOf(EReference.class,
                caller.getEStructuralFeature("__atl2tm_call_t_tag1"));
        assertEquals("(if self.__atl2tm_caller_Box2Box_t_tag1.oclIsUndefined()"
                        + " then 0 else 1 endif) = 1",
                annotation(lazy, PIVOT).getDetails().get("call_Item2Tag_owner"));
    }

    @Test
    void collectionCallsAndUniqueLazyRulesRemainUnsupported() {
        assertTrue(assertThrows(ATL2TMRunner.UnsupportedAtlConstructException.class,
                () -> transform("collect-calls.atl", "collect-calls"))
                .getMessage().contains("only a direct one-argument call"));
        assertTrue(assertThrows(ATL2TMRunner.UnsupportedAtlConstructException.class,
                () -> transform("unique-call.atl", "unique-call"))
                .getMessage().contains("unique lazy rule semantics"));
    }

    @Test
    void existingMatchedRuleTranslationStillHasUniversalMatchConstraint() throws Exception {
        Path fixture = Path.of("src", "test", "resources", "er2rel-paper");
        Path workDir = Path.of("target", "ordinary-lazy-matched-regression");
        Path output = workDir.resolve("tm.ecore");
        new ATL2TMRunner().run(fixture.resolve("ER2REL.atl"),
                fixture.resolve("ER.ecore"), fixture.resolve("REL.ecore"),
                ATL2TM, workDir, output);
        EPackage model = new EcoreModelLoader().load(output);
        EClass source = assertInstanceOf(EClass.class,
                model.getEClassifier("ERSchema"));
        assertTrue(annotation(source, ECORE).getDetails().get("constraints")
                .contains("match_S2S"));
    }

    private static EPackage transform(String atl, String work) throws Exception {
        Path workDir = Path.of("target", "ordinary-lazy-" + work);
        Path output = workDir.resolve("tm.ecore");
        new ATL2TMRunner().run(FIXTURE.resolve(atl), FIXTURE.resolve("src.ecore"),
                FIXTURE.resolve("tgt.ecore"), ATL2TM, workDir, output);
        return new EcoreModelLoader().load(output);
    }

    private static EAnnotation annotation(EClass type, String source) {
        return type.getEAnnotations().stream()
                .filter(a -> source.equals(a.getSource()))
                .findFirst()
                .orElseThrow(() -> new AssertionError("Missing annotation " + source));
    }
}
