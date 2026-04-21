from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
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
from governed_ai_coding_runtime_contracts.repo_attachment import validate_light_pack
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.replay import build_replay_reference
from governed_ai_coding_runtime_contracts.runtime_roots import ensure_runtime_roots, resolve_runtime_roots
from governed_ai_coding_runtime_contracts.task_intake import TaskIntake, apply_interaction_profile_defaults
from governed_ai_coding_runtime_contracts.task_store import FileTaskStore, TaskRecord, TaskRunRecord
from governed_ai_coding_runtime_contracts.verification_runner import (
    build_verification_plan,
    run_verification_plan,
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


def main() -> int:
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
    run_parser.add_argument("--profile", default=str(ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"))
    run_parser.add_argument("--mode", choices=VERIFICATION_MODE_CHOICES, default="full")
    run_parser.add_argument("--json", action="store_true")

    verify_attachment_parser = subparsers.add_parser(
        "verify-attachment",
        help="Execute declared verification gates for an attached target repo",
        description="Execute declared verification gates for an attached target repo.",
    )
    verify_attachment_parser.add_argument("--attachment-root", required=True)
    verify_attachment_parser.add_argument("--attachment-runtime-state-root", required=True)
    verify_attachment_parser.add_argument("--mode", choices=VERIFICATION_MODE_CHOICES, default="quick")
    verify_attachment_parser.add_argument("--task-id", required=True)
    verify_attachment_parser.add_argument("--run-id", required=True)
    verify_attachment_parser.add_argument("--json", action="store_true")

    govern_attachment_write_parser = subparsers.add_parser(
        "govern-attachment-write",
        help="Evaluate attached repo write governance.",
        description="Evaluate attached repo write governance.",
    )
    govern_attachment_write_parser.add_argument("--attachment-root", required=True)
    govern_attachment_write_parser.add_argument("--attachment-runtime-state-root", required=True)
    govern_attachment_write_parser.add_argument("--task-id", required=True)
    govern_attachment_write_parser.add_argument("--tool-name", default="apply_patch")
    govern_attachment_write_parser.add_argument("--tool-command")
    govern_attachment_write_parser.add_argument("--target-path", required=True)
    govern_attachment_write_parser.add_argument("--tier", choices=["low", "medium", "high"], default="medium")
    govern_attachment_write_parser.add_argument("--rollback-reference", default="")
    govern_attachment_write_parser.add_argument("--adapter-id", default="codex-cli")
    govern_attachment_write_parser.add_argument("--session-id")
    govern_attachment_write_parser.add_argument("--resume-id")
    govern_attachment_write_parser.add_argument("--continuation-id")
    govern_attachment_write_parser.add_argument("--json", action="store_true")

    decide_attachment_write_parser = subparsers.add_parser(
        "decide-attachment-write",
        help="Approve or reject an attached write request.",
        description="Approve or reject an attached write request.",
    )
    decide_attachment_write_parser.add_argument("--attachment-runtime-state-root", required=True)
    decide_attachment_write_parser.add_argument("--approval-id", required=True)
    decide_attachment_write_parser.add_argument("--decision", choices=["approve", "reject"], required=True)
    decide_attachment_write_parser.add_argument("--decided-by", default="operator")
    decide_attachment_write_parser.add_argument("--task-id", default="attachment-write")
    decide_attachment_write_parser.add_argument("--adapter-id", default="codex-cli")
    decide_attachment_write_parser.add_argument("--session-id")
    decide_attachment_write_parser.add_argument("--resume-id")
    decide_attachment_write_parser.add_argument("--continuation-id")
    decide_attachment_write_parser.add_argument("--json", action="store_true")

    execute_attachment_write_parser = subparsers.add_parser(
        "execute-attachment-write",
        help="Execute an approved attached write request.",
        description="Execute an approved attached write request.",
    )
    execute_attachment_write_parser.add_argument("--attachment-root", required=True)
    execute_attachment_write_parser.add_argument("--attachment-runtime-state-root", required=True)
    execute_attachment_write_parser.add_argument("--task-id", required=True)
    execute_attachment_write_parser.add_argument(
        "--tool-name",
        choices=["write_file", "append_file", "shell", "git", "package"],
        default="write_file",
    )
    execute_attachment_write_parser.add_argument("--tool-command")
    execute_attachment_write_parser.add_argument("--target-path", required=True)
    execute_attachment_write_parser.add_argument("--tier", choices=["low", "medium", "high"], default="medium")
    execute_attachment_write_parser.add_argument("--rollback-reference", required=True)
    execute_attachment_write_parser.add_argument("--content", required=True)
    execute_attachment_write_parser.add_argument("--approval-id")
    execute_attachment_write_parser.add_argument("--adapter-id", default="codex-cli")
    execute_attachment_write_parser.add_argument("--session-id")
    execute_attachment_write_parser.add_argument("--resume-id")
    execute_attachment_write_parser.add_argument("--continuation-id")
    execute_attachment_write_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print runtime status snapshot")
    status_parser.add_argument("--json", action="store_true")
    status_parser.add_argument("--attachment-root")
    status_parser.add_argument("--attachment-runtime-state-root")

    args = parser.parse_args()
    _configure_runtime_roots(runtime_root=args.runtime_root, compat_runtime_root=bool(args.compat_runtime_root))

    if args.command == "create":
        payload = create_task(task_id=args.task_id, goal=args.goal, scope=args.scope, repo=args.repo)
    elif args.command == "run":
        payload = run_task(task_id=args.task_id, goal=args.goal, scope=args.scope, repo=args.repo, profile_path=args.profile, mode=args.mode)
    elif args.command == "verify-attachment":
        payload = run_attachment_verification(
            attachment_root=args.attachment_root,
            attachment_runtime_state_root=args.attachment_runtime_state_root,
            mode=args.mode,
            task_id=args.task_id,
            run_id=args.run_id,
        )
    elif args.command == "govern-attachment-write":
        payload = govern_attachment_write(
            attachment_root=args.attachment_root,
            attachment_runtime_state_root=args.attachment_runtime_state_root,
            task_id=args.task_id,
            tool_name=args.tool_name,
            command_text=args.tool_command,
            target_path=args.target_path,
            tier=args.tier,
            rollback_reference=args.rollback_reference,
            adapter_id=args.adapter_id,
            session_id=args.session_id,
            resume_id=args.resume_id,
            continuation_id=args.continuation_id,
        )
    elif args.command == "decide-attachment-write":
        payload = decide_attachment_write(
            attachment_runtime_state_root=args.attachment_runtime_state_root,
            approval_id=args.approval_id,
            decision=args.decision,
            decided_by=args.decided_by,
            task_id=args.task_id,
            adapter_id=args.adapter_id,
            session_id=args.session_id,
            resume_id=args.resume_id,
            continuation_id=args.continuation_id,
        )
    elif args.command == "execute-attachment-write":
        payload = execute_attachment_write(
            attachment_root=args.attachment_root,
            attachment_runtime_state_root=args.attachment_runtime_state_root,
            task_id=args.task_id,
            tool_name=args.tool_name,
            command_text=args.tool_command,
            target_path=args.target_path,
            tier=args.tier,
            rollback_reference=args.rollback_reference,
            content=args.content,
            approval_id=args.approval_id,
            adapter_id=args.adapter_id,
            session_id=args.session_id,
            resume_id=args.resume_id,
            continuation_id=args.continuation_id,
        )
    else:
        payload = snapshot_payload(
            attachment_root=args.attachment_root,
            attachment_runtime_state_root=args.attachment_runtime_state_root,
        )

    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_payload(payload))
    return 0


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
    identifier = task_id or create_task(
        task_id=None,
        goal=goal,
        scope=scope,
        repo=repo,
        interaction_defaults=_interaction_defaults_from_profile(profile),
    )["task_id"]
    _apply_profile_interaction_defaults_to_record(store, identifier, profile)
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
        build_verification_plan(mode, task_id=record.task_id, run_id=run.run_id),
        artifact_store=artifact_store,
        execute_gate=_execute_gate,
    )

    replay_ref = ""
    record = store.load(record.task_id)
    if any(result != "pass" for result in verification_artifact.results.values()):
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
        interaction_trace=_interaction_trace_for_record(record, profile),
    )
    evidence_artifact = artifact_store.write_json(
        task_id=record.task_id,
        run_id=run.run_id,
        kind="evidence",
        label="bundle",
        payload=evidence_bundle,
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
    refreshed.run_history = [
        _merge_run_refs(
            item,
            evidence_ref=evidence_artifact.relative_path,
            verification_refs=list(verification_artifact.result_artifact_refs.values()),
            extra_artifact_refs=run.artifact_refs + [handoff_artifact.relative_path],
        )
        if item.run_id == run.run_id
        else item
        for item in refreshed.run_history
    ]
    store.save(refreshed)
    return snapshot_payload(task_id=refreshed.task_id)


def snapshot_payload(
    *,
    task_id: str | None = None,
    attachment_root: str | None = None,
    attachment_runtime_state_root: str | None = None,
) -> dict:
    response = _dispatch_session_command(
        command_type="inspect_status",
        task_id="operator-status",
        repo_binding_id="operator-status",
        adapter_id="codex-cli",
        risk_tier="low",
        payload={},
        command_id="cli-status",
        attachment_root=attachment_root,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )
    status_payload = _response_payload(response)
    tasks = status_payload.get("tasks")
    if not isinstance(tasks, list):
        tasks = []
    maintenance = status_payload.get("maintenance")
    if not isinstance(maintenance, dict):
        maintenance = {
            "stage": status_payload.get("maintenance_stage", "unknown"),
            "compatibility_policy_ref": None,
            "upgrade_policy_ref": None,
            "triage_policy_ref": None,
            "deprecation_policy_ref": None,
            "retirement_policy_ref": None,
        }
    attachments = status_payload.get("attachments")
    if not isinstance(attachments, list):
        attachments = []
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
        "attachments": [item for item in attachments if isinstance(item, dict)],
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


def _interaction_trace_for_record(record: TaskRecord, profile: object) -> dict | None:
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


def run_attachment_verification(
    *,
    attachment_root: str,
    attachment_runtime_state_root: str,
    mode: str,
    task_id: str,
    run_id: str,
) -> dict:
    attachment_runtime_root = Path(attachment_runtime_state_root)
    attachment = validate_light_pack(
        target_repo_root=attachment_root,
        light_pack_path=str(Path(attachment_root) / ".governed-ai" / "light-pack.json"),
        runtime_state_root=str(attachment_runtime_root),
    )
    profile = load_repo_profile(attachment.repo_profile_path)
    command_type = _gate_command_type_for_mode(mode)
    response = _dispatch_session_command(
        command_type=command_type,
        task_id=task_id,
        repo_binding_id=attachment.binding.binding_id,
        adapter_id="codex-cli",
        risk_tier="low",
        payload={"run_id": run_id, "plan_only": False, "gate_level": mode},
        command_id=f"cli-verify-{task_id}-{run_id}",
        attachment_root=attachment_root,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )
    payload = _response_payload(response)
    return {
        "repo_id": profile.repo_id,
        "binding_id": attachment.binding.binding_id,
        "mode": payload["mode"],
        "task_id": task_id,
        "run_id": payload["run_id"],
        "gate_order": payload["gate_order"],
        "results": payload["results"],
        "result_artifact_refs": payload["result_artifact_refs"],
        "evidence_link": payload["evidence_link"],
    }


def govern_attachment_write(
    *,
    attachment_root: str,
    attachment_runtime_state_root: str,
    task_id: str,
    tool_name: str,
    command_text: str | None,
    target_path: str,
    tier: str,
    rollback_reference: str,
    adapter_id: str,
    session_id: str | None = None,
    resume_id: str | None = None,
    continuation_id: str | None = None,
) -> dict:
    request_payload = {
        "tool_name": tool_name,
        "command": command_text or "",
        "target_path": target_path,
        "tier": tier,
        "rollback_reference": rollback_reference,
    }
    if session_id:
        request_payload["session_id"] = session_id
    if resume_id:
        request_payload["resume_id"] = resume_id
    if continuation_id:
        request_payload["continuation_id"] = continuation_id
    response = _dispatch_session_command(
        command_type="write_request",
        task_id=task_id,
        repo_binding_id="attachment-binding",
        adapter_id=adapter_id,
        risk_tier=tier,
        payload=request_payload,
        command_id=f"cli-govern-{task_id}",
        attachment_root=attachment_root,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )
    return _response_payload(response)


def decide_attachment_write(
    *,
    attachment_runtime_state_root: str,
    approval_id: str,
    decision: str,
    decided_by: str,
    adapter_id: str,
    task_id: str = "attachment-write",
    session_id: str | None = None,
    resume_id: str | None = None,
    continuation_id: str | None = None,
) -> dict:
    decision_payload = {
        "approval_id": approval_id,
        "decision": decision,
        "decided_by": decided_by,
    }
    if session_id:
        decision_payload["session_id"] = session_id
    if resume_id:
        decision_payload["resume_id"] = resume_id
    if continuation_id:
        decision_payload["continuation_id"] = continuation_id
    response = _dispatch_session_command(
        command_type="write_approve",
        task_id=task_id,
        repo_binding_id="attachment-binding",
        adapter_id=adapter_id,
        risk_tier="medium",
        payload=decision_payload,
        command_id=f"cli-approve-{approval_id}",
        attachment_runtime_state_root=attachment_runtime_state_root,
    )
    return _response_payload(response)


def execute_attachment_write(
    *,
    attachment_root: str,
    attachment_runtime_state_root: str,
    task_id: str,
    tool_name: str,
    command_text: str | None,
    target_path: str,
    tier: str,
    rollback_reference: str,
    content: str,
    approval_id: str | None,
    adapter_id: str,
    session_id: str | None = None,
    resume_id: str | None = None,
    continuation_id: str | None = None,
) -> dict:
    request_payload = {
        "tool_name": tool_name,
        "command": command_text or "",
        "target_path": target_path,
        "tier": tier,
        "rollback_reference": rollback_reference,
        "approval_id": approval_id,
    }
    if session_id:
        request_payload["session_id"] = session_id
    if resume_id:
        request_payload["resume_id"] = resume_id
    if continuation_id:
        request_payload["continuation_id"] = continuation_id
    request_response = _dispatch_session_command(
        command_type="write_request",
        task_id=task_id,
        repo_binding_id="attachment-binding",
        adapter_id=adapter_id,
        risk_tier=tier,
        payload=request_payload,
        command_id=f"cli-exec-request-{task_id}",
        attachment_root=attachment_root,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )
    request_result = _response_payload(request_response)

    request_identity = request_result.get("session_identity")
    if not isinstance(request_identity, dict):
        request_identity = {}
    resolved_session_id = session_id or request_identity.get("session_id")
    resolved_resume_id = resume_id or request_identity.get("resume_id")
    resolved_continuation_id = continuation_id or request_result.get("continuation_id")
    execute_payload = {
        "tool_name": tool_name,
        "command": command_text or "",
        "target_path": target_path,
        "tier": tier,
        "rollback_reference": rollback_reference,
        "content": content,
        "approval_id": approval_id or request_result.get("approval_id"),
        "execution_id": request_result.get("execution_id"),
        "continuation_id": resolved_continuation_id,
    }
    if isinstance(resolved_session_id, str) and resolved_session_id.strip():
        execute_payload["session_id"] = resolved_session_id.strip()
    if isinstance(resolved_resume_id, str) and resolved_resume_id.strip():
        execute_payload["resume_id"] = resolved_resume_id.strip()
    execute_response = _dispatch_session_command(
        command_type="write_execute",
        task_id=task_id,
        repo_binding_id="attachment-binding",
        adapter_id=adapter_id,
        risk_tier=tier,
        payload=execute_payload,
        command_id=f"cli-exec-{task_id}",
        attachment_root=attachment_root,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )
    return _response_payload(execute_response)


def render_payload(payload: dict) -> str:
    codex_capability = payload.get("codex_capability") if isinstance(payload, dict) else None
    codex_line = None
    if isinstance(codex_capability, dict):
        codex_status = codex_capability.get("status", "unknown")
        codex_tier = codex_capability.get("adapter_tier", "unknown")
        codex_line = f"Codex capability: {codex_status} ({codex_tier})"
    attachment_lines = [
        f"Attachment {attachment['repo_id']}: {attachment['binding_state']} "
        f"({attachment['adapter_preference'] or 'adapter-unknown'})"
        for attachment in payload["attachments"]
    ]
    if not payload["tasks"]:
        lines = [
            f"Total tasks: {payload['total_tasks']}",
            f"Maintenance stage: {payload['maintenance']['stage']}",
        ]
        if codex_line is not None:
            lines.append(codex_line)
        lines.extend(attachment_lines)
        lines.append("No governed tasks recorded.")
        return "\n".join(lines)
    lines = [
        f"Total tasks: {payload['total_tasks']}",
        f"Maintenance stage: {payload['maintenance']['stage']}",
        f"Maintenance policy: {payload['maintenance']['compatibility_policy_ref']}",
    ]
    if codex_line is not None:
        lines.append(codex_line)
    lines.extend(attachment_lines)
    for task in payload["tasks"]:
        lines.append(f"- {task['task_id']}: {task['state']} ({task['goal']})")
        if task["active_run_id"]:
            lines.append(f"  run={task['active_run_id']} workspace={task['workspace_root']}")
        if task["verification_refs"]:
            lines.append(f"  verification={', '.join(task['verification_refs'])}")
        if task["evidence_refs"]:
            lines.append(f"  evidence={', '.join(task['evidence_refs'])}")
    return "\n".join(lines)


def _execute_gate(gate) -> tuple[int, str]:
    return _execute_gate_at_root(gate.command, cwd=ROOT)


def _gate_command_type_for_mode(mode: str) -> str:
    if mode in {"quick", "l1"}:
        return "run_quick_gate"
    return "run_full_gate"


def _execute_gate_at_root(command: str, *, cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
    )
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    return completed.returncode, output


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
    path = REPLAY_ROOT / f"{reference.task_id}-{reference.run_id}.json"
    path.write_text(
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
    return path.relative_to(ROOT).as_posix()


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


def _load_module(path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        msg = f"unable to load module: {path}"
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _build_control_plane_app() -> Any:
    facade_module = _load_module(ROOT / "packages" / "agent-runtime" / "service_facade.py", "runtime_service_facade")
    app_module = _load_module(ROOT / "apps" / "control-plane" / "app.py", "runtime_control_plane_app")
    facade = facade_module.RuntimeServiceFacade(repo_root=ROOT, task_root=TASK_ROOT)
    return app_module.ControlPlaneApplication(facade=facade)


def _dispatch_session_command(
    *,
    command_type: str,
    task_id: str,
    repo_binding_id: str,
    adapter_id: str,
    risk_tier: str,
    payload: dict,
    command_id: str,
    attachment_root: str | Path | None = None,
    attachment_runtime_state_root: str | Path | None = None,
) -> dict:
    app = _build_control_plane_app()
    return app.dispatch(
        route="/session",
        payload={
            "command_type": command_type,
            "task_id": task_id,
            "repo_binding_id": repo_binding_id,
            "adapter_id": adapter_id,
            "risk_tier": risk_tier,
            "payload": payload,
            "command_id": command_id,
            "attachment_root": str(attachment_root) if attachment_root is not None else None,
            "attachment_runtime_state_root": (
                str(attachment_runtime_state_root) if attachment_runtime_state_root is not None else None
            ),
        },
    )


def _response_payload(response: dict) -> dict:
    payload = response.get("payload") if isinstance(response, dict) else None
    if not isinstance(payload, dict):
        msg = "invalid control-plane response payload"
        raise RuntimeError(msg)
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
