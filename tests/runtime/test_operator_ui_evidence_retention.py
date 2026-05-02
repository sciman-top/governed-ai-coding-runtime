import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class OperatorUiEvidenceRetentionTests(unittest.TestCase):
    def test_operator_ui_screenshot_retention_dry_run_reports_categories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            change_root = repo_root / "docs" / "change-evidence"
            change_root.mkdir(parents=True)
            (repo_root / "operator-ui-current-runtime.png").write_bytes(b"latest")
            (repo_root / "operator-ui-overview-button-aligned.png").write_bytes(b"milestone")
            (change_root / "operator-ui-after-runtime-polish.png").write_bytes(b"archive")
            (change_root / "operator-ui-v2-workbench.png").write_bytes(b"workbench")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/prune-operator-ui-screenshots.py",
                    "--repo-root",
                    str(repo_root),
                    "--dry-run",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["total_screenshots"], 4)
            self.assertEqual(payload["summary"]["latest_count"], 1)
            self.assertEqual(payload["summary"]["milestone_count"], 2)
            self.assertEqual(payload["summary"]["archive_candidate_count"], 1)
            self.assertEqual(payload["archive_candidates"][0]["path"], "docs/change-evidence/operator-ui-after-runtime-polish.png")
            self.assertTrue((change_root / "operator-ui-after-runtime-polish.png").exists())

    def test_operator_ui_screenshot_retention_apply_moves_archive_candidates_and_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            change_root = repo_root / "docs" / "change-evidence"
            archive_root = repo_root / "docs" / "change-evidence" / "archive" / "operator-ui-screenshots"
            manifest_root = repo_root / "docs" / "change-evidence" / "archive" / "operator-ui-screenshot-prune-manifests"
            change_root.mkdir(parents=True)
            archive_candidate = change_root / "operator-ui-after-runtime-polish.png"
            archive_candidate.write_bytes(b"archive")
            latest = repo_root / "operator-ui-current-runtime.png"
            latest.write_bytes(b"latest")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/prune-operator-ui-screenshots.py",
                    "--repo-root",
                    str(repo_root),
                    "--archive-root",
                    str(archive_root),
                    "--manifest-root",
                    str(manifest_root),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["moved_count"], 1)
            self.assertFalse(archive_candidate.exists())
            moved_destination = repo_root / payload["moved_files"][0]["destination"]
            self.assertTrue(moved_destination.exists())
            self.assertTrue(latest.exists())

            manifest_path = repo_root / payload["archive_plan"]["manifest_path"]
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["moved_files"][0]["source"], "docs/change-evidence/operator-ui-after-runtime-polish.png")
            self.assertIn("rollback", manifest["rollback_instructions"].lower())


if __name__ == "__main__":
    unittest.main()
