import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class GovernanceHubCertificationTests(unittest.TestCase):
    def test_builder_emits_executable_certification_report(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/build-governance-hub-certification.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["effect_feedback"]["target"], "classroomtoolkit")
        self.assertEqual(payload["effect_feedback"]["decision"], "promote")
        self.assertTrue(all(payload["loop_status"].values()))
        self.assertTrue(payload["loop_status"]["self_evolution_readiness_loop"])
        self.assertTrue(payload["final_answers"]["self_evolution_readiness_loop_executable"])
        self.assertEqual(payload["verifier_results"]["self_evolution_readiness"]["overall_state"], "complete")
        self.assertFalse(payload["verifier_results"]["self_evolution_readiness"]["ready_for_unattended_self_update"])

    def test_verifier_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-governance-hub-certification.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["final_status"], "executable")


if __name__ == "__main__":
    unittest.main()
