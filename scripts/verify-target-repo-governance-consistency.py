from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from lib.target_repo_speed_profile import (
    apply_speed_profile_policy,
    as_command_list,
    normalize_command_text,
    normalize_speed_profile_policy,
    normalize_target_config_test_slice,
    select_preferred_command,
)
from lib.target_repo_quick_test_prompt import build_quick_test_slice_prompt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG_PATH = ROOT / "docs" / "targets" / "target-repos-catalog.json"
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"
DEFAULT_QUICK_TEST_RECOMMENDATION_RELATIVE_PATH = ".governed-ai/quick-test-slice.recommendation.json"
DEFAULT_QUICK_TEST_PROMPT_RELATIVE_PATH = ".governed-ai/quick-test-slice.prompt.md"
DEFAULT_MANAGED_FILE_PROVENANCE_ROOT = ".governed-ai/managed-files"
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


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _drift_resolution_metadata(*, conflict_policy: str, recommended_action: str) -> dict[str, str]:
    return {
        "conflict_policy": conflict_policy,
        "recommended_action": recommended_action,
    }


def _expand_template(value: str, variables: dict[str, str]) -> str:
    expanded = value
    for key, raw in variables.items():
        expanded = expanded.replace("${" + key + "}", raw)
    return expanded


def _validate_baseline(
    path: Path,
) -> tuple[str, dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any] | None]:
    baseline = _load_json(path)
    sync_revision = baseline.get("sync_revision")
    overrides = baseline.get("required_profile_overrides")
    if not isinstance(sync_revision, str) or not sync_revision.strip():
        raise ValueError("baseline.sync_revision must be a non-empty string")
    if not isinstance(overrides, dict) or not overrides:
        raise ValueError("baseline.required_profile_overrides must be a non-empty object")
    managed_files = baseline.get("required_managed_files", [])
    if not isinstance(managed_files, list):
        raise ValueError("baseline.required_managed_files must be a list when present")
    for index, item in enumerate(managed_files):
        if not isinstance(item, dict):
            raise ValueError(f"baseline.required_managed_files[{index}] must be an object")
        target_path = item.get("path")
        source_path = item.get("source")
        management_mode = item.get("management_mode", "block_on_drift")
        if not isinstance(target_path, str) or not target_path.strip():
            raise ValueError(f"baseline.required_managed_files[{index}].path must be a non-empty string")
        if not isinstance(source_path, str) or not source_path.strip():
            raise ValueError(f"baseline.required_managed_files[{index}].source must be a non-empty string")
        if management_mode not in {"replace", "json_merge", "block_on_drift"}:
            raise ValueError(
                f"baseline.required_managed_files[{index}].management_mode must be replace, json_merge, or block_on_drift"
            )
    generated_files = baseline.get("generated_managed_files", [])
    if not isinstance(generated_files, list):
        raise ValueError("baseline.generated_managed_files must be a list when present")
    for index, item in enumerate(generated_files):
        if not isinstance(item, dict):
            raise ValueError(f"baseline.generated_managed_files[{index}] must be an object")
        target_path = item.get("path")
        generator = item.get("generator")
        management_mode = item.get("management_mode", "block_on_drift")
        if not isinstance(target_path, str) or not target_path.strip():
            raise ValueError(f"baseline.generated_managed_files[{index}].path must be a non-empty string")
        if generator != "outer_ai_quick_test_prompt":
            raise ValueError(f"baseline.generated_managed_files[{index}].generator must be outer_ai_quick_test_prompt")
        if management_mode != "block_on_drift":
            raise ValueError(f"baseline.generated_managed_files[{index}].management_mode must be block_on_drift")
    ownership = baseline.get("repo_profile_field_ownership")
    if ownership is None:
        ownership = {
            "baseline_override_fields": sorted(set(overrides.keys())),
            "derived_runtime_fields": sorted(DERIVED_RUNTIME_PROFILE_FIELDS),
            "catalog_input_fields": sorted(CATALOG_PROFILE_FIELDS),
        }
        baseline["repo_profile_field_ownership"] = ownership
    if not isinstance(ownership, dict):
        raise ValueError("baseline.repo_profile_field_ownership must be an object when present")
    baseline_override_fields = set(_as_string_list(ownership.get("baseline_override_fields")))
    derived_runtime_fields = set(_as_string_list(ownership.get("derived_runtime_fields")))
    catalog_input_fields = set(_as_string_list(ownership.get("catalog_input_fields")))
    if not baseline_override_fields:
        raise ValueError("baseline.repo_profile_field_ownership.baseline_override_fields must be a non-empty list")
    if baseline_override_fields != set(overrides.keys()):
        raise ValueError("baseline.repo_profile_field_ownership.baseline_override_fields must match required_profile_overrides keys")
    if not derived_runtime_fields:
        raise ValueError("baseline.repo_profile_field_ownership.derived_runtime_fields must be a non-empty list")
    if derived_runtime_fields != DERIVED_RUNTIME_PROFILE_FIELDS:
        raise ValueError("baseline.repo_profile_field_ownership.derived_runtime_fields must match runtime-derived profile fields")
    if not catalog_input_fields:
        raise ValueError("baseline.repo_profile_field_ownership.catalog_input_fields must be a non-empty list")
    if catalog_input_fields != CATALOG_PROFILE_FIELDS:
        raise ValueError("baseline.repo_profile_field_ownership.catalog_input_fields must match catalog-synced profile fields")
    if baseline_override_fields & derived_runtime_fields:
        raise ValueError("baseline.repo_profile_field_ownership baseline_override_fields and derived_runtime_fields must not overlap")
    if baseline_override_fields & catalog_input_fields:
        raise ValueError("baseline.repo_profile_field_ownership baseline_override_fields and catalog_input_fields must not overlap")
    if derived_runtime_fields & catalog_input_fields:
        raise ValueError("baseline.repo_profile_field_ownership derived_runtime_fields and catalog_input_fields must not overlap")
    speed_policy = baseline.get("target_repo_speed_profile_policy")
    if speed_policy is not None:
        speed_policy = normalize_speed_profile_policy(speed_policy)
    provenance_policy = baseline.get("managed_file_provenance_policy")
    if provenance_policy is not None:
        if not isinstance(provenance_policy, dict):
            raise ValueError("baseline.managed_file_provenance_policy must be an object when present")
        if provenance_policy.get("status") not in {"observe", "enforced", "disabled"}:
            raise ValueError("baseline.managed_file_provenance_policy.status must be observe, enforced, or disabled")
        if provenance_policy.get("strategy") != "sidecar":
            raise ValueError("baseline.managed_file_provenance_policy.strategy must be sidecar")
        if provenance_policy.get("sidecar_root") != DEFAULT_MANAGED_FILE_PROVENANCE_ROOT:
            raise ValueError(
                f"baseline.managed_file_provenance_policy.sidecar_root must be {DEFAULT_MANAGED_FILE_PROVENANCE_ROOT}"
            )
        if not isinstance(provenance_policy.get("write_on_apply"), bool):
            raise ValueError("baseline.managed_file_provenance_policy.write_on_apply must be boolean")
        if not isinstance(provenance_policy.get("require_in_consistency"), bool):
            raise ValueError("baseline.managed_file_provenance_policy.require_in_consistency must be boolean")
    return sync_revision, overrides, managed_files, generated_files, speed_policy


