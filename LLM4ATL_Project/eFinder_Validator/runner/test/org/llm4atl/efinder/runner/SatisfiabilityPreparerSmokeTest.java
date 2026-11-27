package org.llm4atl.efinder.runner;

import java.nio.file.Files;
import java.nio.file.Path;

/** Plain-JDK regression: preserve explicit premises and semantics without extra existence axioms. */
public final class SatisfiabilityPreparerSmokeTest {
    public static void main(String[] args) throws Exception {
        Path fixtures = Path.of(args[0]);
        Path output = Path.of(args[1]);
        var prepared = EcoreCounterexamplePreparer.prepareSatisfiability(
                fixtures.resolve("duplicate-name-atl2tm.ecore"), output, null);
        String xml = Files.readString(prepared.ecore());
        if (!"Sem AND Pre".equals(prepared.verificationFormula())
                || xml.contains("NonEmptySource") || xml.contains("allInstances()->notEmpty()")) {
            throw new AssertionError("Baseline must not add source existence requirements");
        }
        if (xml.contains("key=\"targetConstraint\"") || !xml.contains("key=\"targetSem\"")
                || !xml.contains("key=\"sourceConstraint\"")) {
            throw new AssertionError("Baseline must preserve Sem and disable target properties");
        }
        var contradictory = EcoreCounterexamplePreparer.prepareSatisfiability(
                fixtures.resolve("duplicate-name-atl2tm.ecore"), output.resolve("contradiction"),
                fixtures.resolve("baseline-contradiction"));
        if (!Files.readString(contradictory.ecore()).contains("key=\"ImpossiblePremise\" value=\"false\"")) {
            throw new AssertionError("Explicit global preconditions must remain enabled");
        }
        System.out.println("Satisfiability preparer regression: PASS");
    }
}
