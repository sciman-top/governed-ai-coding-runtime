"""Claude Code first-class adapter probe and trial helpers."""

from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from governed_ai_coding_runtime_contracts.adapter_registry import AdapterCapability, resolve_launch_fallback
from governed_ai_coding_runtime_contracts.subprocess_guard import parse_optional_positive_timeout, run_subprocess

_DEFAULT_CLAUDE_EXECUTABLE = "claude"
_CLAUDE_EXECUTABLE_ENV_KEYS = ("GOVERNED_RUNTIME_CLAUDE_BIN", "CLAUDE_BIN")
_CLAUDE_PROBE_TIMEOUT_SECONDS_ENV_KEY = "GOVERNED_CLAUDE_PROBE_TIMEOUT_SECONDS"
_CLAUDE_PROBE_TIMEOUT_SECONDS_DEFAULT = 20.0


@dataclass(frozen=True, slots=True)
class ClaudeCodeAdapterProfile:
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
    settings_available: bool
    hooks_available: bool
    probe_source: str
    posture_reason: str


@dataclass(frozen=True, slots=True)
class ClaudeCodeProbeCommand:
    cmd: str
    exit_code: int
    key_output: str
    timestamp: str


@dataclass(frozen=True, slots=True)
class ClaudeCodeSurfaceProbe:
    claude_cli_available: bool
    version: str | None
    native_attach_available: bool
    process_bridge_available: bool
    settings_available: bool
    hooks_available: bool
    structured_events_available: bool
    evidence_export_available: bool
    resume_available: bool
    live_session_id: str | None
    live_resume_id: str | None
    reason: str
    probe_commands: list[ClaudeCodeProbeCommand]
    failure_stage: str | None = None
    remediation_hint: str | None = None


@dataclass(frozen=True, slots=True)
class ClaudeCodeCapabilityReadiness:
    status: str
    adapter_tier: str
    flow_kind: str
    settings_available: bool
    hooks_available: bool
    unsupported_capabilities: list[str]
    failure_stage: str | None
    remediation_hint: str | None


@dataclass(frozen=True, slots=True)
class ClaudeCodeAdapterTrialResult:
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
    hook_evidence_refs: list[str]
    handoff_ref: str
    replay_ref: str


def build_claude_code_adapter_profile(
    *,
    process_bridge_available: bool,
    settings_available: bool,
    hooks_available: bool,
    structured_events_available: bool,
    evidence_export_available: bool,
    resume_available: bool,
    native_attach_available: bool = False,
    probe_source: str = "declared_flags",
    posture_reason: str = "",
) -> ClaudeCodeAdapterProfile:
    capability = resolve_launch_fallback(
        adapter_id="claude-code",
        native_attach_available=native_attach_available,
        process_bridge_available=process_bridge_available,
    )
    unsupported_capabilities = _unsupported_capabilities(
        native_attach_available=native_attach_available,
        process_bridge_available=process_bridge_available,
        settings_available=settings_available,
        hooks_available=hooks_available,
        structured_events_available=structured_events_available,
        evidence_export_available=evidence_export_available,
        resume_available=resume_available,
    )
    return ClaudeCodeAdapterProfile(
        adapter_id="claude-code",
        auth_ownership="user_owned_upstream_auth",
        workspace_control="external_workspace",
        tool_visibility="logs_or_transcript_only",
        mutation_model="direct_workspace_write",
        resume_behavior="manual",
        evidence_export_capability="command_log",
        adapter_tier=capability.tier,
        unsupported_capabilities=unsupported_capabilities,
        unsupported_capability_behavior=capability.unsupported_capability_behavior,
        native_attach_available=native_attach_available,
        process_bridge_available=process_bridge_available,
        settings_available=settings_available,
        hooks_available=hooks_available,
        probe_source=_required_string(probe_source, "probe_source"),
        posture_reason=_optional_non_empty_string(posture_reason) or capability.reason,
    )


def build_claude_code_adapter_profile_from_probe(probe: ClaudeCodeSurfaceProbe) -> ClaudeCodeAdapterProfile:
    return build_claude_code_adapter_profile(
        native_attach_available=probe.native_attach_available,
        process_bridge_available=probe.process_bridge_available,
        settings_available=probe.settings_available,
        hooks_available=probe.hooks_available,
        structured_events_available=probe.structured_events_available,
        evidence_export_available=probe.evidence_export_available,
        resume_available=probe.resume_available,
        probe_source="live_probe",
        posture_reason=probe.reason,
    )


def classify_claude_code_adapter(profile: ClaudeCodeAdapterProfile) -> AdapterCapability:
    return resolve_launch_fallback(
        adapter_id=profile.adapter_id,
        native_attach_available=profile.native_attach_available,
        process_bridge_available=profile.process_bridge_available,
    )


