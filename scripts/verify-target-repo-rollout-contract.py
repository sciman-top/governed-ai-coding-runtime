from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_PATH = ROOT / "docs" / "targets" / "target-repo-rollout-contract.json"
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"
DEFAULT_RUNTIME_FLOW_PRESET_PATH = ROOT / "scripts" / "runtime-flow-preset.ps1"
ALLOWED_MANAGEMENT_MODES = {"replace", "json_merge", "block_on_drift"}
DERIVED_RUNTIME_PROFILE_FIELDS = {"quick_gate_commands", "full_gate_commands", "gate_timeout_seconds"}
CATALOG_PROFILE_FIELDS = {"repo_id", "display_name", "primary_language", "build_commands", "test_commands", "contract_commands"}


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


def _normalize_managed_file_entries(value: Any) -> list[tuple[str, str, str]]:
    if not isinstance(value, list):
        return []

    normalized: list[tuple[str, str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        source = item.get("source")
        management_mode = item.get("management_mode", "replace")
        if not (
            isinstance(path, str)
            and path.strip()
            and isinstance(source, str)
            and source.strip()
            and isinstance(management_mode, str)
            and management_mode.strip()
        ):
            continue
        normalized_mode = management_mode.strip()
        if normalized_mode not in ALLOWED_MANAGEMENT_MODES:
            continue
        normalized.append((path.strip(), source.strip(), normalized_mode))
    return normalized


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

    coding_speed_profile_args = _as_string_list(entrypoint.get("coding_speed_profile_args"))
    for required_arg in ("-AllTargets", "-ApplyCodingSpeedProfile"):
        if required_arg not in coding_speed_profile_args:
            _add_error(
                errors,
                "missing_coding_speed_profile_arg",
                f"coding_speed_profile_args must include {required_arg}",
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
    for arg in sorted(set(all_feature_args + coding_speed_profile_args + baseline_milestone_args)):
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


def _validate_managed_file_rollout(
    contract: dict[str, Any],
    baseline: dict[str, Any],
    errors: list[dict[str, str]],
) -> None:
    rollout = contract.get("managed_file_rollout")
    if not isinstance(rollout, dict):
        _add_error(errors, "missing_managed_file_rollout", "managed_file_rollout must be an object")
        return

    distribution_scope = rollout.get("distribution_scope")
    if distribution_scope != "repo_local_artifact":
        _add_error(
            errors,
            "invalid_managed_file_rollout_scope",
            "managed_file_rollout.distribution_scope must be repo_local_artifact",
        )

    baseline_files = _normalize_managed_file_entries(baseline.get("required_managed_files"))
    contract_files = _normalize_managed_file_entries(rollout.get("required_managed_files"))
    if not baseline_files and contract_files:
        _add_error(
            errors,
            "managed_file_rollout_missing_from_baseline",
            "managed_file_rollout.required_managed_files declares files but baseline.required_managed_files is empty",
        )
        return

    baseline_only = sorted(set(baseline_files) - set(contract_files))
    contract_only = sorted(set(contract_files) - set(baseline_files))
    for path, source, management_mode in baseline_only:
        _add_error(
            errors,
            "managed_file_not_in_rollout_contract",
            f"baseline.required_managed_files entry is not registered in managed_file_rollout: {path} <- {source} ({management_mode})",
        )
    for path, source, management_mode in contract_only:
        _add_error(
            errors,
            "managed_file_not_in_baseline",
            f"managed_file_rollout entry is not present in baseline.required_managed_files: {path} <- {source} ({management_mode})",
        )


def _validate_target_repo_speed_profile_rollout(
    contract: dict[str, Any],
    baseline: dict[str, Any],
    runtime_flow_preset_path: Path,
    errors: list[dict[str, str]],
) -> None:
    rollout = contract.get("target_repo_speed_profile_rollout")
    if not isinstance(rollout, dict):
        _add_error(errors, "missing_target_repo_speed_profile_rollout", "target_repo_speed_profile_rollout must be an object")
        return

    distribution_scope = rollout.get("distribution_scope")
    if distribution_scope != "runtime_orchestrated":
        _add_error(
            errors,
            "invalid_target_repo_speed_profile_rollout_scope",
            "target_repo_speed_profile_rollout.distribution_scope must be runtime_orchestrated",
        )

    policy = baseline.get("target_repo_speed_profile_policy")
    if not isinstance(policy, dict) or not policy:
        _add_error(
            errors,
            "target_repo_speed_profile_policy_missing_from_baseline",
            "baseline.target_repo_speed_profile_policy must be a non-empty object",
        )
        return

    required_policy_fields = set(_as_string_list(rollout.get("required_policy_fields")))
    if not required_policy_fields:
        _add_error(
            errors,
            "missing_target_repo_speed_profile_policy_fields",
            "target_repo_speed_profile_rollout.required_policy_fields must be a non-empty list",
        )
    else:
        baseline_fields = set(policy.keys())
        for field in sorted(baseline_fields - required_policy_fields):
            _add_error(
                errors,
                "target_repo_speed_profile_policy_field_not_in_rollout_contract",
                f"baseline.target_repo_speed_profile_policy.{field} is not registered in target_repo_speed_profile_rollout.required_policy_fields",
            )
        for field in sorted(required_policy_fields - baseline_fields):
            _add_error(
                errors,
                "target_repo_speed_profile_policy_field_missing_from_baseline",
                f"target_repo_speed_profile_rollout.required_policy_fields declares {field}, but baseline.target_repo_speed_profile_policy does not define it",
            )

    coding_speed_profile_args = _as_string_list(rollout.get("coding_speed_profile_args"))
    for required_arg in ("-AllTargets", "-ApplyCodingSpeedProfile"):
        if required_arg not in coding_speed_profile_args:
            _add_error(
                errors,
                "missing_target_repo_speed_profile_rollout_arg",
                f"target_repo_speed_profile_rollout.coding_speed_profile_args must include {required_arg}",
            )

    if runtime_flow_preset_path.exists():
        source = runtime_flow_preset_path.read_text(encoding="utf-8")
        for arg in sorted(set(coding_speed_profile_args)):
            if not arg.startswith("-"):
                continue
            parameter = "$" + arg[1:]
            if parameter not in source:
                _add_error(
                    errors,
                    "target_repo_speed_profile_rollout_arg_not_implemented",
                    f"{arg} is declared by target_repo_speed_profile_rollout but not implemented in runtime-flow-preset.ps1",
                )

        for field in _as_string_list(rollout.get("required_json_fields")):
            if field not in source:
                _add_error(
                    errors,
                    "target_repo_speed_profile_rollout_json_field_not_emitted",
                    f"runtime-flow-preset.ps1 must emit JSON field or result field for target_repo_speed_profile_rollout: {field}",
                )


def _validate_repo_profile_ownership_contract(
    contract: dict[str, Any],
    baseline: dict[str, Any],
    baseline_overrides: dict[str, Any],
    errors: list[dict[str, str]],
) -> None:
    ownership = baseline.get("repo_profile_field_ownership")
    if not isinstance(ownership, dict):
        _add_error(errors, "missing_repo_profile_field_ownership", "baseline.repo_profile_field_ownership must be an object")
        return

    contract_ownership = contract.get("repo_profile_ownership_contract")
    if not isinstance(contract_ownership, dict):
        _add_error(errors, "missing_repo_profile_ownership_contract", "repo_profile_ownership_contract must be an object")
        return

    baseline_override_fields = set(_as_string_list(ownership.get("baseline_override_fields")))
    derived_runtime_fields = set(_as_string_list(ownership.get("derived_runtime_fields")))
    catalog_input_fields = set(_as_string_list(ownership.get("catalog_input_fields")))

    contract_override_fields = set(_as_string_list(contract_ownership.get("baseline_override_fields")))
    contract_derived_fields = set(_as_string_list(contract_ownership.get("derived_runtime_fields")))
    contract_catalog_fields = set(_as_string_list(contract_ownership.get("catalog_input_fields")))

    if baseline_override_fields != set(baseline_overrides.keys()):
        _add_error(
            errors,
            "repo_profile_ownership_baseline_override_mismatch",
            "baseline.repo_profile_field_ownership.baseline_override_fields must match required_profile_overrides keys",
        )
    if derived_runtime_fields != DERIVED_RUNTIME_PROFILE_FIELDS:
        _add_error(
            errors,
            "repo_profile_ownership_derived_field_mismatch",
            "baseline.repo_profile_field_ownership.derived_runtime_fields must match runtime-derived profile fields",
        )
    if catalog_input_fields != CATALOG_PROFILE_FIELDS:
        _add_error(
            errors,
            "repo_profile_ownership_catalog_field_mismatch",
            "baseline.repo_profile_field_ownership.catalog_input_fields must match catalog-synced profile fields",
        )

    if baseline_override_fields != contract_override_fields:
        _add_error(
            errors,
            "repo_profile_ownership_contract_override_mismatch",
            "repo_profile_ownership_contract.baseline_override_fields must match baseline.repo_profile_field_ownership.baseline_override_fields",
        )
    if derived_runtime_fields != contract_derived_fields:
        _add_error(
            errors,
            "repo_profile_ownership_contract_derived_mismatch",
            "repo_profile_ownership_contract.derived_runtime_fields must match baseline.repo_profile_field_ownership.derived_runtime_fields",
        )
    if catalog_input_fields != contract_catalog_fields:
        _add_error(
            errors,
            "repo_profile_ownership_contract_catalog_mismatch",
            "repo_profile_ownership_contract.catalog_input_fields must match baseline.repo_profile_field_ownership.catalog_input_fields",
        )

    if baseline_override_fields & derived_runtime_fields:
        _add_error(errors, "repo_profile_ownership_overlap_override_derived", "baseline override fields and derived runtime fields must not overlap")
    if baseline_override_fields & catalog_input_fields:
        _add_error(errors, "repo_profile_ownership_overlap_override_catalog", "baseline override fields and catalog input fields must not overlap")
    if derived_runtime_fields & catalog_input_fields:
        _add_error(errors, "repo_profile_ownership_overlap_derived_catalog", "derived runtime fields and catalog input fields must not overlap")


def _validate_runtime_orchestrated_capability_contracts(
    contract: dict[str, Any],
    runtime_flow_preset_path: Path,
    errors: list[dict[str, str]],
) -> None:
    capabilities = contract.get("target_repo_capabilities")
    if not isinstance(capabilities, list):
        _add_error(errors, "missing_target_repo_capabilities_for_runtime_contract", "target_repo_capabilities must be present")
        return

    runtime_capability_ids = {
        capability.get("capability_id")
        for capability in capabilities
        if isinstance(capability, dict) and capability.get("distribution_scope") == "runtime_orchestrated" and isinstance(capability.get("capability_id"), str)
    }
    contract_entries = contract.get("runtime_orchestrated_capability_contracts")
    if not isinstance(contract_entries, list) or not contract_entries:
        _add_error(errors, "missing_runtime_orchestrated_capability_contracts", "runtime_orchestrated_capability_contracts must be a non-empty list")
        return

    entry_ids: set[str] = set()
    source = runtime_flow_preset_path.read_text(encoding="utf-8") if runtime_flow_preset_path.exists() else ""
    for index, entry in enumerate(contract_entries):
        if not isinstance(entry, dict):
            _add_error(errors, "invalid_runtime_orchestrated_capability_contract", f"runtime_orchestrated_capability_contracts[{index}] must be an object")
            continue
        capability_id = entry.get("capability_id")
        if not isinstance(capability_id, str) or not capability_id.strip():
            _add_error(errors, "missing_runtime_orchestrated_capability_id", f"runtime_orchestrated_capability_contracts[{index}].capability_id is required")
            continue
        capability_id = capability_id.strip()
        if capability_id in entry_ids:
            _add_error(errors, "duplicate_runtime_orchestrated_capability_contract", f"duplicate runtime_orchestrated capability contract: {capability_id}")
            continue
        entry_ids.add(capability_id)
        if capability_id not in runtime_capability_ids:
            _add_error(
                errors,
                "runtime_orchestrated_capability_contract_missing_capability",
                f"{capability_id} is declared in runtime_orchestrated_capability_contracts but not classified as runtime_orchestrated",
            )
            continue
        if not source:
            continue
        for field in _as_string_list(entry.get("required_json_fields")):
            if field not in source:
                _add_error(
                    errors,
                    "runtime_orchestrated_capability_json_field_not_emitted",
                    f"runtime-flow-preset.ps1 must emit JSON field or result field for {capability_id}: {field}",
                )
        for token in _as_string_list(entry.get("required_script_tokens")):
            if token not in source:
                _add_error(
                    errors,
                    "runtime_orchestrated_capability_script_token_missing",
                    f"runtime-flow-preset.ps1 must contain script token for {capability_id}: {token}",
                )

    for capability_id in sorted(runtime_capability_ids - entry_ids):
        _add_error(
            errors,
            "runtime_orchestrated_capability_missing_contract",
            f"{capability_id} is classified as runtime_orchestrated but missing from runtime_orchestrated_capability_contracts",
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
    _validate_managed_file_rollout(
        contract=contract,
        baseline=baseline,
        errors=errors,
    )
    _validate_repo_profile_ownership_contract(
        contract=contract,
        baseline=baseline,
        baseline_overrides=baseline_overrides,
        errors=errors,
    )
    _validate_target_repo_speed_profile_rollout(
        contract=contract,
        baseline=baseline,
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
    _validate_runtime_orchestrated_capability_contracts(
        contract=contract,
        runtime_flow_preset_path=runtime_flow_preset_path,
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
