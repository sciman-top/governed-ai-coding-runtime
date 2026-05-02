import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "archive-change-evidence.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("archive_change_evidence_script", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load script module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ArchiveChangeEvidenceTests(unittest.TestCase):
    def test_builder_reports_expected_candidate_groups(self) -> None:
        module = _load_script_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            change_root = repo_root / "docs" / "change-evidence"
            (change_root / "snapshots" / "old").mkdir(parents=True)
            (change_root / "rule-sync-backups" / "old").mkdir(parents=True)
            (change_root / "snapshots" / "old" / "README.md").write_text("old", encoding="utf-8")
            (change_root / "rule-sync-backups" / "old" / "AGENTS.md").write_text("backup", encoding="utf-8")
            (change_root / "operator-ui-after-runtime-polish.png").write_bytes(b"archive")
            (change_root / "20260503-example.md").write_text("# Example\n", encoding="utf-8")

            payload = module.build_change_evidence_archive_index(repo_root=repo_root)

        self.assertEqual(payload["dry_run"]["mode"], "dry_run")
        self.assertEqual(payload["index"]["index_kind"], "change_evidence_archive_index")
        groups = {item["group"]: item for item in payload["dry_run"]["candidate_groups"]}
        self.assertIn("historical_snapshots", groups)
        self.assertIn("rule_sync_backups", groups)
        self.assertIn("docs_operator_ui_screenshots", groups)
        self.assertGreater(groups["historical_snapshots"]["candidate_file_count"], 0)
        self.assertGreater(groups["rule_sync_backups"]["candidate_file_count"], 0)
        self.assertGreater(len(payload["index"]["current_refs"]["latest_markdown_entries"]), 0)

    def test_cli_prints_json_and_can_write_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_root = Path(tmp_dir)
            temp_docs = temp_root / "docs" / "change-evidence"
            temp_docs.mkdir(parents=True)
            output_index = temp_docs / "evidence-index.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/archive-change-evidence.py",
                    "--dry-run",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["dry_run"]["mode"], "dry_run")

            module = _load_script_module()
            built = module.build_change_evidence_archive_index(repo_root=ROOT)
            output_index.write_text(json.dumps(built["index"], ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            written = json.loads(output_index.read_text(encoding="utf-8"))
            self.assertEqual(written["index_kind"], "change_evidence_archive_index")

    def test_apply_moves_archive_candidates_and_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            change_root = repo_root / "docs" / "change-evidence"
            snapshots = change_root / "snapshots" / "old"
            archive_root = change_root / "archive" / "change-evidence"
            manifest_root = change_root / "archive" / "change-evidence-manifests"
            snapshots.mkdir(parents=True)
            rule_backup = change_root / "rule-sync-backups" / "old"
            rule_backup.mkdir(parents=True)
            old_snapshot = snapshots / "README.md"
            old_snapshot.write_text("old", encoding="utf-8")
            old_backup = rule_backup / "AGENTS.md"
            old_backup.write_text("backup", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/archive-change-evidence.py",
                    "--repo-root",
                    str(repo_root),
                    "--archive-root",
                    str(archive_root),
                    "--manifest-root",
                    str(manifest_root),
                    "--apply",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["apply"]["mode"], "apply")
            self.assertEqual(payload["apply"]["moved_file_count"], 2)
            self.assertFalse(old_snapshot.exists())
            self.assertFalse(old_backup.exists())

            manifest_path = repo_root / payload["apply"]["manifest_path"]
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            sources = {entry["source"] for entry in manifest["moved_files"]}
            self.assertIn("docs/change-evidence/snapshots/old/README.md", sources)
            self.assertIn("docs/change-evidence/rule-sync-backups/old/AGENTS.md", sources)
            self.assertIn("Rollback", manifest["rollback_instructions"])


if __name__ == "__main__":
    unittest.main()
