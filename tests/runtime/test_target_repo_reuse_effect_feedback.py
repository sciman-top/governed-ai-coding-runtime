import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_script(path: str, module_name: str):
    script_path = ROOT / path
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _write_run(path: Path, *, stamp: str, overall_status: str, codex_status: str, flow_kind: str, has_problem: bool) -> None:
    path.write_text(
        json.dumps(
            {
                "overall_status": overall_status,
                "runtime_check": {
                    "payload": {
                        "status": {
                            "attachments": [
                                {
                                    "binding_state": "healthy",
                                    "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                                }
                            ],
                            "codex_capability": {
                                "status": codex_status,
                                "adapter_tier": "process_bridge" if codex_status == "degraded" else "native_attach",
                                "flow_kind": flow_kind,
                            },
                        },
                        "summary": {
                            "overall_status": overall_status,
                            "attachment_health": "healthy",
                        },
                        "verify_attachment": {
                            "results": {"test": "pass", "contract": "pass"},
                            "gate_order": ["test", "contract"],
                            "evidence_link": f"artifacts/{stamp}/contract.txt",
                            "result_artifact_refs": {"contract": f"artifacts/{stamp}/contract.txt"},
                        },
                        "request_gate": {
                            "policy_decision_ref": f"artifacts/{stamp}/policy.json",
                            "payload": {
                                "session_identity": {
                                    "adapter_tier": "process_bridge" if codex_status == "degraded" else "native_attach",
                                    "flow_kind": flow_kind,
                                },
                                "gate_order": ["test", "contract"],
                                "results": {"test": "pass", "contract": "pass"},
                                "evidence_link": f"artifacts/{stamp}/contract.txt",
                            },
                        },
                        "problem_trace": {
                            "has_problem": has_problem,
                            "failure_signature": "summary:fail" if has_problem else "none",
                            "evidence_refs": [f"artifacts/{stamp}/contract.txt"],
                        },
                    }
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


class TargetRepoReuseEffectFeedbackTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("build_target_repo_reuse_effect_report_script", None)
        sys.modules.pop("verify_target_repo_reuse_effect_report_script", None)

    def test_build_effect_report_emits_adjust_decision_for_degraded_after_run(self) -> None:
        build_module = _load_script(
            "scripts/build-target-repo-reuse-effect-report.py",
            "build_target_repo_reuse_effect_report_script",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            runs_root = Path(tmp_dir) / "runs"
            runs_root.mkdir(parents=True)
            _write_run(
                runs_root / "demo-onboard-20260420090000.json",
                stamp="20260420090000",
                overall_status="fail",
                codex_status="ready",
                flow_kind="live_attach",
                has_problem=True,
            )
            _write_run(
                runs_root / "demo-daily-20260420100000.json",
                stamp="20260420100000",
                overall_status="fail",
                codex_status="ready",
                flow_kind="live_attach",
                has_problem=True,
            )
            _write_run(
                runs_root / "demo-daily-20260420120000.json",
                stamp="20260420120000",
                overall_status="pass",
                codex_status="degraded",
                flow_kind="process_bridge",
                has_problem=False,
            )

            report = build_module.build_effect_report(target="demo", runs_root=runs_root)
            self.assertEqual("adjust", report["decision"])
            self.assertEqual("demo-daily-20260420120000.json", report["after_run_ref"])
            self.assertTrue(report["backlog_candidates"])

    def test_verify_effect_report_requires_candidates_when_issue_present(self) -> None:
        verify_module = _load_script(
            "scripts/verify-target-repo-reuse-effect-report.py",
            "verify_target_repo_reuse_effect_report_script",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            runs_root = Path(tmp_dir) / "runs"
            runs_root.mkdir(parents=True)
            _write_run(
                runs_root / "demo-onboard-20260420090000.json",
                stamp="20260420090000",
                overall_status="fail",
                codex_status="ready",
                flow_kind="live_attach",
                has_problem=True,
            )
            _write_run(
                runs_root / "demo-daily-20260420120000.json",
                stamp="20260420120000",
                overall_status="pass",
                codex_status="degraded",
                flow_kind="process_bridge",
                has_problem=False,
            )

            report_path = runs_root / "effect-report-demo.json"
            report_path.write_text(
                json.dumps(
                    {
                        "target": "demo",
                        "baseline_run_ref": "demo-onboard-20260420090000.json",
                        "after_run_ref": "demo-daily-20260420120000.json",
                        "baseline_metrics": {"overall_status": "fail"},
                        "after_metrics": {
                            "overall_status": "pass",
                            "codex_capability_status": "degraded",
                            "evidence_complete": True,
                        },
                        "rolling_kpi": {"problem_run_rate": 0.5},
                        "decision": "adjust",
                        "backlog_candidates": [],
                        "verifier_ref": "python scripts/verify-target-repo-reuse-effect-report.py",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = verify_module.inspect_effect_report(report_path=report_path, runs_root=runs_root)
            self.assertEqual("fail", result["status"])
            codes = {error["code"] for error in result["errors"]}
            self.assertIn("issue_without_candidate", codes)

    def test_verify_effect_report_recomputes_metrics_from_run_refs(self) -> None:
        build_module = _load_script(
            "scripts/build-target-repo-reuse-effect-report.py",
            "build_target_repo_reuse_effect_report_script",
        )
        verify_module = _load_script(
            "scripts/verify-target-repo-reuse-effect-report.py",
            "verify_target_repo_reuse_effect_report_script",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            runs_root = Path(tmp_dir) / "runs"
            runs_root.mkdir(parents=True)
            _write_run(
                runs_root / "demo-onboard-20260420090000.json",
                stamp="20260420090000",
                overall_status="fail",
                codex_status="ready",
                flow_kind="live_attach",
                has_problem=True,
            )
            _write_run(
                runs_root / "demo-daily-20260420120000.json",
                stamp="20260420120000",
                overall_status="pass",
                codex_status="degraded",
                flow_kind="process_bridge",
                has_problem=False,
            )

            report = build_module.build_effect_report(target="demo", runs_root=runs_root)
            report["after_metrics"]["codex_capability_status"] = "ready"
            report["rolling_kpi"]["total_daily_runs"] = 999
            report["backlog_candidates"] = []
            report_path = runs_root / "effect-report-demo.json"
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = verify_module.inspect_effect_report(report_path=report_path, runs_root=runs_root)

        self.assertEqual("fail", result["status"])
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("after_metrics_drift", codes)
        self.assertIn("rolling_kpi_drift", codes)


if __name__ == "__main__":
    unittest.main()
