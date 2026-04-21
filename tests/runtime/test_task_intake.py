import sys
import unittest
from pathlib import Path
import importlib
from dataclasses import asdict

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class TaskIntakeContractTests(unittest.TestCase):
    def test_task_intake_api_exists(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        if not hasattr(module, "TaskIntake"):
            self.fail("TaskIntake is not implemented")

    def test_transition_validator_api_exists(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        if not hasattr(module, "validate_transition"):
            self.fail("validate_transition is not implemented")

    def test_task_intake_requires_goal_scope_acceptance_repo_and_budgets(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        with self.assertRaises(ValueError):
            module.TaskIntake(
                goal="",
                scope="update runtime intake validation",
                acceptance=["task object is persisted"],
                repo="governed-ai-coding-runtime",
                budgets={"max_steps": 10, "max_minutes": 30},
            )

    def test_task_intake_keeps_core_fields(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        task = module.TaskIntake(
            goal="create governed task",
            scope="phase 1 deterministic intake",
            acceptance=["goal is required", "repo is attached"],
            repo="governed-ai-coding-runtime",
            budgets={"max_steps": 10, "max_minutes": 30},
        )

        self.assertEqual(
            asdict(task),
            {
                "goal": "create governed task",
                "scope": "phase 1 deterministic intake",
                "acceptance": ["goal is required", "repo is attached"],
                "repo": "governed-ai-coding-runtime",
                "budgets": {"max_steps": 10, "max_minutes": 30},
                "interaction_defaults": None,
                "interaction_budget_overrides": None,
            },
        )

    def test_task_intake_accepts_optional_interaction_defaults_and_budget_overrides(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        task = module.TaskIntake(
            goal="create governed task",
            scope="phase 1 deterministic intake",
            acceptance=["goal is required", "repo is attached"],
            repo="governed-ai-coding-runtime",
            budgets={"max_steps": 10, "max_minutes": 30},
            interaction_defaults={
                "default_mode": "guided",
                "allow_teaching": True,
                "max_questions": 3,
            },
            interaction_budget_overrides={
                "clarification_budget": 300,
                "explanation_budget": 500,
            },
        )

        self.assertEqual(task.interaction_defaults["default_mode"], "guided")
        self.assertEqual(task.interaction_defaults["max_questions"], 3)
        self.assertEqual(task.interaction_budget_overrides["clarification_budget"], 300)

    def test_task_intake_rejects_interaction_defaults_that_override_clarification_cap(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")

        with self.assertRaises(ValueError):
            module.TaskIntake(
                goal="create governed task",
                scope="phase 1 deterministic intake",
                acceptance=["goal is required", "repo is attached"],
                repo="governed-ai-coding-runtime",
                budgets={"max_steps": 10, "max_minutes": 30},
                interaction_defaults={"default_mode": "guided", "max_questions": 4},
            )

    def test_task_intake_rejects_negative_interaction_budget_override(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")

        with self.assertRaises(ValueError):
            module.TaskIntake(
                goal="create governed task",
                scope="phase 1 deterministic intake",
                acceptance=["goal is required", "repo is attached"],
                repo="governed-ai-coding-runtime",
                budgets={"max_steps": 10, "max_minutes": 30},
                interaction_budget_overrides={"clarification_budget": -1},
            )

    def test_validate_transition_accepts_required_transition(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        self.assertTrue(module.validate_transition("created", "scoped"))

    def test_validate_transition_rejects_illegal_transition(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        with self.assertRaises(ValueError):
            module.validate_transition("created", "delivered")

    def test_validate_transition_accepts_pause_and_retry_transitions(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        self.assertTrue(module.validate_transition("executing", "paused"))
        self.assertTrue(module.validate_transition("failed", "planned"))


if __name__ == "__main__":
    unittest.main()
