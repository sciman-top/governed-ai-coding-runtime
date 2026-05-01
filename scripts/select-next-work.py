from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "docs" / "architecture" / "autonomous-next-work-selection-policy.json"
DEFAULT_LTP_POLICY = ROOT / "docs" / "architecture" / "ltp-autonomous-promotion-policy.json"
VALID_STATUS = {"observe", "enforced", "waived"}
VALID_STATE = {"pass", "fail", "unknown"}
VALID_FRESHNESS = {"fresh", "stale", "unknown"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Select the next autonomous work item.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--ltp-policy", default=str(DEFAULT_LTP_POLICY))
    parser.add_argument("--as-of", default=None, help="ISO date used for expiry checks; defaults to today.")
    parser.add_argument("--gate-state", choices=sorted(VALID_STATE), default=None)
    parser.add_argument("--source-state", choices=sorted(VALID_FRESHNESS), default=None)
    parser.add_argument("--evidence-state", choices=sorted(VALID_FRESHNESS), default=None)
    args = parser.parse_args()

    as_of = dt.date.today()
    if args.as_of:
        try:
            as_of = dt.date.fromisoformat(args.as_of)
        except ValueError:
            print(f"invalid --as-of date: {args.as_of}", file=sys.stderr)
            return 1

    try:
        result = assert_next_work_selection(
            repo_root=Path(args.repo_root),
            policy_path=Path(args.policy),
            ltp_policy_path=Path(args.ltp_policy),
            as_of=as_of,
            gate_state=args.gate_state,
            source_state=args.source_state,
            evidence_state=args.evidence_state,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def assert_next_work_selection(
    *,
    repo_root: Path,
    policy_path: Path,
    ltp_policy_path: Path,
    as_of: dt.date | None = None,
    gate_state: str | None = None,
    source_state: str | None = None,
    evidence_state: str | None = None,
) -> dict:
    result = inspect_next_work_selection(
        repo_root=repo_root,
        policy_path=policy_path,
        ltp_policy_path=ltp_policy_path,
        as_of=as_of,
        gate_state=gate_state,
        source_state=source_state,
        evidence_state=evidence_state,
    )
    failures: list[str] = []
    if result["expired"]:
        failures.append(
            f"next-work selection review expired at {result['review_expires_at']}; refresh selector policy"
        )
    if result["missing_refs"]:
        failures.append("missing refs: " + ", ".join(result["missing_refs"]))
    if result["missing_required_doc_text"]:
        failures.append("missing required doc text: " + ", ".join(result["missing_required_doc_text"]))
    if result["invalid_reasons"]:
        failures.append("invalid next-work policy: " + ", ".join(result["invalid_reasons"]))

    if failures:
        raise ValueError("; ".join(failures))
    return result


def inspect_next_work_selection(
    *,
    repo_root: Path,
    policy_path: Path,
    ltp_policy_path: Path,
    as_of: dt.date | None = None,
    gate_state: str | None = None,
    source_state: str | None = None,
    evidence_state: str | None = None,
) -> dict:
    resolved_root = repo_root.resolve(strict=False)
    policy = _load_policy(policy_path)
    today = as_of or dt.date.today()
    reviewed_on = _parse_iso_date(policy["reviewed_on"], "reviewed_on")
    review_expires_at = _parse_iso_date(policy["review_expires_at"], "review_expires_at")
    if reviewed_on > review_expires_at:
        raise ValueError("reviewed_on must be on or before review_expires_at")

    defaults = policy["default_inputs"]
    auto_inputs = _auto_detect_runtime_inputs(repo_root=resolved_root, as_of=today)
    selected_gate_state = gate_state or auto_inputs["gate_state"] or defaults["gate_state"]
    selected_source_state = source_state or auto_inputs["source_state"] or defaults["source_state"]
    selected_evidence_state = evidence_state or auto_inputs["evidence_state"] or defaults["evidence_state"]
    _validate_runtime_state("gate_state", selected_gate_state, VALID_STATE)
    _validate_runtime_state("source_state", selected_source_state, VALID_FRESHNESS)
    _validate_runtime_state("evidence_state", selected_evidence_state, VALID_FRESHNESS)

    ltp = _load_ltp_module().assert_ltp_promotion_policy(
        repo_root=resolved_root,
        policy_path=ltp_policy_path,
        as_of=today,
    )
    next_action, reason, selected_package = _select_action(
        policy=policy,
        gate_state=selected_gate_state,
        source_state=selected_source_state,
        evidence_state=selected_evidence_state,
        ltp=ltp,
    )
    refs = _collect_refs(policy)
    missing_refs = sorted(ref for ref in refs if ref and not (resolved_root / ref).exists())
    missing_required_doc_text = _collect_missing_required_doc_text(policy, resolved_root)
    invalid_reasons = _collect_invalid_reasons(policy, next_action)

    return {
        "status": "pass",
        "policy_path": policy_path.resolve(strict=False).as_posix(),
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "reviewed_on": reviewed_on.isoformat(),
        "review_expires_at": review_expires_at.isoformat(),
        "as_of": today.isoformat(),
        "expired": policy["status"] == "enforced" and review_expires_at < today,
        "gate_state": selected_gate_state,
        "source_state": selected_source_state,
        "evidence_state": selected_evidence_state,
        "auto_detected_inputs": auto_inputs,
        "ltp_decision": ltp["decision"],
        "ltp_should_promote": bool(ltp["should_promote"]),
        "selected_package": selected_package,
        "next_action": next_action,
        "why": reason,
        "missing_refs": missing_refs,
        "missing_required_doc_text": missing_required_doc_text,
        "invalid_reasons": invalid_reasons,
    }


def _select_action(
    *,
    policy: dict,
    gate_state: str,
    source_state: str,
    evidence_state: str,
    ltp: dict,
) -> tuple[str, str, str | None]:
    if gate_state == "fail":
        return "repair_gate_first", _why(policy, "repair_gate_first"), None
    if source_state in {"stale", "unknown"} or evidence_state in {"stale", "unknown"}:
        return "refresh_evidence_first", _why(policy, "refresh_evidence_first"), None
    if ltp["decision"] == "auto_select":
        return "promote_ltp", _why(policy, "promote_ltp"), ltp["selected_package"]
    if ltp["decision"] == "owner_directed_scope_required":
        return "owner_directed_scope_required", _why(policy, "owner_directed_scope_required"), None
    return "defer_ltp_and_refresh_evidence", _why(policy, "defer_ltp_and_refresh_evidence"), None


def _why(policy: dict, action: str) -> str:
    for item in policy["selection_order"]:
        if item["next_action"] == action:
            return item["why"]
    return "No policy reason found."


def _load_policy(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"next-work selection policy is not readable: {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"next-work selection policy is invalid JSON: {path} ({exc.msg})") from exc

    if not isinstance(payload, dict):
        raise ValueError("next-work selection policy must be a JSON object")
    for field in ("policy_id", "status", "reviewed_on", "review_expires_at", "decision_claim", "rollback_ref"):
        _require_string(payload, field)
    if payload["status"] not in VALID_STATUS:
        raise ValueError("next-work selection policy status is invalid")
    _parse_iso_date(payload["reviewed_on"], "reviewed_on")
    _parse_iso_date(payload["review_expires_at"], "review_expires_at")
    _require_string_list(payload.get("allowed_next_actions"), "allowed_next_actions")
    _validate_selection_order(payload.get("selection_order"), set(payload["allowed_next_actions"]))
    _validate_default_inputs(payload.get("default_inputs"))
    _require_string_list(payload.get("invariants"), "invariants")
    _validate_doc_refs(payload.get("required_doc_refs"))
    _require_string_list(payload.get("evidence_refs"), "evidence_refs")
    return payload


def _validate_selection_order(value: object, allowed: set[str]) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("selection_order must be a non-empty list")
    seen_actions: set[str] = set()
    seen_priorities: set[int] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"selection_order[{index}] must be an object")
        priority = item.get("priority")
        if not isinstance(priority, int) or priority < 1:
            raise ValueError(f"selection_order[{index}].priority must be a positive integer")
        if priority in seen_priorities:
            raise ValueError(f"duplicate selection priority: {priority}")
        seen_priorities.add(priority)
        for field in ("condition", "next_action", "why"):
            _require_string(item, field, prefix=f"selection_order[{index}]")
        action = item["next_action"]
        if action not in allowed:
            raise ValueError(f"selection_order[{index}].next_action is not allowed")
        if action in seen_actions:
            raise ValueError(f"duplicate selection action: {action}")
        seen_actions.add(action)


def _validate_default_inputs(value: object) -> None:
    if not isinstance(value, dict):
        raise ValueError("default_inputs must be an object")
    _validate_runtime_state("default_inputs.gate_state", value.get("gate_state"), VALID_STATE)
    _validate_runtime_state("default_inputs.source_state", value.get("source_state"), VALID_FRESHNESS)
    _validate_runtime_state("default_inputs.evidence_state", value.get("evidence_state"), VALID_FRESHNESS)
    _require_string(value, "ltp_policy_ref", prefix="default_inputs")


def _validate_doc_refs(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("required_doc_refs must be a non-empty list")
    for index, ref in enumerate(value):
        if not isinstance(ref, dict):
            raise ValueError(f"required_doc_refs[{index}] must be an object")
        _require_string(ref, "path", prefix=f"required_doc_refs[{index}]")
        _require_string(ref, "contains", prefix=f"required_doc_refs[{index}]")


def _collect_refs(policy: dict) -> set[str]:
    refs: set[str] = set(policy["evidence_refs"])
    refs.add(policy["default_inputs"]["ltp_policy_ref"])
    for ref in policy["required_doc_refs"]:
        refs.add(ref["path"])
    return refs


def _collect_missing_required_doc_text(policy: dict, repo_root: Path) -> list[str]:
    missing: list[str] = []
    for ref in policy["required_doc_refs"]:
        path = repo_root / ref["path"]
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if ref["contains"] not in text:
            missing.append(f"{ref['path']} missing required text: {ref['contains']}")
    return missing


def _collect_invalid_reasons(policy: dict, next_action: str) -> list[str]:
    reasons: list[str] = []
    allowed = set(policy["allowed_next_actions"])
    if next_action not in allowed:
        reasons.append(f"next_action is not allowed: {next_action}")
    expected_actions = {item["next_action"] for item in policy["selection_order"]}
    missing_actions = sorted(allowed - expected_actions)
    if missing_actions:
        reasons.append("allowed actions missing selection rules: " + ", ".join(missing_actions))
    return reasons


def _load_ltp_module():
    module_path = ROOT / "scripts" / "evaluate-ltp-promotion.py"
    spec = importlib.util.spec_from_file_location("evaluate_ltp_promotion_script", module_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load LTP evaluator: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["evaluate_ltp_promotion_script"] = module
    spec.loader.exec_module(module)
    return module


def _load_helper_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load helper module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _auto_detect_runtime_inputs(*, repo_root: Path, as_of: dt.date) -> dict:
    result = {
        "gate_state": "unknown",
        "source_state": "unknown",
        "evidence_state": "unknown",
        "details": {},
    }

    try:
        functional_module = _load_helper_module(
            ROOT / "scripts" / "verify-functional-effectiveness.py",
            "verify_functional_effectiveness_selector",
        )
        functional = functional_module.inspect_functional_effectiveness(repo_root=repo_root, as_of=as_of)
        gate_fail = (
            functional["status"] != "pass"
            or functional["expired"]
            or functional["future_dated"]
            or bool(functional["missing_sections"])
            or any(check["missing_tokens"] for check in functional["proof_checks"])
        )
        result["gate_state"] = "fail" if gate_fail else "pass"
        result["details"]["functional_effectiveness"] = {
            "status": functional["status"],
            "expired": functional["expired"],
            "evidence_date": functional["evidence_date"],
            "evidence_age_days": functional["evidence_age_days"],
        }
    except Exception as exc:
        result["gate_state"] = "fail"
        result["details"]["functional_effectiveness"] = {"status": "error", "error": str(exc)}

    try:
        current_source_module = _load_helper_module(
            ROOT / "scripts" / "verify-current-source-compatibility.py",
            "verify_current_source_compatibility_selector",
        )
        current_source = current_source_module.inspect_current_source_compatibility(
            repo_root=repo_root,
            policy_path=repo_root / "docs" / "architecture" / "current-source-compatibility-policy.json",
            as_of=as_of,
        )
        evolution_module = _load_helper_module(
            ROOT / "scripts" / "evaluate-runtime-evolution.py",
            "evaluate_runtime_evolution_selector",
        )
        evolution = evolution_module.inspect_runtime_evolution_policy(
            repo_root=repo_root,
            policy_path=repo_root / "docs" / "architecture" / "runtime-evolution-policy.json",
            as_of=as_of,
            write_artifacts=False,
            online_source_check=False,
        )
        source_stale = (
            current_source["status"] != "pass"
            or current_source["expired"]
            or bool(current_source["missing_doc_refs"])
            or bool(current_source["missing_evidence_refs"])
            or bool(current_source["forbidden_pattern_hits"])
            or bool(current_source["protocols_missing_kernel_semantics"])
            or evolution["status"] != "pass"
            or evolution["expired"]
            or evolution["stale"]
            or bool(evolution["missing_required_refs"])
            or bool(evolution["invalid_reasons"])
        )
        result["source_state"] = "stale" if source_stale else "fresh"
        result["details"]["current_source"] = {
            "status": current_source["status"],
            "expired": current_source["expired"],
            "review_expires_at": current_source["review_expires_at"],
        }
        result["details"]["runtime_evolution_review"] = {
            "status": evolution["status"],
            "expired": evolution["expired"],
            "stale": evolution["stale"],
            "review_expires_at": evolution["review_expires_at"],
        }
    except Exception as exc:
        result["source_state"] = "stale"
        result["details"]["source_detection"] = {"status": "error", "error": str(exc)}

    try:
        host_feedback_module = _load_helper_module(
            ROOT / "scripts" / "host-feedback-summary.py",
            "host_feedback_summary_selector",
        )
        host_feedback = host_feedback_module.build_host_feedback_summary(repo_root=repo_root, max_target_runs=5)
        target_runs = next(
            (
                item.get("details", {})
                for item in host_feedback.get("dimensions", [])
                if isinstance(item, dict) and item.get("dimension_id") == "target_runs"
            ),
            {},
        )
        degraded_latest_runs = target_runs.get("degraded_latest_runs")
        if not isinstance(degraded_latest_runs, list):
            degraded_latest_runs = []
        effect_module = _load_helper_module(
            ROOT / "scripts" / "verify-target-repo-reuse-effect-report.py",
            "verify_target_repo_effect_selector",
        )
        effect = effect_module.inspect_effect_report(
            report_path=repo_root / "docs" / "change-evidence" / "target-repo-runs" / "effect-report-classroomtoolkit.json",
            runs_root=repo_root / "docs" / "change-evidence" / "target-repo-runs",
        )
        ai_experience_module = _load_helper_module(
            ROOT / "scripts" / "extract-ai-coding-experience.py",
            "extract_ai_coding_experience_selector",
        )
        ai_experience = ai_experience_module.inspect_ai_coding_experience(repo_root=repo_root, as_of=as_of)
        evidence_stale = (
            host_feedback["status"] == "fail"
            or target_runs.get("freshness_status") != "fresh"
            or bool(degraded_latest_runs)
            or effect["status"] != "pass"
            or ai_experience["status"] != "pass"
            or bool(ai_experience["invalid_reasons"])
        )
        result["evidence_state"] = "stale" if evidence_stale else "fresh"
        result["details"]["host_feedback"] = {
            "status": host_feedback["status"],
            "target_run_freshness": target_runs.get("freshness_status"),
            "degraded_latest_run_count": len(degraded_latest_runs),
        }
        result["details"]["effect_feedback"] = {
            "status": effect["status"],
            "decision": effect.get("decision"),
            "backlog_candidate_count": effect.get("backlog_candidate_count"),
        }
        result["details"]["ai_coding_experience"] = {
            "status": ai_experience["status"],
            "proposal_count": ai_experience["proposal_count"],
            "retirement_record_count": ai_experience["retirement_record_count"],
        }
    except Exception as exc:
        result["evidence_state"] = "stale"
        result["details"]["evidence_detection"] = {"status": "error", "error": str(exc)}

    return result


def _validate_runtime_state(field_name: str, value: object, allowed: set[str]) -> None:
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{field_name} must be one of: {', '.join(sorted(allowed))}")


def _parse_iso_date(value: str, field_name: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO date") from exc


def _require_string(payload: dict, field: str, *, prefix: str | None = None) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        name = f"{prefix}.{field}" if prefix else field
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _require_string_list(value: object, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name}[{index}] must be a non-empty string")
        result.append(item.strip())
    return result


if __name__ == "__main__":
    raise SystemExit(main())
