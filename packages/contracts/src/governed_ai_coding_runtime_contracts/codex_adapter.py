"""Codex-first adapter profile contract."""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Callable

from governed_ai_coding_runtime_contracts.adapter_registry import AdapterCapability, resolve_launch_fallback
from governed_ai_coding_runtime_contracts.evidence import EvidenceEvent, EvidenceTimeline
from governed_ai_coding_runtime_contracts.subprocess_guard import parse_optional_positive_timeout, run_subprocess

_DEFAULT_CODEX_EXECUTABLE = "codex"
_CODEX_EXECUTABLE_ENV_KEYS = ("GOVERNED_RUNTIME_CODEX_BIN", "CODEX_BIN")
_FALLBACK_CODEX_EXECUTABLES = ("codex.cmd", "codex.exe")
_CODEX_PROBE_TIMEOUT_SECONDS_ENV_KEY = "GOVERNED_CODEX_PROBE_TIMEOUT_SECONDS"
_CODEX_PROBE_TIMEOUT_SECONDS_DEFAULT = 20.0


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
    failure_stage: str | None = None
    remediation_hint: str | None = None
    probe_attempts: int = 1
    stability_state: str = "single_pass"


@dataclass(frozen=True, slots=True)
class CodexCapabilityReadiness:
    status: str
    adapter_tier: str
    flow_kind: str
    live_attach_available: bool
    structured_events_available: bool
    evidence_export_available: bool
    resume_available: bool
    unsupported_capabilities: list[str]
    failure_stage: str | None
    remediation_hint: str | None
    probe_attempts: int
    stability_state: str


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
    retry_on_degraded: bool = True,
    max_probe_attempts: int = 2,
    command_runner: Callable[[list[str], Path | None], tuple[int, str, str]] | None = None,
    codex_executable: str | None = None,
) -> CodexSurfaceProbe:
    if max_probe_attempts < 1:
        msg = "max_probe_attempts must be >= 1"
        raise ValueError(msg)
    normalized_cwd: Path | None = None
    if cwd is not None:
        normalized_cwd = Path(cwd).resolve(strict=False)
    resolved_executable = _resolve_codex_executable(codex_executable)
    if command_runner is not None:
        return _probe_codex_surface_with_retries(
            cwd=normalized_cwd,
            command_runner=command_runner,
            codex_executable=resolved_executable,
            retry_on_degraded=retry_on_degraded,
            max_probe_attempts=max_probe_attempts,
        )
    if refresh:
        _probe_codex_surface_cached.cache_clear()
    cache_key = f"{normalized_cwd.as_posix() if normalized_cwd is not None else ''}||{resolved_executable}||{max_probe_attempts}"
    probe = _probe_codex_surface_cached(cache_key, retry_on_degraded)
    # Avoid sticky degraded posture when environment recovers later.
    if retry_on_degraded and _is_probe_retry_candidate(probe):
        _probe_codex_surface_cached.cache_clear()
    return probe


def codex_probe_to_dict(probe: CodexSurfaceProbe) -> dict:
    payload = asdict(probe)
    payload["probe_commands"] = [asdict(item) for item in probe.probe_commands]
    return payload


def summarize_codex_capability_readiness(probe: CodexSurfaceProbe | None = None) -> CodexCapabilityReadiness:
    active_probe = probe or probe_codex_surface()
    profile = build_codex_adapter_profile_from_probe(active_probe)
    tier = profile.adapter_tier
    flow_kind = _flow_kind_from_tier(tier)
    if not active_probe.codex_cli_available or tier == "manual_handoff":
        status = "blocked"
    elif profile.unsupported_capabilities:
        status = "degraded"
    else:
        status = "ready"
    return CodexCapabilityReadiness(
        status=status,
        adapter_tier=tier,
        flow_kind=flow_kind,
        live_attach_available=active_probe.native_attach_available,
        structured_events_available=active_probe.structured_events_available,
        evidence_export_available=active_probe.evidence_export_available,
        resume_available=active_probe.resume_available,
        unsupported_capabilities=list(profile.unsupported_capabilities),
        failure_stage=active_probe.failure_stage,
        remediation_hint=active_probe.remediation_hint,
        probe_attempts=active_probe.probe_attempts,
        stability_state=active_probe.stability_state,
    )


