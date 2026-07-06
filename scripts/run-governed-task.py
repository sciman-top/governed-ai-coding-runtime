from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.artifact_store import LocalArtifactStore
from governed_ai_coding_runtime_contracts.delivery_handoff import build_handoff_package
from governed_ai_coding_runtime_contracts.evidence import build_evidence_bundle
from governed_ai_coding_runtime_contracts.codex_adapter import (
    codex_capability_readiness_to_dict,
    summarize_codex_capability_readiness,
)
from governed_ai_coding_runtime_contracts.execution_runtime import ExecutionRuntime, WorkerExecutionResult
from governed_ai_coding_runtime_contracts.file_guard import atomic_write_text, validate_file_component
from governed_ai_coding_runtime_contracts.learning_efficiency_metrics import build_learning_efficiency_metrics
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.replay import build_replay_reference
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeStatusStore, runtime_snapshot_to_dict
from governed_ai_coding_runtime_contracts.runtime_roots import ensure_runtime_roots, resolve_runtime_roots
from governed_ai_coding_runtime_contracts.subprocess_guard import run_governed_gate_command
from governed_ai_coding_runtime_contracts.task_intake import TaskIntake, apply_interaction_profile_defaults
from governed_ai_coding_runtime_contracts.task_store import FileTaskStore, TaskRecord, TaskRunRecord
from governed_ai_coding_runtime_contracts.workflow_effect_metrics import build_workflow_effect_metrics
from governed_ai_coding_runtime_contracts.workflow_selection import select_workflow_mode
from governed_ai_coding_runtime_contracts.verification_runner import (
    build_repo_profile_verification_plan,
    run_verification_plan,
    verification_overall_outcome,
)
from governed_ai_coding_runtime_contracts.worker import SynchronousLocalWorker
from governed_ai_coding_runtime_contracts.workflow import fail_task, transition_task


_RUNTIME_ROOTS = ensure_runtime_roots(resolve_runtime_roots(repo_root=ROOT))
RUNTIME_ROOT = Path(_RUNTIME_ROOTS.runtime_root)
TASK_ROOT = Path(_RUNTIME_ROOTS.tasks_root)
ARTIFACT_ROOT = Path(_RUNTIME_ROOTS.artifacts_root)
REPLAY_ROOT = Path(_RUNTIME_ROOTS.replay_root)
WORKSPACES_ROOT = Path(_RUNTIME_ROOTS.workspaces_root)
VERIFICATION_MODE_CHOICES = ["quick", "full", "l1", "l2", "l3"]
RETIRED_RUN_GOVERNED_TASK_COMMANDS = {
    "verify-attachment": "Attached target-repo verification was removed with the attachment bridge.",
    "govern-attachment-write": "Attached target-repo write governance was removed with the attachment bridge.",
    "decide-attachment-write": "Attached target-repo approval flow was removed with the attachment bridge.",
    "execute-attachment-write": "Attached target-repo write execution was removed with the attachment bridge.",
}


def main() -> int:
    retired_result = _dispatch_retired_command(sys.argv[1:])
    if retired_result is not None:
        return retired_result

    parser = argparse.ArgumentParser(description="CLI-first governed runtime operator surface")
    parser.add_argument("--runtime-root")
    parser.add_argument("--compat-runtime-root", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a planned governed task")
    create_parser.add_argument("--task-id")
    create_parser.add_argument("--goal", required=True)
    create_parser.add_argument("--scope", default="runtime smoke")
    create_parser.add_argument("--repo", default="governed-ai-coding-runtime")

    run_parser = subparsers.add_parser("run", help="Create or run one governed task end-to-end")
    run_parser.add_argument("--task-id")
    run_parser.add_argument("--goal", default="Run governed runtime smoke task")
    run_parser.add_argument("--scope", default="runtime smoke")
    run_parser.add_argument("--repo", default="governed-ai-coding-runtime")
    run_parser.add_argument(
        "--profile",
        default=str(ROOT / "schemas" / "examples" / "repo-profile" / "governed-ai-coding-runtime.example.json"),
    )
    run_parser.add_argument("--mode", choices=VERIFICATION_MODE_CHOICES, default="full")
    run_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print runtime status snapshot")
    status_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    _configure_runtime_roots(runtime_root=args.runtime_root, compat_runtime_root=bool(args.compat_runtime_root))
    if args.command == "create":
        payload = create_task(task_id=args.task_id, goal=args.goal, scope=args.scope, repo=args.repo)
    elif args.command == "run":
        payload = run_task(task_id=args.task_id, goal=args.goal, scope=args.scope, repo=args.repo, profile_path=args.profile, mode=args.mode)
    else:
        payload = snapshot_payload()

    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_payload(payload))
    return 0


