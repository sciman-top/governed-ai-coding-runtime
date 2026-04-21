import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class InteractionGovernanceTests(unittest.TestCase):
    def test_interaction_governance_api_exists(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.interaction_governance")
        for name in (
            "InteractionSignal",
            "ResponsePolicy",
            "TeachingBudget",
            "build_interaction_signal",
            "build_response_policy",
            "build_teaching_budget",
            "build_task_created_policy",
            "derive_response_policy",
        ):
            if not hasattr(module, name):
                self.fail(f"{name} is not implemented")

    def test_invalid_signal_kind_fails_closed(self) -> None:
        interaction = importlib.import_module("governed_ai_coding_runtime_contracts.interaction_governance")

        with self.assertRaises(ValueError):
            interaction.build_interaction_signal(
                signal_id="sig-001",
                task_id="task-001",
                signal_kind="unknown-signal",
                severity="medium",
                confidence=0.7,
                source="user_input",
                summary="unknown",
                evidence_refs=["evidence://task-001/input"],
                recorded_at="2026-04-22T08:00:00Z",
            )

    def test_invalid_budget_status_fails_closed(self) -> None:
        interaction = importlib.import_module("governed_ai_coding_runtime_contracts.interaction_governance")

        with self.assertRaises(ValueError):
            interaction.build_teaching_budget(
                task_id="task-001",
                total_token_budget=1000,
                execution_budget=500,
                clarification_budget=200,
                explanation_budget=200,
                compaction_budget=100,
                used_execution_tokens=0,
                used_clarification_tokens=0,
                used_explanation_tokens=0,
                used_compaction_tokens=0,
                soft_thresholds={"warning_tokens": 700},
                hard_thresholds={"stop_tokens": 1000},
                budget_status="broken",
            )

    def test_task_created_policy_is_guided_and_requires_restatement(self) -> None:
        interaction = importlib.import_module("governed_ai_coding_runtime_contracts.interaction_governance")

        policy = interaction.build_task_created_policy(task_id="task-001")

        self.assertEqual(policy.mode, "guided")
        self.assertTrue(policy.restatement_required)
        self.assertEqual(policy.posture, "aligned")
        self.assertEqual(policy.max_questions, 0)

    def test_repeated_failure_integrates_with_clarification_policy(self) -> None:
        interaction = importlib.import_module("governed_ai_coding_runtime_contracts.interaction_governance")
        clarification = importlib.import_module("governed_ai_coding_runtime_contracts.clarification")

        signal = interaction.build_interaction_signal(
            signal_id="sig-repeat-001",
            task_id="task-001",
            signal_kind="repeated_failure",
            severity="high",
            confidence=0.9,
            source="verification_result",
            summary="same issue failed twice",
            evidence_refs=["evidence://task-001/fail-1", "evidence://task-001/fail-2"],
            recorded_at="2026-04-22T08:00:00Z",
        )

        policy = interaction.derive_response_policy(
            task_id="task-001",
            signals=[signal],
            clarification_policy=clarification.ClarificationPolicy(trigger_threshold=2, question_cap=3),
            attempt_count=2,
            clarification_current_mode="direct_fix",
            clarification_scenario="bugfix",
        )

        self.assertEqual(policy.posture, "clarifying")
        self.assertEqual(policy.clarification_mode, "required")
        self.assertEqual(policy.max_questions, 3)
        self.assertTrue(policy.restatement_required)

    def test_observation_gap_switches_to_checklist_first_guidance(self) -> None:
        interaction = importlib.import_module("governed_ai_coding_runtime_contracts.interaction_governance")

        signal = interaction.build_interaction_signal(
            signal_id="sig-gap-001",
            task_id="task-001",
            signal_kind="observation_gap",
            severity="medium",
            confidence=0.95,
            source="user_input",
            summary="missing logs and repro",
            evidence_refs=["evidence://task-001/intake"],
            recorded_at="2026-04-22T08:00:00Z",
        )

        policy = interaction.derive_response_policy(task_id="task-001", signals=[signal])

        self.assertEqual(policy.posture, "guiding")
        self.assertEqual(policy.stop_or_escalate, "switch_to_checklist")
        self.assertEqual(policy.max_observation_items, 4)
        self.assertEqual(policy.checklist_kind, "bugfix-observation")

    def test_term_confusion_enters_teaching_mode(self) -> None:
        interaction = importlib.import_module("governed_ai_coding_runtime_contracts.interaction_governance")

        signal = interaction.build_interaction_signal(
            signal_id="sig-term-001",
            task_id="task-001",
            signal_kind="term_confusion",
            severity="medium",
            confidence=0.8,
            source="user_input",
            summary="user keeps mixing symptom and root cause",
            evidence_refs=["evidence://task-001/chat-3"],
            recorded_at="2026-04-22T08:00:00Z",
        )

        policy = interaction.derive_response_policy(task_id="task-001", signals=[signal])

        self.assertEqual(policy.mode, "teaching")
        self.assertEqual(policy.teaching_level, "term_only")
        self.assertEqual(policy.posture, "teaching")
        self.assertEqual(policy.term_explain_limit, 1)

    def test_budget_pressure_can_stop_on_budget(self) -> None:
        interaction = importlib.import_module("governed_ai_coding_runtime_contracts.interaction_governance")

        signal = interaction.build_interaction_signal(
            signal_id="sig-budget-001",
            task_id="task-001",
            signal_kind="budget_pressure",
            severity="high",
            confidence=1.0,
            source="runtime_event",
            summary="interaction budget exhausted",
            evidence_refs=["evidence://task-001/budget"],
            recorded_at="2026-04-22T08:00:00Z",
        )
        budget = interaction.build_teaching_budget(
            task_id="task-001",
            total_token_budget=1000,
            execution_budget=400,
            clarification_budget=200,
            explanation_budget=200,
            compaction_budget=200,
            used_execution_tokens=400,
            used_clarification_tokens=200,
            used_explanation_tokens=200,
            used_compaction_tokens=200,
            soft_thresholds={"warning_tokens": 700},
            hard_thresholds={"stop_tokens": 1000},
            budget_status="exhausted",
        )

        policy = interaction.derive_response_policy(task_id="task-001", signals=[signal], budget=budget)

        self.assertEqual(policy.posture, "stopped_on_budget")
        self.assertEqual(policy.stop_or_escalate, "stop_on_budget")
        self.assertEqual(policy.compression_mode, "ref_only")

    def test_exports_from_package_root(self) -> None:
        package = importlib.import_module("governed_ai_coding_runtime_contracts")
        for name in (
            "InteractionSignal",
            "ResponsePolicy",
            "TeachingBudget",
            "build_interaction_signal",
            "build_response_policy",
            "build_teaching_budget",
            "build_task_created_policy",
            "derive_response_policy",
        ):
            if not hasattr(package, name):
                self.fail(f"{name} is not exported from package root")


if __name__ == "__main__":
    unittest.main()

