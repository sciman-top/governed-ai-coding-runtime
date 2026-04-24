import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _extract_json_payload(raw_stdout: str) -> dict:
    start = raw_stdout.find("{")
    if start < 0:
        raise AssertionError(f"json payload not found in stdout: {raw_stdout}")
    return json.loads(raw_stdout[start:])


class GovernanceGateRunnerTests(unittest.TestCase):
    def test_level_check_l2_runs_middle_gate_layer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            profile_path = workspace / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "layered-l2",
                    "full_gate_commands": [
                        {"id": "build", "required": True, "command": "Write-Host 'build-ok'"},
                        {"id": "test", "required": True, "command": "Write-Host 'test-ok'"},
                        {"id": "contract", "required": True, "command": "Write-Host 'contract-ok'"},
                        {"id": "doctor", "required": True, "command": "Write-Host 'doctor-should-skip'"},
                    ],
                    "auto_commit_policy": {"enabled": False},
                },
            )

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "governance" / "level-check.ps1"),
                    "-RepoProfilePath",
                    str(profile_path),
                    "-WorkingDirectory",
                    str(workspace),
                    "-Level",
                    "l2",
                    "-Json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = _extract_json_payload(completed.stdout)
            self.assertEqual(payload["summary"]["gate_level"], "l2")
            self.assertEqual(payload["summary"]["gate_order"], ["build", "test", "contract"])
            self.assertNotIn("doctor-should-skip", completed.stdout)

    def test_fast_check_runs_matching_additional_non_blocking_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            profile_path = workspace / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "additional-non-blocking",
                    "test_commands": [{"id": "test", "required": True, "command": "Write-Host 'test-ok'"}],
                    "contract_commands": [{"id": "contract", "required": True, "command": "Write-Host 'contract-ok'"}],
                    "additional_gate_commands": [
                        {
                            "id": "quick-extra",
                            "command": "Write-Host 'extra-failed'; exit 7",
                            "profiles": ["quick"],
                            "required": False,
                            "blocking": False,
                        },
                        {
                            "id": "full-extra",
                            "command": "Write-Host 'full-extra-should-skip'",
                            "profiles": ["full"],
                            "required": True,
                        },
                    ],
                    "auto_commit_policy": {"enabled": False},
                },
            )

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "governance" / "fast-check.ps1"),
                    "-RepoProfilePath",
                    str(profile_path),
                    "-WorkingDirectory",
                    str(workspace),
                    "-Json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = _extract_json_payload(completed.stdout)
            self.assertEqual(payload["summary"]["gate_order"], ["test", "contract", "quick-extra"])
            self.assertEqual(payload["summary"]["results"]["quick-extra"], "fail")
            self.assertEqual(payload["summary"]["detailed"][2]["blocking"], False)
            self.assertNotIn("full-extra-should-skip", completed.stdout)

    def test_gate_entry_timeout_overrides_global_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            profile_path = workspace / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "per-gate-timeout",
                    "full_gate_commands": [
                        {
                            "id": "slow-entry",
                            "required": True,
                            "timeout_seconds": 1,
                            "command": "Start-Sleep -Seconds 2; Write-Host 'done'",
                        }
                    ],
                    "auto_commit_policy": {"enabled": False},
                },
            )

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "governance" / "full-check.ps1"),
                    "-RepoProfilePath",
                    str(profile_path),
                    "-WorkingDirectory",
                    str(workspace),
                    "-GateTimeoutSeconds",
                    "30",
                    "-Json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = _extract_json_payload(completed.stdout)
            gate_result = payload["summary"]["detailed"][0]
            self.assertEqual(gate_result["reason"], "timed_out")
            self.assertEqual(gate_result["timeout_seconds"], 1)
            self.assertEqual(gate_result["exit_code"], 124)

    def test_full_check_gate_timeout_seconds_param_enforces_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            profile_path = workspace / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "timeout-param",
                    "full_gate_commands": [
                        {
                            "id": "slow",
                            "required": True,
                            "command": "Start-Sleep -Seconds 2; Write-Host 'done'",
                        }
                    ],
                    "auto_commit_policy": {"enabled": False},
                },
            )

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "governance" / "full-check.ps1"),
                    "-RepoProfilePath",
                    str(profile_path),
                    "-WorkingDirectory",
                    str(workspace),
                    "-GateTimeoutSeconds",
                    "1",
                    "-Json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = _extract_json_payload(completed.stdout)
            self.assertEqual(payload["summary"]["gate_timeout_seconds"], 1)
            gate_result = payload["summary"]["detailed"][0]
            self.assertEqual(gate_result["gate_id"], "slow")
            self.assertEqual(gate_result["status"], "fail")
            self.assertEqual(gate_result["reason"], "timed_out")
            self.assertEqual(gate_result["timed_out"], True)
            self.assertEqual(gate_result["exit_code"], 124)

    def test_full_check_gate_timeout_env_enforces_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            profile_path = workspace / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "timeout-env",
                    "full_gate_commands": [
                        {
                            "id": "slow-env",
                            "required": True,
                            "command": "Start-Sleep -Seconds 2; Write-Host 'done'",
                        }
                    ],
                    "auto_commit_policy": {"enabled": False},
                },
            )

            env = os.environ.copy()
            env["GOVERNED_GATE_TIMEOUT_SECONDS"] = "1"
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "governance" / "full-check.ps1"),
                    "-RepoProfilePath",
                    str(profile_path),
                    "-WorkingDirectory",
                    str(workspace),
                    "-Json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
                env=env,
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = _extract_json_payload(completed.stdout)
            self.assertEqual(payload["summary"]["gate_timeout_seconds"], 1)
            gate_result = payload["summary"]["detailed"][0]
            self.assertEqual(gate_result["gate_id"], "slow-env")
            self.assertEqual(gate_result["status"], "fail")
            self.assertEqual(gate_result["reason"], "timed_out")
            self.assertEqual(gate_result["timed_out"], True)
            self.assertEqual(gate_result["exit_code"], 124)


if __name__ == "__main__":
    unittest.main()
