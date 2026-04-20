"""Codex-first adapter profile contract."""

from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Callable

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
    probe_source: str
    posture_reason: str


@dataclass(frozen=True, slots=True)
class CodexProbeCommand:
    cmd: str
    exit_code: int
    key_output: str
    timestamp: str


@dataclass(frozen=True, slots=True)
class CodexSurfaceProbe:
    codex_cli_available: bool
    version: str | None
    native_attach_available: bool
    process_bridge_available: bool
    structured_events_available: bool
    evidence_export_available: bool
    resume_available: bool
    live_session_id: str | None
    live_resume_id: str | None
    reason: str
    probe_commands: list[CodexProbeCommand]


@dataclass(frozen=True, slots=True)
class CodexLiveHandshake:
    adapter_id: str
    adapter_tier: str
    flow_kind: str
    session_id: str | None
    resume_id: str | None
    continuation_id: str
    live_attach_available: bool
    unsupported_capabilities: list[str]
    posture_reason: str


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
    execution_id: str | None = None
    continuation_id: str | None = None
    event_source: str = "manual_handoff"
    unsupported_events: list[dict] | None = None


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
    flow_kind: str
    session_id: str | None
    resume_id: str | None
    continuation_id: str
    probe_source: str
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
    probe_source: str = "declared_flags",
    posture_reason: str = "",
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
        probe_source=_required_string(probe_source, "probe_source"),
        posture_reason=_optional_non_empty_string(posture_reason) or capability.reason,
    )


def build_codex_adapter_profile_from_probe(probe: CodexSurfaceProbe) -> CodexAdapterProfile:
    return build_codex_adapter_profile(
        native_attach_available=probe.native_attach_available,
        process_bridge_available=probe.process_bridge_available,
        structured_events_available=probe.structured_events_available,
        evidence_export_available=probe.evidence_export_available,
        resume_available=probe.resume_available,
        probe_source="live_probe",
        posture_reason=probe.reason,
    )


def classify_codex_adapter(profile: CodexAdapterProfile) -> AdapterCapability:
    return resolve_launch_fallback(
        adapter_id=profile.adapter_id,
        native_attach_available=profile.native_attach_available,
        process_bridge_available=profile.process_bridge_available,
    )


def probe_codex_surface(
    *,
    cwd: str | Path | None = None,
    refresh: bool = False,
    command_runner: Callable[[list[str], Path | None], tuple[int, str, str]] | None = None,
) -> CodexSurfaceProbe:
    normalized_cwd: Path | None = None
    if cwd is not None:
        normalized_cwd = Path(cwd).resolve(strict=False)
    if command_runner is not None:
        return _probe_codex_surface(cwd=normalized_cwd, command_runner=command_runner)
    if refresh:
        _probe_codex_surface_cached.cache_clear()
    cache_key = normalized_cwd.as_posix() if normalized_cwd is not None else ""
    return _probe_codex_surface_cached(cache_key)


def codex_probe_to_dict(probe: CodexSurfaceProbe) -> dict:
    payload = asdict(probe)
    payload["probe_commands"] = [asdict(item) for item in probe.probe_commands]
    return payload


def handshake_codex_session(
    *,
    task_id: str,
    command_id: str,
    payload: dict | None = None,
    continuation_id: str | None = None,
    probe: CodexSurfaceProbe | None = None,
) -> CodexLiveHandshake:
    normalized_task_id = _required_string(task_id, "task_id")
    normalized_command_id = _required_string(command_id, "command_id")
    normalized_payload = payload if isinstance(payload, dict) else {}
    active_probe = probe or probe_codex_surface()
    profile = build_codex_adapter_profile_from_probe(active_probe)
    capability = classify_codex_adapter(profile)

    digest = hashlib.sha1(f"{normalized_task_id}:{normalized_command_id}".encode("utf-8")).hexdigest()[:12]
    session_id = (
        _payload_optional_string(normalized_payload, "session_id")
        or active_probe.live_session_id
        or f"codex-session-{digest}"
    )
    resume_id = _payload_optional_string(normalized_payload, "resume_id") or active_probe.live_resume_id
    if resume_id is None and profile.resume_behavior == "resume_id":
        resume_id = f"codex-resume-{digest}"
    explicit_continuation = _payload_optional_string(normalized_payload, "continuation_id")
    normalized_continuation = (
        continuation_id
        or explicit_continuation
        or resume_id
        or f"{normalized_task_id}:{normalized_command_id}"
    )
    flow_kind = _flow_kind_from_tier(capability.tier)
    return CodexLiveHandshake(
        adapter_id=profile.adapter_id,
        adapter_tier=capability.tier,
        flow_kind=flow_kind,
        session_id=session_id,
        resume_id=resume_id,
        continuation_id=normalized_continuation,
        live_attach_available=active_probe.native_attach_available,
        unsupported_capabilities=list(profile.unsupported_capabilities),
        posture_reason=profile.posture_reason,
    )


