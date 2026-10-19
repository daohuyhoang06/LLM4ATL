# SOICT 2026 Submission 2052 - Replication Package for Tables 1 & 2

**Paper Title:** Neuro-Symbolic LLM-Based Generation and Verification of ATL Transformations  
**Submission ID:** 2052 (SOICT 2026)  
**Authors:** Huy-Hoang Dao, Duc-Quyen Nguyen, Duc-Hanh Dang  
**Frozen Git Commit:** `dec23a256e8fdc52aca3a28c86b49028919c4afe`  
**Target Release Tag:** `v1.0.0-soict2052-initial`  

---

## 1. Overview and Purpose

This replication package addresses **Minor Comment #4 from Reviewer 1**:
> *"Lưu trữ công cụ và toàn bộ nhật ký thực nghiệm thô (raw experimental traces) tại một phiên bản cố định, không thể thay đổi (immutable revision), để người khác có thể tái tạo độc lập Bảng 1 và Bảng 2."*

It archives the **exact raw traces, generated transformations, parser metrics, and test execution results** that produced **Table 1** and **Table 2** in the submitted paper, prior to any subsequent revisions or experimental reruns.

---

## 2. Directory Structure

```text
replication_package_soict2052/
├── README.md                      # This documentation
├── metadata.json                  # Machine-readable experiment parameters and metadata
├── reproduce_tables.py            # 1-click self-contained reproducibility script
├── tables/                        # Output reproduced tables (CSV format)
│   ├── table1_verification_layers.csv
│   ├── table2_prompting_comparison.csv
│   └── per_task_evaluation_matrix.csv
└── raw_traces/
    ├── atl_parser/                # Raw ATL parser output metrics
    │   ├── atl_parsed_rate_*.csv  # Parsed status & ProblemCount per task
    │   ├── atl_ppls_*.csv         # Problems Per Line of code (PPLs) per task
    │   ├── atl_chrf_*.csv         # ChrF similarity scores against references
    │   └── atl_parser_chrf_results_*.csv
    ├── atl_tests/                 # Raw ATL functional test execution logs
    │   ├── atl_test_results_*.csv # test_pass boolean per task
    │   └── atl_pass_rate_summary_*.csv
    ├── neuro_symbolic_pipeline/   # Neuro-symbolic pipeline outputs
    │   ├── final_responses/
    │   │   ├── atl/               # Final generated ATL files (15 benchmark tasks + ER2REL)
    │   │   └── atl_ast/           # Final generated AST JSON models
    │   └── formal_verification/   # Full formal verification traces & repair attempts
    │       ├── pipeline_attempts/ # Step-by-step verification reports (ATL2TM + eFinder)
    │       ├── llm_repair_runs/   # Multi-turn repair iterations and error diagnostics
    │       └── candidates/        # Candidate ATL ASTs per iteration
    ├── prompting_baselines/       # Baseline generated ATL transformations
    │   └── gemini-3-5-flash/
    │       ├── only_prompt/       # Baseline (Prompt only) - 15 .atl files
    │       ├── few_shot/          # Few-shot (FS) - 15 .atl files
    │       ├── grammar/           # Grammar (GR) - 15 .atl files
    │       └── few_shots_AND_grammar/ # FS + GR - 15 .atl files
    └── references/                # Reference ATL transformations (Ground Truth)
```

---

## 3. How to Reproduce Tables 1 and 2

### Quick Run (1-Click)

From this directory or repository root, run:

```bash
python replication_package_soict2052/reproduce_tables.py
```

The script will:
1. Parse all raw CSV traces directly from `raw_traces/`.
2. Compute the exact metrics (ChrF, Parsed rate, PPLs, Tests Passed).
3. Print formatted Markdown and LaTeX tables for **Table 1** and **Table 2**.
4. Output a detailed **15-task outcome matrix** showing pass/fail status per method.
5. Save the generated tables to `tables/`.

---

## 4. Benchmark Tasks and Evaluation Metrics

The evaluation suite consists of **15 ATL transformation tasks** adapted from the LLM4MTLs benchmark:

1. `AmaltheaToAscet_All`
2. `BibTeX2DocBook_All`
3. `Class2Interface_All`
4. `CPL2SPL_All`
5. `Document2Report_All`
6. `DSL2KM3_All`
7. `FamiliesToPersons_All`
8. `Grafcet2PetriNet_All`
9. `IEEE1471_2_MoDAF_All`
10. `Item2Product_All`
11. `Make2Ant_All`
12. `NetworkToGraph_All`
13. `PetriNet2Grafcet_All`
14. `User2Account_All`
15. `XML2DSL_All`

*(Note: `ER2REL` serves as the motivating example for formal verification.)*

### Metrics Definition:
- **ChrF ↑**: Mean character n-gram F-score comparing generated ATL to canonical reference ATL.
- **Parsed ↑**: Proportion of transformations parsed without syntax errors by the ATL compiler (`ProblemCount == 0`).
- **PPLs ↓**: Average syntax problems per line of code across benchmark tasks.
- **Tests Passed ↑**: Proportion of transformations passing 100% of the associated functional test cases on concrete input models.

---

## 5. Mapping Between Paper Tables and Raw Traces

### Table 1: Incremental Evaluation of Verification Layers

| Configuration | Parsed ↑ | PPLs ↓ | Tests Passed ↑ | Raw Trace Source |
|---|---|---|---|---|
| **Structural Checking (L1)** | 11/15 (0.73) | 0.0178 | 8/15 (0.53) | L1 AST validator |
| **Structural + Static Analysis (L1+L2)** | 15/15 (1.00) | 0.0000 | 10/15 (0.67) | L1+L2 semantic checker |
| **Complete Method (L1+L2+L3)** | 15/15 (1.00) | 0.0000 | 13/15 (0.87) | `raw_traces/atl_tests/atl_test_results_gemini-3-5-flash_neuro_symbolic.csv` |

### Table 2: Comparison with Prompting Strategies

| Method | ChrF ↑ | Parsed ↑ | PPLs ↓ | Tests Passed ↑ | Raw Trace Source |
|---|---|---|---|---|---|
| **Baseline** | 0.55 | 0.87 (13/15) | 0.0047 | 0.47 (7/15) | `atl_*_gemini-3-5-flash_only_prompt.csv` |
| **Few-shot (FS)** | 0.57 | 0.87 (13/15) | 0.0035 | 0.47 (7/15) | `atl_*_gemini-3-5-flash_few_shot.csv` |
| **Grammar (GR)** | 0.56 | 0.93 (14/15) | 0.0015 | 0.53 (8/15) | `atl_*_gemini-3-5-flash_grammar.csv` |
| **FS + GR** | 0.57 | 0.93 (14/15) | 0.0002 | 0.47 (7/15) | `atl_*_gemini-3-5-flash_few_shots_AND_grammar.csv` |
| **Proposed Method** | 0.59 | 1.00 (15/15) | 0.0000 | 0.87 (13/15) | `atl_*_gemini-3-5-flash_neuro_symbolic.csv` |
