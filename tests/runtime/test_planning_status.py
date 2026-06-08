import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_planning_status_script():
    script_path = ROOT / "scripts" / "verify-planning-status.py"
    spec = importlib.util.spec_from_file_location("verify_planning_status_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_planning_status_script"] = module
    spec.loader.exec_module(module)
    return module


class PlanningStatusTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("verify_planning_status_script", None)

    def test_planning_status_succeeds_for_repo(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-planning-status.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["current_active_queue"], "GAP-159..164")
        self.assertEqual(payload["current_decision_gate"], "defer_ltp_and_refresh_evidence")
        self.assertEqual(payload["current_live_posture"], "ready")

    def test_planning_status_fails_when_required_token_missing(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-06",
                        "current_active_queue": {"queue_id": "GAP-159..164"},
                        "current_decision_gate": {"selector": "refresh_evidence_first"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {"status": "attention"},
                        "authoritative_docs": ["docs/README.md"],
                        "required_consistency_tokens": ["single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "README.md").write_text("wrong text", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required tokens"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)

    def test_verify_repo_docs_runs_planning_status_check(self) -> None:
        verifier = (ROOT / "scripts" / "verify-repo.ps1").read_text(encoding="utf-8")
        self.assertIn("Invoke-PlanningStatusChecks", verifier)
        self.assertIn('Write-CheckOk "planning-status"', verifier)


if __name__ == "__main__":
    unittest.main()
