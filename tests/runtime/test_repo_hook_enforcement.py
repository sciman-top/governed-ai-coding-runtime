import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RepoHookEnforcementTests(unittest.TestCase):
    def test_pre_commit_hook_invokes_repo_guard_script(self) -> None:
        hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")

        self.assertIn("scripts/hooks/pre-commit.ps1", hook)
        self.assertIn("pwsh", hook)

    def test_repo_guard_runs_contract_and_codex_reference_checks(self) -> None:
        script = (ROOT / "scripts" / "hooks" / "pre-commit.ps1").read_text(encoding="utf-8")

        self.assertIn("scripts\\verify-repo.ps1", script)
        self.assertIn("-Check Contract", script)
        self.assertIn("tests.runtime.test_codex_executable_reference_guard", script)

    def test_hook_installer_sets_repo_local_hooks_path(self) -> None:
        installer = (ROOT / "scripts" / "install-repo-hooks.ps1").read_text(encoding="utf-8")

        self.assertIn("core.hooksPath", installer)
        self.assertIn(".githooks", installer)
        self.assertNotIn("E:/CODE/repo-governance-hub/hooks-global", installer)


if __name__ == "__main__":
    unittest.main()
