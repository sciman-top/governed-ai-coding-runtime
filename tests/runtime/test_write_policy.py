import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class WritePolicyTests(unittest.TestCase):
    def test_write_policy_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.write_policy")
        except ModuleNotFoundError as exc:
            self.fail(f"write_policy module is not implemented: {exc}")
        if not hasattr(module, "resolve_write_policy"):
            self.fail("resolve_write_policy is not implemented")

    def test_medium_tier_requires_approval_by_default(self) -> None:
        write_policy = importlib.import_module("governed_ai_coding_runtime_contracts.write_policy")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )

        policy = write_policy.resolve_write_policy(profile)

        self.assertEqual(policy.default_write_tier, "medium")
        self.assertTrue(policy.requires_approval("medium"))

    def test_high_tier_always_requires_explicit_approval(self) -> None:
        write_policy = importlib.import_module("governed_ai_coding_runtime_contracts.write_policy")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )

        policy = write_policy.resolve_write_policy(profile)

        self.assertTrue(policy.requires_approval("high"))
        self.assertEqual(policy.approval_mode("high"), "explicit")

    def test_low_tier_can_run_without_approval(self) -> None:
        write_policy = importlib.import_module("governed_ai_coding_runtime_contracts.write_policy")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        profile = repo_profile.load_repo_profile(
            ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
        )

        policy = write_policy.resolve_write_policy(profile)

        self.assertFalse(policy.requires_approval("low"))
        self.assertEqual(policy.approval_mode("low"), "auto")


if __name__ == "__main__":
    unittest.main()
