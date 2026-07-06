import importlib.util
import json
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


class OperatorApiTests(unittest.TestCase):
    def test_operator_routes_expose_status_evidence_handoff_and_continuity_queries(self) -> None:
        service_facade_module = _load_module("packages/agent-runtime/service_facade.py", "service_facade")
        app_module = _load_module("apps/control-plane/app.py", "control_plane_app")
        agent_continuity = _load_module(
            "packages/contracts/src/governed_ai_coding_runtime_contracts/agent_continuity.py",
            "agent_continuity_contract",
        )
        task_store = _load_module(
            "packages/contracts/src/governed_ai_coding_runtime_contracts/task_store.py",
            "task_store_contract",
        )
        task_intake = _load_module(
            "packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py",
            "task_intake_contract",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            tasks_root = workspace / ".runtime" / "tasks"
            evidence_root = workspace / ".runtime" / "artifacts" / "task-operator-api" / "run-operator" / "evidence"
            evidence_root.mkdir(parents=True, exist_ok=True)
            (evidence_root / "bundle.json").write_text(
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
            handoff_root = workspace / ".runtime" / "artifacts" / "task-operator-api" / "run-operator" / "handoff"
            handoff_root.mkdir(parents=True, exist_ok=True)
            (handoff_root / "package.json").write_text("{}", encoding="utf-8")
            replay_root = workspace / ".runtime" / "artifacts" / "task-operator-api" / "run-operator" / "replay"
            replay_root.mkdir(parents=True, exist_ok=True)
            (replay_root / "write-flow.json").write_text("{}", encoding="utf-8")

            store = task_store.FileTaskStore(tasks_root)
            record = task_store.TaskRecord(
                task_id="task-operator-api",
                task=task_intake.TaskIntake(
                    goal="operator api",
                    scope="operator",
                    acceptance=["status and evidence available"],
                    repo="governed-ai-coding-runtime",
                    budgets={"max_steps": 3, "max_minutes": 5},
                ),
                current_state="delivered",
                active_run_id="run-operator",
                run_history=[
                    task_store.TaskRunRecord(
                        run_id="run-operator",
                        attempt_id="attempt-1",
                        worker_id="worker",
                        status="completed",
                        workspace_root=".governed-workspaces/task-operator-api/run-operator",
                        started_at="2026-04-19T00:00:00+00:00",
                        finished_at="2026-04-19T00:01:00+00:00",
                        approval_ids=["approval-operator"],
                        evidence_refs=["artifacts/task-operator-api/run-operator/evidence/bundle.json"],
                        artifact_refs=[
                            "artifacts/task-operator-api/run-operator/handoff/package.json",
                            "artifacts/task-operator-api/run-operator/replay/write-flow.json",
                        ],
                        verification_refs=["artifacts/task-operator-api/run-operator/verification-output/test.txt"],
                    )
                ],
            )
            store.save(record)

            facade = service_facade_module.RuntimeServiceFacade(repo_root=workspace, task_root=tasks_root)
            app = app_module.ControlPlaneApplication(facade=facade)

            status_result = app.dispatch(route="/operator", payload={"action": "status"})
            evidence_result = app.dispatch(
                route="/operator",
                payload={"action": "inspect_evidence", "task_id": "task-operator-api", "run_id": "run-operator"},
            )
            handoff_result = app.dispatch(
                route="/operator",
                payload={"action": "inspect_handoff", "task_id": "task-operator-api", "run_id": "run-operator"},
            )

            continuity_record = agent_continuity.build_claude_desktop_boundary_record(
                repo_root=workspace,
                now="2026-05-10T00:00:00Z",
            ).to_dict()
            continuity_index_root = workspace / ".runtime" / "agent-continuity"
            continuity_write = app.dispatch(
                route="/operator",
                payload={
                    "action": "write_handoff",
                    "index_root": str(continuity_index_root),
                    "record": continuity_record,
                },
            )
            continuity_search = app.dispatch(
                route="/operator",
                payload={
                    "action": "search_context",
                    "index_root": str(continuity_index_root),
                    "repo_id": workspace.name,
                },
            )

            self.assertEqual("ok", status_result["status"])
            self.assertEqual("control-plane", status_result["service_boundary"])
            self.assertTrue(status_result["read_only"])
            self.assertEqual(1, status_result["payload"]["total_tasks"])
            self.assertEqual("task-operator-api", status_result["payload"]["tasks"][0]["task_id"])

            self.assertEqual("ok", evidence_result["status"])
            self.assertEqual("task-operator-api", evidence_result["payload"]["task_id"])
            self.assertEqual("run-operator", evidence_result["payload"]["run_id"])
            self.assertIn(
                "artifacts/task-operator-api/run-operator/evidence/bundle.json",
                evidence_result["payload"]["evidence_refs"],
            )
            self.assertEqual("clarifying", evidence_result["payload"]["interaction_posture"])

            self.assertEqual("ok", handoff_result["status"])
            self.assertIn(
                "artifacts/task-operator-api/run-operator/handoff/package.json",
                handoff_result["payload"]["handoff_refs"],
            )
            self.assertIn(
                "artifacts/task-operator-api/run-operator/replay/write-flow.json",
                handoff_result["payload"]["replay_refs"],
            )

            self.assertEqual("written", continuity_write["status"])
            self.assertEqual("control-plane", continuity_write["service_boundary"])
            self.assertEqual("ok", continuity_search["status"])
            self.assertEqual(1, continuity_search["record_count"])
            self.assertTrue(continuity_search["read_only"])


if __name__ == "__main__":
    unittest.main()
