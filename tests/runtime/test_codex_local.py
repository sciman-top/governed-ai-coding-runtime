import base64
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_SRC = ROOT / "scripts"
if str(SCRIPTS_SRC) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_SRC))

from lib import claude_local, codex_local


def _write_auth(
    path: Path,
    *,
    account_id: str,
    last_refresh: str = "2026-04-30T00:00:00Z",
    email: str = "",
    name: str = "",
    plan_type: str = "",
    subscription_active_start: str = "",
    subscription_active_until: str = "",
    subscription_last_checked: str = "",
    id_token_exp: int | None = None,
    access_token_exp: int | None = None,
) -> None:
    tokens = {
        "account_id": account_id,
    }
    if (
        email
        or name
        or plan_type
        or subscription_active_start
        or subscription_active_until
        or subscription_last_checked
        or id_token_exp is not None
    ):
        id_payload = {
            "email": email,
                "name": name,
                "https://api.openai.com/auth": {
                    "chatgpt_plan_type": plan_type,
                    "chatgpt_subscription_active_start": subscription_active_start,
                    "chatgpt_subscription_active_until": subscription_active_until,
                    "chatgpt_subscription_last_checked": subscription_last_checked,
                },
            }
        if id_token_exp is not None:
            id_payload["exp"] = id_token_exp
        tokens["id_token"] = _jwt(id_payload)
    if access_token_exp is not None:
        tokens["access_token"] = _jwt({"exp": access_token_exp})
    path.write_text(
        json.dumps(
            {
                "auth_mode": "chatgpt",
                "last_refresh": last_refresh,
                "tokens": tokens,
            }
        ),
        encoding="utf-8",
    )


def _jwt(payload: dict[str, object]) -> str:
    def encode(value: dict[str, object]) -> str:
        raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    return f"{encode({'alg': 'none', 'typ': 'JWT'})}.{encode(payload)}."


