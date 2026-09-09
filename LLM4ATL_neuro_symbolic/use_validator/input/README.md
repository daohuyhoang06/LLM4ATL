# input/ — validator inputs

Each check is a pair with the SAME base name is not required, but the output is
named `<use-stem>__<config-stem>`.

| .use | pair with .properties | expected | shows |
|---|---|---|---|
| `contradiction.use` | `contradiction.properties` | UNSATISFIABLE | `n>0 ∧ n<0` on a forced object |
| `pigeonhole.use` | `pigeonhole_unsat.properties` | UNSATISFIABLE | 3 distinct codes cannot come from 2 String atoms |
| `pigeonhole.use` | `pigeonhole_sat.properties` | SATISFIABLE | same model, 4 String atoms → instance found |
| `library.use` | `library_sat.properties` | SATISFIABLE | navigation / forAll / size() / associations, full object model + links |
| `library.use` | `library_unsat.properties` | UNSATISFIABLE | `notOverLent` (borrowers ≤ copies) caps loans below the required minimum |
| `counterexample_demo.use` | `counterexample_demo.properties` | SATISFIABLE | asserts `not P` ("everyone earns less than their manager") → the instance IS a counterexample to P |

The `pigeonhole` SAT↔UNSAT flip — same `.use`, only the String domain changes —
proves the validator genuinely solves the OCL, not just the structure.
