import sys
import tempfile
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class AttachedWriteExecutionTests(unittest.TestCase):
    def test_api_exists(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_execution")
        if not hasattr(module, "execute_attached_write_request"):
            self.fail("execute_attached_write_request is not implemented")
        if not hasattr(module, "decide_attached_write_request"):
            self.fail("decide_attached_write_request is not implemented")

    def test_low_tier_write_executes_without_approval(self) -> None:
        governance_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_governance")
        execution_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_execution")
        target_repo, runtime_state_root = self._attached_target()
        target_file = target_repo / "src" / "main.py"
        target_file.parent.mkdir(parents=True, exist_ok=True)

        governance = governance_module.govern_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-exec-low",
            tool_name="write_file",
            target_path="src/main.py",
            tier="low",
            rollback_reference="git diff -- src/main.py",
        )
        self.assertEqual(governance.policy_decision.status, "allow")

        result = execution_module.execute_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-exec-low",
            tool_name="write_file",
            target_path="src/main.py",
            tier="low",
            rollback_reference="git diff -- src/main.py",
            content="print('hello')\n",
        )

        self.assertEqual(result.execution_status, "executed")
        self.assertEqual(result.policy_decision.status, "allow")
        self.assertEqual(target_file.read_text(encoding="utf-8"), "print('hello')\n")

    def test_medium_tier_requires_approval_then_executes(self) -> None:
        governance_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_governance")
        execution_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_execution")
        target_repo, runtime_state_root = self._attached_target()
        target_file = target_repo / "src" / "main.py"
        target_file.parent.mkdir(parents=True, exist_ok=True)

        governance = governance_module.govern_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-exec-medium",
            tool_name="write_file",
            target_path="src/main.py",
            tier="medium",
            rollback_reference="git diff -- src/main.py",
        )
        self.assertEqual(governance.policy_decision.status, "escalate")
        self.assertIsNotNone(governance.approval_id)

        blocked = execution_module.execute_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-exec-medium",
            tool_name="write_file",
            target_path="src/main.py",
            tier="medium",
            rollback_reference="git diff -- src/main.py",
            content="print('blocked')\n",
        )
        self.assertEqual(blocked.execution_status, "blocked")

        approval = execution_module.decide_attached_write_request(
            attachment_runtime_state_root=runtime_state_root,
            approval_id=governance.approval_id,
            decision="approve",
            decided_by="operator",
        )
        self.assertEqual(approval.status, "approved")

        executed = execution_module.execute_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-exec-medium",
            tool_name="write_file",
            target_path="src/main.py",
            tier="medium",
            rollback_reference="git diff -- src/main.py",
            content="print('approved')\n",
            approval_id=governance.approval_id,
        )
        self.assertEqual(executed.execution_status, "executed")
        self.assertEqual(target_file.read_text(encoding="utf-8"), "print('approved')\n")

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