class CodexLocalTests(unittest.TestCase):
    def test_local_status_subprocesses_are_windowless_on_windows(self) -> None:
        with (
            mock.patch.object(codex_local.os, "name", "nt"),
            mock.patch.object(codex_local.subprocess, "CREATE_NO_WINDOW", 0x08000000, create=True),
            mock.patch.object(claude_local.os, "name", "nt"),
            mock.patch.object(claude_local.subprocess, "CREATE_NO_WINDOW", 0x08000000, create=True),
        ):
            self.assertEqual({"creationflags": 0x08000000}, codex_local._windows_no_window_kwargs())
            self.assertEqual({"creationflags": 0x08000000}, claude_local._windows_no_window_kwargs())

    def test_default_codex_context_profile_targets_one_million_window(self) -> None:
        self.assertEqual(1000000, codex_local.DEFAULT_CONFIG["model_context_window"])
        self.assertEqual(810000, codex_local.DEFAULT_CONFIG["model_auto_compact_token_limit"])
        self.assertEqual("810000 on a 1000000 window", codex_local.DEFAULT_CONFIG_PROFILE["compact_policy"])
        self.assertEqual("xhigh", codex_local.DEFAULT_CONFIG["model_reasoning_effort"])
        self.assertEqual("gpt-5.5 + xhigh + never", codex_local.DEFAULT_CONFIG_PROFILE["current_combo"])
        self.assertEqual("current_default_choice", codex_local.DEFAULT_CONFIG_PROFILE["current_combo_status"])

    def test_auth_profiles_are_sanitized_for_read_only_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(
                home / "auth.json",
                account_id="account-a",
                email="sciman.top@gmail.com",
                name="sci man",
                plan_type="prolite",
                subscription_active_start="2026-04-01T00:00:00+00:00",
                subscription_active_until="2026-05-01T00:00:00+00:00",
                subscription_last_checked="2026-04-30T00:00:00.123456+00:00",
                id_token_exp=1_777_600_000,
                access_token_exp=1_777_603_600,
            )
            _write_auth(home / "auth1.json", account_id="account-b")

            profiles = codex_local.list_auth_profiles(home)
            payload = [profile.to_dict() for profile in profiles]
            status = codex_local.codex_status(home)

            self.assertEqual(["auth", "auth1"], [profile["name"] for profile in payload])
            self.assertTrue(payload[0]["active"])
            self.assertEqual("sciman.top@gmail.com", payload[0]["email"])
            self.assertEqual("sciman.top@gmail.com", payload[0]["account_label"])
            self.assertEqual("prolite", payload[0]["plan_type"])
            self.assertEqual("2026-04-01T00:00:00Z", payload[0]["subscription_active_start"])
            self.assertEqual("2026-05-01T00:00:00Z", payload[0]["subscription_active_until"])
            self.assertEqual("2026-04-30T00:00:00Z", payload[0]["subscription_last_checked"])
            self.assertEqual("2026-05-01T01:46:40Z", payload[0]["id_token_expires_at"])
            self.assertEqual("2026-05-01T02:46:40Z", payload[0]["access_token_expires_at"])
            self.assertEqual("auth", status["active_account"]["name"])
            self.assertEqual("sciman.top@gmail.com", status["active_account"]["email"])
            rendered = json.dumps(payload).lower()
            self.assertNotIn('"id_token":', rendered)
            self.assertNotIn('"access_token":', rendered)
            self.assertNotIn('"refresh_token":', rendered)

    def test_status_deduplicates_auth_json_mirror_from_same_saved_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="account-a", email="same@example.com", plan_type="team")
            (home / "auth3-2.json").write_text((home / "auth.json").read_text(encoding="utf-8"), encoding="utf-8")
            _write_auth(home / "auth1.json", account_id="account-b", email="other@example.com", plan_type="prolite")

            status = codex_local.codex_status(home)
            names = [account["name"] for account in status["accounts"]]

            self.assertEqual(["auth3-2", "auth1"], names)
            self.assertEqual("auth3-2", status["active_account"]["name"])
            self.assertTrue(status["accounts"][0]["active"])

    def test_status_reports_drifted_named_snapshot_for_active_auth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(
                home / "auth.json",
                account_id="account-a",
                email="same@example.com",
                plan_type="team",
                last_refresh="2026-05-02T03:00:00Z",
            )
            _write_auth(
                home / "auth2.json",
                account_id="account-a",
                email="same@example.com",
                plan_type="team",
                last_refresh="2026-04-29T21:01:17Z",
            )

            status = codex_local.codex_status(home)

            self.assertEqual("drifted", status["snapshot_status"]["status"])
            self.assertEqual("auth2", status["snapshot_status"]["profile_name"])
            self.assertEqual("drifted", status["active_account"]["snapshot_status"]["status"])
            self.assertEqual(["auth"], [account["name"] for account in status["accounts"]])

    def test_codex_local_has_no_auth_mutation_entrypoints(self) -> None:
        removed_entrypoints = [
            "switch_auth_profile",
            "save_api_auth_profile",
            "sync_active_auth_snapshot",
            "save_active_auth_snapshot",
            "delete_auth_profile",
            "import_cockpit_codex_accounts",
            "import_codex_accounts_from_payload",
            "install_account_switcher",
            "project_codex_auth_config",
            "persist_api_auth_profile_to_cockpit",
            "ensure_active_auth_snapshot",
        ]

        for name in removed_entrypoints:
            with self.subTest(name=name):
                self.assertFalse(hasattr(codex_local, name))

    def test_codex_status_prefers_switchable_api_duplicate_over_legacy_auto_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="oauth-account")
            (home / "config.toml").write_text('model_provider = "openai"\nforced_login_method = "chatgpt"\n', encoding="utf-8")
            profiles = home / "auth-profiles"
            profiles.mkdir()
            api_key = "sk-relay-secret"
            (profiles / "auto-fdb75e04ea.json").write_text(
                json.dumps({"auth_mode": "apikey", "OPENAI_API_KEY": api_key}),
                encoding="utf-8",
            )
            (profiles / "cockpit-api-35.213.82.91.json").write_text(
                json.dumps(
                    {
                        "auth_mode": "apikey",
                        "OPENAI_API_KEY": api_key,
                        "api_base_url": "http://35.213.82.91:8003/v1",
                        "base_url": "http://35.213.82.91:8003/v1",
                    }
                ),
                encoding="utf-8",
            )

            status = codex_local.codex_status(home)
            api_accounts = [account for account in status["accounts"] if account["auth_mode"] == "apikey"]

            self.assertEqual(1, len(api_accounts))
            self.assertEqual("cockpit-api-35.213.82.91", api_accounts[0]["name"])
            self.assertEqual("35.213.82.91", api_accounts[0]["account_label"])
            self.assertEqual("http://35.213.82.91:8003/v1", api_accounts[0]["api_base_url"])
            self.assertTrue(api_accounts[0]["switchable"])
            self.assertEqual(2, api_accounts[0]["duplicate_count"])

    def test_codex_status_collapses_oauth_profiles_by_email_across_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="active-account", email="active@example.com")
            _write_auth(
                home / "auth1.json",
                account_id="legacy-account-id",
                last_refresh="2026-05-01T00:00:00Z",
                email="sciman.top@gmail.com",
                plan_type="plus",
            )
            profiles = home / "auth-profiles"
            profiles.mkdir()
            _write_auth(
                profiles / "cockpit-sciman.top-gmail.com.json",
                account_id="codex_cockpit_account_id",
                last_refresh="2026-05-06T00:00:00Z",
                email="sciman.top@gmail.com",
                plan_type="plus",
            )

            status = codex_local.codex_status(home)
            matching = [account for account in status["accounts"] if account["email"] == "sciman.top@gmail.com"]

            self.assertEqual(1, len(matching))
            self.assertEqual("cockpit-sciman.top-gmail.com", matching[0]["name"])
            self.assertEqual(2, matching[0]["duplicate_count"])
            self.assertEqual(["auth1"], matching[0]["hidden_duplicate_names"])

    def test_config_health_reports_recommended_defaults_without_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            (home / "config.toml").write_text(
                "\n".join(
                    [
                        'cli_auth_credentials_store = "file"',
                        'model = "gpt-5.3-codex"',
                        'model_reasoning_effort = "xhigh"',
                        'model_verbosity = "medium"',
                        "model_context_window = 1000000",
                        "model_auto_compact_token_limit = 810000",
                        'sandbox_mode = "workspace-write"',
                        'approval_policy = "never"',
                        'web_search = "cached"',
                        "check_for_update_on_startup = false",
                    ]
                ),
                encoding="utf-8",
            )

            health = codex_local.config_health(home)

            self.assertEqual("ok", health["status"])
            self.assertTrue(all(check["ok"] for check in health["checks"]))
            self.assertTrue(any(not check["matches_reference"] for check in health["advisory_checks"]))
            self.assertEqual([], health["secret_like_markers"])

    def test_startup_health_detects_and_remediates_startup_slow_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            (home / "plugins" / "cache" / "openai-bundled" / "chrome" / "0.1.7").mkdir(parents=True)
            (home / "log").mkdir()
            (home / "log" / "codex-tui.log").write_text(
                "\n".join(
                    [
                        "WARN startup remote plugin sync failed",
                        "WARN Request failed with status 403 Forbidden",
                        'WARN failed to load plugin: missing or invalid plugin.json plugin="chrome@openai-bundled"',
                    ]
                ),
                encoding="utf-8",
            )
            (home / "config.toml").write_text(
                "\n".join(
                    [
                        "check_for_update_on_startup = true",
                        '[plugins."chrome@openai-bundled"]',
                        "enabled = true",
                        "[mcp_servers.context7]",
                        'transport = "stdio"',
                        "[mcp_servers.filesystem]",
                        'transport = "stdio"',
                        "[mcp_servers.playwright]",
                        'transport = "stdio"',
                        "[mcp_servers.fetch]",
                        'transport = "stdio"',
                        "[mcp_servers.postgres]",
                        'transport = "stdio"',
                        'command = "pwsh"',
                        'args = ["-Command", "npx -y @modelcontextprotocol/server-postgres $conn"]',
                    ]
                ),
                encoding="utf-8",
            )

            health = codex_local.codex_startup_health(home)

            self.assertEqual("attention", health["status"])
            self.assertIn("startup_update_check_disabled", health["summary"])
            self.assertIn("invalid_chrome_plugin_disabled", health["summary"])
            self.assertIn("stdio_mcp_startup_surface", health["summary"])
            self.assertIn("postgres_mcp_connection_string_not_in_process_args", health["summary"])
            self.assertIn("recent_startup_log_failures", health["summary"])

    def test_context_window_probe_keeps_current_compact_policy_static(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            (home / "config.toml").write_text(
                "\n".join(
                    [
                        'model = "gpt-5.3-codex"',
                        "model_context_window = 1000000",
                        "model_auto_compact_token_limit = 810000",
                    ]
                ),
                encoding="utf-8",
            )

            probe = codex_local.context_window_probe(home)

            self.assertEqual("pass", probe["status"])
            self.assertEqual("keep_current", probe["recommendation"])
            self.assertEqual(1000000, probe["configured_context_window"])
            self.assertEqual(810000, probe["configured_auto_compact_token_limit"])
            self.assertEqual("not_run", probe["catalog_probe"]["status"])
            self.assertEqual([], probe["catalog_probes"])
            self.assertEqual("keep_current", probe["context_settings_decision"]["action"])
            self.assertEqual("config_only", probe["context_settings_decision"]["basis_status"])
            self.assertEqual("informational_only_refresh_before_changing_defaults", probe["external_reference"]["enforcement"])

    def test_context_window_probe_can_read_bundled_catalog_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            (home / "config.toml").write_text(
                "\n".join(
                    [
                        'model = "gpt-5.3-codex"',
                        "model_context_window = 1000000",
                        "model_auto_compact_token_limit = 810000",
                    ]
                ),
                encoding="utf-8",
            )
            catalog = json.dumps(
                {
                    "models": [
                        {
                            "slug": "gpt-5.3-codex",
                            "display_name": "GPT-5.3-Codex",
                            "context_window": 1000000,
                            "max_context_window": 1000000,
                            "effective_context_window_percent": 95,
                        }
                    ]
                }
            )
            completed = mock.Mock(returncode=0, stdout=catalog, stderr="")

            with (
                mock.patch("lib.codex_local.shutil.which", return_value="codex.cmd"),
                mock.patch("lib.codex_local.subprocess.run", return_value=completed),
            ):
                probe = codex_local.context_window_probe(home, run_codex=True)

            self.assertEqual("pass", probe["status"])
            self.assertEqual("pass", probe["catalog_probe"]["status"])
            self.assertEqual(1000000, probe["catalog_probe"]["model"]["context_window"])
            self.assertEqual("single_catalog", probe["context_settings_decision"]["basis_status"])
            self.assertEqual("codex_debug_models_bundled", probe["context_settings_decision"]["context_source"])
            self.assertTrue(all(check["status"] == "pass" for check in probe["checks"]))

    def test_context_window_probe_accepts_catalog_backed_host_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            (home / "config.toml").write_text(
                "\n".join(
                    [
                        'model = "gpt-5.5"',
                        "model_auto_compact_token_limit = 220000",
                    ]
                ),
                encoding="utf-8",
            )
            catalog = json.dumps(
                {
                    "models": [
                        {
                            "slug": "gpt-5.5",
                            "display_name": "GPT-5.5",
                            "context_window": 272000,
                            "max_context_window": 1000000,
                            "effective_context_window_percent": 95,
                        }
                    ]
                }
            )
            completed = mock.Mock(returncode=0, stdout=catalog, stderr="")

            with (
                mock.patch("lib.codex_local.shutil.which", return_value="codex.cmd"),
                mock.patch("lib.codex_local.subprocess.run", return_value=completed),
            ):
                probe = codex_local.context_window_probe(home, run_codex=True)

            self.assertEqual("pass", probe["status"])
            self.assertIsNone(probe["configured_context_window"])
            self.assertEqual(272000, probe["effective_context_window"])
            self.assertEqual(0.8088, probe["compact_ratio"])
            self.assertEqual("keep_host_default", probe["context_settings_decision"]["action"])
            self.assertEqual("keep_current", probe["recommendation"])

    def test_context_window_probe_preserves_explicit_early_compaction_after_catalog_growth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            (home / "config.toml").write_text(
                "\n".join(
                    [
                        'model = "gpt-5.6-sol"',
                        "model_auto_compact_token_limit = 220000",
                    ]
                ),
                encoding="utf-8",
            )
            catalog = json.dumps(
                {
                    "models": [
                        {
                            "slug": "gpt-5.6-sol",
                            "display_name": "GPT-5.6",
                            "context_window": 372000,
                            "max_context_window": 372000,
                            "effective_context_window_percent": 95,
                        }
                    ]
                }
            )
            completed = mock.Mock(returncode=0, stdout=catalog, stderr="")

            with (
                mock.patch("lib.codex_local.shutil.which", return_value="codex.cmd"),
                mock.patch("lib.codex_local.subprocess.run", return_value=completed),
            ):
                probe = codex_local.context_window_probe(home, run_codex=True)

            self.assertEqual("pass", probe["status"])
            self.assertEqual(372000, probe["effective_context_window"])
            self.assertEqual(0.5914, probe["compact_ratio"])
            self.assertEqual("keep_host_default", probe["context_settings_decision"]["action"])
            self.assertEqual("configured_early_threshold", probe["context_settings_decision"]["compact_source"])
            self.assertEqual("keep_current", probe["recommendation"])

    def test_context_window_probe_compares_bundled_and_refreshed_catalogs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            (home / "config.toml").write_text(
                "\n".join(
                    [
                        'model = "gpt-5.3-codex"',
                        "model_context_window = 1000000",
                        "model_auto_compact_token_limit = 810000",
                    ]
                ),
                encoding="utf-8",
            )
            catalog = json.dumps(
                {
                    "models": [
                        {
                            "slug": "gpt-5.3-codex",
                            "display_name": "GPT-5.3-Codex",
                            "context_window": 1000000,
                            "max_context_window": 1000000,
                        }
                    ]
                }
            )
            completed = mock.Mock(returncode=0, stdout=catalog, stderr="")

            with (
                mock.patch("lib.codex_local.shutil.which", return_value="codex.cmd"),
                mock.patch("lib.codex_local.subprocess.run", return_value=completed) as run_mock,
            ):
                probe = codex_local.context_window_probe(home, run_codex=True, probe_all_catalogs=True)

            self.assertEqual("pass", probe["status"])
            self.assertEqual(["bundled", "refreshed"], [item["catalog_mode"] for item in probe["catalog_probes"]])
            self.assertEqual(2, run_mock.call_count)
            self.assertEqual("catalog_consensus", probe["context_settings_decision"]["basis_status"])
            self.assertTrue(
                any(
                    check["check_id"] == "bundled_and_refreshed_catalogs_agree" and check["status"] == "pass"
                    for check in probe["checks"]
                )
            )

    def test_context_window_probe_surfaces_catalog_disagreement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            (home / "config.toml").write_text(
                "\n".join(
                    [
                        'model = "gpt-5.3-codex"',
                        "model_context_window = 1000000",
                        "model_auto_compact_token_limit = 810000",
                    ]
                ),
                encoding="utf-8",
            )
            bundled_catalog = json.dumps({"models": [{"slug": "gpt-5.3-codex", "context_window": 1000000, "max_context_window": 1000000}]})
            refreshed_catalog = json.dumps({"models": [{"slug": "gpt-5.3-codex", "context_window": 300000, "max_context_window": 300000}]})
            completed = [
                mock.Mock(returncode=0, stdout=bundled_catalog, stderr=""),
                mock.Mock(returncode=0, stdout=refreshed_catalog, stderr=""),
            ]

            with (
                mock.patch("lib.codex_local.shutil.which", return_value="codex.cmd"),
                mock.patch("lib.codex_local.subprocess.run", side_effect=completed),
            ):
                probe = codex_local.context_window_probe(home, run_codex=True, probe_all_catalogs=True)

            self.assertEqual("attention", probe["status"])
            self.assertEqual("manual_review", probe["context_settings_decision"]["action"])
            self.assertEqual("catalog_disagreement", probe["context_settings_decision"]["basis_status"])
            self.assertEqual("probe_before_changing_defaults", probe["recommendation"])

    def test_context_window_probe_can_run_exec_probe_with_config_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            (home / "config.toml").write_text(
                "\n".join(
                    [
                        'model = "gpt-5.3-codex"',
                        "model_context_window = 1000000",
                        "model_auto_compact_token_limit = 810000",
                    ]
                ),
                encoding="utf-8",
            )
            completed = mock.Mock(returncode=0, stdout='{"type":"agent_message","message":"ok"}\n', stderr="")

            with (
                mock.patch("lib.codex_local.shutil.which", return_value="codex.cmd"),
                mock.patch("lib.codex_local.subprocess.run", return_value=completed) as run_mock,
            ):
                probe = codex_local.context_window_probe(home, probe_exec=True)

            command = run_mock.call_args.args[0]
            self.assertEqual("pass", probe["status"])
            self.assertEqual("pass", probe["exec_probe"]["status"])
            self.assertIn("exec", command)
            self.assertIn("model_context_window=1000000", command)
            self.assertIn("model_auto_compact_token_limit=810000", command)
            self.assertTrue(probe["exec_probe"]["consumes_quota"])

    def test_status_includes_efficiency_first_core_principle_and_current_choice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="account-a")
            (home / "config.toml").write_text('model = "gpt-5.3-codex"', encoding="utf-8")

            status = codex_local.codex_status(home)

            self.assertEqual("efficiency_first", status["recommended_defaults"]["strategy"])
            self.assertEqual("综合效率优先", status["recommended_defaults"]["strategy_label"])
            self.assertEqual(
                ["少打扰", "自动连续执行", "节省 token / 成本", "保留必要解释", "高效率"],
                status["recommended_defaults"]["strategy_principles"],
            )
            self.assertEqual("gpt-5.5 + xhigh + never", status["recommended_defaults"]["current_combo"])
            self.assertEqual("current_default_choice", status["recommended_defaults"]["current_combo_status"])
            self.assertEqual("810000 on a 1000000 window", status["recommended_defaults"]["compact_policy"])
            self.assertIn("preserve the efficiency-first principle", status["recommended_defaults"]["change_rule"])

    def test_usage_is_read_from_recent_codex_rate_limit_log_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            connection = sqlite3.connect(home / "logs_2.sqlite")
            try:
                connection.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY, ts REAL, feedback_log_body TEXT)")
                connection.execute(
                    "INSERT INTO logs (id, ts, feedback_log_body) VALUES (1, 1777544937, ?)",
                    (
                        'websocket event: {"type":"codex.rate_limits","plan_type":"prolite",'
                        '"rate_limits":{"allowed":true,"limit_reached":false,'
                        '"primary":{"used_percent":1,"window_minutes":300,'
                        '"reset_after_seconds":123,"reset_at":1777562537},'
                        '"secondary":{"used_percent":3,"window_minutes":10080,'
                        '"reset_after_seconds":456,"reset_at":1778073182}}}',
                    ),
                )
                connection.commit()
            finally:
                connection.close()

            with mock.patch("lib.codex_local.time.time", return_value=1_777_544_000.0):
                usage = codex_local.codex_status(home)["usage"]

            self.assertEqual("codex_logs_2_sqlite", usage["source"])
            self.assertEqual("prolite", usage["plan_type"])
            self.assertEqual(["5h", "7d"], [item["window"] for item in usage["windows"]])
            self.assertEqual([100, 97], [item["remaining_percent"] for item in usage["windows"]])
            self.assertEqual("2026-04-30T10:28:57Z", usage["captured_at"])
            self.assertFalse(usage["freshness"]["is_stale"])

    def test_status_does_not_attach_unbound_sqlite_usage_to_active_account(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="account-a", email="active@example.com", plan_type="team")
            connection = sqlite3.connect(home / "logs_2.sqlite")
            try:
                connection.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY, ts REAL, feedback_log_body TEXT)")
                connection.execute(
                    "INSERT INTO logs (id, ts, feedback_log_body) VALUES (1, 0, ?)",
                    (
                        'websocket event: {"type":"codex.rate_limits","plan_type":"team",'
                        '"rate_limits":{"allowed":true,"limit_reached":false,'
                        '"primary":{"used_percent":42,"window_minutes":300,"reset_at":1777565161},'
                        '"secondary":{"used_percent":22,"window_minutes":10080,"reset_at":1778073532}}}',
                    ),
                )
                connection.commit()
            finally:
                connection.close()

            status = codex_local.codex_status(home)
            account = status["active_account"]

            self.assertIsNone(account.get("usage_snapshot"))
            self.assertEqual("codex_logs_2_sqlite", status["usage"]["source"])
            self.assertEqual("global_unbound_log_event", status["usage"]["account_binding"])

    def test_status_recomputes_cached_usage_freshness_before_display(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            account_hash = codex_local._short_string_hash("account-a")
            _write_auth(home / "auth.json", account_id="account-a", email="active@example.com", plan_type="team")
            (home / "account-usage-cache.json").write_text(
                json.dumps(
                    {
                        account_hash: {
                            "account_hash": account_hash,
                            "account_label": "active@example.com",
                            "plan_type": "team",
                            "source": "codex_sessions_jsonl",
                            "account_binding": "active_account_after_online_refresh",
                            "captured_at": "2026-05-02T04:55:00Z",
                            "freshness": {
                                "captured_at": "2026-05-02T04:55:00Z",
                                "age_seconds": 0,
                                "stale_after_seconds": 300,
                                "is_stale": False,
                            },
                            "windows": [
                                {"window": "5h", "window_minutes": 300, "remaining_percent": 58, "remaining": "58%", "reset_at": 1777565161},
                                {"window": "7d", "window_minutes": 10080, "remaining_percent": 78, "remaining": "78%", "reset_at": 1778073532},
                            ],
                        }
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch("lib.codex_local.time.time", return_value=1_778_000_000.0):
                status = codex_local.codex_status(home)

            account = status["active_account"]
            self.assertIsInstance(account.get("usage_snapshot"), dict)
            self.assertTrue(account["usage_snapshot"]["freshness"]["is_stale"])
            self.assertGreater(account["usage_snapshot"]["freshness"]["age_seconds"], 300)

    def test_status_does_not_use_unbound_sqlite_usage_plan_for_account_display(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="account-a", email="active@example.com", plan_type="prolite")
            connection = sqlite3.connect(home / "logs_2.sqlite")
            try:
                connection.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY, ts REAL, feedback_log_body TEXT)")
                connection.execute(
                    "INSERT INTO logs (id, ts, feedback_log_body) VALUES (1, 0, ?)",
                    (
                        'websocket event: {"type":"codex.rate_limits","plan_type":"plus",'
                        '"rate_limits":{"allowed":true,"limit_reached":false,'
                        '"primary":{"used_percent":42,"window_minutes":300,"reset_at":1777565161},'
                        '"secondary":{"used_percent":22,"window_minutes":10080,"reset_at":1778073532}}}',
                    ),
                )
                connection.commit()
            finally:
                connection.close()

            status = codex_local.codex_status(home)

            self.assertEqual("plus", status["usage"]["plan_type"])
            self.assertEqual("global_unbound_log_event", status["usage"]["account_binding"])
            self.assertEqual("prolite", status["active_account"]["plan_type"])
            self.assertEqual("auth_token", status["active_account"]["plan_source"])
            self.assertIsNone(status["active_account"].get("usage_snapshot"))

    def test_status_ignores_local_account_facts_for_plan_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="account-a", email="active@example.com", plan_type="plus")
            (home / "account-usage-cache.json").write_text(
                json.dumps(
                    {
                        codex_local._short_string_hash("account-a"): {
                            "account_hash": codex_local._short_string_hash("account-a"),
                            "account_label": "active@example.com",
                            "plan_type": "plus",
                            "source": "codex_sessions_jsonl",
                        }
                    }
                ),
                encoding="utf-8",
            )
            (home / "account-facts.json").write_text(
                json.dumps(
                    {
                        "accounts": {
                            "active@example.com": {
                                "plan_type": "go",
                                "source": "local_operator_asserted",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            status = codex_local.codex_status(home)

            self.assertEqual("plus", status["active_account"]["plan_type"])
            self.assertEqual("auth_token", status["active_account"]["plan_source"])
            self.assertEqual("disabled_ignored", status["account_facts"]["status"])
            self.assertNotIn("plan_conflicts", status["active_account"])

    def test_status_marks_official_app_persisted_account_separately_from_cli_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            app_root = home / "official-app" / "Local Storage" / "leveldb"
            app_root.mkdir(parents=True, exist_ok=True)
            _write_auth(home / "auth.json", account_id="account-top", email="sciman.top@gmail.com", plan_type="prolite")
            _write_auth(home / "auth3-2.json", account_id="account-phys", email="sciman.phys@gmail.com", plan_type="team")
            (app_root / "000001.ldb").write_bytes(b"official app state account-phys")

            with mock.patch("lib.codex_local._official_codex_app_storage_root", return_value=home / "official-app"):
                status = codex_local.codex_status(home)

            self.assertEqual("auth", status["active_account"]["name"])
            self.assertEqual("sciman.top@gmail.com", status["active_account"]["email"])
            self.assertEqual("ok", status["official_app_account"]["status"])
            self.assertEqual("auth3-2", status["official_app_account"]["name"])
            self.assertEqual("sciman.phys@gmail.com", status["official_app_account"]["email"])
            app_persisted = next(account for account in status["accounts"] if account["name"] == "auth3-2")
            cli_active = next(account for account in status["accounts"] if account["active"])
            self.assertTrue(app_persisted["official_app_current"])
            self.assertFalse(cli_active["official_app_current"])

    def test_status_reports_official_app_ambiguity_limitation_when_latest_storage_contains_multiple_accounts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            app_root = home / "official-app" / "Local Storage" / "leveldb"
            app_root.mkdir(parents=True, exist_ok=True)
            _write_auth(home / "auth.json", account_id="account-top", email="sciman.top@gmail.com", plan_type="prolite")
            _write_auth(home / "auth3-2.json", account_id="account-phys", email="sciman.phys@gmail.com", plan_type="team")
            (app_root / "000001.ldb").write_bytes(b"official app state account-top account-phys")

            with mock.patch("lib.codex_local._official_codex_app_storage_root", return_value=home / "official-app"):
                status = codex_local.codex_status(home)

            self.assertEqual("ambiguous", status["official_app_account"]["status"])
            self.assertIn("limitation", status["official_app_account"])

    def test_list_auth_profiles_accepts_top_level_account_id_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            payload = {
                "auth_mode": "chatgpt",
                "account_id": "top-level-account",
                "email": "top@example.com",
                "name": "Top Level",
                "plan_type": "plus",
            }
            (home / "auth.json").write_text(json.dumps(payload), encoding="utf-8")

            profile = codex_local.list_auth_profiles(home)[0]

            self.assertEqual("top-level-account", profile.account_id)

    def test_online_refresh_prefers_latest_session_snapshot_and_reports_refresh_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="account-a", email="sciman.top@gmail.com", plan_type="prolite")
            sessions_dir = home / "sessions" / "2026" / "04" / "30"
            sessions_dir.mkdir(parents=True, exist_ok=True)
            rollout = sessions_dir / "rollout-2026-04-30T18-55-16-test.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps({"type": "thread.started", "thread_id": "thread_test"}),
                        json.dumps(
                            {
                                "timestamp": "2026-04-30T10:55:25.016Z",
                                "type": "event_msg",
                                "payload": {
                                    "type": "token_count",
                                    "rate_limits": {
                                        "plan_type": "prolite",
                                        "primary": {"used_percent": 5, "window_minutes": 300, "resets_at": 1777562537},
                                        "secondary": {"used_percent": 4, "window_minutes": 10080, "resets_at": 1777975637},
                                    },
                                },
                            }
                        ),
                    ]
                ),
                encoding="utf-8",
            )
            before = rollout.stat().st_mtime

            completed = mock.Mock(returncode=0, stdout="", stderr="")
            with (
                mock.patch("lib.codex_local.shutil.which", return_value="codex.cmd"),
                mock.patch("lib.codex_local.subprocess.run", return_value=completed),
                mock.patch("lib.codex_local.time.time", return_value=before + 0.5),
            ):
                status = codex_local.codex_status(home, refresh_online=True)

            self.assertEqual("ok", status["usage_refresh"]["status"])
            self.assertEqual("codex_sessions_jsonl", status["usage"]["source"])
            self.assertEqual([95, 96], [item["remaining_percent"] for item in status["usage"]["windows"]])
            self.assertEqual("prolite", status["usage"]["plan_type"])

    def test_online_refresh_falls_back_to_local_snapshot_when_exec_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            connection = sqlite3.connect(home / "logs_2.sqlite")
            try:
                connection.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY, ts REAL, feedback_log_body TEXT)")
                connection.execute(
                    "INSERT INTO logs (id, ts, feedback_log_body) VALUES (1, 0, ?)",
                    (
                        'websocket event: {"type":"codex.rate_limits","plan_type":"prolite",'
                        '"rate_limits":{"allowed":true,"limit_reached":false,'
                        '"primary":{"used_percent":1,"window_minutes":300,"reset_at":1777562537},'
                        '"secondary":{"used_percent":3,"window_minutes":10080,"reset_at":1778073182}}}',
                    ),
                )
                connection.commit()
            finally:
                connection.close()

            completed = mock.Mock(returncode=1, stdout="", stderr="network unavailable")
            with (
                mock.patch("lib.codex_local.shutil.which", return_value="codex.cmd"),
                mock.patch("lib.codex_local.subprocess.run", return_value=completed),
                mock.patch("lib.codex_local.time.time", return_value=1_777_562_000.0),
            ):
                status = codex_local.codex_status(home, refresh_online=True)

            self.assertEqual("fallback", status["usage_refresh"]["status"])
            self.assertIn("network unavailable", status["usage_refresh"]["error"])
            self.assertEqual("codex_logs_2_sqlite", status["usage"]["source"])

    def test_status_refreshes_online_when_local_usage_snapshot_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            account_hash = codex_local._short_string_hash("account-a")
            _write_auth(home / "auth.json", account_id="account-a", email="active@example.com", plan_type="prolite")
            (home / "account-usage-cache.json").write_text(
                json.dumps(
                    {
                        account_hash: {
                            "account_hash": account_hash,
                            "account_label": "active@example.com",
                            "plan_type": "prolite",
                            "source": "codex_sessions_jsonl",
                            "account_binding": "active_account_after_online_refresh",
                            "captured_at": "2026-05-02T04:55:00Z",
                            "windows": [
                                {"window": "5h", "window_minutes": 300, "remaining_percent": 40, "remaining": "40%", "reset_at": 1777562537}
                            ],
                        }
                    }
                ),
                encoding="utf-8",
            )
            connection = sqlite3.connect(home / "logs_2.sqlite")
            try:
                connection.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY, ts REAL, feedback_log_body TEXT)")
                connection.execute(
                    "INSERT INTO logs (id, ts, feedback_log_body) VALUES (1, 0, ?)",
                    (
                        'websocket event: {"type":"codex.rate_limits","plan_type":"prolite",'
                        '"rate_limits":{"allowed":true,"limit_reached":false,'
                        '"primary":{"used_percent":60,"window_minutes":300,"reset_at":1777562537},'
                        '"secondary":{"used_percent":30,"window_minutes":10080,"reset_at":1778073182}}}',
                    ),
                )
                connection.commit()
            finally:
                connection.close()

            with mock.patch("lib.codex_local._refresh_codex_usage_online") as refresh_mock:
                refresh_mock.return_value = (
                    {
                        "source": "codex_exec_stdout",
                        "plan_type": "prolite",
                        "windows": [
                            {"window": "5h", "window_minutes": 300, "remaining_percent": 99, "remaining": "99%", "reset_at": 1777562537}
                        ],
                        "account_binding": "online_refresh_current_auth",
                        "captured_at": "2026-05-02T04:55:00Z",
                        "freshness": {
                            "captured_at": "2026-05-02T04:55:00Z",
                            "age_seconds": 0,
                            "stale_after_seconds": 300,
                            "is_stale": False,
                        },
                    },
                    {"attempted": True, "status": "ok", "mode": "online_exec", "consumes_quota": True},
                )
                with mock.patch("lib.codex_local.time.time", return_value=1_777_786_000.0):
                    status = codex_local.codex_status(home, refresh_if_stale=True)

            refresh_mock.assert_called_once()
            self.assertEqual("ok", status["usage_refresh"]["status"])
            self.assertEqual("codex_exec_stdout", status["usage"]["source"])
            self.assertEqual("active_account_after_online_refresh", status["active_account"]["usage_snapshot"]["account_binding"])
            self.assertEqual([99], [item["remaining_percent"] for item in status["active_account"]["usage_snapshot"]["windows"]])


if __name__ == "__main__":
    unittest.main()
