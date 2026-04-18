import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class CompatibilityPolicyTests(unittest.TestCase):
    def test_compatibility_api_exists(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.compatibility")
        if not hasattr(module, "resolve_runtime_posture"):
            self.fail("resolve_runtime_posture is not implemented")

    def test_partial_support_degrades_enforced_to_advisory(self) -> None:
        compatibility = importlib.import_module("governed_ai_coding_runtime_contracts.compatibility")

        result = compatibility.resolve_runtime_posture(
            requested_posture="enforced",
            repo_supported_postures=["observe", "advisory", "enforced"],
            compatibility_signals=[
                {
                    "capability": "structured_events",
                    "status": "partial_support",
                    "degrade_to": "advisory",
                    "reason": "adapter exposes logs only",
                }
            ],
        )

        self.assertEqual(result.support_level, "partial_support")
        self.assertEqual(result.effective_posture, "advisory")
        self.assertEqual(result.degrade_reason, "adapter exposes logs only")

    def test_full_support_preserves_requested_posture(self) -> None:
        compatibility = importlib.import_module("governed_ai_coding_runtime_contracts.compatibility")

        result = compatibility.resolve_runtime_posture(
            requested_posture="advisory",
            repo_supported_postures=["observe", "advisory", "enforced"],
            compatibility_signals=[
                {
                    "capability": "workspace_write",
                    "status": "full_support",
                }
            ],
        )

        self.assertEqual(result.support_level, "full_support")
        self.assertEqual(result.effective_posture, "advisory")
        self.assertEqual(result.degrade_reason, "")

    def test_unsupported_capability_fails_closed_when_requested(self) -> None:
        compatibility = importlib.import_module("governed_ai_coding_runtime_contracts.compatibility")

        result = compatibility.resolve_runtime_posture(
            requested_posture="enforced",
            repo_supported_postures=["observe", "advisory", "enforced"],
            compatibility_signals=[
                {
                    "capability": "pre_write_hook",
                    "status": "unsupported",
                    "degrade_to": "fail_closed",
                    "reason": "no hook interception available",
                }
            ],
        )

        self.assertEqual(result.support_level, "unsupported")
        self.assertEqual(result.effective_posture, "blocked")
        self.assertEqual(result.degrade_reason, "no hook interception available")

    def test_unsupported_capability_without_explicit_degrade_fails_closed(self) -> None:
        compatibility = importlib.import_module("governed_ai_coding_runtime_contracts.compatibility")

        result = compatibility.resolve_runtime_posture(
            requested_posture="enforced",
            repo_supported_postures=["observe", "advisory", "enforced"],
            compatibility_signals=[
                {
                    "capability": "structured_events",
                    "status": "unsupported",
                    "reason": "no structured event surface",
                }
            ],
        )

        self.assertEqual(result.support_level, "unsupported")
        self.assertEqual(result.effective_posture, "blocked")
        self.assertEqual(result.degrade_reason, "no structured event surface")


if __name__ == "__main__":
    unittest.main()
