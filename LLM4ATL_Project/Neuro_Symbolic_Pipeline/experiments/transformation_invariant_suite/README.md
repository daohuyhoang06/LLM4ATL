# Transformation invariant suite

This suite adds one independent source-target invariant to each task reported
as verifiable in Table 3 (`UNSAT` or `SAT -> UNSAT`). It uses the ATL files in
`output/final_responses/atl/` and the case-specific profiles in
`input/constraints/`. Tasks reported as `UNSUPPORTED` are outside this suite.
These invariants use short names. A class name present in both source and target
causes an ambiguity error; package-qualified names are currently unsupported.

From `Neuro_Symbolic_Pipeline`, run:

```powershell
python experiments/transformation_invariant_suite/run.py
```

The script checks only the new `transformation-inv.ocl` obligation for each
task, with object scope 3 and reference scope 6. It writes the per-task eFinder
results and a combined `results/summary.json`. `UNSAT` means no counterexample
was found within those bounds, not an unbounded correctness proof. Existing
target postconditions are checked separately by the normal `--check-all` run.
