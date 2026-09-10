package org.llm4atl.efinder.runner;

import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Plain-JDK smoke test for the Ecore rewrite. Usage:
 * {@code java ...EcoreCounterexamplePreparerSmokeTest input.ecore temp-dir C::invariant}.
 */
public final class EcoreCounterexamplePreparerSmokeTest {
    private EcoreCounterexamplePreparerSmokeTest() {}

    public static void main(String[] args) throws Exception {
        if (args.length != 3) {
            throw new IllegalArgumentException("expected: input.ecore temp-dir EClass::constraint");
        }
        EcoreCounterexamplePreparer.Check check = EcoreCounterexamplePreparer.Check.parse(args[2]);
        EcoreCounterexamplePreparer.PreparedModel prepared = EcoreCounterexamplePreparer.prepare(
                Path.of(args[0]), Path.of(args[1]), check);
        String rewritten = Files.readString(prepared.ecore());
        if (!rewritten.contains(prepared.generatedConstraint()) || !rewritten.contains("allInstances()")) {
            throw new AssertionError("generated Ecore does not contain the expected existential negation");
        }
        System.out.println(prepared.ecore());
    }
}
