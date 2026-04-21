import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class RunGovernedTaskCliTests(unittest.TestCase):
    def test_verify_attachment_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run-governed-task.py", "verify-attachment", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Execute declared verification gates", completed.stdout)

    def test_verify_attachment_executes_declared_target_repo_gates(self) -> None:
        from governed_ai_coding_runtime_contracts.repo_attachment import attach_target_repo

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "target"
            target_repo.mkdir()
            runtime_state_root = workspace / "runtime-state" / "target"
            attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_state_root),
                repo_id="target",
                display_name="Target",
                primary_language="python",
                build_command="cmd /c exit 0",
                test_command="cmd /c exit 0",
                contract_command="cmd /c exit 0",
                adapter_preference="process_bridge",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run-governed-task.py",
                    "verify-attachment",
                    "--attachment-root",
                    str(target_repo),
                    "--attachment-runtime-state-root",
                    str(runtime_state_root),
                    "--mode",
                    "quick",
                    "--task-id",
                    "task-verify-attachment",
                    "--run-id",
                    "run-verify-attachment",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["repo_id"], "target")
            self.assertEqual(payload["gate_order"], ["test", "contract"])
            self.assertEqual(payload["results"], {"test": "pass", "contract": "pass"})
            for artifact_ref in payload["result_artifact_refs"].values():
                self.assertTrue((runtime_state_root / artifact_ref).exists(), artifact_ref)

    def test_verify_attachment_supports_l2_layered_mode(self) -> None:
        from governed_ai_coding_runtime_contracts.repo_attachment import attach_target_repo

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "target"
            target_repo.mkdir()
            runtime_state_root = workspace / "runtime-state" / "target"
            attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_state_root),
                repo_id="target",
                display_name="Target",
                primary_language="python",
                build_command="cmd /c exit 0",
                test_command="cmd /c exit 0",
                contract_command="cmd /c exit 0",
                adapter_preference="process_bridge",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run-governed-task.py",
                    "verify-attachment",
                    "--attachment-root",
                    str(target_repo),
                    "--attachment-runtime-state-root",
                    str(runtime_state_root),
                    "--mode",
                    "l2",
                    "--task-id",
                    "task-verify-attachment-l2",
                    "--run-id",
                    "run-verify-attachment-l2",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["repo_id"], "target")
            self.assertEqual(payload["mode"], "l2")
            self.assertEqual(payload["gate_order"], ["build", "test", "contract"])
            self.assertEqual(payload["results"], {"build": "pass", "test": "pass", "contract": "pass"})

    def test_govern_attachment_write_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run-governed-task.py", "govern-attachment-write", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Evaluate attached repo write governance", completed.stdout)

    def test_decide_attachment_write_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run-governed-task.py", "decide-attachment-write", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Approve or reject an attached write request", completed.stdout)

    def test_execute_attachment_write_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run-governed-task.py", "execute-attachment-write", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Execute an approved attached write request", completed.stdout)

    def test_status_json_reports_runtime_roots_and_runtime_root_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runtime_root = Path(tmp_dir) / "machine-runtime"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run-governed-task.py",
                    "--runtime-root",
                    str(runtime_root),
                    "status",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["runtime_roots"]["runtime_root"], runtime_root.resolve().as_posix())
            self.assertEqual(payload["runtime_roots"]["compatibility_mode"], False)
            self.assertIn("codex_capability", payload)
            self.assertIn("status", payload["codex_capability"])


if __name__ == "__main__":
    unittest.main()
