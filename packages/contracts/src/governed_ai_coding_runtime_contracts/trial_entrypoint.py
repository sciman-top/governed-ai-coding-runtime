"""Scripted read-only trial entrypoint primitives."""

from dataclasses import dataclass
from pathlib import Path

from governed_ai_coding_runtime_contracts.codex_adapter import (
    CodexSurfaceProbe,
    build_codex_adapter_profile,
    build_codex_adapter_profile_from_probe,
    probe_codex_surface,
)
from governed_ai_coding_runtime_contracts.evidence import EvidenceTimeline, TaskOutput, build_task_output
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.task_intake import TaskIntake
from governed_ai_coding_runtime_contracts.tool_runner import (
    ReadOnlySessionSummary,
    ToolRequest,
    run_readonly_session,
)


@dataclass(frozen=True, slots=True)
class ScriptedTrialResult:
    task: TaskIntake
    adapter: dict
    session: ReadOnlySessionSummary
    output: TaskOutput


def codex_cli_adapter_declaration(
    *,
    probe_live: bool = False,
    probe: CodexSurfaceProbe | None = None,
) -> dict:
    if probe is not None:
        profile = build_codex_adapter_profile_from_probe(probe)
    elif probe_live:
        profile = build_codex_adapter_profile_from_probe(probe_codex_surface())
    else:
        profile = build_codex_adapter_profile(
            native_attach_available=True,
            process_bridge_available=True,
            structured_events_available=True,
            evidence_export_available=True,
            resume_available=True,
            probe_source="declared_defaults",
            posture_reason="declared default capability posture for scripted readonly trial",
        )

    invocation_mode = _invocation_mode_from_tier(profile.adapter_tier)
    return {
        "adapter_id": "codex.cli.compatible",
        "display_name": "Codex CLI/App Compatible",
        "product_family": "codex",
        "lifecycle_status": "experimental",
        "rollout_posture": {
            "current_mode": "observe",
            "target_mode": "advisory",
        },
        "invocation_mode": invocation_mode,
        "auth_ownership": "user_owned_upstream_auth",
        "workspace_control": "read_only",
        "event_visibility": profile.tool_visibility,
        "mutation_model": "read_only",
        "continuation_model": profile.resume_behavior,
        "evidence_model": profile.evidence_export_capability,
        "adapter_tier": profile.adapter_tier,
        "probe_source": profile.probe_source,
        "posture_reason": profile.posture_reason,
        "unsupported_capabilities": list(profile.unsupported_capabilities),
        "supported_governance_modes": ["observe_only", "advisory"],
        "minimum_required_runtime_controls": [
            "task_intake",
            "repo_profile_resolution",
            "readonly_tool_policy",
            "evidence_timeline",
        ],
        "unsupported_capability_behavior": profile.unsupported_capability_behavior,
        "compatibility_notes": "Upstream Codex authentication remains user-owned and outside runtime credential control.",
        "compatibility_signals": [
            {
                "capability": "interactive_control_plane",
                "status": "supported" if profile.adapter_tier == "native_attach" else "partial_support",
                "degrade_to": "advisory",
                "reason": profile.posture_reason,
            }
        ],
    }


def run_scripted_readonly_trial(
    *,
    goal: str,
    scope: str,
    acceptance: list[str],
    repo_profile_path: str | Path,
    target_path: str,
    budgets: dict[str, int],
    probe_live: bool = False,
    probe: CodexSurfaceProbe | None = None,
) -> ScriptedTrialResult:
    profile = load_repo_profile(repo_profile_path)
    adapter = codex_cli_adapter_declaration(probe_live=probe_live, probe=probe)
    task = TaskIntake(
        goal=goal,
        scope=scope,
        acceptance=acceptance,
        repo=profile.repo_id,
        budgets=budgets,
    )
    request = ToolRequest(
        tool_name="shell",
        side_effect_class="filesystem_read",
        target_path=target_path,
    )
    session = run_readonly_session([request], profile)

    timeline = EvidenceTimeline()
    timeline.append(profile.repo_id, "task_created", {"goal": task.goal, "scope": task.scope})
    timeline.append(
        profile.repo_id,
        "decision",
        {
            "adapter": adapter["adapter_id"],
            "mode": adapter["invocation_mode"],
            "adapter_tier": adapter["adapter_tier"],
            "probe_source": adapter["probe_source"],
        },
    )
    timeline.append(profile.repo_id, "tool_call", {"tool_name": request.tool_name, "status": "accepted"})
    timeline.append(
        profile.repo_id,
        "output",
        {"summary": f"read-only trial accepted {session.accepted_count} tool request"},
    )

    return ScriptedTrialResult(
        task=task,
        adapter=adapter,
        session=session,
        output=build_task_output(profile.repo_id, timeline),
    )


def _invocation_mode_from_tier(adapter_tier: str) -> str:
    if adapter_tier == "native_attach":
        return "live_attach"
    if adapter_tier == "process_bridge":
        return "process_bridge"
    return "manual_handoff"
