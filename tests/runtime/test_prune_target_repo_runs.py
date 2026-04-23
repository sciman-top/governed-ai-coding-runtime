import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class PruneTargetRepoRunsScriptTests(unittest.TestCase):
    def test_prune_target_repo_runs_dry_run_keeps_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runs_root = Path(tmp_dir) / "runs"
            _write_json(runs_root / "alpha-onboard-20260101010101.json", {"id": "alpha-onboard"})
            _write_json(runs_root / "alpha-daily-20260102020202.json", {"id": "alpha-daily-1"})
            _write_json(runs_root / "alpha-daily-20260103030303.json", {"id": "alpha-daily-2"})
            _write_json(runs_root / "beta-daily-20260101000000.json", {"id": "beta-daily"})
            _write_json(runs_root / "summary-active-targets-latest.json", {"summary": "keep"})

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/prune-target-repo-runs.py",
                    "--runs-root",
                    str(runs_root),
                    "--keep-days",
                    "0",
                    "--keep-latest-per-target",
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
            self.assertEqual(payload["summary"]["total_run_files"], 4)
            self.assertEqual(payload["summary"]["delete_candidates"], 2)
            self.assertEqual(payload["summary"]["deleted"], 0)
            self.assertTrue((runs_root / "alpha-onboard-20260101010101.json").exists())
            self.assertTrue((runs_root / "alpha-daily-20260102020202.json").exists())
            self.assertTrue((runs_root / "summary-active-targets-latest.json").exists())

    def test_prune_target_repo_runs_deletes_old_runs_and_keeps_derived_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runs_root = Path(tmp_dir) / "runs"
            _write_json(runs_root / "alpha-onboard-20260101010101.json", {"id": "alpha-onboard"})
            _write_json(runs_root / "alpha-daily-20260102020202.json", {"id": "alpha-daily-1"})
            _write_json(runs_root / "alpha-daily-20260103030303.json", {"id": "alpha-daily-2"})
            _write_json(runs_root / "beta-daily-20260101000000.json", {"id": "beta-daily"})
            _write_json(runs_root / "summary-active-targets-latest.json", {"summary": "keep"})

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/prune-target-repo-runs.py",
                    "--runs-root",
                    str(runs_root),
                    "--keep-days",
                    "0",
                    "--keep-latest-per-target",
                    "1",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["summary"]["delete_candidates"], 2)
            self.assertEqual(payload["summary"]["deleted"], 2)
            self.assertFalse((runs_root / "alpha-onboard-20260101010101.json").exists())
            self.assertFalse((runs_root / "alpha-daily-20260102020202.json").exists())
            self.assertTrue((runs_root / "alpha-daily-20260103030303.json").exists())
            self.assertTrue((runs_root / "beta-daily-20260101000000.json").exists())
            self.assertTrue((runs_root / "summary-active-targets-latest.json").exists())


if __name__ == "__main__":
    unittest.main()
