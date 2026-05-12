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

            summary = claude_local.settings_summary(home)
            rendered = json.dumps(summary)

            self.assertIn("<redacted>", rendered)
            self.assertNotIn("secret-value", rendered)
            self.assertIn("8192", rendered)

    def test_provider_management_entrypoints_are_disabled_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            settings_path = home / "settings.json"
            _write_settings(settings_path)
            original_settings = settings_path.read_text(encoding="utf-8")

            calls = [
                claude_local.write_default_provider_profiles(home),
                claude_local.switch_provider("deepseek-v4", home),
                claude_local.delete_provider_profile("deepseek-v4", home),
                claude_local.optimize_claude_local(home, provider_name="bigmodel-glm", apply=True, install_switcher=True),
                claude_local.install_provider_switcher(home),
            ]

            for result in calls:
                self.assertEqual("error", result["status"])
                self.assertEqual("project_managed_claude_switching_disabled", result["error"])
                self.assertEqual("CC Switch", result["owner"])
                self.assertFalse(result["changed"])
            self.assertEqual(original_settings, settings_path.read_text(encoding="utf-8"))
            self.assertFalse((home / "provider-profiles.json").exists())
            self.assertFalse((home / "scripts" / "Switch-ClaudeProvider.ps1").exists())

    def test_dry_run_switch_is_also_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")

            result = claude_local.switch_provider("deepseek-v4", home, dry_run=True)

            self.assertEqual("error", result["status"])
            self.assertEqual("project_managed_claude_switching_disabled", result["error"])
            self.assertTrue(result["dry_run"])
            self.assertFalse((home / "provider-profiles.json").exists())

    def test_status_and_list_do_not_write_default_provider_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")

            status = claude_local.claude_status(home)
            profiles = claude_local.load_provider_profiles(home)

            self.assertIn("providers", status)
            self.assertGreaterEqual(len(profiles), 1)
            self.assertFalse((home / "provider-profiles.json").exists())

    def test_session_continuity_status_reports_resume_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")
            project_dir = home / "projects" / "D--CODE--repo"
            project_dir.mkdir(parents=True)
            (project_dir / "session-1.jsonl").write_text("{}\n", encoding="utf-8")
            (home / "history.jsonl").write_text("{}\n", encoding="utf-8")

            result = claude_local.session_continuity_status(home)

            self.assertEqual("ok", result["status"])
            self.assertEqual("preserve_claude_home", result["provider_switch_policy"])
            self.assertEqual(1, result["paths"]["projects"]["jsonl_count"])
            self.assertIn("claude --resume", result["resume_commands"])

    def test_cli_switch_returns_boundary_error_and_does_not_write_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            _write_settings(home / "settings.json")
            env = dict(os.environ)
            env["CLAUDE_CONFIG_DIR"] = str(home)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "claude-provider.py"),
                    "switch",
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

            self.assertEqual(2, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("project_managed_claude_switching_disabled", payload["error"])
            self.assertFalse((home / "provider-profiles.json").exists())


if __name__ == "__main__":
    unittest.main()
