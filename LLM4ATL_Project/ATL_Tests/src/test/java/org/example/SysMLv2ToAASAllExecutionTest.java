package org.example;

import java.io.File;
import java.util.Arrays;
import java.util.stream.Stream;

import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;

public class SysMLv2ToAASAllExecutionTest {
    @TestFactory
    Stream<DynamicTest> allInputs() throws Exception {
        File asm = BenchmarkExecutionSupport.compile("SysMLv2ToAAS_All");
        return Arrays.stream(BenchmarkExecutionSupport.inputs("sysml2aas/xmi"))
            .map(input -> DynamicTest.dynamicTest(input.getFileName().toString(), () ->
                BenchmarkExecutionSupport.execute(asm, "SysMLv2.ecore", "AAS.ecore", "sysml", "AAS", input, "sysml2aas")));
    }
}
