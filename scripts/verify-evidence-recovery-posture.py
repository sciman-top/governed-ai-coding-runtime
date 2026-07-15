from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify repo-local evidence recovery posture after host feedback stabilizes.")
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
    if result["selector"]["next_action"] != "defer_ltp_and_refresh_evidence":
        failures.append("selector must return defer_ltp_and_refresh_evidence once repo-local evidence is fresh and no LTP package is selected")
    if result["selector"]["evidence_state"] != "fresh":
        failures.append("selector evidence_state must be fresh after host-only feedback and repo-local evidence recover")
    if result["host_feedback"]["status"] != "pass":
        failures.append("host feedback summary must be pass after repo-local evidence recovery")
    if result["host_feedback"]["claude_workload_status"] == "blocked":
        failures.append("claude workload must not remain blocked after recovery")
    if result["selector"]["evidence_blocker"] is not None:
        failures.append("evidence_blocker must be cleared after recovery")

    if failures:
        raise ValueError("; ".join(failures))
    result["status"] = "pass"
    return result


def inspect_evidence_recovery_posture(*, repo_root: Path, as_of: dt.date | None = None) -> dict:
    resolved_root = repo_root.resolve(strict=False)
    today = as_of or dt.date.today()
    selector = _load_module("select_next_work_recovery", resolved_root / "scripts" / "select-next-work.py")

    selector_result = selector.assert_next_work_selection(
        repo_root=resolved_root,
        policy_path=resolved_root / "docs" / "architecture" / "autonomous-next-work-selection-policy.json",
        ltp_policy_path=resolved_root / "docs" / "architecture" / "ltp-autonomous-promotion-policy.json",
        as_of=today,
    )
    host_feedback_details = selector_result.get("auto_detected_inputs", {}).get("details", {}).get("host_feedback", {})
    if not isinstance(host_feedback_details, dict):
        host_feedback_details = {}

    return {
        "status": "inspected",
        "as_of": today.isoformat(),
        "selector": {
            "next_action": selector_result["next_action"],
            "evidence_state": selector_result["evidence_state"],
            "evidence_blocker": selector_result.get("evidence_blocker"),
            "ltp_decision": selector_result["ltp_decision"],
        },
        "host_feedback": {
            "status": host_feedback_details.get("status"),
            "recommendation_count": int(host_feedback_details.get("recommendation_count") or 0),
            "codex_host_status": host_feedback_details.get("codex_host_status"),
            "claude_host_status": host_feedback_details.get("claude_host_status"),
            "claude_workload_status": host_feedback_details.get("claude_workload_status"),
            "input_mode": host_feedback_details.get("input_mode"),
            "acceptance_scope": host_feedback_details.get("acceptance_scope"),
            "hosted_acceptance": bool(host_feedback_details.get("hosted_acceptance")),
        },
    }


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    raise SystemExit(main())
