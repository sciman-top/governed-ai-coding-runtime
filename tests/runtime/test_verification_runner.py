import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class VerificationRunnerTests(unittest.TestCase):
    def test_verification_runner_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")
        except ModuleNotFoundError as exc:
            self.fail(f"verification_runner module is not implemented: {exc}")
        if not hasattr(module, "build_verification_plan"):
            self.fail("build_verification_plan is not implemented")

    def test_full_plan_enforces_canonical_gate_order(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        plan = verification_runner.build_verification_plan("full")

        self.assertEqual([gate.gate_id for gate in plan.gates], ["build", "test", "contract", "doctor"])
        self.assertEqual([gate.canonical_name for gate in plan.gates], ["build", "test", "contract_or_invariant", "hotspot_or_health_check"])

    def test_quick_plan_keeps_test_before_contract(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        plan = verification_runner.build_verification_plan("quick")

        self.assertEqual([gate.gate_id for gate in plan.gates], ["test", "contract"])

    def test_escalation_conditions_are_explicit(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        plan = verification_runner.build_verification_plan("quick")

        self.assertIn("quick_failure_requires_full_or_root_cause", plan.escalation_conditions)
        self.assertIn("contract_failure_blocks_delivery", plan.escalation_conditions)

    def test_verification_output_attaches_to_evidence(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")
        plan = verification_runner.build_verification_plan("full")

        artifact = verification_runner.build_verification_artifact(
            plan=plan,
            evidence_link="docs/change-evidence/example.md",
            results={"build": "pass", "test": "pass", "contract": "pass", "doctor": "pass"},
        )

        self.assertEqual(artifact.evidence_link, "docs/change-evidence/example.md")
        self.assertEqual(artifact.results["test"], "pass")
        self.assertEqual(artifact.gate_order, ["build", "test", "contract", "doctor"])


if __name__ == "__main__":
    unittest.main()
