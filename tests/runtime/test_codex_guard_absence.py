from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ABSENCE_SCRIPT = ROOT / "scripts" / "Test-CodexGuardAbsence.ps1"


def run_absence_check(codex_home: Path, task_name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ABSENCE_SCRIPT),
            "-CodexHome",
            str(codex_home),
            "-TaskName",
            task_name,
        ],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        cwd=ROOT,
        check=False,
    )


class CodexGuardAbsenceTests(unittest.TestCase):
    def test_guard_launcher_scripts_are_removed_from_repo(self) -> None:
        self.assertFalse((ROOT / "scripts" / "codex-cockpit-switch-guard.py").exists())
        self.assertFalse((ROOT / "scripts" / "Start-CodexCockpitSwitchGuard.ps1").exists())

    def test_absence_check_passes_without_retired_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / ".codex"
            completed = run_absence_check(
                codex_home,
                f"codex-cockpit-switch-guard-unit-test-{codex_home.parent.name}",
            )

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertFalse(payload["scheduled_task_present"])
        self.assertFalse(payload["startup_launcher_present"])
        self.assertEqual([], payload["retired_installed_files_present"])
        self.assertEqual([], payload["findings"])

    def test_absence_check_fails_when_retired_installed_script_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / ".codex"
            installed_scripts = codex_home / "scripts"
            installed_scripts.mkdir(parents=True)
            (installed_scripts / "Start-CodexShared.ps1").write_text("# retired\n", encoding="utf-8")

            completed = run_absence_check(
                codex_home,
                f"codex-cockpit-switch-guard-unit-test-{root.name}",
            )

        self.assertEqual(2, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("fail", payload["status"])
        self.assertIn("retired_installed_script_present", payload["findings"])
        self.assertEqual(
            [str(installed_scripts / "Start-CodexShared.ps1")],
            payload["retired_installed_files_present"],
        )


if __name__ == "__main__":
    unittest.main()
