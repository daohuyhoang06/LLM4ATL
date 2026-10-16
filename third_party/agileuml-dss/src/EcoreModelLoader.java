/*
 * Copyright (c) 2026.
 * SPDX-License-Identifier: EPL-2.0
 */

import java.io.File;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.Vector;
import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

/** Loads two Ecore metamodels directly into AgileUML's in-memory model. */
public final class EcoreModelLoader
{
  public static final String SOURCE = "source";
  public static final String TARGET = "target";

  public static final class Model
  {
    public final Vector entities = new Vector();
    public final Vector associations = new Vector();
    public final Vector types = new Vector();
    public final Set metamodelNames = new LinkedHashSet();
    private final LinkedHashMap classes = new LinkedHashMap();
    private final LinkedHashMap classOrigins = new LinkedHashMap();
    private final LinkedHashMap namedTypes = new LinkedHashMap();
    private final List pendingClasses = new ArrayList();
    private final List pendingReferences = new ArrayList();
    public EcoreNameAdapter nameAdapter;
  }

  public Model load(File source, File target) throws Exception
  { return load(source, target, new EcoreNameAdapter(
      java.util.Collections.EMPTY_SET, java.util.Collections.EMPTY_SET)); }

  public Model load(File source, File target, EcoreNameAdapter nameAdapter)
    throws Exception
  {
    Model result = new Model();
    result.nameAdapter = nameAdapter;
    loadOne(source, SOURCE, result);
    loadOne(target, TARGET, result);
    resolveInheritance(result);
    resolveReferences(result);
    return result;
  }

  private void loadOne(File file, String side, Model model) throws Exception
  {
    Document document = parse(file);
    Element root = document.getDocumentElement();
    collectPackageNames(root, model.metamodelNames);
    List classifiers = new ArrayList();
    collectClassifiers(root, classifiers);

    for (int i = 0; i < classifiers.size(); i++)
    {
      Element classifier = (Element) classifiers.get(i);
      String kind = xsiType(classifier);
      String name = classifier.getAttribute("name");
      if (name.length() == 0)
      { continue; }
      if (kind.endsWith("EEnum"))
      {
        Vector literals = new Vector();
        List children = childElements(classifier);
        for (int j = 0; j < children.size(); j++)
        {
          Element child = (Element) children.get(j);
          if ("eLiterals".equals(localName(child)))
          {
            String literal = child.getAttribute("name");
            if (literal.length() > 0)
            { literals.add(literal); }
          }
        }
        registerType(name, new Type(name, literals), model);
      }
      else if (kind.endsWith("EDataType"))
      { registerType(name, new Type(name, null), model); }
    }

    for (int i = 0; i < classifiers.size(); i++)
    {
      Element classifier = (Element) classifiers.get(i);
      String kind = xsiType(classifier);
      if (!kind.endsWith("EClass"))
      { continue; }
      String externalName = classifier.getAttribute("name");
      if (externalName.length() == 0)
      { continue; }
      String name = model.nameAdapter.internalName(side, externalName);
      String key = classKey(side, externalName);
      if (model.classes.containsKey(key))
      { throw new IllegalArgumentException(
          "Duplicate EClass '" + externalName + "' in " + file +
          "; already defined by " + model.classOrigins.get(key)); }

      Entity entity = new Entity(name);
      entity.addStereotype(side);
      entity.setAbstract("true".equals(classifier.getAttribute("abstract")));
      model.entities.add(entity);
      model.classes.put(key, entity);
      model.classOrigins.put(key, side + " metamodel " + file);
      model.nameAdapter.register(side, externalName, entity);
      model.pendingClasses.add(new PendingClass(entity, classifier, side));
    }

    for (int i = 0; i < model.pendingClasses.size(); i++)
    {
      PendingClass pending = (PendingClass) model.pendingClasses.get(i);
      if (!side.equals(pending.side))
      { continue; }
      addStructuralFeatures(pending.entity, pending.element, model);
    }
    System.out.println(">>> Loaded " + side + " Ecore " + file);
  }

