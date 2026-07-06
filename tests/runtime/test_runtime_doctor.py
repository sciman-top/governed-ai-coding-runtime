import subprocess
import sys
import os
import shutil
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


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
            encoding="utf-8",
            errors="replace",
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
        self.assertIn("OK windows-process-environment", completed.stdout)
        self.assertIn("OK python-asyncio", completed.stdout)
        self.assertIn("OK gate-command-build", completed.stdout)
        self.assertIn("OK gate-command-doctor", completed.stdout)
        self.assertIn("OK dependency-baseline-doc", completed.stdout)
        self.assertIn("OK repo-hook-pre-commit", completed.stdout)
        self.assertIn("OK repo-hook-commit-msg", completed.stdout)
        self.assertIn("OK repo-hook-script", completed.stdout)
        self.assertIn("OK repo-hook-commit-msg-script", completed.stdout)
        self.assertIn("OK repo-hook-installer", completed.stdout)
        self.assertIn("OK repo-hooks-path", completed.stdout)

    @unittest.skipUnless(os.name == "nt", "Windows process environment normalization")
    def test_doctor_runtime_initializes_windows_process_environment(self) -> None:
        script = ROOT / "scripts" / "doctor-runtime.ps1"
        pwsh = shutil.which("pwsh")
        codex = shutil.which("codex")
        if not pwsh:
            self.skipTest("pwsh is not available")
        if not codex:
            self.skipTest("codex is not available")

        env = os.environ.copy()
        env.pop("SystemRoot", None)
        env.pop("WINDIR", None)
        env.pop("ComSpec", None)
        env.pop("ProgramFiles", None)
        completed = subprocess.run(
            [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
            env=env,
        )

        self.assertTrue(
            ("OK codex-capability-ready" in completed.stdout)
            or ("WARN codex-capability-degraded" in completed.stdout),
            completed.stdout,
        )
        self.assertIn("OK windows-process-environment-normalized", completed.stdout)
        self.assertIn("OK python-asyncio", completed.stdout)
        self.assertNotIn("WARN codex-capability-blocked", completed.stdout)

    @unittest.skipUnless(os.name == "nt", "Windows process environment normalization")
    def test_initializer_restores_programfiles_and_tool_paths(self) -> None:
        script = ROOT / "scripts" / "Initialize-WindowsProcessEnvironment.ps1"
        pwsh = shutil.which("pwsh")
        if not pwsh:
            self.skipTest("pwsh is not available")

        probe = (
            f'. "{script}"; '
            '$env:ProgramFiles=""; '
            'Initialize-WindowsProcessEnvironment; '
            'if ([string]::IsNullOrWhiteSpace($env:ProgramFiles)) { throw "missing ProgramFiles" }; '
            'if ($env:PATH -notlike "*PowerShell\\7*") { throw "missing powershell7 path" }; '
            'if ($env:PATH -notlike "*WindowsPowerShell*") { throw "missing powershell path" }; '
            'Write-Host "OK initializer-programfiles-path"'
        )
        completed = subprocess.run(
            [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", probe],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertIn("OK initializer-programfiles-path", completed.stdout)

    def test_runtime_entrypoints_initialize_windows_process_environment(self) -> None:
        scripts = [
            ROOT / "scripts" / "bootstrap-runtime.ps1",
            ROOT / "scripts" / "build-runtime.ps1",
            ROOT / "scripts" / "doctor-runtime.ps1",
            ROOT / "scripts" / "runtime-check.ps1",
            ROOT / "scripts" / "operator.ps1",
            ROOT / "scripts" / "operator-ui-service.ps1",
            ROOT / "scripts" / "verify-repo.ps1",
        ]

        for script in scripts:
            with self.subTest(script=script.name):
                text = script.read_text(encoding="utf-8")
                self.assertIn("Initialize-WindowsProcessEnvironment.ps1", text)
                self.assertIn("Initialize-WindowsProcessEnvironment", text)

    def test_repo_local_doctor_surface_no_longer_references_target_attachment_flow(self) -> None:
        script = ROOT / "scripts" / "doctor-runtime.ps1"
        text = script.read_text(encoding="utf-8")

        for token in (
            "attach-target-repo.py",
            "repo_attachment",
            "light-pack",
            "AttachmentRoot",
            "RuntimeStateRoot",
        ):
            self.assertNotIn(token, text)

    def test_verify_repo_exposes_build_and_doctor_checks(self) -> None:
        script = ROOT / "scripts" / "verify-repo.ps1"
        verifier = script.read_text(encoding="utf-8")

        self.assertIn('switch ($Check)', verifier)
        self.assertIn('"Build" { Invoke-BuildChecks }', verifier)
        self.assertIn('"Doctor" { Invoke-DoctorChecks }', verifier)
        self.assertIn("scripts/build-runtime.ps1", verifier)
        self.assertIn("scripts/doctor-runtime.ps1", verifier)
        self.assertIn('Write-CheckOk "runtime-build"', verifier)
        self.assertIn('Write-CheckOk "runtime-doctor"', verifier)

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
                    "DocsLinks",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )
        finally:
            shutil.rmtree(fixture_root, ignore_errors=True)

        self.assertIn("OK active-markdown-links", completed.stdout)

    def test_verify_repo_docs_handles_non_ascii_markdown_paths(self) -> None:
        script = ROOT / "scripts" / "verify-repo.ps1"
        fixture_path = ROOT / "docs" / "验证-路径-fixture.md"
        fixture_path.write_text("[ok](./README.md)\n", encoding="utf-8")

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
                    "DocsLinks",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertIn("OK active-markdown-links", completed.stdout)

if __name__ == "__main__":
    unittest.main()
