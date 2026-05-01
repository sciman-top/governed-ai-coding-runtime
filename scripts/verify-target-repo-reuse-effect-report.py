from __future__ import annotations

import argparse
import json
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
    if isinstance(baseline_ref, str):
        if not (runs_root / baseline_ref).exists():
            errors.append({"code": "baseline_run_ref_missing", "detail": f"baseline run ref not found: {baseline_ref}"})
    if isinstance(after_ref, str):
        if not (runs_root / after_ref).exists():
            errors.append({"code": "after_run_ref_missing", "detail": f"after run ref not found: {after_ref}"})
    if baseline_ref == after_ref:
        errors.append({"code": "baseline_after_same", "detail": "baseline_run_ref and after_run_ref must differ"})

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
