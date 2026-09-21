package org.llm4atl.efinder.runner;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.regex.Pattern;

/**
 * Plain-JDK smoke test for the Ecore rewrite. Usage:
 * {@code java ...EcoreCounterexamplePreparerSmokeTest input.ecore temp-dir C::invariant [constraints-path]}.
 */
public final class EcoreCounterexamplePreparerSmokeTest {
    private EcoreCounterexamplePreparerSmokeTest() {}

    public static void main(String[] args) throws Exception {
        if (args.length != 3 && args.length != 4) {
            throw new IllegalArgumentException("expected: input.ecore temp-dir EClass::constraint [constraints-path]");
        }
        EcoreCounterexamplePreparer.Check check = EcoreCounterexamplePreparer.Check.parse(args[2]);
        EcoreCounterexamplePreparer.PreparedModel prepared = EcoreCounterexamplePreparer.prepare(
                Path.of(args[0]), Path.of(args[1]), check,
                args.length == 4 ? Path.of(args[3]) : null);
        String rewritten = Files.readString(prepared.ecore());
        if (!rewritten.contains(prepared.generatedConstraint()) || !rewritten.contains("allInstances()")) {
            throw new AssertionError("generated Ecore does not contain the expected existential negation");
        }
        if (!Pattern.compile("key=\\\"constraints\\\" value=\\\"[^\\\"]*"
                + Pattern.quote(prepared.generatedConstraint()))
                .matcher(rewritten).find()) {
            throw new AssertionError("generated negation is not enabled by the Ecore constraints list");
        }
        System.out.println(prepared.ecore());
    }
}
