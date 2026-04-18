import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PackageRuntimeTests(unittest.TestCase):
    def test_package_runtime_script_emits_distribution_layout(self) -> None:
        script = ROOT / "scripts" / "package-runtime.ps1"
        if not script.exists():
            self.fail("scripts/package-runtime.ps1 is not implemented")

        completed = subprocess.run(
            ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        payload = json.loads(completed.stdout)
        dist_root = ROOT / ".runtime" / "dist" / "public-usable-release"
        self.assertEqual(payload["distribution_root"], dist_root.as_posix())
        self.assertTrue((dist_root / "README.md").exists())
        self.assertTrue((dist_root / "docs" / "quickstart" / "single-machine-runtime-quickstart.md").exists())
        self.assertTrue((dist_root / "docs" / "product" / "runtime-compatibility-and-upgrade-policy.md").exists())
        self.assertTrue((dist_root / "docs" / "product" / "maintenance-deprecation-and-retirement-policy.md").exists())
        self.assertTrue((dist_root / "scripts" / "bootstrap-runtime.ps1").exists())


if __name__ == "__main__":
    unittest.main()
