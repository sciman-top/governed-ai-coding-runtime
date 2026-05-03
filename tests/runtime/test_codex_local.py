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

from lib import codex_local


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
    def test_auth_profiles_are_sanitized_and_switchable(self) -> None:
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

            result = codex_local.switch_auth_profile("auth1", home)
            self.assertEqual("ok", result["status"])
            self.assertTrue(result["changed"])
            self.assertTrue((home / "auth-backups").exists())
            self.assertEqual("auth", codex_local.active_auth_status(home)["active_profile"]["name"])

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

    def test_sync_active_snapshot_overwrites_named_profile_and_keeps_backup(self) -> None:
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

            result = codex_local.sync_active_auth_snapshot(home, target_name="auth2")

            self.assertEqual("ok", result["status"])
            self.assertTrue(result["changed"])
            self.assertTrue((home / "auth-backups").exists())
            self.assertEqual(
                (home / "auth.json").read_text(encoding="utf-8"),
                (home / "auth2.json").read_text(encoding="utf-8"),
            )
            self.assertEqual("synced", codex_local.codex_status(home)["snapshot_status"]["status"])

    def test_delete_auth_profile_backs_up_and_removes_inactive_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="account-a")
            _write_auth(home / "auth1.json", account_id="account-b")

            result = codex_local.delete_auth_profile("auth1", home)

            self.assertEqual("ok", result["status"])
            self.assertTrue(result["changed"])
            self.assertFalse((home / "auth1.json").exists())
            self.assertTrue(Path(result["backup_path"]).exists())
            self.assertEqual("auth1", result["deleted_profile"]["name"])

    def test_delete_auth_profile_refuses_current_auth_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="account-a")
            (home / "auth3-2.json").write_text((home / "auth.json").read_text(encoding="utf-8"), encoding="utf-8")

            active_result = codex_local.delete_auth_profile("auth", home)
            mirrored_result = codex_local.delete_auth_profile("auth3-2", home)

            self.assertEqual("error", active_result["status"])
            self.assertEqual("error", mirrored_result["status"])
            self.assertTrue((home / "auth.json").exists())
            self.assertTrue((home / "auth3-2.json").exists())

    def test_config_health_reports_recommended_defaults_without_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            (home / "config.toml").write_text(
                "\n".join(
                    [
                        'cli_auth_credentials_store = "file"',
                        'model = "gpt-5.5"',
                        'model_reasoning_effort = "medium"',
                        'model_verbosity = "medium"',
                        "model_context_window = 272000",
                        "model_auto_compact_token_limit = 220000",
                        'sandbox_mode = "workspace-write"',
                        'approval_policy = "never"',
                        'web_search = "cached"',
                    ]
                ),
                encoding="utf-8",
            )

            health = codex_local.config_health(home)

            self.assertEqual("ok", health["status"])
            self.assertTrue(all(check["ok"] for check in health["checks"]))
            self.assertEqual([], health["secret_like_markers"])

    def test_status_includes_efficiency_first_core_principle_and_current_choice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="account-a")
            (home / "config.toml").write_text('model = "gpt-5.5"', encoding="utf-8")

            status = codex_local.codex_status(home)

            self.assertEqual("efficiency_first", status["recommended_defaults"]["strategy"])
            self.assertEqual("综合效率优先", status["recommended_defaults"]["strategy_label"])
            self.assertEqual(
                ["少打扰", "自动连续执行", "节省 token / 成本", "保留必要解释", "高效率"],
                status["recommended_defaults"]["strategy_principles"],
            )
            self.assertEqual("gpt-5.5 + medium + never", status["recommended_defaults"]["current_combo"])
            self.assertEqual("current_temporary_choice", status["recommended_defaults"]["current_combo_status"])
            self.assertEqual("220000 on a 272000 window", status["recommended_defaults"]["compact_policy"])
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

    def test_status_attaches_cached_usage_snapshot_to_active_account(self) -> None:
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

            self.assertIsInstance(account.get("usage_snapshot"), dict)
            self.assertEqual("team", account["usage_snapshot"]["plan_type"])
            self.assertEqual([58, 78], [item["remaining_percent"] for item in account["usage_snapshot"]["windows"]])

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
                        "windows": [],
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


if __name__ == "__main__":
    unittest.main()
