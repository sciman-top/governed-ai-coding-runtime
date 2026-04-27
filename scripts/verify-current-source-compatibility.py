from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "docs" / "architecture" / "current-source-compatibility-policy.json"
TEXT_EXTENSIONS = {".md", ".json", ".py", ".ps1", ".yaml", ".yml", ".txt"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify current-source compatibility policy.")
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
        result = assert_current_source_compatibility(
            repo_root=Path(args.repo_root),
            policy_path=Path(args.policy),
            as_of=as_of,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def assert_current_source_compatibility(*, repo_root: Path, policy_path: Path, as_of: dt.date | None = None) -> dict:
    result = inspect_current_source_compatibility(repo_root=repo_root, policy_path=policy_path, as_of=as_of)
    failures: list[str] = []
    if result["expired"]:
        failures.append(
            f"current-source review expired at {result['review_expires_at']}; refresh external-source compatibility"
        )
    if result["missing_doc_refs"]:
        failures.append("missing doc refs: " + ", ".join(result["missing_doc_refs"]))
    if result["missing_evidence_refs"]:
        failures.append("missing evidence refs: " + ", ".join(result["missing_evidence_refs"]))
    if result["forbidden_pattern_hits"]:
        failures.append("forbidden active source patterns found: " + ", ".join(result["forbidden_pattern_hits"]))
    if result["protocols_missing_kernel_semantics"]:
        failures.append(
            "protocol boundaries missing required kernel semantics: "
            + ", ".join(result["protocols_missing_kernel_semantics"])
        )

    if failures:
        raise ValueError("; ".join(failures))
    return result


def inspect_current_source_compatibility(
    *, repo_root: Path, policy_path: Path, as_of: dt.date | None = None
) -> dict:
    resolved_root = repo_root.resolve(strict=False)
    policy = _load_policy(policy_path)
    today = as_of or dt.date.today()
    reviewed_on = _parse_iso_date(policy["reviewed_on"], "reviewed_on")
    review_expires_at = _parse_iso_date(policy["review_expires_at"], "review_expires_at")
    if reviewed_on > review_expires_at:
        raise ValueError("reviewed_on must be on or before review_expires_at")

    missing_doc_refs = _collect_missing_doc_refs(resolved_root, policy["required_doc_refs"])
    missing_evidence_refs = _collect_missing_files(resolved_root, policy["evidence_refs"])
    forbidden_pattern_hits = _collect_forbidden_pattern_hits(resolved_root, policy["forbidden_active_patterns"])
    protocols_missing_kernel_semantics = _collect_protocol_kernel_failures(policy)

    return {
        "status": "pass",
        "policy_path": policy_path.resolve(strict=False).as_posix(),
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "reviewed_on": reviewed_on.isoformat(),
        "review_expires_at": review_expires_at.isoformat(),
        "as_of": today.isoformat(),
        "expired": policy["status"] == "enforced" and review_expires_at < today,
        "source_ids": [source["source_id"] for source in policy["sources"]],
        "protocol_ids": [boundary["protocol_id"] for boundary in policy["protocol_boundaries"]],
        "kernel_owned_semantics": policy["kernel_owned_semantics"],
        "missing_doc_refs": missing_doc_refs,
        "missing_evidence_refs": missing_evidence_refs,
        "forbidden_pattern_hits": forbidden_pattern_hits,
        "protocols_missing_kernel_semantics": protocols_missing_kernel_semantics,
    }


def _load_policy(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"current-source policy is not readable: {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"current-source policy is invalid JSON: {path} ({exc.msg})") from exc

    if not isinstance(payload, dict):
        raise ValueError("current-source policy must be a JSON object")
    for field in ("policy_id", "status", "reviewed_on", "review_expires_at", "compatibility_claim", "rollback_ref"):
        _require_string(payload, field)
    if payload["status"] not in {"observe", "enforced", "waived"}:
        raise ValueError("current-source policy status is invalid")
    _parse_iso_date(payload["reviewed_on"], "reviewed_on")
    _parse_iso_date(payload["review_expires_at"], "review_expires_at")
    payload["kernel_owned_semantics"] = _require_string_list(
        payload.get("kernel_owned_semantics"),
        "kernel_owned_semantics",
    )

    _validate_sources(payload.get("sources"))
    _validate_protocol_boundaries(payload.get("protocol_boundaries"), set(payload["kernel_owned_semantics"]))
    _validate_doc_refs(payload.get("required_doc_refs"), "required_doc_refs")
    _validate_forbidden_patterns(payload.get("forbidden_active_patterns"))
    payload["evidence_refs"] = _require_string_list(payload.get("evidence_refs"), "evidence_refs")
    return payload


def _validate_sources(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("sources must be a non-empty list")
    seen: set[str] = set()
    for index, source in enumerate(value):
        if not isinstance(source, dict):
            raise ValueError(f"sources[{index}] must be an object")
        for field in ("source_id", "url", "source_kind", "reviewed_version"):
            _require_string(source, field, prefix=f"sources[{index}]")
        source_id = source["source_id"]
        if source_id in seen:
            raise ValueError(f"duplicate source_id: {source_id}")
        seen.add(source_id)
        parsed = urlparse(source["url"])
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(f"sources[{index}].url must be an https URL")
        _require_string_list(source.get("boundary_assertions"), f"sources[{index}].boundary_assertions")


def _validate_protocol_boundaries(value: object, allowed_semantics: set[str]) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("protocol_boundaries must be a non-empty list")
    seen: set[str] = set()
    for index, boundary in enumerate(value):
        if not isinstance(boundary, dict):
            raise ValueError(f"protocol_boundaries[{index}] must be an object")
        for field in ("protocol_id", "integration_owner", "required_mapping"):
            _require_string(boundary, field, prefix=f"protocol_boundaries[{index}]")
        protocol_id = boundary["protocol_id"]
        if protocol_id in seen:
            raise ValueError(f"duplicate protocol_id: {protocol_id}")
        seen.add(protocol_id)
        semantics = _require_string_list(
            boundary.get("kernel_owned_semantics"),
            f"protocol_boundaries[{index}].kernel_owned_semantics",
        )
        unknown = sorted(set(semantics) - allowed_semantics)
        if unknown:
            raise ValueError(f"protocol_boundaries[{index}] references unknown kernel semantics: {', '.join(unknown)}")
        _require_string_list(boundary.get("forbidden_claims"), f"protocol_boundaries[{index}].forbidden_claims")


def _validate_doc_refs(value: object, field_name: str) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    for index, ref in enumerate(value):
        if not isinstance(ref, dict):
            raise ValueError(f"{field_name}[{index}] must be an object")
        _require_string(ref, "path", prefix=f"{field_name}[{index}]")
        _require_string(ref, "contains", prefix=f"{field_name}[{index}]")


def _validate_forbidden_patterns(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("forbidden_active_patterns must be a non-empty list")
    for index, guard in enumerate(value):
        if not isinstance(guard, dict):
            raise ValueError(f"forbidden_active_patterns[{index}] must be an object")
        _require_string(guard, "pattern", prefix=f"forbidden_active_patterns[{index}]")
        _require_string_list(guard.get("scan_roots"), f"forbidden_active_patterns[{index}].scan_roots")


def _collect_missing_doc_refs(repo_root: Path, refs: list[dict]) -> list[str]:
    missing: list[str] = []
    for ref in refs:
        path = repo_root / ref["path"]
        if not path.exists():
            missing.append(f"{ref['path']}:missing")
            continue
        text = path.read_text(encoding="utf-8")
        if ref["contains"] not in text:
            missing.append(f"{ref['path']}:missing-token")
    return missing


def _collect_missing_files(repo_root: Path, refs: list[str]) -> list[str]:
    return sorted(ref for ref in refs if not (repo_root / ref).exists())


def _collect_forbidden_pattern_hits(repo_root: Path, guards: list[dict]) -> list[str]:
    hits: list[str] = []
    for guard in guards:
        pattern = guard["pattern"]
        for path in _iter_scan_files(repo_root, guard["scan_roots"]):
            if path.name == "current-source-compatibility-policy.json":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if pattern in text:
                hits.append(f"{path.relative_to(repo_root).as_posix()}:{pattern}")
    return hits


def _iter_scan_files(repo_root: Path, scan_roots: list[str]) -> list[Path]:
    files: list[Path] = []
    for scan_root in scan_roots:
        path = repo_root / scan_root
        if not path.exists():
            continue
        if path.is_file():
            if path.suffix.lower() in TEXT_EXTENSIONS:
                files.append(path)
            continue
        for child in sorted(path.rglob("*")):
            if child.is_file() and child.suffix.lower() in TEXT_EXTENSIONS:
                files.append(child)
    return sorted(set(files))


def _collect_protocol_kernel_failures(policy: dict) -> list[str]:
    required = set(policy["kernel_owned_semantics"])
    failures: list[str] = []
    for boundary in policy["protocol_boundaries"]:
        semantics = set(boundary["kernel_owned_semantics"])
        if not semantics.intersection(required):
            failures.append(boundary["protocol_id"])
    return failures


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