def codex_capability_readiness_to_dict(readiness: CodexCapabilityReadiness) -> dict:
    return asdict(readiness)


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
    probe: CodexSurfaceProbe | None = None,
) -> CodexAdapterTrialResult:
    active_probe = probe or CodexSurfaceProbe(
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
    )
    profile = build_codex_adapter_profile_from_probe(active_probe) if probe else build_codex_adapter_profile(
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
        probe=active_probe,
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


@lru_cache(maxsize=8)
def _probe_codex_surface_cached(cwd_key: str, retry_on_degraded: bool) -> CodexSurfaceProbe:
    resolved_cwd_key, _, tail = cwd_key.partition("||")
    executable, _, attempts_text = tail.partition("||")
    cwd = Path(resolved_cwd_key) if resolved_cwd_key else None
    codex_executable = executable or _DEFAULT_CODEX_EXECUTABLE
    max_probe_attempts = 1
    if attempts_text:
        try:
            max_probe_attempts = max(1, int(attempts_text))
        except ValueError:
            max_probe_attempts = 1
    return _probe_codex_surface_with_retries(
        cwd=cwd,
        command_runner=_default_probe_runner,
        codex_executable=codex_executable,
        retry_on_degraded=retry_on_degraded,
        max_probe_attempts=max_probe_attempts,
    )


def _probe_codex_surface_with_retries(
    *,
    cwd: Path | None,
    command_runner: Callable[[list[str], Path | None], tuple[int, str, str]],
    codex_executable: str,
    retry_on_degraded: bool,
    max_probe_attempts: int,
) -> CodexSurfaceProbe:
    probe = _probe_codex_surface(
        cwd=cwd,
        command_runner=command_runner,
        codex_executable=codex_executable,
    )
    if not retry_on_degraded or max_probe_attempts == 1 or not _is_probe_retry_candidate(probe):
        return probe

    best = probe
    best_score = _probe_capability_score(best)
    merged_commands = list(probe.probe_commands)
    for attempt in range(2, max_probe_attempts + 1):
        candidate = _probe_codex_surface(
            cwd=cwd,
            command_runner=command_runner,
            codex_executable=codex_executable,
        )
        merged_commands.extend(candidate.probe_commands)
        candidate_score = _probe_capability_score(candidate)
        if candidate_score >= best_score:
            best = candidate
            best_score = candidate_score
        if not _is_probe_retry_candidate(best):
            reason = best.reason
            if "recovered after probe retry" not in reason:
                reason = f"{reason}; recovered after probe retry"
            return replace(
                best,
                reason=reason,
                probe_commands=merged_commands,
                probe_attempts=attempt,
                stability_state="stabilized",
            )

    return replace(
        best,
        probe_commands=merged_commands,
        probe_attempts=max_probe_attempts,
        stability_state="degraded_after_retry",
    )


def _probe_codex_surface(
    *,
    cwd: Path | None,
    command_runner: Callable[[list[str], Path | None], tuple[int, str, str]],
    codex_executable: str,
) -> CodexSurfaceProbe:
    commands: list[CodexProbeCommand] = []
    effective_executable = codex_executable
    version_exit, version_output = _run_probe_command(
        command_runner=command_runner,
        cwd=cwd,
        argv=[effective_executable, "--version"],
        commands=commands,
    )
    if (
        version_exit != 0
        and _looks_like_missing_command(_safe_ascii(version_output))
        and _can_try_default_fallback(primary_executable=effective_executable)
    ):
        fallback = _try_fallback_codex_executable(
            primary_executable=effective_executable,
            cwd=cwd,
            command_runner=command_runner,
            commands=commands,
        )
        if fallback is not None:
            effective_executable = fallback[0]
            version_exit = fallback[1]
            version_output = fallback[2]
    if version_exit != 0:
        normalized_output = _safe_ascii(version_output)
        if _looks_like_missing_command(normalized_output):
            reason = f"codex CLI is unavailable: {_truncate_output(normalized_output) or 'command not found'}"
            failure_stage = "codex_command_unavailable"
            remediation_hint = (
                f"Make `{effective_executable}` runnable in this shell, then verify "
                f"`{effective_executable} --version`, `{effective_executable} --help`, `{effective_executable} status`."
            )
        else:
            reason = normalized_output or "codex version probe failed"
            failure_stage = "codex_version_probe_failed"
            remediation_hint = (
                f"Run `{effective_executable} --version` manually and fix the failing runtime environment before "
                "enabling live attach."
            )
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
            failure_stage=failure_stage,
            remediation_hint=remediation_hint,
        )

    _, help_output = _run_probe_command(
        command_runner=command_runner,
        cwd=cwd,
        argv=[effective_executable, "--help"],
        commands=commands,
    )
    help_lower = help_output.lower()
    help_commands = _extract_help_commands(help_output)

    exec_help_output = ""
    exec_help_lower = ""
    if "exec" in help_commands:
        _, exec_help_output = _run_probe_command(
            command_runner=command_runner,
            cwd=cwd,
            argv=[effective_executable, "exec", "--help"],
            commands=commands,
        )
        exec_help_lower = exec_help_output.lower()

    status_command_available = "status" in help_commands
    status_exit = 1
    status_output = ""
    status_lower = ""
    if status_command_available:
        status_exit, status_output = _run_probe_command(
            command_runner=command_runner,
            cwd=cwd,
            argv=[effective_executable, "status"],
            commands=commands,
        )
        status_lower = status_output.lower()

    resume_surface_available = "resume" in help_commands or "resume" in exec_help_lower
    native_attach_available = status_command_available and status_exit == 0
    if not status_command_available and resume_surface_available:
        native_attach_available = True
    process_bridge_available = True
    structured_events_available = _detect_structured_events(
        help_lower=help_lower,
        exec_help_lower=exec_help_lower,
    )
    evidence_export_available = _detect_evidence_export(
        help_lower=help_lower,
        exec_help_lower=exec_help_lower,
        structured_events_available=structured_events_available,
    )
    resume_available = _detect_resume_available(
        help_commands=help_commands,
        help_lower=help_lower,
        exec_help_lower=exec_help_lower,
        status_lower=status_lower,
    )

    live_session_id = _extract_identity_token(status_output, "session")
    live_resume_id = _extract_identity_token(status_output, "resume")
    failure_stage: str | None = None
    remediation_hint: str | None = None
    if not status_command_available:
        if native_attach_available:
            reason = "codex status command is unavailable; native attach is inferred from resume command surface"
            remediation_hint = (
                f"Validate native attach via `{effective_executable} exec resume --help` "
                "and a controlled `exec resume --last --json` probe when needed."
            )
        else:
            reason = "codex CLI does not expose a status command; native live attach probe is unavailable in this build"
            failure_stage = "live_attach_probe_unsupported_status_command_missing"
            remediation_hint = (
                f"Use `{effective_executable} exec --json` for process-bridge runs with structured events/evidence. "
                "Native attach requires a Codex build that exposes a status handshake command."
            )
    elif not native_attach_available and "stdin is not a terminal" in status_lower:
        reason = "codex status requires interactive terminal; live attach unavailable in non-interactive mode"
        failure_stage = "live_attach_unavailable_non_interactive"
        remediation_hint = (
            f"Run `{effective_executable} status` in an interactive terminal to validate live attach. "
            "For non-interactive automation, keep process_bridge/manual_handoff."
        )
    elif native_attach_available:
        reason = "codex status handshake succeeded"
    else:
        reason = _safe_ascii(status_output) or "codex status handshake failed; process bridge fallback remains available"
        failure_stage = "codex_status_probe_failed"
        remediation_hint = (
            f"Inspect `{effective_executable} status` output and ensure active auth/session. "
            "If unresolved, keep process_bridge/manual_handoff and capture probe evidence."
        )
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
        failure_stage=failure_stage,
        remediation_hint=remediation_hint,
    )


