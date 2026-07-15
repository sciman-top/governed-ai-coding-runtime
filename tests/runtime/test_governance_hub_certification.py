import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _fixture_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GACR_HOST_FEEDBACK_FIXTURE"] = str(
        ROOT / "tests" / "fixtures" / "host-feedback" / "clean-windows-runner.json"
    )
    return env


class GovernanceHubCertificationTests(unittest.TestCase):
    def test_builder_emits_executable_certification_report(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/build-governance-hub-certification.py"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
            env=_fixture_env(),
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertNotIn("/.worktrees/", json.dumps(payload).replace("\\", "/"))
        self.assertEqual(payload["effect_feedback"]["scope"], "repo_local_host_feedback")
        self.assertEqual(payload["effect_feedback"]["decision"], "defer_ltp_and_refresh_evidence")
        self.assertTrue(all(payload["loop_status"].values()))
        self.assertTrue(payload["loop_status"]["self_evolution_readiness_loop"])
        self.assertTrue(payload["final_answers"]["self_evolution_readiness_loop_executable"])
        self.assertEqual(payload["verifier_results"]["self_evolution_readiness"]["overall_state"], "complete")
        self.assertFalse(payload["verifier_results"]["self_evolution_readiness"]["ready_for_unattended_self_update"])
        self.assertEqual(payload["effect_feedback"]["input_mode"], "test_fixture")
        self.assertEqual(payload["effect_feedback"]["acceptance_scope"], "test_only_not_hosted")
        self.assertFalse(payload["effect_feedback"]["hosted_acceptance"])

    def test_report_path_uses_canonical_root_when_run_from_worktree(self) -> None:
        if ".worktrees" not in ROOT.parts:
            self.skipTest("worktree-specific canonical-path regression")

        completed = subprocess.run(
            [sys.executable, "scripts/build-governance-hub-certification.py"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
            env=_fixture_env(),
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertNotIn("/.worktrees/", json.dumps(payload).replace("\\", "/"))

    def test_verifier_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-governance-hub-certification.py"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
            env=_fixture_env(),
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["final_status"], "executable")


if __name__ == "__main__":
    unittest.main()
