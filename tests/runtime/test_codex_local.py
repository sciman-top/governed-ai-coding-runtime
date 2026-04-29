import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_SRC = ROOT / "scripts"
if str(SCRIPTS_SRC) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_SRC))

from lib import codex_local


def _write_auth(path: Path, *, account_id: str, last_refresh: str = "2026-04-30T00:00:00Z") -> None:
    path.write_text(
        json.dumps(
            {
                "auth_mode": "chatgpt",
                "last_refresh": last_refresh,
                "tokens": {
                    "account_id": account_id,
                },
            }
        ),
        encoding="utf-8",
    )


class CodexLocalTests(unittest.TestCase):
    def test_auth_profiles_are_sanitized_and_switchable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_auth(home / "auth.json", account_id="account-a")
            _write_auth(home / "auth1.json", account_id="account-b")

            profiles = codex_local.list_auth_profiles(home)
            payload = [profile.to_dict() for profile in profiles]

            self.assertEqual(["auth", "auth1"], [profile["name"] for profile in payload])
            self.assertTrue(payload[0]["active"])
            self.assertNotIn("token", json.dumps(payload).lower())

            result = codex_local.switch_auth_profile("auth1", home)
            self.assertEqual("ok", result["status"])
            self.assertTrue(result["changed"])
            self.assertTrue((home / "auth-backups").exists())
            self.assertEqual("auth", codex_local.active_auth_status(home)["active_profile"]["name"])

    def test_config_health_reports_recommended_defaults_without_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            (home / "config.toml").write_text(
                "\n".join(
                    [
                        'model = "gpt-5.4"',
                        'model_reasoning_effort = "medium"',
                        'model_verbosity = "medium"',
                        "model_context_window = 128000",
                        "model_auto_compact_token_limit = 96000",
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


if __name__ == "__main__":
    unittest.main()
