# Reference-free UML→Java and SysMLv2→AAS benchmarks

Each task uses **one generated ATL module for all ten inputs**. This is a
generalization experiment, not the original per-input agent/repair protocol.
No reference ATL was copied or used; parser ChrF is unavailable for these two
cases. The data below came from `D:\KLTN\repository\uml2java-multi-servers-1-runtime-docker`.

| Case | Prompt key / ATL module | Inputs | Oracles |
| --- | --- | --- | --- |
| UML→Java | `UML2Java_All` | `src/main/resources/models/uml2java/*.xmi` | `src/main/resources/oracles/uml2java/*_cleanOracle.java` |
| SysMLv2→AAS | `SysMLv2ToAAS_All` | `src/main/resources/models/sysml2aas/xmi/*.xmi` | `src/main/resources/oracles/sysml2aas/*.aas` |

The original SysML text is kept in `models/sysml2aas/source/*.sysml`.
`python build_sysml_fixtures.py` regenerates the corresponding XMI. This
adapter preserves named packages, definitions, usages and lexical nesting,
plus some message/succession categories. It **does not** parse general SysML v2
or preserve imports, aliases, type references, redefinitions, connection ends,
and sequencing details. The SysML results therefore measure this subset only.
Each XMI was checked with EMF against the copied metamodel.

`metamodels/SysMLv2.ecore` is a copy of the source SysMLv2 XMI Ecore package,
with `types.ecore` primitives redirected to built-in Ecore types. The UML
metamodel copy similarly redirects external primitive/Ecore URIs and removes
the external `EModelElement` supertype from `Element`, which prevented dynamic
EMF loading in this project. The upstream repository files were not changed.

The Java target metamodel is `java.ecore` and has no Enum/EnumLiteral. As a
result, the score is **partial Structural F1**: UML→Java compares Java class
names and class/field/name/type tuples, excluding enum facts; SysMLv2→AAS
compares shell/submodel names and nested Entity/Property names and qualifier
types, excluding relationship details. Oracle Java files are parsed as text;
they are not compiled (some examples intentionally have malformed names).
Execution means ATL compiled, ran on the input and produced loadable nonempty
target XMI. It is distinct from the F1 score.
The enum-only `0modelio_enum_no_name_test` has no representable facts in
`java.ecore`: it is still an execution case, but its partial F1 is N/A and
the UML→Java macro F1 denominator is nine, not ten.

Run from `LLM4ATL_Project`:

```powershell
python run_case.py --case UML2Java_All
python run_case.py --case SysMLv2ToAAS_All
```

`run_case.py` copies each generated ATL into `ATL_Tests`, runs ten JUnit
dynamic tests, then calls `score_benchmarks.py`. Outputs and per-input CSV
scores are saved under `ATL_Tests/target/benchmark-results/<case>/`.
To rerun only the fixture validation without an ATL module:

```powershell
cd ATL_Tests
mvn.cmd test -Dtest=BenchmarkFixtureLoadTest
```

To rescore existing output XMI without regenerating ATL:

```powershell
python score_benchmarks.py --case uml2java
python score_benchmarks.py --case sysml2aas
```

These benchmarks are prepared but have no generated ATL output or measured
execution/F1 until the pipeline is run with a configured LLM API key.
