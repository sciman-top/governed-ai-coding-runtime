import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class OperatorQueryTests(unittest.TestCase):
    def test_attachment_scoped_query_returns_task_refs_and_posture(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")
        operator_queries = importlib.import_module("governed_ai_coding_runtime_contracts.operator_queries")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "target"
            target_repo.mkdir()
            runtime_state_root = workspace / "runtime-state" / "target"
            repo_attachment.attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_state_root),
                repo_id="target",
                display_name="Target",
                primary_language="python",
                build_command="python -m compileall src",
                test_command="python -m unittest discover",
                contract_command="python -m unittest discover -s tests/contracts",
            )

            approvals_root = runtime_state_root / "approvals"
            approvals_root.mkdir(parents=True, exist_ok=True)
            approval_path = approvals_root / "approval-123.json"
            approval_path.write_text(
                json.dumps(
                    {
                        "approval_id": "approval-123",
                        "task_id": "task-operator",
                        "status": "approved",
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            artifacts_root = runtime_state_root / "artifacts" / "task-operator" / "run-1"
            (artifacts_root / "handoff").mkdir(parents=True, exist_ok=True)
            (artifacts_root / "replay").mkdir(parents=True, exist_ok=True)
            (artifacts_root / "evidence").mkdir(parents=True, exist_ok=True)
            (artifacts_root / "verification-output").mkdir(parents=True, exist_ok=True)
            (artifacts_root / "handoff" / "package.json").write_text("{}", encoding="utf-8")
            (artifacts_root / "replay" / "write-flow.json").write_text("{}", encoding="utf-8")
            (artifacts_root / "evidence" / "bundle.json").write_text("{}", encoding="utf-8")
            (artifacts_root / "verification-output" / "test.txt").write_text("ok", encoding="utf-8")

            store = task_store.FileTaskStore(workspace / ".runtime" / "tasks")
            store.save(
                task_store.TaskRecord(
                    task_id="task-operator",
                    task=task_intake.TaskIntake(
                        goal="operator query",
                        scope="runtime",
                        acceptance=["operator refs visible"],
                        repo="governed-ai-coding-runtime",
                        budgets={"max_steps": 3, "max_minutes": 5},
                    ),
                    current_state="delivered",
                    active_run_id="run-1",
                    run_history=[
                        task_store.TaskRunRecord(
                            run_id="run-1",
                            attempt_id="attempt-1",
                            worker_id="worker",
                            status="completed",
                            workspace_root=".governed-workspaces/task-operator/run-1",
                            started_at="2026-04-20T00:00:00+00:00",
                            finished_at="2026-04-20T00:01:00+00:00",
                            evidence_refs=["artifacts/task-operator/run-1/evidence/bundle.json"],
                            approval_ids=["approval-123"],
                            artifact_refs=[
                                "artifacts/task-operator/run-1/handoff/package.json",
                                "artifacts/task-operator/run-1/replay/write-flow.json",
                            ],
                            verification_refs=["artifacts/task-operator/run-1/verification-output/test.txt"],
                        )
                    ],
                )
            )

            result = operator_queries.query_operator_attachment_surface(
                task_root=store.root_path,
                task_id="task-operator",
                repo_binding_id="binding-target",
                run_id="run-1",
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertTrue(result.task_found)
            self.assertEqual(result.task_id, "task-operator")
            self.assertIn("approval-123", result.approval_ids)
            self.assertIn("artifacts/task-operator/run-1/evidence/bundle.json", result.evidence_refs)
            self.assertIn("artifacts/task-operator/run-1/handoff/package.json", result.handoff_refs)
            self.assertIn("artifacts/task-operator/run-1/replay/write-flow.json", result.replay_refs)
            self.assertEqual(result.posture_summary.binding_state, "healthy")
            self.assertIsNotNone(result.posture_summary.context_pack_summary)
            self.assertTrue(result.posture_summary.context_pack_summary["exists"])
            self.assertTrue(result.read_only)

    def test_attachment_scoped_query_keeps_read_surface_when_task_missing(self) -> None:
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")
        operator_queries = importlib.import_module("governed_ai_coding_runtime_contracts.operator_queries")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "target"
            target_repo.mkdir()
            runtime_state_root = workspace / "runtime-state" / "target"
            repo_attachment.attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_state_root),
                repo_id="target",
                display_name="Target",
                primary_language="python",
                build_command="python -m compileall src",
                test_command="python -m unittest discover",
                contract_command="python -m unittest discover -s tests/contracts",
            )

            result = operator_queries.query_operator_attachment_surface(
                task_root=workspace / ".runtime" / "tasks",
                task_id="task-missing",
                repo_binding_id="binding-target",
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertFalse(result.task_found)
            self.assertEqual(result.evidence_refs, [])
            self.assertEqual(result.handoff_refs, [])
            self.assertEqual(result.replay_refs, [])
            self.assertIsNotNone(result.posture_summary)
            self.assertEqual(result.posture_summary.binding_state, "healthy")


if __name__ == "__main__":
    unittest.main()
