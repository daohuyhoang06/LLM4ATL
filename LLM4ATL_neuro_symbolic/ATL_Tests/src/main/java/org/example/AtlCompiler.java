package org.example;

import java.io.IOException;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;

import org.eclipse.m2m.atl.engine.compiler.CompileTimeError;
import org.eclipse.m2m.atl.engine.compiler.atl2006.Atl2006Compiler;

/**
 * Compiles an ATL module into an ASM artifact for the classic ATL EMFVM.
 */
public final class AtlCompiler {

    public enum Status {
        COMPILED,
        COMPILE_ERROR,
        INPUT_ERROR
    }

    public record Diagnostic(String severity, String location, String description) {
    }

    public record CompileResult(
        Status status,
        Path atlPath,
        Path asmPath,
        long asmSizeBytes,
        String message,
        String exceptionType,
        List<Diagnostic> diagnostics
    ) {
        public boolean isSuccess() {
            return status == Status.COMPILED;
        }
    }

    private AtlCompiler() {
    }

    /**
     * Compiles {@code atlPath} into {@code asmPath}. A temporary artifact is
     * used so a failed compilation never leaves a stale ASM at the destination.
     */
    public static CompileResult compile(Path atlPath, Path asmPath) {
        Path normalizedAtlPath = atlPath.toAbsolutePath().normalize();
        Path normalizedAsmPath = asmPath.toAbsolutePath().normalize();

        if (!Files.isRegularFile(normalizedAtlPath)) {
            return failure(
                Status.INPUT_ERROR,
                normalizedAtlPath,
                normalizedAsmPath,
                "ATL file not found: " + normalizedAtlPath,
                null,
                List.of()
            );
        }

        Path temporaryAsm = null;
        try {
            Path outputDirectory = normalizedAsmPath.getParent();
            if (outputDirectory == null) {
                return failure(
                    Status.INPUT_ERROR,
                    normalizedAtlPath,
                    normalizedAsmPath,
                    "ASM output path must have a parent directory.",
                    null,
                    List.of()
                );
            }

            Files.createDirectories(outputDirectory);
            temporaryAsm = Files.createTempFile(outputDirectory, "atl-compile-", ".asm");

            try (Reader reader = Files.newBufferedReader(normalizedAtlPath, StandardCharsets.UTF_8)) {
                CompileTimeError[] compilerErrors = new Atl2006Compiler().compile(reader, temporaryAsm.toString());
                List<Diagnostic> diagnostics = diagnosticsFor(compilerErrors);
                if (!diagnostics.isEmpty()) {
                    return failure(
                        Status.COMPILE_ERROR,
                        normalizedAtlPath,
                        normalizedAsmPath,
                        compilationErrorMessage(diagnostics),
                        null,
                        diagnostics
                    );
                }
            }

            long asmSize = Files.size(temporaryAsm);
            if (asmSize == 0) {
                return failure(
                    Status.COMPILE_ERROR,
                    normalizedAtlPath,
                    normalizedAsmPath,
                    "ATL compiler did not produce an ASM file. Check ATL syntax and compiler diagnostics.",
                    null,
                    List.of()
                );
            }

            Files.move(
                temporaryAsm,
                normalizedAsmPath,
                StandardCopyOption.REPLACE_EXISTING,
                StandardCopyOption.ATOMIC_MOVE
            );
            temporaryAsm = null;

            return new CompileResult(
                Status.COMPILED,
                normalizedAtlPath,
                normalizedAsmPath,
                asmSize,
                "ATL module compiled successfully.",
                null,
                List.of()
            );
        } catch (Exception exception) {
            return failure(
                Status.COMPILE_ERROR,
                normalizedAtlPath,
                normalizedAsmPath,
                messageFor(exception),
                exception.getClass().getName(),
                List.of()
            );
        } finally {
            if (temporaryAsm != null) {
                try {
                    Files.deleteIfExists(temporaryAsm);
                } catch (IOException ignored) {
                    // A failed cleanup must not hide the compiler diagnostic.
                }
            }
        }
    }

    private static CompileResult failure(
        Status status,
        Path atlPath,
        Path asmPath,
        String message,
        String exceptionType,
        List<Diagnostic> diagnostics
    ) {
        return new CompileResult(status, atlPath, asmPath, 0, message, exceptionType, diagnostics);
    }

    private static List<Diagnostic> diagnosticsFor(CompileTimeError[] compilerErrors) {
        if (compilerErrors == null) {
            return List.of();
        }

        return Arrays.stream(compilerErrors)
            .filter(Objects::nonNull)
            .map(error -> new Diagnostic(error.getSeverity(), error.getLocation(), error.getDescription()))
            .toList();
    }

    private static String compilationErrorMessage(List<Diagnostic> diagnostics) {
        Diagnostic firstDiagnostic = diagnostics.get(0);
        return "ATL compiler reported " + diagnostics.size() + " error(s): " + firstDiagnostic.description();
    }

    private static String messageFor(Exception exception) {
        String message = exception.getMessage();
        return message == null || message.isBlank()
            ? exception.getClass().getSimpleName()
            : message;
    }
}
