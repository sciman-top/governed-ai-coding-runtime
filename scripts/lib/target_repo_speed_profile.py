from __future__ import annotations

import copy
from typing import Any


def normalize_non_negative_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value


def normalize_speed_profile_policy(raw_policy: Any) -> dict[str, Any]:
    if not isinstance(raw_policy, dict):
        raise ValueError("baseline.target_repo_speed_profile_policy must be an object when present")

    policy = copy.deepcopy(raw_policy)
    enabled = policy.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError("target_repo_speed_profile_policy.enabled must be a boolean")
    policy["enabled"] = enabled

    for key in (
        "materialize_quick_gate_commands",
        "materialize_full_gate_commands",
        "preserve_existing_gate_commands",
        "refresh_existing_derived_gate_commands",
    ):
        value = policy.get(key, True)
        if not isinstance(value, bool):
            raise ValueError(f"target_repo_speed_profile_policy.{key} must be a boolean")
        policy[key] = value

    default_timeout = policy.get("default_gate_timeout_seconds", 300)
    policy["default_gate_timeout_seconds"] = normalize_non_negative_int(
        default_timeout,
        "target_repo_speed_profile_policy.default_gate_timeout_seconds",
    )
    for key in ("quick_gate_timeout_seconds", "full_gate_timeout_seconds"):
        value = policy.get(key, policy["default_gate_timeout_seconds"])
        policy[key] = normalize_non_negative_int(value, f"target_repo_speed_profile_policy.{key}")

    return policy


def normalize_target_test_slice(
    *,
    command: Any,
    reason: Any = None,
    timeout_seconds: Any = None,
    timeout_field_name: str = "quick_test_timeout_seconds",
) -> dict[str, Any] | None:
    normalized_command = str(command or "").strip()
    if not normalized_command:
        return None
    slice_config: dict[str, Any] = {"command": normalized_command}
    normalized_reason = str(reason or "").strip()
    if normalized_reason:
        slice_config["reason"] = normalized_reason
    if timeout_seconds is not None:
        slice_config["timeout_seconds"] = normalize_non_negative_int(timeout_seconds, timeout_field_name)
    return slice_config


def normalize_target_config_test_slice(target_config: dict[str, Any]) -> dict[str, Any] | None:
    return normalize_target_test_slice(
        command=target_config.get("quick_test_command"),
        reason=target_config.get("quick_test_reason"),
        timeout_seconds=target_config.get("quick_test_timeout_seconds")
        if "quick_test_timeout_seconds" in target_config
        else None,
        timeout_field_name="target.quick_test_timeout_seconds",
    )


