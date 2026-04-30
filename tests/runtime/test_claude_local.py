import json
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

    def test_switch_requires_matching_provider_credential(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")
            claude_local.write_default_provider_profiles(home)

            result = claude_local.switch_provider("deepseek-v4", home)

            self.assertEqual("error", result["status"])
            self.assertIn("ANTHROPIC_API_KEY", result["error"])


if __name__ == "__main__":
    unittest.main()
