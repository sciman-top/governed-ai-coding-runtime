import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_SRC = ROOT / "scripts"
if str(SCRIPTS_SRC) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_SRC))

from lib import claude_local


def _write_settings(path: Path, *, token_key: str = "ANTHROPIC_AUTH_TOKEN") -> None:
    path.write_text(
        json.dumps(
            {
                "env": {
                    token_key: "secret-value",
                    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
                },
                "permissions": {"allow": ["Read"], "deny": []},
                "model": "opus[1m]",
            }
        ),
        encoding="utf-8",
    )


class ClaudeLocalTests(unittest.TestCase):
    def test_status_redacts_settings_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")
            settings = json.loads((home / "settings.json").read_text(encoding="utf-8"))
            settings["env"]["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = "8192"
            (home / "settings.json").write_text(json.dumps(settings), encoding="utf-8")

            claude_local.write_default_provider_profiles(home)
            summary = claude_local.settings_summary(home)
            rendered = json.dumps(summary)

            self.assertIn("<redacted>", rendered)
            self.assertNotIn("secret-value", rendered)
            self.assertIn("8192", rendered)

    def test_optimize_switches_bigmodel_without_leaking_token_to_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")
            settings = json.loads((home / "settings.json").read_text(encoding="utf-8"))
            settings["env"]["ANTHROPIC_API_KEY"] = "deepseek-secret"
            (home / "settings.json").write_text(json.dumps(settings), encoding="utf-8")

            result = claude_local.optimize_claude_local(home, provider_name="bigmodel-glm", apply=True, install_switcher=False)
            settings = json.loads((home / "settings.json").read_text(encoding="utf-8"))
            profiles = json.loads((home / "provider-profiles.json").read_text(encoding="utf-8"))

            self.assertEqual("ok", result["status"])
            self.assertEqual("opus", settings["model"])
            self.assertEqual("dontAsk", settings["permissions"]["defaultMode"])
            self.assertEqual("disable", settings["permissions"]["disableBypassPermissionsMode"])
            self.assertEqual("glm-5.1", settings["env"]["ANTHROPIC_DEFAULT_OPUS_MODEL"])
            self.assertEqual("secret-value", settings["env"]["ANTHROPIC_AUTH_TOKEN"])
            self.assertEqual("deepseek-secret", settings["env"]["ANTHROPIC_API_KEY"])
            self.assertEqual("100000", settings["env"]["CLAUDE_CODE_AUTO_COMPACT_WINDOW"])
            self.assertEqual("high", settings["env"]["CLAUDE_CODE_EFFORT_LEVEL"])
            self.assertNotIn("secret-value", json.dumps(profiles))
            self.assertNotIn("deepseek-secret", json.dumps(profiles))
            self.assertEqual("ok", claude_local.config_health(home)["status"])

    def test_optimize_dry_run_does_not_write_provider_profiles_or_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            settings_path = home / "settings.json"
            _write_settings(settings_path)
            original_settings = settings_path.read_text(encoding="utf-8")

            result = claude_local.optimize_claude_local(home, provider_name="bigmodel-glm", apply=False, install_switcher=False)

            self.assertEqual("dry_run", result["status"])
            self.assertEqual("dry_run", result["provider_profiles"]["status"])
            self.assertFalse((home / "provider-profiles.json").exists())
            self.assertEqual(original_settings, settings_path.read_text(encoding="utf-8"))

    def test_switch_requires_matching_provider_credential(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")
            claude_local.write_default_provider_profiles(home)

            result = claude_local.switch_provider("deepseek-v4", home)

            self.assertEqual("error", result["status"])
            self.assertIn("ANTHROPIC_API_KEY", result["error"])

    def test_delete_provider_profile_backs_up_and_removes_inactive_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")
            claude_local.write_default_provider_profiles(home, active="bigmodel-glm")

            result = claude_local.delete_provider_profile("deepseek-v4", home)
            payload = json.loads((home / "provider-profiles.json").read_text(encoding="utf-8"))
            names = [profile["name"] for profile in payload["profiles"]]

            self.assertEqual("ok", result["status"])
            self.assertTrue(result["changed"])
            self.assertTrue(Path(result["backup_path"]).exists())
            self.assertNotIn("deepseek-v4", names)
            self.assertEqual("bigmodel-glm", payload["active"])
            self.assertEqual("secret-value", json.loads((home / "settings.json").read_text(encoding="utf-8"))["env"]["ANTHROPIC_AUTH_TOKEN"])

    def test_delete_provider_profile_refuses_active_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")
            claude_local.write_default_provider_profiles(home, active="bigmodel-glm")

            result = claude_local.delete_provider_profile("bigmodel-glm", home)

            self.assertEqual("error", result["status"])
            self.assertIn("active", result["error"])
            names = [profile.name for profile in claude_local.load_provider_profiles(home)]
            self.assertIn("bigmodel-glm", names)

    def test_delete_provider_profile_survives_default_profile_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")
            claude_local.write_default_provider_profiles(home, active="bigmodel-glm")
            claude_local.delete_provider_profile("deepseek-v4", home)

            refresh = claude_local.write_default_provider_profiles(home)
            payload = json.loads((home / "provider-profiles.json").read_text(encoding="utf-8"))
            names = [profile["name"] for profile in payload["profiles"]]

            self.assertEqual("ok", refresh["status"])
            self.assertNotIn("deepseek-v4", names)
            self.assertIn("deepseek-v4", payload["retired_profiles"])
            self.assertNotIn("deepseek-v4", [profile.name for profile in claude_local.load_provider_profiles(home)])

    def test_explicit_active_provider_restores_retired_default_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")
            claude_local.write_default_provider_profiles(home, active="bigmodel-glm")
            claude_local.delete_provider_profile("deepseek-v4", home)

            refresh = claude_local.write_default_provider_profiles(home, active="deepseek-v4")
            payload = json.loads((home / "provider-profiles.json").read_text(encoding="utf-8"))
            names = [profile["name"] for profile in payload["profiles"]]

            self.assertEqual("ok", refresh["status"])
            self.assertIn("deepseek-v4", names)
            self.assertNotIn("deepseek-v4", payload["retired_profiles"])
            self.assertEqual("deepseek-v4", payload["active"])

    def test_cli_delete_dry_run_does_not_write_default_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")
            env = dict(os.environ)
            env["CLAUDE_CONFIG_DIR"] = str(home)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "claude-provider.py"),
                    "delete",
                    "deepseek-v4",
                    "--dry-run",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
                env=env,
            )

            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("ok", payload["status"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse((home / "provider-profiles.json").exists())


if __name__ == "__main__":
    unittest.main()
