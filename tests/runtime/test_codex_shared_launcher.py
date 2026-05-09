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
            self.assertIn("[profiles.shared-cockpit-api]", config)
            self.assertIn("[profiles.shared-cockpit-auth]", config)
            self.assertIn("[profiles.shared-current-provider]", config)
            self.assertIn('model_provider = "rightcode"', config)
            self.assertNotIn("disable_response_storage", config)
            self.assertNotIn("cmp_1778246510288_1", config)

    def test_shared_launcher_supports_cli_exec_and_app_surfaces(self) -> None:
        script = (ROOT / "scripts" / "Start-CodexShared.ps1").read_text(encoding="utf-8")

        self.assertIn("PositionalBinding = $false", script)
        self.assertIn("[ValidateSet('cli', 'exec', 'app', 'resume')]", script)
        self.assertIn("Position = 0, ValueFromRemainingArguments = $true", script)
        self.assertIn("$Surface -eq 'app'", script)
        self.assertIn("$Workdir = $Prompt[0]", script)
        self.assertIn("model_provider={0}", script)
        self.assertIn("$Surface -eq 'exec'", script)
        self.assertIn("$Surface -eq 'resume'", script)
        self.assertIn("Codex app accepts a workspace path", script)
        self.assertIn("UseCockpitCurrentAccount", script)
        self.assertIn("OPENAI_API_KEY sourced from current Cockpit Tools account", script)
        self.assertIn("[Environment]::SetEnvironmentVariable('OPENAI_API_KEY', $null, 'Process')", script)
        self.assertIn("model_providers.{0}.base_url={1}", script)
        self.assertIn("function Invoke-CodexInteropRepair", script)
        self.assertIn("--migrate-provider-bucket", script)
        self.assertIn("function Stop-CodexAppProcesses", script)
        self.assertIn("Get-Process -Name 'Codex', 'codex'", script)
        self.assertIn("Stop-Process -Id $liveProcess.Id", script)
        self.assertIn("$Surface -eq 'app' -and ($UseCockpitCurrentAccount -or $RestartExistingCodexApp)", script)

    def test_optimizer_installs_interop_shortcuts_when_switcher_install_is_enabled(self) -> None:
        script = (ROOT / "scripts" / "Optimize-CodexLocal.ps1").read_text(encoding="utf-8")

        self.assertIn("codex-interop-check.cmd", script)
        self.assertIn("codex-interop-repair.cmd", script)
        self.assertIn("codex-interop-check.py", script)
        self.assertIn("codex-cockpit.cmd", script)
        self.assertIn("codex-cockpit-exec.cmd", script)
        self.assertIn("codex-cockpit-resume.cmd", script)
        self.assertIn("codex-cockpit-app.cmd", script)
        self.assertIn("codex-cockpit-app-restart.cmd", script)
        self.assertIn("codex-relay.cmd", script)
        self.assertIn("codex-relay-exec.cmd", script)
        self.assertIn("codex-relay-resume.cmd", script)
        self.assertIn("codex-relay-app.cmd", script)
        self.assertIn("codex-shared-resume.cmd", script)
        self.assertIn("-Surface resume -UseCockpitCurrentAccount --all --include-non-interactive", script)
        self.assertIn("--cc-switch-db", script)
        self.assertIn("--cockpit-home", script)
        self.assertIn("--migrate-provider-bucket", script)
        self.assertIn("--apply --migrate-provider-bucket %*", script)

    def test_interop_checker_repairs_cc_switch_shared_history_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            _create_codex_state_db(codex_home / "state_5.sqlite")
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            restart_wrapper = root / ".local" / "bin" / "codex-cockpit-app-restart.cmd"
            restart_wrapper.parent.mkdir(parents=True)
            restart_wrapper.write_text("@echo off\n", encoding="ascii")
            _create_cc_switch_db(cc_switch_db)
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_test"}], "current_account_id": "codex_test"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_test.json").write_text(
                json.dumps(
                    {
                        "id": "codex_test",
                        "email": "api-key-test",
                        "auth_mode": "apikey",
                        "openai_api_key": "secret",
                        "api_base_url": "https://right.codes/codex/v1",
                        "api_provider_id": "provider_test",
                        "api_provider_name": "RightCode",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps([{"id": "provider_test", "name": "RightCode"}]),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps({"instances": [], "defaultSettings": {"extraArgs": "", "lastPid": 99999999}}),
                encoding="utf-8",
            )

            dry_run = _run_interop_checker(codex_home, cc_switch_db, cockpit_home)
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            dry_payload = json.loads(dry_run.stdout)
            self.assertEqual("fail", dry_payload["status"])
            dry_check_ids = {
                check["id"]: check for check in dry_payload["after"]["checks"]
            }
            self.assertEqual(
                "fail",
                dry_check_ids["cockpit_current_provider_bucket"]["status"],
            )
            self.assertEqual(
                "fail",
                dry_check_ids["cockpit_live_login_mode_matches_current_account"]["status"],
            )
            self.assertEqual(
                "rightcode",
                dry_check_ids["cockpit_current_provider_bucket"]["dominant_provider"],
            )

            applied = _run_interop_checker(
                codex_home, cc_switch_db, cockpit_home, apply=True, migrate_provider_bucket=True
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            payload = json.loads(applied.stdout)
            self.assertEqual("pass", payload["status"])
            action_ids = {action["id"] for action in payload["actions"]}
            self.assertIn("cockpit_codex_stale_last_pid_cleared", action_ids)
            self.assertIn("codex_live_config_cockpit_provider", action_ids)
            self.assertIn("codex_threads_provider_bucket_migrated", action_ids)
            self.assertIn("cockpit_codex_restart_wrapper_configured", action_ids)
            self.assertIn("codex_history_indexes_ensured", action_ids)

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
            self.assertNotIn(f'sqlite_home = "{escaped_home}"', common)
            self.assertNotIn(f'log_dir = "{escaped_log}"', common)
            self.assertIn("disable_response_storage", provider_settings)

            connection = sqlite3.connect(codex_home / "state_5.sqlite")
            try:
                buckets = dict(
                    connection.execute(
                        "select model_provider, count(*) from threads group by model_provider"
                    ).fetchall()
                )
                indexes = {
                    row[0]
                    for row in connection.execute(
                        "select name from sqlite_master where type = 'index'"
                    ).fetchall()
                }
            finally:
                connection.close()
            self.assertEqual({"openai": 3}, buckets)
            self.assertIn("idx_threads_archived_provider_updated_at_ms", indexes)
            self.assertIn("idx_threads_archived_provider_updated_at", indexes)
            live_config = (codex_home / "config.toml").read_text(encoding="utf-8")
            self.assertIn("[profiles.shared-current-provider]", live_config)
            self.assertIn("[profiles.shared-cockpit-api]", live_config)
            self.assertIn("[profiles.shared-cockpit-auth]", live_config)
            self.assertIn("[profiles.shared-relay]", live_config)
            self.assertNotIn("[model_providers.cockpit]", live_config)
            self.assertIn('forced_login_method = "api"', live_config)
            self.assertIn('model_provider = "openai"', live_config)
            self.assertIn('openai_base_url = "https://right.codes/codex/v1"', live_config)
            cockpit_config = json.loads((cockpit_home / "config.json").read_text(encoding="utf-8"))
            self.assertTrue(cockpit_config["codex_restart_specified_app_on_switch"])
            self.assertEqual(str(restart_wrapper), cockpit_config["codex_specified_app_path"])
            cockpit_instances = json.loads((cockpit_home / "codex_instances.json").read_text(encoding="utf-8"))
            self.assertIsNone(cockpit_instances["defaultSettings"]["lastPid"])

def _run_interop_checker(
    codex_home: Path,
    cc_switch_db: Path,
    cockpit_home: Path,
    *,
    apply: bool = False,
    migrate_provider_bucket: bool = False,
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
    if migrate_provider_bucket:
        command.append("--migrate-provider-bucket")
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
                                "requires_openai_auth = true",
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


def _create_codex_state_db(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            """
            create table threads(
              id text primary key,
              model_provider text,
              archived integer,
              updated_at text,
              updated_at_ms integer
            )
            """
        )
        connection.executemany(
            "insert into threads(id, model_provider, archived, updated_at, updated_at_ms) values(?, ?, ?, ?, ?)",
            [
                ("thread-rightcode-1", "rightcode", 0, "2026-05-09T01:00:00Z", 1),
                ("thread-rightcode-2", "rightcode", 0, "2026-05-09T02:00:00Z", 2),
                ("thread-old-archived", "openai", 1, "2026-05-08T01:00:00Z", 3),
            ],
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    unittest.main()
