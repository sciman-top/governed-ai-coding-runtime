import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class ControlRegistryTests(unittest.TestCase):
    def test_control_registry_api_exists(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.control_registry")
        if not hasattr(module, "evaluate_control_health"):
            self.fail("evaluate_control_health is not implemented")

    def test_hard_control_without_observability_is_not_enforceable(self) -> None:
        control_registry = importlib.import_module("governed_ai_coding_runtime_contracts.control_registry")

        result = control_registry.evaluate_control_health(
            {
                "control_id": "verification.build",
                "class": "hard",
                "mode": "enforce",
                "status": "active",
                "rollback_ref": "docs/runbooks/control-rollback.md",
                "observability_signals": [],
            }
        )

        self.assertFalse(result.healthy_for_enforced_mode)
        self.assertIn("missing_observability_signals", result.gaps)

    def test_progressive_control_requires_review_and_rollback_visibility(self) -> None:
        control_registry = importlib.import_module("governed_ai_coding_runtime_contracts.control_registry")

        result = control_registry.evaluate_control_health(
            {
                "control_id": "clarification.protocol",
                "class": "progressive",
                "mode": "observe",
                "status": "active",
                "rollback_ref": "",
                "observability_signals": ["evidence.completeness"],
                "last_reviewed_at": "",
                "next_review_at": "",
            }
        )

        self.assertFalse(result.healthy_for_enforced_mode)
        self.assertIn("missing_rollback_visibility", result.gaps)
        self.assertIn("missing_review_schedule", result.gaps)


if __name__ == "__main__":
    unittest.main()
