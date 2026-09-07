# use_validator — headless USE Model Validator

One job: run the **USE Model Validator** (Kodkod / SAT) on a UML/OCL model and a
search configuration, head-less, and report **SATISFIABLE** (with the found
object model) or **UNSATISFIABLE**.

```
use_validator/
├── mv_check.py        the runner
├── input/             INPUT  — .use models + .properties configs
└── output/            OUTPUT — one result per run, written by mv_check.py
```

The `.use` + `.properties` files are produced by other tooling (ATL →
transformation model → specification + search configuration). This folder is
only the "import the validator" step.

## Requirements

* Python 3.10+ (standard library only)
* Java 17+ on `PATH`
* `../use_core/use-gui.jar` (USE 7.x) and `../use_core/validator-7.1.1.jar`
  (Model Validator plugin). Nothing is installed — `mv_check.py` builds a
  throw-away `USE_HOME` with `lib/plugins/<plugin>.jar` and points `use` at it.

## Usage

```bash
python3 mv_check.py input/<model>.use input/<config>.properties
python3 mv_check.py input/<model>.use input/<config>.properties --json
python3 mv_check.py input/<model>.use input/<config>.properties --out-dir /tmp/run1
python3 mv_check.py input/<model>.use input/<config>.properties --no-save   # stdout only
```

Exit code: 0 if the validator returned SAT or UNSAT, 1 on error/timeout.

## INPUT — `input/`

A pair per check:

* `<name>.use` — UML class model + OCL. To look for a **counterexample to a
  property P**, assert `not P` (existentially, at model level):

  ```
  context C inv NOT_P:
    C.allInstances->exists(x | not ( <P with self := x> ))
  ```

* `<name>.properties` — the search configuration:

  ```
  <Class>_min = 0        <Class>_max = 3          -- objects per class
  <Assoc>_min = 0        <Assoc>_max = -1         -- links per association (-1 = unbounded)
  Integer_min = 0        Integer_max = 5
  String_min = 1         String_max = 4           -- number of distinct String atoms
  Real_min = 0           Real_max = 0             Real_step = 1
  <Class>_<attr> = Set{'a','b'}                   -- restrict an attribute's value pool (optional)
  <Context>_<InvName> = active                    -- enable an invariant (list every one to enforce)
  ```

The provided pairs (see `input/`): `contradiction`, `pigeonhole` (+`_sat`/`_unsat`),
`library` (+`_sat`/`_unsat`), `counterexample_demo`.

## OUTPUT — `output/`

Named after the two input file stems, `<use>__<config>`:

| file | when | contents |
|---|---|---|
| `<use>__<config>.result.json` | always | `status` (SATISFIABLE / UNSATISFIABLE / error / timeout), `stats`, and on SAT the parsed `instance` (`objects` + `links`) |
| `<use>__<config>.soil` | only on SATISFIABLE | the found object model as a USE `!new` / `!o.a := v` / `!insert (a,b) into A` script — the raw instance / counterexample |

## What the result means

| validator says | meaning | counterexample |
|---|---|---|
| **SATISFIABLE** | `not P` is satisfiable → **P is violated** | the returned object model **is** the counterexample (`.soil` + `instance` in the JSON) |
| **UNSATISFIABLE** | no instance breaks `P` within the configured bounds → **P holds up to that bound** | none — no `.soil` written |

`UNSATISFIABLE` is the *good* answer for a correctness check. A real bug that fits
in the bounds always comes back as SAT with the instance; a bug needing more
objects than the bounds is missed — raise the bounds (this is the "bounded"
limitation).
