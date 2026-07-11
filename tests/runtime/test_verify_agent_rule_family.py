import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify-agent-rule-family.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class VerifyAgentRuleFamilyTests(unittest.TestCase):
    def test_rule_family_passes_on_current_repo(self) -> None:
        completed = _run()

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["managed_tools"], ["codex", "claude"])
        self.assertTrue(payload["common_sections_match"])
        self.assertEqual(payload["project_contract_version"], "2.0")

    def test_rule_family_rejects_manifest_tool_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "default_version": "9.55",
                        "project_contract_version": "2.0",
                        "entries": [{"tool": "codex"}, {"tool": "gemini"}],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            completed = _run("--manifest-path", str(manifest_path))

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("managed tools" in item for item in payload["failures"]))

    def test_common_section_body_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_root = Path(tmp_dir)
            manifest_path = temp_root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "default_version": "9.54",
                        "project_contract_version": "2.0",
                        "entries": [{"tool": "codex"}, {"tool": "claude"}],
                    }
                ),
                encoding="utf-8",
            )
            codex_path = temp_root / "AGENTS.md"
            claude_path = temp_root / "CLAUDE.md"
            codex_text = (ROOT / "rules/global/codex/AGENTS.md").read_text(encoding="utf-8")
            claude_text = (ROOT / "rules/global/claude/CLAUDE.md").read_text(encoding="utf-8")
            claude_text = claude_text.replace(
                "2. `R2 小步闭环`：每步可执行、可验证、可对比。",
                "2. `R2 小步闭环`：这一行故意制造共同正文漂移。",
            )
            codex_path.write_text(codex_text, encoding="utf-8")
            claude_path.write_text(claude_text, encoding="utf-8")

            completed = _run(
                "--manifest-path",
                str(manifest_path),
                "--codex-rule-path",
                str(codex_path),
                "--claude-rule-path",
                str(claude_path),
            )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["common_sections_match"])
        self.assertTrue(any("common section" in item for item in payload["failures"]))

    def test_project_contract_version_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_root = Path(tmp_dir)
            manifest_path = temp_root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "default_version": "9.55",
                        "project_contract_version": "2.0",
                        "entries": [{"tool": "codex"}, {"tool": "claude"}],
                    }
                ),
                encoding="utf-8",
            )
            codex_path = temp_root / "AGENTS.md"
            claude_path = temp_root / "CLAUDE.md"
            for source_path, destination_path in (
                (ROOT / "rules/global/codex/AGENTS.md", codex_path),
                (ROOT / "rules/global/claude/CLAUDE.md", claude_path),
            ):
                text = source_path.read_text(encoding="utf-8").replace(
                    "**项目契约版本**: 2.0",
                    "**项目契约版本**: 1.0",
                )
                destination_path.write_text(text, encoding="utf-8")

            completed = _run(
                "--manifest-path",
                str(manifest_path),
                "--codex-rule-path",
                str(codex_path),
                "--claude-rule-path",
                str(claude_path),
            )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("project contract version" in item for item in payload["failures"]))


if __name__ == "__main__":
    unittest.main()
