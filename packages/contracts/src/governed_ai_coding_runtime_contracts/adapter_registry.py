"""Minimal adapter capability helpers for launch-second fallback."""

from dataclasses import dataclass
from typing import Callable
from typing import Literal


AdapterTier = Literal["native_attach", "process_bridge", "manual_handoff"]
LifecycleStatus = Literal["experimental", "supported", "deprecated"]
EventVisibility = Literal["structured_jsonl", "mcp_events", "app_protocol_events", "logs_only", "transcript_only", "none"]
ContinuationModel = Literal["resume_id", "fork_id", "session_id", "stateless", "manual"]
EvidenceModel = Literal["structured_trace", "command_log", "transcript", "diff_artifact", "external_artifact", "manual_summary"]
AdapterProbe = Callable[[dict], "AdapterProbeResult"]
AdapterDelegate = Callable[[dict], dict]


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


@dataclass(frozen=True, slots=True)
class AdapterProbeResult:
    adapter_id: str
    native_attach_available: bool
    process_bridge_available: bool
    reason: str
    probe_source: str = "registry_default"
    session_id: str | None = None
    resume_id: str | None = None


@dataclass(frozen=True, slots=True)
class AdapterSelection:
    adapter_id: str
    tier: AdapterTier
    flow_kind: str
    reason: str
    unsupported_capability_behavior: str
    probe_source: str
    requested_tier: AdapterTier | None = None
    degraded: bool = False
    degrade_reason: str | None = None


def adapter_selection_from_dict(raw: dict) -> AdapterSelection:
    if not isinstance(raw, dict):
        msg = "adapter selection payload must be an object"
        raise ValueError(msg)
    requested_tier = raw.get("requested_tier")
    if requested_tier is not None:
        requested_tier = _required_tier(requested_tier)
    degraded = raw.get("degraded", False)
    if not isinstance(degraded, bool):
        msg = "degraded must be a boolean"
        raise ValueError(msg)
    return AdapterSelection(
        adapter_id=_required_string(raw.get("adapter_id"), "adapter_id"),
        tier=_required_tier(raw.get("tier")),
        flow_kind=_required_string(raw.get("flow_kind"), "flow_kind"),
        reason=_required_string(raw.get("reason"), "reason"),
        unsupported_capability_behavior=_required_string(
            raw.get("unsupported_capability_behavior"),
            "unsupported_capability_behavior",
        ),
        probe_source=_required_string(raw.get("probe_source"), "probe_source"),
        requested_tier=requested_tier,
        degraded=degraded,
        degrade_reason=_optional_string(raw.get("degrade_reason"), "degrade_reason"),
    )


