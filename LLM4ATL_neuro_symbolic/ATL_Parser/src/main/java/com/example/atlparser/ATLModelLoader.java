package com.example.atlparser;

import org.eclipse.emf.ecore.EObject;
import org.eclipse.m2m.atl.core.IModel;
import org.eclipse.m2m.atl.engine.parser.AtlParser;

import java.io.FileInputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;

public class ATLModelLoader {

    public EObject load(Path atlPath) throws ATLParseException {
        if (atlPath == null) {
            throw new ATLParseException("ATL path must not be null");
        }

        if (!Files.exists(atlPath)) {
            throw new ATLParseException(
                    "ATL file not found: " + atlPath
            );
        }

        if (!Files.isRegularFile(atlPath)) {
            throw new ATLParseException(
                    "ATL path is not a file: " + atlPath
            );
        }

        try {
            AtlParser parser = AtlParser.getDefault();

            try (InputStream input =
                         new FileInputStream(atlPath.toFile())) {

                EObject[] result =
                        parser.parseWithProblems(input);

                if (result == null ||
                    result.length == 0 ||
                    result[0] == null) {

                    throw new ATLParseException(
                            "ATL parser did not produce a model"
                    );
                }

                int problemCount = result.length - 1;

                if (problemCount > 0) {
                    StringBuilder message =
                            new StringBuilder();

                    message.append(
                            "ATL parsing failed with "
                    );
                    message.append(problemCount);
                    message.append(" problem(s)");

                    for (int i = 1; i < result.length; i++) {
                        message.append("\n  - ");
                        message.append(result[i]);
                    }

                    throw new ATLParseException(
                            message.toString(),
                            problemCount
                    );
                }

                return result[0];
            }

        } catch (ATLParseException e) {
            throw e;
        } catch (Exception e) {
            throw new ATLParseException(
                    "Failed to parse ATL file: "
                            + atlPath
                            + ": "
                            + e.getMessage(),
                    e
            );
        }
    }

    public IModel loadAsModel(Path atlPath) throws ATLParseException {
        Path normalizedPath =
                atlPath.toAbsolutePath().normalize();

        if (!Files.isRegularFile(normalizedPath)) {
            throw new ATLParseException(
                    "ATL file not found: " + normalizedPath
            );
        }

        try (InputStream input =
                    Files.newInputStream(normalizedPath)) {

            return AtlParser
                    .getDefault()
                    .parseToModel(input);

        } catch (Exception e) {
            throw new ATLParseException(
                    "Failed to load ATL model: "
                            + normalizedPath,
                    e
            );
        }
    }
}