def _target_quick_test_skip_reason(target_config: dict[str, Any]) -> str:
    return str(target_config.get("quick_test_skip_reason") or "").strip()


def _catalog_command_entries(target_config: dict[str, Any], group_name: str, command_name: str) -> list[dict[str, Any]]:
    raw_entries = target_config.get(group_name)
    if isinstance(raw_entries, list):
        entries: list[dict[str, Any]] = []
        for item in raw_entries:
            if not isinstance(item, dict):
                continue
            command = normalize_command_text(item.get("command"))
            if not command:
                continue
            entries.append(
                {
                    "id": str(item.get("id") or "").strip(),
                    "command": command,
                }
            )
        return entries

    command = normalize_command_text(target_config.get(command_name))
    if not command:
        return []
    return [{"id": "", "command": command}]


def _catalog_gate_fact_drift(profile: dict[str, Any], target_config: dict[str, Any]) -> list[str]:
    drift: list[str] = []
    for field_name, catalog_name in (
        ("repo_id", "repo_id"),
        ("display_name", "display_name"),
        ("primary_language", "primary_language"),
    ):
        expected = str(target_config.get(catalog_name) or "").strip()
        if expected and profile.get(field_name) != expected:
            drift.append(field_name)

    for group_name, catalog_group_name, catalog_name in (
        ("build_commands", "build_commands", "build_command"),
        ("test_commands", "test_commands", "test_command"),
        ("contract_commands", "contract_commands", "contract_command"),
    ):
        expected_entries = _catalog_command_entries(target_config, catalog_group_name, catalog_name)
        if not expected_entries:
            continue
        actual_entries = as_command_list(profile.get(group_name))
        actual_by_id = {str(item.get("id") or "").strip(): normalize_command_text(item.get("command")) for item in actual_entries}
        actual_commands = {normalize_command_text(item.get("command")) for item in actual_entries}
        has_drift = False
        for expected in expected_entries:
            expected_id = expected["id"]
            expected_command = expected["command"]
            if expected_id:
                if actual_by_id.get(expected_id) != expected_command:
                    has_drift = True
                    break
            elif expected_command not in actual_commands:
                actual = select_preferred_command(profile, group_name)
                actual_command = normalize_command_text(actual.get("command") if actual else "")
                if actual_command != expected_command:
                    has_drift = True
                    break
        if has_drift:
            drift.append(group_name)

    return drift


