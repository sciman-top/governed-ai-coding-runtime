"""Durable adapter event sink over metadata persistence."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import json

ADAPTER_EVENTS_NAMESPACE = "adapter_events"


class AdapterEventSink:
    def __init__(self, *, metadata_store) -> None:
        self._metadata_store = metadata_store
        self._ensure_store_interface()

    def write_event(
        self,
        *,
        task_id: str,
        event_type: str,
        payload: dict,
        adapter_id: str,
        adapter_tier: str,
        flow_kind: str,
        execution_id: str,
        continuation_id: str,
        event_source: str,
        created_at: str | None = None,
    ) -> dict:
        created_at_value = created_at or datetime.now(UTC).isoformat()
        record = {
            "task_id": _required_string(task_id, "task_id"),
            "event_type": _required_string(event_type, "event_type"),
            "payload": _required_payload(payload, "payload"),
            "adapter_id": _required_string(adapter_id, "adapter_id"),
            "adapter_tier": _required_string(adapter_tier, "adapter_tier"),
            "flow_kind": _required_string(flow_kind, "flow_kind"),
            "execution_id": _required_string(execution_id, "execution_id"),
            "continuation_id": _required_string(continuation_id, "continuation_id"),
            "event_source": _required_string(event_source, "event_source"),
            "created_at": _required_string(created_at_value, "created_at"),
        }
        event_id = _event_id(record)
        persisted = {**record, "event_id": event_id}
        stored = self._metadata_store.upsert(
            namespace=ADAPTER_EVENTS_NAMESPACE,
            key=event_id,
            payload=persisted,
        )
        stored_payload = getattr(stored, "payload", persisted)
        if not isinstance(stored_payload, dict):
            return persisted
        return dict(stored_payload)

    def list_events(
        self,
        *,
        task_id: str,
        execution_id: str | None = None,
        continuation_id: str | None = None,
    ) -> list[dict]:
        task_id_value = _required_string(task_id, "task_id")
        execution_id_value = _optional_string(execution_id, "execution_id")
        continuation_id_value = _optional_string(continuation_id, "continuation_id")
        results: list[dict] = []
        for record in self._metadata_store.list_namespace(namespace=ADAPTER_EVENTS_NAMESPACE):
            payload = getattr(record, "payload", None)
            if not isinstance(payload, dict):
                continue
            if payload.get("task_id") != task_id_value:
                continue
            if execution_id_value is not None and payload.get("execution_id") != execution_id_value:
                continue
            if continuation_id_value is not None and payload.get("continuation_id") != continuation_id_value:
                continue
            results.append(dict(payload))
        return sorted(
            results,
            key=lambda item: (
                str(item.get("created_at", "")),
                str(item.get("event_id", "")),
            ),
        )

    def _ensure_store_interface(self) -> None:
        for method_name in ["upsert", "list_namespace"]:
            method = getattr(self._metadata_store, method_name, None)
            if callable(method):
                continue
            msg = f"metadata_store must provide {method_name}(...)"
            raise ValueError(msg)


def _event_id(record: dict) -> str:
    digest = hashlib.sha1(json.dumps(record, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    return f"{record['task_id']}:{record['created_at']}:{digest}"


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _optional_string(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, field_name)


def _required_payload(value: dict, field_name: str) -> dict:
    if not isinstance(value, dict):
        msg = f"{field_name} must be an object"
        raise ValueError(msg)
    return dict(value)
