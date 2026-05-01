import datetime as dt
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_selector_script():
    script_path = ROOT / "scripts" / "select-next-work.py"
    spec = importlib.util.spec_from_file_location("select_next_work_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["select_next_work_script"] = module
    spec.loader.exec_module(module)
    return module


class AutonomousNextWorkSelectionTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("select_next_work_script", None)
        sys.modules.pop("evaluate_ltp_promotion_script", None)

    def test_repo_selector_refreshes_evidence_when_target_runs_are_degraded(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/select-next-work.py", "--as-of", "2026-05-01"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["policy_id"], "default-autonomous-next-work-selection")
        self.assertEqual(payload["ltp_decision"], "defer_all")
        self.assertEqual(payload["next_action"], "refresh_evidence_first")
        self.assertIsNone(payload["selected_package"])
        self.assertEqual(payload["gate_state"], "pass")
        self.assertEqual(payload["source_state"], "fresh")
        self.assertEqual(payload["evidence_state"], "stale")
        self.assertGreater(payload["auto_detected_inputs"]["details"]["host_feedback"]["degraded_latest_run_count"], 0)
        self.assertIn("auto_detected_inputs", payload)

    def test_selector_promotes_one_auto_selected_ltp_package(self) -> None:
        module = _load_selector_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            next_policy = self._write_next_policy(repo_root)
            ltp_policy = self._write_ltp_policy(repo_root, decision="auto_select")

            result = module.assert_next_work_selection(
                repo_root=repo_root,
                policy_path=next_policy,
                ltp_policy_path=ltp_policy,
                as_of=dt.date(2026, 4, 27),
                gate_state="pass",
                source_state="fresh",
                evidence_state="fresh",
            )

            self.assertEqual(result["next_action"], "promote_ltp")
            self.assertEqual(result["selected_package"], "LTP-01")

    def test_selector_repairs_gate_before_promoting_ltp(self) -> None:
        module = _load_selector_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            next_policy = self._write_next_policy(repo_root)
            ltp_policy = self._write_ltp_policy(repo_root, decision="auto_select")

            result = module.assert_next_work_selection(
                repo_root=repo_root,
                policy_path=next_policy,
                ltp_policy_path=ltp_policy,
                as_of=dt.date(2026, 4, 27),
                gate_state="fail",
                source_state="fresh",
                evidence_state="fresh",
            )

            self.assertEqual(result["next_action"], "repair_gate_first")
            self.assertIsNone(result["selected_package"])

    def test_selector_refreshes_stale_evidence_before_promoting_ltp(self) -> None:
        module = _load_selector_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            next_policy = self._write_next_policy(repo_root)
            ltp_policy = self._write_ltp_policy(repo_root, decision="auto_select")

            result = module.assert_next_work_selection(
                repo_root=repo_root,
                policy_path=next_policy,
                ltp_policy_path=ltp_policy,
                as_of=dt.date(2026, 4, 27),
                gate_state="pass",
                source_state="fresh",
                evidence_state="stale",
            )

            self.assertEqual(result["next_action"], "refresh_evidence_first")
            self.assertIsNone(result["selected_package"])

    def test_selector_requires_scope_for_owner_directed_ltp(self) -> None:
        module = _load_selector_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            next_policy = self._write_next_policy(repo_root)
            ltp_policy = self._write_ltp_policy(repo_root, decision="owner_directed")

            result = module.assert_next_work_selection(
                repo_root=repo_root,
                policy_path=next_policy,
                ltp_policy_path=ltp_policy,
                as_of=dt.date(2026, 4, 27),
                gate_state="pass",
                source_state="fresh",
                evidence_state="fresh",
            )

            self.assertEqual(result["next_action"], "owner_directed_scope_required")
            self.assertIsNone(result["selected_package"])

    def test_selector_auto_detection_fails_closed_when_repo_lacks_evidence(self) -> None:
        module = _load_selector_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            next_policy = self._write_next_policy(repo_root)
            ltp_policy = self._write_ltp_policy(repo_root, decision="defer_all")

            result = module.assert_next_work_selection(
                repo_root=repo_root,
                policy_path=next_policy,
                ltp_policy_path=ltp_policy,
                as_of=dt.date(2026, 4, 27),
            )

            self.assertEqual(result["gate_state"], "fail")
            self.assertEqual(result["source_state"], "stale")
            self.assertEqual(result["evidence_state"], "stale")
            self.assertEqual(result["next_action"], "repair_gate_first")

    def test_verify_repo_docs_runs_next_work_selector(self) -> None:
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
        self.assertIn("OK autonomous-next-work-selection", completed.stdout)

    def _write_next_policy(self, repo_root: Path) -> Path:
        refs = [
            "docs/roadmap.md",
            "docs/plan.md",
            "docs/backlog.md",
            "docs/claim.json",
            "docs/next-evidence.md",
            "docs/ltp.json",
        ]
        for ref in refs:
            path = repo_root / ref
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("GAP-114 Autonomous Next-Work Selector CLM-009 autonomous next-work selector", encoding="utf-8")
        policy = {
            "schema_version": "1.0",
            "policy_id": "test-next-work-selection",
            "status": "enforced",
            "reviewed_on": "2026-04-27",
            "review_expires_at": "2026-07-26",
            "decision_claim": "test next-work decision",
            "allowed_next_actions": [
                "repair_gate_first",
                "refresh_evidence_first",
                "promote_ltp",
                "owner_directed_scope_required",
                "defer_ltp_and_refresh_evidence",
            ],
            "selection_order": [
                {"priority": 1, "condition": "gate", "next_action": "repair_gate_first", "why": "gate"},
                {"priority": 2, "condition": "freshness", "next_action": "refresh_evidence_first", "why": "freshness"},
                {"priority": 3, "condition": "ltp", "next_action": "promote_ltp", "why": "ltp"},
                {
                    "priority": 4,
                    "condition": "owner",
                    "next_action": "owner_directed_scope_required",
                    "why": "owner",
                },
                {
                    "priority": 5,
                    "condition": "defer",
                    "next_action": "defer_ltp_and_refresh_evidence",
                    "why": "defer",
                },
            ],
            "default_inputs": {
                "gate_state": "pass",
                "source_state": "fresh",
                "evidence_state": "fresh",
                "ltp_policy_ref": "docs/ltp.json",
            },
            "invariants": ["gate first"],
            "required_doc_refs": [
                {"path": "docs/roadmap.md", "contains": "GAP-114"},
                {"path": "docs/plan.md", "contains": "GAP-114"},
                {"path": "docs/backlog.md", "contains": "GAP-114 Autonomous Next-Work Selector"},
                {"path": "docs/claim.json", "contains": "CLM-009"},
                {"path": "docs/next-evidence.md", "contains": "autonomous next-work selector"},
            ],
            "evidence_refs": ["docs/next-evidence.md"],
            "rollback_ref": "git revert test next-work policy",
        }
        policy_path = repo_root / "next-policy.json"
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        return policy_path

    def _write_ltp_policy(self, repo_root: Path, *, decision: str) -> Path:
        refs = ["docs/global.md", "docs/evidence.md", "docs/scope.md", "docs/full-gate.md", "docs/owner.md"]
        for ref in refs:
            path = repo_root / ref
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("GAP-113 CLM-008 Do not directly force the full heavy stack as the default route.", encoding="utf-8")
        selected = decision == "auto_select"
        owner_directed = decision == "owner_directed"
        package = {
            "package_id": "LTP-01",
            "name": "package-1",
            "target_stack": ["heavy stack"],
            "current_decision": "triggered" if selected else "watch" if owner_directed else "defer",
            "autonomous_decision": "auto_selected" if selected else "owner_directed_selected" if owner_directed else "not_selected",
            "why_not_now": "not enough evidence" if not selected else "triggered in test",
            "trigger_evidence_required": ["trigger evidence"],
            "current_evidence_refs": ["docs/evidence.md"],
            "promotion_requirements": ["scope_fence_ref", "full_gate_ref"],
        }
        if selected:
            package["scope_fence_ref"] = "docs/scope.md"
            package["full_gate_ref"] = "docs/full-gate.md"
        if owner_directed:
            package["owner_directed_ref"] = "docs/owner.md"
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
            "packages": [package],
            "required_doc_refs": [{"path": "docs/global.md", "contains": "GAP-113"}],
            "evidence_refs": ["docs/evidence.md"],
            "rollback_ref": "git revert test ltp policy",
        }
        policy_path = repo_root / "docs/ltp.json"
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        return policy_path


if __name__ == "__main__":
    unittest.main()
