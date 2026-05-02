import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "audit-target-repo-gate-speed.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("audit_target_repo_gate_speed", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


class TargetRepoGateSpeedAuditTests(unittest.TestCase):
    def test_audit_passes_for_layered_profile_and_effect_evidence(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo = workspace / "repo-a"
            _write_json(
                repo / ".governed-ai" / "repo-profile.json",
                {
                    "gate_timeout_seconds": 300,
                    "quick_gate_commands": [
                        {
                            "id": "test",
                            "command": "python -m unittest tests.test_fast",
                            "timeout_seconds": 120,
                            "satisfies_gate_ids": ["test", "contract"],
                        }
                    ],
                    "full_gate_commands": [
                        {"id": "build", "command": "python -m compileall .", "timeout_seconds": 300},
                        {"id": "test", "command": "python -m unittest", "timeout_seconds": 300},
                        {"id": "contract", "command": "python -m unittest tests.test_contract", "timeout_seconds": 300},
                    ],
                },
            )
            catalog = workspace / "catalog.json"
            _write_json(
                catalog,
                {
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo),
                            "primary_language": "python",
                            "quick_test_command": "python -m unittest tests.test_fast",
                        }
                    }
                },
            )
            serial = workspace / "serial.json"
            parallel = workspace / "parallel.json"
            _write_json(
                serial,
                {
                    "batch_elapsed_seconds": 100,
                    "failure_count": 0,
                    "batch_timed_out": False,
                    "results": [{"target": "repo-a", "target_duration_ms": 100000, "exit_code": 0}],
                },
            )
            _write_json(
                parallel,
                {
                    "batch_elapsed_seconds": 40,
                    "failure_count": 0,
                    "batch_timed_out": False,
                    "results": [{"target": "repo-a", "target_duration_ms": 40000, "exit_code": 0}],
                },
            )

            report = module.audit(
                repo_root=workspace,
                catalog_path=catalog,
                quick_timeout_budget_seconds=180,
                full_timeout_budget_seconds=600,
                serial_result_path=serial,
                parallel_result_path=parallel,
            )

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["error_count"], 0)
            self.assertEqual(report["effect_summary"]["speedup_ratio"], 2.5)
            self.assertEqual(report["targets"][0]["quick_gate_summary"]["covered_gate_ids"], ["contract", "test"])

    def test_audit_fails_when_required_gate_timeout_is_missing(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo = workspace / "repo-a"
            _write_json(
                repo / ".governed-ai" / "repo-profile.json",
                {
                    "quick_gate_commands": [{"id": "test", "command": "python -m unittest tests.test_fast"}],
                    "full_gate_commands": [{"id": "build", "command": "python -m compileall ."}],
                },
            )
            catalog = workspace / "catalog.json"
            _write_json(
                catalog,
                {
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo),
                            "primary_language": "python",
                            "quick_test_skip_reason": "No safe smaller slice.",
                        }
                    }
                },
            )

            report = module.audit(
                repo_root=workspace,
                catalog_path=catalog,
                quick_timeout_budget_seconds=180,
                full_timeout_budget_seconds=600,
                serial_result_path=None,
                parallel_result_path=None,
            )

            self.assertEqual(report["status"], "fail")
            codes = {finding["code"] for finding in report["findings"]}
            self.assertIn("missing_timeout", codes)
            self.assertIn("missing_required_gate_ids", codes)

    def test_cli_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo = workspace / "repo-a"
            _write_json(
                repo / ".governed-ai" / "repo-profile.json",
                {
                    "gate_timeout_seconds": 300,
                    "quick_gate_commands": [
                        {
                            "id": "test",
                            "command": "python -m unittest tests.test_fast",
                            "timeout_seconds": 120,
                            "satisfies_gate_ids": ["test", "contract"],
                        }
                    ],
                    "full_gate_commands": [
                        {"id": "build", "command": "python -m compileall .", "timeout_seconds": 300},
                        {"id": "test", "command": "python -m unittest", "timeout_seconds": 300},
                        {"id": "contract", "command": "python -m unittest tests.test_contract", "timeout_seconds": 300},
                    ],
                },
            )
            catalog = workspace / "catalog.json"
            output = workspace / "audit.json"
            _write_json(
                catalog,
                {
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo),
                            "primary_language": "python",
                            "quick_test_command": "python -m unittest tests.test_fast",
                        }
                    }
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--repo-root",
                    str(workspace),
                    "--catalog",
                    str(catalog),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            summary = json.loads(completed.stdout)
            self.assertEqual(summary["status"], "pass")
            self.assertTrue(output.exists())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["report_kind"], "target_repo_gate_speed_audit")


if __name__ == "__main__":
    unittest.main()
