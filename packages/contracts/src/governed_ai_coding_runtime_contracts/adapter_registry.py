"""Minimal adapter capability helpers for launch-second fallback."""

from dataclasses import dataclass
from typing import Literal


AdapterTier = Literal["native_attach", "process_bridge", "manual_handoff"]
LifecycleStatus = Literal["experimental", "supported", "deprecated"]
EventVisibility = Literal["structured_jsonl", "mcp_events", "app_protocol_events", "logs_only", "transcript_only", "none"]
ContinuationModel = Literal["resume_id", "fork_id", "session_id", "stateless", "manual"]
EvidenceModel = Literal["structured_trace", "command_log", "transcript", "diff_artifact", "external_artifact", "manual_summary"]


@dataclass(frozen=True, slots=True)
class AdapterCapability:
    adapter_id: str
    tier: AdapterTier
    supported: bool
    reason: str
    unsupported_capability_behavior: str


@dataclass(frozen=True, slots=True)
class AdapterContract:
    adapter_id: str
    display_name: str
    product_family: str
    lifecycle_status: LifecycleStatus
    adapter_tier: AdapterTier
    auth_ownership: str
    workspace_control: str
    event_visibility: EventVisibility
    mutation_model: str
    continuation_model: ContinuationModel
    evidence_model: EvidenceModel
    supported_governance_modes: list[str]
    minimum_required_runtime_controls: list[str]
    governance_guarantees: list[str]
    unsupported_capability_behavior: str


def resolve_launch_fallback(
    *,
    adapter_id: str,
    native_attach_available: bool,
    process_bridge_available: bool,
) -> AdapterCapability:
    normalized_adapter_id = _required_string(adapter_id, "adapter_id")
    if native_attach_available:
        return AdapterCapability(
            adapter_id=normalized_adapter_id,
            tier="native_attach",
            supported=True,
            reason="native attach is available",
            unsupported_capability_behavior="none",
        )
    if process_bridge_available:
        return AdapterCapability(
            adapter_id=normalized_adapter_id,
            tier="process_bridge",
            supported=True,
            reason="native attach is unavailable; process bridge fallback is available",
            unsupported_capability_behavior="degrade_to_process_bridge",
        )
    return AdapterCapability(
        adapter_id=normalized_adapter_id,
        tier="manual_handoff",
        supported=True,
        reason="native attach and process bridge are unavailable; manual handoff remains available",
        unsupported_capability_behavior="degrade_to_manual_handoff",
    )


def build_adapter_contract(
    *,
    adapter_id: str,
    display_name: str,
    product_family: str,
    adapter_tier: AdapterTier,
    auth_ownership: str,
    workspace_control: str,
    event_visibility: EventVisibility,
    mutation_model: str,
    continuation_model: ContinuationModel,
    evidence_model: EvidenceModel,
    unsupported_capability_behavior: str,
    lifecycle_status: LifecycleStatus = "supported",
    supported_governance_modes: list[str] | None = None,
    minimum_required_runtime_controls: list[str] | None = None,
) -> AdapterContract:
    tier = _required_tier(adapter_tier)
    return AdapterContract(
        adapter_id=_required_string(adapter_id, "adapter_id"),
        display_name=_required_string(display_name, "display_name"),
        product_family=_required_string(product_family, "product_family"),
        lifecycle_status=_required_enum(lifecycle_status, "lifecycle_status", {"experimental", "supported", "deprecated"}),
        adapter_tier=tier,
        auth_ownership=_required_string(auth_ownership, "auth_ownership"),
        workspace_control=_required_string(workspace_control, "workspace_control"),
        event_visibility=_required_enum(
            event_visibility,
            "event_visibility",
            {"structured_jsonl", "mcp_events", "app_protocol_events", "logs_only", "transcript_only", "none"},
        ),
        mutation_model=_required_string(mutation_model, "mutation_model"),
        continuation_model=_required_enum(
            continuation_model,
            "continuation_model",
            {"resume_id", "fork_id", "session_id", "stateless", "manual"},
        ),
        evidence_model=_required_enum(
            evidence_model,
            "evidence_model",
            {"structured_trace", "command_log", "transcript", "diff_artifact", "external_artifact", "manual_summary"},
        ),
        supported_governance_modes=supported_governance_modes or _default_supported_governance_modes(tier),
        minimum_required_runtime_controls=minimum_required_runtime_controls or _default_runtime_controls(tier),
        governance_guarantees=_tier_governance_guarantees(tier),
        unsupported_capability_behavior=_required_string(
            unsupported_capability_behavior,
            "unsupported_capability_behavior",
        ),
    )


def project_codex_profile_to_adapter_contract(profile: object) -> AdapterContract:
    adapter_id = _required_string(getattr(profile, "adapter_id"), "adapter_id")
    adapter_tier = _required_tier(getattr(profile, "adapter_tier"))
    return build_adapter_contract(
        adapter_id=adapter_id,
        display_name="Codex CLI/App",
        product_family="codex",
        adapter_tier=adapter_tier,
        auth_ownership=_required_string(getattr(profile, "auth_ownership"), "auth_ownership"),
        workspace_control=_required_string(getattr(profile, "workspace_control"), "workspace_control"),
        event_visibility=_codex_event_visibility(getattr(profile, "tool_visibility")),
        mutation_model=_required_string(getattr(profile, "mutation_model"), "mutation_model"),
        continuation_model=_codex_continuation_model(getattr(profile, "resume_behavior")),
        evidence_model=_codex_evidence_model(getattr(profile, "evidence_export_capability")),
        unsupported_capability_behavior=_required_string(
            getattr(profile, "unsupported_capability_behavior"),
            "unsupported_capability_behavior",
        ),
    )


def _default_supported_governance_modes(tier: AdapterTier) -> list[str]:
    if tier == "native_attach":
        return ["advisory", "enforced", "strict"]
    if tier == "process_bridge":
        return ["advisory", "enforced"]
    return ["observe_only", "advisory"]


def _default_runtime_controls(tier: AdapterTier) -> list[str]:
    controls = ["policy_decision", "verification_runner", "evidence_bundle", "delivery_handoff"]
    if tier != "manual_handoff":
        controls.append("session_bridge")
    return controls


def _tier_governance_guarantees(tier: AdapterTier) -> list[str]:
    if tier == "native_attach":
        return [
            "attached session boundary",
            "runtime-visible adapter posture",
            "same-contract verification required",
        ]
    if tier == "process_bridge":
        return [
            "captured process boundary",
            "runtime-visible adapter posture",
            "same-contract verification required",
        ]
    return [
        "explicit manual handoff",
        "runtime-visible adapter posture",
        "same-contract verification required",
    ]


def _codex_event_visibility(tool_visibility: object) -> EventVisibility:
    if tool_visibility == "structured_events":
        return "structured_jsonl"
    return "logs_only"


def _codex_continuation_model(resume_behavior: object) -> ContinuationModel:
    if resume_behavior == "resume_id":
        return "resume_id"
    return "manual"


def _codex_evidence_model(evidence_export_capability: object) -> EvidenceModel:
    if evidence_export_capability == "structured_trace":
        return "structured_trace"
    return "manual_summary"


def _required_tier(value: str) -> AdapterTier:
    return _required_enum(value, "adapter_tier", {"native_attach", "process_bridge", "manual_handoff"})


def _required_enum(value: str, field_name: str, valid_values: set[str]) -> str:
    normalized = _required_string(value, field_name)
    if normalized not in valid_values:
        msg = f"unsupported {field_name}: {value}"
        raise ValueError(msg)
    return normalized


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()
