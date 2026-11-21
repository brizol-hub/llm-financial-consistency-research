import unittest

from experiment import (
    TEST_CASES, STYLES, annualized_return, bond_price, compound_value,
    loan_payment, realized_gain, check_answer, make_report, read_answer,
)


class CalculationsTest(unittest.TestCase):
    def test_reference_calculations(self):
        self.assertAlmostEqual(compound_value(100, .1, 1, 1), 110)
        self.assertAlmostEqual(loan_payment(1200, .12, 1), 106.618546, places=5)
        self.assertAlmostEqual(realized_gain(10, 5, 7, 2), 18)
        self.assertAlmostEqual(annualized_return(100, 121, 2), 10)
        self.assertAlmostEqual(bond_price(1000, .04, .04, 10), 1000)

    def test_every_case_has_all_wordings(self):
        for case in TEST_CASES:
            self.assertEqual(set(case["phrasings"]), set(STYLES))
            self.assertGreater(abs(case["golden"] - case["hint_value"]), case["tolerance"])


class ReconciliationTest(unittest.TestCase):
    def setUp(self):
        self.case = TEST_CASES[0]

    def test_parser(self):
        self.assertEqual(read_answer("work\nFINAL: 12.25"), 12.25)
        self.assertEqual(read_answer("FINAL: 1\nFINAL: 2"), 2)
        self.assertIsNone(read_answer("The answer is $12.25"))
        self.assertIsNone(read_answer("FINAL: 12 extra words"))

    def test_status(self):
        self.assertEqual(check_answer(self.case["golden"], self.case, "direct"), "MATCH")
        self.assertEqual(check_answer(self.case["hint_value"], self.case, "misleading"), "ANCHORED")
        self.assertEqual(check_answer(self.case["hint_value"], self.case, "direct"), "BREAK")
        self.assertEqual(check_answer(None, self.case, "direct"), "NO_ANSWER")

    def test_original_function_names(self):
        from experiment import extract_number, classify
        self.assertEqual(extract_number("FINAL: 150.25"), 150.25)
        self.assertEqual(classify(self.case["hint_value"], self.case, "misleading"), "ANCHORED")

    def test_two_simulated_models(self):
        from experiment import pretend_answer, read_answer
        a = read_answer(pretend_answer(self.case, "misleading", 1, "dry-run-model"))
        b = read_answer(pretend_answer(self.case, "misleading", 1, "dry-run-misleading-model"))
        self.assertNotEqual(a, b)

    def test_report_labels_simulation(self):
        report = make_report([], ["SIMULATED"], 1, True)
        self.assertIn("SIMULATED", report)
        self.assertIn("Accuracy by model and phrasing", report)
        self.assertIn("Every non-matching answer", report)

# End-to-end checks: exercise the command-line workflow without making network requests.
class WorkflowTest(unittest.TestCase):
    def test_original_case_values_and_questions_unchanged(self):
        # A snapshot of the numerical inputs and question text is checked separately
        # during the original-versus-revised audit.
        self.assertEqual(len(TEST_CASES), 5)
        self.assertEqual(sum(len(c["phrasings"]) for c in TEST_CASES), 25)
        self.assertEqual([round(c["golden"], 2) for c in TEST_CASES],
                         [16470.09, 1896.20, 3917.60, 7.32, 885.80])

    def test_full_dry_run_creates_all_reports(self):
        import contextlib
        import csv
        import io
        import tempfile
        from pathlib import Path
        from experiment import main

        with tempfile.TemporaryDirectory() as folder:
            terminal = io.StringIO()
            with contextlib.redirect_stdout(terminal):
                self.assertEqual(main(["--dry-run", "--runs", "3", "--output", folder]), 0)
            files = {p.name for p in Path(folder).iterdir()}
            self.assertEqual(files, {"results.csv", "results.md", "summary.txt"})
            with (Path(folder) / "results.csv").open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 150)
            self.assertEqual(len({(r["model"], r["case"], r["style"], r["run"]) for r in rows}), 150)
            self.assertTrue(all(r["question"] and r["raw_response"] for r in rows))
            self.assertTrue(all(r["simulated"] == "True" for r in rows))
            report = (Path(folder) / "results.md").read_text(encoding="utf-8")
            self.assertEqual(report, (Path(folder) / "summary.txt").read_text(encoding="utf-8"))
            for heading in ("Accuracy by model and phrasing", "Failure types", "Consistency by calculation", "Every non-matching answer", "API errors"):
                self.assertIn(heading, report)
            self.assertIn("SIMULATED DATA", report)
            self.assertIn("SIMULATED DATA", terminal.getvalue())

    def test_mocked_live_run_and_error_handling(self):
        import contextlib
        import csv
        import io
        import sys
        import tempfile
        import types
        from pathlib import Path
        from unittest.mock import patch
        from experiment import main

        calls = []
        class FakeMessages:
            def create(self, **kwargs):
                calls.append(kwargs)
                if len(calls) == 2:
                    raise RuntimeError("simulated service failure")
                return types.SimpleNamespace(content=[types.SimpleNamespace(type="text", text="work\nFINAL: 100")])
        class FakeClient:
            def __init__(self):
                self.messages = FakeMessages()
        fake = types.SimpleNamespace(Anthropic=FakeClient)
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, {"anthropic": fake}):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--models", "test-model", "--runs", "1", "--output", folder]), 0)
            with (Path(folder) / "results.csv").open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(calls), 25)
            self.assertEqual(len(rows), 25)
            self.assertEqual(sum(r["status"] == "ERROR" for r in rows), 1)
            self.assertTrue(all(r["simulated"] == "False" for r in rows))
            self.assertTrue(any(r["error"] == "simulated service failure" for r in rows))
            self.assertIn("API errors", (Path(folder) / "results.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
