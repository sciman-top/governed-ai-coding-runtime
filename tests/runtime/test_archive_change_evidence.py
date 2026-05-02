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
        payload = module.build_change_evidence_archive_index(repo_root=ROOT)

        self.assertEqual(payload["dry_run"]["mode"], "dry_run")
        self.assertEqual(payload["index"]["index_kind"], "change_evidence_archive_index")
        groups = {item["group"]: item for item in payload["dry_run"]["candidate_groups"]}
        self.assertIn("historical_snapshots", groups)
        self.assertIn("rule_sync_backups", groups)
        self.assertIn("target_repo_raw_runs", groups)
        self.assertIn("docs_operator_ui_screenshots", groups)
        self.assertGreater(groups["historical_snapshots"]["candidate_file_count"], 0)
        self.assertGreater(groups["rule_sync_backups"]["candidate_file_count"], 0)
        self.assertGreater(groups["target_repo_raw_runs"]["candidate_file_count"], 0)
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


if __name__ == "__main__":
    unittest.main()
