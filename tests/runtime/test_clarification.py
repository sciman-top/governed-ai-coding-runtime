import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class ClarificationPolicyTests(unittest.TestCase):
    def test_clarification_policy_api_exists(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.clarification")
        if not hasattr(module, "ClarificationPolicy"):
            self.fail("ClarificationPolicy is not implemented")
        if not hasattr(module, "evaluate_clarification"):
            self.fail("evaluate_clarification is not implemented")

    def test_repeated_failures_trigger_clarification_mode(self) -> None:
        clarification = importlib.import_module("governed_ai_coding_runtime_contracts.clarification")

        decision = clarification.evaluate_clarification(
            clarification.ClarificationPolicy(trigger_threshold=2, question_cap=3),
            issue_id="gap-020",
            attempt_count=2,
            current_mode="direct_fix",
            scenario="bugfix",
        )

        self.assertTrue(decision.clarification_required)
        self.assertEqual(decision.next_mode, "clarify_required")
        self.assertEqual(decision.question_cap, 3)
        self.assertIn("issue_id", decision.required_evidence_fields)
        self.assertIn("clarification_questions", decision.required_evidence_fields)

    def test_low_attempt_count_stays_in_direct_fix(self) -> None:
        clarification = importlib.import_module("governed_ai_coding_runtime_contracts.clarification")

        decision = clarification.evaluate_clarification(
            clarification.ClarificationPolicy(trigger_threshold=2, question_cap=3),
            issue_id="gap-020",
            attempt_count=1,
            current_mode="direct_fix",
            scenario="plan",
        )

        self.assertFalse(decision.clarification_required)
        self.assertEqual(decision.next_mode, "direct_fix")

    def test_confirmation_resets_attempt_counter_and_mode(self) -> None:
        clarification = importlib.import_module("governed_ai_coding_runtime_contracts.clarification")

        state = clarification.reset_clarification_state(
            issue_id="gap-020",
            clarified=True,
        )

        self.assertEqual(state.issue_id, "gap-020")
        self.assertEqual(state.attempt_count, 0)
        self.assertEqual(state.mode, "direct_fix")


if __name__ == "__main__":
    unittest.main()
