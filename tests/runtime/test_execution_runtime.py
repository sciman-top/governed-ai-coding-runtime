import sys
import tempfile
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class ExecutionRuntimeTests(unittest.TestCase):
    def test_runtime_binds_run_metadata_and_workspace_to_stored_task(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        execution_runtime = importlib.import_module("governed_ai_coding_runtime_contracts.execution_runtime")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir) / "tasks")
            runtime = execution_runtime.ExecutionRuntime(store=store)
            profile = repo_profile.load_repo_profile(
                ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
            )
            record = task_store.TaskRecord(
                task_id="task-runtime-bind",
                task=task_intake.TaskIntake(
                    goal="bind task to a governed run",
                    scope="runtime task",
                    acceptance=["run metadata is persisted"],
                    repo="governed-ai-coding-runtime",
                    budgets={"max_steps": 5, "max_minutes": 15},
                ),
                current_state="planned",
            )
            store.save(record)

            prepared = runtime.prepare_run("task-runtime-bind", profile)
            reloaded = store.load("task-runtime-bind")

            self.assertEqual(prepared.record.current_state, "executing")
            self.assertEqual(reloaded.active_run_id, prepared.run.run_id)
            self.assertEqual(reloaded.current_attempt_id, prepared.run.attempt_id)
            self.assertEqual(reloaded.workspace_root, prepared.workspace.workspace_root)
            self.assertEqual(reloaded.run_history[-1].workspace_root, prepared.workspace.workspace_root)
            self.assertIn(prepared.run.run_id, prepared.workspace.workspace_root)

    def test_runtime_finalize_completed_run_preserves_rollback_reference(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        execution_runtime = importlib.import_module("governed_ai_coding_runtime_contracts.execution_runtime")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir) / "tasks")
            runtime = execution_runtime.ExecutionRuntime(store=store)
            profile = repo_profile.load_repo_profile(
                ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
            )
            record = task_store.TaskRecord(
                task_id="task-runtime-complete",
                task=task_intake.TaskIntake(
                    goal="finalize a governed run",
                    scope="runtime task",
                    acceptance=["rollback ref survives completion"],
                    repo="governed-ai-coding-runtime",
                    budgets={"max_steps": 5, "max_minutes": 15},
                ),
                current_state="planned",
            )
            store.save(record)
            prepared = runtime.prepare_run("task-runtime-complete", profile)

            completed = runtime.finalize_run(
                "task-runtime-complete",
                execution_runtime.WorkerExecutionResult(
                    outcome="completed",
                    summary="worker completed",
                    rollback_ref="docs/runbooks/control-rollback.md",
                    evidence_refs=["docs/change-evidence/runtime.md"],
                ),
            )

            self.assertEqual(completed.current_state, "verifying")
            self.assertEqual(completed.rollback_ref, "docs/runbooks/control-rollback.md")
            self.assertEqual(completed.run_history[-1].status, "completed")
            self.assertEqual(completed.run_history[-1].rollback_ref, "docs/runbooks/control-rollback.md")
            self.assertEqual(completed.run_history[-1].evidence_refs, ["docs/change-evidence/runtime.md"])
            self.assertEqual(completed.active_run_id, prepared.run.run_id)


if __name__ == "__main__":
    unittest.main()
