/*
 * Copyright (c) 2026.
 * SPDX-License-Identifier: EPL-2.0
 */

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;

/** Writes only the forward TL artifact required by LLM4ATL. */
public final class ForwardTlWriter
{
  private ForwardTlWriter() { }

  public static void write(ModelMatching matching, File output)
    throws IOException
  {
    write(matching, output, new EcoreNameAdapter(
      java.util.Collections.EMPTY_SET, java.util.Collections.EMPTY_SET));
  }

  public static void write(ModelMatching matching, File output,
                           EcoreNameAdapter nameAdapter)
    throws IOException
  {
    File parent = output.getAbsoluteFile().getParentFile();
    if (parent != null && !parent.isDirectory() && !parent.mkdirs())
    { throw new IOException("Cannot create output directory: " + parent); }
    PrintWriter writer = new PrintWriter(new BufferedWriter(
      new OutputStreamWriter(new FileOutputStream(output), StandardCharsets.UTF_8)));
    try
    { writer.println(nameAdapter.restore(String.valueOf(matching))); }
    finally
    { writer.close(); }
  }
}
