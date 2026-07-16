import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "rulesctl.py"
WORKFLOW = b"name: Agent Rule Contract\n# agent-rule-contract-ci: 2.1\n"


def _project_rule(release: str) -> str:
    return "\n".join(
        [
            "# AGENTS.md - pilot",
            "**项目契约**: 2.0",
            f"**全局规则复核**: {release}",
            "",
            "## 1. 范围",
            "- 当前落点：pilot。",
            "- 目标归宿：保持规则契约可验证。",
            "",
            "## A. 仓库事实",
            "- `src/` 是实现目录。",
            "",
            "## B. 执行边界",
            "- 只修改当前任务范围。",
            "",
            "## C. 门禁",
            "- fixed order：`build -> test -> contract/invariant -> hotspot`。",
            "- `.github/workflows/agent-rule-contract.yml` 只验证规则契约。",
            "",
            "## D. 证据与回滚",
            "- 证据：`docs/change-evidence/`。",
            "- 回滚：只回滚当前规则切片。",
            "",
        ]
    )


class RulesCtlTests(unittest.TestCase):
    def test_status_separates_default_branch_from_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            repo = workspace / "pilot"
            workflow_path = repo / ".github" / "workflows" / "agent-rule-contract.yml"
            workflow_path.parent.mkdir(parents=True)
            (repo / "AGENTS.md").write_text(_project_rule("9.57"), encoding="utf-8")
            (repo / "CLAUDE.md").write_bytes(b"@AGENTS.md\n")
            workflow_path.write_bytes(WORKFLOW)
            subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
            subprocess.run(
                ["git", "config", "core.autocrlf", "false"], cwd=repo, check=True
            )
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Rule Tests",
                    "-c",
                    "user.email=rules@example.invalid",
                    "commit",
                    "--quiet",
                    "-m",
                    "fixture",
                ],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
                cwd=repo,
                check=True,
            )
            (repo / "AGENTS.md").write_text(_project_rule("9.56"), encoding="utf-8")

            workflow_hash = hashlib.sha256(WORKFLOW).hexdigest()
            coordination = {
                "schema_version": "2.3",
                "coordination_id": "target-project-rule-coordination",
                "rule_release": "9.57",
                "project_contract_version": "2.0",
                "workspace_root": str(workspace),
                "updated_on": "2026-07-16",
                "workspace_inventory": {
                    "mode": "direct_git_roots",
                    "excluded_directories": [],
                    "unlisted_repository_policy": "block",
                    "missing_allowlisted_repository_policy": "block_on_require_all",
                },
                "ci_contract": {
                    "contract_id": "agent-rule-contract-ci",
                    "version": "2.1",
                    "workflow_hash_mode": "utf8_lf_v1",
                    "workflow_sha256": workflow_hash,
                },
                "targets": [
                    {
                        "repo_id": "pilot",
                        "repo_path": "pilot",
                        "github_repository": "example/pilot",
                        "github_visibility": "public",
                        "aggregate_mode": "checkout",
                        "ci_workflow_path": ".github/workflows/agent-rule-contract.yml",
                        "tools": ["codex", "claude"],
                        "project_common_rule": "AGENTS.md",
                        "claude_wrapper_rule": "CLAUDE.md",
                        "claude_wrapper_mode": "import_only",
                        "project_contract_version": "2.0",
                        "reviewed_global_release": "9.57",
                        "required_anchors": ["src/"],
                        "evidence_path": "docs/change-evidence/",
                        "budgets": {
                            "project_max_bytes": 16384,
                            "project_max_lines": 140,
                            "wrapper_max_lines": 4,
                            "effective_context_warning_lines": 160,
                        },
                        "coordination_mode": "audit_only",
                    }
                ],
            }
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(coordination), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "status",
                    "--coordination-path",
                    str(coordination_path),
                    "--workspace-root",
                    str(workspace),
                    "--default-ref",
                    "origin/main",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["states"]["source_ready"])
        self.assertTrue(payload["states"]["global_projected"])
        self.assertTrue(payload["states"]["default_branch_effective"])
        self.assertFalse(payload["states"]["workspace_effective"])
        self.assertIsNone(payload["states"]["host_loaded"])
        self.assertIsNone(payload["states"]["hosted_accepted"])
        self.assertEqual(payload["components"]["workspace"]["status"], "fail")


if __name__ == "__main__":
    unittest.main()
