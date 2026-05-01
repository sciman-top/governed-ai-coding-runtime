import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RepoMapContextArtifactTests(unittest.TestCase):
    def test_builder_generates_required_governance_files_and_metrics(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/build-repo-map-context-artifact.py"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["decision"], "keep")
        self.assertEqual(payload["metrics"]["file_selection_accuracy"], 1.0)
        self.assertIn("scripts/verify-repo.ps1", payload["selected_files"])

    def test_verifier_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-repo-map-context-artifact.py"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["decision"], "keep")
        self.assertGreaterEqual(payload["metrics"]["clarification_reduction_proxy"], 0.75)


if __name__ == "__main__":
    unittest.main()
