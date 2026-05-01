import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PolicyToolCredentialAuditTests(unittest.TestCase):
    def test_builder_generates_fail_closed_report(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/build-policy-tool-credential-audit.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["summary"]["unknown_tool_count"], 0)
        self.assertGreaterEqual(payload["summary"]["audited_tool_count"], 4)
        self.assertGreaterEqual(payload["summary"]["override_surface_count"], 2)

    def test_verifier_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-policy-tool-credential-audit.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["invalid_reasons"])


if __name__ == "__main__":
    unittest.main()
