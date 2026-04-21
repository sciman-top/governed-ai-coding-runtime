import sys
import tempfile
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class AttachedWriteGovernanceTests(unittest.TestCase):
    def test_api_exists(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_governance")
        if not hasattr(module, "govern_attached_write_request"):
            self.fail("govern_attached_write_request is not implemented")

    def test_low_tier_allowed_for_write_allow_path(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_governance")
        target_repo, runtime_state_root = self._attached_target()

        result = module.govern_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-low",
            tool_name="apply_patch",
            target_path="src/main.py",
            tier="low",
            rollback_reference="git diff -- src/main.py",
        )

        self.assertEqual(result.governance_status, "allowed")
        self.assertEqual(result.policy_decision.status, "allow")
        self.assertIsNone(result.approval_id)

    def test_medium_tier_escalates_to_approval(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_governance")
        target_repo, runtime_state_root = self._attached_target()

        result = module.govern_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-medium",
            tool_name="apply_patch",
            target_path="src/main.py",
            tier="medium",
            rollback_reference="git diff -- src/main.py",
        )

        self.assertEqual(result.governance_status, "paused")
        self.assertEqual(result.policy_decision.status, "escalate")
        self.assertIsNotNone(result.approval_id)
        self.assertEqual(result.task_state, "approval_pending")

    def test_blocked_path_returns_deny_policy_decision(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_governance")
        target_repo, runtime_state_root = self._attached_target()

        result = module.govern_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-deny",
            tool_name="apply_patch",
            target_path="secrets/prod.env",
            tier="low",
            rollback_reference="git diff -- secrets/prod.env",
        )

        self.assertEqual(result.governance_status, "denied")
        self.assertEqual(result.policy_decision.status, "deny")
        self.assertIn("outside allowed scopes", result.reason or "")
        self.assertTrue(result.preflight_blocked)
        self.assertTrue(result.remediation_hint)
        self.assertEqual(result.allowed_write_scopes, ("src/**", "tests/**", "docs/**"))
        self.assertTrue(result.suggested_target_path)

    def _attached_target(self) -> tuple[Path, Path]:
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        workspace = Path(tmp_dir.name)
        target_repo = workspace / "target"
        target_repo.mkdir()
        runtime_state_root = workspace / "runtime-state" / "target"
        repo_attachment.attach_target_repo(
            target_repo_root=str(target_repo),
            runtime_state_root=str(runtime_state_root),
            repo_id="target",
            display_name="Target",
            primary_language="python",
            build_command="cmd /c exit 0",
            test_command="cmd /c exit 0",
            contract_command="cmd /c exit 0",
            adapter_preference="process_bridge",
        )
        return target_repo, runtime_state_root


if __name__ == "__main__":
    unittest.main()
