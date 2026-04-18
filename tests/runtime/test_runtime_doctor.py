import subprocess
import sys
import shutil
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RuntimeBuildAndDoctorScriptTests(unittest.TestCase):
    def test_build_runtime_script_succeeds(self) -> None:
        script = ROOT / "scripts" / "build-runtime.ps1"
        if not script.exists():
            self.fail("scripts/build-runtime.ps1 is not implemented")

        completed = subprocess.run(
            ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertIn("OK python-bytecode", completed.stdout)
        self.assertIn("OK python-import", completed.stdout)

    def test_doctor_runtime_script_succeeds(self) -> None:
        script = ROOT / "scripts" / "doctor-runtime.ps1"
        if not script.exists():
            self.fail("scripts/doctor-runtime.ps1 is not implemented")

        completed = subprocess.run(
            ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertIn("OK python-command", completed.stdout)
        self.assertIn("OK gate-command-build", completed.stdout)
        self.assertIn("OK gate-command-doctor", completed.stdout)

    def test_verify_repo_exposes_build_and_doctor_checks(self) -> None:
        script = ROOT / "scripts" / "verify-repo.ps1"
        build_completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-Check",
                "Build",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        doctor_completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-Check",
                "Doctor",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertIn("OK runtime-build", build_completed.stdout)
        self.assertIn("OK runtime-doctor", doctor_completed.stdout)

    def test_verify_repo_docs_ignores_ignored_worktree_markdown(self) -> None:
        script = ROOT / "scripts" / "verify-repo.ps1"
        fixture_root = ROOT / ".worktrees" / "verify-repo-docs-fixture"
        fixture_docs = fixture_root / "docs"
        fixture_docs.mkdir(parents=True, exist_ok=True)
        (fixture_docs / "README.md").write_text("[broken](../AGENTS.md)\n", encoding="utf-8")

        try:
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                    "-Check",
                    "Docs",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
        finally:
            shutil.rmtree(fixture_root, ignore_errors=True)

        self.assertIn("OK active-markdown-links", completed.stdout)
        self.assertIn("OK backlog-yaml-ids", completed.stdout)
        self.assertIn("OK old-project-name-historical-only", completed.stdout)


if __name__ == "__main__":
    unittest.main()
