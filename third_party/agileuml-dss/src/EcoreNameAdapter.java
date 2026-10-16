/*
 * Copyright (c) 2026.
 * SPDX-License-Identifier: EPL-2.0
 */

import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;
import java.util.Vector;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Gives colliding source/target EClasses unique internal names.
 *
 * AgileUML stores EClasses in a single simple-name namespace. Ecore, however,
 * permits source and target packages to contain classes with the same name.
 * The adapter renames only the target-side collision while DSS is running,
 * seeds the natural same-name correspondence, and restores the original name
 * in emitted TL files.
 */
public final class EcoreNameAdapter
{
  private final LinkedHashMap targetAliases = new LinkedHashMap();
  private final LinkedHashMap externalNames = new LinkedHashMap();
  private final LinkedHashMap sourceEntities = new LinkedHashMap();
  private final LinkedHashMap targetEntities = new LinkedHashMap();

  public EcoreNameAdapter(Set sourceNames, Set targetNames)
  {
    Set occupied = new HashSet();
    occupied.addAll(sourceNames);
    occupied.addAll(targetNames);

    LinkedHashSet duplicates = new LinkedHashSet();
    duplicates.addAll(sourceNames);
    duplicates.retainAll(targetNames);
    java.util.Iterator iterator = duplicates.iterator();
    while (iterator.hasNext())
    {
      String original = String.valueOf(iterator.next());
      String base = original + "__DssTarget";
      String alias = base;
      int suffix = 2;
      while (occupied.contains(alias))
      { alias = base + suffix++; }
      occupied.add(alias);
      targetAliases.put(original, alias);
      externalNames.put(alias, original);
    }
  }

  public boolean hasCollisions()
  { return !targetAliases.isEmpty(); }

  public Set collisionNames()
  { return new LinkedHashSet(targetAliases.keySet()); }

  public String internalName(String side, String externalName)
  {
    if (EcoreModelLoader.TARGET.equals(side))
    {
      String alias = (String) targetAliases.get(externalName);
      if (alias != null)
      { return alias; }
    }
    return externalName;
  }

  public void register(String side, String externalName, Entity entity)
  {
    if (!targetAliases.containsKey(externalName))
    { return; }
    if (EcoreModelLoader.SOURCE.equals(side))
    { sourceEntities.put(externalName, entity); }
    else if (EcoreModelLoader.TARGET.equals(side))
    { targetEntities.put(externalName, entity); }
  }

  /** Add a deterministic identity seed for each colliding simple name. */
  public void addCollisionMappings(ModelMatching matching)
  {
    if (matching == null)
    { return; }
    if (matching.entitymatches == null)
    { matching.entitymatches = new Vector(); }

    java.util.Iterator iterator = targetAliases.keySet().iterator();
    while (iterator.hasNext())
    {
      String name = String.valueOf(iterator.next());
      Entity source = (Entity) sourceEntities.get(name);
      Entity target = (Entity) targetEntities.get(name);
      if (source == null || target == null || contains(mappingVector(matching), source, target))
      { continue; }
      matching.entitymatches.add(new EntityMatching(source, target));
      System.out.println(">>> Added collision seed: " + name + " |--> " + name);
    }
  }

  private Vector mappingVector(ModelMatching matching)
  { return matching.entitymatches == null ? new Vector() : matching.entitymatches; }

  private boolean contains(Vector mappings, Entity source, Entity target)
  {
    for (int i = 0; i < mappings.size(); i++)
    {
      Object value = mappings.get(i);
      if (!(value instanceof EntityMatching))
      { continue; }
      EntityMatching mapping = (EntityMatching) value;
      if (mapping.realsrc == source && mapping.realtrg == target)
      { return true; }
    }
    return false;
  }

  /** Restore internal aliases in a rendered TL artifact. */
  public String restore(String text)
  {
    if (text == null || externalNames.isEmpty())
    { return text; }
    String result = text;
    java.util.Iterator iterator = externalNames.entrySet().iterator();
    while (iterator.hasNext())
    {
      Map.Entry entry = (Map.Entry) iterator.next();
      String internal = String.valueOf(entry.getKey());
      String external = String.valueOf(entry.getValue());
      Pattern token = Pattern.compile(
        "(?<![A-Za-z0-9_$])" + Pattern.quote(internal) +
        "(?![A-Za-z0-9_$])");
      result = token.matcher(result).replaceAll(Matcher.quoteReplacement(external));
    }
    return result;
  }

  public String toString()
  { return targetAliases.toString(); }
}
