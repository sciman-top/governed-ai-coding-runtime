from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = ROOT / "docs" / "architecture" / "host-capability-claim-upgrade-policy.json"

VALID_STATUS = {"observe", "enforced", "waived"}
REQUIRED_SURFACE_FIELDS = {
    "host_family",
    "surface_class",
    "attach_mode",
    "adapter_tier",
    "degrade_reason",
    "verification_refs",
    "evidence_refs",
}
FAIL_CLOSED_VALUES = {"fail_closed"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify host capability claim-upgrade policy alignment.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--policy-path", default=str(DEFAULT_POLICY_PATH))
    parser.add_argument("--as-of", default=None, help="ISO date for expiry checks; defaults to today.")
    args = parser.parse_args()

    as_of = dt.date.today()
    if args.as_of:
        try:
            as_of = dt.date.fromisoformat(args.as_of)
        except ValueError:
            print(f"invalid --as-of date: {args.as_of}", file=sys.stderr)
            return 1

    try:
        result = assert_host_capability_claim_upgrade_policy(
            repo_root=Path(args.repo_root),
            policy_path=Path(args.policy_path),
            as_of=as_of,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def assert_host_capability_claim_upgrade_policy(*, repo_root: Path, policy_path: Path, as_of: dt.date | None = None) -> dict:
    result = inspect_host_capability_claim_upgrade_policy(repo_root=repo_root, policy_path=policy_path, as_of=as_of)
    failures: list[str] = []
    if result["expired"]:
        failures.append(f"policy expired at {result['review_expires_at']}")
    if result["missing_surface_fields"]:
        failures.append("missing canonical surface fields: " + ", ".join(result["missing_surface_fields"]))
    if result["invalid_fail_closed_defaults"]:
        failures.append("invalid fail-closed defaults: " + ", ".join(result["invalid_fail_closed_defaults"]))
    if result["missing_rules"]:
        failures.append("missing rules: " + ", ".join(result["missing_rules"]))
    if result["missing_refs"]:
        failures.append("missing refs: " + ", ".join(result["missing_refs"]))
    if result["missing_required_doc_text"]:
        failures.append("missing required doc text: " + ", ".join(result["missing_required_doc_text"]))
    if failures:
        raise ValueError("host capability claim-upgrade policy verification failed: " + "; ".join(failures))
    return result


def inspect_host_capability_claim_upgrade_policy(*, repo_root: Path, policy_path: Path, as_of: dt.date | None = None) -> dict:
    root = repo_root.resolve(strict=False)
    policy = _load_policy(policy_path)
    today = as_of or dt.date.today()
    reviewed_on = _parse_iso_date(policy["reviewed_on"], "reviewed_on")
    review_expires_at = _parse_iso_date(policy["review_expires_at"], "review_expires_at")
    if reviewed_on > review_expires_at:
        raise ValueError("reviewed_on must be on or before review_expires_at")

    surface_fields = set(policy.get("canonical_surface_fields") or [])
    missing_surface_fields = sorted(REQUIRED_SURFACE_FIELDS - surface_fields)

    fail_closed_defaults = policy.get("fail_closed_defaults") or {}
    invalid_fail_closed_defaults = sorted(
        key
        for key, value in fail_closed_defaults.items()
        if value not in FAIL_CLOSED_VALUES
    )
    for required_key in (
        "missing_surface_field",
        "missing_verification_refs",
        "missing_evidence_refs",
        "historical_certification_without_fresh_recovery",
        "fresh_but_degraded_posture",
    ):
        if required_key not in fail_closed_defaults:
            invalid_fail_closed_defaults.append(required_key)
    invalid_fail_closed_defaults = sorted(set(invalid_fail_closed_defaults))

    rules = policy.get("upgrade_rules") or []
    rule_ids = {str(item.get("claim_scope") or "").strip() for item in rules if isinstance(item, dict)}
    missing_rules = sorted({"codex_live_native_attach_upgrade", "wording_refresh_only", "backlog_candidate_trigger"} - rule_ids)

    refs = [str(item) for item in policy.get("evidence_refs") or []]
    refs.extend(str(item.get("path") or "") for item in policy.get("required_doc_refs") or [])
    missing_refs = sorted(ref for ref in refs if ref and not (root / ref).exists())

    missing_required_doc_text: list[str] = []
    for item in policy.get("required_doc_refs") or []:
        if not isinstance(item, dict):
            continue
        path_value = str(item.get("path") or "").strip()
        token = str(item.get("contains") or "").strip()
        if not path_value or not token:
            continue
        path = root / path_value
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if token not in text:
            missing_required_doc_text.append(f"{path_value}:{token}")

    return {
        "status": "pass",
        "policy_path": policy_path.resolve(strict=False).as_posix(),
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "reviewed_on": reviewed_on.isoformat(),
        "review_expires_at": review_expires_at.isoformat(),
        "as_of": today.isoformat(),
        "expired": policy["status"] == "enforced" and review_expires_at < today,
        "missing_surface_fields": missing_surface_fields,
        "invalid_fail_closed_defaults": invalid_fail_closed_defaults,
        "missing_rules": missing_rules,
        "missing_refs": missing_refs,
        "missing_required_doc_text": missing_required_doc_text,
    }


def _load_policy(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"host capability claim-upgrade policy is not readable: {path} ({exc})") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"host capability claim-upgrade policy is invalid JSON: {path} ({exc.msg})") from exc
    if not isinstance(payload, dict):
        raise ValueError("host capability claim-upgrade policy must be a JSON object")
    for field in ("policy_id", "status", "reviewed_on", "review_expires_at", "decision_claim", "rollback_ref"):
        _require_string(payload, field)
    if payload["status"] not in VALID_STATUS:
        raise ValueError("host capability claim-upgrade policy status is invalid")
    _require_string_list(payload.get("canonical_surface_fields"), "canonical_surface_fields")
    if not isinstance(payload.get("fail_closed_defaults"), dict):
        raise ValueError("fail_closed_defaults must be an object")
    if not isinstance(payload.get("upgrade_rules"), list) or not payload["upgrade_rules"]:
        raise ValueError("upgrade_rules must be a non-empty list")
    if not isinstance(payload.get("required_doc_refs"), list) or not payload["required_doc_refs"]:
        raise ValueError("required_doc_refs must be a non-empty list")
    _require_string_list(payload.get("evidence_refs"), "evidence_refs")
    return payload


def _require_string(payload: dict, field_name: str) -> None:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")


def _require_string_list(value: object, field_name: str) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name} must only contain non-empty strings")


def _parse_iso_date(value: str, field_name: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO date") from exc


if __name__ == "__main__":
    raise SystemExit(main())
