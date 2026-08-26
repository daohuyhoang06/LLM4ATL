package com.example.atlparser;

import org.eclipse.emf.ecore.EObject;
import org.eclipse.m2m.atl.engine.parser.AtlParser;
import org.junit.jupiter.api.Test;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class AtlParserTest {

    private static final Path TEST_RESOURCES_DIR = Path.of("src", "test", "resources");

    private static List<String> getAtlFiles() throws Exception {
        try (var files = Files.list(TEST_RESOURCES_DIR)) {
            return files
                    .filter(Files::isRegularFile)
                    .map(path -> path.getFileName().toString())
                    .filter(fileName -> fileName.endsWith(".atl"))
                    .sorted()
                    .toList();
        }
    }

    @Test
    void testParseAllAtlFiles() throws Exception {
        AtlParser parser = AtlParser.getDefault();
        List<String> failures = new ArrayList<>();
        List<String> atlFiles = getAtlFiles();

        assertFalse(atlFiles.isEmpty(), "No ATL files found in " + TEST_RESOURCES_DIR);

        for (String fileName : atlFiles) {
            try (InputStream input = getClass().getClassLoader().getResourceAsStream(fileName)) {
                assertNotNull(input, "File not found: " + fileName);

                EObject[] result = parser.parseWithProblems(input);
                assertNotNull(result[0], "Failed to parse: " + fileName);

                int problemCount = result.length - 1;

                if (problemCount > 0) {
                    System.out.println("FAIL: " + fileName + " (" + problemCount + " errors)");
                    for (int i = 1; i < result.length; i++) {
                        System.out.println("  - " + result[i]);
                    }
                    failures.add(fileName + " (" + problemCount + " errors)");
                } else {
                    System.out.println("OK: " + fileName);
                }
            }
        }

        if (!failures.isEmpty()) {
            fail("Files with syntax errors:\n  " + String.join("\n  ", failures));
        }
    }
}
