import sys
import tempfile
import unittest
import os
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

    def test_rejects_task_ids_with_path_traversal(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir))
            record = task_store.TaskRecord(
                task_id="../escape",
                task=task_intake.TaskIntake(
                    goal="reject unsafe ids",
                    scope="foundation task store",
                    acceptance=["unsafe ids do not escape the task root"],
                    repo="governed-ai-coding-runtime",
                    budgets={"max_steps": 1, "max_minutes": 1},
                ),
                current_state="planned",
            )

            with self.assertRaisesRegex(ValueError, "task_id"):
                store.save(record)

            with self.assertRaisesRegex(ValueError, "task_id"):
                store.load("../escape")

    def test_rejects_symlinked_task_record_outside_root(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "tasks"
            root.mkdir()
            outside = Path(tmp_dir) / "outside-task.json"
            outside.write_text("before", encoding="utf-8")
            try:
                os.symlink(outside, root / "task-symlink.json")
            except (OSError, NotImplementedError):
                self.skipTest("file symlinks are not available in this environment")

            store = task_store.FileTaskStore(root)
            record = task_store.TaskRecord(
                task_id="task-symlink",
                task=task_intake.TaskIntake(
                    goal="reject symlinked task records",
                    scope="task store hardening",
                    acceptance=["task store does not write outside its root"],
                    repo="governed-ai-coding-runtime",
                    budgets={"max_steps": 1, "max_minutes": 1},
                ),
                current_state="planned",
            )

            with self.assertRaisesRegex(ValueError, "task record path"):
                store.save(record)

            with self.assertRaisesRegex(ValueError, "task record path"):
                store.load("task-symlink")

            self.assertEqual(outside.read_text(encoding="utf-8"), "before")


if __name__ == "__main__":
    unittest.main()
