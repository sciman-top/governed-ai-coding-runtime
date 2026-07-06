import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]


class RunGovernedTaskCliTests(unittest.TestCase):
    def test_help_hides_retired_commands(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run-governed-task.py", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("{create,run,status}", completed.stdout)
        self.assertNotIn("verify-attachment", completed.stdout)
        self.assertNotIn("govern-attachment-write", completed.stdout)
        self.assertNotIn("decide-attachment-write", completed.stdout)
        self.assertNotIn("execute-attachment-write", completed.stdout)

    def test_retired_commands_fail_closed_with_retirement_message(self) -> None:
        for command in (
            "verify-attachment",
            "govern-attachment-write",
            "decide-attachment-write",
            "execute-attachment-write",
        ):
            with self.subTest(command=command):
                completed = subprocess.run(
                    [sys.executable, "scripts/run-governed-task.py", command],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=ROOT,
                )

                self.assertEqual(completed.returncode, 1)
                self.assertIn("Status: retired_command", completed.stdout)
                self.assertIn("Attachment and target-repo bridge flows were removed.", completed.stdout)

    def test_run_task_executes_profile_local_quick_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runtime_root = Path(tmp_dir) / "runtime"
            profile_path = Path(tmp_dir) / "repo-profile.json"
            gate_command = f'"{sys.executable}" -c "print(\'gate-ok\')"'
            profile_path.write_text(
                json.dumps(
                    {
                        "repo_id": "fast-test-repo",
                        "primary_language": "python",
                        "rollout_posture": {"current_mode": "observe", "target_mode": "advisory"},
                        "build_commands": [{"id": "build", "command": gate_command, "required": True}],
                        "test_commands": [{"id": "test", "command": gate_command, "required": True}],
                        "quick_gate_commands": [{"id": "quick", "command": gate_command, "required": True}],
                        "contract_commands": [{"id": "contract", "command": gate_command, "required": True}],
                        "invariant_commands": [],
                        "tool_allowlist": ["shell", "python"],
                        "path_policies": {"read_allow": ["**"], "write_allow": ["**"], "blocked": []},
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run-governed-task.py",
                    "--runtime-root",
                    str(runtime_root),
                    "run",
                    "--task-id",
                    "task-cli-quick-profile",
                    "--goal",
                    "CLI quick profile smoke",
                    "--scope",
                    "runtime cli",
                    "--repo",
                    "fast-test-repo",
                    "--profile",
                    str(profile_path),
                    "--mode",
                    "quick",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["total_tasks"], 1)
            self.assertEqual(payload["tasks"][0]["task_id"], "task-cli-quick-profile")
            self.assertEqual(payload["tasks"][0]["current_state"], "delivered")

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
            self.assertNotIn("attachments", payload)

    def test_status_text_no_longer_mentions_attachments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runtime_root = Path(tmp_dir) / "machine-runtime"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run-governed-task.py",
                    "--runtime-root",
                    str(runtime_root),
                    "status",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("No governed tasks recorded.", completed.stdout)
            self.assertNotIn("Attachment ", completed.stdout)


if __name__ == "__main__":
    unittest.main()
