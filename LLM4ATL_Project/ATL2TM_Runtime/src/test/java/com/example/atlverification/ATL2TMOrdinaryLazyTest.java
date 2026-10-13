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
            "pipeline", "formal_verification", "hot-atl2tm", "ATL2TM.generated.atl");

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
    void unsupportedCollectionShapeAndUniqueLazyRulesRemainRejected() {
        assertTrue(assertThrows(ATL2TMRunner.UnsupportedAtlConstructException.class,
                () -> transform("collect-calls.atl", "collect-calls"))
                .getMessage().contains("direct call or a Set collect call"));
        assertTrue(assertThrows(ATL2TMRunner.UnsupportedAtlConstructException.class,
                () -> transform("unique-call.atl", "unique-call"))
                .getMessage().contains("unique lazy rule semantics"));
        String nonSetMessage = assertThrows(ATL2TMRunner.UnsupportedAtlConstructException.class,
                () -> transformCollect("collect-nonset.atl", "collect-nonset"))
                .getMessage();
        assertTrue(nonSetMessage.contains("pure OCL Set"), nonSetMessage);
        Path orderedWork = Path.of("target", "ordinary-lazy-collect-ordered");
        assertTrue(assertThrows(ATL2TMRunner.UnsupportedAtlConstructException.class,
                () -> new ATL2TMRunner().run(FIXTURE.resolve("collect-set.atl"),
                        FIXTURE.resolve("collect-ordered-src.ecore"),
                        FIXTURE.resolve("collect-tgt.ecore"), ATL2TM, orderedWork,
                        orderedWork.resolve("tm.ecore")))
                .getMessage().contains("pure OCL Set"));
    }

    @Test
    void nestedPureOclSetFeedsLazyCollect() throws Exception {
        EPackage model = transformCollectExpression(
                "collect-pure-expression.atl", "collect-pure-expression");
        EClass caller = assertInstanceOf(EClass.class, model.getEClassifier("Box2Box"));
        String coverage = annotation(caller, PIVOT).getDetails()
                .get("call_Box2Box_t_tags_coverage");
        String noExtra = annotation(caller, PIVOT).getDetails()
                .get("call_Box2Box_t_tags_noExtra");
        assertTrue(coverage.contains("self.s.groups->collect(g | "
                + "g.items->select(i | i.isKey))->flatten()->asSet()->forAll"));
        assertTrue(noExtra.contains("self.s.groups->collect(g | "
                + "g.items->select(i | i.isKey))->flatten()->asSet()->includes(c.s)"));
    }

    @Test
    void setUnionIsAnotherPureOclSourceExpression() throws Exception {
        EPackage model = transformCollectExpression(
                "collect-union-source.atl", "collect-union-source");
        EClass caller = assertInstanceOf(EClass.class, model.getEClassifier("Box2Box"));
        assertTrue(annotation(caller, PIVOT).getDetails()
                .get("call_Box2Box_t_tags_coverage")
                .contains("self.s.primary->union(self.s.secondary)->forAll"));
    }

    @Test
    void unionCombinesMatchedOutputsWithOneLazyCollectSite() throws Exception {
        EPackage model = transformCollectExpression(
                "union-matched-lazy.atl", "union-matched-lazy");
        EClass caller = assertInstanceOf(EClass.class, model.getEClassifier("Box2Box"));
        EClass lazy = assertInstanceOf(EClass.class, model.getEClassifier("Item2Tag"));
        EReference call = assertInstanceOf(EReference.class,
                caller.getEStructuralFeature("__atl2tm_calls_t_tags_u1"));
        assertEquals(lazy, call.getEType());
        assertEquals(-1, call.getUpperBound());
        assertFalse(call.isOrdered());
        String binding = annotation(caller, PIVOT).getDetails().get("bind_Box2Box_t_tags");
        assertTrue(binding.contains("ItemMatched"), binding);
        assertTrue(binding.contains("->union(self.__atl2tm_calls_t_tags_u1"), binding);
        assertTrue(annotation(caller, PIVOT).getDetails()
                .get("call_Box2Box_t_tags_u1_coverage")
                .contains("self.s.secondary->forAll"));
        assertTrue(annotation(lazy, PIVOT).getDetails()
                .get("call_Item2Tag_owner")
                .contains("__atl2tm_caller_Box2Box_t_tags_u1"));
    }

    @Test
    void nestedUnionKeepsTwoLazyCallSitesDistinct() throws Exception {
        EPackage model = transformCollectExpression(
                "union-nested-lazy.atl", "union-nested-lazy");
        EClass caller = assertInstanceOf(EClass.class, model.getEClassifier("Box2Box"));
        EClass lazy = assertInstanceOf(EClass.class, model.getEClassifier("Item2Tag"));
        assertInstanceOf(EReference.class,
                caller.getEStructuralFeature("__atl2tm_calls_t_tags_u1"));
        assertInstanceOf(EReference.class,
                caller.getEStructuralFeature("__atl2tm_calls_t_tags_u2"));
        String binding = annotation(caller, PIVOT).getDetails().get("bind_Box2Box_t_tags");
        assertTrue(binding.contains("__atl2tm_calls_t_tags_u1"), binding);
        assertTrue(binding.contains("__atl2tm_calls_t_tags_u2"), binding);
        String owner = annotation(lazy, PIVOT).getDetails().get("call_Item2Tag_owner");
        assertTrue(owner.contains("__atl2tm_caller_Box2Box_t_tags_u1"), owner);
        assertTrue(owner.contains("__atl2tm_caller_Box2Box_t_tags_u2"), owner);
    }

    @Test
    void er2relKeyExpressionCanFeedLazyCollectWithoutOuterUnion() throws Exception {
        Path workDir = Path.of("target", "ordinary-lazy-er2rel-source");
        Path output = workDir.resolve("tm.ecore");
        Path erEcore = Path.of("..", "Neuro_Symbolic_Pipeline", "input",
                "ATL_metamodel", "ER.ecore");
        new ATL2TMRunner().run(FIXTURE.resolve("collect-er2rel-flattened.atl"),
                erEcore, FIXTURE.resolve("collect-tgt.ecore"), ATL2TM,
                workDir, output);
        EPackage model = new EcoreModelLoader().load(output);
        EClass caller = assertInstanceOf(EClass.class,
                model.getEClassifier("Relship2Box"));
        assertTrue(annotation(caller, PIVOT).getDetails()
                .get("call_Relship2Box_t_tags_coverage")
                .contains("self.s.ends->collect(e | "
                        + "e.entity.attrs->select(a | a.isKey))->flatten()->asSet()->forAll"));
    }

    @Test
    void nestedCollectWithoutFlattenIsNotASetOfLazyInputs() {
        Path workDir = Path.of("target", "ordinary-lazy-er2rel-unflattened");
        Path erEcore = Path.of("..", "Neuro_Symbolic_Pipeline", "input",
                "ATL_metamodel", "ER.ecore");
        String message = assertThrows(ATL2TMRunner.UnsupportedAtlConstructException.class,
                () -> new ATL2TMRunner().run(
                        FIXTURE.resolve("collect-er2rel-source.atl"),
                        erEcore, FIXTURE.resolve("collect-tgt.ecore"),
                        ATL2TM, workDir, workDir.resolve("tm.ecore")))
                .getMessage();
        assertTrue(message.contains("pure OCL Set of source objects"), message);
    }

    @Test
    void setCollectCreatesOneTracePerSourceMemberWithoutOrphans() throws Exception {
        EPackage model = transformCollect("collect-set.atl", "collect-set");
        EClass caller = assertInstanceOf(EClass.class, model.getEClassifier("Box2Box"));
        EClass lazy = assertInstanceOf(EClass.class, model.getEClassifier("Item2Tag"));
        EClass target = assertInstanceOf(EClass.class, model.getEClassifier("BoxOut"));
        EReference calls = assertInstanceOf(EReference.class,
                caller.getEStructuralFeature("__atl2tm_calls_t_tags"));
        assertEquals(0, calls.getLowerBound());
        assertEquals(-1, calls.getUpperBound());
        assertFalse(calls.isOrdered());
        assertEquals(lazy, calls.getEType());
        assertEquals("self.t.tags = self.__atl2tm_calls_t_tags->collect(c | c.t)->asSet()",
                annotation(caller, PIVOT).getDetails().get("bind_Box2Box_t_tags"));
        assertEquals("self.s.items->forAll(i | self.__atl2tm_calls_t_tags"
                        + "->one(c | c.s = i))",
                annotation(caller, PIVOT).getDetails().get("call_Box2Box_t_tags_coverage"));
        assertEquals("self.__atl2tm_calls_t_tags->forAll(c | self.s.items->includes(c.s))",
                annotation(caller, PIVOT).getDetails().get("call_Box2Box_t_tags_noExtra"));
        assertEquals("(if self.__atl2tm_caller_Box2Box_t_tags.oclIsUndefined()"
                        + " then 0 else 1 endif) = 1",
                annotation(lazy, PIVOT).getDetails().get("call_Item2Tag_owner"));
        assertEquals(-1, ((EReference) target.getEStructuralFeature("tags")).getUpperBound());
    }

    @Test
    void directAndCollectCallsShareExclusiveOwnerConstraint() throws Exception {
        EPackage model = transformCollect("collect-and-direct.atl", "collect-and-direct");
        EClass lazy = assertInstanceOf(EClass.class, model.getEClassifier("Item2Tag"));
        assertEquals("(if self.__atl2tm_caller_Box2Box_t_tag1.oclIsUndefined()"
                        + " then 0 else 1 endif) + "
                        + "(if self.__atl2tm_caller_Box2Box_t_tags.oclIsUndefined()"
                        + " then 0 else 1 endif) = 1",
                annotation(lazy, PIVOT).getDetails().get("call_Item2Tag_owner"));
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

    private static EPackage transformCollect(String atl, String work) throws Exception {
        Path workDir = Path.of("target", "ordinary-lazy-" + work);
        Path output = workDir.resolve("tm.ecore");
        new ATL2TMRunner().run(FIXTURE.resolve(atl), FIXTURE.resolve("collect-src.ecore"),
                FIXTURE.resolve("collect-tgt.ecore"), ATL2TM, workDir, output);
        return new EcoreModelLoader().load(output);
    }

    private static EPackage transformCollectExpression(String atl, String work)
            throws Exception {
        Path workDir = Path.of("target", "ordinary-lazy-" + work);
        Path output = workDir.resolve("tm.ecore");
        new ATL2TMRunner().run(FIXTURE.resolve(atl),
                FIXTURE.resolve("collect-expression-src.ecore"),
                FIXTURE.resolve("collect-tgt.ecore"), ATL2TM, workDir, output);
        return new EcoreModelLoader().load(output);
    }

    private static EAnnotation annotation(EClass type, String source) {
        return type.getEAnnotations().stream()
                .filter(a -> source.equals(a.getSource()))
                .findFirst()
                .orElseThrow(() -> new AssertionError("Missing annotation " + source));
    }
}
