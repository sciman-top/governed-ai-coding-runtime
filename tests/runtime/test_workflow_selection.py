import importlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class WorkflowSelectionTests(unittest.TestCase):
    def test_repeated_stable_task_prefers_automation_when_supported(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.workflow_selection")

        decision = module.select_workflow_mode(
            risk_level="low",
            multi_file=False,
            unclear_requirements=False,
            needs_review=False,
            supports_worktrees=True,
            supports_subagents=True,
            supports_background_automation=True,
            repeated_stable_task=True,
        )

        self.assertEqual(decision.workflow_mode_selected, "maintenance_automation")
        self.assertEqual(decision.workflow_degrade_reason, "")

    def test_repeated_stable_task_degrades_to_direct_fix_without_automation(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.workflow_selection")

        decision = module.select_workflow_mode(
            risk_level="low",
            multi_file=False,
            unclear_requirements=False,
            needs_review=False,
            supports_worktrees=True,
            supports_subagents=True,
            supports_background_automation=False,
            repeated_stable_task=True,
        )

        self.assertEqual(decision.workflow_mode_selected, "direct_fix")
        self.assertIn("degraded from maintenance_automation", decision.workflow_degrade_reason)

    def test_high_risk_or_review_required_prefers_spec_plus_review(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.workflow_selection")

        decision = module.select_workflow_mode(
            risk_level="high",
            multi_file=False,
            unclear_requirements=False,
            needs_review=False,
            supports_worktrees=True,
            supports_subagents=True,
            supports_background_automation=False,
            repeated_stable_task=False,
        )

        self.assertEqual(decision.workflow_mode_selected, "spec_plus_review")
        self.assertEqual(decision.workflow_required_artifacts, ["spec"])

    def test_medium_risk_or_multi_file_prefers_spec_first(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.workflow_selection")

        decision = module.select_workflow_mode(
            risk_level="medium",
            multi_file=True,
            unclear_requirements=False,
            needs_review=False,
            supports_worktrees=True,
            supports_subagents=True,
            supports_background_automation=False,
            repeated_stable_task=False,
        )

        self.assertEqual(decision.workflow_mode_selected, "spec_first")
        self.assertEqual(decision.workflow_required_artifacts, ["spec"])

    def test_small_low_risk_work_defaults_to_direct_fix(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.workflow_selection")

        decision = module.select_workflow_mode(
            risk_level="low",
            multi_file=False,
            unclear_requirements=False,
            needs_review=False,
            supports_worktrees=False,
            supports_subagents=False,
            supports_background_automation=False,
            repeated_stable_task=False,
        )

        self.assertEqual(decision.workflow_mode_selected, "direct_fix")
        self.assertEqual(decision.workflow_required_artifacts, [])


if __name__ == "__main__":
    unittest.main()
