import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = ROOT / "docs" / "targets" / "templates" / "claude-code" / "settings.json"
HOOK_PATH = ROOT / "docs" / "targets" / "templates" / "claude-code" / "governed-pre-tool-use.py"


class ClaudeCodeGovernanceTemplateTests(unittest.TestCase):
    def test_settings_template_binds_pretooluse_hook_without_local_settings(self) -> None:
        settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        self.assertIn("permissions", settings)
        self.assertIn("hooks", settings)
        self.assertIn("Read(**/target.json)", settings["permissions"]["deny"])
        self.assertNotIn("settings.local.json", json.dumps(settings))

        pre_tool_use = settings["hooks"]["PreToolUse"]
        self.assertEqual(pre_tool_use[0]["matcher"], "Bash|Read")
        hook = pre_tool_use[0]["hooks"][0]
        self.assertEqual(hook["type"], "command")
        self.assertEqual(hook["shell"], "powershell")
        self.assertIn("CLAUDE_PROJECT_DIR", hook["command"])
        self.assertIn("governed-pre-tool-use.py", hook["command"])

    def test_hook_blocks_direct_windows_powershell_commands(self) -> None:
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "powershell.exe -NoProfile -File scripts/build.ps1"},
        }
        completed = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            cwd=ROOT,
            check=False,
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("Blocked by governed Claude Code hook", completed.stderr)
        self.assertIn("powershell.exe", completed.stderr)

    def test_hook_blocks_sensitive_local_file_reads(self) -> None:
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "configs/target.json"},
        }
        completed = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            cwd=ROOT,
            check=False,
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("sensitive local configuration", completed.stderr)

    def test_hook_allows_pwsh_commands(self) -> None:
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "pwsh -NoProfile -File scripts/build.ps1"},
        }
        completed = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            cwd=ROOT,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
