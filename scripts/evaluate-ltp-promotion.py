from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "docs" / "architecture" / "ltp-autonomous-promotion-policy.json"
VALID_STATUS = {"observe", "enforced", "waived"}
VALID_CURRENT_DECISIONS = {"defer", "watch", "triggered", "candidate", "implemented", "partially_covered"}
VALID_AUTONOMOUS_DECISIONS = {"not_selected", "auto_selected", "owner_directed_selected"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate autonomous LTP promotion readiness.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--as-of", default=None, help="ISO date used for expiry checks; defaults to today.")
    args = parser.parse_args()

    as_of = dt.date.today()
    if args.as_of:
        try:
            as_of = dt.date.fromisoformat(args.as_of)
        except ValueError:
            print(f"invalid --as-of date: {args.as_of}", file=sys.stderr)
            return 1

    try:
        result = assert_ltp_promotion_policy(
            repo_root=Path(args.repo_root),
            policy_path=Path(args.policy),
            as_of=as_of,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def assert_ltp_promotion_policy(*, repo_root: Path, policy_path: Path, as_of: dt.date | None = None) -> dict:
    result = inspect_ltp_promotion_policy(repo_root=repo_root, policy_path=policy_path, as_of=as_of)
    failures: list[str] = []
    if result["expired"]:
        failures.append(
            f"LTP promotion review expired at {result['review_expires_at']}; refresh promotion scope fence"
        )
    if result["missing_refs"]:
        failures.append("missing refs: " + ", ".join(result["missing_refs"]))
    if result["missing_required_doc_text"]:
        failures.append("missing required doc text: " + ", ".join(result["missing_required_doc_text"]))
    if result["invalid_selection_reasons"]:
        failures.append("invalid LTP selection: " + ", ".join(result["invalid_selection_reasons"]))

    if failures:
        raise ValueError("; ".join(failures))
    return result


def inspect_ltp_promotion_policy(*, repo_root: Path, policy_path: Path, as_of: dt.date | None = None) -> dict:
    resolved_root = repo_root.resolve(strict=False)
    policy = _load_policy(policy_path)
    today = as_of or dt.date.today()
    reviewed_on = _parse_iso_date(policy["reviewed_on"], "reviewed_on")
    review_expires_at = _parse_iso_date(policy["review_expires_at"], "review_expires_at")
    if reviewed_on > review_expires_at:
        raise ValueError("reviewed_on must be on or before review_expires_at")

    refs = _collect_refs(policy)
    missing_refs = sorted(ref for ref in refs if ref and not (resolved_root / ref).exists())
    missing_required_doc_text = _collect_missing_required_doc_text(policy, resolved_root)
    invalid_selection_reasons = _collect_invalid_selection_reasons(policy)
    selected = [package for package in policy["packages"] if package["autonomous_decision"] == "auto_selected"]
    owner_directed = [
        package for package in policy["packages"] if package["autonomous_decision"] == "owner_directed_selected"
    ]

    selected_package = selected[0]["package_id"] if len(selected) == 1 and not invalid_selection_reasons else None
    decision = "auto_select" if selected_package else "defer_all"
    if owner_directed and not selected_package:
        decision = "owner_directed_scope_required"

    return {
        "status": "pass",
        "policy_path": policy_path.resolve(strict=False).as_posix(),
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "reviewed_on": reviewed_on.isoformat(),
        "review_expires_at": review_expires_at.isoformat(),
        "as_of": today.isoformat(),
        "expired": policy["status"] == "enforced" and review_expires_at < today,
        "autonomous_mode_enabled": bool(policy["autonomous_mode"]["enabled"]),
        "decision": decision,
        "should_promote": selected_package is not None,
        "selected_package": selected_package,
        "auto_selected_count": len(selected),
        "owner_directed_count": len(owner_directed),
        "package_results": [
            {
                "package_id": package["package_id"],
                "name": package["name"],
                "current_decision": package["current_decision"],
                "autonomous_decision": package["autonomous_decision"],
                "should_promote": package["package_id"] == selected_package,
                "why_not_now": package.get("why_not_now", ""),
            }
            for package in policy["packages"]
        ],
        "missing_refs": missing_refs,
        "missing_required_doc_text": missing_required_doc_text,
        "invalid_selection_reasons": invalid_selection_reasons,
    }


def _load_policy(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"LTP promotion policy is not readable: {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"LTP promotion policy is invalid JSON: {path} ({exc.msg})") from exc

    if not isinstance(payload, dict):
        raise ValueError("LTP promotion policy must be a JSON object")
    for field in ("policy_id", "status", "reviewed_on", "review_expires_at", "decision_claim", "rollback_ref"):
        _require_string(payload, field)
    if payload["status"] not in VALID_STATUS:
        raise ValueError("LTP promotion policy status is invalid")
    _parse_iso_date(payload["reviewed_on"], "reviewed_on")
    _parse_iso_date(payload["review_expires_at"], "review_expires_at")
    _validate_autonomous_mode(payload.get("autonomous_mode"))
    _require_string_list(payload.get("global_required_refs"), "global_required_refs")
    _require_string_list(payload.get("decision_invariants"), "decision_invariants")
    _validate_packages(payload.get("packages"))
    _validate_doc_refs(payload.get("required_doc_refs"))
    _require_string_list(payload.get("evidence_refs"), "evidence_refs")
    return payload


def _validate_autonomous_mode(value: object) -> None:
    if not isinstance(value, dict):
        raise ValueError("autonomous_mode must be an object")
    for field in (
        "enabled",
        "requires_scope_fence_ref",
        "requires_full_gate_ref",
        "requires_current_source_guard",
        "owner_directed_allowed",
        "owner_directed_requires_ref",
    ):
        if not isinstance(value.get(field), bool):
            raise ValueError(f"autonomous_mode.{field} must be boolean")
    max_auto = value.get("max_auto_selected_packages")
    if not isinstance(max_auto, int) or max_auto < 1:
        raise ValueError("autonomous_mode.max_auto_selected_packages must be a positive integer")
    _require_string(value, "safe_default", prefix="autonomous_mode")


def _validate_packages(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("packages must be a non-empty list")
    seen: set[str] = set()
    for index, package in enumerate(value):
        if not isinstance(package, dict):
            raise ValueError(f"packages[{index}] must be an object")
        for field in ("package_id", "name", "current_decision", "autonomous_decision", "why_not_now"):
            _require_string(package, field, prefix=f"packages[{index}]")
        package_id = package["package_id"]
        if package_id in seen:
            raise ValueError(f"duplicate package_id: {package_id}")
        seen.add(package_id)
        if package["current_decision"] not in VALID_CURRENT_DECISIONS:
            raise ValueError(f"packages[{index}].current_decision is invalid")
        if package["autonomous_decision"] not in VALID_AUTONOMOUS_DECISIONS:
            raise ValueError(f"packages[{index}].autonomous_decision is invalid")
        _require_string_list(package.get("target_stack"), f"packages[{index}].target_stack")
        _require_string_list(package.get("trigger_evidence_required"), f"packages[{index}].trigger_evidence_required")
        _require_string_list(package.get("current_evidence_refs"), f"packages[{index}].current_evidence_refs")
        _require_string_list(package.get("promotion_requirements"), f"packages[{index}].promotion_requirements")


def _validate_doc_refs(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("required_doc_refs must be a non-empty list")
    for index, ref in enumerate(value):
        if not isinstance(ref, dict):
            raise ValueError(f"required_doc_refs[{index}] must be an object")
        _require_string(ref, "path", prefix=f"required_doc_refs[{index}]")
        _require_string(ref, "contains", prefix=f"required_doc_refs[{index}]")


def _collect_refs(policy: dict) -> set[str]:
    refs: set[str] = set(policy["global_required_refs"])
    refs.update(policy["evidence_refs"])
    for ref in policy["required_doc_refs"]:
        refs.add(ref["path"])
    for package in policy["packages"]:
        refs.update(package["current_evidence_refs"])
        for optional_ref in ("scope_fence_ref", "full_gate_ref", "owner_directed_ref", "rollback_ref"):
            value = package.get(optional_ref)
            if isinstance(value, str) and value.strip():
                refs.add(value.strip())
    return refs


def _collect_invalid_selection_reasons(policy: dict) -> list[str]:
    reasons: list[str] = []
    mode = policy["autonomous_mode"]
    selected = [package for package in policy["packages"] if package["autonomous_decision"] == "auto_selected"]
    owner_directed = [
        package for package in policy["packages"] if package["autonomous_decision"] == "owner_directed_selected"
    ]
    if selected and not mode["enabled"]:
        reasons.append("auto_selected package exists while autonomous mode is disabled")
    if len(selected) > mode["max_auto_selected_packages"]:
        reasons.append(
            f"auto_selected package count {len(selected)} exceeds limit {mode['max_auto_selected_packages']}"
        )
    if selected and owner_directed:
        reasons.append("auto_selected and owner_directed_selected packages cannot be mixed in one review")
    for package in selected:
        if package["current_decision"] not in {"triggered", "candidate"}:
            reasons.append(f"{package['package_id']} auto_selected without triggered/candidate decision")
        if mode["requires_scope_fence_ref"] and not _has_string(package, "scope_fence_ref"):
            reasons.append(f"{package['package_id']} auto_selected without scope_fence_ref")
        if mode["requires_full_gate_ref"] and not _has_string(package, "full_gate_ref"):
            reasons.append(f"{package['package_id']} auto_selected without full_gate_ref")
    if owner_directed and not mode["owner_directed_allowed"]:
        reasons.append("owner_directed_selected package exists while owner-directed mode is disabled")
    for package in owner_directed:
        if mode["owner_directed_requires_ref"] and not _has_string(package, "owner_directed_ref"):
            reasons.append(f"{package['package_id']} owner_directed_selected without owner_directed_ref")
        if package["current_decision"] not in {"triggered", "candidate", "watch"}:
            reasons.append(f"{package['package_id']} owner_directed_selected from invalid current decision")
    return reasons


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


def _has_string(payload: dict, field: str) -> bool:
    value = payload.get(field)
    return isinstance(value, str) and bool(value.strip())


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