def record_codex_session_evidence(
    timeline: EvidenceTimeline,
    session: CodexSessionEvidence,
) -> list[EvidenceEvent]:
    events: list[EvidenceEvent] = [
        timeline.append(
            session.task_id,
            "codex_adapter_posture",
            _session_event_payload(
                session,
                {
                    "adapter_tier": session.adapter_tier,
                    "flow_kind": session.flow_kind,
                    "unsupported_capabilities": session.unsupported_capabilities,
                },
            ),
        )
    ]
    events.extend(
        timeline.append(
            session.task_id,
            "adapter_file_change",
            _session_event_payload(session, {"path": path}),
        )
        for path in session.file_changes
    )
    events.extend(
        timeline.append(
            session.task_id,
            "adapter_tool_call",
            _session_event_payload(session, tool_call),
        )
        for tool_call in session.tool_calls
    )
    events.extend(
        timeline.append(
            session.task_id,
            "adapter_gate_run",
            _session_event_payload(session, {"artifact_ref": artifact_ref}),
        )
        for artifact_ref in session.gate_runs
    )
    events.extend(
        timeline.append(
            session.task_id,
            "adapter_approval_event",
            _session_event_payload(session, {"approval_id": approval_id}),
        )
        for approval_id in session.approvals
    )
    events.extend(
        timeline.append(
            session.task_id,
            "adapter_handoff",
            _session_event_payload(session, {"handoff_ref": handoff_ref}),
        )
        for handoff_ref in session.handoff_refs
    )
    events.extend(
        timeline.append(
            session.task_id,
            "adapter_unsupported_event",
            _session_event_payload(
                session,
                {
                    "capability": capability,
                    "reason": "unsupported capability recorded by adapter posture",
                },
            ),
        )
        for capability in session.unsupported_capabilities
    )
    for item in session.unsupported_events or []:
        if not isinstance(item, dict):
            continue
        capability = _payload_optional_string(item, "capability")
        event_type = _payload_optional_string(item, "event_type")
        reason = _payload_optional_string(item, "reason") or "unsupported adapter event"
        events.append(
            timeline.append(
                session.task_id,
                "adapter_unsupported_event",
                _session_event_payload(
                    session,
                    {
                        "capability": capability,
                        "event_type": event_type,
                        "reason": reason,
                        "raw_event": item,
                    },
                ),
            )
        )
    return events


def codex_session_events_to_records(session: CodexSessionEvidence) -> list[dict]:
    records: list[dict] = []
    created_at = datetime.now(UTC).isoformat()

    def _record(event_type: str, payload: dict) -> None:
        record = {
            "task_id": session.task_id,
            "adapter_id": session.adapter_id,
            "adapter_tier": session.adapter_tier,
            "flow_kind": session.flow_kind,
            "event_type": event_type,
            "payload": dict(payload),
            "execution_id": session.execution_id,
            "continuation_id": session.continuation_id,
            "event_source": session.event_source,
            "created_at": created_at,
        }
        records.append(record)

    _record(
        "codex_adapter_posture",
        {"unsupported_capabilities": list(session.unsupported_capabilities)},
    )
    for path in session.file_changes:
        _record("adapter_file_change", {"path": path})
    for tool_call in session.tool_calls:
        _record("adapter_tool_call", dict(tool_call))
    for gate_run in session.gate_runs:
        _record("adapter_gate_run", {"artifact_ref": gate_run})
    for approval in session.approvals:
        _record("adapter_approval_event", {"approval_id": approval})
    for handoff in session.handoff_refs:
        _record("adapter_handoff", {"handoff_ref": handoff})
    for capability in session.unsupported_capabilities:
        _record(
            "adapter_unsupported_event",
            {
                "capability": capability,
                "reason": "unsupported capability recorded by adapter posture",
            },
        )
    for item in session.unsupported_events or []:
        if not isinstance(item, dict):
            continue
        _record("adapter_unsupported_event", dict(item))

    return records


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
    handshake = handshake_codex_session(
        task_id=normalized_task_id,
        command_id=normalized_run_id,
        continuation_id=f"{normalized_task_id}:{normalized_run_id}",
        probe=CodexSurfaceProbe(
            codex_cli_available=True,
            version=None,
            native_attach_available=native_attach_available,
            process_bridge_available=process_bridge_available,
            structured_events_available=structured_events_available,
            evidence_export_available=evidence_export_available,
            resume_available=resume_available,
            live_session_id=None,
            live_resume_id=None,
            reason="declared trial flags",
            probe_commands=[],
        ),
    )
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
        flow_kind=handshake.flow_kind,
        session_id=handshake.session_id,
        resume_id=handshake.resume_id,
        continuation_id=handshake.continuation_id,
        probe_source=profile.probe_source,
        evidence_refs=evidence_refs,
        verification_refs=verification_refs,
        handoff_ref=f"{base_ref}/handoff/package.json",
    )


def codex_adapter_trial_to_dict(result: CodexAdapterTrialResult) -> dict:
    return asdict(result)