def normalize_command_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def as_command_list(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    raw_items = value if isinstance(value, list) else [value]
    items: list[dict[str, Any]] = []
    for item in raw_items:
        if isinstance(item, dict) and isinstance(item.get("command"), str) and item["command"].strip():
            items.append(item)
    return items


def select_preferred_command(profile: dict[str, Any], group_name: str) -> dict[str, Any] | None:
    commands = as_command_list(profile.get(group_name))
    required = [item for item in commands if item.get("required", True) is True]
    if required:
        return required[0]
    if commands:
        return commands[0]
    return None


def _derived_gate_entry(
    profile: dict[str, Any],
    source_group: str,
    default_id: str,
    timeout_seconds: int,
) -> dict[str, Any] | None:
    source = select_preferred_command(profile, source_group)
    if source is None:
        return None
    entry = copy.deepcopy(source)
    entry["id"] = str(entry.get("id") or default_id)
    if "required" not in entry:
        entry["required"] = True
    if timeout_seconds > 0 and "timeout_seconds" not in entry:
        entry["timeout_seconds"] = timeout_seconds
    return entry


def _normalized_entry_command(entry: dict[str, Any]) -> str:
    return normalize_command_text(entry.get("command", ""))


def dedupe_gate_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    by_command: dict[str, dict[str, Any]] = {}
    for entry in entries:
        command_key = _normalized_entry_command(entry)
        gate_id = str(entry.get("id") or "").strip()
        if not command_key or not gate_id:
            continue
        existing = by_command.get(command_key)
        if existing is None:
            updated = copy.deepcopy(entry)
            updated["satisfies_gate_ids"] = [gate_id]
            merged.append(updated)
            by_command[command_key] = updated
            continue
        aliases = list(existing.get("satisfies_gate_ids") or [str(existing.get("id"))])
        if gate_id not in aliases:
            aliases.append(gate_id)
        existing["satisfies_gate_ids"] = aliases
    return merged


def _has_non_empty_gate_group(profile: dict[str, Any], group_name: str) -> bool:
    return bool(as_command_list(profile.get(group_name)))


def _build_legacy_speed_groups(
    profile: dict[str, Any],
    policy: dict[str, Any],
    target_test_slice: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    test_entry = _derived_gate_entry(profile, "test_commands", "test", int(policy["quick_gate_timeout_seconds"]))
    if target_test_slice is not None:
        test_entry = {
            "id": "test",
            "command": str(target_test_slice["command"]),
            "required": True,
            "timeout_seconds": int(target_test_slice.get("timeout_seconds", policy["quick_gate_timeout_seconds"])),
        }
        reason = str(target_test_slice.get("reason", "")).strip()
        if reason:
            test_entry["description"] = reason

    quick_commands = [
        item
        for item in (
            test_entry,
            _derived_gate_entry(profile, "contract_commands", "contract", int(policy["quick_gate_timeout_seconds"])),
            _derived_gate_entry(profile, "invariant_commands", "invariant", int(policy["quick_gate_timeout_seconds"])),
        )
        if item is not None
    ]
    if len(quick_commands) > 2:
        quick_commands = quick_commands[:2]

    contract_entry = _derived_gate_entry(
        profile,
        "contract_commands",
        "contract",
        int(policy["full_gate_timeout_seconds"]),
    )
    if contract_entry is None:
        contract_entry = _derived_gate_entry(
            profile,
            "invariant_commands",
            "invariant",
            int(policy["full_gate_timeout_seconds"]),
        )
    full_commands = [
        item
        for item in (
            _derived_gate_entry(profile, "build_commands", "build", int(policy["full_gate_timeout_seconds"])),
            _derived_gate_entry(profile, "test_commands", "test", int(policy["full_gate_timeout_seconds"])),
            contract_entry,
        )
        if item is not None
    ]
    return quick_commands, full_commands


def _looks_like_generated_gate_group(value: Any) -> bool:
    raw_items = value if isinstance(value, list) else [value]
    if not raw_items:
        return False
    generated_keys = {"id", "command", "required", "timeout_seconds", "satisfies_gate_ids", "description"}
    for item in raw_items:
        if not isinstance(item, dict):
            return False
        if "satisfies_gate_ids" not in item:
            return False
        if any(key not in generated_keys for key in item.keys()):
            return False
    return True


def _should_replace_gate_group(
    profile: dict[str, Any],
    group_name: str,
    legacy_commands: list[dict[str, Any]],
    preserve_existing: bool,
    refresh_existing_derived: bool,
    legacy_fallback_commands: list[dict[str, Any]] | None = None,
) -> bool:
    if not _has_non_empty_gate_group(profile, group_name):
        return True
    if not preserve_existing:
        return True
    if not refresh_existing_derived:
        return False
    current = profile.get(group_name)
    if _looks_like_generated_gate_group(current):
        return True
    legacy_equivalents = [legacy_commands, dedupe_gate_entries(legacy_commands)]
    if any(current == candidate for candidate in legacy_equivalents):
        return True
    if legacy_fallback_commands is None:
        return False
    fallback_equivalents = [legacy_fallback_commands, dedupe_gate_entries(legacy_fallback_commands)]
    return any(current == candidate for candidate in fallback_equivalents)


def apply_speed_profile_policy(
    profile: dict[str, Any],
    policy: dict[str, Any] | None,
    target_test_slice: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    if policy is None:
        return profile, []

    normalized_policy = normalize_speed_profile_policy(policy)
    if not normalized_policy["enabled"]:
        return profile, []

    updated = copy.deepcopy(profile)
    changed_fields: list[str] = []
    preserve_existing = bool(normalized_policy["preserve_existing_gate_commands"])
    refresh_existing_derived = bool(normalized_policy["refresh_existing_derived_gate_commands"])
    legacy_quick_commands, legacy_full_commands = _build_legacy_speed_groups(
        updated, normalized_policy, target_test_slice
    )
    fallback_quick_commands, fallback_full_commands = _build_legacy_speed_groups(updated, normalized_policy)

    if bool(normalized_policy["materialize_quick_gate_commands"]):
        if _should_replace_gate_group(
            updated,
            "quick_gate_commands",
            legacy_quick_commands,
            preserve_existing,
            refresh_existing_derived,
            fallback_quick_commands,
        ):
            quick_commands = dedupe_gate_entries(legacy_quick_commands)
            if quick_commands and updated.get("quick_gate_commands") != quick_commands:
                updated["quick_gate_commands"] = quick_commands
                changed_fields.append("quick_gate_commands")

    if bool(normalized_policy["materialize_full_gate_commands"]):
        if _should_replace_gate_group(
            updated,
            "full_gate_commands",
            legacy_full_commands,
            preserve_existing,
            refresh_existing_derived,
            fallback_full_commands,
        ):
            full_commands = dedupe_gate_entries(legacy_full_commands)
            if full_commands and updated.get("full_gate_commands") != full_commands:
                updated["full_gate_commands"] = full_commands
                changed_fields.append("full_gate_commands")

    if "gate_timeout_seconds" not in updated:
        updated["gate_timeout_seconds"] = int(normalized_policy["default_gate_timeout_seconds"])
        changed_fields.append("gate_timeout_seconds")

    return updated, changed_fields
