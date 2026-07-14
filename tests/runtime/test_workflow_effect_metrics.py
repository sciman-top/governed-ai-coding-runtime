import importlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class WorkflowEffectMetricsTests(unittest.TestCase):
    def test_effect_metrics_preserve_declared_fields(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.workflow_effect_metrics")

        payload = module.build_workflow_effect_metrics(
            workflow_mode_selected="spec_plus_review",
            workflow_mode_source="repo_profile_policy",
            workflow_degrade_reason="host_missing_worktree_capability",
            recommendation_improved=True,
            mode_level_comparison_reason="medium risk multi-file change",
            manual_intervention_count=1,
            problem_run_rate=0.25,
        )

        self.assertEqual(
            payload,
            {
                "workflow_mode_selected": "spec_plus_review",
                "workflow_mode_source": "repo_profile_policy",
                "workflow_degrade_reason": "host_missing_worktree_capability",
                "recommendation_improved": True,
                "mode_level_comparison_reason": "medium risk multi-file change",
                "manual_intervention_count": 1,
                "problem_run_rate": 0.25,
            },
        )


if __name__ == "__main__":
    unittest.main()
