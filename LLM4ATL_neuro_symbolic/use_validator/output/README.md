# output/ — validator results

`mv_check.py` writes here, one pair of files per run, named `<use-stem>__<config-stem>`:

- `*.result.json` — always. `status` (SATISFIABLE / UNSATISFIABLE / error / timeout),
  `stats`, and on SAT the parsed `instance` (`objects` + `links`) plus a pointer to the `.soil`.
- `*.soil` — only on SATISFIABLE. The found object model as a USE
  `!new` / `!o.attr := v` / `!insert (a,b) into Assoc` script. This is the raw
  instance = the counterexample when the input `.use` asserted `not P`.

Generated files are git-ignored (see `.gitignore`).
