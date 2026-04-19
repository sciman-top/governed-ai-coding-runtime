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


class OperatorApiTests(unittest.TestCase):
    def test_operator_routes_expose_status_and_evidence_queries(self) -> None:
        service_facade_module = _load_module("packages/agent-runtime/service_facade.py", "service_facade")
        app_module = _load_module("apps/control-plane/app.py", "control_plane_app")
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            tasks_root = workspace / ".runtime" / "tasks"
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
                        evidence_refs=["artifacts/task-operator-api/run-operator/evidence/bundle.json"],
                        artifact_refs=["artifacts/task-operator-api/run-operator/handoff/package.json"],
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

            self.assertEqual(status_result["status"], "ok")
            self.assertEqual(status_result["service_boundary"], "control-plane")
            self.assertEqual(evidence_result["status"], "ok")
            self.assertIn(
                "artifacts/task-operator-api/run-operator/evidence/bundle.json",
                evidence_result["payload"]["evidence_refs"],
            )
            self.assertEqual(handoff_result["status"], "ok")
            self.assertIn(
                "artifacts/task-operator-api/run-operator/handoff/package.json",
                handoff_result["payload"]["handoff_refs"],
            )


if __name__ == "__main__":
    unittest.main()
