from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOST_RECOVERY_RULE = "fresh target run with codex_capability_status=ready and adapter_tier=native_attach"
HOST_CLAIM_GUARD = "do not claim native_attach recovery until a fresh target repo run proves it"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify evidence recovery posture after degraded target runs.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--as-of", default=None, help="ISO date used for selector expiry checks; defaults to today.")
    args = parser.parse_args()

    as_of = dt.date.today()
    if args.as_of:
        try:
            as_of = dt.date.fromisoformat(args.as_of)
        except ValueError:
            print(f"invalid --as-of date: {args.as_of}", file=sys.stderr)
            return 1

    try:
        result = assert_evidence_recovery_posture(repo_root=Path(args.repo_root), as_of=as_of)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def assert_evidence_recovery_posture(*, repo_root: Path, as_of: dt.date | None = None) -> dict:
    result = inspect_evidence_recovery_posture(repo_root=repo_root, as_of=as_of)
    failures: list[str] = []
    if result["selector"]["next_action"] != "refresh_evidence_first":
        failures.append("selector must keep choosing refresh_evidence_first while latest target runs are degraded")
    if result["selector"]["evidence_state"] != "stale":
        failures.append("selector evidence_state must remain stale while latest target runs are degraded")
    if result["target_runs"]["status"] != "attention":
        failures.append("target_runs status must be attention for fresh degraded target runs")
    if result["target_runs"]["freshness_status"] != "fresh":
        failures.append("target run evidence must be fresh before this recovery posture can close")
    if result["target_runs"]["degraded_latest_run_count"] < 1:
        failures.append("expected at least one degraded latest target run")
    if result["effect_report"]["decision"] != "adjust":
        failures.append("effect report must keep decision=adjust while host capability recovery is incomplete")
    if not result["effect_report"]["host_capability_candidate_present"]:
        failures.append("effect report must include target-repo-reuse-host-capability-gap candidate")
    if result["effect_report"]["required_recovery_evidence"] != HOST_RECOVERY_RULE:
        failures.append("effect report recovery evidence rule drifted")
    if result["effect_report"]["claim_guard"] != HOST_CLAIM_GUARD:
        failures.append("effect report claim guard drifted")

    if failures:
        raise ValueError("; ".join(failures))
    result["status"] = "pass"
    return result


def inspect_evidence_recovery_posture(*, repo_root: Path, as_of: dt.date | None = None) -> dict:
    resolved_root = repo_root.resolve(strict=False)
    today = as_of or dt.date.today()
    selector = _load_module("select_next_work_recovery", resolved_root / "scripts" / "select-next-work.py")
    host_feedback = _load_module("host_feedback_summary_recovery", resolved_root / "scripts" / "host-feedback-summary.py")

    selector_result = selector.assert_next_work_selection(
        repo_root=resolved_root,
        policy_path=resolved_root / "docs" / "architecture" / "autonomous-next-work-selection-policy.json",
        ltp_policy_path=resolved_root / "docs" / "architecture" / "ltp-autonomous-promotion-policy.json",
        as_of=today,
    )
    feedback = host_feedback.build_host_feedback_summary(repo_root=resolved_root, max_target_runs=5)
    target_runs = _find_dimension(feedback, "target_runs")
    target_details = target_runs.get("details", {})
    degraded_latest_runs = target_details.get("degraded_latest_runs")
    if not isinstance(degraded_latest_runs, list):
        degraded_latest_runs = []

    effect_report = _load_json(
        resolved_root
        / "docs"
        / "change-evidence"
        / "target-repo-runs"
        / "effect-report-classroomtoolkit.json"
    )
    host_candidate = _find_candidate(effect_report, "target-repo-reuse-host-capability-gap")
    remediation_boundary = host_candidate.get("remediation_boundary", {}) if host_candidate else {}

    return {
        "status": "inspected",
        "as_of": today.isoformat(),
        "selector": {
            "next_action": selector_result["next_action"],
            "evidence_state": selector_result["evidence_state"],
            "ltp_decision": selector_result["ltp_decision"],
        },
        "target_runs": {
            "status": target_runs.get("status"),
            "freshness_status": target_details.get("freshness_status"),
            "degraded_latest_run_count": len(degraded_latest_runs),
            "degraded_repos": sorted(
                str(item.get("repo_id")) for item in degraded_latest_runs if isinstance(item, dict)
            ),
        },
        "effect_report": {
            "decision": effect_report.get("decision"),
            "host_capability_candidate_present": bool(host_candidate),
            "required_recovery_evidence": remediation_boundary.get("required_recovery_evidence"),
            "claim_guard": remediation_boundary.get("claim_guard"),
        },
        "recovery_rule": HOST_RECOVERY_RULE,
        "claim_guard": HOST_CLAIM_GUARD,
    }


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"unable to read JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON file: {path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return payload


def _find_dimension(report: dict, dimension_id: str) -> dict:
    for item in report.get("dimensions", []):
        if isinstance(item, dict) and item.get("dimension_id") == dimension_id:
            return item
    raise ValueError(f"host feedback dimension not found: {dimension_id}")


def _find_candidate(report: dict, candidate_id: str) -> dict | None:
    for item in report.get("backlog_candidates", []):
        if isinstance(item, dict) and item.get("candidate_id") == candidate_id:
            return item
    return None


if __name__ == "__main__":
    raise SystemExit(main())