def _default_probe_runner(argv: list[str], cwd: Path | None) -> tuple[int, str, str]:
    try:
        timeout_seconds = parse_optional_positive_timeout(
            os.environ.get(_CODEX_PROBE_TIMEOUT_SECONDS_ENV_KEY),
            _CODEX_PROBE_TIMEOUT_SECONDS_ENV_KEY,
        )
        if timeout_seconds is None:
            timeout_seconds = _CODEX_PROBE_TIMEOUT_SECONDS_DEFAULT
        use_shell = os.name == "nt" and Path(argv[0]).suffix.lower() != ".exe"
        completed = run_subprocess(
            command=subprocess.list2cmdline(argv) if use_shell else argv,
            shell=use_shell,
            cwd=cwd,
            timeout_seconds=timeout_seconds,
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


def _resolve_codex_executable(explicit: str | None) -> str:
    candidate = _optional_non_empty_string(explicit)
    if candidate is not None:
        return candidate
    for env_key in _CODEX_EXECUTABLE_ENV_KEYS:
        env_value = _optional_non_empty_string(os.environ.get(env_key))
        if env_value is not None:
            return env_value
    return _DEFAULT_CODEX_EXECUTABLE


def _can_try_default_fallback(*, primary_executable: str) -> bool:
    normalized_primary = primary_executable.strip().lower()
    return normalized_primary == _DEFAULT_CODEX_EXECUTABLE


def _try_fallback_codex_executable(
    *,
    primary_executable: str,
    cwd: Path | None,
    command_runner: Callable[[list[str], Path | None], tuple[int, str, str]],
    commands: list[CodexProbeCommand],
) -> tuple[str, int, str] | None:
    primary_normalized = primary_executable.strip().lower()
    for candidate in _FALLBACK_CODEX_EXECUTABLES:
        if candidate.lower() == primary_normalized:
            continue
        exit_code, output = _run_probe_command(
            command_runner=command_runner,
            cwd=cwd,
            argv=[candidate, "--version"],
            commands=commands,
        )
        if exit_code == 0:
            return candidate, exit_code, output
    return None


def _looks_like_missing_command(output: str) -> bool:
    normalized = output.lower()
    patterns = (
        "command not found",
        "is not recognized",
        "no such file or directory",
        "cannot find the file",
        "[winerror 2]",
    )
    return any(pattern in normalized for pattern in patterns)


def _extract_help_commands(output: str) -> set[str]:
    commands: set[str] = set()
    in_commands = False
    for raw_line in output.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        lowered = stripped.lower()
        if not in_commands:
            if lowered.startswith("commands:"):
                in_commands = True
            continue
        if not stripped:
            continue
        if lowered.startswith("arguments:") or lowered.startswith("options:"):
            break
        match = re.match(r"^([a-z0-9][a-z0-9_-]*)\b", lowered)
        if match:
            commands.add(match.group(1))
    return commands


def _detect_structured_events(*, help_lower: str, exec_help_lower: str) -> bool:
    return ("structured" in help_lower and "event" in help_lower) or "--json" in help_lower or "--json" in exec_help_lower


def _detect_evidence_export(*, help_lower: str, exec_help_lower: str, structured_events_available: bool) -> bool:
    if "trace" in help_lower or "evidence" in help_lower:
        return True
    if "--output-last-message" in help_lower or "--output-last-message" in exec_help_lower:
        return True
    return structured_events_available and ("jsonl" in exec_help_lower or "--json" in exec_help_lower)


def _detect_resume_available(
    *,
    help_commands: set[str],
    help_lower: str,
    exec_help_lower: str,
    status_lower: str,
) -> bool:
    return (
        "resume" in help_commands
        or "resume" in help_lower
        or "resume" in exec_help_lower
        or "resume" in status_lower
    )


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


def _is_probe_retry_candidate(probe: CodexSurfaceProbe) -> bool:
    return (
        not probe.codex_cli_available
        or not probe.native_attach_available
        or not probe.structured_events_available
        or not probe.evidence_export_available
        or not probe.resume_available
        or probe.failure_stage is not None
    )


def _probe_capability_score(probe: CodexSurfaceProbe) -> int:
    score = 0
    if probe.codex_cli_available:
        score += 100
    if probe.native_attach_available:
        score += 50
    if probe.process_bridge_available:
        score += 25
    if probe.structured_events_available:
        score += 10
    if probe.evidence_export_available:
        score += 8
    if probe.resume_available:
        score += 6
    if probe.failure_stage is None:
        score += 4
    return score


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
