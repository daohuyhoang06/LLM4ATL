/*
 * Copyright (c) 2026.
 * SPDX-License-Identifier: EPL-2.0
 */

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.Vector;

/** Headless form of UCDArea.requirements2TL0(). */
public final class RequirementsEngine
{
  private RequirementsEngine() { }

  public static ModelMatching analyse(File taggedRequirements,
                                      Vector entities,
                                      Vector types,
                                      String[] metamodelNames,
                                      double nameThreshold,
                                      File reqOutput)
    throws IOException
  {
    return analyse(taggedRequirements, entities, types, metamodelNames,
      nameThreshold, reqOutput, new EcoreNameAdapter(
        java.util.Collections.EMPTY_SET, java.util.Collections.EMPTY_SET));
  }

  public static ModelMatching analyse(File taggedRequirements,
                                      Vector entities,
                                      Vector types,
                                      String[] metamodelNames,
                                      double nameThreshold,
                                      File reqOutput,
                                      EcoreNameAdapter nameAdapter)
    throws IOException
  {
    if (taggedRequirements == null || !taggedRequirements.isFile())
    { throw new IOException("Tagged requirements not found: " + taggedRequirements); }

    RequirementsPhrase.threshold = nameThreshold;
    Vector requirementBlocks = readRequirementBlocks(taggedRequirements);
    Vector entityMappings = new Vector();

    for (int i = 0; i < requirementBlocks.size(); i++)
    {
      String text = (String) requirementBlocks.get(i);
      Compiler2 compiler = new Compiler2();
      compiler.nospacelexicalanalysis(text);
      Vector phrases = compiler.parseRequirementsText();
      RequirementsSentence sentence = new RequirementsSentence("", phrases);
      String classification = RequirementsPhrase.classify(
        phrases, entities, types, metamodelNames, sentence);
      sentence.sentencekind = classification;
      Vector mappings = sentence.toEntityMappings(entityMappings);
      entityMappings.addAll(mappings);
      System.out.println(">>> Requirement " + (i + 1) + ": " + classification);
    }

    ModelMatching result = new ModelMatching();
    result.entitymatches = entityMappings;
    nameAdapter.addCollisionMappings(result);
    if (reqOutput != null)
    { write(result, reqOutput, nameAdapter); }
    return result;
  }

  private static Vector readRequirementBlocks(File input) throws IOException
  {
    Vector result = new Vector();
    BufferedReader reader = new BufferedReader(new InputStreamReader(
      new FileInputStream(input), StandardCharsets.UTF_8));
    try
    {
      StringBuilder current = new StringBuilder();
      String line;
      while ((line = reader.readLine()) != null)
      {
        if (line.startsWith("--"))
        { continue; }
        if (line.trim().length() == 0)
        {
          addBlock(result, current);
        }
        else
        {
          if (current.length() > 0)
          { current.append(' '); }
          current.append(line);
        }
      }
      addBlock(result, current);
    }
    finally
    { reader.close(); }
    return result;
  }

  private static void addBlock(Vector result, StringBuilder current)
  {
    if (current.length() == 0)
    { return; }
    result.add(current.toString());
    current.setLength(0);
  }

  private static void write(ModelMatching matching, File output,
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
