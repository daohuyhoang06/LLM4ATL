/*
 * Copyright (c) 2026.
 * SPDX-License-Identifier: EPL-2.0
 */

import java.util.Vector;

/**
 * Headless extraction of UCDArea.flattenModel("all maps", ...).
 * It keeps requirement-derived class mappings fixed during the DSS search and
 * restores requirement-derived feature mappings before producing the result.
 */
public final class DssEngine
{
  public ModelMatching synthesise(Vector originalEntities,
                                  Vector types,
                                  ModelMatching initialMatching,
                                  Vector thesaurus,
                                  DssOptions options)
  {
    options.validate();
    if (initialMatching == null)
    { initialMatching = new ModelMatching(); }
    if (thesaurus == null)
    { thesaurus = new Vector(); }

    Vector flattened = new Vector();
    Map flattening = new Map();
    for (int i = 0; i < originalEntities.size(); i++)
    {
      Entity entity = (Entity) originalEntities.get(i);
      int depth = entity.isTarget()
        ? options.targetFeatureChainLength
        : options.sourceFeatureChainLength;
      Entity copy = entity.makeFlattenedCopy(true, depth, options.exactTypeMatch);
      flattened.add(copy);
      flattening.set(entity, copy);
    }
    for (int i = 0; i < originalEntities.size(); i++)
    {
      Entity entity = (Entity) originalEntities.get(i);
      Entity copy = (Entity) flattening.get(entity);
      copy.copyInheritances(entity, flattening);
    }

    Vector workingEntities = new Vector();
    workingEntities.addAll(originalEntities);
    workingEntities.addAll(flattened);

    Vector sourceEntities = new Vector();
    Vector concreteSources = new Vector();
    Vector targetEntities = new Vector();
    Vector sharedEntities = new Vector();
    sharedEntities.addAll(flattened);

    for (int i = 0; i < flattened.size(); i++)
    {
      Entity entity = (Entity) flattened.get(i);
      if (entity.isSource())
      {
        sourceEntities.add(entity);
        if (entity.isConcrete())
        { concreteSources.add(entity); }
      }
      else if (entity.isTarget())
      { targetEntities.add(entity); }
    }
    sharedEntities.removeAll(sourceEntities);
    sharedEntities.removeAll(targetEntities);

    if (sourceEntities.size() == 0)
    { throw new IllegalArgumentException("No source-stereotyped classes were loaded"); }
    if (targetEntities.size() == 0)
    { throw new IllegalArgumentException("No target-stereotyped classes were loaded"); }

    Vector assumedSources = new Vector();
    Vector assumedTargets = new Vector();
    for (int i = 0; i < initialMatching.entitymatches.size(); i++)
    {
      EntityMatching mapping =
        (EntityMatching) initialMatching.entitymatches.get(i);
      if (mapping.realsrc == null || mapping.realtrg == null)
      { continue; }
      Entity source = (Entity) ModelElement.lookupByName(
        mapping.realsrc.getName() + "$", workingEntities);
      Entity target = (Entity) ModelElement.lookupByName(
        mapping.realtrg.getName() + "$", workingEntities);
      if (source == null || target == null)
      { continue; }
      if (source.isConcrete() && target.isAbstract())
      {
        Vector subclasses = target.getAllConcreteSubclasses();
        if (subclasses.size() == 0)
        { continue; }
        target = (Entity) subclasses.get(0);
      }
      assumedSources.add(source);
      assumedTargets.add(target);
    }

    sourceEntities.removeAll(assumedSources);
    concreteSources.removeAll(assumedSources);
    System.out.println("**** Assumed matchings are: " + assumedSources +
                       " -> " + assumedTargets);

    ModelMatching selected = search(sourceEntities, targetEntities,
      sharedEntities, assumedSources, assumedTargets, workingEntities,
      thesaurus, options);

    // Preserve the paper's cm0 subset cm and fm0 subset fm requirement.
    selected.combineMatches(initialMatching.entitymatches);

    /* The desktop workflow reviews these suggestions through JOptionPane.
     * The headless copies of ModelMatching/EntityMatching/AttributeMatching
     * route the same questions to DssPromptPolicy instead. */
    if ("none".equals(options.reviewMode))
    { selected.addFlagVariables(new Vector()); }
    else
    {
      DssPromptPolicy.configure(options.reviewMode);
      selected.removeInvalidMatchings();
      selected.copySuperclassMatchings(thesaurus, originalEntities);
      selected.checkBidirectionalAssociationConsistency();
      selected.checkEntityMapCompleteness(originalEntities);
      Vector correlations = selected.analyseCorrelationPatterns(
        originalEntities, types);
      Vector sources = Entity.sourceEntities(originalEntities);
      Vector unusedTargets = selected.unusedTargetEntities(originalEntities);
      selected.checkValidity(unusedTargets, workingEntities, sources,
                             initialMatching.entitymatches, thesaurus);
      if (options.checkTargetFeatureCompleteness)
      { selected.checkTargetFeatureCompleteness(
          workingEntities, sources, thesaurus); }
      selected.removeSpuriousMatchings();

      // A review pass may replace a requirements-derived feature mapping.
      // Restore the requirements as the authoritative lower bound fm0.
      selected.combineMatches(initialMatching.entitymatches);
      selected.addFlagVariables(correlations);
    }
    return selected;
  }

