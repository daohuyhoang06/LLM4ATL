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
    def run_with_checks(self, checks):
        case = "__result_priority_test__"
        with tempfile.TemporaryDirectory() as directory:
            def fake_run_efinder(_case, ecore, _constraints, out_dir, *_args, **_kwargs):
                out_dir.mkdir(parents=True, exist_ok=True)
                report = out_dir / f"{ecore.stem}.all.result.json"
                report.write_text(json.dumps({
                    "status": "BATCH_COMPLETED", "checks": checks,
                }), encoding="utf-8")
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

    def test_error_still_stops_when_no_counterexample_exists(self):
        result = self.run_with_checks([
            {"check": "Section::Ambiguous", "status": "ERROR",
             "detail": "Ambiguous type Section"},
            {"check": "Report::ValidTitle", "status": "UNSAT"},
        ])
        self.assertEqual(result.status, "EFINDER_UNSUPPORTED_FEATURE")
        self.assertIn("Ambiguous type Section", result.detail)


if __name__ == "__main__":
    unittest.main()
