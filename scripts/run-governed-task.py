from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import subprocess
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
from governed_ai_coding_runtime_contracts.repo_attachment import validate_light_pack
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.replay import build_replay_reference
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeStatusStore
from governed_ai_coding_runtime_contracts.runtime_roots import ensure_runtime_roots, resolve_runtime_roots
from governed_ai_coding_runtime_contracts.session_bridge import (
    build_session_bridge_command,
    handle_session_bridge_command,
)
from governed_ai_coding_runtime_contracts.task_intake import TaskIntake
from governed_ai_coding_runtime_contracts.task_store import FileTaskStore, TaskRecord, TaskRunRecord
from governed_ai_coding_runtime_contracts.verification_runner import (
    build_repo_profile_verification_plan,
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
    run_parser.add_argument("--mode", choices=["quick", "full"], default="full")
    run_parser.add_argument("--json", action="store_true")

    verify_attachment_parser = subparsers.add_parser(
        "verify-attachment",
        help="Execute declared verification gates for an attached target repo",
        description="Execute declared verification gates for an attached target repo.",
    )
    verify_attachment_parser.add_argument("--attachment-root", required=True)
    verify_attachment_parser.add_argument("--attachment-runtime-state-root", required=True)
    verify_attachment_parser.add_argument("--mode", choices=["quick", "full"], default="quick")
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
    decide_attachment_write_parser.add_argument("--adapter-id", default="codex-cli")
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
        )
    elif args.command == "decide-attachment-write":
        payload = decide_attachment_write(
            attachment_runtime_state_root=args.attachment_runtime_state_root,
            approval_id=args.approval_id,
            decision=args.decision,
            decided_by=args.decided_by,
            adapter_id=args.adapter_id,
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


def create_task(*, task_id: str | None, goal: str, scope: str, repo: str) -> dict:
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
        ),
        current_state="planned",
    )
    store.save(record)
    return {"task_id": identifier, "state": "planned"}