def _load_outer_ai_test_slice_recommendation(target_repo: Path) -> dict[str, Any] | None:
    recommendation_path = target_repo / DEFAULT_QUICK_TEST_RECOMMENDATION_RELATIVE_PATH
    if not recommendation_path.exists():
        return None

    raw = _load_json(recommendation_path)
    status = str(raw.get("status") or "").strip().lower()
    if status and status not in {"ready", "skip"}:
        raise ValueError(f"quick test slice recommendation status must be ready or skip: {recommendation_path}")
    if status == "skip":
        return None

    slice_config = normalize_target_config_test_slice(
        {
            "quick_test_command": raw.get("quick_test_command"),
            "quick_test_reason": raw.get("quick_test_reason"),
            "quick_test_timeout_seconds": raw.get("quick_test_timeout_seconds"),
        }
    )
    if slice_config is None:
        raise ValueError(
            f"quick test slice recommendation must define quick_test_command when status is ready: {recommendation_path}"
        )
    return slice_config


def _target_relative_path(target_repo: Path, raw_path: str) -> Path:
    relative = Path(raw_path)
    if relative.is_absolute():
        raise ValueError(f"managed file path must be repo-relative: {raw_path}")
    if any(part == ".." for part in relative.parts):
        raise ValueError(f"managed file path must not contain '..': {raw_path}")
    resolved = (target_repo / relative).resolve(strict=False)
    try:
        resolved.relative_to(target_repo.resolve(strict=False))
    except ValueError as exc:
        raise ValueError(f"managed file path escapes target repo: {raw_path}") from exc
    return resolved


def _source_path(raw_path: str) -> Path:
    source = Path(raw_path)
    if not source.is_absolute():
        source = ROOT / source
    return source.resolve(strict=False)


