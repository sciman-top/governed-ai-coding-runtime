import subprocess
import sys
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
            self.assertIn("OK attachment-posture-healthy", healthy_completed.stdout)

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
