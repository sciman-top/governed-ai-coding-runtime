import sys
import tempfile
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

    def test_verification_plan_can_bind_to_task_and_run(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        plan = verification_runner.build_verification_plan("quick", task_id="task-quick", run_id="run-quick")

        self.assertEqual(plan.task_id, "task-quick")
        self.assertEqual(plan.run_id, "run-quick")

    def test_verification_runner_persists_gate_outputs_as_artifacts(self) -> None:
        artifact_store = importlib.import_module("governed_ai_coding_runtime_contracts.artifact_store")
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = artifact_store.LocalArtifactStore(Path(tmp_dir))
            plan = verification_runner.build_verification_plan("quick", task_id="task-verify", run_id="run-verify")
            artifact = verification_runner.run_verification_plan(
                plan,
                artifact_store=store,
                execute_gate=lambda gate: (0, f"{gate.gate_id} passed"),
            )

            self.assertEqual(artifact.task_id, "task-verify")
            self.assertEqual(artifact.run_id, "run-verify")
            self.assertIn("test", artifact.result_artifact_refs)
            self.assertEqual(artifact.results["contract"], "pass")

    def test_repo_profile_verification_plan_prefers_declared_commands(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        plan = verification_runner.build_repo_profile_verification_plan(
            "full",
            task_id="task-profile",
            run_id="run-profile",
            profile_raw={
                "full_gate_commands": [
                    {"id": "build", "command": "dotnet build Repo.sln -c Debug"},
                    {"id": "test", "command": "dotnet test tests/Repo.Tests.csproj -c Debug"},
                    {"id": "contract", "command": "dotnet test tests/Repo.Tests.csproj -c Debug --filter Contract"},
                ]
            },
        )

        self.assertEqual([gate.gate_id for gate in plan.gates], ["build", "test", "contract"])
        self.assertEqual(
            [gate.command for gate in plan.gates],
            [
                "dotnet build Repo.sln -c Debug",
                "dotnet test tests/Repo.Tests.csproj -c Debug",
                "dotnet test tests/Repo.Tests.csproj -c Debug --filter Contract",
            ],
        )

    def test_repo_profile_declared_gate_contract_fails_loudly_when_required_gates_missing(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        with self.assertRaises(ValueError):
            verification_runner.build_repo_profile_verification_plan(
                "quick",
                task_id="task-profile",
                run_id="run-profile",
                profile_raw={
                    "quick_gate_commands": [
                        {"id": "test", "command": "python -m unittest discover"},
                    ]
                },
            )

    def test_verification_artifact_reader_requires_contract_shape(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")
        artifact = verification_runner.verification_artifact_from_dict(
            {
                "mode": "quick",
                "task_id": "task-verify",
                "run_id": "run-verify",
                "gate_order": ["test", "contract"],
                "evidence_link": "artifacts/task-verify/run-verify/verification-output/contract.txt",
                "results": {"test": "pass", "contract": "pass"},
                "result_artifact_refs": {
                    "test": "artifacts/task-verify/run-verify/verification-output/test.txt",
                    "contract": "artifacts/task-verify/run-verify/verification-output/contract.txt",
                },
                "escalation_conditions": ["contract_failure_blocks_delivery"],
                "risky_artifact_refs": [],
            }
        )
        self.assertEqual(artifact.mode, "quick")
        with self.assertRaises(ValueError):
            verification_runner.verification_artifact_from_dict(
                {
                    "mode": "quick",
                    "task_id": "task-verify",
                    "run_id": "run-verify",
                    "gate_order": ["test", "contract"],
                    "results": {"test": "pass", "contract": "pass"},
                }
            )


if __name__ == "__main__":
    unittest.main()
