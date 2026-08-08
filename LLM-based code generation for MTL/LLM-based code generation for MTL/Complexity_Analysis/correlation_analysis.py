#!/usr/bin/env python3
"""
Join complexity features with per-script evaluation metrics; Spearman correlations;
bucket analysis (LoC / McCabe tertiles).
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

OUTPUT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
MTL_ROOT = REPO_ROOT / "LLM-based code generation for MTL"

PATH_ATL = MTL_ROOT / "ATL_Tests/atl_test_results.csv"
PATH_ETL = MTL_ROOT / "ETL_Test/etl_test_results.csv"
PATH_QVTO = MTL_ROOT / "QVT-O_Test/qvto_test_results.csv"
PATH_RX_PARSED = (
    MTL_ROOT
    / "Workflows/n8n-docker/workflows/updated_reactions_workflow/evaluate_generated_reactions_workflow/results/parsed_rate/parsed_rate_report.csv"
)
PATH_RX_CHRF = (
    MTL_ROOT
    / "Workflows/n8n-docker/workflows/updated_reactions_workflow/evaluate_generated_reactions_workflow/results/similarity_chrf/chrf_similarity_report.csv"
)
PATH_RX_TEST = (
    MTL_ROOT
    / "Workflows/n8n-docker/workflows/updated_reactions_workflow/evaluate_generated_reactions_workflow/evaluate_pass1rate/test_matrix_report.csv"
)


def load_complexity() -> pd.DataFrame:
    c = pd.read_csv(REPO_ROOT / "complexity_features.csv", na_values=["", " "])
    c["n_mm_artifacts"] = pd.to_numeric(c["n_mm_artifacts"], errors="coerce")
    return c


def load_atl_eval(cpx: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(PATH_ATL)
    loc_map = cpx[cpx["mtl"] == "atl"].set_index("script_key")["loc"].to_dict()
    df["mtl"] = "atl"
    df["script_key"] = df["File"].astype(str)
    df["llm"] = df["LLM"].astype(str)
    df["strategy"] = df["Strategy"].astype(str)
    df["chrf"] = pd.to_numeric(df["CHRF_Score"], errors="coerce")
    df["parsed"] = df["Parsed"].map({True: True, False: False, "True": True, "False": False})
    df["unparsed_rate"] = (~df["parsed"]).astype(float)
    ref_loc = df["script_key"].map(loc_map)
    df["ppls"] = pd.to_numeric(df["ProblemCount"], errors="coerce") / ref_loc
    tp = df["test_pass"].map({True: True, False: False, "True": True, "False": False})
    df["pass_at_1"] = (df["parsed"] & tp).astype(int)
    return df[
        ["mtl", "script_key", "llm", "strategy", "chrf", "unparsed_rate", "ppls", "pass_at_1"]
    ]


def load_etl_eval(cpx: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(PATH_ETL)
    loc_map = cpx[cpx["mtl"] == "etl"].set_index("script_key")["loc"].to_dict()
    df["mtl"] = "etl"
    df["script_key"] = df["File"].astype(str)
    df["llm"] = df["LLM"].astype(str)
    df["strategy"] = df["Strategy"].astype(str)
    df["chrf"] = pd.to_numeric(df["CHRF_Score"], errors="coerce")
    df["parsed"] = df["Parsed"].map({True: True, False: False, "True": True, "False": False})
    df["unparsed_rate"] = (~df["parsed"]).astype(float)
    ref_loc = df["script_key"].map(loc_map)
    df["ppls"] = pd.to_numeric(df["ProblemCount"], errors="coerce") / ref_loc
    tp = df["test_pass"].map({True: True, False: False, "True": True, "False": False})
    df["pass_at_1"] = (df["parsed"] & tp).astype(int)
    return df[
        ["mtl", "script_key", "llm", "strategy", "chrf", "unparsed_rate", "ppls", "pass_at_1"]
    ]


def load_qvto_eval(cpx: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(PATH_QVTO)
    loc_map = cpx[cpx["mtl"] == "qvto"].set_index("script_key")["loc"].to_dict()
    df["mtl"] = "qvto"
    df["script_key"] = df["file"].apply(lambda x: Path(str(x)).stem)
    df["llm"] = df["model"].astype(str)
    df["strategy"] = df["strategy"].astype(str)
    # Normalize ChrF to 0–100 (repository uses 0–1)
    df["chrf"] = pd.to_numeric(df["chrF"], errors="coerce") * 100.0
    df["parsed"] = df["parse_success"]
    df["unparsed_rate"] = (~df["parsed"]).astype(float)
    ref_loc = df["script_key"].map(loc_map)
    df["ppls"] = pd.to_numeric(df["problem_count"], errors="coerce") / ref_loc
    df["pass_at_1"] = (df["parsed"] & df["test_pass"]).astype(int)
    return df[
        ["mtl", "script_key", "llm", "strategy", "chrf", "unparsed_rate", "ppls", "pass_at_1"]
    ]


def load_reactions_eval() -> pd.DataFrame:
    parsed = pd.read_csv(PATH_RX_PARSED)
    chrf = pd.read_csv(PATH_RX_CHRF)
    test = pd.read_csv(PATH_RX_TEST)

    parsed["script_key"] = parsed["ReactionFile"].apply(
        lambda p: Path(str(p).split("/")[-1]).stem
    )
    chrf["script_key"] = chrf["File"].astype(str)
    test["script_key"] = test["Task"].astype(str)

    merged = parsed.merge(
        chrf,
        on=["LLM", "Strategy", "script_key"],
        how="inner",
        suffixes=("_p", ""),
    )
    merged = merged.merge(
        test,
        on=["LLM", "Strategy", "script_key"],
        how="inner",
    )
    merged["mtl"] = "reactions"
    merged["llm"] = merged["LLM"].astype(str)
    merged["strategy"] = merged["Strategy"].astype(str)
    merged["chrf"] = pd.to_numeric(merged["Score"], errors="coerce")
    merged["parsed"] = merged["Parsed"].map(
        {True: True, False: False, "True": True, "False": False}
    )
    merged["unparsed_rate"] = (~merged["parsed"]).astype(float)
    merged["ppls"] = pd.to_numeric(merged["ErrorsPerLineOfCode"], errors="coerce")
    # Pass@1: syntactic parse succeeds AND Maven test stage completed successfully
    merged["pass_at_1"] = (
        (merged["parsed"]) & (merged["Stage"].astype(str) == "ok")
    ).astype(int)

    return merged[
        ["mtl", "script_key", "llm", "strategy", "chrf", "unparsed_rate", "ppls", "pass_at_1"]
    ]


def build_eval_table(cpx: pd.DataFrame) -> pd.DataFrame:
    parts = [
        load_atl_eval(cpx),
        load_etl_eval(cpx),
        load_qvto_eval(cpx),
        load_reactions_eval(),
    ]
    return pd.concat(parts, ignore_index=True)


COMPLEXITY_FEATURES = ["loc", "n_rules", "n_helpers", "n_mm_artifacts", "mccabe"]
QUALITY_METRICS = ["chrf", "unparsed_rate", "ppls", "pass_at_1"]


def spearman_safe(
    x: np.ndarray, y: np.ndarray
) -> Tuple[float, float, int]:
    mask = np.isfinite(x) & np.isfinite(y)
    n = int(mask.sum())
    if n < 3:
        return float("nan"), float("nan"), n
    xs, ys = x[mask], y[mask]
    if np.nanstd(xs) == 0 or np.nanstd(ys) == 0:
        return float("nan"), float("nan"), n
    r, p = stats.spearmanr(xs, ys)
    return float(r), float(p), n


def correlation_table(cpx: pd.DataFrame, ev: pd.DataFrame) -> pd.DataFrame:
    j = ev.merge(
        cpx,
        on=["mtl", "script_key"],
        how="left",
        suffixes=("", "_cpx"),
    )
    rows: List[dict] = []
    for mtl in j["mtl"].unique():
        sub = j[j["mtl"] == mtl]
        for llm in sub["llm"].unique():
            for strat in sub["strategy"].unique():
                sel = sub[(sub["llm"] == llm) & (sub["strategy"] == strat)]
                for cf in COMPLEXITY_FEATURES:
                    xv = pd.to_numeric(sel[cf], errors="coerce").to_numpy()
                    for qm in QUALITY_METRICS:
                        yv = pd.to_numeric(sel[qm], errors="coerce").to_numpy()
                        rho, p, n = spearman_safe(xv, yv)
                        rows.append(
                            {
                                "mtl": mtl,
                                "llm": llm,
                                "strategy": strat,
                                "complexity_feature": cf,
                                "quality_metric": qm,
                                "spearman_rho": rho,
                                "p_value": p,
                                "n": n,
                            }
                        )
    return pd.DataFrame(rows)


def main() -> None:
    cpx = load_complexity()
    ev = build_eval_table(cpx)
    corr_df = correlation_table(cpx, ev)
    corr_df.to_csv(OUTPUT_DIR / "correlation_results.csv", index=False)
    print(f"Wrote correlation_results.csv ({len(corr_df)} rows)")


if __name__ == "__main__":
    main()