  private ModelMatching search(Vector sources,
                               Vector targets,
                               Vector shared,
                               Vector assumedSources,
                               Vector assumedTargets,
                               Vector entities,
                               Vector thesaurus,
                               DssOptions options)
  {
    if (sources.size() == 0 || targets.size() <= 1)
    {
      Map base = new Map(sources, targets);
      Map withShared = Map.extendDomainRange(base, shared);
      Map candidate = Map.extendDomainRange(
        withShared, assumedSources, assumedTargets);
      ModelMatching only = new ModelMatching(candidate, entities);
      score(candidate, only, entities, thesaurus, options.exactTypeMatch);
      return only;
    }

    LexicographicOrdering ordering = new LexicographicOrdering();
    ordering.setalphabet(targets);
    ordering.init();
    int maximumSize = sources.size();
    int minimumSize = maximumSize / 2;
    Vector word = new Vector();
    word = (Vector) ordering.increment(word);
    while (word.size() < minimumSize)
    { word = (Vector) ordering.increment(word); }

    Vector best = new Vector();
    double bestScore = 0;
    long evaluated = 0;
    while (word.size() <= maximumSize)
    {
      if (++evaluated > options.maxCandidateMappings)
      { throw new IllegalStateException(
          "DSS candidate limit exceeded: " + options.maxCandidateMappings); }
      Map partial = ordering.getMap(word, sources);
      Map withShared = Map.extendDomainRange(partial, shared);
      Map candidate = Map.extendDomainRange(
        withShared, assumedSources, assumedTargets);
      ModelMatching matching = new ModelMatching(candidate, entities);
      double candidateScore = score(candidate, matching, entities,
        thesaurus, options.exactTypeMatch);
      if (candidateScore > bestScore)
      {
        bestScore = candidateScore;
        best.clear();
        best.add(matching);
      }
      else if (candidateScore > 0 && candidateScore == bestScore)
      { best.add(matching); }
      word = (Vector) ordering.increment(word);
    }

    if (best.size() == 0)
    { throw new IllegalStateException("DSS found no valid metamodel mapping"); }

    ModelMatching selected = (ModelMatching) best.get(0);
    double selectedNameScore = selected.nameSimilarity();
    for (int i = 1; i < best.size(); i++)
    {
      ModelMatching alternative = (ModelMatching) best.get(i);
      double nameScore = alternative.nameSimilarity();
      // Keep the same tie-break order as UCDArea.flattenModel("all maps").
      if (alternative.size() < selected.size())
      { selected = alternative; }
      else if (nameScore > selectedNameScore)
      { selected = alternative; }
    }
    System.out.println(">>> DSS evaluated " + evaluated +
                       " candidates; best score = " + bestScore);
    return selected;
  }

  private double score(Map candidate,
                       ModelMatching matching,
                       Vector entities,
                       Vector thesaurus,
                       boolean exact)
  {
    double result = 0;
    double factor = 1;
    Vector domain = candidate.domain();
    for (int i = 0; i < domain.size(); i++)
    {
      Entity source = (Entity) domain.get(i);
      Entity target = (Entity) candidate.get(source);
      if (source.isConcrete() && target.isAbstract())
      { factor = 0; }
      else if (factor > 0)
      {
        double structural = source.similarity(
          target, matching, entities, exact, false, thesaurus);
        double name = ModelElement.similarity(
          source.getName().toLowerCase(), target.getName().toLowerCase());
        double semanticName = source.nms$Similarity(target, thesaurus);
        result += structural + name * ModelMatching.NAMEWEIGHT +
                  semanticName * ModelMatching.NMSWEIGHT;
      }
    }
    return result * factor;
  }
}
