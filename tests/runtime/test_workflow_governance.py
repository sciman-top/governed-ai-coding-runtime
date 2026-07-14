import importlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class WorkflowGovernanceTests(unittest.TestCase):
    def test_supported_modes_remain_allowlisted(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.workflow_governance")

        for mode in {
            "direct_fix",
            "spec_first",
            "spec_plus_review",
            "worktree_isolated_execution",
            "parallel_subagent_assist",
            "maintenance_automation",
        }:
            with self.subTest(mode=mode):
                self.assertEqual(module.ensure_supported_workflow_mode(mode), mode)

    def test_unsupported_mode_fails_closed(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.workflow_governance")

        with self.assertRaisesRegex(ValueError, "unsupported workflow mode"):
            module.ensure_supported_workflow_mode("freeform_agent_loop")


if __name__ == "__main__":
    unittest.main()
