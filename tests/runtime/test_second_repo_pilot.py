import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class SecondRepoPilotTests(unittest.TestCase):
    def test_second_repo_pilot_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.second_repo_pilot")
        except ModuleNotFoundError as exc:
            self.fail(f"second_repo_pilot module is not implemented: {exc}")
        if not hasattr(module, "run_second_repo_reuse_pilot"):
            self.fail("run_second_repo_reuse_pilot is not implemented")

    def test_second_repo_uses_same_kernel_semantics(self) -> None:
        second_repo_pilot = importlib.import_module("governed_ai_coding_runtime_contracts.second_repo_pilot")

        result = second_repo_pilot.run_second_repo_reuse_pilot(
            primary_profile_path=ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json",
            second_profile_path=ROOT / "schemas" / "examples" / "repo-profile" / "typescript-webapp.example.json",
        )

        self.assertEqual(result.second_repo_id, "typescript-webapp-sample")
        self.assertTrue(result.same_kernel_semantics)
        self.assertFalse(result.kernel_fork_required)

    def test_only_repo_profile_values_differ(self) -> None:
        second_repo_pilot = importlib.import_module("governed_ai_coding_runtime_contracts.second_repo_pilot")

        result = second_repo_pilot.run_second_repo_reuse_pilot(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json",
            ROOT / "schemas" / "examples" / "repo-profile" / "typescript-webapp.example.json",
        )

        self.assertIn("primary_language", result.profile_differences)
        self.assertIn("build_commands", result.profile_differences)
        self.assertNotIn("task_lifecycle", result.profile_differences)

    def test_additional_agent_product_shape_is_represented_as_adapter_gap(self) -> None:
        second_repo_pilot = importlib.import_module("governed_ai_coding_runtime_contracts.second_repo_pilot")

        adapter = second_repo_pilot.generic_process_adapter_declaration()
        result = second_repo_pilot.classify_adapter_compatibility(adapter)

        self.assertEqual(adapter["invocation_mode"], "non_interactive_cli")
        self.assertEqual(result.adapter_id, "generic.process.cli")
        self.assertEqual(result.compatibility_status, "compatible_with_gaps")
        self.assertIn("logs_only_event_visibility", result.gaps)


if __name__ == "__main__":
    unittest.main()
