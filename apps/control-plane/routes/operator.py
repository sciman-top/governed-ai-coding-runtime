"""Operator read routes for the control-plane app."""

from __future__ import annotations

from typing import Any


def handle_operator_route(facade: Any, payload: dict) -> dict:
    action = _string_or_default(payload.get("action"), "status")
    if action == "status":
        return facade.operator_status(
            attachment_root=_string_or_none(payload.get("attachment_root")),
            attachment_runtime_state_root=_string_or_none(payload.get("attachment_runtime_state_root")),
        )
    if action == "inspect_evidence":
        return facade.operator_inspect_evidence(
            task_id=_required_string(payload.get("task_id"), "task_id"),
            run_id=_string_or_none(payload.get("run_id")),
        )
    if action == "inspect_handoff":
        return facade.operator_inspect_handoff(
            task_id=_required_string(payload.get("task_id"), "task_id"),
            run_id=_string_or_none(payload.get("run_id")),
            handoff_ref=_string_or_none(payload.get("handoff_ref")),
        )
    if action == "write_status":
        return facade.operator_write_status(
            task_id=_string_or_default(payload.get("task_id"), "attachment-write"),
            approval_id=_string_or_none(payload.get("approval_id")),
            target_path=_string_or_none(payload.get("target_path")),
            execution_id=_string_or_none(payload.get("execution_id")),
            attachment_runtime_state_root=_string_or_none(payload.get("attachment_runtime_state_root")),
        )
    msg = f"unsupported operator action: {action}"
    raise ValueError(msg)


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
