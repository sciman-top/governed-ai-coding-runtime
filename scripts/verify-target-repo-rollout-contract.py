from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_PATH = ROOT / "docs" / "targets" / "target-repo-rollout-contract.json"
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"
DEFAULT_RUNTIME_FLOW_PRESET_PATH = ROOT / "scripts" / "runtime-flow-preset.ps1"


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json object required: {path}")
    return data


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _has_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _add_error(errors: list[dict[str, str]], code: str, detail: str) -> None:
    errors.append({"code": code, "detail": detail})


def _validate_one_click_entrypoint(
    contract: dict[str, Any],
    runtime_flow_preset_path: Path,
    errors: list[dict[str, str]],
) -> None:
    entrypoint = contract.get("canonical_one_click_entrypoint")
    if not isinstance(entrypoint, dict):
        _add_error(errors, "missing_one_click_entrypoint", "canonical_one_click_entrypoint must be an object")
        return

    script_ref = entrypoint.get("script")
    if script_ref != "scripts/runtime-flow-preset.ps1":
        _add_error(
            errors,
            "unexpected_one_click_script",
            "canonical one-click script must be scripts/runtime-flow-preset.ps1",
        )

    all_feature_args = _as_string_list(entrypoint.get("all_targets_apply_all_features_args"))
    for required_arg in ("-AllTargets", "-ApplyAllFeatures"):
        if required_arg not in all_feature_args:
            _add_error(
                errors,
                "missing_all_features_arg",
                f"all_targets_apply_all_features_args must include {required_arg}",
            )

    baseline_milestone_args = _as_string_list(entrypoint.get("feature_baseline_and_milestone_args"))
    for required_arg in ("-AllTargets", "-ApplyFeatureBaselineAndMilestoneCommit", "-MilestoneTag"):
        if required_arg not in baseline_milestone_args:
            _add_error(
                errors,
                "missing_baseline_milestone_arg",
                f"feature_baseline_and_milestone_args must include {required_arg}",
            )

    if not runtime_flow_preset_path.exists():
        _add_error(errors, "runtime_flow_preset_missing", f"missing script: {runtime_flow_preset_path}")
        return

    source = runtime_flow_preset_path.read_text(encoding="utf-8")
    for arg in sorted(set(all_feature_args + baseline_milestone_args)):
        if not arg.startswith("-"):
            continue
        parameter = "$" + arg[1:]
        if parameter not in source:
            _add_error(
                errors,
                "one_click_arg_not_implemented",
                f"{arg} is declared by the rollout contract but not implemented in runtime-flow-preset.ps1",
            )

    for field in _as_string_list(entrypoint.get("required_json_fields")):
        if field not in source:
            _add_error(
                errors,
                "one_click_json_field_not_emitted",
                f"runtime-flow-preset.ps1 must emit JSON field or result field: {field}",
            )


def _validate_feature_registry(
    contract: dict[str, Any],
    baseline_overrides: dict[str, Any],
    errors: list[dict[str, str]],
) -> None:
    features = contract.get("target_profile_features")
    if not isinstance(features, list) or not features:
        _add_error(errors, "missing_target_profile_features", "target_profile_features must be a non-empty list")
        return

    contract_fields: set[str] = set()
    feature_ids: set[str] = set()
    required_modes = {
        "apply_all_features",
        "feature_baseline_only",
        "feature_baseline_and_milestone_commit",
    }
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            _add_error(errors, "invalid_feature_entry", f"target_profile_features[{index}] must be an object")
            continue

        feature_id = feature.get("feature_id")
        if not isinstance(feature_id, str) or not feature_id.strip():
            _add_error(errors, "invalid_feature_id", f"target_profile_features[{index}].feature_id is required")
        elif feature_id in feature_ids:
            _add_error(errors, "duplicate_feature_id", f"duplicate feature_id: {feature_id}")
        else:
            feature_ids.add(feature_id)

        fields = _as_string_list(feature.get("baseline_fields"))
        if not fields:
            _add_error(errors, "missing_feature_baseline_fields", f"{feature_id or index} must declare baseline_fields")
        for field in fields:
            contract_fields.add(field)
            if field not in baseline_overrides:
                _add_error(
                    errors,
                    "feature_field_missing_from_baseline",
                    f"{feature_id or index} declares {field}, but baseline.required_profile_overrides does not define it",
                )

        modes = set(_as_string_list(feature.get("rollout_modes")))
        if "apply_all_features" not in modes:
            _add_error(
                errors,
                "feature_not_in_apply_all_features",
                f"{feature_id or index} must be covered by apply_all_features",
            )
        unknown_modes = modes - required_modes
        if unknown_modes:
            _add_error(
                errors,
                "unknown_feature_rollout_mode",
                f"{feature_id or index} declares unknown rollout mode(s): {', '.join(sorted(unknown_modes))}",
            )

    for field in sorted(baseline_overrides.keys()):
        if field not in contract_fields:
            _add_error(
                errors,
                "baseline_field_not_in_rollout_contract",
                f"baseline.required_profile_overrides.{field} is not registered in target_profile_features",
            )


