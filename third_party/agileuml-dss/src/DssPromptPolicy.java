/*
 * Copyright (c) 2026.
 * SPDX-License-Identifier: EPL-2.0
 */

/** Deterministic replacement for the DSS review dialogs used by the GUI. */
public final class DssPromptPolicy
{
  private static String mode = "reject";

  private DssPromptPolicy() { }

  public static void configure(String value)
  { mode = value == null ? "reject" : value; }

  public static String ask(Object message)
  {
    String prompt = String.valueOf(message);
    String answer;
    if (prompt.indexOf("name/null") >= 0 ||
        prompt.indexOf("expression/null") >= 0)
    { answer = "null"; }
    else if ("accept".equals(mode))
    { answer = "y"; }
    else
    { answer = "n"; }
    System.out.println(">>> DSS review [" + answer + "]: " + prompt);
    return answer;
  }
}

