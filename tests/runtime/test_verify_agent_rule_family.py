import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class VerifyAgentRuleFamilyTests(unittest.TestCase):
    def test_rule_family_passes_on_current_repo(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-agent-rule-family.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["managed_tools"], ["codex", "claude"])

    def test_rule_family_rejects_manifest_tool_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_root = Path(tmp_dir)
            manifest_path = temp_root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "default_version": "9.54",
                        "entries": [
                            {"tool": "codex"},
                            {"tool": "gemini"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "verify-agent-rule-family.py"), "--manifest-path", str(manifest_path)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertTrue(any("managed tools" in item for item in payload["failures"]))


if __name__ == "__main__":
    unittest.main()
