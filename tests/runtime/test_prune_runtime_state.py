import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _set_mtime(path: Path, timestamp: int) -> None:
    os.utime(path, (timestamp, timestamp))


class PruneRuntimeStateScriptTests(unittest.TestCase):
    def test_prune_runtime_state_dry_run_protects_referenced_and_latest_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            runtime_root = workspace / "runtime-state" / "self"
            runs_root = workspace / "target-runs"
            _write_text(runtime_root / "artifacts" / "task-old-delete" / "out.txt", "delete")
            _write_text(runtime_root / "artifacts" / "task-ref-keep" / "out.txt", "ref")
            _write_text(runtime_root / "artifacts" / "task-latest-keep" / "out.txt", "latest")
            _set_mtime(runtime_root / "artifacts" / "task-old-delete", 100)
            _set_mtime(runtime_root / "artifacts" / "task-ref-keep", 200)
            _set_mtime(runtime_root / "artifacts" / "task-latest-keep", 300)
            _write_json(runs_root / "self-runtime-daily-20260501010101.json", {
                "result_artifact_refs": {
                    "contract": "artifacts/task-ref-keep/run/verification-output/contract.txt",
                }
            })
            _write_json(runtime_root / "doctor" / "remediation-20260501T010101000.json", {"id": "old"})
            _write_json(runtime_root / "doctor" / "remediation-20260502T010101000.json", {"id": "latest"})
            _write_json(runtime_root / "approvals" / "approval-a.json", {"id": "approval"})
            _write_json(runtime_root / "context" / "context-pack.json", {"id": "context"})

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/prune-runtime-state.py",
                    "--runtime-state-root",
                    str(runtime_root),
                    "--target-run-root",
                    str(runs_root),
                    "--keep-latest-artifacts",
                    "1",
                    "--keep-latest-remediations",
                    "1",
                    "--dry-run",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["summary"]["artifact_dirs_total"], 3)
            self.assertEqual(payload["summary"]["artifact_dirs_referenced_by_target_runs"], 1)
            self.assertEqual(payload["summary"]["artifact_dirs_delete_candidates"], 1)
            self.assertEqual(payload["artifact_delete_candidates"][0]["name"], "task-old-delete")
            self.assertEqual(payload["summary"]["doctor_remediation_delete_candidates"], 1)
            self.assertTrue((runtime_root / "artifacts" / "task-old-delete").exists())
            self.assertTrue((runtime_root / "doctor" / "remediation-20260501T010101000.json").exists())

    def test_prune_runtime_state_apply_deletes_candidates_after_backup_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            runtime_root = workspace / "runtime-state" / "self"
            runs_root = workspace / "target-runs"
            backup_root = workspace / "backup"
            _write_text(runtime_root / "artifacts" / "task-old-delete" / "out.txt", "delete")
            _write_text(runtime_root / "artifacts" / "task-ref-keep" / "out.txt", "ref")
            _write_text(runtime_root / "artifacts" / "task-latest-keep" / "out.txt", "latest")
            _set_mtime(runtime_root / "artifacts" / "task-old-delete", 100)
            _set_mtime(runtime_root / "artifacts" / "task-ref-keep", 200)
            _set_mtime(runtime_root / "artifacts" / "task-latest-keep", 300)
            _write_json(runs_root / "self-runtime-daily-20260501010101.json", {
                "evidence_link": "artifacts/task-ref-keep/run/verification-output/contract.txt",
            })
            _write_json(runtime_root / "doctor" / "remediation-20260501T010101000.json", {"id": "old"})
            _write_json(runtime_root / "doctor" / "remediation-20260502T010101000.json", {"id": "latest"})
            _write_json(runtime_root / "approvals" / "approval-a.json", {"id": "approval"})
            _write_json(runtime_root / "context" / "context-pack.json", {"id": "context"})

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/prune-runtime-state.py",
                    "--runtime-state-root",
                    str(runtime_root),
                    "--target-run-root",
                    str(runs_root),
                    "--keep-latest-artifacts",
                    "1",
                    "--keep-latest-remediations",
                    "1",
                    "--backup-root",
                    str(backup_root),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["summary"]["artifact_dirs_deleted"], 1)
            self.assertEqual(payload["summary"]["doctor_remediation_files_deleted"], 1)
            self.assertFalse((runtime_root / "artifacts" / "task-old-delete").exists())
            self.assertFalse((runtime_root / "doctor" / "remediation-20260501T010101000.json").exists())
            self.assertTrue((runtime_root / "artifacts" / "task-ref-keep").exists())
            self.assertTrue((runtime_root / "artifacts" / "task-latest-keep").exists())
            self.assertTrue((runtime_root / "approvals" / "approval-a.json").exists())
            self.assertTrue((runtime_root / "context" / "context-pack.json").exists())
            self.assertTrue((backup_root / "artifacts" / "task-old-delete" / "out.txt").exists())
            self.assertTrue((backup_root / "doctor" / "remediation-20260501T010101000.json").exists())
            manifest = json.loads((backup_root / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["operation_type"], "runtime_state_prune")
            self.assertIn("rollback", manifest["rollback_instructions"].lower())


if __name__ == "__main__":
    unittest.main()
