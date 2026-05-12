from __future__ import annotations

import json
import importlib.util
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CodexSharedLauncherTests(unittest.TestCase):
    def test_interop_checker_accepts_common_cockpit_api_base_url_field_names(self) -> None:
        spec = importlib.util.spec_from_file_location("codex_interop_check", ROOT / "scripts" / "codex-interop-check.py")
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(spec.loader)
        spec.loader.exec_module(module)

        for key in ["api_base_url", "base_url", "baseUrl", "apiBaseUrl", "OPENAI_BASE_URL"]:
            with self.subTest(key=key):
                self.assertEqual(
                    "https://relay.example.test/v1",
                    module._cockpit_account_base_url(
                        {
                            "auth_mode": "apikey",
                            key: "https://relay.example.test/v1/",
                        }
                    ),
                )

    def test_project_managed_codex_launchers_are_removed(self) -> None:
        removed_paths = [
            ROOT / "scripts" / "Optimize-CodexLocal.ps1",
            ROOT / "scripts" / "Start-CodexShared.ps1",
            ROOT / "scripts" / "codex-account.py",
            ROOT / "scripts" / "codex-account.ps1",
        ]

        for path in removed_paths:
            with self.subTest(path=path):
                self.assertFalse(path.exists())

    def test_disable_project_interop_disables_top_level_codex_shims(self) -> None:
        script = (ROOT / "scripts" / "Disable-CodexProjectInterop.ps1").read_text(encoding="utf-8")

        self.assertIn("'codex.cmd'", script)
        self.assertIn("'codex.ps1'", script)
        self.assertIn("'codex-account.cmd'", script)
        self.assertIn("codex-cockpit.cmd", script)

    def test_interop_checker_fails_when_any_active_thread_uses_non_shared_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            _create_codex_state_db(codex_home / "state_5.sqlite")
            connection = sqlite3.connect(codex_home / "state_5.sqlite")
            try:
                connection.execute(
                    "insert into threads(id, model_provider, archived, updated_at, updated_at_ms) values(?, ?, ?, ?, ?)",
                    ("thread-openai-majority", "openai", 0, "2026-05-09T03:00:00Z", 4),
                )
                connection.execute(
                    "insert into threads(id, model_provider, archived, updated_at, updated_at_ms) values(?, ?, ?, ?, ?)",
                    ("thread-openai-majority-2", "openai", 0, "2026-05-09T04:00:00Z", 5),
                )
                connection.commit()
            finally:
                connection.close()
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_chatgpt"}], "current_account_id": "codex_chatgpt"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_chatgpt.json").write_text(
                json.dumps({"id": "codex_chatgpt", "auth_mode": "chatgpt", "tokens": {"access_token": "token"}}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps([{"id": "openai", "name": "OpenAI"}]),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps({"instances": [], "defaultSettings": {"extraArgs": "", "lastPid": None}}),
                encoding="utf-8",
            )
            (codex_home / "config.toml").write_text(
                'model_provider = "openai"\nforced_login_method = "chatgpt"\n',
                encoding="utf-8",
            )

            checked = _run_interop_checker(codex_home, cc_switch_db, cockpit_home)

            self.assertEqual(checked.returncode, 2, checked.stdout + checked.stderr)
            payload = json.loads(checked.stdout)
            checks = {check["id"]: check for check in payload["after"]["checks"]}
            provider_check = checks["codex_thread_provider_distribution"]
            self.assertEqual("fail", provider_check["status"])
            self.assertEqual("openai", provider_check["dominant_provider"])
            self.assertEqual({"rightcode": 2}, provider_check["unexpected_providers"])
            self.assertIn("different provider bucket", provider_check["reason"])

    def test_interop_checker_warns_when_api_history_bucket_differs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            _create_codex_state_db(codex_home / "state_5.sqlite")
            connection = sqlite3.connect(codex_home / "state_5.sqlite")
            try:
                connection.execute(
                    "insert into threads(id, model_provider, archived, updated_at, updated_at_ms) values(?, ?, ?, ?, ?)",
                    ("thread-openai-history", "openai", 0, "2026-05-09T03:00:00Z", 4),
                )
                connection.commit()
            finally:
                connection.close()
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_api"}], "current_account_id": "codex_api"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_api.json").write_text(
                json.dumps(
                    {
                        "id": "codex_api",
                        "auth_mode": "apikey",
                        "openai_api_key": "secret",
                        "api_base_url": "http://35.213.82.91:8003/v1",
                        "api_provider_id": "cmp_1778165666417_1",
                        "api_provider_name": "35.213.82.91",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps([{"id": "cmp_1778165666417_1", "name": "35.213.82.91"}]),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps(
                    {
                        "instances": [],
                        "defaultSettings": {
                            "extraArgs": "",
                            "lastPid": None,
                            "followLocalAccount": True,
                            "bindAccountId": None,
                        },
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "config.json").write_text(
                json.dumps(
                    {
                        "codex_launch_on_switch": True,
                        "codex_restart_specified_app_on_switch": False,
                        "codex_specified_app_path": "",
                        "antigravity_dual_switch_no_restart_enabled": False,
                    }
                ),
                encoding="utf-8",
            )
            (codex_home / "config.toml").write_text(
                "\n".join(
                    [
                        'model_provider = "cmp_1778165666417_1"',
                        'forced_login_method = "api"',
                        "",
                        "[model_providers.cmp_1778165666417_1]",
                        'name = "35.213.82.91"',
                        'base_url = "http://35.213.82.91:8003/v1"',
                        'wire_api = "responses"',
                        "requires_openai_auth = true",
                        "supports_websockets = false",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (codex_home / "auth.json").write_text(
                json.dumps(
                    {
                        "auth_mode": "apikey",
                        "OPENAI_API_KEY": "secret",
                        "api_base_url": "http://35.213.82.91:8003/v1",
                        "base_url": "http://35.213.82.91:8003/v1",
                    }
                ),
                encoding="utf-8",
            )

            checked = _run_interop_checker(codex_home, cc_switch_db, cockpit_home, quick_launch=True)

            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
            payload = json.loads(checked.stdout)
            self.assertEqual("attention", payload["status"])
            checks = {check["id"]: check for check in payload["after"]["checks"]}
            self.assertEqual("warn", checks["codex_thread_provider_distribution"]["status"])
            self.assertIn(
                "API connectivity is primary",
                checks["codex_thread_provider_distribution"]["reason"],
            )
            self.assertEqual("warn", checks["codex_live_provider_bucket"]["status"])

    def test_interop_checker_blocks_project_managed_shared_history_repair(self) -> None:
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
            session_dir = codex_home / "sessions" / "2026" / "05" / "10"
            session_dir.mkdir(parents=True)
            session_path = session_dir / "rollout-test.jsonl"
            session_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-rightcode-1",
                                    "model_provider": "rightcode",
                                    "source": "vscode",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "response_item",
                                "payload": {
                                    "text": 'user text mentions "model_provider":"cmp_1778165666417_1"',
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            os.utime(session_path, ns=(1_700_000_000_123_456_789, 1_700_000_000_123_456_789))
            original_session_mtime_ns = session_path.stat().st_mtime_ns
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
            (cockpit_home / "config.json").write_text(
                json.dumps(
                    {
                        "codex_launch_on_switch": True,
                        "codex_restart_specified_app_on_switch": False,
                        "codex_specified_app_path": "",
                        "antigravity_dual_switch_no_restart_enabled": False,
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps(
                    {
                        "instances": [],
                        "defaultSettings": {
                            "extraArgs": "",
                            "lastPid": 99999999,
                            "followLocalAccount": False,
                            "bindAccountId": "codex_old_oauth",
                            "launchMode": "cli",
                        },
                    }
                ),
                encoding="utf-8",
            )

            dry_run = _run_interop_checker(codex_home, cc_switch_db, cockpit_home)
            self.assertEqual(dry_run.returncode, 2, dry_run.stderr)
            dry_payload = json.loads(dry_run.stdout)
            self.assertEqual("fail", dry_payload["status"])
            dry_check_ids = {
                check["id"]: check for check in dry_payload["after"]["checks"]
            }
            self.assertEqual(
                "warn",
                dry_check_ids["cockpit_current_provider_bucket"]["status"],
            )
            self.assertEqual(
                "fail",
                dry_check_ids["cockpit_live_login_mode_matches_current_account"]["status"],
            )
            self.assertEqual(
                "fail",
                dry_check_ids["codex_auth_matches_cockpit_current_account"]["status"],
            )
            self.assertIn(
                "OPENAI_API_KEY is missing from auth.json",
                dry_check_ids["codex_auth_matches_cockpit_current_account"]["issues"],
            )
            self.assertEqual(
                "rightcode",
                dry_check_ids["cockpit_current_provider_bucket"]["dominant_provider"],
            )
            self.assertEqual("pass", dry_check_ids["cockpit_codex_app_restart_semantics"]["status"])
            self.assertEqual(
                "pass",
                dry_check_ids["cockpit_codex_native_launch_on_switch_enabled"]["status"],
            )
            self.assertEqual(
                "fail",
                dry_check_ids["cockpit_codex_instances_follow_current_account"]["status"],
            )
            self.assertEqual(
                "pass",
                dry_check_ids["cockpit_codex_dual_switch_no_restart_enabled"]["status"],
            )
            self.assertEqual(
                "fail",
                dry_check_ids["cockpit_codex_default_cli_launch_mode_absent"]["status"],
            )

            before_files = {
                "config": (codex_home / "config.toml").read_text(encoding="utf-8") if (codex_home / "config.toml").exists() else None,
                "auth": (codex_home / "auth.json").read_text(encoding="utf-8") if (codex_home / "auth.json").exists() else None,
                "cockpit_config": (cockpit_home / "config.json").read_text(encoding="utf-8"),
                "instances": (cockpit_home / "codex_instances.json").read_text(encoding="utf-8"),
                "session": session_path.read_text(encoding="utf-8"),
            }

            applied = _run_interop_checker(
                codex_home, cc_switch_db, cockpit_home, apply=True, migrate_provider_bucket=True
            )
            self.assertEqual(applied.returncode, 2, applied.stdout + applied.stderr)
            payload = json.loads(applied.stdout)
            self.assertEqual("fail", payload["status"])
            actions = {action["id"]: action for action in payload["actions"]}
            self.assertEqual("blocked", actions["codex_interop_write_repair_deprecated"]["status"])
            self.assertEqual("blocked", actions["codex_provider_bucket_migration_deprecated"]["status"])
            self.assertNotIn("codex_live_config_cockpit_provider", actions)
            self.assertNotIn("codex_auth_cockpit_projected", actions)
            self.assertNotIn("codex_threads_provider_bucket_migrated", actions)
            self.assertNotIn("codex_session_provider_bucket_migrated", actions)
            self.assertNotIn("codex_provider_bucket_triggers_ensured", actions)

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
                triggers = {
                    row[0]
                    for row in connection.execute(
                        "select name from sqlite_master where type = 'trigger'"
                    ).fetchall()
                }
            finally:
                connection.close()
            self.assertEqual({"openai": 1, "rightcode": 2}, buckets)
            self.assertEqual({"sqlite_autoindex_threads_1"}, indexes)
            self.assertEqual(set(), triggers)
            session_lines = [json.loads(line) for line in session_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual("rightcode", session_lines[0]["payload"]["model_provider"])
            self.assertEqual(original_session_mtime_ns, session_path.stat().st_mtime_ns)
            self.assertEqual(before_files["config"], (codex_home / "config.toml").read_text(encoding="utf-8") if (codex_home / "config.toml").exists() else None)
            self.assertEqual(before_files["auth"], None)
            self.assertEqual(before_files["cockpit_config"], (cockpit_home / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(before_files["instances"], (cockpit_home / "codex_instances.json").read_text(encoding="utf-8"))
            self.assertEqual(before_files["session"], session_path.read_text(encoding="utf-8"))

    def test_interop_checker_quick_launch_skips_session_scan_and_blocks_sqlite_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            _create_codex_state_db(codex_home / "state_5.sqlite")
            session_dir = codex_home / "sessions" / "2026" / "05" / "10"
            session_dir.mkdir(parents=True)
            (session_dir / "rollout-test.jsonl").write_text(
                json.dumps(
                    {
                        "type": "session_meta",
                        "payload": {"id": "thread-rightcode-1", "model_provider": "rightcode"},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_chatgpt"}], "current_account_id": "codex_chatgpt"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_chatgpt.json").write_text(
                json.dumps({"id": "codex_chatgpt", "auth_mode": "chatgpt", "tokens": {"access_token": "token"}}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps([{"id": "openai", "name": "OpenAI"}]),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps({"instances": [], "defaultSettings": {"extraArgs": "", "lastPid": None}}),
                encoding="utf-8",
            )
            (codex_home / "config.toml").write_text(
                'model_provider = "openai"\nforced_login_method = "chatgpt"\n',
                encoding="utf-8",
            )

            applied = _run_interop_checker(
                codex_home,
                cc_switch_db,
                cockpit_home,
                apply=True,
                migrate_provider_bucket=True,
                quick_launch=True,
            )

            self.assertEqual(applied.returncode, 2, applied.stdout + applied.stderr)
            payload = json.loads(applied.stdout)
            checks = {check["id"]: check for check in payload["after"]["checks"]}
            self.assertTrue(checks["codex_session_provider_distribution"]["session_scan_skipped"])
            actions = {action["id"]: action for action in payload["actions"]}
            self.assertEqual("blocked", actions["codex_interop_write_repair_deprecated"]["status"])
            self.assertEqual("blocked", actions["codex_provider_bucket_migration_deprecated"]["status"])
            self.assertNotIn("codex_session_provider_bucket_migrated", actions)
            self.assertNotIn("codex_provider_bucket_triggers_ensured", actions)
            connection = sqlite3.connect(codex_home / "state_5.sqlite")
            try:
                triggers = {
                    row[0]
                    for row in connection.execute(
                        "select name from sqlite_master where type = 'trigger'"
                    ).fetchall()
                }
                connection.execute(
                    "insert into threads(id, model_provider, archived, updated_at, updated_at_ms) values(?, ?, ?, ?, ?)",
                    ("thread-repoison-attempt", "rightcode", 0, "2026-05-09T05:00:00Z", 6),
                )
                guarded_provider = connection.execute(
                    "select model_provider from threads where id = ?",
                    ("thread-repoison-attempt",),
                ).fetchone()[0]
            finally:
                connection.close()
            self.assertEqual(set(), triggers)
            self.assertEqual("rightcode", guarded_provider)

    def test_interop_checker_restores_cockpit_api_provider_metadata_from_codex_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            (codex_home / "config.toml").write_text(
                'model_provider = "openai"\nopenai_base_url = "https://right.codes/codex/v1"\n',
                encoding="utf-8",
            )
            (codex_home / "auth.json").write_text(
                json.dumps({"auth_mode": "apikey", "OPENAI_API_KEY": "secret"}),
                encoding="utf-8",
            )
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_api"}], "current_account_id": "codex_api"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_api.json").write_text(
                json.dumps(
                    {
                        "id": "codex_api",
                        "email": "api-key-test",
                        "auth_mode": "apikey",
                        "openai_api_key": "secret",
                        "api_provider_mode": "openai_builtin",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps(
                    [
                        {
                            "id": "provider_test",
                            "name": "RightCode",
                            "baseUrl": "https://right.codes/codex/v1",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps({"instances": [], "defaultSettings": {"extraArgs": "", "lastPid": None}}),
                encoding="utf-8",
            )

            before_account = (cockpit_home / "codex_accounts" / "codex_api.json").read_text(encoding="utf-8")

            applied = _run_interop_checker(codex_home, cc_switch_db, cockpit_home, apply=True)

            self.assertEqual(applied.returncode, 2, applied.stdout + applied.stderr)
            payload = json.loads(applied.stdout)
            self.assertEqual("fail", payload["status"])
            actions = {action["id"]: action for action in payload["actions"]}
            self.assertEqual("blocked", actions["codex_interop_write_repair_deprecated"]["status"])
            self.assertNotIn("cockpit_current_api_provider_metadata_restored", actions)
            self.assertEqual(
                before_account,
                (cockpit_home / "codex_accounts" / "codex_api.json").read_text(encoding="utf-8"),
            )

    def test_interop_checker_refuses_api_account_without_base_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            (codex_home / "config.toml").write_text("", encoding="utf-8")
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_api"}], "current_account_id": "codex_api"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_api.json").write_text(
                json.dumps(
                    {
                        "id": "codex_api",
                        "email": "api-key-test",
                        "auth_mode": "apikey",
                        "openai_api_key": "secret",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text("[]", encoding="utf-8")
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps({"instances": [], "defaultSettings": {"extraArgs": "", "lastPid": None}}),
                encoding="utf-8",
            )

            applied = _run_interop_checker(codex_home, cc_switch_db, cockpit_home, apply=True)

            self.assertEqual(applied.returncode, 2, applied.stdout + applied.stderr)
            payload = json.loads(applied.stdout)
            checks = {check["id"]: check for check in payload["after"]["checks"]}
            self.assertEqual("fail", checks["cockpit_current_account_projectable"]["status"])
            self.assertEqual("", checks["cockpit_current_account_projectable"]["base_url"])
            self.assertNotIn("https://api.openai.com/v1", (codex_home / "config.toml").read_text(encoding="utf-8"))
            self.assertFalse((codex_home / "auth.json").exists())

    def test_interop_checker_does_not_mutate_existing_auth_for_unprojectable_api_account(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            (codex_home / "config.toml").write_text("", encoding="utf-8")
            original_auth = {"auth_mode": "chatgpt", "tokens": {"access_token": "old-token"}}
            (codex_home / "auth.json").write_text(json.dumps(original_auth), encoding="utf-8")
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_api"}], "current_account_id": "codex_api"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_api.json").write_text(
                json.dumps(
                    {
                        "id": "codex_api",
                        "email": "api-key-test",
                        "auth_mode": "apikey",
                        "openai_api_key": "secret",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text("[]", encoding="utf-8")
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps({"instances": [], "defaultSettings": {"extraArgs": "", "lastPid": None}}),
                encoding="utf-8",
            )

            applied = _run_interop_checker(codex_home, cc_switch_db, cockpit_home, apply=True)

            self.assertEqual(applied.returncode, 2, applied.stdout + applied.stderr)
            payload = json.loads(applied.stdout)
            action_ids = {action["id"] for action in payload["actions"]}
            self.assertNotIn("codex_auth_cockpit_projected", action_ids)
            self.assertEqual(original_auth, json.loads((codex_home / "auth.json").read_text(encoding="utf-8")))

    def test_interop_checker_treats_cockpit_oauth_as_codex_chatgpt_auth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            _create_codex_state_db(codex_home / "state_5.sqlite")
            connection = sqlite3.connect(codex_home / "state_5.sqlite")
            try:
                connection.execute("update threads set model_provider = 'cockpit_http' where archived = 0")
                connection.commit()
            finally:
                connection.close()
            (codex_home / "config.toml").write_text(
                "\n".join(
                    [
                        'model_provider = "openai"',
                        'forced_login_method = "api"',
                        "",
                        "[model_providers.openai]",
                        'base_url = "http://35.213.82.91:8003/v1"',
                        'wire_api = "responses"',
                        "supports_websockets = false",
                        "",
                        '[model_providers."ollama"]',
                        'base_url = "http://localhost:11434/v1"',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (codex_home / "auth.json").write_text(
                json.dumps({"tokens": {"access_token": "old-token"}}),
                encoding="utf-8",
            )
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_oauth"}], "current_account_id": "codex_oauth"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_oauth.json").write_text(
                json.dumps(
                    {
                        "id": "codex_oauth",
                        "email": "oauth-test@example.test",
                        "auth_mode": "oauth",
                        "tokens": {"access_token": "oauth-token"},
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps([{"id": "openai", "name": "OpenAI"}]),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps(
                    {
                        "instances": [],
                        "defaultSettings": {
                            "extraArgs": "",
                            "lastPid": None,
                            "followLocalAccount": False,
                            "bindAccountId": "codex_old_api",
                        },
                    }
                ),
                encoding="utf-8",
            )

            dry_run = _run_interop_checker(codex_home, cc_switch_db, cockpit_home, quick_launch=True)
            self.assertEqual(dry_run.returncode, 2, dry_run.stdout + dry_run.stderr)
            dry_payload = json.loads(dry_run.stdout)
            dry_checks = {check["id"]: check for check in dry_payload["after"]["checks"]}
            self.assertEqual("fail", dry_checks["codex_builtin_provider_overrides_absent"]["status"])
            self.assertEqual(["ollama", "openai"], dry_checks["codex_builtin_provider_overrides_absent"]["configured_builtin_overrides"])
            self.assertEqual("chatgpt", dry_checks["codex_auth_matches_cockpit_current_account"]["expected_auth_mode"])
            self.assertEqual("chatgpt", dry_checks["codex_auth_matches_cockpit_current_account"]["actual_auth_mode"])
            self.assertEqual("pass", dry_checks["codex_auth_matches_cockpit_current_account"]["status"])
            self.assertEqual("oauth", dry_checks["codex_auth_matches_cockpit_current_account"]["cockpit_auth_mode"])

            before_config = (codex_home / "config.toml").read_text(encoding="utf-8")
            before_auth = (codex_home / "auth.json").read_text(encoding="utf-8")
            before_instances = (cockpit_home / "codex_instances.json").read_text(encoding="utf-8")

            applied = _run_interop_checker(
                codex_home,
                cc_switch_db,
                cockpit_home,
                apply=True,
                migrate_provider_bucket=True,
                quick_launch=True,
            )

            self.assertEqual(applied.returncode, 2, applied.stdout + applied.stderr)
            payload = json.loads(applied.stdout)
            self.assertEqual("fail", payload["status"])
            action_ids = {action["id"] for action in payload["actions"]}
            self.assertIn("codex_interop_write_repair_deprecated", action_ids)
            self.assertIn("codex_provider_bucket_migration_deprecated", action_ids)
            self.assertNotIn("codex_live_config_cockpit_provider", action_ids)
            self.assertNotIn("codex_auth_cockpit_projected", action_ids)
            self.assertNotIn("codex_threads_provider_bucket_migrated", action_ids)
            connection = sqlite3.connect(codex_home / "state_5.sqlite")
            try:
                buckets = dict(
                    connection.execute(
                        "select model_provider, count(*) from threads where archived = 0 group by model_provider"
                    ).fetchall()
                )
            finally:
                connection.close()
            self.assertEqual({"cockpit_http": 2}, buckets)
            self.assertEqual(before_config, (codex_home / "config.toml").read_text(encoding="utf-8"))
            after_checks = {check["id"]: check for check in payload["after"]["checks"]}
            self.assertEqual("fail", after_checks["codex_builtin_provider_overrides_absent"]["status"])
            self.assertEqual(before_auth, (codex_home / "auth.json").read_text(encoding="utf-8"))
            self.assertEqual(before_instances, (cockpit_home / "codex_instances.json").read_text(encoding="utf-8"))

    def test_interop_checker_blocks_explicit_api_account_repair_when_current_account_is_oauth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            _create_codex_state_db(codex_home / "state_5.sqlite")
            (codex_home / "config.toml").write_text(
                'model_provider = "openai"\nforced_login_method = "chatgpt"\n',
                encoding="utf-8",
            )
            (codex_home / "auth.json").write_text(
                json.dumps({"auth_mode": "chatgpt", "tokens": {"access_token": "oauth-token"}}),
                encoding="utf-8",
            )
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps(
                    {
                        "accounts": [{"id": "codex_oauth"}, {"id": "codex_api"}],
                        "current_account_id": "codex_oauth",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_oauth.json").write_text(
                json.dumps(
                    {
                        "id": "codex_oauth",
                        "auth_mode": "oauth",
                        "tokens": {"access_token": "oauth-token"},
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_api.json").write_text(
                json.dumps(
                    {
                        "id": "codex_api",
                        "email": "api-key-test",
                        "auth_mode": "apikey",
                        "openai_api_key": "secret",
                        "api_base_url": "http://35.213.82.91:8003/v1",
                        "api_provider_id": "cmp_35",
                        "api_provider_name": "35.213.82.91",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps([{"id": "cmp_35", "name": "35.213.82.91", "baseUrl": "http://35.213.82.91:8003/v1"}]),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps(
                    {
                        "instances": [],
                        "defaultSettings": {
                            "extraArgs": "",
                            "lastPid": None,
                            "followLocalAccount": True,
                            "bindAccountId": None,
                        },
                    }
                ),
                encoding="utf-8",
            )

            before_config = (codex_home / "config.toml").read_text(encoding="utf-8")
            before_auth = (codex_home / "auth.json").read_text(encoding="utf-8")

            applied = _run_interop_checker(
                codex_home,
                cc_switch_db,
                cockpit_home,
                apply=True,
                migrate_provider_bucket=True,
                quick_launch=True,
                cockpit_account_id="codex_api",
            )

            self.assertEqual(applied.returncode, 2, applied.stdout + applied.stderr)
            payload = json.loads(applied.stdout)
            checks = {check["id"]: check for check in payload["after"]["checks"]}
            self.assertEqual("codex_api", checks["cockpit_codex_current_account_present"]["inspected_account_id"])
            self.assertEqual("chatgpt", checks["codex_auth_matches_cockpit_current_account"]["actual_auth_mode"])
            actions = {action["id"]: action for action in payload["actions"]}
            self.assertEqual("blocked", actions["codex_interop_write_repair_deprecated"]["status"])
            self.assertEqual("blocked", actions["codex_provider_bucket_migration_deprecated"]["status"])
            self.assertEqual(before_config, (codex_home / "config.toml").read_text(encoding="utf-8"))
            self.assertEqual(before_auth, (codex_home / "auth.json").read_text(encoding="utf-8"))

    def test_interop_checker_normalizes_api_profiles_while_current_account_is_oauth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            _create_codex_state_db(codex_home / "state_5.sqlite")
            connection = sqlite3.connect(codex_home / "state_5.sqlite")
            try:
                connection.execute("update threads set model_provider = 'openai' where archived = 0")
                connection.commit()
            finally:
                connection.close()
            (codex_home / "config.toml").write_text(
                "\n".join(
                    [
                        'model_provider = "openai"',
                        'forced_login_method = "chatgpt"',
                        "",
                        "[model_providers.cmp_35]",
                        'name = "35.213.82.91"',
                        'base_url = "http://35.213.82.91:8003/v1"',
                        'wire_api = "responses"',
                        "requires_openai_auth = true",
                        "",
                        "[profiles.shared-cockpit-api]",
                        'forced_login_method = "api"',
                        'model_provider = "openai"',
                        'openai_base_url = "https://api.openai.com/v1"',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (codex_home / "auth.json").write_text(
                json.dumps({"auth_mode": "chatgpt", "tokens": {"access_token": "oauth-token"}}),
                encoding="utf-8",
            )
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps(
                    {
                        "accounts": [{"id": "codex_oauth"}, {"id": "codex_api"}],
                        "current_account_id": "codex_oauth",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_oauth.json").write_text(
                json.dumps(
                    {
                        "id": "codex_oauth",
                        "auth_mode": "oauth",
                        "tokens": {"access_token": "oauth-token"},
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_api.json").write_text(
                json.dumps(
                    {
                        "id": "codex_api",
                        "email": "api-key-test",
                        "auth_mode": "apikey",
                        "openai_api_key": "secret",
                        "api_base_url": "http://35.213.82.91:8003/v1",
                        "api_provider_id": "cmp_35",
                        "api_provider_name": "35.213.82.91",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps([{"id": "cmp_35", "name": "35.213.82.91", "baseUrl": "http://35.213.82.91:8003/v1"}]),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps(
                    {
                        "instances": [],
                        "defaultSettings": {
                            "extraArgs": "",
                            "lastPid": None,
                            "followLocalAccount": True,
                            "bindAccountId": None,
                        },
                    }
                ),
                encoding="utf-8",
            )

            checked = _run_interop_checker(
                codex_home,
                cc_switch_db,
                cockpit_home,
                quick_launch=True,
            )

            self.assertEqual(checked.returncode, 2, checked.stdout + checked.stderr)
            before_payload = json.loads(checked.stdout)
            before_checks = {check["id"]: check for check in before_payload["after"]["checks"]}
            saved_provider_check = before_checks["cockpit_saved_api_provider_profiles_projectable"]
            self.assertEqual("fail", saved_provider_check["status"])
            self.assertEqual("normalize_saved_api_provider_profiles", saved_provider_check["repair_strategy"])
            self.assertIn("cmp_35", saved_provider_check["provider_ids"])
            self.assertTrue(saved_provider_check["findings"])

            before_config = (codex_home / "config.toml").read_text(encoding="utf-8")
            before_auth = (codex_home / "auth.json").read_text(encoding="utf-8")

            applied = _run_interop_checker(
                codex_home,
                cc_switch_db,
                cockpit_home,
                apply=True,
                quick_launch=True,
            )

            self.assertEqual(applied.returncode, 2, applied.stdout + applied.stderr)
            payload = json.loads(applied.stdout)
            actions = {action["id"]: action for action in payload["actions"]}
            self.assertEqual("blocked", actions["codex_interop_write_repair_deprecated"]["status"])
            self.assertNotIn("normalize_saved_api_provider_profiles", actions)
            self.assertEqual(before_config, (codex_home / "config.toml").read_text(encoding="utf-8"))
            self.assertEqual(before_auth, (codex_home / "auth.json").read_text(encoding="utf-8"))

    def test_interop_checker_detects_recent_cockpit_raw_start_after_switch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            _create_codex_state_db(codex_home / "state_5.sqlite")
            connection = sqlite3.connect(codex_home / "state_5.sqlite")
            try:
                connection.execute("update threads set model_provider = 'openai'")
                connection.commit()
            finally:
                connection.close()
            (codex_home / "config.toml").write_text(
                'model_provider = "openai"\nforced_login_method = "chatgpt"\n',
                encoding="utf-8",
            )
            (codex_home / "auth.json").write_text(
                json.dumps({"auth_mode": "chatgpt", "tokens": {"access_token": "oauth-token"}}),
                encoding="utf-8",
            )
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "logs").mkdir()
            (cockpit_home / "config.json").write_text(
                json.dumps({"codex_launch_on_switch": True, "codex_restart_specified_app_on_switch": False}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_oauth"}], "current_account_id": "codex_oauth"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_oauth.json").write_text(
                json.dumps(
                    {
                        "id": "codex_oauth",
                        "auth_mode": "oauth",
                        "tokens": {"access_token": "oauth-token"},
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps([{"id": "openai", "name": "OpenAI"}]),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps(
                    {
                        "instances": [],
                        "defaultSettings": {
                            "extraArgs": "",
                            "lastPid": None,
                            "followLocalAccount": True,
                            "bindAccountId": None,
                        },
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "logs" / "app.log.2026-05-11").write_text(
                "\n".join(
                    [
                        "2099-05-11T00:03:57.627100600+08:00  INFO [Codex切号] 开始切换账号: account_id=codex_oauth",
                        "2099-05-11T00:04:01.545008600+08:00  INFO [Codex Start] 启动策略=system-store-entry app_id=OpenAI.Codex_2p2nqsd0c76g0!App pid=44968",
                    ]
                ),
                encoding="utf-8",
            )

            checked = _run_interop_checker(codex_home, cc_switch_db, cockpit_home, quick_launch=True)

            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
            payload = json.loads(checked.stdout)
            checks_payload = payload.get("checks") or payload["after"]["checks"]
            checks = {check["id"]: check for check in checks_payload}
            self.assertEqual("pass", checks["cockpit_codex_native_launch_on_switch_enabled"]["status"])
            self.assertEqual("pass", checks["cockpit_codex_recent_native_start_after_switch_observed"]["status"])
            self.assertTrue(checks["cockpit_codex_recent_native_start_after_switch_observed"]["detected"])

    def test_interop_checker_does_not_mask_cockpit_raw_start_after_state_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            _create_codex_state_db(codex_home / "state_5.sqlite")
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "logs").mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_oauth"}], "current_account_id": "codex_oauth"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_oauth.json").write_text(
                json.dumps(
                    {
                        "id": "codex_oauth",
                        "auth_mode": "oauth",
                        "tokens": {"access_token": "oauth-token"},
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps([{"id": "openai", "name": "OpenAI"}]),
                encoding="utf-8",
            )
            config_path = cockpit_home / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "codex_launch_on_switch": True,
                        "codex_restart_specified_app_on_switch": False,
                        "codex_specified_app_path": "",
                        "antigravity_dual_switch_no_restart_enabled": False,
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps({"instances": [], "defaultSettings": {"extraArgs": "", "lastPid": None}}),
                encoding="utf-8",
            )
            (cockpit_home / "logs" / "app.log.2000-01-01").write_text(
                "\n".join(
                    [
                        "2000-01-01T00:00:00.000000000+08:00  INFO [Codex切号] 开始切换账号: account_id=codex_oauth",
                        "2000-01-01T00:00:04.000000000+08:00  INFO [Codex Start] 启动策略=system-store-entry app_id=OpenAI.Codex_2p2nqsd0c76g0!App pid=44968",
                    ]
                ),
                encoding="utf-8",
            )
            os.utime(config_path, None)

            checked = _run_interop_checker(codex_home, cc_switch_db, cockpit_home, quick_launch=True)

            self.assertEqual(2, checked.returncode, checked.stdout + checked.stderr)
            payload = json.loads(checked.stdout)
            checks = {check["id"]: check for check in payload["after"]["checks"]}
            start_check = checks["cockpit_codex_recent_native_start_after_switch_observed"]
            self.assertEqual("pass", start_check["status"])
            self.assertTrue(start_check["detected"])
            self.assertTrue(start_check["superseded_by_state_write"])

    def test_interop_checker_flags_unreadable_codex_state_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            codex_home = root / "codex-home"
            codex_home.mkdir()
            (codex_home / "config.toml").write_text("", encoding="utf-8")
            connection = sqlite3.connect(codex_home / "state_5.sqlite")
            try:
                connection.execute("create table unrelated(id text)")
                connection.commit()
            finally:
                connection.close()
            cc_switch_db = root / ".cc-switch" / "cc-switch.db"
            cc_switch_db.parent.mkdir()
            _create_cc_switch_db(cc_switch_db)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts").mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "codex_chatgpt"}], "current_account_id": "codex_chatgpt"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_chatgpt.json").write_text(
                json.dumps(
                    {
                        "id": "codex_chatgpt",
                        "email": "chatgpt-test",
                        "auth_mode": "chatgpt",
                        "tokens": {"access_token": "token"},
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps([{"id": "openai", "name": "OpenAI"}]),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps({"instances": [], "defaultSettings": {"extraArgs": "", "lastPid": None}}),
                encoding="utf-8",
            )

            checked = _run_interop_checker(codex_home, cc_switch_db, cockpit_home)

            self.assertEqual(checked.returncode, 2, checked.stdout + checked.stderr)
            payload = json.loads(checked.stdout)
            checks = {check["id"]: check for check in payload["after"]["checks"]}
            self.assertEqual("fail", checks["codex_thread_provider_distribution"]["status"])
            self.assertIn("threads", checks["codex_thread_provider_distribution"]["reason"])

def _run_interop_checker(
    codex_home: Path,
    cc_switch_db: Path,
    cockpit_home: Path,
    *,
    apply: bool = False,
    migrate_provider_bucket: bool = False,
    quick_launch: bool = False,
    cockpit_account_id: str | None = None,
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
    if quick_launch:
        command.append("--quick-launch")
    if cockpit_account_id:
        command.extend(["--cockpit-account-id", cockpit_account_id])
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
