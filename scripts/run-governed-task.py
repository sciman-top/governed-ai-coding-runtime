from __future__ import annotations

import argparse
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
from governed_ai_coding_runtime_contracts.execution_runtime import ExecutionRuntime, WorkerExecutionResult
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.replay import build_replay_reference
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeStatusStore
from governed_ai_coding_runtime_contracts.task_intake import TaskIntake
from governed_ai_coding_runtime_contracts.task_store import FileTaskStore, TaskRecord, TaskRunRecord
from governed_ai_coding_runtime_contracts.verification_runner import build_verification_plan, run_verification_plan
from governed_ai_coding_runtime_contracts.worker import SynchronousLocalWorker
from governed_ai_coding_runtime_contracts.workflow import fail_task, transition_task


RUNTIME_ROOT = ROOT / ".runtime"
TASK_ROOT = RUNTIME_ROOT / "tasks"
ARTIFACT_ROOT = RUNTIME_ROOT / "artifacts"
REPLAY_ROOT = RUNTIME_ROOT / "replay"


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI-first governed runtime operator surface")
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

    status_parser = subparsers.add_parser("status", help="Print runtime status snapshot")
    status_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

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
    runtime = ExecutionRuntime(store=store)
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


def snapshot_payload(*, task_id: str | None = None) -> dict:
    snapshot = RuntimeStatusStore(TASK_ROOT, ROOT).snapshot()
    payload = {
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
    }
    return payload


def render_payload(payload: dict) -> str:
    if not payload["tasks"]:
        return "\n".join(
            [
                f"Total tasks: {payload['total_tasks']}",
                f"Maintenance stage: {payload['maintenance']['stage']}",
                "No governed tasks recorded.",
            ]
        )
    lines = [
        f"Total tasks: {payload['total_tasks']}",
        f"Maintenance stage: {payload['maintenance']['stage']}",
        f"Maintenance policy: {payload['maintenance']['compatibility_policy_ref']}",
    ]
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
    completed = subprocess.run(
        gate.command,
        shell=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
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


if __name__ == "__main__":
    raise SystemExit(main())
