from __future__ import annotations

import json
import subprocess
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
            self.assertNotIn("cmp_1778246510288_1", config)

    def test_shared_launcher_supports_cli_exec_and_app_surfaces(self) -> None:
        script = (ROOT / "scripts" / "Start-CodexShared.ps1").read_text(encoding="utf-8")

        self.assertIn("[ValidateSet('cli', 'exec', 'app')]", script)
        self.assertIn("model_provider={0}", script)
        self.assertIn("$Surface -eq 'exec'", script)
        self.assertIn("Codex app accepts a workspace path", script)


if __name__ == "__main__":
    unittest.main()