def _validate_capability_classification(
    contract: dict[str, Any],
    baseline_overrides: dict[str, Any],
    errors: list[dict[str, str]],
) -> None:
    capabilities = contract.get("target_repo_capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        _add_error(errors, "missing_target_repo_capabilities", "target_repo_capabilities must be a non-empty list")
        return

    features = contract.get("target_profile_features")
    feature_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(features, list):
        for feature in features:
            if not isinstance(feature, dict):
                continue
            feature_id = feature.get("feature_id")
            if isinstance(feature_id, str) and feature_id.strip():
                feature_by_id[feature_id] = feature

    allowed_scopes = {
        "profile_baseline",
        "runtime_orchestrated",
        "repo_local_artifact",
        "runtime_only",
    }
    capability_ids: set[str] = set()
    profile_baseline_fields: set[str] = set()
    for index, capability in enumerate(capabilities):
        if not isinstance(capability, dict):
            _add_error(errors, "invalid_capability_entry", f"target_repo_capabilities[{index}] must be an object")
            continue

        capability_id = capability.get("capability_id")
        if not isinstance(capability_id, str) or not capability_id.strip():
            _add_error(errors, "invalid_capability_id", f"target_repo_capabilities[{index}].capability_id is required")
            continue
        if capability_id in capability_ids:
            _add_error(errors, "duplicate_capability_id", f"duplicate capability_id: {capability_id}")
        capability_ids.add(capability_id)

        scope = capability.get("distribution_scope")
        if scope not in allowed_scopes:
            _add_error(
                errors,
                "invalid_capability_distribution_scope",
                f"{capability_id}.distribution_scope must be one of: {', '.join(sorted(allowed_scopes))}",
            )
            continue

        reason = capability.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            _add_error(errors, "missing_capability_reason", f"{capability_id} must explain its distribution decision")

        fields = _as_string_list(capability.get("baseline_fields"))
        if scope == "profile_baseline":
            if not fields:
                _add_error(errors, "profile_capability_missing_fields", f"{capability_id} must declare baseline_fields")
            feature = feature_by_id.get(capability_id)
            if feature is None:
                _add_error(
                    errors,
                    "profile_capability_missing_rollout_feature",
                    f"{capability_id} is profile_baseline but missing from target_profile_features",
                )
            else:
                feature_fields = set(_as_string_list(feature.get("baseline_fields")))
                missing_from_feature = sorted(set(fields) - feature_fields)
                if missing_from_feature:
                    _add_error(
                        errors,
                        "profile_capability_field_missing_from_feature",
                        f"{capability_id} baseline field(s) not present in target_profile_features: {', '.join(missing_from_feature)}",
                    )
            for field in fields:
                profile_baseline_fields.add(field)
                if field not in baseline_overrides:
                    _add_error(
                        errors,
                        "profile_capability_field_missing_from_baseline",
                        f"{capability_id} declares {field}, but baseline.required_profile_overrides does not define it",
                    )
        elif fields:
            _add_error(
                errors,
                "non_profile_capability_declares_baseline_fields",
                f"{capability_id} is {scope} and must not declare baseline_fields",
            )

    for feature_id in sorted(feature_by_id.keys()):
        if feature_id not in capability_ids:
            _add_error(
                errors,
                "rollout_feature_missing_capability_classification",
                f"{feature_id} is in target_profile_features but missing from target_repo_capabilities",
            )

    for field in sorted(baseline_overrides.keys()):
        if field not in profile_baseline_fields:
            _add_error(
                errors,
                "baseline_field_missing_profile_capability",
                f"baseline.required_profile_overrides.{field} is not classified as a profile_baseline capability field",
            )


def _validate_milestone_auto_commit(
    contract: dict[str, Any],
    baseline_overrides: dict[str, Any],
    errors: list[dict[str, str]],
) -> None:
    requirements = contract.get("milestone_auto_commit")
    if not isinstance(requirements, dict):
        _add_error(errors, "missing_milestone_auto_commit", "milestone_auto_commit must be an object")
        return

    baseline_field = requirements.get("baseline_field")
    if not isinstance(baseline_field, str) or not baseline_field.strip():
        _add_error(errors, "missing_auto_commit_baseline_field", "milestone_auto_commit.baseline_field is required")
        return

    policy = baseline_overrides.get(baseline_field)
    if not isinstance(policy, dict):
        _add_error(
            errors,
            "auto_commit_policy_missing_from_baseline",
            f"baseline.required_profile_overrides.{baseline_field} must be an object",
        )
        return

    if policy.get("enabled") is not True:
        _add_error(errors, "auto_commit_policy_not_enabled", f"{baseline_field}.enabled must be true")

    required_trigger = requirements.get("required_trigger", "milestone")
    if required_trigger not in _as_string_list(policy.get("on")):
        _add_error(
            errors,
            "auto_commit_policy_missing_trigger",
            f"{baseline_field}.on must include {required_trigger}",
        )

    if requirements.get("require_all_required_gates_pass") is True and policy.get("require_all_required_gates_pass") is not True:
        _add_error(
            errors,
            "auto_commit_policy_gate_guard_missing",
            f"{baseline_field}.require_all_required_gates_pass must be true",
        )

    markers = set(_as_string_list(policy.get("milestone_markers")))
    for marker in _as_string_list(requirements.get("required_markers")):
        if marker not in markers:
            _add_error(
                errors,
                "auto_commit_policy_missing_marker",
                f"{baseline_field}.milestone_markers must include {marker}",
            )

    template = policy.get("commit_message_template")
    if not isinstance(template, str) or not template.strip():
        _add_error(
            errors,
            "auto_commit_policy_template_missing",
            f"{baseline_field}.commit_message_template must be a non-empty Chinese template",
        )
        return

    if requirements.get("message_language") == "zh-CN" and not _has_cjk(template):
        _add_error(
            errors,
            "auto_commit_policy_template_not_chinese",
            f"{baseline_field}.commit_message_template must contain Chinese text",
        )

    for token in _as_string_list(requirements.get("required_message_tokens")):
        if token not in template:
            _add_error(
                errors,
                "auto_commit_policy_template_missing_token",
                f"{baseline_field}.commit_message_template must include {token}",
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that target-repo features are forced through the unified one-click rollout contract."
    )
    parser.add_argument("--contract-path", default=str(DEFAULT_CONTRACT_PATH))
    parser.add_argument("--baseline-path", default=str(DEFAULT_BASELINE_PATH))
    parser.add_argument("--runtime-flow-preset-path", default=str(DEFAULT_RUNTIME_FLOW_PRESET_PATH))
    args = parser.parse_args()

    contract_path = Path(args.contract_path).resolve(strict=False)
    baseline_path = Path(args.baseline_path).resolve(strict=False)
    runtime_flow_preset_path = Path(args.runtime_flow_preset_path).resolve(strict=False)

    errors: list[dict[str, str]] = []
    if not contract_path.exists():
        raise SystemExit(f"contract file not found: {contract_path}")
    if not baseline_path.exists():
        raise SystemExit(f"baseline file not found: {baseline_path}")

    contract = _load_json(contract_path)
    baseline = _load_json(baseline_path)
    baseline_overrides = baseline.get("required_profile_overrides")
    if not isinstance(baseline_overrides, dict) or not baseline_overrides:
        raise SystemExit("baseline.required_profile_overrides must be a non-empty object")

    sync_revision = contract.get("sync_revision")
    if not isinstance(sync_revision, str) or not sync_revision.strip():
        _add_error(errors, "contract_sync_revision_missing", "contract.sync_revision must be a non-empty string")

    _validate_one_click_entrypoint(
        contract=contract,
        runtime_flow_preset_path=runtime_flow_preset_path,
        errors=errors,
    )
    _validate_feature_registry(
        contract=contract,
        baseline_overrides=baseline_overrides,
        errors=errors,
    )
    _validate_capability_classification(
        contract=contract,
        baseline_overrides=baseline_overrides,
        errors=errors,
    )
    _validate_milestone_auto_commit(
        contract=contract,
        baseline_overrides=baseline_overrides,
        errors=errors,
    )

    output = {
        "status": "pass" if not errors else "fail",
        "contract_path": str(contract_path),
        "baseline_path": str(baseline_path),
        "runtime_flow_preset_path": str(runtime_flow_preset_path),
        "sync_revision": sync_revision,
        "capability_count": len(contract.get("target_repo_capabilities", []))
        if isinstance(contract.get("target_repo_capabilities"), list)
        else 0,
        "feature_count": len(contract.get("target_profile_features", []))
        if isinstance(contract.get("target_profile_features"), list)
        else 0,
        "baseline_field_count": len(baseline_overrides),
        "errors": errors,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
