"""Session route adapters for the control-plane app."""

from __future__ import annotations

from typing import Any


def handle_session_route(facade: Any, payload: dict) -> dict:
    return facade.session_command(
        command_type=_required_string(payload.get("command_type"), "command_type"),
        task_id=_required_string(payload.get("task_id"), "task_id"),
        repo_binding_id=_required_string(payload.get("repo_binding_id"), "repo_binding_id"),
        adapter_id=_string_or_default(payload.get("adapter_id"), "codex-cli"),
        risk_tier=_string_or_default(payload.get("risk_tier"), "low"),
        payload=payload.get("payload") if isinstance(payload.get("payload"), dict) else {},
        command_id=_string_or_none(payload.get("command_id")),
        policy_status=_string_or_default(payload.get("policy_status"), "allow"),
        attachment_root=_string_or_none(payload.get("attachment_root")),
        attachment_runtime_state_root=_string_or_none(payload.get("attachment_runtime_state_root")),
    )


def _required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _string_or_default(value: object, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _string_or_none(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None
