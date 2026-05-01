import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PolicyToolCredentialAuditTests(unittest.TestCase):
    def test_builder_generates_fail_closed_report(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/build-policy-tool-credential-audit.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["summary"]["unknown_tool_count"], 0)
        self.assertGreaterEqual(payload["summary"]["audited_tool_count"], 4)
        self.assertGreaterEqual(payload["summary"]["override_surface_count"], 2)
        self.assertIn(payload["local_agent_config_audit"]["status"], {"pass", "platform_na"})

    def test_verifier_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-policy-tool-credential-audit.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["invalid_reasons"])

    def test_builder_audits_local_agent_config_without_exposing_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            codex = home / ".codex"
            claude = home / ".claude"
            gemini = home / ".gemini"
            (codex / "rules").mkdir(parents=True)
            claude.mkdir()
            gemini.mkdir()

            (codex / "config.toml").write_text(
                '\n'.join(
                    [
                        'approval_policy = "never"',
                        '[analytics]',
                        'enabled = false',
                        '[mcp_servers.github]',
                        'transport = "http"',
                        'url = "https://api.githubcopilot.com/mcp/"',
                        'bearer_token_env_var = "CODEX_GITHUB_PERSONAL_ACCESS_TOKEN"',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (codex / "rules" / "default.rules").write_text("allow prefix_rule([\"git\", \"status\"])\n", encoding="utf-8")
            (claude / "settings.json").write_text(
                json.dumps(
                    {
                        "env": {"ANTHROPIC_AUTH_TOKEN": "secret-for-login-convenience"},
                        "permissions": {
                            "deny": [
                                f"Read({(claude / 'settings.json').as_posix()})",
                                f"Read({(codex / 'auth*.json').as_posix()})",
                                f"Read({(gemini / 'oauth_creds.json').as_posix()})",
                                f"Read({(gemini / 'google_accounts.json').as_posix()})",
                            ]
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (claude / ".mcp.json").write_text(
                json.dumps({"mcpServers": {"github": {"headers": {"Authorization": "Bearer ${GITHUB_TOKEN}"}}}}),
                encoding="utf-8",
            )
            (gemini / ".geminiignore").write_text(
                "oauth_creds.json\ngoogle_accounts.json\n*credentials*\n",
                encoding="utf-8",
            )
            (gemini / "settings.json").write_text(
                json.dumps(
                    {
                        "admin": {"secureModeEnabled": True},
                        "security": {
                            "environmentVariableRedaction": {
                                "enabled": True,
                                "blocked": [
                                    "ANTHROPIC_AUTH_TOKEN",
                                    "GITHUB_PERSONAL_ACCESS_TOKEN",
                                    "OPENAI_API_KEY",
                                    "GEMINI_API_KEY",
                                ],
                            }
                        },
                        "advanced": {
                            "excludedEnvVars": [
                                "ANTHROPIC_AUTH_TOKEN",
                                "GITHUB_PERSONAL_ACCESS_TOKEN",
                                "OPENAI_API_KEY",
                                "GEMINI_API_KEY",
                            ]
                        },
                        "context": {
                            "fileFiltering": {
                                "respectGeminiIgnore": True,
                                "customIgnoreFilePaths": [(gemini / ".geminiignore").as_posix()],
                            }
                        },
                        "mcpServers": {
                            "github": {
                                "headers": {"Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"}
                            }
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (gemini / ".mcp.json").write_text(
                json.dumps({"mcpServers": {"github": {"headers": {"Authorization": "Bearer ${GITHUB_TOKEN}"}}}}),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/build-policy-tool-credential-audit.py",
                    "--home",
                    str(home),
                    "--output",
                    str(home / "report.json"),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        local_audit = payload["local_agent_config_audit"]
        self.assertEqual(local_audit["status"], "pass")
        self.assertFalse(local_audit["failed_checks"])
        self.assertNotIn("secret-for-login-convenience", completed.stdout)

    def test_builder_fails_when_denied_tool_is_allowlisted(self) -> None:
        profile = json.loads((ROOT / ".governed-ai/repo-profile.json").read_text(encoding="utf-8"))
        profile["tool_allowlist"] = ["shell", "browser"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            profile_path = tmp_root / "repo-profile.json"
            profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/build-policy-tool-credential-audit.py",
                    "--repo-profile",
                    str(profile_path),
                    "--output",
                    str(tmp_root / "report.json"),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertIn("browser", payload["denied_allowlisted_tools"])
        browser = next(item for item in payload["audited_tools"] if item["tool_name"] == "browser")
        self.assertEqual("fail", browser["status"])


if __name__ == "__main__":
    unittest.main()
