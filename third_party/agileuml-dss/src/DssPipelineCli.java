/*
 * Copyright (c) 2026.
 * SPDX-License-Identifier: EPL-2.0
 */

import java.io.File;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;
import java.util.Vector;
import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

/** Command-line requirements analysis plus native AgileUML DSS matching. */
public final class DssPipelineCli
{
  private DssPipelineCli() { }

  public static void main(String[] arguments)
  {
    try
    {
      System.setProperty("java.awt.headless", "true");
      HashMap options = parse(arguments);
      if (options.containsKey("help"))
      { usage(); return; }

      File source = requiredFile(options, "source");
      File target = requiredFile(options, "target");
      File tagged = requiredFile(options, "tagged-requirements");
      File reqOutput = requiredOutput(options, "req-output");
      File forwardOutput = requiredOutput(options, "forward-output");

      Set sourceNames = ecoreClassNames(source);
      Set targetNames = ecoreClassNames(target);
      EcoreNameAdapter nameAdapter = new EcoreNameAdapter(
        sourceNames, targetNames);
      if (nameAdapter.hasCollisions())
      { System.out.println(">>> Adapting colliding EClass names: " +
                           nameAdapter.collisionNames()); }

      String sourceName = value(options, "source-name", ecorePackageName(source));
      String targetName = value(options, "target-name", ecorePackageName(target));
      double threshold = doubleValue(options, "name-threshold", 0.5);

      DssOptions dssOptions = new DssOptions();
      dssOptions.sourceFeatureChainLength = intValue(
        options, "source-chain", 2);
      dssOptions.targetFeatureChainLength = intValue(
        options, "target-chain", 2);
      dssOptions.exactTypeMatch =
        "exact".equalsIgnoreCase(value(options, "type-match", "fuzzy"));
      dssOptions.maxCandidateMappings = longValue(
        options, "max-candidates", 1000000L);
      dssOptions.reviewMode = value(options, "review", "none").toLowerCase();
      dssOptions.checkTargetFeatureCompleteness = booleanValue(
        options, "check-target-features", false);
      dssOptions.validate();

      EcoreModelLoader.Model model =
        new EcoreModelLoader().load(source, target, nameAdapter);

      String[] metamodelNames = new String[] { sourceName, targetName };
      ModelMatching initial = RequirementsEngine.analyse(
        tagged, model.entities, model.types, metamodelNames,
        threshold, reqOutput, nameAdapter);

      DssEngine engine = new DssEngine();
      ModelMatching result = engine.synthesise(
        model.entities, model.types, initial, new Vector(), dssOptions);
      ForwardTlWriter.write(result, forwardOutput, nameAdapter);

      System.out.println(">>> Requirements TL: " + reqOutput.getAbsolutePath());
      System.out.println(">>> Forward DSS TL: " + forwardOutput.getAbsolutePath());
    }
    catch (Throwable error)
    {
      System.err.println("DSS pipeline failed: " + error.getMessage());
      error.printStackTrace(System.err);
      System.exit(1);
    }
  }

  private static HashMap parse(String[] arguments)
  {
    HashMap result = new HashMap();
    for (int i = 0; i < arguments.length; i++)
    {
      String argument = arguments[i];
      if ("--help".equals(argument) || "-h".equals(argument))
      { result.put("help", "true"); continue; }
      if (!argument.startsWith("--") || i + 1 >= arguments.length)
      { throw new IllegalArgumentException(
          "Expected --option value, got: " + argument); }
      result.put(argument.substring(2), arguments[++i]);
    }
    return result;
  }

  private static File requiredFile(HashMap options, String name)
  {
    String text = (String) options.get(name);
    if (text == null || text.length() == 0)
    { throw new IllegalArgumentException("Missing --" + name); }
    File result = new File(text).getAbsoluteFile();
    if (!result.isFile())
    { throw new IllegalArgumentException("File not found for --" + name +
                                         ": " + result); }
    return result;
  }

  private static File requiredOutput(HashMap options, String name)
  {
    String text = (String) options.get(name);
    if (text == null || text.length() == 0)
    { throw new IllegalArgumentException("Missing --" + name); }
    return new File(text).getAbsoluteFile();
  }

  private static String value(HashMap options, String name, String fallback)
  {
    String result = (String) options.get(name);
    return result == null || result.length() == 0 ? fallback : result;
  }

  private static int intValue(HashMap options, String name, int fallback)
  { return Integer.parseInt(value(options, name, String.valueOf(fallback))); }

  private static long longValue(HashMap options, String name, long fallback)
  { return Long.parseLong(value(options, name, String.valueOf(fallback))); }

  private static double doubleValue(HashMap options, String name, double fallback)
  { return Double.parseDouble(value(options, name, String.valueOf(fallback))); }

  private static boolean booleanValue(HashMap options, String name,
                                      boolean fallback)
  {
    String text = value(options, name, String.valueOf(fallback));
    if ("true".equalsIgnoreCase(text) || "y".equalsIgnoreCase(text))
    { return true; }
    if ("false".equalsIgnoreCase(text) || "n".equalsIgnoreCase(text))
    { return false; }
    throw new IllegalArgumentException(
      "--" + name + " must be true/false or y/n");
  }

  private static Document parseEcore(File file) throws Exception
  {
    DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
    factory.setNamespaceAware(true);
    try { factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true); }
    catch (Exception ignored) { }
    try { factory.setFeature("http://xml.org/sax/features/external-general-entities", false); }
    catch (Exception ignored) { }
    try { factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false); }
    catch (Exception ignored) { }
    factory.setXIncludeAware(false);
    factory.setExpandEntityReferences(false);
    try { factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, ""); }
    catch (Exception ignored) { }
    try { factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_SCHEMA, ""); }
    catch (Exception ignored) { }
    return factory.newDocumentBuilder().parse(file);
  }

  private static Set ecoreClassNames(File file) throws Exception
  {
    Set result = new HashSet();
    NodeList nodes = parseEcore(file).getElementsByTagNameNS("*", "eClassifiers");
    for (int i = 0; i < nodes.getLength(); i++)
    {
      Element element = (Element) nodes.item(i);
      String type = element.getAttributeNS(
        "http://www.w3.org/2001/XMLSchema-instance", "type");
      if (type.length() == 0)
      { type = element.getAttribute("xsi:type"); }
      if (type.endsWith("EClass"))
      { result.add(element.getAttribute("name")); }
    }
    return result;
  }

  private static String ecorePackageName(File file) throws Exception
  {
    Element root = parseEcore(file).getDocumentElement();
    String name = root.getAttribute("name");
    if (name != null && name.length() > 0)
    { return name; }
    return file.getName().replaceFirst("\\.[^.]+$", "");
  }

  private static void usage()
  {
    System.out.println(
      "Usage: java DssPipelineCli --source source.ecore --target target.ecore " +
      "--tagged-requirements tagged.txt --req-output req.tl " +
      "--forward-output forward.tl " +
      "[--source-name IN] [--target-name OUT] " +
      "[--name-threshold 0.5] [--source-chain 2] [--target-chain 2] " +
      "[--type-match fuzzy|exact] [--max-candidates 1000000] " +
      "[--review none|accept|reject] [--check-target-features false]");
  }
}
