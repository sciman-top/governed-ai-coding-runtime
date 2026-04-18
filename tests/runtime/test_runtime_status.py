import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class RuntimeStatusTests(unittest.TestCase):
    def test_runtime_status_lists_current_and_recent_tasks(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        maintenance_policy = importlib.import_module("governed_ai_coding_runtime_contracts.maintenance_policy")
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir) / "tasks")
            store.save(
                task_store.TaskRecord(
                    task_id="task-status-1",
                    task=task_intake.TaskIntake(
                        goal="show first task",
                        scope="status",
                        acceptance=["listed"],
                        repo="governed-ai-coding-runtime",
                        budgets={"max_steps": 5, "max_minutes": 15},
                    ),
                    current_state="planned",
                )
            )
            store.save(
                task_store.TaskRecord(
                    task_id="task-status-2",
                    task=task_intake.TaskIntake(
                        goal="show second task",
                        scope="status",
                        acceptance=["listed"],
                        repo="governed-ai-coding-runtime",
                        budgets={"max_steps": 5, "max_minutes": 15},
                    ),
                    current_state="failed",
                    rollback_ref="docs/runbooks/control-rollback.md",
                )
            )

            snapshot = runtime_status.RuntimeStatusStore(store.root_path).snapshot()

            self.assertEqual(snapshot.total_tasks, 2)
            self.assertEqual(snapshot.maintenance.stage, "missing")
            self.assertEqual(snapshot.tasks[0].task_id, "task-status-1")
            self.assertEqual(snapshot.tasks[1].rollback_ref, "docs/runbooks/control-rollback.md")

    def test_runtime_status_surfaces_run_level_evidence_and_replay_refs(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir) / "tasks")
            store.save(
                task_store.TaskRecord(
                    task_id="task-status-rich",
                    task=task_intake.TaskIntake(
                        goal="show rich read model",
                        scope="status",
                        acceptance=["run refs are visible"],
                        repo="governed-ai-coding-runtime",
                        budgets={"max_steps": 5, "max_minutes": 15},
                    ),
                    current_state="failed",
                    active_run_id="run-rich",
                    run_history=[
                        task_store.TaskRunRecord(
                            run_id="run-rich",
                            attempt_id="task-status-rich-attempt-1",
                            worker_id="worker-1",
                            status="failed",
                            workspace_root=".governed-workspaces/python/task-status-rich/run-rich",
                            started_at="2026-04-18T00:00:00+00:00",
                            finished_at="2026-04-18T00:10:00+00:00",
                            evidence_refs=["artifacts/task-status-rich/run-rich/evidence/evidence.json"],
                            approval_ids=["approval-001"],
                            artifact_refs=["artifacts/task-status-rich/run-rich/execution-output/worker.txt"],
                            verification_refs=["artifacts/task-status-rich/run-rich/verification-output/test.txt"],
                        )
                    ],
                )
            )

            snapshot = runtime_status.RuntimeStatusStore(store.root_path).snapshot()

            self.assertEqual(snapshot.tasks[0].approval_ids, ["approval-001"])
            self.assertEqual(
                snapshot.tasks[0].verification_refs,
                ["artifacts/task-status-rich/run-rich/verification-output/test.txt"],
            )
            self.assertEqual(
                snapshot.tasks[0].evidence_refs,
                ["artifacts/task-status-rich/run-rich/evidence/evidence.json"],
            )

    def test_runtime_status_handles_empty_state(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = task_store.FileTaskStore(Path(tmp_dir) / "tasks")

            snapshot = runtime_status.RuntimeStatusStore(store.root_path).snapshot()

            self.assertEqual(snapshot.total_tasks, 0)
            self.assertEqual(snapshot.tasks, [])

    def test_runtime_status_loads_repo_maintenance_policy_refs(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_product = repo_root / "docs" / "product"
            docs_product.mkdir(parents=True, exist_ok=True)
            (docs_product / "runtime-compatibility-and-upgrade-policy.md").write_text("# policy\n", encoding="utf-8")
            (docs_product / "maintenance-deprecation-and-retirement-policy.md").write_text("# policy\n", encoding="utf-8")
            store = task_store.FileTaskStore(repo_root / ".runtime" / "tasks")

            snapshot = runtime_status.RuntimeStatusStore(store.root_path, repo_root).snapshot()

            self.assertEqual(snapshot.maintenance.stage, "completed")
            self.assertEqual(
                snapshot.maintenance.compatibility_policy_ref,
                "docs/product/runtime-compatibility-and-upgrade-policy.md",
            )
            self.assertEqual(
                snapshot.maintenance.retirement_policy_ref,
                "docs/product/maintenance-deprecation-and-retirement-policy.md",
            )

    def test_runtime_status_reports_attached_repo_posture(self) -> None:
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            runtime_root = workspace / "runtime-state" / "attached-target"
            target_repo = workspace / "attached-target"
            target_repo.mkdir()
            repo_attachment.attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_root),
                repo_id="attached-target",
                display_name="Attached Target",
                primary_language="python",
                build_command="python -m compileall src",
                test_command="python -m unittest discover",
                contract_command="python -m unittest discover -s tests/contracts",
                adapter_preference="manual_handoff",
                gate_profile="default",
            )
            store = task_store.FileTaskStore(workspace / ".runtime" / "tasks")

            snapshot = runtime_status.RuntimeStatusStore(
                store.root_path,
                workspace,
                attachment_roots=[target_repo],
                attachment_runtime_state_root=runtime_root,
            ).snapshot()

            self.assertEqual(len(snapshot.attachments), 1)
            attachment = snapshot.attachments[0]
            self.assertEqual(attachment.repo_id, "attached-target")
            self.assertEqual(attachment.binding_state, "healthy")
            self.assertEqual(attachment.adapter_preference, "manual_handoff")
            self.assertEqual(Path(attachment.light_pack_path), (target_repo / ".governed-ai" / "light-pack.json").resolve())

    def test_runtime_status_text_reports_attachment_without_tasks(self) -> None:
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            runtime_root = workspace / "runtime-state" / "attached-target"
            target_repo = workspace / "attached-target"
            target_repo.mkdir()
            repo_attachment.attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_root),
                repo_id="attached-target",
                display_name="Attached Target",
                primary_language="python",
                build_command="python -m compileall src",
                test_command="python -m unittest discover",
                contract_command="python -m unittest discover -s tests/contracts",
                adapter_preference="manual_handoff",
                gate_profile="default",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run-governed-task.py",
                    "status",
                    "--attachment-root",
                    str(target_repo),
                    "--attachment-runtime-state-root",
                    str(runtime_root),
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertIn("Attachment attached-target: healthy", completed.stdout)


if __name__ == "__main__":
    unittest.main()
