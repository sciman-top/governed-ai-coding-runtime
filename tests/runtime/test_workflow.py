import sys
import tempfile
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class WorkflowSkeletonTests(unittest.TestCase):
    def test_illegal_transition_is_rejected(self) -> None:
        workflow = importlib.import_module("governed_ai_coding_runtime_contracts.workflow")
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")

        record = task_store.TaskRecord(
            task_id="task-illegal",
            task=task_intake.TaskIntake(
                goal="reject illegal transition",
                scope="workflow skeleton",
                acceptance=["illegal transitions fail"],
                repo="governed-ai-coding-runtime",
                budgets={"max_steps": 3, "max_minutes": 10},
            ),
            current_state="created",
        )

        with self.assertRaises(ValueError):
            workflow.transition_task(record, "delivered", actor_type="system", actor_id="workflow", reason="skip flow")

    def test_resume_after_reload_uses_persisted_resume_state(self) -> None:
        workflow = importlib.import_module("governed_ai_coding_runtime_contracts.workflow")
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir))
            record = task_store.TaskRecord(
                task_id="task-resume",
                task=task_intake.TaskIntake(
                    goal="resume after reload",
                    scope="workflow skeleton",
                    acceptance=["paused task resumes deterministically"],
                    repo="governed-ai-coding-runtime",
                    budgets={"max_steps": 3, "max_minutes": 10},
                ),
                current_state="executing",
            )

            paused = workflow.pause_task(record, actor_type="human", actor_id="owner", reason="approval required")
            store.save(paused)
            reloaded = store.load("task-resume")
            resumed = workflow.resume_task(reloaded, actor_type="human", actor_id="owner", reason="approved")

            self.assertEqual(resumed.current_state, "executing")
            self.assertEqual(resumed.resume_state, None)

    def test_retry_transition_persists_count_and_reason(self) -> None:
        workflow = importlib.import_module("governed_ai_coding_runtime_contracts.workflow")
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir))
            record = task_store.TaskRecord(
                task_id="task-retry",
                task=task_intake.TaskIntake(
                    goal="persist retry metadata",
                    scope="workflow skeleton",
                    acceptance=["retry metadata survives reload"],
                    repo="governed-ai-coding-runtime",
                    budgets={"max_steps": 3, "max_minutes": 10},
                ),
                current_state="executing",
            )

            failed = workflow.fail_task(
                record,
                actor_type="system",
                actor_id="workflow",
                reason="timeout",
                timeout_at="2026-04-17T00:00:00Z",
            )
            retried = workflow.retry_task(failed, actor_type="human", actor_id="owner", reason="retry accepted")
            store.save(retried)
            reloaded = store.load("task-retry")

            self.assertEqual(reloaded.current_state, "planned")
            self.assertEqual(reloaded.retry_count, 1)
            self.assertEqual(reloaded.last_failure_reason, "timeout")


if __name__ == "__main__":
    unittest.main()
