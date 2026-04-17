import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class ReadOnlyToolRunnerTests(unittest.TestCase):
    def test_readonly_tool_request_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.tool_runner")
        except ModuleNotFoundError as exc:
            self.fail(f"tool_runner module is not implemented: {exc}")
        if not hasattr(module, "ToolRequest"):
            self.fail("ToolRequest is not implemented")

    def test_readonly_request_allowed_for_profile_read_scope(self) -> None:
        tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.tool_runner")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )
        request = tool_runner.ToolRequest(
            tool_name="shell",
            side_effect_class="filesystem_read",
            target_path="src/service.py",
        )

        self.assertTrue(tool_runner.validate_readonly_request(request, profile))

    def test_blocked_tool_fails_closed(self) -> None:
        tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.tool_runner")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )
        request = tool_runner.ToolRequest(
            tool_name="curl",
            side_effect_class="network_read",
            target_path="src/service.py",
        )

        with self.assertRaises(ValueError):
            tool_runner.validate_readonly_request(request, profile)

    def test_write_side_effect_fails_closed(self) -> None:
        tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.tool_runner")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )
        request = tool_runner.ToolRequest(
            tool_name="shell",
            side_effect_class="filesystem_write",
            target_path="src/service.py",
        )

        with self.assertRaises(ValueError):
            tool_runner.validate_readonly_request(request, profile)

    def test_path_outside_read_scope_fails_closed(self) -> None:
        tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.tool_runner")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )
        request = tool_runner.ToolRequest(
            tool_name="shell",
            side_effect_class="filesystem_read",
            target_path="secrets/prod.env",
        )

        with self.assertRaises(ValueError):
            tool_runner.validate_readonly_request(request, profile)

    def test_bounded_readonly_session_returns_accepted_summary(self) -> None:
        tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.tool_runner")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )
        requests = [
            tool_runner.ToolRequest(
                tool_name="shell",
                side_effect_class="filesystem_read",
                target_path="src/service.py",
            )
        ]

        if not hasattr(tool_runner, "run_readonly_session"):
            self.fail("run_readonly_session is not implemented")
        summary = tool_runner.run_readonly_session(requests, profile)

        self.assertEqual(summary.repo_id, "python-service-sample")
        self.assertEqual(summary.accepted_count, 1)
        self.assertEqual(summary.tool_names, ["shell"])


if __name__ == "__main__":
    unittest.main()