  private void addStructuralFeatures(Entity owner, Element eclass, Model model)
  {
    List children = childElements(eclass);
    for (int i = 0; i < children.size(); i++)
    {
      Element feature = (Element) children.get(i);
      if (!"eStructuralFeatures".equals(localName(feature)))
      { continue; }
      String role = feature.getAttribute("name");
      String kind = xsiType(feature);
      if (role.length() == 0)
      { continue; }

      if (kind.endsWith("EAttribute"))
      {
        Type type = resolveDataType(featureTypeReference(feature), model);
        Attribute attribute = new Attribute(role, type, ModelElement.INTERNAL);
        attribute.setEntity(owner);
        attribute.setElementType(type);
        attribute.setUnique(!"false".equals(feature.getAttribute("unique")));
        attribute.setSorted("true".equals(feature.getAttribute("ordered")));
        owner.addAttribute(attribute);
      }
      else if (kind.endsWith("EReference"))
      {
        String lower = defaultValue(feature.getAttribute("lowerBound"), "0");
        String upper = defaultValue(feature.getAttribute("upperBound"), "1");
        model.pendingReferences.add(new PendingReference(
          owner, featureTypeReference(feature), role, lower, upper, pendingSide(owner, model),
          "true".equals(feature.getAttribute("containment")),
          "true".equals(feature.getAttribute("ordered"))));
      }
    }
  }

  private void resolveInheritance(Model model)
  {
    for (int i = 0; i < model.pendingClasses.size(); i++)
    {
      PendingClass pending = (PendingClass) model.pendingClasses.get(i);
      String value = pending.element.getAttribute("eSuperTypes").trim();
      if (value.length() == 0)
      { continue; }
      String[] references = value.split("\\s+");
      for (int j = 0; j < references.length; j++)
      {
        Entity parent = resolveClass(references[j], pending.side, model);
        if (parent == null)
        { throw new IllegalArgumentException(
            "Cannot resolve ESuperType '" + references[j] + "' of " +
            pending.entity.getName()); }
        pending.entity.addSuperclass(parent);
        parent.addSubclass(pending.entity);
      }
    }
  }

  private void resolveReferences(Model model)
  {
    for (int i = 0; i < model.pendingReferences.size(); i++)
    {
      PendingReference pending =
        (PendingReference) model.pendingReferences.get(i);
      Entity target = resolveClass(pending.targetReference, pending.side, model);
      if (target == null)
      { throw new IllegalArgumentException(
          "Cannot resolve EReference type '" + pending.targetReference +
          "' for " + pending.owner.getName() + "." + pending.role); }
      String matchingLower = "1".equals(pending.upper)
        ? "1" : pending.lower;
      Association association = new Association(
        pending.owner, target, matchingLower, pending.upper, null, pending.role);
      association.setName("ecoreReference" + i);
      association.setAggregation(pending.containment);
      association.setOrdered(pending.ordered);
      pending.owner.addAssociation(association);
      model.associations.add(association);
    }
  }

  private Entity resolveClass(String reference, String side, Model model)
  { return (Entity) model.classes.get(classKey(side, referencedName(reference))); }

  private String classKey(String side, String externalName)
  { return side + "::" + externalName; }

  private String pendingSide(Entity owner, Model model)
  {
    for (int i = 0; i < model.pendingClasses.size(); i++)
    {
      PendingClass pending = (PendingClass) model.pendingClasses.get(i);
      if (pending.entity == owner)
      { return pending.side; }
    }
    throw new IllegalArgumentException("No Ecore side registered for " + owner);
  }

  private Type resolveDataType(String reference, Model model)
  {
    String name = mapEcorePrimitive(referencedName(reference));
    Type result = (Type) model.namedTypes.get(name);
    if (result != null)
    { return result; }
    result = new Type(name, null);
    model.namedTypes.put(name, result);
    if (!isBuiltInType(name))
    { model.types.add(result); }
    return result;
  }

  private void registerType(String name, Type type, Model model)
  {
    if (model.namedTypes.containsKey(name))
    { return; }
    model.namedTypes.put(name, type);
    model.types.add(type);
  }

  private Document parse(File file) throws Exception
  {
    DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
    factory.setNamespaceAware(true);
    try { factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true); }
    catch (Exception ignored) { }
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

  private void collectPackageNames(Element element, Set result)
  {
    String tag = localName(element);
    if ("EPackage".equals(tag) || "eSubpackages".equals(tag))
    {
      String name = element.getAttribute("name");
      if (name.length() > 0)
      { result.add(name); }
    }
    List children = childElements(element);
    for (int i = 0; i < children.size(); i++)
    { collectPackageNames((Element) children.get(i), result); }
  }

