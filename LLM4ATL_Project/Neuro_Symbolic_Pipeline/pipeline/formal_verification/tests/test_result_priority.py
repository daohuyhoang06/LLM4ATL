"""Layer 3 must deliver a found counterexample even when another check errors."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_case  # noqa: E402


class ResultPriorityTest(unittest.TestCase):
    def run_with_checks(self, checks, baseline_status=None):
        case = "__result_priority_test__"
        with tempfile.TemporaryDirectory() as directory:
            def fake_run_efinder(_case, ecore, _constraints, out_dir, *_args, **_kwargs):
                out_dir.mkdir(parents=True, exist_ok=True)
                report = out_dir / f"{ecore.stem}.all.result.json"
                summary = {
                    "status": "BATCH_COMPLETED", "checks": checks,
                }
                if baseline_status:
                    summary.update(status="BASELINE_UNSAT" if baseline_status == "UNSAT"
                                   else "BASELINE_ERROR", satisfiability={"status": baseline_status})
                report.write_text(json.dumps(summary), encoding="utf-8")
                return 0

            with patch.object(run_case, "run_atl2tm"), patch.object(
                run_case, "run_efinder", side_effect=fake_run_efinder
            ):
                return run_case.verify_atl_for_pipeline(
                    case, Path("unused.atl"), Path("source.ecore"),
                    Path("target.ecore"), output_root=Path(directory),
                )

    def test_sat_takes_priority_over_ambiguous_name_error(self):
        result = self.run_with_checks([
            {"check": "Section::Ambiguous", "status": "ERROR",
             "detail": "Ambiguous type Section"},
            {"check": "Document::NamePreservation", "status": "SAT"},
            {"check": "Report::ValidTitle", "status": "UNSAT"},
        ])
        self.assertEqual(result.status, "COUNTEREXAMPLE")
        self.assertIn("Document::NamePreservation", result.feedback)
        self.assertNotIn("Section::Ambiguous", result.feedback)
        self.assertIn("1 other check(s) had verifier errors", result.detail)
        self.assertIsNotNone(result.report)

    def test_unsat_baseline_stops_without_llm_feedback(self):
        result = self.run_with_checks([], baseline_status="UNSAT")
        self.assertEqual(result.status, "SATISFIABILITY_UNSAT")
        self.assertFalse(result.feedback)
        self.assertIn("LLM will not retry", result.detail)

    def test_error_still_stops_when_no_counterexample_exists(self):
        result = self.run_with_checks([
            {"check": "Section::Ambiguous", "status": "ERROR",
             "detail": "Ambiguous type Section"},
            {"check": "Report::ValidTitle", "status": "UNSAT"},
        ])
        self.assertEqual(result.status, "EFINDER_UNSUPPORTED_FEATURE")
        self.assertIn("Ambiguous type Section", result.detail)

    def test_feedback_includes_all_violated_ocl_and_xmi_content(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "transformation-inv.ocl").write_text(
                "context Document inv KeepName: self.title = 'expected'", encoding="utf-8")
            (folder / "target-post.ocl").write_text(
                "context Report inv HasTitle: self.title <> ''", encoding="utf-8")
            witness = folder / "witness.xmi"
            witness.write_text('<source title="actual"/>', encoding="utf-8")
            feedback = run_case._counterexample_feedback([
                {"check": "Document::KeepName", "counterexample_file": str(witness)},
                {"check": "Report::HasTitle", "counterexample_file": str(witness)},
            ], folder)
            self.assertIn("Document::KeepName", feedback)
            self.assertIn("Report::HasTitle", feedback)
            self.assertIn("self.title = 'expected'", feedback)
            self.assertIn("self.title <> ''", feedback)
            self.assertEqual(feedback.count('<source title="actual"/>'), 2)


if __name__ == "__main__":
    unittest.main()
