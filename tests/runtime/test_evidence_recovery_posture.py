import datetime as dt
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_script():
    script_path = ROOT / "scripts" / "verify-evidence-recovery-posture.py"
    spec = importlib.util.spec_from_file_location("verify_evidence_recovery_posture_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_evidence_recovery_posture_script"] = module
    spec.loader.exec_module(module)
    return module


class EvidenceRecoveryPostureTests(unittest.TestCase):
    def tearDown(self) -> None:
        for module_name in (
            "verify_evidence_recovery_posture_script",
            "select_next_work_recovery",
            "host_feedback_summary_recovery",
            "evaluate_ltp_promotion_script",
        ):
            sys.modules.pop(module_name, None)

    def test_live_recovery_posture_requires_refresh_before_implementation(self) -> None:
        module = _load_script()

        payload = module.assert_evidence_recovery_posture(repo_root=ROOT, as_of=dt.date(2026, 5, 1))
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["selector"]["next_action"], "refresh_evidence_first")
        self.assertEqual(payload["selector"]["evidence_state"], "stale")
        self.assertEqual(payload["target_runs"]["status"], "attention")
        self.assertGreater(payload["target_runs"]["degraded_latest_run_count"], 0)
        self.assertTrue(payload["effect_report"]["host_capability_candidate_present"])

    def test_recovery_posture_fails_closed_when_selector_is_not_refreshing_evidence(self) -> None:
        module = _load_script()

        result = module.inspect_evidence_recovery_posture(repo_root=ROOT, as_of=dt.date(2026, 5, 1))
        result["selector"]["next_action"] = "promote_ltp"

        failures = []
        if result["selector"]["next_action"] != "refresh_evidence_first":
            failures.append("selector must keep choosing refresh_evidence_first while latest target runs are degraded")

        self.assertIn("selector must keep choosing refresh_evidence_first", failures[0])


if __name__ == "__main__":
    unittest.main()