def _deep_merge_json(base: Any, overlay: Any) -> Any:
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = {key: copy.deepcopy(value) for key, value in base.items()}
        for key, value in overlay.items():
            if key in merged:
                merged[key] = _deep_merge_json(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged
    return copy.deepcopy(overlay)


def _managed_file_expected_text(*, source_text: str, actual_text: str | None, management_mode: str) -> str:
    if management_mode in {"replace", "block_on_drift"} or actual_text is None:
        return source_text
    if management_mode != "json_merge":
        raise ValueError(f"unsupported management_mode: {management_mode}")

    source_json = json.loads(source_text)
    actual_json = json.loads(actual_text)
    merged = _deep_merge_json(actual_json, source_json)
    return json.dumps(merged, ensure_ascii=False, indent=2) + "\n"


def _load_targets(catalog_path: Path) -> dict[str, dict[str, Any]]:
    catalog = _load_json(catalog_path)
    targets = catalog.get("targets")
    if not isinstance(targets, dict) or not targets:
        raise ValueError("target catalog must define a non-empty targets object")
    validated: dict[str, dict[str, Any]] = {}
    for key, value in targets.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("target catalog key must be a non-empty string")
        if not isinstance(value, dict):
            raise ValueError(f"target '{key}' must be an object")
        attachment_root = value.get("attachment_root")
        if not isinstance(attachment_root, str) or not attachment_root.strip():
            raise ValueError(f"target '{key}' missing attachment_root")
        validated[key] = value
    return validated


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify governance feature consistency across all active target repos.")
    parser.add_argument("--catalog-path", default=str(DEFAULT_CATALOG_PATH))
    parser.add_argument("--baseline-path", default=str(DEFAULT_BASELINE_PATH))
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--code-root", default=None)
    parser.add_argument("--runtime-state-base", default=None)
    args = parser.parse_args()

    catalog_path = Path(args.catalog_path).resolve(strict=False)
    baseline_path = Path(args.baseline_path).resolve(strict=False)
    repo_root = Path(args.repo_root).resolve(strict=False)
    code_root = Path(args.code_root).resolve(strict=False) if args.code_root else repo_root.parent
    runtime_state_base = (
        Path(args.runtime_state_base).resolve(strict=False)
        if args.runtime_state_base
        else repo_root / ".runtime" / "attachments"
    )

    if not catalog_path.exists():
        raise SystemExit(f"catalog file not found: {catalog_path}")
    if not baseline_path.exists():
        raise SystemExit(f"baseline file not found: {baseline_path}")

    sync_revision, expected_overrides, managed_files, generated_files, speed_policy = _validate_baseline(baseline_path)
    targets = _load_targets(catalog_path)
    variables = {
        "repo_root": str(repo_root),
        "code_root": str(code_root),
        "runtime_state_base": str(runtime_state_base),
    }

    checked_targets: list[str] = []
    drift: list[dict[str, Any]] = []

    for target_name in sorted(targets.keys()):
        checked_targets.append(target_name)
        target = targets[target_name]
        attachment_root = Path(_expand_template(str(target["attachment_root"]), variables)).resolve(strict=False)
        profile_path = attachment_root / ".governed-ai" / "repo-profile.json"

        if not attachment_root.exists():
            drift.append(
                {
                    "target": target_name,
                    "reason": "target_repo_not_found",
                    "target_repo": str(attachment_root),
                    "profile_path": str(profile_path),
                }
            )
            continue

        if not profile_path.exists():
            drift.append(
                {
                    "target": target_name,
                    "reason": "repo_profile_not_found",
                    "target_repo": str(attachment_root),
                    "profile_path": str(profile_path),
                }
            )
            continue

        profile = _load_json(profile_path)
        mismatched_fields: list[str] = []
        for field_name, expected_value in expected_overrides.items():
            if profile.get(field_name) != expected_value:
                mismatched_fields.append(field_name)
        if mismatched_fields:
            drift.append(
                {
                    "target": target_name,
                    "reason": "governance_profile_drift",
                    "target_repo": str(attachment_root),
                    "profile_path": str(profile_path),
                    "mismatched_fields": mismatched_fields,
                }
            )

        mismatched_catalog_fields = _catalog_gate_fact_drift(profile, target)
        if mismatched_catalog_fields:
            drift.append(
                {
                    "target": target_name,
                    "reason": "catalog_gate_fact_drift",
                    "target_repo": str(attachment_root),
                    "profile_path": str(profile_path),
                    "mismatched_catalog_fields": mismatched_catalog_fields,
                    "conflict_policy": "block_on_drift",
                    "recommended_action": "compare target repo profile gate facts with docs/targets/target-repos-catalog.json, integrate the correct command source, then rerun consistency verification",
                }
            )

        target_test_slice = normalize_target_config_test_slice(target)
        target_test_skip_reason = _target_quick_test_skip_reason(target)
        if target_test_slice is not None and target_test_skip_reason:
            raise ValueError(f"target cannot define both quick_test_command and quick_test_skip_reason: {target_name}")
        recommendation_path = attachment_root / DEFAULT_QUICK_TEST_RECOMMENDATION_RELATIVE_PATH
        if target_test_slice is None and not target_test_skip_reason and recommendation_path.exists():
            target_test_slice = _load_outer_ai_test_slice_recommendation(attachment_root)
        _, mismatched_speed_profile_fields = apply_speed_profile_policy(
            profile,
            speed_policy,
            target_test_slice=target_test_slice,
        )
        if mismatched_speed_profile_fields:
            drift.append(
                {
                    "target": target_name,
                    "reason": "speed_profile_drift",
                    "target_repo": str(attachment_root),
                    "profile_path": str(profile_path),
                    "mismatched_speed_profile_fields": mismatched_speed_profile_fields,
                }
            )

        mismatched_managed_files: list[dict[str, str]] = []
        for item in managed_files:
            target_path = _target_relative_path(attachment_root, str(item["path"]))
            source_path = _source_path(str(item["source"]))
            management_mode = str(item.get("management_mode", "block_on_drift"))
            if not source_path.exists():
                raise SystemExit(f"managed file source not found: {source_path}")
            source_text = source_path.read_text(encoding="utf-8")
            actual = target_path.read_text(encoding="utf-8") if target_path.exists() else None
            expected = _managed_file_expected_text(
                source_text=source_text,
                actual_text=actual,
                management_mode=management_mode,
            )
            if actual != expected:
                mismatched_managed_files.append(
                    {
                        "path": str(target_path.relative_to(attachment_root)).replace("\\", "/"),
                        "source": str(source_path),
                        "management_mode": management_mode,
                        "reason": "missing" if actual is None else "content_drift",
                        "source_sha256": _sha256_text(source_text),
                        "target_sha256": _sha256_text(actual) if actual is not None else "",
                        "expected_sha256": _sha256_text(expected),
                        "conflict_policy": "create_missing" if actual is None else "block_on_drift",
                        "recommended_action": (
                            "create the missing managed file from the control-repo source"
                            if actual is None
                            else "diff target file against source, integrate target-local fixes into the control-repo source or explicitly retire the target change, then rerun consistency verification"
                        ),
                    }
                )
        if mismatched_managed_files:
            drift.append(
                {
                    "target": target_name,
                    "reason": "managed_file_drift",
                    "target_repo": str(attachment_root),
                    "profile_path": str(profile_path),
                    "mismatched_managed_files": mismatched_managed_files,
                }
            )

        mismatched_generated_files: list[dict[str, str]] = []
        should_have_quick_prompt = target_test_slice is None and not target_test_skip_reason and not recommendation_path.exists()
        if should_have_quick_prompt:
            for item in generated_files:
                if item.get("generator") != "outer_ai_quick_test_prompt":
                    continue
                prompt_path = _target_relative_path(attachment_root, str(item["path"]))
                expected_prompt = build_quick_test_slice_prompt(target_repo=attachment_root, profile=profile)
                actual_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else None
                if actual_prompt != expected_prompt:
                    mismatched_generated_files.append(
                        {
                            "path": str(prompt_path.relative_to(attachment_root)).replace("\\", "/"),
                            "generator": "outer_ai_quick_test_prompt",
                            "management_mode": str(item.get("management_mode", "block_on_drift")),
                            "reason": "missing" if actual_prompt is None else "content_drift",
                            "target_sha256": _sha256_text(actual_prompt) if actual_prompt is not None else "",
                            "expected_sha256": _sha256_text(expected_prompt),
                            "conflict_policy": "create_missing" if actual_prompt is None else "block_on_drift",
                            "recommended_action": (
                                "create the missing generated prompt from the current generator"
                                if actual_prompt is None
                                else "compare generated prompt with target-local content, update the generator or accept the target recommendation, then rerun consistency verification"
                            ),
                        }
                    )
        if mismatched_generated_files:
            drift.append(
                {
                    "target": target_name,
                    "reason": "generated_managed_file_drift",
                    "target_repo": str(attachment_root),
                    "profile_path": str(profile_path),
                    "mismatched_generated_files": mismatched_generated_files,
                }
            )

    status = "pass" if not drift else "fail"
    output = {
        "status": status,
        "catalog_path": str(catalog_path),
        "baseline_path": str(baseline_path),
        "sync_revision": sync_revision,
        "target_count": len(checked_targets),
        "checked_targets": checked_targets,
        "drift_count": len(drift),
        "drift": drift,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