def _dispatch_retired_command(argv: list[str]) -> int | None:
    command, json_output = _extract_requested_command(argv)
    if command not in RETIRED_RUN_GOVERNED_TASK_COMMANDS:
        return None
    payload = {
        "status": "retired_command",
        "command": command,
        "reason": RETIRED_RUN_GOVERNED_TASK_COMMANDS[command],
        "remediation_hint": "Use create/run/status for repo-local runtime work. Attachment and target-repo bridge flows were removed.",
    }
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_payload(payload))
    return 1


def _extract_requested_command(argv: list[str]) -> tuple[str | None, bool]:
    json_output = False
    skip_next = False
    for token in argv:
        if skip_next:
            skip_next = False
            continue
        if token == "--json":
            json_output = True
            continue
        if token == "--runtime-root":
            skip_next = True
            continue
        if token == "--compat-runtime-root":
            continue
        if token.startswith("-"):
            continue
        return token, json_output
    return None, json_output


def create_task(
    *,
    task_id: str | None,
    goal: str,
    scope: str,
    repo: str,
    interaction_defaults: dict[str, object] | None = None,
    interaction_budget_overrides: dict[str, int] | None = None,
) -> dict:
    store = FileTaskStore(TASK_ROOT)
    identifier = task_id or f"task-{uuid4().hex[:8]}"
    record = TaskRecord(
        task_id=identifier,
        task=TaskIntake(
            goal=goal,
            scope=scope,
            acceptance=["task executes through the governed runtime"],
            repo=repo,
            budgets={"max_steps": 10, "max_minutes": 30},
            interaction_defaults=interaction_defaults,
            interaction_budget_overrides=interaction_budget_overrides,
        ),
        current_state="planned",
    )
    store.save(record)
    return {"task_id": identifier, "state": "planned"}


