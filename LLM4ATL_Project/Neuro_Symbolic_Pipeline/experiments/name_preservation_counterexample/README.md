# NamePreservation Layer-3 counterexample test

This focused test runs the source-target obligation directly from
`constraints/direct/transformation-inv.ocl`:

```ocl
context Document
inv NamePreservation:
  Report.allInstances()->exists(r | r.title = self.title)
```

against a type-correct but semantically wrong ATL binding:

```atl
title <- d.author
```

The source precondition requires a Document with `title <> author`, preventing
the wrong binding from being hidden by equal string values.

Run from `Neuro_Symbolic_Pipeline`:

```powershell
python experiments/name_preservation_counterexample/run_test.py
```

The test passes only when ATL parsing succeeds, ATL2TM emits
`self.r.title = self.d.author`, the wrong binding and missing output return
`SAT`, the correct baseline returns `UNSAT`, and a counterexample XMI exists.
The same invariant is available in the main `input/constraints/Document2Report_All/`
profile for normal Layer-3 runs.

## LLM repair experiment

Run `python experiments/name_preservation_counterexample/run_llm_repair.py`
from `Neuro_Symbolic_Pipeline`. The script uses the LLM configured in `.env`.
It checks the wrong ATL, saves the exact Layer-3 feedback in
`results/llm_repair/feedback_to_llm.txt`, sends that feedback with the normal
pipeline prompt and AST schema, and checks the returned ATL against
`Document::NamePreservation` again. The result is bounded by object scope 3
and reference scope 6. Generated files stay under ignored `results/`.
The observed one-attempt repair result is recorded in
`llm-repair-observed-results.json`.

## Requirement-category counterexamples

Run the five independent transformation-requirement checks without invoking
an LLM:

```powershell
python experiments/name_preservation_counterexample/run_requirement_categories.py
```

The experiment covers binding correctness, mapping completeness, mapping
cardinality, relationship preservation, and mapping conditions. Each category
checks one deliberately faulty ATL and one correct ATL using
`Sem AND Pre AND NOT Inv_i`, object scope 3, and reference scope 6. The run
passes only when every faulty ATL returns `SAT` with a counterexample and every
correct ATL returns `UNSAT`. The compact observed result is stored in
`requirement-categories-observed-results.json`; detailed generated Ecore,
result JSON, and counterexample XMI files stay under ignored `results/`.