@lru_cache(maxsize=4)
def _probe_codex_surface_cached(cwd_key: str) -> CodexSurfaceProbe:
    cwd = Path(cwd_key) if cwd_key else None
    return _probe_codex_surface(cwd=cwd, command_runner=_default_probe_runner)


def _probe_codex_surface(
    *,
    cwd: Path | None,
    command_runner: Callable[[list[str], Path | None], tuple[int, str, str]],
) -> CodexSurfaceProbe:
    commands: list[CodexProbeCommand] = []
    version_exit, version_output = _run_probe_command(
        command_runner=command_runner,
        cwd=cwd,
        argv=["codex", "--version"],
        commands=commands,
    )
    if version_exit != 0:
        reason = _safe_ascii(version_output) or "codex command is unavailable"
        return CodexSurfaceProbe(
            codex_cli_available=False,
            version=None,
            native_attach_available=False,
            process_bridge_available=False,
            structured_events_available=False,
            evidence_export_available=False,
            resume_available=False,
            live_session_id=None,
            live_resume_id=None,
            reason=reason,
            probe_commands=commands,
        )

    _, help_output = _run_probe_command(
        command_runner=command_runner,
        cwd=cwd,
        argv=["codex", "--help"],
        commands=commands,
    )
    status_exit, status_output = _run_probe_command(
        command_runner=command_runner,
        cwd=cwd,
        argv=["codex", "status"],
        commands=commands,
    )

    help_lower = help_output.lower()
    status_lower = status_output.lower()
    native_attach_available = status_exit == 0
    process_bridge_available = True
    structured_events_available = ("structured" in help_lower and "event" in help_lower) or "--json" in help_lower
    evidence_export_available = "trace" in help_lower or "evidence" in help_lower
    resume_available = "resume" in help_lower or "resume" in status_lower

    live_session_id = _extract_identity_token(status_output, "session")
    live_resume_id = _extract_identity_token(status_output, "resume")
    if not native_attach_available and "stdin is not a terminal" in status_lower:
        reason = "codex status requires interactive terminal; live attach unavailable in non-interactive mode"
    elif native_attach_available:
        reason = "codex status handshake succeeded"
    else:
        reason = _safe_ascii(status_output) or "codex status handshake failed; process bridge fallback remains available"
    version = _safe_ascii(version_output).splitlines()[0].strip() if version_output.strip() else None
    return CodexSurfaceProbe(
        codex_cli_available=True,
        version=version,
        native_attach_available=native_attach_available,
        process_bridge_available=process_bridge_available,
        structured_events_available=structured_events_available,
        evidence_export_available=evidence_export_available,
        resume_available=resume_available,
        live_session_id=live_session_id,
        live_resume_id=live_resume_id,
        reason=reason,
        probe_commands=commands,
    )


def _default_probe_runner(argv: list[str], cwd: Path | None) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        return 127, "", str(exc)
    return completed.returncode, completed.stdout, completed.stderr


def _run_probe_command(
    *,
    command_runner: Callable[[list[str], Path | None], tuple[int, str, str]],
    cwd: Path | None,
    argv: list[str],
    commands: list[CodexProbeCommand],
) -> tuple[int, str]:
    exit_code, stdout, stderr = command_runner(argv, cwd)
    output = _safe_ascii("\n".join(part for part in [stdout, stderr] if part).strip())
    commands.append(
        CodexProbeCommand(
            cmd=" ".join(argv),
            exit_code=exit_code,
            key_output=_truncate_output(output),
            timestamp=datetime.now(UTC).isoformat(),
        )
    )
    return exit_code, output


def _extract_identity_token(output: str, token_name: str) -> str | None:
    token = _required_string(token_name, "token_name")
    match = re.search(rf"{token}[_\s-]*id\s*[:=]\s*([^\s,;]+)", output, re.IGNORECASE)
    if not match:
        return None
    candidate = match.group(1).strip()
    if not candidate:
        return None
    return candidate


def _flow_kind_from_tier(tier: str) -> str:
    if tier == "native_attach":
        return "live_attach"
    if tier == "process_bridge":
        return "process_bridge"
    return "manual_handoff"


def _truncate_output(output: str, limit: int = 240) -> str:
    normalized = output.strip()
    if not normalized:
        return ""
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _safe_ascii(value: str) -> str:
    if not isinstance(value, str):
        return ""
    return value.encode("ascii", "replace").decode("ascii")


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


def _optional_non_empty_string(value: str) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized


def _payload_optional_string(payload: dict, field_name: str) -> str | None:
    value = payload.get(field_name)
    if value is None:
        return None
    return _required_string(value, field_name)


def _session_event_payload(session: CodexSessionEvidence, payload: dict) -> dict:
    normalized = {"adapter_id": session.adapter_id, **dict(payload)}
    if session.event_source:
        normalized["event_source"] = session.event_source
    if session.execution_id:
        normalized["execution_id"] = session.execution_id
    if session.continuation_id:
        normalized["continuation_id"] = session.continuation_id
    return normalized