def run_task(*, task_id: str | None, goal: str, scope: str, repo: str, profile_path: str, mode: str) -> dict:
    store = FileTaskStore(TASK_ROOT)
    identifier = task_id or create_task(task_id=None, goal=goal, scope=scope, repo=repo)["task_id"]
    profile = load_repo_profile(profile_path)
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
    attachment_roots = [Path(attachment_root)] if attachment_root else None
    runtime_state_root = Path(attachment_runtime_state_root) if attachment_runtime_state_root else None
    snapshot = RuntimeStatusStore(
        TASK_ROOT,
        ROOT,
        attachment_roots=attachment_roots,
        attachment_runtime_state_root=runtime_state_root,
    ).snapshot()
    payload = {
        "runtime_roots": {
            "runtime_root": RUNTIME_ROOT.as_posix(),
            "tasks_root": TASK_ROOT.as_posix(),
            "artifacts_root": ARTIFACT_ROOT.as_posix(),
            "replay_root": REPLAY_ROOT.as_posix(),
            "workspaces_root": WORKSPACES_ROOT.as_posix(),
            "compatibility_mode": _RUNTIME_ROOTS.compatibility_mode,
        },
        "total_tasks": snapshot.total_tasks,
        "maintenance": {
            "stage": snapshot.maintenance.stage,
            "compatibility_policy_ref": snapshot.maintenance.compatibility_policy_ref,
            "upgrade_policy_ref": snapshot.maintenance.upgrade_policy_ref,
            "triage_policy_ref": snapshot.maintenance.triage_policy_ref,
            "deprecation_policy_ref": snapshot.maintenance.deprecation_policy_ref,
            "retirement_policy_ref": snapshot.maintenance.retirement_policy_ref,
        },
        "tasks": [
            {
                "task_id": task.task_id,
                "state": task.current_state,
                "goal": task.goal,
                "active_run_id": task.active_run_id,
                "workspace_root": task.workspace_root,
                "rollback_ref": task.rollback_ref,
                "approval_ids": task.approval_ids,
                "artifact_refs": task.artifact_refs,
                "evidence_refs": task.evidence_refs,
                "verification_refs": task.verification_refs,
            }
            for task in snapshot.tasks
            if task_id is None or task.task_id == task_id
        ],
        "attachments": [
            {
                "repo_id": attachment.repo_id,
                "binding_id": attachment.binding_id,
                "binding_state": attachment.binding_state,
                "light_pack_path": attachment.light_pack_path,
                "adapter_preference": attachment.adapter_preference,
                "gate_profile": attachment.gate_profile,
                "reason": attachment.reason,
                "remediation": attachment.remediation,
                "fail_closed": attachment.fail_closed,
            }
            for attachment in snapshot.attachments
        ],
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
    plan = build_repo_profile_verification_plan(
        mode,
        profile_raw=profile.raw,
        task_id=task_id,
        run_id=run_id,
    )
    artifact_store = LocalArtifactStore(attachment_runtime_root)
    artifact = run_verification_plan(
        plan,
        artifact_store=artifact_store,
        execute_gate=lambda gate: _execute_gate_at_root(gate.command, cwd=Path(attachment_root)),
    )
    return {
        "repo_id": profile.repo_id,
        "binding_id": attachment.binding.binding_id,
        "mode": artifact.mode,
        "task_id": artifact.task_id,
        "run_id": artifact.run_id,
        "gate_order": artifact.gate_order,
        "results": artifact.results,
        "result_artifact_refs": artifact.result_artifact_refs,
        "evidence_link": artifact.evidence_link,
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
) -> dict:
    command = build_session_bridge_command(
        command_id=f"cli-govern-{task_id}",
        command_type="write_request",
        task_id=task_id,
        repo_binding_id="attachment-binding",
        adapter_id=adapter_id,
        risk_tier=tier,
        payload={
            "tool_name": tool_name,
            "command": command_text or "",
            "target_path": target_path,
            "tier": tier,
            "rollback_reference": rollback_reference,
        },
    )
    result = handle_session_bridge_command(
        command,
        task_root=TASK_ROOT,
        repo_root=ROOT,
        attachment_root=attachment_root,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )
    return result.payload


def decide_attachment_write(
    *,
    attachment_runtime_state_root: str,
    approval_id: str,
    decision: str,
    decided_by: str,
    adapter_id: str,
) -> dict:
    command = build_session_bridge_command(
        command_id=f"cli-approve-{approval_id}",
        command_type="write_approve",
        task_id="attachment-write",
        repo_binding_id="attachment-binding",
        adapter_id=adapter_id,
        risk_tier="medium",
        payload={
            "approval_id": approval_id,
            "decision": decision,
            "decided_by": decided_by,
        },
    )
    result = handle_session_bridge_command(
        command,
        task_root=TASK_ROOT,
        repo_root=ROOT,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )
    return result.payload


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
) -> dict:
    request_command = build_session_bridge_command(
        command_id=f"cli-exec-request-{task_id}",
        command_type="write_request",
        task_id=task_id,
        repo_binding_id="attachment-binding",
        adapter_id=adapter_id,
        risk_tier=tier,
        payload={
            "tool_name": tool_name,
            "command": command_text or "",
            "target_path": target_path,
            "tier": tier,
            "rollback_reference": rollback_reference,
            "approval_id": approval_id,
        },
    )
    request_result = handle_session_bridge_command(
        request_command,
        task_root=TASK_ROOT,
        repo_root=ROOT,
        attachment_root=attachment_root,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )

    execute_command = build_session_bridge_command(
        command_id=f"cli-exec-{task_id}",
        command_type="write_execute",
        task_id=task_id,
        repo_binding_id="attachment-binding",
        adapter_id=adapter_id,
        risk_tier=tier,
        payload={
            "tool_name": tool_name,
            "command": command_text or "",
            "target_path": target_path,
            "tier": tier,
            "rollback_reference": rollback_reference,
            "content": content,
            "approval_id": approval_id or request_result.payload.get("approval_id"),
            "execution_id": request_result.payload.get("execution_id"),
            "continuation_id": request_result.payload.get("continuation_id"),
        },
        policy_decision_ref=request_result.payload.get("policy_decision_ref"),
    )
    execute_result = handle_session_bridge_command(
        execute_command,
        task_root=TASK_ROOT,
        repo_root=ROOT,
        attachment_root=attachment_root,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )
    return execute_result.payload


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


if __name__ == "__main__":
    raise SystemExit(main())
