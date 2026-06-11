import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PreflightCiWiringTests(unittest.TestCase):
    def test_repo_profile_full_gate_declares_hotspot_step(self) -> None:
        profile = json.loads((ROOT / ".governed-ai" / "repo-profile.json").read_text(encoding="utf-8"))
        full_gate_ids = [entry["id"] for entry in profile.get("full_gate_commands", [])]

        self.assertEqual(full_gate_ids, ["build", "test", "contract", "doctor"])

    def test_preflight_entrypoint_runs_release_ready_checks(self) -> None:
        script_path = ROOT / "scripts" / "governance" / "preflight.ps1"
        self.assertTrue(script_path.exists(), f"missing preflight entrypoint: {script_path}")

        content = script_path.read_text(encoding="utf-8")
        self.assertIn("Invoke-RepoProfileGateRun", content)
        self.assertIn("scripts/verify-repo.ps1 -Check Docs", content)
        self.assertIn("scripts/verify-repo.ps1 -Check Scripts", content)
        self.assertIn("git diff --check", content)

    def test_verify_workflow_runs_preflight_job(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")

        self.assertIn("release-preflight:", workflow)
        self.assertIn("./scripts/governance/preflight.ps1", workflow)


if __name__ == "__main__":
    unittest.main()
