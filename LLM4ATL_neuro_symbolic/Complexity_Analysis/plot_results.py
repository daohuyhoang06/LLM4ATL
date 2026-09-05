#!/usr/bin/env python3
"""
Figures: bucket Pass@1 bar chart; scatter complexity vs quality (PDF multi-page).
Also writes table1_extended.tex from complexity_features.csv.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

OUTPUT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
MTL_ROOT = REPO_ROOT / "LLM4ATL_neuro_symbolic"

MTL_LABEL = {
    "atl": "ATL",
    "reactions": "Reactions",
    "etl": "ETL",
    "qvto": "QVTo",
}
MTL_COLORS = {
    "atl": "#1f77b4",
    "reactions": "#ff7f0e",
    "etl": "#2ca02c",
    "qvto": "#d62728",
}


def fmt_stat(x: float, nd: int = 1) -> str:
    if not np.isfinite(x):
        return "---"
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.{nd}f}"


def agg_stats(s: pd.Series) -> Tuple[float, float, float, float]:
    s = pd.to_numeric(s, errors="coerce").dropna()
    if s.empty:
        return (np.nan, np.nan, np.nan, np.nan)
    return (
        float(s.min()),
        float(s.median()),
        float(s.max()),
        float(s.mean()),
    )


def write_table1_extended() -> None:
    df = pd.read_csv(OUTPUT_DIR / "complexity_features.csv", na_values=["", " "])
    lines: List[str] = []
    lines.append(r"\begin{table*}[t]")
    lines.append(r"\centering")
    lines.append(
        r"\caption{Per-script complexity of canonical reference transformations (47 scripts), "
        r"aggregated by MTL. LoC counts non-empty, non-comment lines. "
        r"McCabe-style metric sums $(1 + \text{explicit control-flow tokens})$ per rule/helper/routine/mapping body (see analysis notes).}"
    )
    lines.append(r"\begin{tabular}{l r rrrr rrrr rrrr rrrr rrrr}")
    lines.append(r"\toprule")
    lines.append(
        r"MTL & $N$ & "
        r"\multicolumn{4}{c}{LoC} & \multicolumn{4}{c}{McCabe} & "
        r"\multicolumn{4}{c}{$n_{\mathrm{rules}}$} & \multicolumn{4}{c}{$n_{\mathrm{helpers}}$} & "
        r"\multicolumn{4}{c}{$n_{\mathrm{mm}}$} \\"
    )
    lines.append(
        r" &  & min & med & max & $\mu$ & min & med & max & $\mu$ & "
        r"min & med & max & $\mu$ & min & med & max & $\mu$ & "
        r"min & med & max & $\mu$ \\"
    )
    lines.append(r"\midrule")
    for mtl, sub in df.groupby("mtl"):
        n = len(sub)
        loc_s = agg_stats(sub["loc"])
        mc_s = agg_stats(sub["mccabe"])
        nr_s = agg_stats(sub["n_rules"])
        nh_s = agg_stats(sub["n_helpers"])
        nm_s = agg_stats(sub["n_mm_artifacts"])
        row = [MTL_LABEL.get(mtl, mtl), str(n)]
        for tup in (loc_s, mc_s, nr_s, nh_s, nm_s):
            row.extend([fmt_stat(tup[0]), fmt_stat(tup[1]), fmt_stat(tup[2]), fmt_stat(tup[3])])
        lines.append(" & ".join(row) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\label{tab:complexity-by-mtl}")
    lines.append(r"\end{table*}")
    out = OUTPUT_DIR / "table1_extended.tex"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


def choose_scatter_feature() -> str:
    cr = pd.read_csv(OUTPUT_DIR / "correlation_results.csv")
    cr = cr[np.isfinite(cr["spearman_rho"]) & (cr["n"] >= 5)].copy()
    if cr.empty:
        return "loc"
    cr["abs"] = cr["spearman_rho"].abs()
    row = cr.loc[cr["abs"].idxmax()]
    return str(row["complexity_feature"])


def load_plot_frame() -> Tuple[pd.DataFrame, pd.DataFrame]:
    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from correlation_analysis import build_eval_table, load_complexity

    cpx = load_complexity()
    ev = build_eval_table(cpx)
    j = ev.merge(cpx, on=["mtl", "script_key"], how="left")
    return j, cpx



def plot_scatter_complexity() -> None:
    feat = choose_scatter_feature()
    j, _ = load_plot_frame()
    llms = sorted(j["llm"].unique())
    strats = sorted(j["strategy"].unique())
    nrows, ncols = len(llms), len(strats)
    fig_p = OUTPUT_DIR / "scatter_complexity_vs_quality.pdf"
    from matplotlib.backends.backend_pdf import PdfPages

    with PdfPages(fig_p) as pdf:
        for yname, ylab in [("pass_at_1", "Pass@1"), ("chrf", "ChrF (0--100)")]:
            fig, axes = plt.subplots(
                nrows,
                ncols,
                figsize=(2.2 * ncols, 2.0 * nrows),
                squeeze=False,
            )
            for r, llm in enumerate(llms):
                for c, st in enumerate(strats):
                    ax = axes[r][c]
                    sel = j[(j["llm"] == llm) & (j["strategy"] == st)]
                    if sel.empty:
                        ax.set_visible(False)
                        continue
                    for mtl in sorted(sel["mtl"].unique()):
                        s2 = sel[sel["mtl"] == mtl]
                        xv = pd.to_numeric(s2[feat], errors="coerce")
                        yv = pd.to_numeric(s2[yname], errors="coerce")
                        ax.scatter(
                            xv,
                            yv,
                            s=22,
                            alpha=0.75,
                            color=MTL_COLORS[mtl],
                        )
                    ax.set_title(f"{llm}\n{st}", fontsize=7)
                    ax.set_xlabel(feat, fontsize=7)
                    ax.set_ylabel(ylab, fontsize=7)
                    ax.tick_params(labelsize=6)
            leg_mtls = ["atl", "reactions", "etl", "qvto"]
            handles = [
                Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="w",
                    markerfacecolor=MTL_COLORS[m],
                    markersize=7,
                    label=MTL_LABEL[m],
                )
                for m in leg_mtls
            ]
            fig.legend(
                handles=handles,
                loc="upper center",
                bbox_to_anchor=(0.5, 1.02),
                ncol=4,
                fontsize=7,
            )
            fig.suptitle(
                f"Reference-script {feat} vs {ylab} (max $|\\rho|$ feature, $n\\geq 5$)",
                fontsize=9,
                y=1.08,
            )
            fig.tight_layout(rect=[0, 0, 1, 1.05])
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
    print(f"Wrote {fig_p} (feature={feat})")


def main() -> None:
    write_table1_extended()
    plot_scatter_complexity()


if __name__ == "__main__":
    main()