def run_task(*, task_id: str | None, goal: str, scope: str, repo: str, profile_path: str, mode: str) -> dict:
    store = FileTaskStore(TASK_ROOT)
    profile = load_repo_profile(profile_path)
    if task_id:
        identifier = task_id
        try:
            store.load(identifier)
        except FileNotFoundError:
            create_task(
                task_id=identifier,
                goal=goal,
                scope=scope,
                repo=repo,
                interaction_defaults=_interaction_defaults_from_profile(profile),
            )
    else:
        identifier = create_task(
            task_id=None,
            goal=goal,
            scope=scope,
            repo=repo,
            interaction_defaults=_interaction_defaults_from_profile(profile),
        )["task_id"]
    _apply_profile_interaction_defaults_to_record(store, identifier, profile)
    workflow_decision = _select_workflow_decision(profile=profile, goal=goal, scope=scope, mode=mode)
    runtime = ExecutionRuntime(store=store, runtime_workspaces_root=WORKSPACES_ROOT.as_posix())
    artifact_store = LocalArtifactStore(ARTIFACT_ROOT)

    def handler(context) -> WorkerExecutionResult:
        execution_artifact = artifact_store.write_text(
            task_id=context.record.task_id,
            run_id=context.run.run_id,
            kind="execution-output",
            label="worker-summary",
            content=f"goal={context.record.task.goal}\nworkspace={context.workspace.workspace_root}\n",
        )
        return WorkerExecutionResult(
            outcome="completed",
            summary=f"executed {context.run.run_id}",
            artifact_refs=[execution_artifact.relative_path],
            rollback_ref="docs/runbooks/control-rollback.md",
        )

    record = runtime.execute_task(identifier, profile, SynchronousLocalWorker(worker_id="local-worker", handler=handler))
    run = _active_run(record)
    verification_artifact = run_verification_plan(
        build_repo_profile_verification_plan(
            mode,
            profile_raw=profile.raw,
            task_id=record.task_id,
            run_id=run.run_id,
        ),
        artifact_store=artifact_store,
        execute_gate=_execute_gate,
    )

    replay_ref = ""
    record = store.load(record.task_id)
    if verification_overall_outcome(verification_artifact) != "pass":
        replay = build_replay_reference(
            task_id=record.task_id,
            run_id=run.run_id,
            failure_reason="verification failed",
            artifact_refs=run.artifact_refs,
            verification_artifact_refs=list(verification_artifact.result_artifact_refs.values()),
        )
        replay_ref = _write_replay_case(replay)
        record = fail_task(
            record,
            actor_type="system",
            actor_id="verification-runner",
            reason="verification failed",
        )
    else:
        record = transition_task(
            record,
            "delivered",
            actor_type="system",
            actor_id="verification-runner",
            reason="verification passed",
            store=store,
        )
    store.save(record)

    evidence_bundle = build_evidence_bundle(
        task_id=record.task_id,
        repo_id=profile.repo_id,
        goal=record.task.goal,
        acceptance_criteria=record.task.acceptance,
        verification_artifact=verification_artifact,
        rollback_ref=record.rollback_ref or "docs/runbooks/control-rollback.md",
        final_status="completed" if record.current_state == "delivered" else "failed",
        final_summary="governed runtime task completed" if record.current_state == "delivered" else "governed runtime task failed",
        artifact_refs=run.artifact_refs + list(verification_artifact.result_artifact_refs.values()),
        replay_case_ref=replay_ref or None,
        failure_signature="verification failed" if replay_ref else None,
        interaction_trace=_interaction_trace_for_record(record, profile, workflow_decision=workflow_decision),
    )
    evidence_artifact = artifact_store.write_json(
        task_id=record.task_id,
        run_id=run.run_id,
        kind="evidence",
        label="bundle",
        payload=evidence_bundle,
    )
    learning_metrics = build_learning_efficiency_metrics(
        task_id=record.task_id,
        run_id=run.run_id,
        metrics_source_ref=evidence_artifact.relative_path,
        evidence_bundle=evidence_bundle,
    )
    learning_metrics_artifact = artifact_store.write_json(
        task_id=record.task_id,
        run_id=run.run_id,
        kind="metrics",
        label="learning-efficiency",
        payload=learning_metrics.to_dict(),
    )
    handoff = build_handoff_package(
        task_id=record.task_id,
        changed_files=["scripts/run-governed-task.py"],
        verification_artifact=verification_artifact,
        risk_notes=verification_artifact.risky_artifact_refs,
        replay_references=[replay_ref] if replay_ref else ["not-needed"],
    )
    handoff_artifact = artifact_store.write_json(
        task_id=record.task_id,
        run_id=run.run_id,
        kind="handoff",
        label="package",
        payload={
            "task_id": handoff.task_id,
            "validation_status": handoff.validation_status,
            "risk_notes": handoff.risk_notes,
            "replay_references": handoff.replay_references,
        },
    )

    refreshed = store.load(record.task_id)
    workflow_metrics = build_workflow_effect_metrics(
        workflow_mode_selected=workflow_decision["workflow_mode_selected"],
        workflow_mode_source=workflow_decision["workflow_mode_source"],
        workflow_degrade_reason=workflow_decision["workflow_degrade_reason"],
        recommendation_improved=workflow_decision["workflow_mode_selected"] != "direct_fix",
        mode_level_comparison_reason=workflow_decision["workflow_mode_reason"],
        manual_intervention_count=1 if workflow_decision["workflow_mode_selected"] == "spec_plus_review" else 0,
        problem_run_rate=0.0 if refreshed.current_state == "delivered" else 1.0,
    )
    refreshed.run_history = [
        _merge_run_refs(
            item,
            evidence_ref=evidence_artifact.relative_path,
            verification_refs=list(verification_artifact.result_artifact_refs.values()),
            extra_artifact_refs=run.artifact_refs + [handoff_artifact.relative_path, learning_metrics_artifact.relative_path],
        )
        if item.run_id == run.run_id
        else item
        for item in refreshed.run_history
    ]
    store.save(refreshed)
    return snapshot_payload(task_id=refreshed.task_id, workflow_metrics=workflow_metrics, workflow_decision=workflow_decision)


