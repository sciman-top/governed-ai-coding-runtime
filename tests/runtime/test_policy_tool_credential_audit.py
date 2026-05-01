import json
import subprocess
import sys
import tempfile
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

    def test_builder_fails_when_denied_tool_is_allowlisted(self) -> None:
        profile = json.loads((ROOT / ".governed-ai/repo-profile.json").read_text(encoding="utf-8"))
        profile["tool_allowlist"] = ["shell", "browser"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            profile_path = tmp_root / "repo-profile.json"
            profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/build-policy-tool-credential-audit.py",
                    "--repo-profile",
                    str(profile_path),
                    "--output",
                    str(tmp_root / "report.json"),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertIn("browser", payload["denied_allowlisted_tools"])
        browser = next(item for item in payload["audited_tools"] if item["tool_name"] == "browser")
        self.assertEqual("fail", browser["status"])


if __name__ == "__main__":
    unittest.main()
