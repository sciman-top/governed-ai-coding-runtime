import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class DeliveryHandoffTests(unittest.TestCase):
    def test_delivery_handoff_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.delivery_handoff")
        except ModuleNotFoundError as exc:
            self.fail(f"delivery_handoff module is not implemented: {exc}")
        if not hasattr(module, "build_handoff_package"):
            self.fail("build_handoff_package is not implemented")

    def test_handoff_package_is_generated_per_completed_task(self) -> None:
        delivery_handoff = importlib.import_module("governed_ai_coding_runtime_contracts.delivery_handoff")
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")
        plan = verification_runner.build_verification_plan("quick")
        artifact = verification_runner.build_verification_artifact(
            plan,
            "docs/change-evidence/example.md",
            {"test": "pass", "contract": "pass"},
        )

        package = delivery_handoff.build_handoff_package(
            task_id="GAP-013",
            changed_files=["packages/contracts/src/governed_ai_coding_runtime_contracts/delivery_handoff.py"],
            verification_artifact=artifact,
            risk_notes=["contract-only implementation"],
            replay_references=["python -m unittest tests.runtime.test_delivery_handoff -v"],
        )

        self.assertEqual(package.task_id, "GAP-013")
        self.assertIn("delivery_handoff.py", package.changed_files[0])

    def test_handoff_distinguishes_fully_and_partially_validated(self) -> None:
        delivery_handoff = importlib.import_module("governed_ai_coding_runtime_contracts.delivery_handoff")
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")
        quick_plan = verification_runner.build_verification_plan("quick")
        full_plan = verification_runner.build_verification_plan("full")

        full_package = delivery_handoff.build_handoff_package(
            "task-full",
            ["README.md"],
            verification_runner.build_verification_artifact(
                full_plan,
                "docs/change-evidence/full.md",
                {"build": "pass", "test": "pass", "contract": "pass", "doctor": "pass"},
            ),
            [],
            ["pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All"],
        )
        partial_package = delivery_handoff.build_handoff_package(
            "task-partial",
            ["README.md"],
            verification_runner.build_verification_artifact(
                quick_plan,
                "docs/change-evidence/partial.md",
                {"test": "pass", "contract": "pass"},
            ),
            ["build gate not applicable"],
            ["pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime"],
        )

        self.assertEqual(full_package.validation_status, "fully_validated")
        self.assertEqual(partial_package.validation_status, "partially_validated")

    def test_failed_or_interrupted_handoff_requires_replay_reference(self) -> None:
        delivery_handoff = importlib.import_module("governed_ai_coding_runtime_contracts.delivery_handoff")
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")
        plan = verification_runner.build_verification_plan("quick")
        artifact = verification_runner.build_verification_artifact(
            plan,
            "docs/change-evidence/failed.md",
            {"test": "fail", "contract": "not_run"},
        )

        with self.assertRaises(ValueError):
            delivery_handoff.build_handoff_package("task-failed", ["README.md"], artifact, ["test failed"], [])


if __name__ == "__main__":
    unittest.main()