def probe_claude_code_surface(
    *,
    cwd: str | Path | None = None,
    command_runner: Callable[[list[str], Path | None], tuple[int, str, str]] | None = None,
    claude_executable: str | None = None,
) -> ClaudeCodeSurfaceProbe:
    normalized_cwd: Path | None = None
    if cwd is not None:
        normalized_cwd = Path(cwd).resolve(strict=False)
    resolved_executable = _resolve_claude_executable(claude_executable)
    runner = command_runner or _default_probe_runner

    commands: list[ClaudeCodeProbeCommand] = []
    version_exit, version_output = _run_probe_command(
        command_runner=runner,
        cwd=normalized_cwd,
        argv=[resolved_executable, "--version"],
        commands=commands,
    )
    if version_exit != 0:
        normalized_output = _safe_ascii(version_output)
        if _looks_like_missing_command(normalized_output):
            reason = f"Claude Code CLI is unavailable: {_truncate_output(normalized_output) or 'command not found'}"
            failure_stage = "claude_command_unavailable"
            remediation_hint = (
                f"Make `{resolved_executable}` runnable in this shell, then verify "
                f"`{resolved_executable} --version` and `{resolved_executable} --help`."
            )
        else:
            reason = normalized_output or "Claude Code version probe failed"
            failure_stage = "claude_version_probe_failed"
            remediation_hint = f"Run `{resolved_executable} --version` manually and fix the host environment."
        return ClaudeCodeSurfaceProbe(
            claude_cli_available=False,
            version=None,
            native_attach_available=False,
            process_bridge_available=False,
            settings_available=False,
            hooks_available=False,
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
        command_runner=runner,
        cwd=normalized_cwd,
        argv=[resolved_executable, "--help"],
        commands=commands,
    )
    help_lower = help_output.lower()
    project_root = normalized_cwd or Path.cwd().resolve(strict=False)
    settings_available = (project_root / ".claude" / "settings.json").exists()
    hooks_available = (project_root / ".claude" / "hooks" / "governed-pre-tool-use.py").exists()
    process_bridge_available = True
    structured_events_available = "--output-format" in help_lower and "json" in help_lower
    evidence_export_available = structured_events_available or "--json" in help_lower
    resume_available = "resume" in help_lower

    reason = "Claude Code CLI and managed settings/hooks are available"
    failure_stage = None
    remediation_hint = None
    if not settings_available or not hooks_available:
        missing = []
        if not settings_available:
            missing.append(".claude/settings.json")
        if not hooks_available:
            missing.append(".claude/hooks/governed-pre-tool-use.py")
        reason = "Claude Code CLI is available but managed settings/hooks are incomplete: " + ", ".join(missing)
        failure_stage = "claude_managed_settings_hooks_missing"
        remediation_hint = "Run governance baseline sync to materialize managed Claude Code settings/hooks."

    version = _safe_ascii(version_output).splitlines()[0].strip() if version_output.strip() else None
    return ClaudeCodeSurfaceProbe(
        claude_cli_available=True,
        version=version,
        native_attach_available=False,
        process_bridge_available=process_bridge_available,
        settings_available=settings_available,
        hooks_available=hooks_available,
        structured_events_available=structured_events_available,
        evidence_export_available=evidence_export_available,
        resume_available=resume_available,
        live_session_id=None,
        live_resume_id=None,
        reason=reason,
        probe_commands=commands,
        failure_stage=failure_stage,
        remediation_hint=remediation_hint,
    )


def summarize_claude_code_capability_readiness(
    probe: ClaudeCodeSurfaceProbe | None = None,
) -> ClaudeCodeCapabilityReadiness:
    active_probe = probe or probe_claude_code_surface()
    profile = build_claude_code_adapter_profile_from_probe(active_probe)
    tier = profile.adapter_tier
    if not active_probe.claude_cli_available or tier == "manual_handoff":
        status = "blocked"
    elif not active_probe.settings_available or not active_probe.hooks_available or profile.unsupported_capabilities:
        status = "degraded"
    else:
        status = "ready"
    return ClaudeCodeCapabilityReadiness(
        status=status,
        adapter_tier=tier,
        flow_kind=_flow_kind_from_tier(tier),
        settings_available=active_probe.settings_available,
        hooks_available=active_probe.hooks_available,
        unsupported_capabilities=list(profile.unsupported_capabilities),
        failure_stage=active_probe.failure_stage,
        remediation_hint=active_probe.remediation_hint,
    )


