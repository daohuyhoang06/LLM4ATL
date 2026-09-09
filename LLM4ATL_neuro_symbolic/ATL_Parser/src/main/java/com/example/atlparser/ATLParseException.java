package com.example.atlparser;

public class ATLParseException extends Exception {

    private final int problemCount;

    public ATLParseException(String message) {
        super(message);
        this.problemCount = -1;
    }

    public ATLParseException(
            String message,
            int problemCount
    ) {
        super(message);
        this.problemCount = problemCount;
    }

    public ATLParseException(
            String message,
            Throwable cause
    ) {
        super(message, cause);
        this.problemCount = -1;
    }

    public int getProblemCount() {
        return problemCount;
    }
}