def snapshot_payload(
    *,
    task_id: str | None = None,
    workflow_metrics: dict | None = None,
    workflow_decision: dict | None = None,
) -> dict:
    status_payload = runtime_snapshot_to_dict(
        RuntimeStatusStore(
            TASK_ROOT,
            ROOT,
            runtime_root=RUNTIME_ROOT,
        ).snapshot()
    )
    tasks = status_payload.get("tasks", [])
    maintenance = status_payload.get("maintenance", {})
    workflow_decision = workflow_decision if isinstance(workflow_decision, dict) else {}
    payload = {
        "runtime_roots": {
            "runtime_root": RUNTIME_ROOT.as_posix(),
            "tasks_root": TASK_ROOT.as_posix(),
            "artifacts_root": ARTIFACT_ROOT.as_posix(),
            "replay_root": REPLAY_ROOT.as_posix(),
            "workspaces_root": WORKSPACES_ROOT.as_posix(),
            "compatibility_mode": _RUNTIME_ROOTS.compatibility_mode,
        },
        "total_tasks": int(status_payload.get("total_tasks", 0)),
        "maintenance": maintenance,
        "tasks": [
            item
            for item in tasks
            if isinstance(item, dict) and (task_id is None or item.get("task_id") == task_id)
        ],
        "workflow_mode_selected": workflow_decision.get("workflow_mode_selected"),
        "workflow_mode_source": workflow_decision.get("workflow_mode_source"),
        "workflow_mode_reason": workflow_decision.get("workflow_mode_reason"),
        "workflow_degrade_reason": workflow_decision.get("workflow_degrade_reason"),
        "workflow_required_artifacts": workflow_decision.get("workflow_required_artifacts", []),
        "workflow_metrics": workflow_metrics if isinstance(workflow_metrics, dict) else None,
    }
    try:
        payload["codex_capability"] = codex_capability_readiness_to_dict(
            summarize_codex_capability_readiness()
        )
    except Exception as exc:  # pragma: no cover - defensive fallback for operator status surface
        payload["codex_capability"] = {
            "status": "unknown",
            "reason": str(exc),
        }
    return payload


def _interaction_defaults_from_profile(profile: object) -> dict[str, object] | None:
    interaction_profile = getattr(profile, "interaction_profile", None)
    if not isinstance(interaction_profile, dict) or not interaction_profile:
        return None
    defaults: dict[str, object] = {}
    for field_name in (
        "default_mode",
        "default_checklist_kind",
        "summary_template",
        "handoff_teaching_notes",
        "term_explain_style",
    ):
        if field_name in interaction_profile:
            defaults[field_name] = interaction_profile[field_name]
    return defaults or None


def _apply_profile_interaction_defaults_to_record(store: FileTaskStore, task_id: str, profile: object) -> None:
    record = store.load(task_id)
    updated_task = apply_interaction_profile_defaults(
        record.task,
        getattr(profile, "interaction_profile", None),
    )
    if updated_task is record.task:
        return
    record.task = updated_task
    store.save(record)


def _select_workflow_decision(*, profile: object, goal: str, scope: str, mode: str) -> dict:
    workflow_policy = getattr(profile, "workflow_governance_policy", {}) if profile is not None else {}
    allowed_modes = [
        "direct_fix",
        "spec_first",
        "spec_plus_review",
        "worktree_isolated_execution",
        "parallel_subagent_assist",
        "maintenance_automation",
    ]
    if isinstance(workflow_policy, dict):
        configured = workflow_policy.get("allowed_workflow_modes")
        if isinstance(configured, list) and configured:
            allowed_modes = [item for item in configured if isinstance(item, str) and item in allowed_modes]
    selected = select_workflow_mode(
        risk_level="high" if mode == "full" else "low",
        multi_file=("multi" in scope.lower()) or ("workflow" in goal.lower()),
        unclear_requirements=("?" in goal) or ("spec" not in goal.lower()),
        needs_review=mode == "full",
        supports_worktrees="worktree_isolated_execution" in allowed_modes,
        supports_subagents="parallel_subagent_assist" in allowed_modes,
        supports_background_automation="maintenance_automation" in allowed_modes,
        repeated_stable_task=scope.lower().startswith("runtime"),
    )
    return {
        "workflow_mode_selected": selected.workflow_mode_selected,
        "workflow_mode_source": selected.workflow_mode_source,
        "workflow_mode_reason": selected.workflow_mode_reason,
        "workflow_degrade_reason": selected.workflow_degrade_reason,
        "workflow_required_artifacts": selected.workflow_required_artifacts,
    }


