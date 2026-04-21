"""Shared adapter conformance checks for Codex and non-Codex trial surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ConformanceStatus = Literal["pass", "fail"]
ParityStatus = Literal["supported", "degraded", "blocked"]


@dataclass(frozen=True, slots=True)
class AdapterConformanceResult:
    adapter_id: str
    host_family: str
    status: ConformanceStatus
    failed_checks: list[str]
    parity_status: ParityStatus
    linkage_refs: list[str]


def evaluate_codex_trial_conformance(payload: dict) -> AdapterConformanceResult:
    _require_object(payload, "codex trial payload")
    adapter_id = _required_string(payload.get("adapter_id"), "adapter_id")
    host_family = "codex"

    checks: list[str] = []
    if not _non_empty_string(payload.get("session_id")):
        checks.append("missing_session_id")
    if not _non_empty_string(payload.get("resume_id")):
        checks.append("missing_resume_id")
    if not _non_empty_string(payload.get("continuation_id")):
        checks.append("missing_continuation_id")

    evidence_refs = _required_string_list(payload.get("evidence_refs"), "evidence_refs")
    verification_refs = _required_string_list(payload.get("verification_refs"), "verification_refs")
    handoff_ref = _required_string(payload.get("handoff_ref"), "handoff_ref")

    linkage_refs = evidence_refs + verification_refs + [handoff_ref]
    if not linkage_refs:
        checks.append("missing_linkage_refs")

    flow_kind = _required_string(payload.get("flow_kind"), "flow_kind")
    unsupported_behavior = _required_string(
        payload.get("unsupported_capability_behavior"),
        "unsupported_capability_behavior",
    )
    if flow_kind not in {"live_attach", "process_bridge", "manual_handoff"}:
        checks.append("unsupported_flow_kind")

    parity_status: ParityStatus
    if checks:
        parity_status = "blocked"
    elif flow_kind == "live_attach" and unsupported_behavior == "none":
        parity_status = "supported"
    else:
        parity_status = "degraded"

    return AdapterConformanceResult(
        adapter_id=adapter_id,
        host_family=host_family,
        status="fail" if checks else "pass",
        failed_checks=checks,
        parity_status=parity_status,
        linkage_refs=linkage_refs,
    )


def evaluate_runtime_check_conformance(payload: dict, *, host_family: str) -> AdapterConformanceResult:
    _require_object(payload, "runtime-check payload")
    _required_string(host_family, "host_family")

    summary = _require_object(payload.get("summary"), "summary")
    request_gate = _require_object(payload.get("request_gate"), "request_gate")
    request_payload = _require_object(request_gate.get("payload"), "request_gate.payload")

    adapter_id = _required_string(request_payload.get("adapter_id"), "request_gate.payload.adapter_id")
    checks: list[str] = []

    if not _non_empty_string(summary.get("session_id")):
        checks.append("missing_session_id")
    if not _non_empty_string(summary.get("resume_id")):
        checks.append("missing_resume_id")
    if not _non_empty_string(summary.get("continuation_id")):
        checks.append("missing_continuation_id")

    live_loop = _require_object(payload.get("live_loop"), "live_loop")
    runtime_refs = _required_string_list(live_loop.get("runtime_refs"), "live_loop.runtime_refs")
    if not runtime_refs:
        checks.append("missing_linkage_refs")

    flow_kind = _required_string(live_loop.get("flow_kind"), "live_loop.flow_kind")
    fallback_explicit = live_loop.get("fallback_explicit")
    if not isinstance(fallback_explicit, bool):
        checks.append("fallback_explicit_not_boolean")

    parity_status: ParityStatus
    if checks:
        parity_status = "blocked"
    elif flow_kind == "live_attach" and fallback_explicit is False:
        parity_status = "supported"
    elif fallback_explicit is True:
        parity_status = "degraded"
    else:
        parity_status = "degraded"

    return AdapterConformanceResult(
        adapter_id=adapter_id,
        host_family=host_family,
        status="fail" if checks else "pass",
        failed_checks=checks,
        parity_status=parity_status,
        linkage_refs=runtime_refs,
    )


def build_parity_matrix(results: list[AdapterConformanceResult]) -> list[dict]:
    matrix: list[dict] = []
    for result in results:
        matrix.append(
            {
                "adapter_id": result.adapter_id,
                "host_family": result.host_family,
                "conformance_status": result.status,
                "parity_status": result.parity_status,
                "failed_checks": list(result.failed_checks),
                "linkage_ref_count": len(result.linkage_refs),
            }
        )
    return matrix


def _required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _required_string_list(value: object, field_name: str) -> list[str]:
    if not isinstance(value, list):
        msg = f"{field_name} must be an array"
        raise ValueError(msg)
    normalized: list[str] = []
    for index, item in enumerate(value):
        normalized.append(_required_string(item, f"{field_name}[{index}]") )
    return normalized


def _require_object(value: object, field_name: str) -> dict:
    if not isinstance(value, dict):
        msg = f"{field_name} must be an object"
        raise ValueError(msg)
    return value


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())
