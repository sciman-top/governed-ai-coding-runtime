from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CodexSharedLauncherTests(unittest.TestCase):
    def test_optimizer_apply_writes_shared_history_config_without_fixed_relay_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / "codex-home"
            codex_home.mkdir()
            (codex_home / "config.toml").write_text(
                '\n'.join(
                    [
                        'model_provider = "rightcode"',
                        "disable_response_storage = true",
                        "",
                        "[model_providers.rightcode]",
                        'base_url = "https://right.codes/codex/v1"',
                        'wire_api = "responses"',
                    ]
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "Optimize-CodexLocal.ps1"),
                    "-Apply",
                    "-InstallAccountSwitcher:$false",
                    "-SkipInteropCheck",
                    "-CodexHome",
                    str(codex_home),
                    "-TrustedRepoRoot",
                    str(ROOT),
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=60,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("ok", payload["status"])

            config = (codex_home / "config.toml").read_text(encoding="utf-8")
            escaped_home = str(codex_home).replace("\\", "\\\\")
            self.assertIn(f'sqlite_home = "{escaped_home}"', config)
            self.assertIn("[history]", config)
            self.assertIn('persistence = "save-all"', config)
            self.assertIn("[profiles.shared-chatgpt]", config)
            self.assertIn("[profiles.shared-openai-api]", config)
            self.assertIn("[profiles.shared-current-provider]", config)
            self.assertIn('model_provider = "rightcode"', config)
            self.assertNotIn("disable_response_storage", config)
            self.assertNotIn("cmp_1778246510288_1", config)

    def test_shared_launcher_supports_cli_exec_and_app_surfaces(self) -> None:
        script = (ROOT / "scripts" / "Start-CodexShared.ps1").read_text(encoding="utf-8")

        self.assertIn("[ValidateSet('cli', 'exec', 'app')]", script)
        self.assertIn("model_provider={0}", script)
        self.assertIn("$Surface -eq 'exec'", script)
        self.assertIn("Codex app accepts a workspace path", script)

    def test_optimizer_installs_interop_shortcuts_when_switcher_install_is_enabled(self) -> None:
        script = (ROOT / "scripts" / "Optimize-CodexLocal.ps1").read_text(encoding="utf-8")

        self.assertIn("codex-interop-check.cmd", script)
        self.assertIn("codex-interop-repair.cmd", script)
        self.assertIn("codex-interop-check.py", script)
        self.assertIn("--cc-switch-db", script)
        self.assertIn("--cockpit-home", script)
        self.assertIn("--apply %*", script)

    def test_interop_checker_repairs_cc_switch_shared_history_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            _create_cc_switch_db(cc_switch_db)
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_test"}], "current_account_id": "codex_test"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps([{"id": "provider_test", "name": "RightCode"}]),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps({"instances": [], "defaultSettings": {"extraArgs": ""}}),
                encoding="utf-8",
            )

            dry_run = _run_interop_checker(codex_home, cc_switch_db, cockpit_home)
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            dry_payload = json.loads(dry_run.stdout)
            self.assertEqual("fail", dry_payload["status"])

            applied = _run_interop_checker(codex_home, cc_switch_db, cockpit_home, apply=True)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            payload = json.loads(applied.stdout)
            self.assertEqual("pass", payload["status"])
            action_ids = {action["id"] for action in payload["actions"]}
            self.assertIn("cc_switch_db_backup", action_ids)
            self.assertIn("cc_switch_common_config_shared_history", action_ids)
            self.assertIn("cc_switch_provider_storage_enabled", action_ids)

            connection = sqlite3.connect(cc_switch_db)
            try:
                common = connection.execute(
                    "select value from settings where key = 'common_config_codex'"
                ).fetchone()[0]
                provider_settings = connection.execute(
                    "select settings_config from providers where app_type = 'codex'"
                ).fetchone()[0]
            finally:
                connection.close()
            escaped_home = str(codex_home.resolve()).replace("\\", "\\\\")
            escaped_log = str((codex_home / "log").resolve()).replace("\\", "\\\\")
            self.assertIn(f'sqlite_home = "{escaped_home}"', common)
            self.assertIn(f'log_dir = "{escaped_log}"', common)
            self.assertIn('persistence = "save-all"', common)
            self.assertNotIn("disable_response_storage", provider_settings)

def _run_interop_checker(
    codex_home: Path,
    cc_switch_db: Path,
    cockpit_home: Path,
    *,
    apply: bool = False,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "codex-interop-check.py"),
        "--codex-home",
        str(codex_home),
        "--cc-switch-db",
        str(cc_switch_db),
        "--cockpit-home",
        str(cockpit_home),
    ]
    if apply:
        command.append("--apply")
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=60,
    )


def _create_cc_switch_db(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute("create table settings(key text primary key, value text)")
        connection.execute(
            """
            create table providers(
              id text primary key,
              app_type text,
              name text,
              settings_config text,
              is_current boolean
            )
            """
        )
        connection.execute(
            "insert into settings(key, value) values(?, ?)",
            (
                "common_config_codex",
                '\n'.join(
                    [
                        'approval_policy = "never"',
                        "",
                        "[history]",
                        'persistence = "none"',
                    ]
                ),
            ),
        )
        connection.execute(
            "insert into providers(id, app_type, name, settings_config, is_current) values(?, ?, ?, ?, ?)",
            (
                "provider-test",
                "codex",
                "RightCode",
                json.dumps(
                    {
                        "auth": {"OPENAI_API_KEY": "secret"},
                        "config": '\n'.join(
                            [
                                'model_provider = "rightcode"',
                                "disable_response_storage = true",
                                "",
                                "[model_providers.rightcode]",
                                'base_url = "https://right.codes/codex/v1"',
                                'wire_api = "responses"',
                            ]
                        ),
                    }
                ),
                1,
            ),
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    unittest.main()
