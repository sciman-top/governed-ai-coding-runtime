import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class OperatorRunbookTests(unittest.TestCase):
    def test_minimum_operator_runbooks_exist(self) -> None:
        runbooks = [
            ROOT / "docs" / "runbooks" / "failed-rollout-recovery.md",
            ROOT / "docs" / "runbooks" / "expired-waiver-handling.md",
            ROOT / "docs" / "runbooks" / "control-rollback.md",
            ROOT / "docs" / "runbooks" / "repeated-trial-recovery.md",
        ]

        for runbook in runbooks:
            self.assertTrue(runbook.exists(), f"missing runbook: {runbook}")

    def test_progressive_controls_point_to_rollback_behavior(self) -> None:
        text = (ROOT / "docs" / "runbooks" / "control-rollback.md").read_text(encoding="utf-8")

        self.assertIn("observe -> enforce", text)
        self.assertIn("rollback", text.lower())
        self.assertIn("docs/change-evidence/", text)

    def test_repeated_trial_operation_has_recovery_paths(self) -> None:
        text = (ROOT / "docs" / "runbooks" / "repeated-trial-recovery.md").read_text(encoding="utf-8")

        self.assertIn("rerun", text.lower())
        self.assertIn("pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All", text)
        self.assertIn("evidence", text.lower())


if __name__ == "__main__":
    unittest.main()
