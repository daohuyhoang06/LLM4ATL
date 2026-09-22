package com.example.atlparser;

import org.eclipse.emf.ecore.EObject;
import org.eclipse.m2m.atl.engine.parser.AtlParser;
import org.junit.jupiter.api.Test;

import java.io.InputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class AtlParserTest {

    private static final Path TEST_RESOURCES_DIR = Path.of(
            System.getProperty("atl.test.resources.dir", "src/test/resources/other_references")
    );

    private static List<Path> getAtlFiles() throws IOException {
        try (var files = Files.walk(TEST_RESOURCES_DIR)) {
            return files
                    .filter(Files::isRegularFile)
                    .filter(path -> path.getFileName().toString().endsWith(".atl"))
                    .map(TEST_RESOURCES_DIR::relativize)
                    .sorted()
                    .toList();
        }
    }

    @Test
    void testParseAllAtlFiles() throws Exception {
        AtlParser parser = AtlParser.getDefault();
        List<String> failures = new ArrayList<>();
        List<Path> atlFiles = getAtlFiles();

        assertFalse(atlFiles.isEmpty(), "No ATL files found in " + TEST_RESOURCES_DIR);

        for (Path relativePath : atlFiles) {
            String displayName = relativePath.toString();
            try (InputStream input = Files.newInputStream(TEST_RESOURCES_DIR.resolve(relativePath))) {

                EObject[] result = parser.parseWithProblems(input);
                assertNotNull(result[0], "Failed to parse: " + displayName);

                int problemCount = result.length - 1;

                if (problemCount > 0) {
                    System.out.println("FAIL: " + displayName + " (" + problemCount + " errors)");
                    for (int i = 1; i < result.length; i++) {
                        System.out.println("  - " + result[i]);
                    }
                    failures.add(displayName + " (" + problemCount + " errors)");
                } else {
                    System.out.println("OK: " + displayName);
                }
            }
        }

        if (!failures.isEmpty()) {
            fail("Files with syntax errors:\n  " + String.join("\n  ", failures));
        }
    }
}
