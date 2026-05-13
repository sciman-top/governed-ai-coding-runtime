from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "codex-cockpit-switch-guard.py"


def load_guard_module():
    spec = importlib.util.spec_from_file_location("codex_cockpit_switch_guard", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CodexCockpitSwitchGuardTests(unittest.TestCase):
    def test_fingerprint_detects_tracked_file_changes(self) -> None:
        guard = load_guard_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / ".codex"
            cockpit_home = root / ".antigravity_cockpit"
            codex_home.mkdir()
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            config = cockpit_home / "codex_instances.json"
            config.write_text('{"defaultSettings":{"followLocalAccount":true}}', encoding="utf-8")

            before = guard.fingerprint(codex_home, cockpit_home)
            config.write_text('{"defaultSettings":{"followLocalAccount":false}}', encoding="utf-8")
            after = guard.fingerprint(codex_home, cockpit_home)

            self.assertIn(str(config), guard.changed_paths(before, after))

    def test_repair_command_runs_current_account_projection_only(self) -> None:
        guard = load_guard_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            repair_script = root / "codex-interop-check.py"
            repair_script.write_text(
                "import json, sys\n"
                "print(json.dumps({'status':'pass','argv':sys.argv[1:],'actions':[]}))\n",
                encoding="utf-8",
            )

            result = guard.run_interop_repair(
                repair_script=repair_script,
                codex_home=root / ".codex",
                cockpit_home=root / ".antigravity_cockpit",
                cc_switch_db=root / ".cc-switch" / "cc-switch.db",
                timeout_seconds=10,
            )

            self.assertEqual(0, result["exit_code"])
            self.assertEqual("pass", result["stdout_status"])
            self.assertIn("--quick-launch", result["command"])
            self.assertIn("--repair-current-cockpit-account-projection", result["command"])
            self.assertNotIn("--apply", result["command"])
            self.assertNotIn("--migrate-provider-bucket", result["command"])
            self.assertEqual("", result["stderr"])

    def test_once_mode_runs_repair_and_logs_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            repair_script = root / "codex-interop-check.py"
            log_path = root / "guard.jsonl"
            repair_script.write_text(
                "import json\n"
                "print(json.dumps({'status':'pass','actions':[{'id':'repair_current_cockpit_account_projection','status':'changed'}]}))\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--once",
                    "--codex-home",
                    str(root / ".codex"),
                    "--cockpit-home",
                    str(root / ".antigravity_cockpit"),
                    "--cc-switch-db",
                    str(root / ".cc-switch" / "cc-switch.db"),
                    "--repair-script",
                    str(repair_script),
                    "--log-path",
                    str(log_path),
                ],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("manual_repair", payload["event"])
            self.assertEqual("pass", payload["repair"]["stdout_status"])
            self.assertTrue(log_path.exists())

    def test_powershell_launcher_can_install_and_start_current_account_projector(self) -> None:
        source = (ROOT / "scripts" / "Start-CodexCockpitSwitchGuard.ps1").read_text(encoding="utf-8")

        self.assertIn("--repair-script", source)
        self.assertIn("codex-interop-check.py", source)
        self.assertIn("if ($InstallTask)", source)
        self.assertIn("elseif ($Start)", source)
        self.assertIn("Register-ScheduledTask", source)
        self.assertIn("Start-Process", source)
        self.assertIn("Write-StartupLauncher", source)
        self.assertIn("Resolve-PwshPath", source)
        self.assertIn("Select-Object -First 1", source)
        self.assertIn("$PwshPath -split '\\r?\\n'", source)
        self.assertIn("Select-Object -First 1)[0].Trim()", source)
        self.assertIn("startup_launcher_exists", source)
        self.assertIn("guard_worker_not_running", source)

    def test_startup_launcher_writes_single_line_shell_run_command(self) -> None:
        pwsh = shutil.which("pwsh")
        if not pwsh:
            self.skipTest("pwsh is not available")

        source = (ROOT / "scripts" / "Start-CodexCockpitSwitchGuard.ps1").read_text(encoding="utf-8")
        function_start = source.index("function Write-StartupLauncher")
        function_end = source.index("if ($RunWorker)")
        function_source = source[function_start:function_end]

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            launcher = root / "guard.vbs"
            probe = root / "probe.ps1"
            multiline_pwsh = "\r\nC:\\Program Files\\PowerShell\\7\\pwsh.exe\r\n"
            probe.write_text(
                "$CodexHome = 'C:\\Users\\demo\\.codex'\n"
                "$CockpitHome = 'C:\\Users\\demo\\.antigravity_cockpit'\n"
                "$CcSwitchDb = 'C:\\Users\\demo\\.cc-switch\\cc-switch.db'\n"
                + function_source
                + "\nWrite-StartupLauncher -LauncherPath '"
                + str(launcher).replace("'", "''")
                + "' -PwshPath '"
                + multiline_pwsh.replace("'", "''")
                + "'\n"
                + "Get-Content -LiteralPath '"
                + str(launcher).replace("'", "''")
                + "' -Raw\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(probe)],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            vbs = completed.stdout.strip()
            lines = vbs.splitlines()
            self.assertEqual(2, len(lines), vbs)
            self.assertTrue(lines[1].startswith('shell.Run "'), vbs)
            self.assertIn('""C:\\Program Files\\PowerShell\\7\\pwsh.exe""', lines[1])
            self.assertTrue(lines[1].endswith('", 0, False'), vbs)

    def test_guard_has_no_legacy_generic_repair_or_trigger_path(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn("--repair-current-cockpit-account-projection", source)
        self.assertNotIn("--migrate-provider-bucket", source)
        self.assertNotIn("trg_threads_shared_provider", source)
        self.assertIn("if not args.once and not args.watch", source)


if __name__ == "__main__":
    unittest.main()
