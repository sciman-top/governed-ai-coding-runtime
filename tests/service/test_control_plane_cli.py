import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ControlPlaneCliTests(unittest.TestCase):
    def test_control_plane_cli_reports_invalid_payload_json_as_structured_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "apps" / "control-plane" / "main.py"),
                "--route",
                "/health",
                "--payload-json",
                "{",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["error"]["code"], "invalid_payload_json")
        self.assertEqual(payload["route"], "/health")

    def test_control_plane_cli_reports_route_validation_as_structured_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "apps" / "control-plane" / "main.py"),
                "--route",
                "/operator",
                "--payload-json",
                json.dumps({"action": "unsupported"}),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["error"]["code"], "validation_error")
        self.assertIn("unsupported operator action", payload["error"]["message"])
        self.assertEqual(payload["service"], "control-plane")

    def test_control_plane_cli_requires_object_payload(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "apps" / "control-plane" / "main.py"),
                "--route",
                "/health",
                "--payload-json",
                "[]",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["error"]["code"], "validation_error")
        self.assertIn("payload-json must decode to an object", payload["error"]["message"])


if __name__ == "__main__":
    unittest.main()
