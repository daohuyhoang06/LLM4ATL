#!/usr/bin/env python3
"""Print generation, parser, PPLS, and ATL functional-test metrics.

The script reads one strategy's ``run_summary.json`` plus the corresponding
ATL_Parser and ATL_Tests CSV reports, then prints the aggregate metrics to the
terminal. It does not create any new report file.

PPLS is calculated from the current parser result as::

    ProblemCount / reference_lines

This ensures it is consistent with the parser report selected for the run.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any


STRATEGIES_DIR = Path(__file__).resolve().parent
PROJECT_DIR = STRATEGIES_DIR.parent
PARSER_DIR = PROJECT_DIR / "ATL_Parser"
TESTS_DIR = PROJECT_DIR / "ATL_Tests"
REFERENCES_DIR = (
    STRATEGIES_DIR
    / "n8n-docker"
    / "mtl_snippets"
    / "ATLAS_transformation_language"
    / "references"
)


def read_csv_by_task(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as file:
        return {row["File"]: row for row in csv.DictReader(file)}


def find_latest_report(directory: Path, prefix: str) -> Path | None:
    reports = sorted(directory.glob(f"{prefix}*.csv"), key=lambda path: path.stat().st_mtime, reverse=True)
    return reports[0] if reports else None


def resolve_report(explicit: Path | None, directory: Path, prefix: str, label: str) -> Path:
    path = explicit.resolve() if explicit else find_latest_report(directory, prefix)
    if path is None or not path.exists():
        raise FileNotFoundError(
            f"No {label} report found. Pass --{label}-results explicitly or generate the report first."
        )
    return path


def to_bool(value: str | None) -> bool | None:
    if value is None or value == "":
        return None
    return value.strip().lower() == "true"


def to_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def reference_line_count(task_name: str) -> int | None:
    reference = REFERENCES_DIR / f"{task_name}.atl"
    if not reference.exists():
        return None
    return len(reference.read_text(encoding="utf-8").splitlines())


def numeric_summary(tasks: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    values = [(task["task"], to_number(task.get(metric))) for task in tasks]
    values = [(name, value) for name, value in values if value is not None]
    if not values:
        return {"count": 0, "average": None, "min": None, "max": None}
    minimum = min(values, key=lambda pair: pair[1])
    maximum = max(values, key=lambda pair: pair[1])
    return {
        "count": len(values),
        "average": round(mean(value for _, value in values), 3),
        "min": {"task": minimum[0], "value": minimum[1]},
        "max": {"task": maximum[0], "value": maximum[1]},
    }


def rate_summary(tasks: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    values = [task.get(metric) for task in tasks if task.get(metric) is not None]
    positive = sum(value is True for value in values)
    return {
        "count": len(values),
        "passed": positive,
        "failed": len(values) - positive,
        "rate_percent": round(positive / len(values) * 100, 2) if values else None,
    }


def format_number(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.3f}"


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    """Print a dependency-free ASCII table suitable for PowerShell/cmd."""
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    def render(row: list[str]) -> str:
        return "|" + "|".join(f" {cell:<{widths[index]}} " for index, cell in enumerate(row)) + "|"

    print(border)
    print(render(headers))
    print(border)
    for row in rows:
        print(render(row))
    print(border)


def statistic_row(metric: str, summary: dict[str, Any], unit: str = "") -> list[str]:
    minimum = summary["min"]
    maximum = summary["max"]
    min_text = "N/A" if minimum is None else f"{format_number(minimum['value'])}{unit} ({minimum['task']})"
    max_text = "N/A" if maximum is None else f"{format_number(maximum['value'])}{unit} ({maximum['task']})"
    return [metric, str(summary["count"]), f"{format_number(summary['average'])}{unit}", min_text, max_text]


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize ATL prompting strategy metrics")
    parser.add_argument("--strategy", required=True, help="Strategy directory name, e.g. only_prompt")
    parser.add_argument("--llm", default="gemini-3-5-flash", help="LLM label used in parser/test report names")
    parser.add_argument("--run-summary", type=Path, default=None, help="Path to run_summary.json")
    parser.add_argument("--parser-results", type=Path, default=None, help="Path to atl_parser_chrf_results CSV")
    parser.add_argument("--test-results", type=Path, default=None, help="Path to atl_test_results CSV")
    args = parser.parse_args()

    output_dir = STRATEGIES_DIR / "output" / args.strategy
    run_summary_path = (args.run_summary or output_dir / "run_summary.json").resolve()
    if not run_summary_path.exists():
        raise FileNotFoundError(f"Run summary not found: {run_summary_path}")

    parser_results_path = resolve_report(
        args.parser_results,
        PARSER_DIR,
        f"atl_parser_chrf_results_{args.llm}_{args.strategy}",
        "parser",
    )
    test_results_path = resolve_report(
        args.test_results,
        TESTS_DIR,
        f"atl_test_results_{args.llm}_{args.strategy}",
        "test",
    )

    run_summary = json.loads(run_summary_path.read_text(encoding="utf-8"))
    parser_rows = read_csv_by_task(parser_results_path)
    test_rows = read_csv_by_task(test_results_path)

    tasks: list[dict[str, Any]] = []
    for task in run_summary.get("tasks", []):
        task_name = task["task"]
        metrics = task.get("metrics", {})
        parser_row = parser_rows.get(task_name, {})
        test_row = test_rows.get(task_name, {})
        reference_lines = reference_line_count(task_name)
        problem_count = to_number(parser_row.get("ProblemCount"))
        ppls = problem_count / reference_lines if problem_count is not None and reference_lines else None
        tasks.append({
            "task": task_name,
            "status": task.get("status"),
            "parsed": to_bool(parser_row.get("Parsed")),
            "problem_count": int(problem_count) if problem_count is not None else None,
            "reference_lines": reference_lines,
            "ppls": ppls,
            "test_pass": to_bool(test_row.get("test_pass")),
            "input_tokens": metrics.get("input_tokens"),
            "output_tokens": metrics.get("output_tokens"),
            "total_tokens": metrics.get("total_tokens"),
            "task_elapsed_seconds": metrics.get("task_elapsed_seconds"),
            "llm_elapsed_seconds": metrics.get("llm_elapsed_seconds"),
        })

    summary = {
        "llm": args.llm,
        "strategy": args.strategy,
        "task_count": len(tasks),
        "sources": {
            "run_summary": str(run_summary_path),
            "parser_results": str(parser_results_path),
            "test_results": str(test_results_path),
        },
        "parsed": rate_summary(tasks, "parsed"),
        "test_pass": rate_summary(tasks, "test_pass"),
        "ppls": numeric_summary(tasks, "ppls"),
        "input_tokens": numeric_summary(tasks, "input_tokens"),
        "output_tokens": numeric_summary(tasks, "output_tokens"),
        "total_tokens": numeric_summary(tasks, "total_tokens"),
        "task_elapsed_seconds": numeric_summary(tasks, "task_elapsed_seconds"),
        "llm_elapsed_seconds": numeric_summary(tasks, "llm_elapsed_seconds"),
    }

    print(f"\nStrategy: {args.strategy} | LLM: {args.llm} | Tasks: {len(tasks)}\n")
    print_table(
        ["Evaluation metric", "Passed", "Failed", "Rate"],
        [
            ["Parsed", str(summary["parsed"]["passed"]), str(summary["parsed"]["failed"]), f"{summary['parsed']['rate_percent']}%"],
            ["Test pass", str(summary["test_pass"]["passed"]), str(summary["test_pass"]["failed"]), f"{summary['test_pass']['rate_percent']}%"],
        ],
    )
    print()
    print_table(
        ["Metric", "Tasks", "Average", "Min (task)", "Max (task)"],
        [
            statistic_row("PPLS", summary["ppls"]),
            statistic_row("Input tokens", summary["input_tokens"]),
            statistic_row("Output tokens", summary["output_tokens"]),
            statistic_row("Total tokens", summary["total_tokens"]),
            statistic_row("Task execution time", summary["task_elapsed_seconds"], "s"),
        ],
    )


if __name__ == "__main__":
    main()
