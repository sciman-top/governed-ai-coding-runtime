"""Scripted read-only trial entrypoint primitives."""

from dataclasses import dataclass
from pathlib import Path

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


def codex_cli_adapter_declaration() -> dict:
    return {
        "adapter_id": "codex.cli.compatible",
        "display_name": "Codex CLI/App Compatible",
        "product_family": "codex",
        "lifecycle_status": "experimental",
        "invocation_mode": "manual_handoff",
        "auth_ownership": "user_owned_upstream_auth",
        "workspace_control": "read_only",
        "event_visibility": "manual_summary",
        "mutation_model": "read_only",
        "continuation_model": "manual",
        "evidence_model": "manual_summary",
        "supported_governance_modes": ["observe_only", "advisory"],
        "minimum_required_runtime_controls": [
            "task_intake",
            "repo_profile_resolution",
            "readonly_tool_policy",
            "evidence_timeline",
        ],
        "unsupported_capability_behavior": "degrade_to_manual_handoff",
        "compatibility_notes": "Upstream Codex authentication remains user-owned and outside runtime credential control.",
    }


def run_scripted_readonly_trial(
    *,
    goal: str,
    scope: str,
    acceptance: list[str],
    repo_profile_path: str | Path,
    target_path: str,
    budgets: dict[str, int],
) -> ScriptedTrialResult:
    profile = load_repo_profile(repo_profile_path)
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
    timeline.append(profile.repo_id, "decision", {"adapter": "codex.cli.compatible", "mode": "manual_handoff"})
    timeline.append(profile.repo_id, "tool_call", {"tool_name": request.tool_name, "status": "accepted"})
    timeline.append(
        profile.repo_id,
        "output",
        {"summary": f"read-only trial accepted {session.accepted_count} tool request"},
    )

    return ScriptedTrialResult(
        task=task,
        adapter=codex_cli_adapter_declaration(),
        session=session,
        output=build_task_output(profile.repo_id, timeline),
    )
