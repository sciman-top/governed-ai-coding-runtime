import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class EvalTraceTests(unittest.TestCase):
    def test_eval_trace_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.eval_trace")
        except ModuleNotFoundError as exc:
            self.fail(f"eval_trace module is not implemented: {exc}")
        if not hasattr(module, "record_eval_baseline"):
            self.fail("record_eval_baseline is not implemented")

    def test_required_eval_suites_are_recorded_from_repo_profile(self) -> None:
        eval_trace = importlib.import_module("governed_ai_coding_runtime_contracts.eval_trace")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )

        baseline = eval_trace.record_eval_baseline(profile)

        self.assertEqual(baseline.required_suites, ["python-service-smoke", "api-regression"])

    def test_required_trace_fields_are_emitted(self) -> None:
        eval_trace = importlib.import_module("governed_ai_coding_runtime_contracts.eval_trace")

        trace = eval_trace.emit_trace_record(
            task_id="GAP-014",
            evidence_link="docs/change-evidence/example.md",
            validation_status="partially_validated",
            outcome_quality="pass",
        )

        self.assertEqual(trace.task_id, "GAP-014")
        self.assertEqual(trace.evidence_link, "docs/change-evidence/example.md")
        self.assertEqual(trace.validation_status, "partially_validated")
        self.assertEqual(trace.outcome_quality, "pass")

    def test_trace_grading_distinguishes_missing_evidence_from_poor_outcome(self) -> None:
        eval_trace = importlib.import_module("governed_ai_coding_runtime_contracts.eval_trace")
        missing_evidence = eval_trace.emit_trace_record("task-1", "", "partially_validated", "pass")
        poor_quality = eval_trace.emit_trace_record(
            "task-2",
            "docs/change-evidence/example.md",
            "fully_validated",
            "fail",
        )

        self.assertEqual(eval_trace.grade_trace(missing_evidence).grade, "missing_evidence")
        self.assertEqual(eval_trace.grade_trace(poor_quality).grade, "poor_outcome_quality")


if __name__ == "__main__":
    unittest.main()
