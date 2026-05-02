import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_prune_module():
    path = ROOT / "scripts" / "prune-retired-managed-files.py"
    scripts_path = str(ROOT / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    spec = importlib.util.spec_from_file_location("prune_retired_managed_files_script", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load script: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["prune_retired_managed_files_script"] = module
    spec.loader.exec_module(module)
    return module


class PruneRetiredManagedFilesTests(unittest.TestCase):
    def test_prune_retired_managed_files_dry_run_keeps_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            retired_text = "old managed\n"
            _write_text(target / ".governed-ai" / "old.py", retired_text)
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "retired_managed_files": [
                        {
                            "path": ".governed-ai/old.py",
                            "previous_sha256": f"sha256:{_sha256(retired_text)}",
                            "retire_reason": "obsolete",
                            "replacement": "none",
                            "safe_delete_when": ["target_sha256_matches_previous_sha256", "no_active_references"],
                            "backup_required": True,
                        }
                    ]
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/prune-retired-managed-files.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--dry-run",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["delete_candidates"], 1)
            self.assertEqual(payload["summary"]["deleted"], 0)
            self.assertTrue((target / ".governed-ai" / "old.py").exists())

    def test_prune_retired_managed_files_apply_deletes_with_backup_proof_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            retired_text = "old managed\n"
            retired_path = target / ".governed-ai" / "old.py"
            _write_text(retired_path, retired_text)
            baseline_path = workspace / "baseline.json"
            backup_root = workspace / "backups"
            _write_json(
                baseline_path,
                {
                    "retired_managed_files": [
                        {
                            "path": ".governed-ai/old.py",
                            "previous_sha256": f"sha256:{_sha256(retired_text)}",
                            "retire_reason": "obsolete",
                            "replacement": ".governed-ai/new.py",
                            "safe_delete_when": ["target_sha256_matches_previous_sha256", "no_active_references"],
                            "backup_required": True,
                        }
                    ]
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/prune-retired-managed-files.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--backup-root",
                    str(backup_root),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertFalse(retired_path.exists())
            self.assertEqual(payload["operation_type"], "retired_managed_files_cleanup")
            self.assertEqual(
                payload["deletion_policy"],
                "delete_only_registered_hash_matched_unreferenced_retired_managed_files",
            )
            self.assertIn("deletion_time_sha256_recheck", payload["safety_contract"]["delete_requires"])
            self.assertEqual(payload["summary"]["delete_candidates"], 1)
            self.assertEqual(payload["summary"]["deleted"], 1)
            candidate = payload["delete_candidates"][0]
            self.assertEqual(candidate["path"], ".governed-ai/old.py")
            self.assertEqual(
                candidate["proof"],
                {
                    "baseline_registered": True,
                    "path_bounded": True,
                    "target_sha256_matches_previous_sha256": True,
                    "no_active_references": True,
                    "backup_required": True,
                    "backup_written": True,
                },
            )
            deleted = payload["deleted_files"][0]
            backup_path = Path(deleted["backup_path"])
            self.assertTrue(backup_path.exists())
            self.assertEqual(backup_path.read_text(encoding="utf-8"), retired_text)
            self.assertEqual(deleted["proof"]["backup_written"], True)
            manifest_path = backup_root / "manifest.json"
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["summary"]["deleted"], 1)
            self.assertEqual(manifest["deleted_files"][0]["path"], ".governed-ai/old.py")
            self.assertEqual(payload["manifest_path"], str(manifest_path))

    def test_prune_retired_managed_files_deletes_hash_matched_file_and_blocks_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            retired_text = "old managed\n"
            _write_text(target / ".governed-ai" / "old.py", retired_text)
            _write_text(target / ".governed-ai" / "drifted.py", "target edit\n")
            baseline_path = workspace / "baseline.json"
            backup_root = workspace / "backups"
            _write_json(
                baseline_path,
                {
                    "retired_managed_files": [
                        {
                            "path": ".governed-ai/old.py",
                            "previous_sha256": f"sha256:{_sha256(retired_text)}",
                            "retire_reason": "obsolete",
                            "replacement": "none",
                            "safe_delete_when": ["target_sha256_matches_previous_sha256", "no_active_references"],
                            "backup_required": True,
                        },
                        {
                            "path": ".governed-ai/drifted.py",
                            "previous_sha256": f"sha256:{_sha256(retired_text)}",
                            "retire_reason": "obsolete",
                            "replacement": "none",
                            "safe_delete_when": ["target_sha256_matches_previous_sha256", "no_active_references"],
                            "backup_required": True,
                        },
                    ]
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/prune-retired-managed-files.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--backup-root",
                    str(backup_root),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["summary"]["delete_candidates"], 1)
            self.assertEqual(payload["summary"]["deleted"], 0)
            self.assertEqual(payload["summary"]["blocked"], 1)
            self.assertTrue((target / ".governed-ai" / "old.py").exists())
            self.assertTrue((target / ".governed-ai" / "drifted.py").exists())
            self.assertEqual(payload["deleted_files"], [])

    def test_prune_retired_managed_files_blocks_when_target_changes_after_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            retired_text = "old managed\n"
            target_path = target / ".governed-ai" / "old.py"
            _write_text(target_path, retired_text)
            backup_root = workspace / "backups"
            baseline = {
                "retired_managed_files": [
                    {
                        "path": ".governed-ai/old.py",
                        "previous_sha256": f"sha256:{_sha256(retired_text)}",
                        "retire_reason": "obsolete",
                        "replacement": "none",
                        "safe_delete_when": ["target_sha256_matches_previous_sha256", "no_active_references"],
                        "backup_required": True,
                    }
                ]
            }
            module = _load_prune_module()
            original_copy2 = module.shutil.copy2

            def copy_then_mutate(src, dst):
                result = original_copy2(src, dst)
                target_path.write_text("changed after backup\n", encoding="utf-8")
                return result

            with mock.patch.object(module.shutil, "copy2", side_effect=copy_then_mutate):
                payload, exit_code = module.prune_retired_managed_files(
                    target_repo=target,
                    baseline=baseline,
                    backup_root=backup_root,
                    dry_run=False,
                    apply=True,
                )

            self.assertEqual(exit_code, 2)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["summary"]["deleted"], 0)
            self.assertEqual(payload["blocked_files"][0]["reason"], "target_changed_before_delete")
            self.assertTrue(target_path.exists())
            self.assertEqual(target_path.read_text(encoding="utf-8"), "changed after backup\n")
            self.assertTrue((backup_root / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
