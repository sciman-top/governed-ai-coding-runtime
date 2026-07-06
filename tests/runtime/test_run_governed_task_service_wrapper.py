import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
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


class RunGovernedTaskServiceWrapperTests(unittest.TestCase):
    def test_run_task_applies_repo_profile_interaction_defaults_to_task_and_evidence(self) -> None:
        module = _load_run_governed_task_module()
        task_store = __import__("governed_ai_coding_runtime_contracts.task_store", fromlist=["FileTaskStore"])
        verification_runner = __import__(
            "governed_ai_coding_runtime_contracts.verification_runner",
            fromlist=["build_verification_artifact"],
        )

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

    def test_snapshot_payload_reads_repo_local_runtime_status(self) -> None:
        module = _load_run_governed_task_module()
        task_store = __import__("governed_ai_coding_runtime_contracts.task_store", fromlist=["FileTaskStore", "TaskRecord", "TaskRunRecord"])
        task_intake = __import__("governed_ai_coding_runtime_contracts.task_intake", fromlist=["TaskIntake"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            tasks_root = workspace / "tasks"
            artifacts_root = workspace / "artifacts" / "task-1" / "run-1" / "evidence"
            artifacts_root.mkdir(parents=True, exist_ok=True)
            (artifacts_root / "bundle.json").write_text(
                json.dumps({"interaction_trace": {"applied_policies": [{"posture": "clarifying"}]}}),
                encoding="utf-8",
            )
            store = task_store.FileTaskStore(tasks_root)
            store.save(
                task_store.TaskRecord(
                    task_id="task-1",
                    task=task_intake.TaskIntake(
                        goal="goal",
                        scope="scope",
                        acceptance=["ok"],
                        repo="governed-ai-coding-runtime",
                        budgets={"max_steps": 1, "max_minutes": 1},
                    ),
                    current_state="planned",
                    active_run_id="run-1",
                    run_history=[
                        task_store.TaskRunRecord(
                            run_id="run-1",
                            attempt_id="attempt-1",
                            worker_id="worker",
                            status="planned",
                            workspace_root=".governed-workspaces/task-1/run-1",
                            started_at="2026-01-01T00:00:00+00:00",
                            evidence_refs=["artifacts/task-1/run-1/evidence/bundle.json"],
                        )
                    ],
                )
            )

            with patch.object(module, "TASK_ROOT", tasks_root), patch.object(
                module, "RUNTIME_ROOT", workspace
            ), patch.object(
                module, "ARTIFACT_ROOT", workspace / "artifacts"
            ), patch.object(
                module, "summarize_codex_capability_readiness", return_value={"status": "ready"}
            ), patch.object(module, "codex_capability_readiness_to_dict", return_value={"status": "ready"}):
                payload = module.snapshot_payload()

        self.assertEqual(payload["total_tasks"], 1)
        self.assertEqual(payload["tasks"][0]["task_id"], "task-1")
        self.assertEqual(payload["tasks"][0]["interaction_posture"], "clarifying")
        self.assertNotIn("attachments", payload)


if __name__ == "__main__":
    unittest.main()
