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
