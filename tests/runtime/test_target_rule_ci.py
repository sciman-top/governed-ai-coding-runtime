import hashlib
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COORDINATION = ROOT / "rules" / "target-project-rule-coordination.json"
TEMPLATE = ROOT / "rules" / "templates" / "github" / "agent-rule-contract.yml"
MATRIX_SCRIPT = ROOT / "scripts" / "export-target-rule-ci-matrix.py"
AGGREGATE_WORKFLOW = ROOT / ".github" / "workflows" / "agent-rule-coordination.yml"
VERIFY_WORKFLOW = ROOT / ".github" / "workflows" / "verify.yml"
CHECKOUT_V4_SHA = "34e114876b0b11c390a56381ad16ebd13914f8d5"


def _workflow_sha256(raw: bytes) -> str:
    normalized = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class TargetRuleCiTests(unittest.TestCase):
    @staticmethod
    def _workflow_script() -> str:
        workflow = TEMPLATE.read_text(encoding="utf-8")
        body = workflow.split("python - <<'PY'\n", 1)[1].split("\n          PY", 1)[0]
        return textwrap.dedent(body)

    @staticmethod
    def _project_rule(project_contract: str) -> str:
        return "\n".join(
            [
                "# AGENTS.md - pilot",
                f"**项目契约**: {project_contract}",
                "**全局规则复核**: 9.55",
                "## 1. 当前落点与目标归宿",
                "- 当前落点：pilot。目标归宿：verified。",
                "## A. 仓库事实",
                "- fact",
                "## B. 执行与风险边界",
                "- boundary",
                "## C. 门禁、证据与回滚",
                "- build -> test -> contract/invariant -> hotspot",
                "- 证据：docs/change-evidence/。回滚：only this slice。",
                "## D. Global Rule -> Repo Action",
                "- R6",
                "",
            ]
        )

    def _run_workflow_script(self, project_contract: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "AGENTS.md").write_text(
                self._project_rule(project_contract), encoding="utf-8"
            )
            (root / "CLAUDE.md").write_bytes(b"@AGENTS.md\n")
            return subprocess.run(
                [sys.executable, "-c", self._workflow_script()],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_manifest_hash_matches_canonical_workflow_template(self) -> None:
        payload = json.loads(COORDINATION.read_text(encoding="utf-8"))
        workflow = TEMPLATE.read_bytes()

        self.assertEqual(
            _workflow_sha256(workflow),
            payload["ci_contract"]["workflow_sha256"],
        )
        self.assertEqual(payload["ci_contract"]["workflow_hash_mode"], "utf8_lf_v1")
        self.assertIn(b"agent-rule-contract-ci: 2.1", workflow)
        self.assertIn(b"@AGENTS.md", workflow)
        self.assertIn(b"Normalize incomplete submodule metadata", workflow)
        self.assertIn(b"persist-credentials: true", workflow)

    def test_matrix_export_is_generated_from_all_nine_allowlisted_targets(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(MATRIX_SCRIPT), "--coordination-path", str(COORDINATION)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        matrix = json.loads(completed.stdout)
        self.assertEqual(len(matrix["include"]), 9)
        by_id = {entry["repo_id"]: entry for entry in matrix["include"]}
        self.assertEqual(
            by_id["local-ai-dev-orchestrator"]["repository"],
            "sciman-top/local-ai-runtime",
        )
        self.assertEqual(
            by_id["qq-codex-bot"]["repository"],
            "sciman-top/qq-astrbot-stack",
        )
        self.assertEqual(by_id["github-toolkit"]["aggregate_mode"], "target_local_only")
        self.assertEqual(by_id["qq-codex-bot"]["aggregate_mode"], "target_local_only")
        self.assertEqual(by_id["skills-manager"]["aggregate_mode"], "checkout")

    def test_canonical_workflow_executes_and_rejects_wrong_project_contract(self) -> None:
        accepted = self._run_workflow_script("2.0")
        rejected = self._run_workflow_script("1.9")

        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
        self.assertNotEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
        self.assertIn("project contract", rejected.stdout + rejected.stderr)

    def test_aggregate_workflow_uses_generated_matrix_and_strict_target_audit(self) -> None:
        workflow = AGGREGATE_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("export-target-rule-ci-matrix.py", workflow)
        self.assertIn("fromJSON(needs.prepare.outputs.matrix)", workflow)
        self.assertIn("repository: ${{ matrix.repository }}", workflow)
        self.assertIn("matrix.aggregate_mode == 'checkout'", workflow)
        self.assertIn("matrix.aggregate_mode == 'target_local_only'", workflow)
        self.assertIn("--workspace-root", workflow)
        self.assertIn("--require-all", workflow)

    def test_aggregate_workflow_normalizes_incomplete_target_submodule_metadata(self) -> None:
        workflow = AGGREGATE_WORKFLOW.read_text(encoding="utf-8")
        target_checkout = workflow.split("- name: Checkout target repository", 1)[1].split(
            "- name: Audit target rule contract", 1
        )[0]

        self.assertIn("persist-credentials: true", target_checkout)
        self.assertIn("Normalize incomplete target submodule metadata", workflow)
        self.assertIn("working-directory: workspace/${{ matrix.repo_path }}", workflow)
        self.assertIn("if: always() && matrix.aggregate_mode == 'checkout'", workflow)

    def test_new_workflows_pin_checkout_to_a_full_commit_sha(self) -> None:
        template = TEMPLATE.read_text(encoding="utf-8")
        aggregate = AGGREGATE_WORKFLOW.read_text(encoding="utf-8")

        expected = f"actions/checkout@{CHECKOUT_V4_SHA} # v4"
        self.assertIn(expected, template)
        self.assertEqual(aggregate.count(expected), 3)
        self.assertNotIn("actions/checkout@v4", template + aggregate)

    def test_control_repo_ci_uses_only_rule_governance_gates(self) -> None:
        workflow = VERIFY_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("python scripts/rulesctl.py verify --skip-projection --skip-targets", workflow)
        self.assertIn("runs-on: ubuntu-latest", workflow)
        self.assertNotIn("verify-repo.ps1", workflow)
        self.assertNotIn("preflight.ps1", workflow)
        self.assertNotIn("runtime", workflow.lower())


if __name__ == "__main__":
    unittest.main()
