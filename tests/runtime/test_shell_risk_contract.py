import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "verify-shell-risk-contract.py"
VERIFY_REPO_PATH = ROOT / "scripts" / "verify-repo.ps1"


class ShellRiskContractTests(unittest.TestCase):
    def test_current_repo_shell_risks_are_allowlisted(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--json"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["finding_count"], 0)
        self.assertEqual(payload["stale_allowlist_count"], 0)

    def test_fails_on_unapproved_python_shell_true(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            package_dir = repo / "packages" / "sample"
            package_dir.mkdir(parents=True)
            (package_dir / "runner.py").write_text(
                "\n".join(
                    [
                        "import subprocess",
                        "",
                        "subprocess.run('echo unsafe', shell=True)",
                    ]
                ),
                encoding="utf-8",
            )

            payload = self._run_contract(repo)

        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["findings"][0]["kind"], "python_shell_true")
        self.assertEqual(payload["findings"][0]["path"], "packages/sample/runner.py")

    def test_fails_on_unapproved_remove_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            scripts_dir = repo / "scripts"
            scripts_dir.mkdir(parents=True)
            (scripts_dir / "cleanup.ps1").write_text(
                "Remove-Item -Recurse -Force $Target\n",
                encoding="utf-8",
            )

            payload = self._run_contract(repo)

        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["findings"][0]["kind"], "powershell_remove_item")
        self.assertEqual(payload["findings"][0]["path"], "scripts/cleanup.ps1")

    def test_fails_on_unbounded_start_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            scripts_dir = repo / "scripts"
            scripts_dir.mkdir(parents=True)
            (scripts_dir / "launch.ps1").write_text(
                "Start-Process -FilePath pwsh -ArgumentList '-NoProfile'\n",
                encoding="utf-8",
            )

            payload = self._run_contract(repo)

        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["findings"][0]["kind"], "powershell_start_process")
        self.assertEqual(payload["findings"][0]["path"], "scripts/launch.ps1")

    def test_allows_bounded_start_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            scripts_dir = repo / "scripts"
            scripts_dir.mkdir(parents=True)
            (scripts_dir / "launch.ps1").write_text(
                "\n".join(
                    [
                        "$process = Start-Process `",
                        "  -FilePath pwsh `",
                        "  -ArgumentList '-NoProfile' `",
                        "  -WindowStyle Hidden `",
                        "  -PassThru",
                    ]
                ),
                encoding="utf-8",
            )

            payload = self._run_contract(repo)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["finding_count"], 0)
        self.assertEqual(payload["stale_allowlist_count"], 0)
        self.assertFalse(payload["allowlist_expected_counts_enforced"])

    def test_contract_gate_invokes_shell_risk_check(self) -> None:
        source = VERIFY_REPO_PATH.read_text(encoding="utf-8")
        self.assertIn("scripts/verify-shell-risk-contract.py", source)
        self.assertIn('Write-CheckOk "shell-risk-contract"', source)
        self.assertIn("Invoke-ShellRiskContractChecks", source)

    @staticmethod
    def _run_contract(repo: Path) -> dict:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--repo-root",
                str(repo),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
