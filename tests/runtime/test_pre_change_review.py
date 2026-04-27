import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=False, capture_output=True, text=True)


def _init_repo(path: Path) -> None:
    _run(["git", "init", "-b", "main"], path)
    _run(["git", "config", "user.email", "test@example.invalid"], path)
    _run(["git", "config", "user.name", "Test User"], path)
    (path / "README.md").write_text("baseline\n", encoding="utf-8")
    _run(["git", "add", "README.md"], path)
    _run(["git", "commit", "-m", "baseline"], path)


class PreChangeReviewTests(unittest.TestCase):
    def test_sensitive_change_requires_structured_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            _init_repo(repo)
            (repo / "rules").mkdir()
            (repo / "rules" / "manifest.json").write_text("{}\n", encoding="utf-8")

            completed = _run(
                [sys.executable, str(ROOT / "scripts" / "verify-pre-change-review.py"), "--repo-root", str(repo)],
                repo,
            )

            self.assertEqual(completed.returncode, 1)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertEqual(payload["reason"], "missing_pre_change_review_evidence")
            self.assertIn("rules/manifest.json", payload["sensitive_paths"])

    def test_sensitive_change_passes_with_structured_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            _init_repo(repo)
            (repo / "scripts").mkdir()
            (repo / "scripts" / "sync-agent-rules.py").write_text("print('sync')\n", encoding="utf-8")
            evidence = repo / "docs" / "change-evidence" / "pre-change.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text(
                "\n".join(
                    [
                        "pre_change_review",
                        "control_repo_manifest_and_rule_sources",
                        "user_level_deployed_rule_files",
                        "target_repo_deployed_rule_files",
                        "target_repo_gate_scripts_and_ci",
                        "target_repo_repo_profile",
                        "target_repo_readme_and_operator_docs",
                        "current_official_tool_loading_docs",
                        "drift-integration decision",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            completed = _run(
                [sys.executable, str(ROOT / "scripts" / "verify-pre-change-review.py"), "--repo-root", str(repo)],
                repo,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["matched_evidence"], "docs/change-evidence/pre-change.md")


if __name__ == "__main__":
    unittest.main()