def _interaction_trace_for_record(record: TaskRecord, profile: object, *, workflow_decision: dict | None = None) -> dict | None:
    interaction_defaults = record.task.interaction_defaults or _interaction_defaults_from_profile(profile)
    if not interaction_defaults:
        return None
    mode = interaction_defaults.get("default_mode", "guided")
    interaction_profile = getattr(profile, "interaction_profile", {})
    compression_mode = "none"
    if isinstance(interaction_profile, dict):
        compression_mode = interaction_profile.get("compaction_preference", "none")
    return {
        "signals": [],
        "applied_policies": [
            {
                "policy_id": f"{record.task_id}:repo-profile-interaction-defaults",
                "mode": str(mode),
                "posture": "aligned",
                "clarification_mode": "none",
                "compression_mode": str(compression_mode),
                "stop_or_escalate": "continue",
                "rationale_signal_ids": [],
            }
        ],
        "task_restatements": [],
        "clarification_rounds": [],
        "observation_checklists": [],
        "terms_explained": [],
        "compression_actions": [],
        "budget_snapshots": [],
        "alignment_outcome": "repo profile interaction defaults applied",
        "stop_or_degrade_reason": "none",
    }
    if isinstance(workflow_decision, dict) and workflow_decision:
        trace["workflow_mode_selected"] = workflow_decision.get("workflow_mode_selected")
        trace["workflow_mode_source"] = workflow_decision.get("workflow_mode_source")
        trace["workflow_mode_reason"] = workflow_decision.get("workflow_mode_reason")
        trace["workflow_degrade_reason"] = workflow_decision.get("workflow_degrade_reason")
        trace["workflow_required_artifacts"] = workflow_decision.get("workflow_required_artifacts", [])
        trace["workflow_metrics"] = build_workflow_effect_metrics(
            workflow_mode_selected=str(workflow_decision.get("workflow_mode_selected") or "direct_fix"),
            workflow_mode_source=str(workflow_decision.get("workflow_mode_source") or "deterministic_policy"),
            workflow_degrade_reason=str(workflow_decision.get("workflow_degrade_reason") or ""),
            recommendation_improved=str(workflow_decision.get("workflow_mode_selected") or "") != "direct_fix",
            mode_level_comparison_reason=str(workflow_decision.get("workflow_mode_reason") or ""),
            manual_intervention_count=1 if workflow_decision.get("workflow_mode_selected") == "spec_plus_review" else 0,
            problem_run_rate=0.0,
        )
    return trace


def render_payload(payload: dict) -> str:
    if payload.get("status") == "retired_command":
        lines = [f"Status: {payload['status']}", f"Reason: {payload.get('reason', 'retired')}"]
        remediation = payload.get("remediation_hint", "")
        if remediation:
            lines.append(f"Remediation: {remediation}")
        return "\n".join(lines)
    codex_capability = payload.get("codex_capability") if isinstance(payload, dict) else None
    codex_line = None
    if isinstance(codex_capability, dict):
        codex_status = codex_capability.get("status", "unknown")
        codex_tier = codex_capability.get("adapter_tier", "unknown")
        codex_line = f"Codex capability: {codex_status} ({codex_tier})"
    if not payload["tasks"]:
        lines = [
            f"Total tasks: {payload['total_tasks']}",
            f"Maintenance stage: {payload['maintenance']['stage']}",
        ]
        if codex_line is not None:
            lines.append(codex_line)
        lines.append("No governed tasks recorded.")
        return "\n".join(lines)
    lines = [
        f"Total tasks: {payload['total_tasks']}",
        f"Maintenance stage: {payload['maintenance']['stage']}",
        f"Maintenance policy: {payload['maintenance']['compatibility_policy_ref']}",
    ]
    if codex_line is not None:
        lines.append(codex_line)
    for task in payload["tasks"]:
        lines.append(f"- {task['task_id']}: {task['current_state']} ({task['goal']})")
        if task["active_run_id"]:
            lines.append(f"  run={task['active_run_id']} workspace={task['workspace_root']}")
        if task["verification_refs"]:
            lines.append(f"  verification={', '.join(task['verification_refs'])}")
        if task["evidence_refs"]:
            lines.append(f"  evidence={', '.join(task['evidence_refs'])}")
    return "\n".join(lines)


