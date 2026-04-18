import sys
import tempfile
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class WorkerTests(unittest.TestCase):
    def test_local_worker_can_execute_one_synchronous_governed_run(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        execution_runtime = importlib.import_module("governed_ai_coding_runtime_contracts.execution_runtime")
        worker_module = importlib.import_module("governed_ai_coding_runtime_contracts.worker")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir) / "tasks")
            runtime = execution_runtime.ExecutionRuntime(store=store)
            profile = repo_profile.load_repo_profile(
                ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
            )
            store.save(
                task_store.TaskRecord(
                    task_id="task-worker-success",
                    task=task_intake.TaskIntake(
                        goal="execute through the local worker",
                        scope="worker runtime",
                        acceptance=["worker runs synchronously"],
                        repo="governed-ai-coding-runtime",
                        budgets={"max_steps": 5, "max_minutes": 15},
                    ),
                    current_state="planned",
                )
            )

            def handler(context):
                return execution_runtime.WorkerExecutionResult(
                    outcome="completed",
                    summary=f"executed {context.run.run_id}",
                    rollback_ref="docs/runbooks/control-rollback.md",
                )

            worker = worker_module.SynchronousLocalWorker(worker_id="worker-001", handler=handler)
            record = runtime.execute_task("task-worker-success", profile, worker)

            self.assertEqual(record.current_state, "verifying")
            self.assertEqual(record.run_history[-1].worker_id, "worker-001")
            self.assertEqual(record.run_history[-1].status, "completed")
            self.assertEqual(record.rollback_ref, "docs/runbooks/control-rollback.md")

    def test_local_worker_can_interrupt_execution_for_approval(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        execution_runtime = importlib.import_module("governed_ai_coding_runtime_contracts.execution_runtime")
        worker_module = importlib.import_module("governed_ai_coding_runtime_contracts.worker")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir) / "tasks")
            runtime = execution_runtime.ExecutionRuntime(store=store)
            profile = repo_profile.load_repo_profile(
                ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
            )
            store.save(
                task_store.TaskRecord(
                    task_id="task-worker-interrupt",
                    task=task_intake.TaskIntake(
                        goal="interrupt when approval is required",
                        scope="worker runtime",
                        acceptance=["approval ids survive interruption"],
                        repo="governed-ai-coding-runtime",
                        budgets={"max_steps": 5, "max_minutes": 15},
                    ),
                    current_state="planned",
                )
            )

            def handler(_context):
                return execution_runtime.WorkerExecutionResult(
                    outcome="interrupted",
                    summary="await approval",
                    approval_ids=["approval-123"],
                    evidence_refs=["docs/change-evidence/approval.md"],
                )

            worker = worker_module.SynchronousLocalWorker(worker_id="worker-approval", handler=handler)
            record = runtime.execute_task("task-worker-interrupt", profile, worker)

            self.assertEqual(record.current_state, "paused")
            self.assertEqual(record.resume_state, "executing")
            self.assertEqual(record.run_history[-1].status, "interrupted")
            self.assertEqual(record.run_history[-1].approval_ids, ["approval-123"])

    def test_worker_rejects_illegal_state_transition(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        repo_profile = importlib.import_module("governed_ai_coding_runtime_contracts.repo_profile")
        execution_runtime = importlib.import_module("governed_ai_coding_runtime_contracts.execution_runtime")
        worker_module = importlib.import_module("governed_ai_coding_runtime_contracts.worker")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir) / "tasks")
            runtime = execution_runtime.ExecutionRuntime(store=store)
            profile = repo_profile.load_repo_profile(
                ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"
            )
            store.save(
                task_store.TaskRecord(
                    task_id="task-worker-illegal",
                    task=task_intake.TaskIntake(
                        goal="reject illegal execution start",
                        scope="worker runtime",
                        acceptance=["illegal transitions fail"],
                        repo="governed-ai-coding-runtime",
                        budgets={"max_steps": 5, "max_minutes": 15},
                    ),
                    current_state="created",
                )
            )
            worker = worker_module.SynchronousLocalWorker(
                worker_id="worker-illegal",
                handler=lambda _context: execution_runtime.WorkerExecutionResult(outcome="completed", summary="done"),
            )

            with self.assertRaises(ValueError):
                runtime.execute_task("task-worker-illegal", profile, worker)


if __name__ == "__main__":
    unittest.main()
