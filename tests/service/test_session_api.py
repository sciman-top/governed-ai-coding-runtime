import importlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


def _load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class SessionApiTests(unittest.TestCase):
    def test_service_session_api_matches_session_bridge_contract_for_quick_gate_plan(self) -> None:
        service_facade_module = _load_module("packages/agent-runtime/service_facade.py", "service_facade")
        tracing_module = _load_module("packages/observability/runtime_tracing.py", "runtime_tracing")
        session_bridge = importlib.import_module("governed_ai_coding_runtime_contracts.session_bridge")
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            task_root = workspace / ".runtime" / "tasks"
            self._seed_task(task_root, task_id="task-service-session")
            tracer = tracing_module.RuntimeTracer()
            facade = service_facade_module.RuntimeServiceFacade(
                repo_root=ROOT,
                task_root=task_root,
                tracer=tracer,
            )

            api_result = facade.session_command(
                command_type="run_quick_gate",
                task_id="task-service-session",
                repo_binding_id="binding-service-session",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={"run_id": "run-service-001", "plan_only": True},
            )
            direct_command = session_bridge.build_session_bridge_command(
                command_id="direct-service-session",
                command_type="run_quick_gate",
                task_id="task-service-session",
                repo_binding_id="binding-service-session",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={"run_id": "run-service-001", "plan_only": True},
                policy_decision=policy_decision.build_policy_decision(
                    task_id="task-service-session",
                    action_id="direct:run_quick_gate",
                    risk_tier="low",
                    subject="session_command:run_quick_gate",
                    status="allow",
                    decision_basis=["direct parity check"],
                    evidence_ref="artifacts/task-service-session/policy/direct-allow.json",
                ),
            )
            direct_result = session_bridge.handle_session_bridge_command(
                direct_command,
                task_root=task_root,
                repo_root=ROOT,
            )

            self.assertEqual(api_result["status"], direct_result.status)
            self.assertEqual(api_result["payload"]["execution_id"], direct_result.payload["execution_id"])
            self.assertEqual(api_result["payload"]["continuation_id"], direct_result.payload["continuation_id"])
            self.assertEqual(api_result["payload"]["gate_order"], direct_result.payload["gate_order"])
            self.assertEqual(api_result["service_boundary"], "control-plane")
            self.assertGreaterEqual(len(tracer.events()), 1)

    def test_service_session_api_matches_session_bridge_contract_for_full_gate_plan(self) -> None:
        service_facade_module = _load_module("packages/agent-runtime/service_facade.py", "service_facade_full")
        session_bridge = importlib.import_module("governed_ai_coding_runtime_contracts.session_bridge")
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            task_root = workspace / ".runtime" / "tasks"
            self._seed_task(task_root, task_id="task-service-full")
            facade = service_facade_module.RuntimeServiceFacade(repo_root=ROOT, task_root=task_root)

            api_result = facade.session_command(
                command_type="run_full_gate",
                task_id="task-service-full",
                repo_binding_id="binding-service-full",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={"run_id": "run-full-001", "plan_only": True},
            )
            direct_command = session_bridge.build_session_bridge_command(
                command_id="direct-service-full",
                command_type="run_full_gate",
                task_id="task-service-full",
                repo_binding_id="binding-service-full",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={"run_id": "run-full-001", "plan_only": True},
                policy_decision=policy_decision.build_policy_decision(
                    task_id="task-service-full",
                    action_id="direct:run_full_gate",
                    risk_tier="low",
                    subject="session_command:run_full_gate",
                    status="allow",
                    decision_basis=["direct parity check"],
                    evidence_ref="artifacts/task-service-full/policy/direct-allow.json",
                ),
            )
            direct_result = session_bridge.handle_session_bridge_command(
                direct_command,
                task_root=task_root,
                repo_root=ROOT,
            )

            self.assertEqual(api_result["status"], direct_result.status)
            self.assertEqual(api_result["payload"]["execution_id"], direct_result.payload["execution_id"])
            self.assertEqual(api_result["payload"]["continuation_id"], direct_result.payload["continuation_id"])
            self.assertEqual(api_result["payload"]["gate_order"], direct_result.payload["gate_order"])
            self.assertEqual(api_result["payload"]["plan_only"], True)
            self.assertEqual(api_result["service_boundary"], "control-plane")

    def test_service_session_api_matches_session_bridge_contract_for_write_execute_approval_path(self) -> None:
        from governed_ai_coding_runtime_contracts.repo_attachment import attach_target_repo

        service_facade_module = _load_module("packages/agent-runtime/service_facade.py", "service_facade_write")
        session_bridge = importlib.import_module("governed_ai_coding_runtime_contracts.session_bridge")
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            attachment_root = workspace / "target-repo"
            attachment_root.mkdir(parents=True)
            attachment_runtime_state_root = workspace / "runtime-state" / "target-repo"
            attach_target_repo(
                target_repo_root=str(attachment_root),
                runtime_state_root=str(attachment_runtime_state_root),
                repo_id="target-repo",
                display_name="Target Repo",
                primary_language="python",
                build_command="cmd /c exit 0",
                test_command="cmd /c exit 0",
                contract_command="cmd /c exit 0",
                adapter_preference="process_bridge",
            )

            task_root = workspace / ".runtime" / "tasks"
            self._seed_task(task_root, task_id="task-service-write")
            facade = service_facade_module.RuntimeServiceFacade(repo_root=ROOT, task_root=task_root)
            payload = {
                "tool_name": "write_file",
                "target_path": "docs/service-write.txt",
                "tier": "medium",
                "rollback_reference": "docs/runbooks/control-rollback.md",
                "content": "service parity write path",
            }

            api_result = facade.session_command(
                command_type="write_execute",
                task_id="task-service-write",
                repo_binding_id="binding-service-write",
                adapter_id="codex-cli",
                risk_tier="medium",
                payload=payload,
                attachment_root=attachment_root,
                attachment_runtime_state_root=attachment_runtime_state_root,
            )
            direct_command = session_bridge.build_session_bridge_command(
                command_id="direct-service-write",
                command_type="write_execute",
                task_id="task-service-write",
                repo_binding_id="binding-service-write",
                adapter_id="codex-cli",
                risk_tier="medium",
                payload=payload,
                policy_decision=policy_decision.build_policy_decision(
                    task_id="task-service-write",
                    action_id="direct:write_execute",
                    risk_tier="medium",
                    subject="session_command:write_execute",
                    status="allow",
                    decision_basis=["direct parity check"],
                    evidence_ref="artifacts/task-service-write/policy/direct-allow.json",
                ),
            )
            direct_result = session_bridge.handle_session_bridge_command(
                direct_command,
                task_root=task_root,
                repo_root=ROOT,
                attachment_root=attachment_root,
                attachment_runtime_state_root=attachment_runtime_state_root,
            )

            self.assertEqual(api_result["status"], direct_result.status)
            self.assertEqual(api_result["payload"]["execution_status"], direct_result.payload["execution_status"])
            self.assertEqual(api_result["payload"]["approval_status"], direct_result.payload["approval_status"])
            self.assertEqual(api_result["payload"]["reason"], direct_result.payload["reason"])
            self.assertTrue(str(api_result["payload"]["execution_id"]).startswith("task-service-write:approval:"))
            self.assertTrue(str(direct_result.payload["execution_id"]).startswith("task-service-write:approval:"))
            self.assertEqual(api_result["service_boundary"], "control-plane")

    def test_verification_runner_can_persist_run_metadata_for_service_boundary(self) -> None:
        persistence_module = _load_module("packages/agent-runtime/persistence.py", "service_persistence")
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")
        artifact_store = importlib.import_module("governed_ai_coding_runtime_contracts.artifact_store")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            store = persistence_module.SqliteMetadataStore(workspace / "metadata.db")
            artifact = verification_runner.run_verification_plan(
                verification_runner.build_verification_plan("quick", task_id="task-service", run_id="run-service"),
                artifact_store=artifact_store.LocalArtifactStore(workspace / "artifacts"),
                execute_gate=lambda _gate: (0, "ok"),
                metadata_store=store,
            )
            record = store.get(namespace="verification_runs", key="task-service:run-service")

            self.assertEqual(artifact.mode, "quick")
            self.assertIsNotNone(record)
            self.assertEqual(record.payload["results"], {"test": "pass", "contract": "pass"})

    def _seed_task(self, task_root: Path, *, task_id: str) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        store = task_store.FileTaskStore(task_root)
        store.save(
            task_store.TaskRecord(
                task_id=task_id,
                task=task_intake.TaskIntake(
                    goal="service api parity",
                    scope="service",
                    acceptance=["api and cli parity"],
                    repo="governed-ai-coding-runtime",
                    budgets={"max_steps": 5, "max_minutes": 10},
                ),
                current_state="planned",
            )
        )


if __name__ == "__main__":
    unittest.main()
