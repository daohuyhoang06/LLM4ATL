package com.example.atlverification;

import java.nio.file.Path;

public final class ATL2TMRunnerMain {

    private ATL2TMRunnerMain() {
    }

    public static void main(String[] args) {

        if (args.length != 6) {
            System.err.println(
                "Usage: ATL2TMRunnerMain "
                + "<input.atl> "
                + "<source.ecore> "
                + "<target.ecore> "
                + "<ATL2TM.atl> "
                + "<work-dir> "
                + "<output.ecore>"
            );
            System.exit(2);
        }

        try {
            ATL2TMRunner runner = new ATL2TMRunner();

            runner.run(
                Path.of(args[0]),
                Path.of(args[1]),
                Path.of(args[2]),
                Path.of(args[3]),
                Path.of(args[4]),
                Path.of(args[5])
            );

            System.out.println("RESULT:OK");

        } catch (ATL2TMRunner.UnsupportedAtlConstructException e) {
            System.out.println("RESULT:UNSUPPORTED");
            System.err.println(e.getMessage());
            System.exit(3);
        } catch (Exception e) {
            System.out.println("RESULT:FAIL");
            e.printStackTrace();
            System.exit(1);
        }
    }
}