class ExecutableAdapterRegistry:
    def __init__(self) -> None:
        self._contracts: dict[str, AdapterContract] = {}
        self._probers: dict[str, AdapterProbe] = {}
        self._delegates: dict[str, AdapterDelegate] = {}

    def register(
        self,
        *,
        contract: AdapterContract,
        probe: AdapterProbe | None = None,
        delegate: AdapterDelegate | None = None,
    ) -> None:
        self._contracts[contract.adapter_id] = contract
        if probe is not None:
            self._probers[contract.adapter_id] = probe
        if delegate is not None:
            self._delegates[contract.adapter_id] = delegate

    def adapter_ids(self) -> list[str]:
        return sorted(self._contracts)

    def discover(
        self,
        *,
        product_family: str | None = None,
        adapter_tier: AdapterTier | None = None,
    ) -> list[AdapterContract]:
        contracts = list(self._contracts.values())
        if product_family is not None:
            normalized_family = _required_string(product_family, "product_family")
            contracts = [contract for contract in contracts if contract.product_family == normalized_family]
        if adapter_tier is not None:
            normalized_tier = _required_tier(adapter_tier)
            contracts = [contract for contract in contracts if contract.adapter_tier == normalized_tier]
        return sorted(contracts, key=lambda contract: contract.adapter_id)

    def probe(self, adapter_id: str, *, context: dict | None = None) -> AdapterProbeResult:
        normalized_adapter_id = _required_string(adapter_id, "adapter_id")
        contract = self._contracts.get(normalized_adapter_id)
        if contract is None:
            msg = f"adapter is not registered: {normalized_adapter_id}"
            raise ValueError(msg)
        probe = self._probers.get(normalized_adapter_id)
        if probe is None:
            return AdapterProbeResult(
                adapter_id=normalized_adapter_id,
                native_attach_available=contract.adapter_tier == "native_attach",
                process_bridge_available=contract.adapter_tier in {"native_attach", "process_bridge"},
                reason="no live probe registered; using contract-declared tier",
                probe_source="contract_declared",
            )
        result = probe(dict(context or {}))
        if result.adapter_id != normalized_adapter_id:
            msg = "probe result adapter_id does not match registry key"
            raise ValueError(msg)
        return result

    def select(self, adapter_id: str, *, context: dict | None = None) -> AdapterSelection:
        probe_result = self.probe(adapter_id, context=context)
        capability = resolve_launch_fallback(
            adapter_id=probe_result.adapter_id,
            native_attach_available=probe_result.native_attach_available,
            process_bridge_available=probe_result.process_bridge_available,
        )
        requested_tier = _requested_tier_from_context(context)
        degraded = requested_tier is not None and _tier_order(capability.tier) < _tier_order(requested_tier)
        degrade_reason = None
        if degraded:
            degrade_reason = f"requested {requested_tier} degraded to {capability.tier}"
        return AdapterSelection(
            adapter_id=capability.adapter_id,
            tier=capability.tier,
            flow_kind=_flow_kind(capability.tier),
            reason=probe_result.reason or capability.reason,
            unsupported_capability_behavior=capability.unsupported_capability_behavior,
            probe_source=probe_result.probe_source,
            requested_tier=requested_tier,
            degraded=degraded,
            degrade_reason=degrade_reason,
        )

    def select_for_attachment(
        self,
        *,
        attachment: dict,
        preferred_adapter_id: str | None = None,
        context: dict | None = None,
    ) -> AdapterSelection:
        if not isinstance(attachment, dict):
            msg = "attachment is required"
            raise ValueError(msg)
        requested_tier = _requested_tier_from_context({"requested_tier": attachment.get("adapter_preference")})
        allowed_adapters = attachment.get("allowed_adapters")
        allowed: set[str] = set(self._contracts)
        if isinstance(allowed_adapters, list) and allowed_adapters:
            allowed = {_required_string(item, "allowed_adapters[]") for item in allowed_adapters}
        candidate_ids: list[str] = []
        if preferred_adapter_id is not None:
            candidate_ids.append(_required_string(preferred_adapter_id, "preferred_adapter_id"))
        candidate_ids.extend(adapter_id for adapter_id in sorted(self._contracts) if adapter_id not in candidate_ids)

        selections: list[AdapterSelection] = []
        for candidate_id in candidate_ids:
            if candidate_id not in self._contracts or candidate_id not in allowed:
                continue
            runtime_context = dict(context or {})
            runtime_context.setdefault("requested_tier", requested_tier)
            runtime_context.setdefault("attachment", attachment)
            selections.append(self.select(candidate_id, context=runtime_context))
        if not selections:
            msg = "no registered adapters satisfy attachment constraints"
            raise ValueError(msg)

        ranked = sorted(
            selections,
            key=lambda selection: (
                _requested_match_score(selection.tier, requested_tier),
                _tier_order(selection.tier),
            ),
            reverse=True,
        )
        return ranked[0]

    def delegate(
        self,
        *,
        adapter_id: str,
        context: dict | None = None,
        request: dict | None = None,
    ) -> dict:
        selection = self.select(adapter_id, context=context)
        delegate = self._delegates.get(selection.adapter_id)
        if delegate is None:
            return {
                "adapter_id": selection.adapter_id,
                "tier": selection.tier,
                "flow_kind": selection.flow_kind,
                "status": "manual_handoff" if selection.tier == "manual_handoff" else "selected_no_delegate",
                "reason": selection.reason,
                "unsupported_capability_behavior": selection.unsupported_capability_behavior,
                "probe_source": selection.probe_source,
                "requested_tier": selection.requested_tier,
                "degraded": selection.degraded,
                "degrade_reason": selection.degrade_reason,
            }
        result = dict(delegate(dict(request or {})))
        result.setdefault("adapter_id", selection.adapter_id)
        result.setdefault("tier", selection.tier)
        result.setdefault("flow_kind", selection.flow_kind)
        result.setdefault("unsupported_capability_behavior", selection.unsupported_capability_behavior)
        result.setdefault("probe_source", selection.probe_source)
        result.setdefault("requested_tier", selection.requested_tier)
        result.setdefault("degraded", selection.degraded)
        result.setdefault("degrade_reason", selection.degrade_reason)
        return result


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


def build_claude_code_contract(*, adapter_tier: AdapterTier = "process_bridge") -> AdapterContract:
    tier = _required_tier(adapter_tier)
    unsupported_behavior = "degrade_to_process_bridge"
    if tier == "native_attach":
        unsupported_behavior = "none"
    elif tier == "process_bridge":
        unsupported_behavior = "degrade_to_process_bridge"
    elif tier == "manual_handoff":
        unsupported_behavior = "degrade_to_manual_handoff"
    return build_adapter_contract(
        adapter_id="claude-code",
        display_name="Claude Code",
        product_family="claude_code",
        adapter_tier=tier,
        auth_ownership="user_owned_upstream_auth",
        workspace_control="external_workspace",
        event_visibility="structured_jsonl" if tier == "native_attach" else "logs_only",
        mutation_model="direct_workspace_write",
        continuation_model="resume_id" if tier == "native_attach" else "manual",
        evidence_model="structured_trace" if tier == "native_attach" else "command_log",
        unsupported_capability_behavior=unsupported_behavior,
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


def _flow_kind(tier: AdapterTier) -> str:
    if tier == "native_attach":
        return "live_attach"
    if tier == "process_bridge":
        return "process_bridge"
    return "manual_handoff"


def _requested_tier_from_context(context: dict | None) -> AdapterTier | None:
    if not isinstance(context, dict):
        return None
    requested = context.get("requested_tier")
    if requested is None:
        return None
    return _required_tier(requested)


def _tier_order(tier: AdapterTier) -> int:
    if tier == "manual_handoff":
        return 0
    if tier == "process_bridge":
        return 1
    return 2


def _requested_match_score(actual_tier: AdapterTier, requested_tier: AdapterTier | None) -> int:
    if requested_tier is None:
        return 1
    delta = abs(_tier_order(actual_tier) - _tier_order(requested_tier))
    return 100 - delta


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


def _optional_string(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, field_name)
