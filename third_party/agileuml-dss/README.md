# AgileUML DSS headless adapter

This directory exposes the requirements analysis and native `all maps` DSS
search from AgileUML as a deterministic command-line component. It produces
the following standalone artefacts:

- `req.tl`: mappings extracted from POS-tagged requirements;
- `forward.tl`: the requirements mappings completed by native DSS metamodel
  matching.

The adapter intentionally does not instantiate `UCDArea` or any Swing class.
The three DSS post-processing classes used by the workflow are included with
one mechanical change: calls to `JOptionPane.showInputDialog` are routed to a
deterministic review policy. The DSS candidate enumeration, similarity scoring,
requirements-derived assumed mappings, and optional review passes are retained.

This component is currently standalone. It is **not imported or invoked by the
LLM4ATL pipeline**; integration should happen only after its mappings have been
evaluated on the desired cases.

## Upstream

- Project: Eclipse AgileUML (`https://github.com/eclipse-agileuml/agileuml`)
- Source revision inspected: `3f08999975dccf40ab129e0a477b9c5ef2fff5fe`
- License: EPL-2.0 (see the copyright/SPDX headers in upstream source files)

The adapter is self-contained apart from requiring a JDK on `PATH`. Its runtime
dependencies are bundled under `lib/`:

- `lib/agileuml-runtime.jar`: class-only AgileUML runtime, EPL-2.0;
- `lib/stanford-postagger/stanford-postagger.jar`: Stanford POS Tagger 4.2.0;
- `lib/stanford-postagger/stanford-postagger-4.2.0-sources.jar`: corresponding
  Stanford source archive;
- `lib/stanford-postagger/models/english-left3words-distsim.tagger`: English
  tagging model.

Stanford POS Tagger is distributed under GPL v2. Its original `LICENSE.txt`
and `README.txt` are included beside the JAR. Review GPL v2 compatibility with
the intended distribution model before publishing or redistributing the whole
repository.

`AGILEUML_RUNTIME_DIR`, `DSS_STANFORD_TAGGER_DIR`, and `DSS_STANFORD_MODEL`
remain optional overrides for development; normal use does not require them.

Controlled natural-language requirements used for manual evaluation are kept
under `requirements/`. These files paraphrase the original ATL-oriented user
prompts into short class- and feature-mapping sentences that AgileUML's
requirements analyser can recognise.

## Build and direct use

```powershell
.\build.ps1

.\run.ps1 `
  -Source D:\models\source.ecore `
  -Target D:\models\target.ecore `
  -TaggedRequirements D:\work\tagged.txt `
  -ReqOutput D:\work\req.tl `
  -ForwardOutput D:\work\forward.tl
```

`run.ps1` expects already POS-tagged requirements. For a raw
controlled-language requirements file, use the standalone wrapper:

```powershell
.\run_raw.ps1 `
  -Source D:\models\source.ecore `
  -Target D:\models\target.ecore `
  -Requirements D:\work\requirements.txt `
  -OutputDir D:\work\dss-result
```

`run_raw.ps1` writes `requirements.tagged.txt`, `req.tl`, and `forward.tl`
into `OutputDir`. The Ecore models are loaded directly into AgileUML's
in-memory `Entity`, `Attribute`, `Association`, and `Type` objects; no
intermediate `mm.txt` participates in matching.

Stanford POS tagging does not translate domain synonyms into EClass names. For
example, `table` does not automatically become `Relation`. Requirements used as
DSS seeds should mention actual source and target EClass/EFeature names, as in
`Each Entity is transformed into a Relation.`

Source and target EClasses may have the same simple name. The adapter assigns
the target collision a unique internal name, adds the natural same-name class
mapping as a DSS seed, and restores the original EClass name in `req.tl` and
`forward.tl`. For example, `network::Link` and `graph::Link` are processed as
distinct internal classes but emitted as `Link |--> Link`.

Default DSS settings match the intended GUI run:

- source feature-chain length: `1` in `run_raw.ps1` (`2` in low-level `run.ps1`);
- target feature-chain length: `1` in `run_raw.ps1` (`2` in low-level `run.ps1`);
- type matching: `fuzzy`;
- candidate mapping limit: `1,000,000`.

Review settings are explicit:

- `-Review none`: return the scored DSS candidate without review passes;
- `-Review accept`: deterministically accept y/n suggestions (the test preset);
- `-Review reject`: deterministically reject y/n suggestions;
- `-CheckTargetFeatures $false`: corresponds to answering `n` to the GUI's
  “Check that all target features are used?” question.

## Repeatable test

```powershell
.\test.ps1
```

The test uses the bundled ER/REL Ecore and POS-tagged controlled requirements,
runs with `chain=1`, fuzzy matching, accepted review suggestions, and target
feature completeness disabled. It verifies both requirements-derived seeds and
DSS-synthesised collection mappings. Generated files are written under
`build/test-output/` and are not passed to an LLM.

To compare the adapter with the unmodified matching bytecode from a local
AgileUML checkout, run:

```powershell
.\test_original_compat.ps1 -OriginalAgileUmlDir D:\path\to\AgileUML\umlrsds
```

This runs FamiliesToPersons, Class2Interface, and Document2Report twice with
identical tagged requirements and `review=none`. The second run places the
original AgileUML directory first on the Java classpath, so its unmodified
`ModelMatching`, `EntityMatching`, and `AttributeMatching` classes are used.
Both `req.tl` and `forward.tl` must match after newline normalisation.

Additional synthetic edge cases can be run with:

```powershell
.\test_special_cases.ps1 -OriginalAgileUmlDir D:\path\to\AgileUML\umlrsds
```

These cover duplicate source/target EClass names, enums and recursive
references, abstract inheritance with exact type matching, source feature
chains of length 2, and DSS synthesis with an empty requirements seed. The
no-seed case is also repeated to check deterministic selection.

