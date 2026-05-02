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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class UninstallTargetRepoGovernanceTests(unittest.TestCase):
    def test_uninstall_governance_dry_run_keeps_files_and_reports_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            source = workspace / "templates" / "managed.py"
            settings_source = workspace / "templates" / "settings.json"
            _write_text(source, "print('managed')\n")
            _write_text(target / ".governed-ai" / "managed.py", "print('managed')\n")
            _write_json(settings_source, {"permissions": {"deny": ["Bash(powershell:*)"]}})
            _write_json(
                target / ".claude" / "settings.json",
                {
                    "permissions": {"deny": ["Bash(powershell:*)", "Read(**/.env)"]},
                    "local": {"keep": True},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [
                        {"path": ".governed-ai/managed.py", "source": str(source), "management_mode": "block_on_drift"},
                        {"path": ".claude/settings.json", "source": str(settings_source), "management_mode": "json_merge"},
                    ],
                    "generated_managed_files": [],
                    "retired_managed_files": [],
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
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
            self.assertEqual(payload["summary"]["shared_patch_candidates"], 1)
            self.assertTrue((target / ".governed-ai" / "managed.py").exists())
            self.assertTrue((target / ".claude" / "settings.json").exists())

    def test_uninstall_governance_applies_safe_deletes_and_patches_shared_json_but_blocks_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            source = workspace / "templates" / "managed.py"
            drift_source = workspace / "templates" / "drifted.py"
            settings_source = workspace / "templates" / "settings.json"
            backup_root = workspace / "backups"
            _write_text(source, "print('managed')\n")
            _write_text(drift_source, "print('managed')\n")
            _write_text(target / ".governed-ai" / "managed.py", "print('managed')\n")
            _write_text(target / ".governed-ai" / "drifted.py", "target edit\n")
            _write_json(settings_source, {"permissions": {"deny": ["Bash(powershell:*)"]}})
            _write_json(
                target / ".claude" / "settings.json",
                {
                    "permissions": {"deny": ["Bash(powershell:*)", "Read(**/.env)"]},
                    "local": {"keep": True},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [
                        {"path": ".governed-ai/managed.py", "source": str(source), "management_mode": "block_on_drift"},
                        {"path": ".governed-ai/drifted.py", "source": str(drift_source), "management_mode": "block_on_drift"},
                        {"path": ".claude/settings.json", "source": str(settings_source), "management_mode": "json_merge"},
                    ],
                    "generated_managed_files": [],
                    "retired_managed_files": [],
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
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
            self.assertEqual(payload["summary"]["deleted"], 1)
            self.assertEqual(payload["summary"]["shared_patched"], 1)
            self.assertEqual(payload["summary"]["blocked"], 1)
            self.assertFalse((target / ".governed-ai" / "managed.py").exists())
            self.assertTrue((target / ".governed-ai" / "drifted.py").exists())
            settings = json.loads((target / ".claude" / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(settings["permissions"]["deny"], ["Read(**/.env)"])
            self.assertEqual(settings["local"], {"keep": True})
            self.assertTrue(Path(payload["deleted_files"][0]["backup_path"]).exists())
            self.assertTrue(Path(payload["patched_shared_files"][0]["backup_path"]).exists())


if __name__ == "__main__":
    unittest.main()
