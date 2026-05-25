import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RepoHookEnforcementTests(unittest.TestCase):
    def test_pre_commit_hook_invokes_repo_guard_script(self) -> None:
        hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")

        self.assertIn("scripts/hooks/pre-commit.ps1", hook)
        self.assertIn("pwsh", hook)

    def test_commit_msg_hook_invokes_chinese_subject_guard(self) -> None:
        hook = (ROOT / ".githooks" / "commit-msg").read_text(encoding="utf-8")

        self.assertIn("scripts/hooks/commit-msg.ps1", hook)
        self.assertIn("pwsh", hook)

    def test_repo_guard_runs_contract_and_codex_reference_checks(self) -> None:
        script = (ROOT / "scripts" / "hooks" / "pre-commit.ps1").read_text(encoding="utf-8")

        self.assertIn("scripts\\verify-repo.ps1", script)
        self.assertIn("-Check Contract", script)
        self.assertIn("tests.runtime.test_codex_executable_reference_guard", script)

    def test_commit_msg_guard_requires_chinese_subject_by_default(self) -> None:
        script = (ROOT / "scripts" / "hooks" / "commit-msg.ps1").read_text(encoding="utf-8")

        self.assertIn("GOVERNED_ALLOW_NON_CHINESE_COMMIT", script)
        self.assertIn("普通提交信息默认必须中文优先", script)
        self.assertIn("\\p{IsCJKUnifiedIdeographs}", script)

    @unittest.skipUnless(shutil.which("pwsh") or shutil.which("powershell"), "PowerShell is required")
    def test_commit_msg_guard_blocks_plain_english_subject(self) -> None:
        shell = shutil.which("pwsh") or shutil.which("powershell")
        assert shell is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            message_path = Path(tmp_dir) / "COMMIT_EDITMSG"
            message_path.write_text("fix sync drift\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    shell,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "hooks" / "commit-msg.ps1"),
                    "-CommitMessagePath",
                    str(message_path),
                ],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                cwd=ROOT,
                check=False,
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("subject 需要包含中文", completed.stderr)

    @unittest.skipUnless(shutil.which("pwsh") or shutil.which("powershell"), "PowerShell is required")
    def test_commit_msg_guard_allows_chinese_subject(self) -> None:
        shell = shutil.which("pwsh") or shutil.which("powershell")
        assert shell is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            message_path = Path(tmp_dir) / "COMMIT_EDITMSG"
            message_path.write_text("修复目标仓中文提交约束\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    shell,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "hooks" / "commit-msg.ps1"),
                    "-CommitMessagePath",
                    str(message_path),
                ],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                cwd=ROOT,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)

    @unittest.skipUnless(shutil.which("pwsh") or shutil.which("powershell"), "PowerShell is required")
    def test_commit_msg_guard_has_explicit_english_override(self) -> None:
        shell = shutil.which("pwsh") or shutil.which("powershell")
        assert shell is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            message_path = Path(tmp_dir) / "COMMIT_EDITMSG"
            message_path.write_text("docs: update generated API reference\n", encoding="utf-8")
            env = dict(os.environ)
            env["GOVERNED_ALLOW_NON_CHINESE_COMMIT"] = "1"

            completed = subprocess.run(
                [
                    shell,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "hooks" / "commit-msg.ps1"),
                    "-CommitMessagePath",
                    str(message_path),
                ],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                cwd=ROOT,
                env=env,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_hook_installer_sets_repo_local_hooks_path(self) -> None:
        installer = (ROOT / "scripts" / "install-repo-hooks.ps1").read_text(encoding="utf-8")

        self.assertIn("core.hooksPath", installer)
        self.assertIn(".githooks", installer)
        self.assertIn("commit-msg", installer)
        self.assertNotIn("E:/CODE/repo-governance-hub/hooks-global", installer)

    def test_runtime_doctor_checks_commit_msg_hook(self) -> None:
        doctor = (ROOT / "scripts" / "doctor-runtime.ps1").read_text(encoding="utf-8")

        self.assertIn(".githooks/commit-msg", doctor)
        self.assertIn("scripts/hooks/commit-msg.ps1", doctor)
        self.assertIn("repo-hook-commit-msg", doctor)


if __name__ == "__main__":
    unittest.main()
