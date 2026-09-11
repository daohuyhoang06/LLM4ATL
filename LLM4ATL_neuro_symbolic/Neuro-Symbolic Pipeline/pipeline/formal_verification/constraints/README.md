# External eFinder verification profiles

Each case-study directory contains a `target-post.ocl` file with target-model
properties. Several directories also contain `source-pre.ocl`, which records
the non-trivial source domain for which the corresponding transformation
property is intended. They intentionally live outside the source and target
metamodels, so existing ATL execution tests and generated artefacts remain
unchanged.

The supported declaration format is a sequence of standard Pivot OCL
invariants with a named context:

```ocl
context Interface
inv InterfaceHasMethods:
  self.methods->notEmpty()
```

Before solving, the eFinder runner imports the invariants into the temporary
ATL2TM Ecore model's Ecore/Pivot annotations. Invariants from
`target-post.ocl` are added to target `postConstraints`; those from
`source-pre.ocl` are added to source `preConstraints`. It then checks:

```text
Sem AND Pre AND NOT Post_i
```

`--check-all` selects only entries from `target-post.ocl`; `source-pre.ocl`
always remains in the premise. A case has no `source-pre.ocl` when its target
property is independent of source data (for example, a constant assigned by
an ATL rule).

When an assumption must hold even if the source classifier has no instance,
use the special `global inv` form in `source-pre.ocl`:

```ocl
global inv SourceModelIsValid:
  SourceRoot.allInstances()->exists(r | r.elements->notEmpty())
```

The runner attaches this premise to the selected target context, so it is
evaluated whenever the negated postcondition creates a target witness. A
regular `context SourceClass inv ...` remains useful for per-object rules, but
by itself is universally quantified and can be vacuously true when there are
no source objects.

The profiles are deliberately behavioural: they encode values, links, or
objects created by the reference ATL transformation, rather than merely
restating Ecore lower bounds. Source preconditions prevent a trivial empty or
out-of-domain source model from being reported as a counterexample. They are
verification assumptions, not universally mandatory constraints of the
standalone source metamodel.

## How these profiles were chosen

Each profile has been cross-checked against both the corresponding ATL module
and its JUnit execution test.  The test gives a concrete oracle, but its
fixture-specific literals and cardinalities (for example `TaskA`,
`Calculator`, or exactly three products) are not used as universal
postconditions.  Instead, the profile records the general behaviour of the
ATL bindings: preserved names and identifiers, required output containment,
and ATL-defined constants or derived value domains.

Conversely, a target attribute is deliberately absent from a postcondition
when the ATL module never assigns it.  For example, the Grafcet-to-PetriNet
profile does not claim a value for `Arc.weight`, and the PetriNet-to-Grafcet
profile does not claim a value for `Step.action`.

The selected bounds must be large enough for any cardinality created by the
ATL semantics.  In particular, `BibTeX2DocBook_All` creates four article
sections and `XML2DSL_All` creates four primitive types, so use at least
`--reference-scope 4` for those cases.  A smaller bound can return `UNSAT`
only because the bounded semantic model itself cannot be constructed.

## Run a case

Generate the ATL2TM model as usual, then point the wrapper at the case folder:

```powershell
Set-Location D:\LLM4ATL\LLM4ATL_neuro_symbolic\efinder_validator
python .\efinder_check.py <ATL2TM-output.ecore> `
  --constraints "..\Neuro-Symbolic Pipeline\pipeline\formal_verification\constraints\Class2Interface_All" `
  --check-all --scope 3 --reference-scope 6
```

Use `--check Interface::InterfaceRetainsOperationsAndParameters` to run a
single property. The
original ATL2TM Ecore is never changed; the injected and negated copy is
written below `efinder_validator/output`.

The profiles use the OCL subset supported by the current backend. A `SAT`
result is a bounded counterexample under `Sem` and the listed `Pre`, not a
proof that the ATL program is wrong in every scope. Unsupported attributes
that are unrelated to the active verification formula may be abstracted in
the temporary Ecore copy; attributes used by `Sem`, `Pre`, or `Post_i` still
produce `UNSUPPORTED_FEATURE` until a sound backend encoding is available.

Repository-local primitive aliases are normalized before that check. For
example, a custom `PrimitiveTypes::String` backed by `java.lang.String` is
mapped to Ecore `EString`; `Integer` and `Boolean` are mapped to `EInt` and
`EBoolean`. The result JSON reports these under `normalized_features`.
Non-primitive types such as `Date`, enums, or domain-specific datatypes are
not silently mapped and retain the `UNSUPPORTED_FEATURE` policy when they
affect the active formula.
