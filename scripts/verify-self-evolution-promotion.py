from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_ROOT = ROOT / "docs" / "change-evidence" / "self-evolution-promotions"
DEFAULT_SCHEMA_PATH = ROOT / "schemas" / "jsonschema" / "self-evolution-promotion-controller.schema.json"
REQUIRED_LANES = {
    "policy_mutation",
    "skill_enablement",
    "push_or_merge",
}
DISABLED_GUARDS = {
    "automatic_policy_mutation",
    "automatic_skill_enablement",
    "automatic_push_or_merge",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify governed self-evolution promotion controller artifacts.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--artifact", default=None, help="Promotion controller artifact path; defaults to latest.")
    args = parser.parse_args()

    try:
        result = verify_self_evolution_promotion(
            repo_root=Path(args.repo_root),
            artifact_path=Path(args.artifact) if args.artifact else None,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def verify_self_evolution_promotion(*, repo_root: Path, artifact_path: Path | None = None) -> dict:
    root = repo_root.resolve(strict=False)
    path = _resolve_artifact_path(root=root, artifact_path=artifact_path)
    if path is None:
        raise ValueError("self-evolution promotion controller artifact is missing")
    payload = verify_self_evolution_promotion_artifact(artifact_path=path)
    return {
        "status": "pass",
        "artifact_path": _display_path(path=path, root=root),
        "as_of": payload.get("as_of"),
        "promotion_stage": payload.get("promotion_stage"),
        "effective_change_allowed": bool(payload.get("effective_change_allowed")),
        "selector_next_action": payload.get("selector_next_action"),
        "lane_status": {
            lane["lane"]: {
                "status": lane.get("status"),
                "automatic_enabled": bool(lane.get("automatic_enabled")),
                "next_action": lane.get("next_action"),
            }
            for lane in payload.get("control_lanes", [])
        },
    }


def verify_self_evolution_promotion_artifact(*, artifact_path: Path) -> dict:
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    invalid_reasons: list[str] = []

    invalid_reasons.extend(_validate_artifact_schema(payload=payload, schema_path=DEFAULT_SCHEMA_PATH))

    if payload.get("artifact_type") != "self_evolution_promotion_controller_report":
        invalid_reasons.append("artifact_type_must_be_self_evolution_promotion_controller_report")
    if payload.get("effective_change_allowed") is not False:
        invalid_reasons.append("effective_change_allowed_must_be_false")

    guards = payload.get("guards") or {}
    for guard_key in sorted(DISABLED_GUARDS):
        if guards.get(guard_key) is not False:
            invalid_reasons.append(f"{guard_key}_must_be_false")
    if guards.get("requires_human_review_before_effective_change") is not True:
        invalid_reasons.append("requires_human_review_before_effective_change_must_be_true")

    lanes = payload.get("control_lanes")
    if not isinstance(lanes, list):
        invalid_reasons.append("control_lanes_must_be_list")
        lanes = []
    lane_ids = {lane.get("lane") for lane in lanes if isinstance(lane, dict)}
    if lane_ids != REQUIRED_LANES:
        invalid_reasons.append("control_lanes_must_cover_policy_skill_push")
    for lane in lanes:
        if not isinstance(lane, dict):
            invalid_reasons.append("control_lane_must_be_object")
            continue
        if lane.get("automatic_enabled") is not False:
            invalid_reasons.append(f"lane_{lane.get('lane')}_automatic_enabled_must_be_false")
        if not str(lane.get("status") or "").strip():
            invalid_reasons.append(f"lane_{lane.get('lane')}_status_missing")
        if not str(lane.get("next_action") or "").strip():
            invalid_reasons.append(f"lane_{lane.get('lane')}_next_action_missing")

    trigger_model = payload.get("trigger_model") or {}
    if trigger_model.get("automatic_effective_change") is not False:
        invalid_reasons.append("trigger_model_automatic_effective_change_must_be_false")
    if trigger_model.get("recommended_operator_action") != "SelfEvolutionPromotionPlan":
        invalid_reasons.append("recommended_operator_action_must_be_SelfEvolutionPromotionPlan")

    if not str(payload.get("rollback") or "").strip():
        invalid_reasons.append("rollback_must_be_present")
    if not str(payload.get("as_of") or "").strip():
        invalid_reasons.append("as_of_must_be_present")
    else:
        try:
            dt.date.fromisoformat(str(payload["as_of"]))
        except ValueError:
            invalid_reasons.append("as_of_must_be_iso_date")

    if invalid_reasons:
        raise ValueError("invalid self-evolution promotion controller: " + ", ".join(invalid_reasons))
    return payload


def _validate_artifact_schema(*, payload: Any, schema_path: Path) -> list[str]:
    if not schema_path.exists():
        return [f"schema_file_missing:{schema_path.as_posix()}"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    _validate_json_schema(value=payload, schema=schema, root_schema=schema, path="$", errors=errors)
    if errors:
        return ["schema_validation_failed:" + ";".join(errors)]
    return []


def _validate_json_schema(*, value: Any, schema: dict, root_schema: dict, path: str, errors: list[str]) -> None:
    if "$ref" in schema:
        schema = _resolve_local_ref(root_schema=root_schema, ref=str(schema["$ref"]))

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}:enum")
        return

    expected_type = schema.get("type")
    if expected_type is not None and not _matches_json_type(value=value, expected_type=expected_type):
        errors.append(f"{path}:type")
        return

    if expected_type == "object" or "properties" in schema:
        if not isinstance(value, dict):
            errors.append(f"{path}:object")
            return
        properties = schema.get("properties") or {}
        for required_key in schema.get("required", []):
            if required_key not in value:
                errors.append(f"{path}.{required_key}:required")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}.{key}:additional")
        for key, child_schema in properties.items():
            if key in value:
                _validate_json_schema(
                    value=value[key],
                    schema=child_schema,
                    root_schema=root_schema,
                    path=f"{path}.{key}",
                    errors=errors,
                )
        return

    if expected_type == "array" or "items" in schema:
        if not isinstance(value, list):
            errors.append(f"{path}:array")
            return
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{path}:minItems")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_json_schema(
                    value=item,
                    schema=item_schema,
                    root_schema=root_schema,
                    path=f"{path}[{index}]",
                    errors=errors,
                )
        return

    if schema.get("format") == "date" and isinstance(value, str):
        try:
            dt.date.fromisoformat(value)
        except ValueError:
            errors.append(f"{path}:format_date")


def _resolve_local_ref(*, root_schema: dict, ref: str) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported schema ref: {ref}")
    current: Any = root_schema
    for segment in ref[2:].split("/"):
        segment = segment.replace("~1", "/").replace("~0", "~")
        current = current[segment]
    if not isinstance(current, dict):
        raise ValueError(f"schema ref does not point to an object: {ref}")
    return current


def _matches_json_type(*, value: Any, expected_type: object) -> bool:
    if isinstance(expected_type, list):
        return any(_matches_json_type(value=value, expected_type=item) for item in expected_type)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    return True


def _resolve_artifact_path(*, root: Path, artifact_path: Path | None) -> Path | None:
    if artifact_path is not None:
        path = artifact_path if artifact_path.is_absolute() else root / artifact_path
        if not path.exists():
            raise ValueError(f"self-evolution promotion controller artifact does not exist: {artifact_path}")
        return path.resolve(strict=False)
    candidates = sorted((root / "docs" / "change-evidence" / "self-evolution-promotions").glob("*-self-evolution-promotion-controller.json"))
    return candidates[-1].resolve(strict=False) if candidates else None


def _display_path(*, path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.resolve(strict=False).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
