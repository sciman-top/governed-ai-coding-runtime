import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


def _load_run_governed_task_module():
    module_path = ROOT / "scripts" / "run-governed-task.py"
    spec = importlib.util.spec_from_file_location("run_governed_task_module", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_governed_task_module"] = module
    spec.loader.exec_module(module)
    return module


class _FakeApp:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def dispatch(self, *, route: str, payload: dict | None = None) -> dict:
        self.calls.append({"route": route, "payload": dict(payload or {})})
        if not self._responses:
            raise AssertionError("no fake response left for dispatch")
        return self._responses.pop(0)


class RunGovernedTaskServiceWrapperTests(unittest.TestCase):
    def test_run_task_applies_repo_profile_interaction_defaults_to_task_and_evidence(self) -> None:
        module = _load_run_governed_task_module()
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)

            def fake_run_verification_plan(plan, *, artifact_store, execute_gate):
                return verification_runner.build_verification_artifact(
                    plan,
                    "artifacts/task/run/verification-output/test.txt",
                    {gate.gate_id: "pass" for gate in plan.gates},
                    {gate.gate_id: f"artifacts/task/run/verification-output/{gate.gate_id}.txt" for gate in plan.gates},
                )

            with patch.object(module, "TASK_ROOT", workspace / "tasks"), patch.object(
                module, "ARTIFACT_ROOT", workspace / "artifacts"
            ), patch.object(module, "WORKSPACES_ROOT", workspace / "workspaces"), patch.object(
                module, "run_verification_plan", side_effect=fake_run_verification_plan
            ), patch.object(
                module,
                "_dispatch_session_command",
                return_value={"payload": {"total_tasks": 0, "tasks": [], "attachments": []}},
            ), patch.object(
                module, "summarize_codex_capability_readiness", return_value={"status": "ready"}
            ), patch.object(module, "codex_capability_readiness_to_dict", return_value={"status": "ready"}):
                module.run_task(
                    task_id=None,
                    goal="profile defaults reach runtime",
                    scope="interaction defaults",
                    repo="governed-ai-coding-runtime",
                    profile_path=str(ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"),
                    mode="quick",
                )

            store = task_store.FileTaskStore(workspace / "tasks")
            task_ids = [path.stem for path in (workspace / "tasks").glob("*.json")]
            self.assertEqual(len(task_ids), 1)
            record = store.load(task_ids[0])
            self.assertEqual(record.task.interaction_defaults["default_mode"], "guided")

            evidence_files = sorted((workspace / "artifacts").glob("*/**/evidence/bundle.json"))
            self.assertEqual(len(evidence_files), 1)
            evidence = json.loads(evidence_files[0].read_text(encoding="utf-8"))
            self.assertEqual(evidence["interaction_trace"]["applied_policies"][0]["mode"], "guided")
            self.assertEqual(evidence["interaction_trace"]["applied_policies"][0]["posture"], "aligned")
            metrics_files = sorted((workspace / "artifacts").glob("*/**/metrics/learning-efficiency.json"))
            self.assertEqual(len(metrics_files), 1)
            metrics = json.loads(metrics_files[0].read_text(encoding="utf-8"))
            self.assertEqual(metrics["task_id"], record.task_id)
            self.assertEqual(metrics["metrics_source_ref"], evidence_files[0].relative_to(workspace / "artifacts").as_posix())
            self.assertEqual(metrics["issue_resolution_without_repeated_question"], 1)

    def test_snapshot_payload_uses_service_dispatch(self) -> None:
        module = _load_run_governed_task_module()
        fake_app = _FakeApp(
            [
                {
                    "payload": {
                        "total_tasks": 1,
                        "maintenance_stage": "observe",
                        "maintenance": {
                            "stage": "observe",
                            "compatibility_policy_ref": "docs/policy.md",
                            "upgrade_policy_ref": None,
                            "triage_policy_ref": None,
                            "deprecation_policy_ref": None,
                            "retirement_policy_ref": None,
                        },
                        "tasks": [
                            {
                                "task_id": "task-1",
                                "state": "planned",
                                "goal": "goal",
                                "active_run_id": None,
                                "workspace_root": None,
                                "rollback_ref": None,
                                "approval_ids": [],
                                "artifact_refs": [],
                                "evidence_refs": [],
                                "verification_refs": [],
                            }
                        ],
                        "attachments": [],
                    }
                }
            ]
        )

        with patch.object(module, "_build_control_plane_app", return_value=fake_app), patch.object(
            module, "summarize_codex_capability_readiness", return_value={"status": "ready"}
        ), patch.object(module, "codex_capability_readiness_to_dict", return_value={"status": "ready"}):
            payload = module.snapshot_payload()

        self.assertEqual(payload["total_tasks"], 1)
        self.assertEqual(payload["maintenance"]["stage"], "observe")
        self.assertEqual(len(fake_app.calls), 1)
        self.assertEqual(fake_app.calls[0]["route"], "/session")
        self.assertEqual(fake_app.calls[0]["payload"]["command_type"], "inspect_status")

    def test_govern_attachment_write_uses_service_dispatch(self) -> None:
        module = _load_run_governed_task_module()
        fake_app = _FakeApp([{"payload": {"execution_status": "blocked", "approval_id": "approval-1"}}])

        with patch.object(module, "_build_control_plane_app", return_value=fake_app):
            payload = module.govern_attachment_write(
                attachment_root=str(ROOT),
                attachment_runtime_state_root=str(ROOT / ".runtime"),
                task_id="task-govern",
                tool_name="write_file",
                command_text="",
                target_path="docs/x.txt",
                tier="medium",
                rollback_reference="docs/runbooks/control-rollback.md",
                adapter_id="codex-cli",
            )

        self.assertEqual(payload["execution_status"], "blocked")
        self.assertEqual(fake_app.calls[0]["payload"]["command_type"], "write_request")

    def test_decide_attachment_write_uses_service_dispatch(self) -> None:
        module = _load_run_governed_task_module()
        fake_app = _FakeApp([{"payload": {"approval_id": "approval-1", "status": "approved"}}])

        with patch.object(module, "_build_control_plane_app", return_value=fake_app):
            payload = module.decide_attachment_write(
                attachment_runtime_state_root=str(ROOT / ".runtime"),
                approval_id="approval-1",
                decision="approve",
                decided_by="tester",
                adapter_id="codex-cli",
                task_id="task-approve",
            )

        self.assertEqual(payload["status"], "approved")
        self.assertEqual(fake_app.calls[0]["payload"]["command_type"], "write_approve")

    def test_execute_attachment_write_uses_two_service_dispatch_calls(self) -> None:
        module = _load_run_governed_task_module()
        fake_app = _FakeApp(
            [
                {
                    "payload": {
                        "execution_id": "task:approval:1",
                        "continuation_id": "task:approval:1",
                        "approval_id": "approval-1",
                        "session_identity": {"session_id": "s-1", "resume_id": "r-1"},
                    }
                },
                {"payload": {"execution_status": "write_executed", "approval_status": "approved"}},
            ]
        )

        with patch.object(module, "_build_control_plane_app", return_value=fake_app):
            payload = module.execute_attachment_write(
                attachment_root=str(ROOT),
                attachment_runtime_state_root=str(ROOT / ".runtime"),
                task_id="task-write",
                tool_name="write_file",
                command_text="",
                target_path="docs/x.txt",
                tier="medium",
                rollback_reference="docs/runbooks/control-rollback.md",
                content="payload",
                approval_id=None,
                adapter_id="codex-cli",
            )

        self.assertEqual(payload["execution_status"], "write_executed")
        self.assertEqual(len(fake_app.calls), 2)
        self.assertEqual(fake_app.calls[0]["payload"]["command_type"], "write_request")
        self.assertEqual(fake_app.calls[1]["payload"]["command_type"], "write_execute")

    def test_run_attachment_verification_uses_service_dispatch(self) -> None:
        module = _load_run_governed_task_module()
        fake_app = _FakeApp(
            [
                {
                    "payload": {
                        "mode": "quick",
                        "run_id": "run-1",
                        "gate_order": ["test", "contract"],
                        "results": {"test": "pass", "contract": "pass"},
                        "result_artifact_refs": {"test": "a.json", "contract": "b.json"},
                        "evidence_link": "artifacts/task/run-1/verification-output/contract.json",
                    }
                }
            ]
        )
        fake_attachment = SimpleNamespace(
            binding=SimpleNamespace(binding_id="binding-1"),
            repo_profile_path="schemas/examples/repo-profile/python-service.example.json",
        )
        fake_profile = SimpleNamespace(repo_id="target-repo")

        with patch.object(module, "_build_control_plane_app", return_value=fake_app), patch.object(
            module, "validate_light_pack", return_value=fake_attachment
        ), patch.object(module, "load_repo_profile", return_value=fake_profile):
            payload = module.run_attachment_verification(
                attachment_root=str(ROOT),
                attachment_runtime_state_root=str(ROOT / ".runtime"),
                mode="quick",
                task_id="task-verify",
                run_id="run-1",
            )

        self.assertEqual(payload["repo_id"], "target-repo")
        self.assertEqual(payload["binding_id"], "binding-1")
        self.assertEqual(payload["results"], {"test": "pass", "contract": "pass"})
        self.assertEqual(fake_app.calls[0]["payload"]["command_type"], "run_quick_gate")

    def test_run_attachment_verification_l2_uses_full_command_with_gate_level_payload(self) -> None:
        module = _load_run_governed_task_module()
        fake_app = _FakeApp(
            [
                {
                    "payload": {
                        "mode": "l2",
                        "run_id": "run-2",
                        "gate_order": ["build", "test", "contract"],
                        "results": {"build": "pass", "test": "pass", "contract": "pass"},
                        "result_artifact_refs": {"build": "a.json", "test": "b.json", "contract": "c.json"},
                        "evidence_link": "artifacts/task/run-2/verification-output/contract.json",
                    }
                }
            ]
        )
        fake_attachment = SimpleNamespace(
            binding=SimpleNamespace(binding_id="binding-2"),
            repo_profile_path="schemas/examples/repo-profile/python-service.example.json",
        )
        fake_profile = SimpleNamespace(repo_id="target-repo")

        with patch.object(module, "_build_control_plane_app", return_value=fake_app), patch.object(
            module, "validate_light_pack", return_value=fake_attachment
        ), patch.object(module, "load_repo_profile", return_value=fake_profile):
            payload = module.run_attachment_verification(
                attachment_root=str(ROOT),
                attachment_runtime_state_root=str(ROOT / ".runtime"),
                mode="l2",
                task_id="task-verify-l2",
                run_id="run-2",
            )

        self.assertEqual(payload["mode"], "l2")
        self.assertEqual(payload["gate_order"], ["build", "test", "contract"])
        self.assertEqual(fake_app.calls[0]["payload"]["command_type"], "run_full_gate")
        self.assertEqual(fake_app.calls[0]["payload"]["payload"]["gate_level"], "l2")

    def test_write_replay_case_rejects_unsafe_task_id(self) -> None:
        module = _load_run_governed_task_module()
        replay = importlib.import_module("governed_ai_coding_runtime_contracts.replay")

        reference = replay.build_replay_reference(
            task_id="../escape",
            run_id="run-safe",
            failure_reason="verification failed",
            artifact_refs=["artifacts/task/run/evidence.json"],
            verification_artifact_refs=[],
        )

        with tempfile.TemporaryDirectory() as tmp_dir, patch.object(module, "REPLAY_ROOT", Path(tmp_dir)):
            with self.assertRaisesRegex(ValueError, "task_id"):
                module._write_replay_case(reference)


if __name__ == "__main__":
    unittest.main()
