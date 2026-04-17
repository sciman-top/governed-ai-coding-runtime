import sys
import tempfile
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class TaskStoreTests(unittest.TestCase):
    def test_task_store_round_trip_persists_task_state(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir))
            record = task_store.TaskRecord(
                task_id="task-001",
                task=task_intake.TaskIntake(
                    goal="persist workflow task",
                    scope="foundation task store",
                    acceptance=["task survives reload"],
                    repo="governed-ai-coding-runtime",
                    budgets={"max_steps": 10, "max_minutes": 30},
                ),
                current_state="planned",
            )

            store.save(record)
            loaded = store.load("task-001")

            self.assertEqual(loaded.task_id, "task-001")
            self.assertEqual(loaded.current_state, "planned")
            self.assertEqual(loaded.task.goal, "persist workflow task")

    def test_timeout_and_retry_metadata_survive_reload(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir))
            record = task_store.TaskRecord(
                task_id="task-timeout",
                task=task_intake.TaskIntake(
                    goal="persist timeout metadata",
                    scope="foundation task store",
                    acceptance=["timeout metadata survives reload"],
                    repo="governed-ai-coding-runtime",
                    budgets={"max_steps": 5, "max_minutes": 15},
                ),
                current_state="failed",
                retry_count=1,
                timeout_at="2026-04-17T00:00:00Z",
                last_failure_reason="timeout",
            )

            store.save(record)
            loaded = store.load("task-timeout")

            self.assertEqual(loaded.retry_count, 1)
            self.assertEqual(loaded.timeout_at, "2026-04-17T00:00:00Z")
            self.assertEqual(loaded.last_failure_reason, "timeout")


if __name__ == "__main__":
    unittest.main()
