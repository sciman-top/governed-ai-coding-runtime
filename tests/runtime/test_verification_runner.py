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

    def test_l2_plan_runs_build_test_contract(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        plan = verification_runner.build_verification_plan("l2")

        self.assertEqual(plan.mode, "l2")
        self.assertEqual([gate.gate_id for gate in plan.gates], ["build", "test", "contract"])

    def test_l3_plan_runs_build_test_contract_doctor(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        plan = verification_runner.build_verification_plan("l3")

        self.assertEqual(plan.mode, "l3")
        self.assertEqual([gate.gate_id for gate in plan.gates], ["build", "test", "contract", "doctor"])

    def test_quick_full_aliases_match_layered_gate_shapes(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        quick_plan = verification_runner.build_verification_plan("quick")
        l1_plan = verification_runner.build_verification_plan("l1")
        full_plan = verification_runner.build_verification_plan("full")
        l3_plan = verification_runner.build_verification_plan("l3")

        self.assertEqual([gate.gate_id for gate in quick_plan.gates], [gate.gate_id for gate in l1_plan.gates])
        self.assertEqual([gate.gate_id for gate in full_plan.gates], [gate.gate_id for gate in l3_plan.gates])

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
            self.assertEqual(artifact.cache_hits, {"test": False, "contract": False})

    def test_verification_runner_reuses_cache_hits_when_scope_key_matches(self) -> None:
        artifact_store = importlib.import_module("governed_ai_coding_runtime_contracts.artifact_store")
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        class _CacheStore:
            def __init__(self) -> None:
                self._store: dict[tuple[str, str], dict] = {}

            def get(self, *, namespace: str, key: str) -> dict | None:
                return self._store.get((namespace, key))

            def upsert(self, *, namespace: str, key: str, payload: dict) -> None:
                self._store[(namespace, key)] = dict(payload)

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = artifact_store.LocalArtifactStore(Path(tmp_dir))
            cache_store = _CacheStore()
            plan = verification_runner.build_verification_plan("quick", task_id="task-cache", run_id="run-cache-1")
            calls: list[str] = []

            def _execute(gate) -> tuple[int, str]:
                calls.append(gate.gate_id)
                return 0, f"{gate.gate_id} pass"

            first = verification_runner.run_verification_plan(
                plan,
                artifact_store=store,
                execute_gate=_execute,
                cache_store=cache_store,
                cache_scope_key="repo@commit-1",
            )
            self.assertEqual(calls, ["test", "contract"])
            self.assertEqual(first.cache_hits, {"test": False, "contract": False})

            calls.clear()
            second_plan = verification_runner.build_verification_plan("quick", task_id="task-cache", run_id="run-cache-2")
            second = verification_runner.run_verification_plan(
                second_plan,
                artifact_store=store,
                execute_gate=_execute,
                cache_store=cache_store,
                cache_scope_key="repo@commit-1",
            )
            self.assertEqual(calls, [])
            self.assertEqual(second.cache_hits, {"test": True, "contract": True})

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

    def test_repo_profile_l2_ignores_doctor_even_when_declared_in_full_group(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        plan = verification_runner.build_repo_profile_verification_plan(
            "l2",
            task_id="task-profile",
            run_id="run-profile",
            profile_raw={
                "full_gate_commands": [
                    {"id": "build", "command": "dotnet build Repo.sln -c Debug"},
                    {"id": "test", "command": "dotnet test tests/Repo.Tests.csproj -c Debug"},
                    {"id": "contract", "command": "dotnet test tests/Repo.Tests.csproj -c Debug --filter Contract"},
                    {"id": "doctor", "command": "dotnet tool run doctor"},
                ]
            },
        )

        self.assertEqual([gate.gate_id for gate in plan.gates], ["build", "test", "contract"])

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

    def test_repo_profile_additional_gate_commands_apply_by_profile(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        quick_plan = verification_runner.build_repo_profile_verification_plan(
            "quick",
            task_id="task-profile-quick",
            run_id="run-profile-quick",
            profile_raw={
                "test_commands": [{"id": "test", "command": "python -m unittest"}],
                "contract_commands": [{"id": "contract", "command": "python -m unittest tests/contracts"}],
                "additional_gate_commands": [
                    {"id": "quick-extra", "command": "python scripts/quick-extra.py", "profiles": ["quick"]},
                    {"id": "full-extra", "command": "python scripts/full-extra.py", "profiles": ["full"]},
                ],
            },
        )

        full_plan = verification_runner.build_repo_profile_verification_plan(
            "l2",
            task_id="task-profile-full",
            run_id="run-profile-full",
            profile_raw={
                "build_commands": [{"id": "build", "command": "python -m build"}],
                "test_commands": [{"id": "test", "command": "python -m unittest"}],
                "contract_commands": [{"id": "contract", "command": "python -m unittest tests/contracts"}],
                "additional_gate_commands": [
                    {"id": "quick-extra", "command": "python scripts/quick-extra.py", "profiles": ["quick"]},
                    {"id": "full-extra", "command": "python scripts/full-extra.py", "profiles": ["full"]},
                ],
            },
        )

        self.assertEqual([gate.gate_id for gate in quick_plan.gates], ["test", "contract", "quick-extra"])
        self.assertEqual([gate.gate_id for gate in full_plan.gates], ["build", "test", "contract", "full-extra"])

    def test_verification_overall_outcome_ignores_non_blocking_failures(self) -> None:
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        plan = verification_runner.VerificationPlan(
            mode="quick",
            task_id="task-non-blocking",
            run_id="run-non-blocking",
            gates=[
                verification_runner.VerificationGate(
                    gate_id="test",
                    canonical_name="test",
                    command="python -m unittest",
                    required=True,
                    blocking=True,
                ),
                verification_runner.VerificationGate(
                    gate_id="ui-sampling",
                    canonical_name="ui-sampling",
                    command="python scripts/sample_ui.py",
                    required=False,
                    blocking=False,
                ),
            ],
            escalation_conditions=[],
        )
        artifact = verification_runner.build_verification_artifact(
            plan=plan,
            evidence_link="docs/change-evidence/example.md",
            results={"test": "pass", "ui-sampling": "fail"},
            result_artifact_refs={"test": "a.txt", "ui-sampling": "b.txt"},
        )

        self.assertFalse(verification_runner.verification_has_blocking_failures(artifact))
        self.assertEqual(verification_runner.verification_overall_outcome(artifact), "pass")

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
        layered_artifact = verification_runner.verification_artifact_from_dict(
            {
                "mode": "l3",
                "task_id": "task-verify",
                "run_id": "run-verify",
                "gate_order": ["build", "test", "contract", "doctor"],
                "evidence_link": "artifacts/task-verify/run-verify/verification-output/doctor.txt",
                "results": {"build": "pass", "test": "pass", "contract": "pass", "doctor": "pass"},
                "result_artifact_refs": {
                    "build": "artifacts/task-verify/run-verify/verification-output/build.txt",
                    "test": "artifacts/task-verify/run-verify/verification-output/test.txt",
                    "contract": "artifacts/task-verify/run-verify/verification-output/contract.txt",
                    "doctor": "artifacts/task-verify/run-verify/verification-output/doctor.txt",
                },
                "escalation_conditions": ["contract_failure_blocks_delivery"],
                "risky_artifact_refs": [],
            }
        )
        self.assertEqual(layered_artifact.mode, "l3")
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
