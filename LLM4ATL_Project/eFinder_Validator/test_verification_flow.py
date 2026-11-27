"""Regression checks for the baseline gate and complete counterexample collection."""
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import efinder_check as verifier


class VerificationFlowTest(unittest.TestCase):
    def args(self):
        return SimpleNamespace(ecore=Path("unused.ecore"), constraints=None, progress=True)

    def test_unsat_and_errors_stop_before_properties(self):
        for status in ("UNSAT", "SOLVER_ERROR", "TIMEOUT"):
            with self.subTest(status=status), patch.object(verifier, "is_atl2tm", return_value=True), \
                    patch.object(verifier, "run_one", return_value=({"status": status}, 0)) as run, \
                    redirect_stdout(io.StringIO()):
                result = verifier.run_verification(self.args(), ["A::P"])
                self.assertEqual(result["checks"], [])
                self.assertIn(result["status"], {"BASELINE_UNSAT", "BASELINE_ERROR"})
                run.assert_called_once()

    def test_collects_all_sat_and_groups_terminal_output(self):
        output = io.StringIO()
        calls = []
        def run(_args, check):
            calls.append(check)
            return {"status": "UNSAT" if check == "B::Good" else "SAT", "check": check}, 0
        with patch.object(verifier, "is_atl2tm", return_value=True), \
                patch.object(verifier, "invariant_checks", return_value={"A::First", "A::Second"}), \
                patch.object(verifier, "run_one", side_effect=run), redirect_stdout(output):
            result = verifier.run_verification(self.args(), ["B::Good", "A::First", "B::Bad", "A::Second"])
        self.assertEqual(calls, ["Satisfiability", "A::First", "A::Second", "B::Good", "B::Bad"])
        self.assertEqual(result["counts"], {"SAT": 3, "UNSAT": 1})
        self.assertIn("Behavioral Consistency - Inv", output.getvalue())
        self.assertIn("Behavioral Consistency - Post", output.getvalue())
        self.assertNotIn("UNSAT: B::Good", output.getvalue())


if __name__ == "__main__":
    unittest.main()
