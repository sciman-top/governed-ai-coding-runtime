import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_policy_script():
    script_path = ROOT / "scripts" / "verify-host-capability-claim-upgrade-policy.py"
    spec = importlib.util.spec_from_file_location("verify_host_capability_claim_upgrade_policy_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_host_capability_claim_upgrade_policy_script"] = module
    spec.loader.exec_module(module)
    return module


class HostCapabilityClaimUpgradePolicyTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("verify_host_capability_claim_upgrade_policy_script", None)

    def test_policy_verifier_succeeds_for_repo(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-host-capability-claim-upgrade-policy.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["missing_surface_fields"])

    def test_policy_verifier_fails_when_required_field_missing(self) -> None:
        module = _load_policy_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "strategy").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "product").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "backlog").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "change-evidence").mkdir(parents=True, exist_ok=True)

            policy_path = repo_root / "docs" / "architecture" / "host-capability-claim-upgrade-policy.json"
            policy_path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "policy_id": "test",
                        "status": "enforced",
                        "reviewed_on": "2026-06-07",
                        "review_expires_at": "2026-09-05",
                        "decision_claim": "test",
                        "canonical_surface_fields": ["host_family"],
                        "fail_closed_defaults": {
                            "missing_surface_field": "fail_closed",
                            "missing_verification_refs": "fail_closed",
                            "missing_evidence_refs": "fail_closed",
                            "historical_certification_without_fresh_recovery": "fail_closed",
                            "fresh_but_degraded_posture": "fail_closed",
                        },
                        "upgrade_rules": [
                            {"claim_scope": "codex_live_native_attach_upgrade"},
                            {"claim_scope": "wording_refresh_only"},
                            {"claim_scope": "backlog_candidate_trigger"},
                        ],
                        "required_doc_refs": [
                            {
                                "path": "docs/strategy/current-best-end-state-blueprint.md",
                                "contains": "Claim upgrade requires fresh evidence",
                            }
                        ],
                        "evidence_refs": ["docs/change-evidence/example.md"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "strategy" / "current-best-end-state-blueprint.md").write_text(
                "Claim upgrade requires fresh evidence",
                encoding="utf-8",
            )
            (repo_root / "docs" / "change-evidence" / "example.md").write_text("evidence", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing canonical surface fields"):
                module.assert_host_capability_claim_upgrade_policy(repo_root=repo_root, policy_path=policy_path)

    def test_verify_repo_docs_runs_host_capability_claim_upgrade_policy_check(self) -> None:
        verifier = (ROOT / "scripts" / "verify-repo.ps1").read_text(encoding="utf-8")
        self.assertIn("Invoke-HostCapabilityClaimUpgradePolicyChecks", verifier)
        self.assertIn('Write-CheckOk "host-capability-claim-upgrade-policy"', verifier)


if __name__ == "__main__":
    unittest.main()
