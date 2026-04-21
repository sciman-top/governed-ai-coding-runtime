import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
import importlib
import json

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

    def test_runtime_status_projects_interaction_fields_from_evidence_bundle(self) -> None:
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            evidence_path = workspace / "artifacts" / "task-status-interaction" / "run-1" / "evidence"
            evidence_path.mkdir(parents=True, exist_ok=True)
            (evidence_path / "bundle.json").write_text(
                json.dumps(
                    {
                        "interaction_trace": {
                            "applied_policies": [{"posture": "guiding"}],
                            "task_restatements": ["Confirm the repro before changing code."],
                            "clarification_rounds": [{"scenario": "bugfix", "questions": [], "answers": []}],
                            "observation_checklists": [{"checklist_kind": "bugfix", "items": ["logs", "repro"]}],
                            "compression_actions": [{"compression_mode": "stage_summary"}],
                            "budget_snapshots": [{"budget_status": "warning"}],
                        }
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            store = task_store.FileTaskStore(workspace / "tasks")
            store.save(
                task_store.TaskRecord(
                    task_id="task-status-interaction",
                    task=task_intake.TaskIntake(
                        goal="show interaction read model",
                        scope="status",
                        acceptance=["interaction fields are visible"],
                        repo="governed-ai-coding-runtime",
                        budgets={"max_steps": 5, "max_minutes": 15},
                    ),
                    current_state="executing",
                    active_run_id="run-1",
                    run_history=[
                        task_store.TaskRunRecord(
                            run_id="run-1",
                            attempt_id="task-status-interaction-attempt-1",
                            worker_id="worker-1",
                            status="running",
                            workspace_root=".governed-workspaces/python/task-status-interaction/run-1",
                            started_at="2026-04-18T00:00:00+00:00",
                            evidence_refs=["artifacts/task-status-interaction/run-1/evidence/bundle.json"],
                        )
                    ],
                )
            )

            snapshot = runtime_status.RuntimeStatusStore(store.root_path, runtime_root=workspace).snapshot()

            self.assertEqual(snapshot.tasks[0].interaction_posture, "guiding")
            self.assertEqual(
                snapshot.tasks[0].latest_task_restatement,
                "Confirm the repro before changing code.",
            )
            self.assertEqual(snapshot.tasks[0].interaction_budget_status, "warning")
            self.assertTrue(snapshot.tasks[0].clarification_active)
            self.assertEqual(snapshot.tasks[0].latest_compression_action, "stage_summary")
            self.assertEqual(snapshot.tasks[0].outstanding_observation_items_count, 2)

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
            self.assertFalse(attachment.fail_closed)
            self.assertIsNone(attachment.remediation)
            self.assertIsNotNone(attachment.context_pack_summary)
            self.assertTrue(attachment.context_pack_summary["exists"])

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

    def test_runtime_snapshot_reader_requires_contract_shape(self) -> None:
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")
        snapshot = runtime_status.runtime_snapshot_from_dict(
            {
                "total_tasks": 0,
                "maintenance": {
                    "stage": "completed",
                    "compatibility_policy_ref": "docs/product/runtime-compatibility-and-upgrade-policy.md",
                    "upgrade_policy_ref": "docs/product/runtime-compatibility-and-upgrade-policy.md",
                    "triage_policy_ref": "docs/product/maintenance-deprecation-and-retirement-policy.md",
                    "deprecation_policy_ref": "docs/product/maintenance-deprecation-and-retirement-policy.md",
                    "retirement_policy_ref": "docs/product/maintenance-deprecation-and-retirement-policy.md",
                },
                "tasks": [],
                "attachments": [],
                "runtime_root": ".runtime",
                "persistence_backend": "filesystem",
            }
        )
        self.assertEqual(snapshot.total_tasks, 0)
        with self.assertRaises(ValueError):
            runtime_status.runtime_snapshot_from_dict(
                {
                    "total_tasks": 0,
                    "tasks": [],
                    "attachments": [],
                }
            )

    def test_runtime_snapshot_reader_accepts_optional_interaction_projection(self) -> None:
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")
        snapshot = runtime_status.runtime_snapshot_from_dict(
            {
                "total_tasks": 1,
                "maintenance": {
                    "stage": "completed",
                    "compatibility_policy_ref": "docs/product/runtime-compatibility-and-upgrade-policy.md",
                    "upgrade_policy_ref": "docs/product/runtime-compatibility-and-upgrade-policy.md",
                    "triage_policy_ref": "docs/product/maintenance-deprecation-and-retirement-policy.md",
                    "deprecation_policy_ref": "docs/product/maintenance-deprecation-and-retirement-policy.md",
                    "retirement_policy_ref": "docs/product/maintenance-deprecation-and-retirement-policy.md",
                },
                "tasks": [
                    {
                        "task_id": "task-1",
                        "current_state": "executing",
                        "goal": "project interaction posture",
                        "active_run_id": "run-1",
                        "workspace_root": ".governed-workspaces/task-1/run-1",
                        "rollback_ref": None,
                        "approval_ids": [],
                        "artifact_refs": [],
                        "evidence_refs": [],
                        "verification_refs": [],
                        "interaction_posture": "guiding",
                        "latest_task_restatement": "Confirm the repro before changing code.",
                        "interaction_budget_status": "warning",
                        "clarification_active": True,
                        "latest_compression_action": "stage_summary",
                        "outstanding_observation_items_count": 2,
                    }
                ],
                "attachments": [],
                "runtime_root": ".runtime",
                "persistence_backend": "filesystem",
            }
        )

        self.assertEqual(snapshot.tasks[0].interaction_posture, "guiding")
        self.assertEqual(snapshot.tasks[0].outstanding_observation_items_count, 2)


if __name__ == "__main__":
    unittest.main()
