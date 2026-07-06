import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _write_target_repo(repo_root: Path, *, wrapper_body: str | None = None, project_body: str | None = None) -> None:
    repo_root.mkdir(parents=True, exist_ok=True)
    agents = project_body or "\n".join(
        [
            "# AGENTS.md",
            "**承接来源**: `GlobalUser/AGENTS.md v9.54`",
            "runtime/host-orchestrator",
            ".ai/state/control-plane.db",
            ".ai/runs/<run_id>/<task_id>/",
            "docs/change-evidence/README.md",
            "Global Rule -> Repo Action",
            "回滚",
            "",
        ]
    )
    (repo_root / "AGENTS.md").write_text(agents, encoding="utf-8")
    if wrapper_body is not None:
        (repo_root / "CLAUDE.md").write_text(wrapper_body, encoding="utf-8")


class VerifyTargetProjectRulesTests(unittest.TestCase):
    def _coordination_payload(self, repo_root: Path) -> dict:
        return {
            "targets": [
                {
                    "repo_id": "pilot",
                    "repo_root": str(repo_root),
                    "tools": ["codex", "claude"],
                    "project_common_rule": "AGENTS.md",
                    "claude_wrapper_rule": "CLAUDE.md",
                    "coordination_mode": "wrapper_and_contract_audit",
                }
            ]
        }

    def test_wrapper_missing_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir) / "pilot"
            _write_target_repo(repo_root, wrapper_body=None)
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(self._coordination_payload(repo_root)), encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "verify-target-project-rules.py"), "--coordination-path", str(coordination_path)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["results"][0]["drift_category"], "project_wrapper_missing")

    def test_nonthin_wrapper_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir) / "pilot"
            _write_target_repo(
                repo_root,
                wrapper_body="\n".join(
                    [
                        "@AGENTS.md",
                        "",
                        "## 1. 阅读指引",
                        "**承接来源**: `GlobalUser/CLAUDE.md v9.54`",
                        "## A. 不应复制共同正文",
                        "runtime/host-orchestrator",
                    ]
                ),
            )
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(self._coordination_payload(repo_root)), encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "verify-target-project-rules.py"), "--coordination-path", str(coordination_path)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["results"][0]["drift_category"], "project_wrapper_nonthin")

    def test_contract_missing_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir) / "pilot"
            _write_target_repo(
                repo_root,
                wrapper_body="\n".join(
                    [
                        "@AGENTS.md",
                        "",
                        "# CLAUDE.md",
                        "**承接来源**: `GlobalUser/CLAUDE.md v9.54`",
                        "## 1. 阅读指引",
                        "## B. Claude 平台差异",
                        "## D. 维护校验",
                    ]
                ),
                project_body="# AGENTS.md\n**承接来源**: `GlobalUser/AGENTS.md v9.54`\n",
            )
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(self._coordination_payload(repo_root)), encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "verify-target-project-rules.py"), "--coordination-path", str(coordination_path)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["results"][0]["drift_category"], "project_contract_missing")

    def test_passes_for_shared_body_and_thin_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir) / "pilot"
            _write_target_repo(
                repo_root,
                wrapper_body="\n".join(
                    [
                        "@AGENTS.md",
                        "",
                        "# CLAUDE.md",
                        "**承接来源**: `GlobalUser/CLAUDE.md v9.54`",
                        "## 1. 阅读指引",
                        "## B. Claude 平台差异",
                        "CLAUDE.local.md",
                        "## D. 维护校验",
                    ]
                ),
            )
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(self._coordination_payload(repo_root)), encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "verify-target-project-rules.py"), "--coordination-path", str(coordination_path)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["results"][0]["status"], "pass")
        self.assertTrue(payload["results"][0]["shared_body_model"])


if __name__ == "__main__":
    unittest.main()
