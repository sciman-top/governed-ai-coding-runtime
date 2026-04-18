import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class BootstrapRuntimeTests(unittest.TestCase):
    def test_bootstrap_runtime_script_creates_runtime_roots_and_status(self) -> None:
        script = ROOT / "scripts" / "bootstrap-runtime.ps1"
        if not script.exists():
            self.fail("scripts/bootstrap-runtime.ps1 is not implemented")

        completed = subprocess.run(
            ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        payload = json.loads(completed.stdout)
        self.assertIn("runtime_root", payload)
        self.assertIn("status", payload)
        self.assertTrue((ROOT / ".runtime" / "tasks").exists())
        self.assertTrue((ROOT / ".runtime" / "artifacts").exists())
        self.assertTrue((ROOT / ".runtime" / "replay").exists())
        self.assertIn("total_tasks", payload["status"])


if __name__ == "__main__":
    unittest.main()
