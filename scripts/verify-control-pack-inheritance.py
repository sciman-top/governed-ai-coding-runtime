from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX_PATH = ROOT / "docs" / "architecture" / "control-pack-inheritance-matrix.json"
DEFAULT_CONTROL_PACK_PATH = ROOT / "schemas" / "control-packs" / "minimum-governance-kernel.control-pack.json"
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"
DEFAULT_REPO_PROFILE_SCHEMA_PATH = ROOT / "schemas" / "jsonschema" / "repo-profile.schema.json"
DEFAULT_REPO_PROFILE_PATH = ROOT / ".governed-ai" / "repo-profile.json"
DEFAULT_LIGHT_PACK_PATH = ROOT / ".governed-ai" / "light-pack.json"


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json object required: {path}")
    return data


def _record_na(records: list[dict[str, str]], kind: str, reason: str, evidence_link: str) -> None:
    records.append(
        {
            "kind": kind,
            "reason": reason,
            "alternative_verification": "Use checked-in source contracts and evidence under docs/change-evidence/ while the missing surface is restored.",
            "evidence_link": evidence_link,
            "expires_at": "2026-05-31",
        }
    )


def _has_data_path(data: Any, field_path: str) -> bool:
    current = data
    for part in field_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def _has_schema_path(schema: dict[str, Any], field_path: str) -> bool:
    current: Any = schema
    parts = field_path.split(".")
    for index, part in enumerate(parts):
        if not isinstance(current, dict):
            return False
        if index == 0:
            properties = current.get("properties")
            if not isinstance(properties, dict) or part not in properties:
                return False
            current = properties[part]
            continue
        properties = current.get("properties")
        if not isinstance(properties, dict) or part not in properties:
            return False
        current = properties[part]
    return True


def _flatten_paths(data: Any, prefix: str = "") -> set[str]:
    if not isinstance(data, dict):
        return set()
    paths: set[str] = set()
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        paths.add(path)
        if isinstance(value, dict):
            paths.update(_flatten_paths(value, path))
    return paths


