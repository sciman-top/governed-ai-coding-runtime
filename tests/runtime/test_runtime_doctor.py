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
        self.assertIn("OK repo-hook-script", completed.stdout)
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

        self.assertIn("OK codex-capability-ready", completed.stdout)
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
            ROOT / "scripts" / "runtime-flow.ps1",
            ROOT / "scripts" / "runtime-flow-classroomtoolkit.ps1",
            ROOT / "scripts" / "runtime-flow-preset.ps1",
            ROOT / "scripts" / "operator.ps1",
            ROOT / "scripts" / "operator-ui-service.ps1",
            ROOT / "scripts" / "verify-repo.ps1",
        ]

        for script in scripts:
            with self.subTest(script=script.name):
                text = script.read_text(encoding="utf-8")
                self.assertIn("Initialize-WindowsProcessEnvironment.ps1", text)
                self.assertIn("Initialize-WindowsProcessEnvironment", text)

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
                    "Docs",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertIn("OK active-markdown-links", completed.stdout)
        self.assertIn("OK backlog-yaml-ids", completed.stdout)
        self.assertIn("OK old-project-name-historical-only", completed.stdout)

    def test_doctor_runtime_reports_attachment_postures(self) -> None:
        import tempfile

        from governed_ai_coding_runtime_contracts.repo_attachment import attach_target_repo

        script = ROOT / "scripts" / "doctor-runtime.ps1"
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)

            missing_root = workspace / "missing"
            missing_root.mkdir()
            missing_completed = self._run_doctor_attachment(script, missing_root, workspace / "state" / "missing")
            self.assertNotEqual(missing_completed.returncode, 0)
            self.assertIn("FAIL attachment-posture-missing-light-pack", missing_completed.stdout)
            self.assertIn("REMEDIATE", missing_completed.stdout)
            self.assertIn("REMEDIATE-ACTION", missing_completed.stdout)
            self.assertIn("scripts/attach-target-repo.py", missing_completed.stdout)
            self.assertIn("--target-repo", missing_completed.stdout)
            self.assertNotIn("--target-repo-root", missing_completed.stdout)
            self.assertNotIn("attach --target-repo", missing_completed.stdout)
            self.assertIn("REMEDIATE-EVIDENCE", missing_completed.stdout)
            self.assertTrue((workspace / "state" / "missing" / "doctor" / "latest-remediation.json").exists())

            healthy_root = workspace / "healthy"
            healthy_root.mkdir()
            attach_target_repo(
                target_repo_root=str(healthy_root),
                runtime_state_root=str(workspace / "state" / "healthy"),
                repo_id="healthy",
                display_name="Healthy",
                primary_language="python",
                build_command="python -m compileall src",
                test_command="python -m unittest discover",
                contract_command="python -m unittest discover -s tests/contracts",
                adapter_preference="manual_handoff",
                gate_profile="default",
            )
            healthy_completed = self._run_doctor_attachment(script, healthy_root, workspace / "state" / "healthy")
            self.assertEqual(healthy_completed.returncode, 0)
            self.assertIn("OK attachment-target-repo-dependency-baseline", healthy_completed.stdout)
            self.assertIn("OK attachment-light-pack-provenance", healthy_completed.stdout)
            self.assertIn("OK attachment-posture-healthy", healthy_completed.stdout)
            self.assertIn("REMEDIATE-EVIDENCE", healthy_completed.stdout)
            self.assertTrue((workspace / "state" / "healthy" / "doctor" / "latest-remediation.json").exists())

            missing_baseline_path = healthy_root / ".governed-ai" / "dependency-baseline.json"
            missing_baseline_path.unlink()
            missing_baseline_completed = self._run_doctor_attachment(
                script,
                healthy_root,
                workspace / "state" / "healthy",
            )
            self.assertNotEqual(missing_baseline_completed.returncode, 0)
            self.assertIn(
                "FAIL attachment-posture-missing-target-repo-dependency-baseline",
                missing_baseline_completed.stdout,
            )
            self.assertIn("scripts/verify-dependency-baseline.py", missing_baseline_completed.stdout)
            self.assertIn("REMEDIATE-ACTION", missing_baseline_completed.stdout)

            invalid_root = workspace / "invalid"
            (invalid_root / ".governed-ai").mkdir(parents=True)
            (invalid_root / ".governed-ai" / "light-pack.json").write_text(
                json.dumps({"pack_kind": "repo_attachment_light_pack", "repo_profile_ref": "../outside.json"}),
                encoding="utf-8",
            )
            invalid_completed = self._run_doctor_attachment(script, invalid_root, workspace / "state" / "invalid")
            self.assertNotEqual(invalid_completed.returncode, 0)
            self.assertIn("FAIL attachment-posture-invalid-light-pack", invalid_completed.stdout)
            self.assertIn("REMEDIATE", invalid_completed.stdout)
            self.assertIn("REMEDIATE-ACTION", invalid_completed.stdout)
            self.assertIn("scripts/attach-target-repo.py", invalid_completed.stdout)
            self.assertIn("--target-repo", invalid_completed.stdout)
            self.assertNotIn("--target-repo-root", invalid_completed.stdout)
            self.assertNotIn("attach --target-repo", invalid_completed.stdout)
            self.assertIn("REMEDIATE-EVIDENCE", invalid_completed.stdout)
            self.assertTrue((workspace / "state" / "invalid" / "doctor" / "latest-remediation.json").exists())

            stale_root = workspace / "stale"
            stale_root.mkdir()
            attach_target_repo(
                target_repo_root=str(stale_root),
                runtime_state_root=str(workspace / "state" / "stale"),
                repo_id="stale",
                display_name="Stale",
                primary_language="python",
                build_command="python -m compileall src",
                test_command="python -m unittest discover",
                contract_command="python -m unittest discover -s tests/contracts",
                adapter_preference="manual_handoff",
                gate_profile="default",
            )
            light_pack_path = stale_root / ".governed-ai" / "light-pack.json"
            light_pack = json.loads(light_pack_path.read_text(encoding="utf-8"))
            light_pack["binding_id"] = "binding-old-target"
            light_pack_path.write_text(json.dumps(light_pack), encoding="utf-8")
            stale_completed = self._run_doctor_attachment(script, stale_root, workspace / "state" / "stale")
            self.assertNotEqual(stale_completed.returncode, 0)
            self.assertIn("FAIL attachment-posture-stale-binding", stale_completed.stdout)
            self.assertIn("REMEDIATE", stale_completed.stdout)
            self.assertIn("REMEDIATE-ACTION", stale_completed.stdout)
            self.assertIn("scripts/attach-target-repo.py", stale_completed.stdout)
            self.assertIn("--target-repo", stale_completed.stdout)
            self.assertNotIn("--target-repo-root", stale_completed.stdout)
            self.assertNotIn("attach --target-repo", stale_completed.stdout)
            self.assertIn("REMEDIATE-EVIDENCE", stale_completed.stdout)
            self.assertTrue((workspace / "state" / "stale" / "doctor" / "latest-remediation.json").exists())

    def _run_doctor_attachment(self, script: Path, attachment_root: Path, runtime_state_root: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-AttachmentRoot",
                str(attachment_root),
                "-RuntimeStateRoot",
                str(runtime_state_root),
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )


if __name__ == "__main__":
    unittest.main()
