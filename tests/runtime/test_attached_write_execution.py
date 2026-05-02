import sys
import tempfile
import unittest
import os
from pathlib import Path
import importlib
import hashlib
import json

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

    def test_high_tier_fails_closed_when_approval_missing(self) -> None:
        execution_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_execution")
        target_repo, runtime_state_root = self._attached_target()
        target_file = target_repo / "src" / "main.py"
        target_file.parent.mkdir(parents=True, exist_ok=True)

        denied = execution_module.execute_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-exec-high-missing",
            tool_name="write_file",
            target_path="src/main.py",
            tier="high",
            rollback_reference="git diff -- src/main.py",
            content="print('should-not-write')\n",
        )

        self.assertEqual(denied.execution_status, "denied")
        self.assertEqual(denied.policy_decision.status, "deny")
        self.assertEqual(denied.reason, "approval_required")
        self.assertFalse(target_file.exists())

    def test_high_tier_fails_closed_when_approval_is_stale(self) -> None:
        governance_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_governance")
        execution_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_execution")
        target_repo, runtime_state_root = self._attached_target()
        target_file = target_repo / "src" / "main.py"
        target_file.parent.mkdir(parents=True, exist_ok=True)

        governance = governance_module.govern_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-exec-high-stale",
            tool_name="write_file",
            target_path="src/main.py",
            tier="high",
            rollback_reference="git diff -- src/main.py",
        )
        self.assertIsNotNone(governance.approval_id)
        approval = execution_module.decide_attached_write_request(
            attachment_runtime_state_root=runtime_state_root,
            approval_id=governance.approval_id,
            decision="approve",
            decided_by="operator",
        )
        self.assertEqual(approval.status, "approved")

        approval_path = runtime_state_root / "approvals" / f"{governance.approval_id}.json"
        raw = json.loads(approval_path.read_text(encoding="utf-8"))
        raw["decided_at"] = "2000-01-01T00:00:00+00:00"
        approval_path.write_text(json.dumps(raw, indent=2, sort_keys=True), encoding="utf-8")

        denied = execution_module.execute_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-exec-high-stale",
            tool_name="write_file",
            target_path="src/main.py",
            tier="high",
            rollback_reference="git diff -- src/main.py",
            content="print('stale')\n",
            approval_id=governance.approval_id,
        )

        self.assertEqual(denied.execution_status, "denied")
        self.assertEqual(denied.policy_decision.status, "deny")
        self.assertEqual(denied.reason, "approval_stale_or_missing")
        self.assertFalse(target_file.exists())

    def test_decide_rejects_unsafe_approval_ids(self) -> None:
        execution_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_execution")
        _target_repo, runtime_state_root = self._attached_target()

        with self.assertRaisesRegex(ValueError, "approval_id"):
            execution_module.decide_attached_write_request(
                attachment_runtime_state_root=runtime_state_root,
                approval_id="../../escape",
                decision="approve",
                decided_by="operator",
            )

    def test_write_file_denies_existing_file_without_expected_sha256(self) -> None:
        execution_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_execution")
        target_repo, runtime_state_root = self._attached_target()
        target_file = target_repo / "src" / "main.py"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text("print('target-local')\n", encoding="utf-8")

        result = execution_module.execute_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-existing-no-if-match",
            tool_name="write_file",
            target_path="src/main.py",
            tier="low",
            rollback_reference="git diff -- src/main.py",
            content="print('stale-request')\n",
        )

        self.assertEqual(result.execution_status, "denied")
        self.assertEqual(result.reason, "expected_sha256_required")
        self.assertEqual(target_file.read_text(encoding="utf-8"), "print('target-local')\n")

    def test_write_file_executes_existing_file_when_expected_sha256_matches(self) -> None:
        execution_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_execution")
        target_repo, runtime_state_root = self._attached_target()
        target_file = target_repo / "src" / "main.py"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        original = "print('target-local')\n"
        target_file.write_text(original, encoding="utf-8")
        expected_sha256 = hashlib.sha256(original.encode("utf-8")).hexdigest()

        result = execution_module.execute_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-existing-if-match",
            tool_name="write_file",
            target_path="src/main.py",
            tier="low",
            rollback_reference="git diff -- src/main.py",
            content="print('fresh-request')\n",
            expected_sha256=expected_sha256,
        )

        self.assertEqual(result.execution_status, "executed")
        self.assertEqual(target_file.read_text(encoding="utf-8"), "print('fresh-request')\n")

    def test_write_file_updates_symlink_target_without_replacing_link(self) -> None:
        execution_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_execution")
        target_repo, runtime_state_root = self._attached_target()
        source_file = target_repo / "src" / "source.txt"
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text("before\n", encoding="utf-8")
        link_path = target_repo / "src" / "linked.txt"

        try:
            os.symlink(source_file, link_path)
        except (OSError, NotImplementedError):
            self.skipTest("file symlinks are not available in this environment")

        result = execution_module.execute_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-symlink",
            tool_name="write_file",
            target_path="src/linked.txt",
            tier="low",
            rollback_reference="git diff -- src/linked.txt",
            content="after\n",
            expected_sha256=hashlib.sha256("before\n".encode("utf-8")).hexdigest(),
        )

        self.assertEqual(result.execution_status, "executed")
        self.assertTrue(link_path.is_symlink())
        self.assertEqual(source_file.read_text(encoding="utf-8"), "after\n")

    def test_write_file_denies_symlink_target_outside_attachment_root(self) -> None:
        execution_module = importlib.import_module("governed_ai_coding_runtime_contracts.attached_write_execution")
        target_repo, runtime_state_root = self._attached_target()
        external_file = target_repo.parent / "outside.txt"
        external_file.write_text("outside-before\n", encoding="utf-8")
        link_path = target_repo / "src" / "outside-link.txt"
        link_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            os.symlink(external_file, link_path)
        except (OSError, NotImplementedError):
            self.skipTest("file symlinks are not available in this environment")

        result = execution_module.execute_attached_write_request(
            attachment_root=target_repo,
            attachment_runtime_state_root=runtime_state_root,
            task_id="task-write-symlink-outside",
            tool_name="write_file",
            target_path="src/outside-link.txt",
            tier="low",
            rollback_reference="git diff -- src/outside-link.txt",
            content="outside-after\n",
        )

        self.assertEqual(result.execution_status, "denied")
        self.assertIn("outside attachment_root", result.reason or "")
        self.assertEqual(external_file.read_text(encoding="utf-8"), "outside-before\n")

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

