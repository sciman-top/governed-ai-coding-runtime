import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class WriteToolRunnerTests(unittest.TestCase):
    def _fixtures(self):
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        workspace = importlib.import_module("governed_ai_coding_runtime_contracts.workspace")
        write_policy = importlib.import_module("governed_ai_coding_runtime_contracts.write_policy")
        approval = importlib.import_module("governed_ai_coding_runtime_contracts.approval")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )
        allocation = workspace.allocate_workspace("task-123", profile)
        policy = write_policy.resolve_write_policy(profile)
        return allocation, policy, approval.ApprovalLedger()

    def test_write_tool_runner_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.write_tool_runner")
        except ModuleNotFoundError as exc:
            self.fail(f"write_tool_runner module is not implemented: {exc}")
        if not hasattr(module, "govern_write_request"):
            self.fail("govern_write_request is not implemented")

    def test_low_tier_write_can_be_allowed_after_path_policy(self) -> None:
        write_tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.write_tool_runner")
        allocation, policy, ledger = self._fixtures()
        request = write_tool_runner.WriteToolRequest(
            task_id="task-123",
            tool_name="apply_patch",
            target_path="src/service.py",
            tier="low",
            rollback_reference="git diff -- src/service.py",
        )

        decision = write_tool_runner.govern_write_request(request, allocation, policy, ledger)

        self.assertEqual(decision.status, "allowed")
        self.assertIsNone(decision.approval_id)

    def test_approval_required_write_pauses_before_execution(self) -> None:
        write_tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.write_tool_runner")
        allocation, policy, ledger = self._fixtures()
        request = write_tool_runner.WriteToolRequest(
            task_id="task-123",
            tool_name="apply_patch",
            target_path="src/service.py",
            tier="medium",
            rollback_reference="git diff -- src/service.py",
        )

        decision = write_tool_runner.govern_write_request(request, allocation, policy, ledger)

        self.assertEqual(decision.status, "paused")
        self.assertEqual(decision.task_state, "approval_pending")
        self.assertIsNotNone(decision.approval_id)

    def test_blocked_write_path_fails_closed(self) -> None:
        write_tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.write_tool_runner")
        allocation, policy, ledger = self._fixtures()
        request = write_tool_runner.WriteToolRequest(
            task_id="task-123",
            tool_name="apply_patch",
            target_path="secrets/prod.env",
            tier="low",
            rollback_reference="git diff -- secrets/prod.env",
        )

        with self.assertRaises(ValueError):
            write_tool_runner.govern_write_request(request, allocation, policy, ledger)

    def test_risky_writes_require_rollback_reference(self) -> None:
        write_tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.write_tool_runner")
        allocation, policy, ledger = self._fixtures()
        request = write_tool_runner.WriteToolRequest(
            task_id="task-123",
            tool_name="apply_patch",
            target_path="src/service.py",
            tier="high",
            rollback_reference="",
        )

        with self.assertRaises(ValueError):
            write_tool_runner.govern_write_request(request, allocation, policy, ledger)


if __name__ == "__main__":
    unittest.main()
