import sys
import unittest
from pathlib import Path
import importlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class ToolRunnerGovernanceTests(unittest.TestCase):
    def test_govern_execution_request_allows_bounded_git_status(self) -> None:
        tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.tool_runner")

        decision = tool_runner.govern_execution_request(
            tool_name="git",
            command="git status --short",
            tier="low",
            rollback_reference="git checkout -- .",
        )

        self.assertEqual(decision.status, "allow")
        self.assertFalse(decision.requires_approval)

    def test_govern_execution_request_escalates_medium_tier(self) -> None:
        tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.tool_runner")

        decision = tool_runner.govern_execution_request(
            tool_name="shell",
            command="git diff --name-only",
            tier="medium",
            rollback_reference="git checkout -- .",
        )

        self.assertEqual(decision.status, "escalate")
        self.assertTrue(decision.requires_approval)

    def test_govern_execution_request_denies_mutating_or_unbounded_commands(self) -> None:
        tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.tool_runner")

        denied_git = tool_runner.govern_execution_request(
            tool_name="git",
            command="git commit -m test",
            tier="low",
            rollback_reference="git reset --soft HEAD~1",
        )
        denied_package = tool_runner.govern_execution_request(
            tool_name="package",
            command="pip install requests",
            tier="low",
            rollback_reference="pip uninstall requests -y",
        )

        self.assertEqual(denied_git.status, "deny")
        self.assertEqual(denied_package.status, "deny")

    def test_execute_governed_command_captures_exit_code_and_output(self) -> None:
        tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.tool_runner")

        result = tool_runner.execute_governed_command(
            command=f"{sys.executable} -c \"print('tool-ok')\"",
            cwd=str(ROOT),
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("tool-ok", result.output)

    def test_tool_runner_cli_emits_structured_result(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "apps" / "tool-runner" / "main.py"),
                "--command",
                f"{sys.executable} -c \"print('tool-cli-ok')\"",
                "--cwd",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["exit_code"], 0)
        self.assertEqual(payload["command"], f"{sys.executable} -c \"print('tool-cli-ok')\"")
        self.assertIn("tool-cli-ok", payload["output"])
        self.assertFalse(payload["timed_out"])


if __name__ == "__main__":
    unittest.main()
