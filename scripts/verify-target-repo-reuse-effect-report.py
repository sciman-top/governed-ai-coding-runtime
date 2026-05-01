from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNS_ROOT = ROOT / "docs" / "change-evidence" / "target-repo-runs"
DEFAULT_REPORT_PATH = DEFAULT_RUNS_ROOT / "effect-report-classroomtoolkit.json"


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json object required: {path}")
    return data


def inspect_effect_report(*, report_path: Path = DEFAULT_REPORT_PATH, runs_root: Path = DEFAULT_RUNS_ROOT) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not report_path.exists():
        return {
            "status": "fail",
            "errors": [
                {
                    "code": "effect_report_missing",
                    "detail": f"effect report not found: {report_path}",
                }
            ],
        }

    report = _load_json(report_path)
    for field_name in (
        "target",
        "baseline_run_ref",
        "after_run_ref",
        "baseline_metrics",
        "after_metrics",
        "rolling_kpi",
        "decision",
        "backlog_candidates",
        "verifier_ref",
    ):
        if field_name not in report:
            errors.append({"code": "missing_report_field", "detail": f"report is missing field {field_name}"})

    baseline_ref = report.get("baseline_run_ref")
    after_ref = report.get("after_run_ref")
    baseline_path = runs_root / baseline_ref if isinstance(baseline_ref, str) else None
    after_path = runs_root / after_ref if isinstance(after_ref, str) else None
    if isinstance(baseline_ref, str):
        if not baseline_path.exists():
            errors.append({"code": "baseline_run_ref_missing", "detail": f"baseline run ref not found: {baseline_ref}"})
    if isinstance(after_ref, str):
        if not after_path.exists():
            errors.append({"code": "after_run_ref_missing", "detail": f"after run ref not found: {after_ref}"})
    if baseline_ref == after_ref:
        errors.append({"code": "baseline_after_same", "detail": "baseline_run_ref and after_run_ref must differ"})

    expected_after_metrics: dict[str, Any] | None = None
    expected_rolling_kpi: dict[str, Any] | None = None
    if not errors and baseline_path is not None and after_path is not None:
        builder = _load_effect_report_builder()
        try:
            baseline_entry = _run_entry_from_path(builder, baseline_path)
            after_entry = _run_entry_from_path(builder, after_path)
            expected_baseline_metrics = builder._extract_metrics(baseline_entry)
            expected_after_metrics = builder._extract_metrics(after_entry)
            _append_metric_drift_errors(
                errors=errors,
                code="baseline_metrics_drift",
                report_metrics=report.get("baseline_metrics", {}),
                expected_metrics=expected_baseline_metrics,
                fields=[
                    "overall_status",
                    "required_entrypoint_policy_present",
                    "codex_capability_status",
                    "adapter_tier",
                    "flow_kind",
                    "gate_order",
                    "gate_results",
                    "evidence_complete",
                ],
            )
            _append_metric_drift_errors(
                errors=errors,
                code="after_metrics_drift",
                report_metrics=report.get("after_metrics", {}),
                expected_metrics=expected_after_metrics,
                fields=[
                    "overall_status",
                    "required_entrypoint_policy_present",
                    "codex_capability_status",
                    "adapter_tier",
                    "flow_kind",
                    "gate_order",
                    "gate_results",
                    "evidence_complete",
                ],
            )
            expected_rolling_kpi = _build_expected_kpi(builder, target=str(report.get("target", "")), runs_root=runs_root)
            _append_metric_drift_errors(
                errors=errors,
                code="rolling_kpi_drift",
                report_metrics=report.get("rolling_kpi", {}),
                expected_metrics=expected_rolling_kpi,
                fields=[
                    "total_daily_runs",
                    "fallback_rate",
                    "problem_run_rate",
                    "problem_recovery_retries",
                    "latest_problem_run_ref",
                    "latest_evidence_ref",
                ],
            )
            expected_decision, expected_candidates = builder._decision_for(expected_after_metrics, expected_rolling_kpi)
            if report.get("decision") != expected_decision:
                errors.append(
                    {
                        "code": "decision_drift",
                        "detail": f"decision expected {expected_decision!r} from run refs, got {report.get('decision')!r}",
                    }
                )
            expected_candidate_ids = {item.get("candidate_id") for item in expected_candidates}
            reported_candidate_ids = {
                item.get("candidate_id")
                for item in report.get("backlog_candidates", [])
                if isinstance(item, dict)
            }
            if expected_candidate_ids != reported_candidate_ids:
                errors.append(
                    {
                        "code": "backlog_candidates_drift",
                        "detail": "backlog candidate ids do not match recomputed run evidence",
                    }
                )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append({"code": "run_ref_recompute_failed", "detail": str(exc)})

    after_metrics = report.get("after_metrics", {})
    if not isinstance(after_metrics, dict):
        after_metrics = {}
    rolling_kpi = report.get("rolling_kpi", {})
    if not isinstance(rolling_kpi, dict):
        rolling_kpi = {}
    backlog_candidates = report.get("backlog_candidates", [])
    if not isinstance(backlog_candidates, list):
        backlog_candidates = []

    has_adjustable_issue = (
        after_metrics.get("codex_capability_status") not in {"ready", None}
        or after_metrics.get("overall_status") != "pass"
        or not after_metrics.get("evidence_complete", False)
        or (rolling_kpi.get("problem_run_rate") or 0.0) > 0
    )
    if has_adjustable_issue and not backlog_candidates:
        errors.append(
            {
                "code": "issue_without_candidate",
                "detail": "effect report observed reusable issues but did not emit backlog_candidates",
            }
        )

    if report.get("verifier_ref") != "python scripts/verify-target-repo-reuse-effect-report.py":
        errors.append(
            {
                "code": "verifier_ref_drift",
                "detail": "effect report verifier_ref must point to python scripts/verify-target-repo-reuse-effect-report.py",
            }
        )

    return {
        "status": "pass" if not errors else "fail",
        "report_path": str(report_path),
        "target": report.get("target"),
        "decision": report.get("decision"),
        "backlog_candidate_count": len(backlog_candidates),
        "errors": errors,
    }


