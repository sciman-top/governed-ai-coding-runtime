"""Codex-first adapter profile contract."""

from dataclasses import asdict, dataclass

from governed_ai_coding_runtime_contracts.adapter_registry import AdapterCapability, resolve_launch_fallback
from governed_ai_coding_runtime_contracts.evidence import EvidenceEvent, EvidenceTimeline


@dataclass(frozen=True, slots=True)
class CodexAdapterProfile:
    adapter_id: str
    auth_ownership: str
    workspace_control: str
    tool_visibility: str
    mutation_model: str
    resume_behavior: str
    evidence_export_capability: str
    adapter_tier: str
    unsupported_capabilities: list[str]
    unsupported_capability_behavior: str
    native_attach_available: bool
    process_bridge_available: bool


@dataclass(frozen=True, slots=True)
class CodexSessionEvidence:
    task_id: str
    adapter_id: str
    adapter_tier: str
    flow_kind: str
    file_changes: list[str]
    tool_calls: list[dict]
    gate_runs: list[str]
    approvals: list[str]
    handoff_refs: list[str]
    unsupported_capabilities: list[str]


@dataclass(frozen=True, slots=True)
class CodexAdapterTrialResult:
    mode: str
    repo_id: str
    task_id: str
    binding_id: str
    adapter_id: str
    adapter_tier: str
    unsupported_capabilities: list[str]
    unsupported_capability_behavior: str
    evidence_refs: list[str]
    verification_refs: list[str]
    handoff_ref: str


def build_codex_adapter_profile(
    *,
    native_attach_available: bool,
    process_bridge_available: bool,
    structured_events_available: bool,
    evidence_export_available: bool,
    resume_available: bool,
) -> CodexAdapterProfile:
    capability = resolve_launch_fallback(
        adapter_id="codex-cli",
        native_attach_available=native_attach_available,
        process_bridge_available=process_bridge_available,
    )
    unsupported_capabilities = _unsupported_capabilities(
        native_attach_available=native_attach_available,
        process_bridge_available=process_bridge_available,
        structured_events_available=structured_events_available,
        evidence_export_available=evidence_export_available,
        resume_available=resume_available,
    )
    return CodexAdapterProfile(
        adapter_id="codex-cli",
        auth_ownership="user_owned_upstream_auth",
        workspace_control="external_workspace",
        tool_visibility="structured_events" if structured_events_available else "logs_or_transcript_only",
        mutation_model="direct_workspace_write",
        resume_behavior="resume_id" if resume_available else "manual",
        evidence_export_capability="structured_trace" if evidence_export_available else "manual_summary",
        adapter_tier=capability.tier,
        unsupported_capabilities=unsupported_capabilities,
        unsupported_capability_behavior=capability.unsupported_capability_behavior,
        native_attach_available=native_attach_available,
        process_bridge_available=process_bridge_available,
    )


def classify_codex_adapter(profile: CodexAdapterProfile) -> AdapterCapability:
    return resolve_launch_fallback(
        adapter_id=profile.adapter_id,
        native_attach_available=profile.native_attach_available,
        process_bridge_available=profile.process_bridge_available,
    )


def record_codex_session_evidence(
    timeline: EvidenceTimeline,
    session: CodexSessionEvidence,
) -> list[EvidenceEvent]:
    events: list[EvidenceEvent] = [
        timeline.append(
            session.task_id,
            "codex_adapter_posture",
            {
                "adapter_id": session.adapter_id,
                "adapter_tier": session.adapter_tier,
                "flow_kind": session.flow_kind,
                "unsupported_capabilities": session.unsupported_capabilities,
            },
        )
    ]
    events.extend(
        timeline.append(session.task_id, "adapter_file_change", {"path": path, "adapter_id": session.adapter_id})
        for path in session.file_changes
    )
    events.extend(
        timeline.append(session.task_id, "adapter_tool_call", {"adapter_id": session.adapter_id, **tool_call})
        for tool_call in session.tool_calls
    )
    events.extend(
        timeline.append(session.task_id, "adapter_gate_run", {"artifact_ref": artifact_ref, "adapter_id": session.adapter_id})
        for artifact_ref in session.gate_runs
    )
    events.extend(
        timeline.append(session.task_id, "adapter_approval_event", {"approval_id": approval_id, "adapter_id": session.adapter_id})
        for approval_id in session.approvals
    )
    events.extend(
        timeline.append(session.task_id, "adapter_handoff", {"handoff_ref": handoff_ref, "adapter_id": session.adapter_id})
        for handoff_ref in session.handoff_refs
    )
    return events


def build_codex_adapter_trial_result(
    *,
    repo_id: str,
    task_id: str,
    binding_id: str,
    native_attach_available: bool,
    process_bridge_available: bool,
    structured_events_available: bool,
    evidence_export_available: bool,
    resume_available: bool,
    mode: str = "safe",
    run_id: str = "codex-trial-safe",
) -> CodexAdapterTrialResult:
    profile = build_codex_adapter_profile(
        native_attach_available=native_attach_available,
        process_bridge_available=process_bridge_available,
        structured_events_available=structured_events_available,
        evidence_export_available=evidence_export_available,
        resume_available=resume_available,
    )
    normalized_mode = _required_string(mode, "mode")
    normalized_run_id = _required_string(run_id, "run_id")
    normalized_task_id = _required_string(task_id, "task_id")
    base_ref = f"artifacts/{normalized_task_id}/{normalized_run_id}"
    evidence_refs = [
        f"{base_ref}/evidence/codex-session.json",
        f"{base_ref}/handoff/package.json",
    ]
    verification_refs = [
        f"{base_ref}/verification-output/runtime.txt",
        f"{base_ref}/verification-output/contract.txt",
    ]
    return CodexAdapterTrialResult(
        mode=normalized_mode,
        repo_id=_required_string(repo_id, "repo_id"),
        task_id=normalized_task_id,
        binding_id=_required_string(binding_id, "binding_id"),
        adapter_id=profile.adapter_id,
        adapter_tier=profile.adapter_tier,
        unsupported_capabilities=list(profile.unsupported_capabilities),
        unsupported_capability_behavior=profile.unsupported_capability_behavior,
        evidence_refs=evidence_refs,
        verification_refs=verification_refs,
        handoff_ref=f"{base_ref}/handoff/package.json",
    )


def codex_adapter_trial_to_dict(result: CodexAdapterTrialResult) -> dict:
    return asdict(result)


def _unsupported_capabilities(
    *,
    native_attach_available: bool,
    process_bridge_available: bool,
    structured_events_available: bool,
    evidence_export_available: bool,
    resume_available: bool,
) -> list[str]:
    unsupported: list[str] = []
    if not native_attach_available:
        unsupported.append("native_attach")
    if not process_bridge_available:
        unsupported.append("process_bridge")
    if not structured_events_available:
        unsupported.append("structured_events")
    if not evidence_export_available:
        unsupported.append("structured_evidence_export")
    if not resume_available:
        unsupported.append("resume_id")
    return unsupported


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()
