import importlib
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


class TargetRepoSpeedKpiTests(unittest.TestCase):
    def test_export_target_repo_speed_kpi_latest(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.target_repo_speed_kpi")
        with tempfile.TemporaryDirectory() as tmp_dir:
            runs_root = Path(tmp_dir)
            self._write_run_file(
                runs_root / "alpha-onboard-20260420090000.json",
                flow_kind="live_attach",
                write_status=None,
                write_tier=None,
                evidence_link="artifacts/a-onboard/contract.txt",
            )
            self._write_run_file(
                runs_root / "alpha-daily-deny-20260420100000.json",
                flow_kind="live_attach",
                write_status="denied",
                write_tier="medium",
                evidence_link="artifacts/a-daily-deny/contract.txt",
            )
            self._write_run_file(
                runs_root / "alpha-daily-allow-20260420103000.json",
                flow_kind="live_attach",
                write_status="completed",
                write_tier="medium",
                evidence_link="artifacts/a-daily-allow/contract.txt",
            )

            snapshot = module.export_target_repo_speed_kpi(
                target_repo_runs_root=runs_root,
                window_kind="latest",
                window_size=5,
            )
            self.assertEqual(snapshot.record_count, 1)
            record = snapshot.records[0]
            self.assertEqual(record.target, "alpha")
            self.assertEqual(record.total_daily_runs, 1)
            self.assertEqual(record.fallback_rate, 0.0)
            self.assertEqual(record.medium_risk_loop_success_ratio, 1.0)
            self.assertEqual(record.latest_evidence_ref, "artifacts/a-daily-allow/contract.txt")
            self.assertGreaterEqual(record.onboarding_latency_seconds or 0, 0)

    def test_export_target_repo_speed_kpi_rolling_detects_fallback_and_retry(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.target_repo_speed_kpi")
        with tempfile.TemporaryDirectory() as tmp_dir:
            runs_root = Path(tmp_dir)
            self._write_run_file(
                runs_root / "beta-onboard-20260420090000.json",
                flow_kind="live_attach",
                write_status=None,
                write_tier=None,
                evidence_link="artifacts/b-onboard/contract.txt",
            )
            self._write_run_file(
                runs_root / "beta-daily-deny-20260420100000.json",
                flow_kind="manual_handoff",
                write_status="denied",
                write_tier="medium",
                evidence_link="artifacts/b-daily-deny/contract.txt",
            )
            self._write_run_file(
                runs_root / "beta-daily-allow-20260420110000.json",
                flow_kind="live_attach",
                write_status="completed",
                write_tier="medium",
                evidence_link="artifacts/b-daily-allow/contract.txt",
            )

            snapshot = module.export_target_repo_speed_kpi(
                target_repo_runs_root=runs_root,
                window_kind="rolling",
                window_size=10,
            )
            self.assertEqual(snapshot.record_count, 1)
            record = snapshot.records[0]
            self.assertEqual(record.total_daily_runs, 2)
            self.assertEqual(record.deny_to_success_retries, 1)
            self.assertEqual(record.fallback_rate, 0.5)
            self.assertEqual(record.medium_risk_loop_success_ratio, 0.5)

    def test_export_target_repo_speed_kpi_cli_writes_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runs_root = Path(tmp_dir) / "runs"
            runs_root.mkdir(parents=True)
            output_path = Path(tmp_dir) / "kpi-latest.json"
            self._write_run_file(
                runs_root / "gamma-onboard-20260420090000.json",
                flow_kind="live_attach",
                write_status=None,
                write_tier=None,
                evidence_link="artifacts/g-onboard/contract.txt",
            )
            self._write_run_file(
                runs_root / "gamma-daily-allow-20260420100000.json",
                flow_kind="live_attach",
                write_status="completed",
                write_tier="medium",
                evidence_link="artifacts/g-daily/contract.txt",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/export-target-repo-speed-kpi.py",
                    "--runs-root",
                    str(runs_root),
                    "--window-kind",
                    "latest",
                    "--window-size",
                    "5",
                    "--output",
                    str(output_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["window_kind"], "latest")
            self.assertEqual(payload["record_count"], 1)
            self.assertEqual(payload["records"][0]["target"], "gamma")

    def _write_run_file(
        self,
        path: Path,
        *,
        flow_kind: str,
        write_status: str | None,
        write_tier: str | None,
        evidence_link: str,
    ) -> None:
        payload = {
            "runtime_check": {
                "payload": {
                    "request_gate": {
                        "payload": {
                            "session_identity": {
                                "flow_kind": flow_kind,
                            }
                        }
                    },
                    "verify_attachment": {"evidence_link": evidence_link},
                    "write_execute": (
                        {
                            "execution_status": write_status,
                            "write_tier": write_tier,
                            "session_identity": {"flow_kind": flow_kind},
                        }
                        if write_status is not None
                        else None
                    ),
                }
            }
        }
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
