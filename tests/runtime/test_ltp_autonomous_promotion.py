import datetime as dt
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_ltp_script():
    script_path = ROOT / "scripts" / "evaluate-ltp-promotion.py"
    spec = importlib.util.spec_from_file_location("evaluate_ltp_promotion_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["evaluate_ltp_promotion_script"] = module
    spec.loader.exec_module(module)
    return module


class LtpAutonomousPromotionTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("evaluate_ltp_promotion_script", None)

    def test_ltp_policy_succeeds_for_repo_without_promotion(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/evaluate-ltp-promotion.py", "--as-of", "2026-04-27"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["policy_id"], "default-ltp-autonomous-promotion")
        self.assertEqual(payload["decision"], "defer_all")
        self.assertFalse(payload["should_promote"])
        self.assertIsNone(payload["selected_package"])

    def test_ltp_policy_can_auto_select_one_package_when_scope_fenced(self) -> None:
        module = _load_ltp_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            policy_path = self._write_policy(repo_root, auto_selected_count=1)

            result = module.assert_ltp_promotion_policy(
                repo_root=repo_root,
                policy_path=policy_path,
                as_of=dt.date(2026, 4, 27),
            )

            self.assertTrue(result["should_promote"])
            self.assertEqual(result["selected_package"], "LTP-01")
            self.assertEqual(result["decision"], "auto_select")

    def test_ltp_policy_rejects_multiple_auto_selected_packages(self) -> None:
        module = _load_ltp_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            policy_path = self._write_policy(repo_root, auto_selected_count=2)

            with self.assertRaisesRegex(ValueError, "exceeds limit"):
                module.assert_ltp_promotion_policy(
                    repo_root=repo_root,
                    policy_path=policy_path,
                    as_of=dt.date(2026, 4, 27),
                )

    def test_ltp_policy_rejects_missing_required_doc_text(self) -> None:
        module = _load_ltp_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            policy_path = self._write_policy(repo_root, auto_selected_count=0)
            (repo_root / "docs/global.md").write_text("required marker removed", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing required doc text"):
                module.assert_ltp_promotion_policy(
                    repo_root=repo_root,
                    policy_path=policy_path,
                    as_of=dt.date(2026, 4, 27),
                )

    def test_verify_repo_docs_runs_ltp_promotion_policy(self) -> None:
        verifier = (ROOT / "scripts" / "verify-repo.ps1").read_text(encoding="utf-8")

        self.assertIn("function Invoke-DocsChecks", verifier)
        self.assertIn("Invoke-LtpAutonomousPromotionChecks", verifier)
        self.assertIn('Write-CheckOk "ltp-autonomous-promotion"', verifier)

    def _write_policy(self, repo_root: Path, *, auto_selected_count: int) -> Path:
        refs = [
            "docs/global.md",
            "docs/evidence.md",
            "docs/scope.md",
            "docs/full-gate.md",
            "docs/owner.md",
        ]
        for ref in refs:
            path = repo_root / ref
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("GAP-113 CLM-008 Do not directly force the full heavy stack as the default route.", encoding="utf-8")
        packages = []
        for index in range(2):
            selected = index < auto_selected_count
            package = {
                "package_id": f"LTP-0{index + 1}",
                "name": f"package-{index + 1}",
                "target_stack": ["heavy stack"],
                "current_decision": "triggered" if selected else "defer",
                "autonomous_decision": "auto_selected" if selected else "not_selected",
                "why_not_now": "not enough evidence" if not selected else "triggered in test",
                "trigger_evidence_required": ["trigger evidence"],
                "current_evidence_refs": ["docs/evidence.md"],
                "promotion_requirements": ["scope_fence_ref", "full_gate_ref"],
            }
            if selected:
                package["scope_fence_ref"] = "docs/scope.md"
                package["full_gate_ref"] = "docs/full-gate.md"
            packages.append(package)
        policy = {
            "schema_version": "1.0",
            "policy_id": "test-ltp-promotion",
            "status": "enforced",
            "reviewed_on": "2026-04-27",
            "review_expires_at": "2026-07-26",
            "decision_claim": "test decision",
            "autonomous_mode": {
                "enabled": True,
                "max_auto_selected_packages": 1,
                "requires_scope_fence_ref": True,
                "requires_full_gate_ref": True,
                "requires_current_source_guard": True,
                "owner_directed_allowed": True,
                "owner_directed_requires_ref": True,
                "safe_default": "defer",
            },
            "global_required_refs": ["docs/global.md"],
            "decision_invariants": ["one package only"],
            "packages": packages,
            "required_doc_refs": [{"path": "docs/global.md", "contains": "GAP-113"}],
            "evidence_refs": ["docs/evidence.md"],
            "rollback_ref": "git revert test ltp policy",
        }
        policy_path = repo_root / "policy.json"
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        return policy_path


if __name__ == "__main__":
    unittest.main()
