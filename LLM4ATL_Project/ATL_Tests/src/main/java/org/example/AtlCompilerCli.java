package org.example;

import java.nio.file.Path;
import java.util.List;
import java.util.StringJoiner;

/**
 * Command-line adapter for {@link AtlCompiler}. It writes one JSON result to
 * stdout so the Python tract-validation layer can consume it directly.
 */
public final class AtlCompilerCli {

    private static final String INPUT_ENVIRONMENT_VARIABLE = "ATL_COMPILER_INPUT";
    private static final String OUTPUT_ENVIRONMENT_VARIABLE = "ATL_COMPILER_OUTPUT";

    private AtlCompilerCli() {
    }

    public static void main(String[] args) {
        String[] compilerArguments = compilerArguments(args);
        if (compilerArguments == null) {
            System.out.println(toJson(new AtlCompiler.CompileResult(
                AtlCompiler.Status.INPUT_ERROR,
                null,
                null,
                0,
                "Usage: AtlCompilerCli <input.atl> <output.asm>, or set "
                    + INPUT_ENVIRONMENT_VARIABLE + " and " + OUTPUT_ENVIRONMENT_VARIABLE + ".",
                null,
                List.of()
            )));
            System.exit(2);
        }

        AtlCompiler.CompileResult result = AtlCompiler.compile(
            Path.of(compilerArguments[0]),
            Path.of(compilerArguments[1])
        );
        System.out.println(toJson(result));
        System.exit(result.isSuccess() ? 0 : 1);
    }

    private static String[] compilerArguments(String[] args) {
        if (args.length == 2) {
            return args;
        }
        if (args.length != 0) {
            return null;
        }

        String inputPath = System.getenv(INPUT_ENVIRONMENT_VARIABLE);
        String outputPath = System.getenv(OUTPUT_ENVIRONMENT_VARIABLE);
        if (inputPath == null || inputPath.isBlank() || outputPath == null || outputPath.isBlank()) {
            return null;
        }
        return new String[] {inputPath, outputPath};
    }

    private static String toJson(AtlCompiler.CompileResult result) {
        return "{" +
            "\"status\":\"" + result.status().name() + "\"," +
            "\"atl_path\":" + jsonString(pathValue(result.atlPath())) + "," +
            "\"asm_path\":" + jsonString(pathValue(result.asmPath())) + "," +
            "\"asm_size_bytes\":" + result.asmSizeBytes() + "," +
            "\"message\":" + jsonString(result.message()) + "," +
            "\"exception_type\":" + jsonString(result.exceptionType()) +
            ",\"diagnostics\":" + diagnosticsJson(result.diagnostics()) +
            "}";
    }

    private static String diagnosticsJson(List<AtlCompiler.Diagnostic> diagnostics) {
        StringJoiner joiner = new StringJoiner(",", "[", "]");
        for (AtlCompiler.Diagnostic diagnostic : diagnostics) {
            joiner.add("{" +
                "\"severity\":" + jsonString(diagnostic.severity()) + "," +
                "\"location\":" + jsonString(diagnostic.location()) + "," +
                "\"description\":" + jsonString(diagnostic.description()) +
                "}");
        }
        return joiner.toString();
    }

    private static String pathValue(Path path) {
        return path == null ? null : path.toString();
    }

    private static String jsonString(String value) {
        if (value == null) {
            return "null";
        }

        StringBuilder escaped = new StringBuilder(value.length() + 8);
        escaped.append('"');
        for (int index = 0; index < value.length(); index++) {
            char character = value.charAt(index);
            switch (character) {
                case '"' -> escaped.append("\\\"");
                case '\\' -> escaped.append("\\\\");
                case '\b' -> escaped.append("\\b");
                case '\f' -> escaped.append("\\f");
                case '\n' -> escaped.append("\\n");
                case '\r' -> escaped.append("\\r");
                case '\t' -> escaped.append("\\t");
                default -> {
                    if (character < 0x20) {
                        escaped.append(String.format("\\u%04x", (int) character));
                    } else {
                        escaped.append(character);
                    }
                }
            }
        }
        escaped.append('"');
        return escaped.toString();
    }
}
