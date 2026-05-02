from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from lib.target_repo_speed_profile import (
    apply_speed_profile_policy,
    as_command_list,
    normalize_speed_profile_policy,
    normalize_target_test_slice,
)
from lib.target_repo_quick_test_prompt import build_quick_test_slice_prompt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"
DEFAULT_MANAGED_FILE_BACKUP_ROOT = ROOT / "docs" / "change-evidence" / "managed-file-sync-backups"
DEFAULT_QUICK_TEST_RECOMMENDATION_RELATIVE_PATH = ".governed-ai/quick-test-slice.recommendation.json"
DEFAULT_QUICK_TEST_PROMPT_RELATIVE_PATH = ".governed-ai/quick-test-slice.prompt.md"
OUTER_AI_QUICK_TEST_INSTRUCTION = (
    "Read the target repo .governed-ai/quick-test-slice.prompt.md, inspect the test structure, "
    "and write .governed-ai/quick-test-slice.recommendation.json with status=ready and a safe "
    "quick_test_command, or status=skip when no safe fast slice exists. Do not modify the full "
    "test command."
)
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


def _backup_existing(target_path: Path, backup_root: Path, target_text: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    anchor = target_path.anchor
    drive = target_path.drive.replace(":", "") if target_path.drive else "relative"
    safe_parts = [drive]
    for part in target_path.parts:
        if part in {target_path.drive, target_path.root, anchor, "\\", "/"}:
            continue
        safe_parts.append(part.replace(":", "_"))
    backup_path = backup_root / timestamp / Path(*safe_parts)
    if backup_path.resolve(strict=False) == target_path.resolve(strict=False):
        raise ValueError(f"backup path resolves to target path: {target_path}")
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_text(target_text, encoding="utf-8")
    return backup_path


def _resolve_profile_path(target_repo: Path, profile_path_arg: str | None) -> Path:
    if profile_path_arg:
        return Path(profile_path_arg).resolve(strict=False)
    return target_repo / ".governed-ai" / "repo-profile.json"


def _normalize_baseline(path: Path) -> dict[str, Any]:
    baseline = _load_json(path)
    overrides = baseline.get("required_profile_overrides")
    if not isinstance(overrides, dict) or not overrides:
        raise ValueError("baseline.required_profile_overrides must be a non-empty object")
    sync_revision = baseline.get("sync_revision")
    if not isinstance(sync_revision, str) or not sync_revision.strip():
        raise ValueError("baseline.sync_revision must be a non-empty string")
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
    generated_files = baseline.get("generated_managed_files")
    if generated_files is None:
        generated_files = [
            {
                "path": DEFAULT_QUICK_TEST_PROMPT_RELATIVE_PATH,
                "generator": "outer_ai_quick_test_prompt",
                "management_mode": "block_on_drift",
            }
        ]
        baseline["generated_managed_files"] = generated_files
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
        if not isinstance(generator, str) or generator not in {"outer_ai_quick_test_prompt"}:
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
        normalize_speed_profile_policy(speed_policy)
    return baseline


def _apply_profile_overrides(
    profile: dict[str, Any],
    overrides: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    updated = dict(profile)
    changed_fields: list[str] = []
    for key, value in overrides.items():
        expected = copy.deepcopy(value)
        if updated.get(key) != expected:
            changed_fields.append(key)
        updated[key] = expected
    return updated, changed_fields


def _load_outer_ai_test_slice_recommendation(
    *,
    target_repo: Path,
    recommendation_path_arg: str | None = None,
) -> tuple[dict[str, Any] | None, str, str | None]:
    recommendation_path = (
        Path(recommendation_path_arg).resolve(strict=False)
        if recommendation_path_arg
        else target_repo / DEFAULT_QUICK_TEST_RECOMMENDATION_RELATIVE_PATH
    )
    if not recommendation_path.exists():
        return None, "none", str(recommendation_path)

    raw = _load_json(recommendation_path)
    status = str(raw.get("status") or "").strip().lower()
    if status and status not in {"ready", "skip"}:
        raise ValueError("quick test slice recommendation status must be ready or skip")
    if status == "skip":
        return None, "recommendation_file_skip", str(recommendation_path)

    slice_config = normalize_target_test_slice(
        command=raw.get("quick_test_command"),
        reason=raw.get("quick_test_reason"),
        timeout_seconds=raw.get("quick_test_timeout_seconds"),
    )
    if slice_config is None:
        raise ValueError("quick test slice recommendation must define quick_test_command when status is ready")
    return slice_config, "recommendation_file", str(recommendation_path)


def _write_outer_ai_test_slice_prompt(
    *,
    target_repo: Path,
    profile: dict[str, Any],
    prompt_path_arg: str | None = None,
    check_only: bool,
) -> tuple[str, str | None, list[dict[str, str]], list[dict[str, str]]]:
    prompt_path = (
        Path(prompt_path_arg).resolve(strict=False)
        if prompt_path_arg
        else target_repo / DEFAULT_QUICK_TEST_PROMPT_RELATIVE_PATH
    )
    prompt = build_quick_test_slice_prompt(target_repo=target_repo, profile=profile)
    existing = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else None
    file_record = {
        "path": str(prompt_path.relative_to(target_repo)).replace("\\", "/"),
        "generator": "outer_ai_quick_test_prompt",
        "management_mode": "block_on_drift",
        "reason": "missing" if existing is None else "content_drift",
        "source_sha256": _sha256_text(prompt),
        "target_sha256": _sha256_text(existing) if existing is not None else "",
        "expected_sha256": _sha256_text(prompt),
    }
    if existing == prompt:
        return "prompt_current", str(prompt_path), [], []
    if existing is not None:
        file_record["blocking_reason"] = "generated file content differs; review and integrate before applying"
        return "prompt_blocked", str(prompt_path), [], [file_record]
    if check_only:
        return "prompt_available", str(prompt_path), [file_record], []
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    return "prompt_written", str(prompt_path), [file_record], []


def _catalog_gate_entry(gate_id: str, command: str) -> dict[str, Any] | None:
    normalized = " ".join(str(command or "").strip().split())
    if not normalized:
        return None
    return {"id": gate_id, "command": normalized, "required": True}


def _catalog_gate_entries(
    *,
    default_gate_id: str,
    command: str | None = None,
    commands_json: str | None = None,
) -> list[dict[str, Any]]:
    raw_json = str(commands_json or "").strip()
    if not raw_json:
        entry = _catalog_gate_entry(default_gate_id, command or "")
        return [entry] if entry is not None else []

    parsed = json.loads(raw_json)
    if not isinstance(parsed, list):
        raise ValueError("--contract-commands-json must be a JSON array")

    entries: list[dict[str, Any]] = []
    for index, raw_entry in enumerate(parsed):
        if not isinstance(raw_entry, dict):
            raise ValueError(f"--contract-commands-json[{index}] must be an object")
        gate_id = str(raw_entry.get("id") or f"{default_gate_id}:{index + 1}").strip()
        entry = _catalog_gate_entry(gate_id, str(raw_entry.get("command") or ""))
        if entry is None:
            raise ValueError(f"--contract-commands-json[{index}].command must be a non-empty string")
        merged = copy.deepcopy(raw_entry)
        merged["id"] = entry["id"]
        merged["command"] = entry["command"]
        if "required" not in merged:
            merged["required"] = True
        entries.append(merged)
    return entries


def _apply_catalog_profile_facts(
    profile: dict[str, Any],
    *,
    repo_id: str | None = None,
    display_name: str | None = None,
    primary_language: str | None = None,
    build_command: str | None = None,
    test_command: str | None = None,
    contract_command: str | None = None,
    contract_commands_json: str | None = None,
) -> tuple[dict[str, Any], list[str], list[dict[str, Any]]]:
    updated = copy.deepcopy(profile)
    changed_fields: list[str] = []
    blocked_fields: list[dict[str, Any]] = []
    for field_name, value in (
        ("repo_id", repo_id),
        ("display_name", display_name),
        ("primary_language", primary_language),
    ):
        normalized = str(value or "").strip()
        current = str(updated.get(field_name) or "").strip()
        if not normalized:
            continue
        if not current:
            updated[field_name] = normalized
            changed_fields.append(field_name)
        elif current != normalized:
            blocked_fields.append(
                {
                    "field": field_name,
                    "reason": "content_drift",
                    "target_value": current,
                    "source_value": normalized,
                    "blocking_reason": "catalog profile field differs; review and integrate target repo fixes before applying",
                }
            )

    for group_name, gate_id, command in (
        ("build_commands", "build", build_command),
        ("test_commands", "test", test_command),
    ):
        entry = _catalog_gate_entry(gate_id, command or "")
        if entry is None:
            continue
        expected_group = [entry]
        actual_group = as_command_list(updated.get(group_name))
        if not actual_group:
            updated[group_name] = expected_group
            changed_fields.append(group_name)
        elif not _command_group_satisfies(actual_group, expected_group):
            blocked_fields.append(_catalog_group_block(group_name, actual_group, expected_group))

    expected_contract_commands = _catalog_gate_entries(
        default_gate_id="contract",
        command=contract_command,
        commands_json=contract_commands_json,
    )
    actual_contract_commands = as_command_list(updated.get("contract_commands"))
    if expected_contract_commands and not actual_contract_commands:
        updated["contract_commands"] = expected_contract_commands
        changed_fields.append("contract_commands")
    elif expected_contract_commands and not _command_group_satisfies(actual_contract_commands, expected_contract_commands):
        blocked_fields.append(_catalog_group_block("contract_commands", actual_contract_commands, expected_contract_commands))

    return updated, changed_fields, blocked_fields


def _command_group_satisfies(actual_group: list[dict[str, Any]], expected_group: list[dict[str, Any]]) -> bool:
    actual_by_id = {str(item.get("id") or "").strip(): str(item.get("command") or "").strip() for item in actual_group}
    actual_commands = {str(item.get("command") or "").strip() for item in actual_group}
    for expected in expected_group:
        expected_id = str(expected.get("id") or "").strip()
        expected_command = str(expected.get("command") or "").strip()
        if expected_id:
            if actual_by_id.get(expected_id) != expected_command:
                return False
        elif expected_command not in actual_commands:
            return False
    return True


def _catalog_group_block(
    group_name: str,
    actual_group: list[dict[str, Any]],
    expected_group: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "field": group_name,
        "reason": "content_drift",
        "target_value": copy.deepcopy(actual_group),
        "source_value": copy.deepcopy(expected_group),
        "blocking_reason": "catalog gate field differs; review and integrate target repo fixes before applying",
    }


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


def _source_path(baseline_path: Path, raw_path: str) -> Path:
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


def _sync_managed_files(
    *,
    target_repo: Path,
    baseline_path: Path,
    managed_files: list[dict[str, Any]],
    check_only: bool,
    backup_root: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    changed_files: list[dict[str, str]] = []
    blocked_files: list[dict[str, str]] = []
    for item in managed_files:
        target_path = _target_relative_path(target_repo, str(item["path"]))
        source_path = _source_path(baseline_path, str(item["source"]))
        management_mode = str(item.get("management_mode", "block_on_drift"))
        if not source_path.exists():
            raise ValueError(f"managed file source not found: {source_path}")
        source_text = source_path.read_text(encoding="utf-8")
        actual = target_path.read_text(encoding="utf-8") if target_path.exists() else None
        source_hash = _sha256_text(source_text)
        target_hash = _sha256_text(actual) if actual is not None else ""
        expected = _managed_file_expected_text(
            source_text=source_text,
            actual_text=actual,
            management_mode=management_mode,
        )
        expected_hash = _sha256_text(expected)
        if actual == expected:
            continue
        file_drift = {
            "path": str(target_path.relative_to(target_repo)).replace("\\", "/"),
            "source": str(source_path),
            "management_mode": management_mode,
            "reason": "missing" if actual is None else "content_drift",
            "source_sha256": source_hash,
            "target_sha256": target_hash,
            "expected_sha256": expected_hash,
        }
        if management_mode in {"replace", "block_on_drift"} and actual is not None:
            file_drift["blocking_reason"] = "managed file content differs; review and integrate before applying"
            blocked_files.append(file_drift)
            continue
        changed_files.append(file_drift)
        if not check_only:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if actual is not None:
                backup_path = _backup_existing(target_path, backup_root, actual)
                file_drift["backup_path"] = str(backup_path)
            target_path.write_text(expected, encoding="utf-8")
    return changed_files, blocked_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply governance baseline overrides into a target repo profile.")
    parser.add_argument("--target-repo", required=True, help="Target repository root.")
    parser.add_argument(
        "--baseline-path",
        default=str(DEFAULT_BASELINE_PATH),
        help="Path to governance baseline json.",
    )
    parser.add_argument(
        "--profile-path",
        default=None,
        help="Explicit repo-profile path. Defaults to <target-repo>/.governed-ai/repo-profile.json",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Do not write files; return non-zero when drift is detected.",
    )
    parser.add_argument(
        "--managed-file-backup-root",
        default=str(DEFAULT_MANAGED_FILE_BACKUP_ROOT),
        help="Backup root for existing managed files before writing merged content.",
    )
    parser.add_argument("--repo-id", help="Catalog repo id to sync into the target repo profile.")
    parser.add_argument("--display-name", help="Catalog display name to sync into the target repo profile.")
    parser.add_argument("--primary-language", help="Catalog primary language to sync into the target repo profile.")
    parser.add_argument("--build-command", help="Catalog build gate command to sync into build_commands.")
    parser.add_argument("--test-command", help="Catalog test gate command to sync into test_commands.")
    parser.add_argument("--contract-command", help="Catalog contract gate command to sync into contract_commands.")
    parser.add_argument("--contract-commands-json", help="Catalog contract gate command array to sync into contract_commands.")
    parser.add_argument("--quick-test-command", help="Target-specific quick test slice command for fast gates.")
    parser.add_argument("--quick-test-reason", help="Short reason for the quick test slice command.")
    parser.add_argument("--quick-test-timeout-seconds", type=int, help="Timeout override for the quick test slice command.")
    parser.add_argument(
        "--quick-test-skip-reason",
        help="Catalog-level reason that no target-specific quick test slice should be generated.",
    )
    parser.add_argument(
        "--quick-test-recommendation-path",
        help=(
            "Optional outer-AI recommendation JSON. Defaults to "
            f"{DEFAULT_QUICK_TEST_RECOMMENDATION_RELATIVE_PATH} when present."
        ),
    )
    parser.add_argument(
        "--quick-test-prompt-path",
        help=(
            "Optional output path for the outer-AI quick-test recommendation prompt. Defaults to "
            f"{DEFAULT_QUICK_TEST_PROMPT_RELATIVE_PATH}."
        ),
    )
    args = parser.parse_args()

    target_repo = Path(args.target_repo).resolve(strict=False)
    baseline_path = Path(args.baseline_path).resolve(strict=False)
    profile_path = _resolve_profile_path(target_repo=target_repo, profile_path_arg=args.profile_path)
    managed_file_backup_root = Path(args.managed_file_backup_root).resolve(strict=False)

    if not baseline_path.exists():
        raise SystemExit(f"baseline file not found: {baseline_path}")
    if not target_repo.exists():
        raise SystemExit(f"target repo not found: {target_repo}")
    if not profile_path.exists():
        raise SystemExit(f"repo profile not found: {profile_path}")

    baseline = _normalize_baseline(baseline_path)
    profile = _load_json(profile_path)
    target_test_slice = normalize_target_test_slice(
        command=args.quick_test_command,
        reason=args.quick_test_reason,
        timeout_seconds=args.quick_test_timeout_seconds,
    )
    quick_test_skip_reason = str(args.quick_test_skip_reason or "").strip()
    if target_test_slice is not None and quick_test_skip_reason:
        parser.error("--quick-test-command and --quick-test-skip-reason are mutually exclusive")

    quick_test_slice_source = "argument" if target_test_slice is not None else "none"
    if target_test_slice is None and quick_test_skip_reason:
        quick_test_slice_source = "argument_skip"
    recommendation_path = None
    if quick_test_slice_source == "none":
        target_test_slice, quick_test_slice_source, recommendation_path = _load_outer_ai_test_slice_recommendation(
            target_repo=target_repo,
            recommendation_path_arg=args.quick_test_recommendation_path,
        )
    outer_ai_action = "none"
    quick_test_prompt_path = None
    overrides = baseline["required_profile_overrides"]
    updated_profile, changed_catalog_fields, blocked_catalog_fields = _apply_catalog_profile_facts(
        profile,
        repo_id=args.repo_id,
        display_name=args.display_name,
        primary_language=args.primary_language,
        build_command=args.build_command,
        test_command=args.test_command,
        contract_command=args.contract_command,
        contract_commands_json=args.contract_commands_json,
    )
    updated_profile, changed_fields = _apply_profile_overrides(profile=updated_profile, overrides=overrides)
    changed_speed_profile_fields: list[str] = []
    changed_managed_files: list[dict[str, str]] = []
    blocked_managed_files: list[dict[str, str]] = []
    changed_generated_files: list[dict[str, str]] = []
    blocked_generated_files: list[dict[str, str]] = []

    if blocked_catalog_fields:
        status = "blocked"
    else:
        status = "pass"

    if not blocked_catalog_fields and quick_test_slice_source == "none":
        (
            outer_ai_action,
            quick_test_prompt_path,
            changed_generated_files,
            blocked_generated_files,
        ) = _write_outer_ai_test_slice_prompt(
            target_repo=target_repo,
            profile=updated_profile,
            prompt_path_arg=args.quick_test_prompt_path,
            check_only=args.check_only,
        )

    if not blocked_catalog_fields and not blocked_generated_files:
        if {"build_commands", "test_commands", "contract_commands"}.intersection(changed_catalog_fields):
            updated_profile.pop("quick_gate_commands", None)
            updated_profile.pop("full_gate_commands", None)
        updated_profile, changed_speed_profile_fields = apply_speed_profile_policy(
            profile=updated_profile,
            policy=baseline.get("target_repo_speed_profile_policy"),
            target_test_slice=target_test_slice,
        )
        changed_managed_files, blocked_managed_files = _sync_managed_files(
            target_repo=target_repo,
            baseline_path=baseline_path,
            managed_files=baseline.get("required_managed_files", []),
            check_only=args.check_only,
            backup_root=managed_file_backup_root,
        )

    if blocked_catalog_fields or blocked_generated_files or blocked_managed_files:
        status = "blocked"
    elif (
        changed_catalog_fields
        or changed_fields
        or changed_speed_profile_fields
        or changed_managed_files
        or changed_generated_files
    ):
        status = "drift" if args.check_only else "applied"

    if status != "blocked" and not args.check_only and (changed_catalog_fields or changed_fields or changed_speed_profile_fields):
        profile_path.write_text(
            json.dumps(updated_profile, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    output = {
        "status": status,
        "target_repo": str(target_repo),
        "profile_path": str(profile_path),
        "baseline_path": str(baseline_path),
        "managed_file_backup_root": str(managed_file_backup_root),
        "sync_revision": baseline["sync_revision"],
        "changed_catalog_fields": changed_catalog_fields,
        "blocked_catalog_fields": blocked_catalog_fields,
        "changed_fields": changed_fields,
        "changed_speed_profile_fields": changed_speed_profile_fields,
        "changed_managed_files": changed_managed_files,
        "blocked_managed_files": blocked_managed_files,
        "changed_generated_files": changed_generated_files,
        "blocked_generated_files": blocked_generated_files,
        "quick_test_slice_source": quick_test_slice_source,
        "quick_test_skip_reason": quick_test_skip_reason if quick_test_slice_source.endswith("_skip") else "",
        "quick_test_recommendation_path": recommendation_path,
        "outer_ai_action": outer_ai_action,
        "quick_test_prompt_path": quick_test_prompt_path,
        "outer_ai_instruction": OUTER_AI_QUICK_TEST_INSTRUCTION if outer_ai_action in {"prompt_written", "prompt_available"} else "",
        "check_only": args.check_only,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

    if blocked_catalog_fields or blocked_generated_files or blocked_managed_files:
        return 2
    if args.check_only and (
        changed_catalog_fields
        or changed_fields
        or changed_speed_profile_fields
        or changed_managed_files
        or changed_generated_files
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
