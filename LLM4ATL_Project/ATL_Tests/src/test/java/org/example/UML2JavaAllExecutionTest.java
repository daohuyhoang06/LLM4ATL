package org.example;

import java.io.File;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.stream.Stream;

import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;

public class UML2JavaAllExecutionTest {
    @TestFactory
    Stream<DynamicTest> allInputs() throws Exception {
        File asm = BenchmarkExecutionSupport.compile("UML2Java_All");
        return Arrays.stream(BenchmarkExecutionSupport.inputs("uml2java"))
            .map(input -> DynamicTest.dynamicTest(input.getFileName().toString(), () ->
                BenchmarkExecutionSupport.execute(asm, "UML.ecore", "java.ecore", "UML", "Java", input, "uml2java")));
    }
}
