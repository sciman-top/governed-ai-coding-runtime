import json
import zipfile
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PackageRuntimeTests(unittest.TestCase):
    def test_package_runtime_script_emits_distribution_layout(self) -> None:
        script = ROOT / "scripts" / "package-runtime.ps1"
        if not script.exists():
            self.fail("scripts/package-runtime.ps1 is not implemented")

        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-Version",
                "0.1.0-test",
            ],
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
        self.assertTrue((dist_root / "run.ps1").exists())
        self.assertTrue((dist_root / "install.ps1").exists())
        self.assertTrue((dist_root / "release.ps1").exists())
        self.assertTrue((dist_root / "LICENSE").exists())
        self.assertTrue((dist_root / "rules" / "manifest.json").exists())
        self.assertTrue((dist_root / ".githooks" / "pre-commit").exists())
        self.assertFalse((dist_root / ".runtime").exists())
        self.assertFalse((dist_root / "docs" / "change-evidence").exists())

        release_zip = Path(payload["release_zip_path"])
        release_manifest = Path(payload["release_manifest_path"])
        sha256_path = Path(payload["release_sha256_path"])
        provenance_path = Path(payload["provenance_path"])
        self.assertTrue(release_zip.exists())
        self.assertTrue(release_manifest.exists())
        self.assertTrue(sha256_path.exists())
        self.assertTrue(provenance_path.exists())

        release_payload = json.loads(release_manifest.read_text(encoding="utf-8"))
        self.assertEqual(release_payload["version"], "0.1.0-test")
        self.assertEqual(release_payload["channel"], "portable")
        self.assertEqual(release_payload["install_entrypoint"], "install.ps1")
        self.assertIn("docs/change-evidence/**", release_payload["excluded_paths"])

        with zipfile.ZipFile(release_zip) as archive:
            names = {name.replace("\\", "/") for name in archive.namelist()}
        self.assertIn("install.ps1", names)
        self.assertIn("run.ps1", names)
        self.assertIn("rules/manifest.json", names)
        self.assertIn(".githooks/pre-commit", names)
        self.assertFalse(any(name.startswith("docs/change-evidence/") for name in names))
        self.assertFalse(any(name.startswith(".runtime/") for name in names))

    def test_release_entrypoint_uses_repo_root_when_called_from_another_directory(self) -> None:
        script = ROOT / "release.ps1"
        if not script.exists():
            self.fail("release.ps1 is not implemented")

        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                    "-Version",
                    "0.1.0-cwd-test",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=tmp,
            )

        payload = json.loads(completed.stdout)
        self.assertTrue(Path(payload["release_zip_path"]).is_relative_to(ROOT / ".runtime" / "dist" / "releases"))
        self.assertTrue((ROOT / ".runtime" / "dist" / "public-usable-release" / "install.ps1").exists())

    def test_release_entrypoint_rejects_path_like_version(self) -> None:
        script = ROOT / "release.ps1"
        if not script.exists():
            self.fail("release.ps1 is not implemented")

        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-Version",
                "..\\escape",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Invalid release version", completed.stderr + completed.stdout)

    def test_install_runtime_dry_run_reports_portable_runtime_root(self) -> None:
        script = ROOT / "install.ps1"
        if not script.exists():
            self.fail("install.ps1 is not implemented")

        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-Mode",
                "Portable",
                "-DryRun",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "Portable")
        self.assertTrue(payload["dry_run"])
        self.assertEqual(Path(payload["runtime_root"]), ROOT / ".runtime")
        self.assertIn("pwsh", payload["required_commands"])
        self.assertIn("python", payload["required_commands"])
        self.assertIn(".\\install.ps1 -Mode User", payload["next_commands"])


if __name__ == "__main__":
    unittest.main()
