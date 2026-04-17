import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class WorkspaceAllocationTests(unittest.TestCase):
    def test_workspace_allocator_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.workspace")
        except ModuleNotFoundError as exc:
            self.fail(f"workspace module is not implemented: {exc}")
        if not hasattr(module, "allocate_workspace"):
            self.fail("allocate_workspace is not implemented")

    def test_workspace_allocation_is_tied_to_task_and_repo_profile(self) -> None:
        workspace = importlib.import_module("governed_ai_coding_runtime_contracts.workspace")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )

        allocation = workspace.allocate_workspace("task-123", profile)

        self.assertEqual(allocation.task_id, "task-123")
        self.assertEqual(allocation.repo_id, "python-service-sample")
        self.assertIn("task-123", allocation.workspace_root)
        self.assertEqual(allocation.path_policies["write_allow"][0], "src/**")

    def test_workspace_rejects_arbitrary_live_directory(self) -> None:
        workspace = importlib.import_module("governed_ai_coding_runtime_contracts.workspace")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )

        with self.assertRaises(ValueError):
            workspace.allocate_workspace("task-123", profile, workspace_root="D:/OneDrive/CODE/live-repo")

    def test_write_path_policy_comes_from_profile(self) -> None:
        workspace = importlib.import_module("governed_ai_coding_runtime_contracts.workspace")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )
        allocation = workspace.allocate_workspace("task-123", profile)

        self.assertTrue(workspace.validate_write_path(allocation, "src/service.py"))
        with self.assertRaises(ValueError):
            workspace.validate_write_path(allocation, "secrets/prod.env")


if __name__ == "__main__":
    unittest.main()
