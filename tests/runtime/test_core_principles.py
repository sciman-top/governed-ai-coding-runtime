import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_core_principles_script():
    script_path = ROOT / "scripts" / "verify-core-principles.py"
    spec = importlib.util.spec_from_file_location("verify_core_principles_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_core_principles_script"] = module
    spec.loader.exec_module(module)
    return module


class CorePrinciplesTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("verify_core_principles_script", None)

    def test_core_principles_policy_succeeds_for_repo(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-core-principles.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["policy_id"], "default-core-principles")
        self.assertIn("codex_claude_cooperation_hosts", payload["principle_ids"])
        self.assertIn("governance_hub_reusable_contract_final_state", payload["principle_ids"])
        self.assertIn("automation_first_outer_ai_intelligent_evolution", payload["principle_ids"])
        self.assertIn("context_budget_and_instruction_minimalism", payload["principle_ids"])
        self.assertIn("least_privilege_tool_credential_boundary", payload["principle_ids"])
        self.assertIn("measured_effect_feedback_over_claims", payload["principle_ids"])
        self.assertIn("delete_candidate", payload["portfolio_outcomes"])
        self.assertTrue(payload["outer_ai_automatic_trigger_allowed"])
        self.assertIn("evolution_proposal_generation", payload["outer_ai_allowed_actions"])
        self.assertIn("active_policy_mutation", payload["outer_ai_forbidden_effective_actions"])
        self.assertIn("structured_candidate", payload["outer_ai_required_controls"])

    def test_core_principles_fail_when_required_principle_missing(self) -> None:
        module = _load_core_principles_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            policy_path = self._write_policy(repo_root)
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            policy["principles"] = [
                item for item in policy["principles"] if item["principle_id"] != "no_host_competition"
            ]
            policy_path.write_text(json.dumps(policy), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing core principles"):
                module.assert_core_principles(repo_root=repo_root, policy_path=policy_path)

    def test_core_principles_fail_when_doc_token_missing(self) -> None:
        module = _load_core_principles_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            policy_path = self._write_policy(repo_root, doc_token="not present")

            with self.assertRaisesRegex(ValueError, "missing doc refs"):
                module.assert_core_principles(repo_root=repo_root, policy_path=policy_path)

    def test_core_principles_fail_when_outer_ai_control_missing(self) -> None:
        module = _load_core_principles_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            policy_path = self._write_policy(repo_root)
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            policy["outer_ai_evolution_controls"]["allowed_automatic_actions"].remove(
                "evolution_proposal_generation"
            )
            policy_path.write_text(json.dumps(policy), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing outer AI allowed actions"):
                module.assert_core_principles(repo_root=repo_root, policy_path=policy_path)

    def test_verify_repo_docs_runs_core_principles_gate(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/verify-repo.ps1",
                "-Check",
                "Docs",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("OK core-principles", completed.stdout)

    def _write_policy(self, repo_root: Path, *, doc_token: str = "cooperation hosts") -> Path:
        docs_dir = repo_root / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / "README.md").write_text("cooperation hosts", encoding="utf-8")
        evidence = docs_dir / "evidence.md"
        evidence.write_text("evidence", encoding="utf-8")
        policy = {
            "schema_version": "1.0",
            "policy_id": "test-core-principles",
            "status": "enforced",
            "principles": [
                {
                    "principle_id": principle_id,
                    "category": "positioning",
                    "summary": principle_id,
                    "required": True,
                    "enforcement_level": "docs_gate",
                    "machine_gate": "verify-core-principles",
                    "rollback_ref": "git revert test policy",
                }
                for principle_id in [
                    "efficiency_first",
                    "codex_claude_cooperation_hosts",
                    "no_host_competition",
                    "claude_third_party_provider_boundary",
                    "external_mechanism_selective_absorption",
                    "governance_hub_reusable_contract_final_state",
                    "controlled_evolution_portfolio_lifecycle",
                    "automation_first_outer_ai_intelligent_evolution",
                    "no_automatic_mutation_without_review",
                    "evidence_and_rollback_required",
                    "context_budget_and_instruction_minimalism",
                    "least_privilege_tool_credential_boundary",
                    "measured_effect_feedback_over_claims",
                    "hard_gate_order",
                ]
            ],
            "capability_portfolio_outcomes": [
                "add",
                "keep",
                "improve",
                "merge",
                "deprecate",
                "retire",
                "delete_candidate",
            ],
            "outer_ai_evolution_controls": {
                "automatic_trigger_allowed": True,
                "allowed_automatic_actions": [
                    "source_collection",
                    "experience_extraction",
                    "knowledge_candidate_generation",
                    "skill_candidate_generation",
                    "evolution_proposal_generation",
                    "candidate_evaluation",
                    "effect_feedback_analysis",
                ],
                "forbidden_automatic_effective_actions": [
                    "active_policy_mutation",
                    "skill_enablement",
                    "target_repo_sync",
                    "push",
                    "merge",
                    "reviewed_evidence_deletion",
                    "active_gate_deletion",
                ],
                "required_controls": [
                    "structured_candidate",
                    "risk_gate",
                    "machine_gate",
                    "evidence_ref",
                    "rollback_ref",
                    "human_review_for_high_risk",
                ],
            },
            "required_doc_refs": [{"path": "docs/README.md", "contains": doc_token}],
            "forbidden_active_patterns": [
                {
                    "pattern": "official Claude subscription is required",
                    "scan_roots": ["docs/README.md"],
                }
            ],
            "evidence_refs": ["docs/evidence.md"],
            "rollback_ref": "git revert test policy",
        }
        policy_path = repo_root / "policy.json"
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        return policy_path


if __name__ == "__main__":
    unittest.main()
