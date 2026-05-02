import hashlib
import json
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


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


if __name__ == "__main__":
    unittest.main()