def build_claude_code_adapter_trial_result(
    *,
    repo_id: str,
    task_id: str,
    binding_id: str,
    process_bridge_available: bool,
    settings_available: bool,
    hooks_available: bool,
    structured_events_available: bool,
    evidence_export_available: bool,
    resume_available: bool,
    mode: str = "safe",
    run_id: str = "claude-code-trial-safe",
    probe: ClaudeCodeSurfaceProbe | None = None,
) -> ClaudeCodeAdapterTrialResult:
    active_probe = probe or ClaudeCodeSurfaceProbe(
        claude_cli_available=True,
        version=None,
        native_attach_available=False,
        process_bridge_available=process_bridge_available,
        settings_available=settings_available,
        hooks_available=hooks_available,
        structured_events_available=structured_events_available,
        evidence_export_available=evidence_export_available,
        resume_available=resume_available,
        live_session_id=None,
        live_resume_id=None,
        reason="declared trial flags",
        probe_commands=[],
    )
    profile = build_claude_code_adapter_profile_from_probe(active_probe) if probe else build_claude_code_adapter_profile(
        process_bridge_available=process_bridge_available,
        settings_available=settings_available,
        hooks_available=hooks_available,
        structured_events_available=structured_events_available,
        evidence_export_available=evidence_export_available,
        resume_available=resume_available,
    )
    normalized_task_id = _required_string(task_id, "task_id")
    normalized_run_id = _required_string(run_id, "run_id")
    digest = hashlib.sha1(f"{normalized_task_id}:{normalized_run_id}".encode("utf-8")).hexdigest()[:12]
    session_id = active_probe.live_session_id or f"claude-code-session-{digest}"
    resume_id = active_probe.live_resume_id or f"claude-code-resume-{digest}"
    continuation_id = f"{normalized_task_id}:{normalized_run_id}"
    base_ref = f"artifacts/{normalized_task_id}/{normalized_run_id}"
    return ClaudeCodeAdapterTrialResult(
        mode=_required_string(mode, "mode"),
        repo_id=_required_string(repo_id, "repo_id"),
        task_id=normalized_task_id,
        binding_id=_required_string(binding_id, "binding_id"),
        adapter_id=profile.adapter_id,
        adapter_tier=profile.adapter_tier,
        unsupported_capabilities=list(profile.unsupported_capabilities),
        unsupported_capability_behavior=profile.unsupported_capability_behavior,
        flow_kind=_flow_kind_from_tier(profile.adapter_tier),
        session_id=session_id,
        resume_id=resume_id,
        continuation_id=continuation_id,
        probe_source=profile.probe_source,
        evidence_refs=[
            f"{base_ref}/evidence/claude-code-session.json",
            f"{base_ref}/evidence/claude-code-probe.json",
        ],
        verification_refs=[
            f"{base_ref}/verification-output/runtime.txt",
            f"{base_ref}/verification-output/contract.txt",
        ],
        hook_evidence_refs=[f"{base_ref}/evidence/claude-code-hooks.json"],
        handoff_ref=f"{base_ref}/handoff/package.json",
        replay_ref=f"{base_ref}/replay/adapter-flow.json",
    )


def claude_code_probe_to_dict(probe: ClaudeCodeSurfaceProbe) -> dict:
    payload = asdict(probe)
    payload["probe_commands"] = [asdict(item) for item in probe.probe_commands]
    return payload


def claude_code_capability_readiness_to_dict(readiness: ClaudeCodeCapabilityReadiness) -> dict:
    return asdict(readiness)


def claude_code_adapter_trial_to_dict(result: ClaudeCodeAdapterTrialResult) -> dict:
    return asdict(result)


def _default_probe_runner(argv: list[str], cwd: Path | None) -> tuple[int, str, str]:
    try:
        timeout_seconds = parse_optional_positive_timeout(
            os.environ.get(_CLAUDE_PROBE_TIMEOUT_SECONDS_ENV_KEY),
            _CLAUDE_PROBE_TIMEOUT_SECONDS_ENV_KEY,
        )
        if timeout_seconds is None:
            timeout_seconds = _CLAUDE_PROBE_TIMEOUT_SECONDS_DEFAULT
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
    commands: list[ClaudeCodeProbeCommand],
) -> tuple[int, str]:
    exit_code, stdout, stderr = command_runner(argv, cwd)
    output = _safe_ascii("\n".join(part for part in [stdout, stderr] if part).strip())
    commands.append(
        ClaudeCodeProbeCommand(
            cmd=" ".join(argv),
            exit_code=exit_code,
            key_output=_truncate_output(output),
            timestamp=datetime.now(UTC).isoformat(),
        )
    )
    return exit_code, output


def _resolve_claude_executable(explicit: str | None) -> str:
    candidate = _optional_non_empty_string(explicit)
    if candidate is not None:
        return candidate
    for env_key in _CLAUDE_EXECUTABLE_ENV_KEYS:
        env_value = _optional_non_empty_string(os.environ.get(env_key))
        if env_value is not None:
            return env_value
    return _DEFAULT_CLAUDE_EXECUTABLE


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


def _unsupported_capabilities(
    *,
    native_attach_available: bool,
    process_bridge_available: bool,
    settings_available: bool,
    hooks_available: bool,
    structured_events_available: bool,
    evidence_export_available: bool,
    resume_available: bool,
) -> list[str]:
    unsupported: list[str] = []
    if not native_attach_available:
        unsupported.append("native_attach")
    if not process_bridge_available:
        unsupported.append("process_bridge")
    if not settings_available:
        unsupported.append("managed_settings")
    if not hooks_available:
        unsupported.append("managed_hooks")
    if not structured_events_available:
        unsupported.append("structured_events")
    if not evidence_export_available:
        unsupported.append("structured_evidence_export")
    if not resume_available:
        unsupported.append("resume_id")
    return unsupported


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


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _optional_non_empty_string(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized
