# ATL2TM source fragments

`ATL2TM.atl` in the parent directory is the generated module used by the existing ATL runner and Java tests. Edit the `.atlpart` files here, then run `python build.py` to update it. Run `python build.py --check` to verify that it is current. The Python formal-verification runner builds it automatically before invoking ATL.

The `steps/` files follow Figure 5 of *Verification of ATL Transformations Using Transformation Models and Model Finders*:

1. Copy the source and target metamodels, including their OCL constraints.
2. Create trace classes and associations; encode matching, bindings, implicit resolution, and frame conditions.
3. Require each target object to have exactly one creator.
4. Exclude overlapping matched rules.

`common/` holds shared expression rendering, analysis, and generation support. `extensions/Provenance.atlpart` holds metadata used by the current verification pipeline. These fragments contain only declarations already present on this branch; the split does not add ATL features.

ATL needs one module. Each `-- @hot-atl2tm-part NNNN` marker identifies the following original code segment. `build.py` joins segments by marker number, preserving the existing declaration order and exact content. Keep each marker with its code when moving a segment; marker numbers must stay unique and consecutive. Do not edit the generated `ATL2TM.atl` directly.