def _load_effect_report_builder():
    script_path = ROOT / "scripts" / "build-target-repo-reuse-effect-report.py"
    spec = importlib.util.spec_from_file_location("build_target_repo_reuse_effect_report_for_verifier", script_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load effect report builder: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_entry_from_path(builder, path: Path) -> dict[str, Any]:
    match = builder._RUN_FILE_PATTERN.match(path.name)
    if not match:
        raise ValueError(f"run ref filename does not match expected target-flow-stamp shape: {path.name}")
    return {
        "path": path,
        "flow": match.group("flow"),
        "stamp": match.group("stamp"),
        "timestamp": datetime.strptime(match.group("stamp"), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc),
        "payload": _load_json(path),
    }


def _build_expected_kpi(builder, *, target: str, runs_root: Path) -> dict[str, Any]:
    if not target:
        raise ValueError("effect report target must be a non-empty string")
    kpi_snapshot = builder.export_target_repo_speed_kpi(
        target_repo_runs_root=runs_root,
        window_kind="rolling",
        window_size=5,
    )
    kpi_record = next((builder.asdict(record) for record in kpi_snapshot.records if record.target == target), None)
    if kpi_record is None:
        raise ValueError(f"rolling KPI record not found for target {target}")
    return kpi_record


def _append_metric_drift_errors(
    *,
    errors: list[dict[str, str]],
    code: str,
    report_metrics: object,
    expected_metrics: dict[str, Any],
    fields: list[str],
) -> None:
    if not isinstance(report_metrics, dict):
        errors.append({"code": code, "detail": "metrics payload must be an object"})
        return
    mismatches = [
        field
        for field in fields
        if report_metrics.get(field) != expected_metrics.get(field)
    ]
    if mismatches:
        errors.append(
            {
                "code": code,
                "detail": "field mismatch: " + ", ".join(mismatches),
            }
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a target repo reuse effect feedback report.")
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--runs-root", default=str(DEFAULT_RUNS_ROOT))
    args = parser.parse_args()

    result = inspect_effect_report(
        report_path=Path(args.report_path).resolve(strict=False),
        runs_root=Path(args.runs_root).resolve(strict=False),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
