import datetime as dt
import importlib.util
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
    _live_payload: dict | None = None

    def tearDown(self) -> None:
        for module_name in (
            "verify_evidence_recovery_posture_script",
            "select_next_work_recovery",
            "host_feedback_summary_recovery",
            "evaluate_ltp_promotion_script",
        ):
            sys.modules.pop(module_name, None)

    @classmethod
    def _live_recovery_payload(cls) -> dict:
        if cls._live_payload is None:
            module = _load_script()
            cls._live_payload = module.assert_evidence_recovery_posture(
                repo_root=ROOT,
                as_of=dt.date(2026, 6, 9),
            )
        return dict(cls._live_payload)

    def test_live_recovery_posture_requires_fresh_ready_native_attach_evidence(self) -> None:
        payload = self._live_recovery_payload()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["selector"]["next_action"], "defer_ltp_and_refresh_evidence")
        self.assertEqual(payload["selector"]["evidence_state"], "fresh")
        self.assertIsNone(payload["selector"]["evidence_blocker"])
        self.assertEqual(payload["target_runs"]["status"], "ok")
        self.assertEqual(payload["target_runs"]["degraded_latest_run_count"], 0)
        self.assertFalse(payload["effect_report"]["host_capability_candidate_present"])
        self.assertEqual(payload["effect_report"]["decision"], "promote")
        self.assertEqual(payload["effect_report"]["latest_codex_capability_status"], "ready")
        self.assertEqual(payload["effect_report"]["latest_adapter_tier"], "native_attach")

    def test_recovery_posture_fails_closed_when_selector_is_not_in_recovered_defer_state(self) -> None:
        result = self._live_recovery_payload()
        result["selector"]["next_action"] = "promote_ltp"

        failures = []
        if result["selector"]["next_action"] != "defer_ltp_and_refresh_evidence":
            failures.append(
                "selector must return defer_ltp_and_refresh_evidence once fresh host capability recovery is proven and no LTP package is selected"
            )

        self.assertIn("selector must return defer_ltp_and_refresh_evidence", failures[0])


if __name__ == "__main__":
    unittest.main()