def _execute_gate(gate) -> tuple[int, str]:
    return _execute_gate_at_root(gate.command, cwd=ROOT)


def _execute_gate_at_root(command: str, *, cwd: Path) -> tuple[int, str]:
    return run_governed_gate_command(command=command, cwd=cwd)


def _active_run(record: TaskRecord) -> TaskRunRecord:
    for item in record.run_history:
        if item.run_id == record.active_run_id:
            return item
    msg = "active run missing from task record"
    raise ValueError(msg)


def _merge_run_refs(
    run: TaskRunRecord,
    *,
    evidence_ref: str,
    verification_refs: list[str],
    extra_artifact_refs: list[str],
) -> TaskRunRecord:
    artifact_refs = list(dict.fromkeys(run.artifact_refs + extra_artifact_refs))
    return TaskRunRecord(
        run_id=run.run_id,
        attempt_id=run.attempt_id,
        worker_id=run.worker_id,
        status=run.status,
        workspace_root=run.workspace_root,
        started_at=run.started_at,
        finished_at=run.finished_at,
        summary=run.summary,
        evidence_refs=list(dict.fromkeys(run.evidence_refs + [evidence_ref])),
        approval_ids=run.approval_ids,
        artifact_refs=artifact_refs,
        verification_refs=list(dict.fromkeys(run.verification_refs + verification_refs)),
        rollback_ref=run.rollback_ref,
        failure_reason=run.failure_reason,
    )


def _write_replay_case(reference) -> str:
    REPLAY_ROOT.mkdir(parents=True, exist_ok=True)
    task_id = validate_file_component(reference.task_id, "task_id")
    run_id = validate_file_component(reference.run_id, "run_id")
    path = REPLAY_ROOT / f"{task_id}-{run_id}.json"
    atomic_write_text(
        path,
        json.dumps(
            {
                "task_id": reference.task_id,
                "run_id": reference.run_id,
                "failure_signature": {
                    "signature_id": reference.failure_signature.signature_id,
                    "failure_reason": reference.failure_signature.failure_reason,
                },
                "artifact_refs": reference.artifact_refs,
                "verification_artifact_refs": reference.verification_artifact_refs,
                "created_at": reference.created_at,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return _runtime_ref_for_path(path)


def _runtime_ref_for_path(path: Path) -> str:
    resolved = Path(path).resolve(strict=False)
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.relative_to(RUNTIME_ROOT).as_posix()


def _configure_runtime_roots(*, runtime_root: str | None, compat_runtime_root: bool) -> None:
    global _RUNTIME_ROOTS
    global RUNTIME_ROOT
    global TASK_ROOT
    global ARTIFACT_ROOT
    global REPLAY_ROOT
    global WORKSPACES_ROOT

    compatibility_mode = True if compat_runtime_root else None
    _RUNTIME_ROOTS = ensure_runtime_roots(
        resolve_runtime_roots(
            repo_root=ROOT,
            runtime_root=runtime_root,
            compatibility_mode=compatibility_mode,
        )
    )
    RUNTIME_ROOT = Path(_RUNTIME_ROOTS.runtime_root)
    TASK_ROOT = Path(_RUNTIME_ROOTS.tasks_root)
    ARTIFACT_ROOT = Path(_RUNTIME_ROOTS.artifacts_root)
    REPLAY_ROOT = Path(_RUNTIME_ROOTS.replay_root)
    WORKSPACES_ROOT = Path(_RUNTIME_ROOTS.workspaces_root)


if __name__ == "__main__":
    raise SystemExit(main())
