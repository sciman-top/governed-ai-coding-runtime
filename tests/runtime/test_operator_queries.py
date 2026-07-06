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
    def test_repo_local_query_returns_task_refs_and_interaction_projection(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        operator_queries = importlib.import_module("governed_ai_coding_runtime_contracts.operator_queries")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            artifacts_root = workspace / ".runtime" / "artifacts" / "task-operator" / "run-1"
            (artifacts_root / "handoff").mkdir(parents=True, exist_ok=True)
            (artifacts_root / "replay").mkdir(parents=True, exist_ok=True)
            (artifacts_root / "evidence").mkdir(parents=True, exist_ok=True)
            (artifacts_root / "verification-output").mkdir(parents=True, exist_ok=True)
            (artifacts_root / "handoff" / "package.json").write_text("{}", encoding="utf-8")
            (artifacts_root / "replay" / "write-flow.json").write_text("{}", encoding="utf-8")
            (artifacts_root / "evidence" / "bundle.json").write_text(
                json.dumps(
                    {
                        "interaction_trace": {
                            "applied_policies": [{"posture": "clarifying"}],
                            "task_restatements": ["Restate the failing request before retrying."],
                            "clarification_rounds": [{"scenario": "bugfix", "questions": [], "answers": []}],
                            "observation_checklists": [{"checklist_kind": "bugfix", "items": ["request", "logs", "diff"]}],
                            "compression_actions": [{"compression_mode": "stage_summary"}],
                            "budget_snapshots": [{"budget_status": "near_limit"}],
                        }
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
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

            result = operator_queries.query_operator_task_surface(
                task_root=store.root_path,
                task_id="task-operator",
                run_id="run-1",
                runtime_root=workspace / ".runtime",
            )

            self.assertTrue(result.task_found)
            self.assertEqual(result.task_id, "task-operator")
            self.assertIn("approval-123", result.approval_ids)
            self.assertIn("artifacts/task-operator/run-1/evidence/bundle.json", result.evidence_refs)
            self.assertIn("artifacts/task-operator/run-1/handoff/package.json", result.handoff_refs)
            self.assertIn("artifacts/task-operator/run-1/replay/write-flow.json", result.replay_refs)
            self.assertEqual(result.interaction_posture, "clarifying")
            self.assertEqual(result.latest_task_restatement, "Restate the failing request before retrying.")
            self.assertEqual(result.interaction_budget_status, "near_limit")
            self.assertTrue(result.clarification_active)
            self.assertEqual(result.latest_compression_action, "stage_summary")
            self.assertEqual(result.outstanding_observation_items_count, 3)
            self.assertTrue(result.read_only)

    def test_repo_local_query_keeps_read_surface_when_task_missing(self) -> None:
        operator_queries = importlib.import_module("governed_ai_coding_runtime_contracts.operator_queries")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)

            result = operator_queries.query_operator_task_surface(
                task_root=workspace / ".runtime" / "tasks",
                task_id="task-missing",
                runtime_root=workspace / ".runtime",
            )

            self.assertFalse(result.task_found)
            self.assertEqual(result.evidence_refs, [])
            self.assertEqual(result.handoff_refs, [])
            self.assertEqual(result.replay_refs, [])
            self.assertIsNone(result.interaction_posture)
            self.assertFalse(result.clarification_active)


if __name__ == "__main__":
    unittest.main()