def inspect_control_pack_inheritance(
    *,
    matrix_path: Path = DEFAULT_MATRIX_PATH,
    control_pack_path: Path = DEFAULT_CONTROL_PACK_PATH,
    baseline_path: Path = DEFAULT_BASELINE_PATH,
    repo_profile_schema_path: Path = DEFAULT_REPO_PROFILE_SCHEMA_PATH,
    repo_profile_path: Path = DEFAULT_REPO_PROFILE_PATH,
    light_pack_path: Path = DEFAULT_LIGHT_PACK_PATH,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    na_records: list[dict[str, str]] = []

    required_paths = {
        "matrix_path": matrix_path,
        "control_pack_path": control_pack_path,
        "baseline_path": baseline_path,
        "repo_profile_schema_path": repo_profile_schema_path,
        "repo_profile_path": repo_profile_path,
        "light_pack_path": light_pack_path,
    }
    for label, path in required_paths.items():
        if not path.exists():
            _record_na(na_records, "gate_na", f"required file is missing: {label}", str(path))

    if na_records:
        return {
            "status": "fail",
            "errors": errors,
            "na_records": na_records,
        }

    matrix = _load_json(matrix_path)
    control_pack = _load_json(control_pack_path)
    baseline = _load_json(baseline_path)
    repo_profile_schema = _load_json(repo_profile_schema_path)
    repo_profile = _load_json(repo_profile_path)
    light_pack = _load_json(light_pack_path)

    baseline_overrides = baseline.get("required_profile_overrides")
    if not isinstance(baseline_overrides, dict) or not baseline_overrides:
        errors.append(
            {
                "code": "baseline_required_profile_overrides_missing",
                "detail": "baseline.required_profile_overrides must be a non-empty object",
            }
        )
        baseline_overrides = {}

    unified_entries = matrix.get("unified_governance", [])
    for entry in unified_entries:
        field_path = entry["field_path"]
        if not _has_data_path(control_pack, field_path):
            errors.append(
                {
                    "code": "missing_unified_control_pack_field",
                    "detail": f"control pack is missing unified field path: {field_path}",
                }
            )
        root_name = field_path.split(".", 1)[0]
        if root_name in baseline_overrides:
            errors.append(
                {
                    "code": "unified_field_leaked_to_baseline",
                    "detail": f"baseline.required_profile_overrides must not define unified field root {root_name}",
                }
            )
        if root_name in repo_profile:
            errors.append(
                {
                    "code": "unified_field_leaked_to_repo_profile",
                    "detail": f"repo profile must not inline unified field root {root_name}",
                }
            )
        if root_name in light_pack:
            errors.append(
                {
                    "code": "unified_field_leaked_to_light_pack",
                    "detail": f"light pack must not inline unified field root {root_name}",
                }
            )

    inherited_fields_seen: set[str] = set()
    for entry in matrix.get("target_inherit", []):
        profile_field = entry["profile_field"]
        baseline_field = entry["baseline_field"]
        control_pack_reference = entry["control_pack_reference"]
        if profile_field in inherited_fields_seen:
            errors.append(
                {
                    "code": "duplicate_inherited_profile_field",
                    "detail": f"matrix.target_inherit duplicates profile_field {profile_field}",
                }
            )
        inherited_fields_seen.add(profile_field)
        if baseline_field not in baseline_overrides:
            errors.append(
                {
                    "code": "missing_inherited_baseline_field",
                    "detail": f"baseline.required_profile_overrides is missing {baseline_field}",
                }
            )
        if not _has_schema_path(repo_profile_schema, entry["schema_path"]):
            errors.append(
                {
                    "code": "missing_schema_path",
                    "detail": f"repo-profile.schema.json is missing schema path {entry['schema_path']}",
                }
            )
        if not _has_data_path(repo_profile, profile_field):
            errors.append(
                {
                    "code": "missing_repo_profile_inherited_field",
                    "detail": f"emitted repo profile is missing inherited field {profile_field}",
                }
            )
        if not _has_data_path(control_pack, control_pack_reference):
            errors.append(
                {
                    "code": "missing_control_pack_reference",
                    "detail": f"control pack is missing inherited reference {control_pack_reference}",
                }
            )

    if set(baseline_overrides.keys()) != inherited_fields_seen:
        missing = sorted(set(baseline_overrides.keys()) - inherited_fields_seen)
        extra = sorted(inherited_fields_seen - set(baseline_overrides.keys()))
        if missing:
            errors.append(
                {
                    "code": "baseline_field_missing_from_matrix",
                    "detail": "baseline override field(s) missing from target_inherit: " + ", ".join(missing),
                }
            )
        if extra:
            errors.append(
                {
                    "code": "matrix_inherited_field_missing_from_baseline",
                    "detail": "matrix target_inherit field(s) missing from baseline.required_profile_overrides: "
                    + ", ".join(extra),
                }
            )

    for entry in matrix.get("target_override", []):
        profile_field = entry["profile_field"]
        root_name = profile_field.split(".", 1)[0]
        override_rule = entry["override_rule"]
        if not _has_schema_path(repo_profile_schema, entry["schema_path"]):
            errors.append(
                {
                    "code": "missing_schema_path",
                    "detail": f"repo-profile.schema.json is missing schema path {entry['schema_path']}",
                }
            )
        if root_name in baseline_overrides:
            errors.append(
                {
                    "code": "repo_local_override_claimed_by_baseline",
                    "detail": f"baseline.required_profile_overrides must not own repo-local override field root {root_name}",
                }
            )
        if _has_data_path(repo_profile, profile_field):
            value = repo_profile
            for part in profile_field.split("."):
                value = value[part]
            if override_rule == "must_remain_true" and value is not True:
                errors.append(
                    {
                        "code": "override_field_weakened",
                        "detail": f"{profile_field} must remain true when present in the emitted repo profile",
                    }
                )

    forbidden_roots = {
        blocked_name
        for entry in matrix.get("forbidden_override", [])
        for blocked_name in entry.get("blocked_field_names", [])
    }
    light_pack_paths = _flatten_paths(light_pack)
    for entry in matrix.get("forbidden_override", []):
        for blocked_name in entry["blocked_field_names"]:
            if blocked_name in baseline_overrides:
                errors.append(
                    {
                        "code": "forbidden_override_present_in_baseline",
                        "detail": f"baseline.required_profile_overrides must not define forbidden field {blocked_name}",
                    }
                )
            if blocked_name in repo_profile:
                errors.append(
                    {
                        "code": "forbidden_override_present_in_repo_profile",
                        "detail": f"repo profile must not define forbidden field {blocked_name}",
                    }
                )
            if blocked_name in light_pack_paths or blocked_name in light_pack:
                errors.append(
                    {
                        "code": "forbidden_override_present_in_light_pack",
                        "detail": f"light pack must not define forbidden field {blocked_name}",
                    }
                )

    for root_name in sorted(inherited_fields_seen | {item["profile_field"].split(".", 1)[0] for item in matrix.get("target_override", [])}):
        if root_name in light_pack and root_name not in {"repo_profile_ref"}:
            errors.append(
                {
                    "code": "light_pack_inlines_repo_override",
                    "detail": f"light pack must reference repo profile instead of inlining {root_name}",
                }
            )

    runtime_contract_refs = light_pack.get("runtime_contract_refs")
    if not isinstance(runtime_contract_refs, dict):
        errors.append(
            {
                "code": "light_pack_runtime_contract_refs_missing",
                "detail": "light pack must expose runtime_contract_refs",
            }
        )
    else:
        if runtime_contract_refs.get("repo_profile_schema") != "schemas/jsonschema/repo-profile.schema.json":
            errors.append(
                {
                    "code": "light_pack_repo_profile_schema_ref_drift",
                    "detail": "light pack runtime_contract_refs.repo_profile_schema must point to schemas/jsonschema/repo-profile.schema.json",
                }
            )

    return {
        "status": "pass" if not errors and not na_records else "fail",
        "matrix_path": str(matrix_path),
        "control_pack_path": str(control_pack_path),
        "baseline_path": str(baseline_path),
        "repo_profile_schema_path": str(repo_profile_schema_path),
        "repo_profile_path": str(repo_profile_path),
        "light_pack_path": str(light_pack_path),
        "inherited_field_count": len(matrix.get("target_inherit", [])),
        "override_field_count": len(matrix.get("target_override", [])),
        "forbidden_override_count": len(matrix.get("forbidden_override", [])),
        "errors": errors,
        "na_records": na_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify control-pack inheritance, allowed overrides, and forbidden override surfaces.")
    parser.add_argument("--matrix-path", default=str(DEFAULT_MATRIX_PATH))
    parser.add_argument("--control-pack-path", default=str(DEFAULT_CONTROL_PACK_PATH))
    parser.add_argument("--baseline-path", default=str(DEFAULT_BASELINE_PATH))
    parser.add_argument("--repo-profile-schema-path", default=str(DEFAULT_REPO_PROFILE_SCHEMA_PATH))
    parser.add_argument("--repo-profile-path", default=str(DEFAULT_REPO_PROFILE_PATH))
    parser.add_argument("--light-pack-path", default=str(DEFAULT_LIGHT_PACK_PATH))
    args = parser.parse_args()

    result = inspect_control_pack_inheritance(
        matrix_path=Path(args.matrix_path).resolve(strict=False),
        control_pack_path=Path(args.control_pack_path).resolve(strict=False),
        baseline_path=Path(args.baseline_path).resolve(strict=False),
        repo_profile_schema_path=Path(args.repo_profile_schema_path).resolve(strict=False),
        repo_profile_path=Path(args.repo_profile_path).resolve(strict=False),
        light_pack_path=Path(args.light_pack_path).resolve(strict=False),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
