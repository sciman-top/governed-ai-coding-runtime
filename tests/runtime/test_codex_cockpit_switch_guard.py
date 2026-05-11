from __future__ import annotations

import importlib.util
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

    def test_repair_command_is_deprecated_and_does_not_run_checker(self) -> None:
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

            self.assertEqual(2, result["exit_code"])
            self.assertEqual([], result["command"])
            self.assertEqual("deprecated", result["stdout_status"])
            self.assertIn("deprecated", result["stderr"])

    def test_powershell_launcher_refuses_install_and_start(self) -> None:
        source = (ROOT / "scripts" / "Start-CodexCockpitSwitchGuard.ps1").read_text(encoding="utf-8")

        self.assertIn("codex-cockpit-switch-guard is deprecated", source)
        self.assertIn("if ($InstallTask)", source)
        self.assertIn("elseif ($Start)", source)
        self.assertNotIn("Register-ScheduledTask", source)
        self.assertNotIn("Start-GuardProcessFallback", source)
        self.assertIn("guard_worker_not_running", source)

    def test_watch_loop_delays_rather_than_drops_min_interval_changes(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn("change_delayed_min_interval", source)
        self.assertIn("time.sleep(wait_seconds)", source)
        self.assertNotIn("change_skipped_min_interval", source)


if __name__ == "__main__":
    unittest.main()
