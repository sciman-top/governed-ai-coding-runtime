import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class RepoProfileContractTests(unittest.TestCase):
    def test_repo_profile_loader_api_exists(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        if not hasattr(module, "load_repo_profile"):
            self.fail("load_repo_profile is not implemented")

    def test_repo_profile_model_api_exists(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        if not hasattr(module, "RepoProfile"):
            self.fail("RepoProfile is not implemented")

    def test_load_repo_profile_reads_sample_identity_and_commands(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = module.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )

        self.assertEqual(profile.repo_id, "python-service-sample")
        self.assertEqual(profile.primary_language, "python")
        self.assertEqual(profile.rollout_posture["current_mode"], "advisory")
        self.assertEqual(profile.interaction_profile["default_mode"], "guided")
        if not hasattr(profile, "command_ids"):
            self.fail("RepoProfile.command_ids is not implemented")
        self.assertEqual(profile.command_ids("build"), ["build-wheel"])
        self.assertEqual(profile.path_policies["read_allow"][0], "src/**")

    def test_repo_profile_admission_minimums_reject_missing_read_scope(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        raw = {
            "repo_id": "bad-repo",
            "primary_language": "python",
            "rollout_posture": {"current_mode": "observe", "target_mode": "advisory"},
            "build_commands": [{"id": "build", "command": "uv build"}],
            "test_commands": [{"id": "test", "command": "uv run pytest"}],
            "contract_commands": [{"id": "contract", "command": "uv run pytest tests/contracts"}],
            "invariant_commands": [],
            "tool_allowlist": ["shell"],
            "path_policies": {"read_allow": [], "write_allow": [], "blocked": []},
        }

        if not hasattr(module.RepoProfile, "from_dict"):
            self.fail("RepoProfile.from_dict is not implemented")
        with self.assertRaises(ValueError):
            module.RepoProfile.from_dict(raw)

    def test_repo_profile_rejects_invalid_interaction_profile_defaults(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        raw = {
            "repo_id": "bad-repo",
            "primary_language": "python",
            "rollout_posture": {"current_mode": "observe", "target_mode": "advisory"},
            "build_commands": [{"id": "build", "command": "uv build"}],
            "test_commands": [{"id": "test", "command": "uv run pytest"}],
            "contract_commands": [{"id": "contract", "command": "uv run pytest tests/contracts"}],
            "invariant_commands": [],
            "tool_allowlist": ["shell"],
            "path_policies": {"read_allow": ["src/**"], "write_allow": [], "blocked": []},
            "interaction_profile": {"default_mode": "verbose"},
        }

        with self.assertRaises(ValueError):
            module.RepoProfile.from_dict(raw)


if __name__ == "__main__":
    unittest.main()