  private void collectClassifiers(Element element, List result)
  {
    if ("eClassifiers".equals(localName(element)))
    { result.add(element); }
    List children = childElements(element);
    for (int i = 0; i < children.size(); i++)
    { collectClassifiers((Element) children.get(i), result); }
  }

  private List childElements(Element parent)
  {
    List result = new ArrayList();
    NodeList children = parent.getChildNodes();
    for (int i = 0; i < children.getLength(); i++)
    {
      Node child = children.item(i);
      if (child instanceof Element)
      { result.add(child); }
    }
    return result;
  }

  private String localName(Element element)
  {
    String result = element.getLocalName();
    if (result != null)
    { return result; }
    String tag = element.getTagName();
    int colon = tag.indexOf(':');
    return colon >= 0 ? tag.substring(colon + 1) : tag;
  }

  private String xsiType(Element element)
  {
    String result = element.getAttributeNS(
      "http://www.w3.org/2001/XMLSchema-instance", "type");
    if (result == null || result.length() == 0)
    { result = element.getAttribute("xsi:type"); }
    return result == null ? "" : result;
  }

  private String featureTypeReference(Element feature)
  {
    String direct = feature.getAttribute("eType");
    if (direct.length() > 0)
    { return direct; }
    List children = childElements(feature);
    for (int i = 0; i < children.size(); i++)
    {
      Element child = (Element) children.get(i);
      if ("eType".equals(localName(child)))
      {
        String href = child.getAttribute("href");
        if (href.length() > 0)
        { return href; }
      }
    }
    return "";
  }

  private String referencedName(String reference)
  {
    if (reference == null)
    { return ""; }
    String value = reference.trim();
    int space = value.lastIndexOf(' ');
    if (space >= 0)
    { value = value.substring(space + 1); }
    int marker = value.lastIndexOf("#//");
    if (marker >= 0)
    { value = value.substring(marker + 3); }
    int slash = value.lastIndexOf('/');
    if (slash >= 0)
    { value = value.substring(slash + 1); }
    int colon = value.lastIndexOf(':');
    if (colon >= 0)
    { value = value.substring(colon + 1); }
    return value;
  }

  private String mapEcorePrimitive(String name)
  {
    if ("EString".equals(name) || "EChar".equals(name) ||
        "ECharacterObject".equals(name) || "EDate".equals(name))
    { return "String"; }
    if ("EInt".equals(name) || "EIntegerObject".equals(name) ||
        "EShort".equals(name) || "EShortObject".equals(name) ||
        "EByte".equals(name) || "EByteObject".equals(name))
    { return "int"; }
    if ("ELong".equals(name) || "ELongObject".equals(name) ||
        "EBigInteger".equals(name))
    { return "long"; }
    if ("EFloat".equals(name) || "EFloatObject".equals(name) ||
        "EDouble".equals(name) || "EDoubleObject".equals(name) ||
        "EBigDecimal".equals(name))
    { return "double"; }
    if ("EBoolean".equals(name) || "EBooleanObject".equals(name))
    { return "boolean"; }
    return name.length() == 0 ? "String" : name;
  }

  private boolean isBuiltInType(String name)
  { return "String".equals(name) || "int".equals(name) ||
           "long".equals(name) || "double".equals(name) ||
           "boolean".equals(name); }

  private String defaultValue(String value, String fallback)
  { return value == null || value.length() == 0 ? fallback : value; }

  private static final class PendingClass
  {
    final Entity entity;
    final Element element;
    final String side;
    PendingClass(Entity entity, Element element, String side)
    { this.entity = entity; this.element = element; this.side = side; }
  }

  private static final class PendingReference
  {
    final Entity owner;
    final String targetReference;
    final String role;
    final String lower;
    final String upper;
    final String side;
    final boolean containment;
    final boolean ordered;
    PendingReference(Entity owner, String targetReference, String role,
                     String lower, String upper, String side, boolean containment,
                     boolean ordered)
    {
      this.owner = owner;
      this.targetReference = targetReference;
      this.role = role;
      this.lower = lower;
      this.upper = upper;
      this.side = side;
      this.containment = containment;
      this.ordered = ordered;
    }
  }
}
