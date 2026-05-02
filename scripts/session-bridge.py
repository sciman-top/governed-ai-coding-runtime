from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

VERIFICATION_MODE_CHOICES = ["quick", "full", "l1", "l2", "l3"]

from governed_ai_coding_runtime_contracts.policy_decision import build_policy_decision
from governed_ai_coding_runtime_contracts.adapter_registry import resolve_launch_fallback
from governed_ai_coding_runtime_contracts.entrypoint_policy import EntrypointPolicyViolation
from governed_ai_coding_runtime_contracts.session_bridge import (
    build_session_bridge_command,
    handle_session_bridge_command,
    manual_handoff_result,
    run_launch_mode,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Local governed session bridge.")
    parser.add_argument("--task-root", default=str(ROOT / ".runtime" / "tasks"))
    parser.add_argument("--repo-root", default=str(ROOT))
    subparsers = parser.add_subparsers(dest="command", required=True)

    bind_parser = _add_common(subparsers.add_parser("bind-task", help="Bind an existing task to an attached repo."))
    bind_parser.set_defaults(command_type="bind_task")

    posture_parser = _add_common(subparsers.add_parser("repo-posture", help="Show attached repo posture."))
    posture_parser.add_argument("--attachment-root", required=True)
    posture_parser.add_argument("--attachment-runtime-state-root", required=True)
    posture_parser.set_defaults(command_type="show_repo_posture")

    status_parser = _add_common(subparsers.add_parser("status", help="Inspect runtime status."))
    status_parser.add_argument("--attachment-root")
    status_parser.add_argument("--attachment-runtime-state-root")
    status_parser.set_defaults(command_type="inspect_status")

    gate_parser = _add_common(
        subparsers.add_parser(
            "request-gate",
            help="Run a layered verification gate flow.",
        )
    )
    gate_parser.add_argument("--mode", choices=VERIFICATION_MODE_CHOICES, required=True)
    gate_parser.add_argument("--run-id", default="session-bridge-request")
    gate_parser.add_argument("--plan-only", action="store_true")
    gate_parser.add_argument("--policy-status", choices=["allow", "escalate", "deny"], default="allow")
    gate_parser.add_argument("--approval-ref")
    gate_parser.add_argument("--remediation-hint")
    gate_parser.add_argument("--attachment-root")
    gate_parser.add_argument("--attachment-runtime-state-root")
    gate_parser.set_defaults(command_type="run_gate")

    inspect_evidence_parser = _add_common(
        subparsers.add_parser("inspect-evidence", help="Inspect evidence refs for a task or run.")
    )
    inspect_evidence_parser.add_argument("--run-id")
    inspect_evidence_parser.add_argument("--attachment-root")
    inspect_evidence_parser.add_argument("--attachment-runtime-state-root")
    inspect_evidence_parser.set_defaults(command_type="inspect_evidence")

    inspect_handoff_parser = _add_common(
        subparsers.add_parser("inspect-handoff", help="Inspect handoff refs for a task or run.")
    )
    inspect_handoff_parser.add_argument("--run-id")
    inspect_handoff_parser.add_argument("--handoff-ref")
    inspect_handoff_parser.add_argument("--attachment-root")
    inspect_handoff_parser.add_argument("--attachment-runtime-state-root")
    inspect_handoff_parser.set_defaults(command_type="inspect_handoff")

    write_request_parser = _add_common(
        subparsers.add_parser("write-request", help="Request governed write approval or allowance.")
    )
    write_request_parser.add_argument("--attachment-root", required=True)
    write_request_parser.add_argument("--attachment-runtime-state-root", required=True)
    write_request_parser.add_argument("--tool-name", required=True)
    write_request_parser.add_argument("--target-path", required=True)
    write_request_parser.add_argument("--tier", choices=["low", "medium", "high"], required=True)
    write_request_parser.add_argument("--rollback-reference", required=True)
    write_request_parser.set_defaults(command_type="write_request")

    write_approve_parser = _add_common(
        subparsers.add_parser("write-approve", help="Record an approval decision for a governed write.")
    )
    write_approve_parser.add_argument("--attachment-runtime-state-root", required=True)
    write_approve_parser.add_argument("--approval-id", required=True)
    write_approve_parser.add_argument("--decision", choices=["approve", "reject"], required=True)
    write_approve_parser.add_argument("--decided-by", required=True)
    write_approve_parser.set_defaults(command_type="write_approve")

    write_execute_parser = _add_common(
        subparsers.add_parser("write-execute", help="Execute a governed write after policy and approval checks.")
    )
    write_execute_parser.add_argument("--attachment-root", required=True)
    write_execute_parser.add_argument("--attachment-runtime-state-root", required=True)
    write_execute_parser.add_argument("--tool-name", required=True)
    write_execute_parser.add_argument("--target-path", required=True)
    write_execute_parser.add_argument("--tier", choices=["low", "medium", "high"], required=True)
    write_execute_parser.add_argument("--rollback-reference", required=True)
    write_execute_parser.add_argument("--content", required=True)
    write_execute_parser.add_argument("--approval-id")
    write_execute_parser.add_argument("--expected-sha256")
    write_execute_parser.add_argument("--policy-status", choices=["allow", "escalate", "deny"], default="allow")
    write_execute_parser.add_argument("--policy-decision-ref")
    write_execute_parser.add_argument("--approval-ref")
    write_execute_parser.add_argument("--remediation-hint")
    write_execute_parser.add_argument("--timeout-seconds", type=float)
    write_execute_parser.add_argument("--timeout-exempt", action="store_true")
    write_execute_parser.set_defaults(command_type="write_execute")

    write_status_parser = _add_common(
        subparsers.add_parser("write-status", help="Inspect the current status of a governed write flow.")
    )
    write_status_parser.add_argument("--attachment-runtime-state-root")
    write_status_parser.add_argument("--approval-id")
    write_status_parser.add_argument("--target-path")
    write_status_parser.add_argument("--execution-id")
    write_status_parser.add_argument("--policy-decision-ref")
    write_status_parser.set_defaults(command_type="write_status")

    launch_parser = _add_common(
        subparsers.add_parser(
            "launch",
            help="Launch a process bridge fallback.",
            description="Launch a process bridge fallback.",
        )
    )
    launch_parser.add_argument("--process-bridge-unavailable", action="store_true")
    launch_parser.add_argument("--snapshot-scope")
    launch_parser.add_argument("--snapshot-mode", choices=["auto", "balanced", "strict"], default="auto")
    launch_parser.add_argument("--timeout-seconds", type=float)
    launch_parser.add_argument("--timeout-exempt", action="store_true")
    launch_parser.add_argument("argv", nargs=argparse.REMAINDER)
    launch_parser.set_defaults(command_type="launch")

    args = parser.parse_args()
    command_type = args.command_type
    payload = {}
    policy_decision = None
    if command_type == "run_gate":
        command_type = _gate_command_type_for_mode(args.mode)
        payload = {"run_id": args.run_id, "plan_only": bool(args.plan_only), "gate_level": args.mode}
        policy_decision = build_policy_decision(
            task_id=args.task_id,
            action_id=f"session:{command_type}",
            risk_tier=args.risk_tier,
            subject=f"session_command:{command_type}",
            status=args.policy_status,
            decision_basis=[f"session bridge CLI policy status is {args.policy_status}"],
            evidence_ref=f"artifacts/{args.task_id}/policy/session-bridge-{args.policy_status}.json",
            required_approval_ref=args.approval_ref,
            remediation_hint=args.remediation_hint,
        )
    elif command_type == "inspect_evidence":
        payload = {"run_id": args.run_id} if args.run_id else {}
    elif command_type == "inspect_handoff":
        payload = {}
        if args.run_id:
            payload["run_id"] = args.run_id
        if args.handoff_ref:
            payload["handoff_ref"] = args.handoff_ref
    elif command_type == "write_request":
        payload = {
            "tool_name": args.tool_name,
            "target_path": args.target_path,
            "tier": args.tier,
            "rollback_reference": args.rollback_reference,
        }
    elif command_type == "write_approve":
        payload = {
            "approval_id": args.approval_id,
            "decision": args.decision,
            "decided_by": args.decided_by,
        }
    elif command_type == "write_execute":
        payload = {
            "tool_name": args.tool_name,
            "target_path": args.target_path,
            "tier": args.tier,
            "rollback_reference": args.rollback_reference,
            "content": args.content,
        }
        if args.approval_id:
            payload["approval_id"] = args.approval_id
        if args.expected_sha256:
            payload["expected_sha256"] = args.expected_sha256
        if args.policy_decision_ref:
            payload["policy_decision_ref"] = args.policy_decision_ref
        if args.timeout_seconds is not None:
            payload["timeout_seconds"] = args.timeout_seconds
        if args.timeout_exempt:
            payload["timeout_exempt"] = True
        policy_decision_ref = args.policy_decision_ref
        if policy_decision_ref is None:
            policy_decision = build_policy_decision(
                task_id=args.task_id,
                action_id="session:write_execute",
                risk_tier=args.risk_tier,
                subject=f"session_command:write_execute:{args.target_path}",
                status=args.policy_status,
                decision_basis=[f"session bridge CLI policy status is {args.policy_status}"],
                evidence_ref=f"artifacts/{args.task_id}/policy/session-bridge-write-{args.policy_status}.json",
                required_approval_ref=args.approval_ref,
                remediation_hint=args.remediation_hint,
            )
    elif command_type == "write_status":
        payload = {}
        if args.approval_id:
            payload["approval_id"] = args.approval_id
        if args.target_path:
            payload["target_path"] = args.target_path
        if args.execution_id:
            payload["execution_id"] = args.execution_id

    if args.session_id:
        payload["session_id"] = args.session_id
    if args.resume_id:
        payload["resume_id"] = args.resume_id
    if args.continuation_id:
        payload["continuation_id"] = args.continuation_id
    if args.entrypoint_id:
        payload["entrypoint_id"] = args.entrypoint_id

    bridge_command_type = "bind_task" if command_type == "launch" else command_type
    command = build_session_bridge_command(
        command_id=args.command_id,
        command_type=bridge_command_type,
        task_id=args.task_id,
        repo_binding_id=args.repo_binding_id,
        adapter_id=args.adapter_id,
        risk_tier=args.risk_tier,
        payload=payload,
        policy_decision=policy_decision,
        policy_decision_ref=getattr(args, "policy_decision_ref", None),
    )
    try:
        if command_type == "launch":
            capability = resolve_launch_fallback(
                adapter_id=args.adapter_id,
                native_attach_available=False,
                process_bridge_available=not args.process_bridge_unavailable,
            )
            if capability.tier == "manual_handoff":
                result = manual_handoff_result(command, reason=capability.reason)
            else:
                argv = args.argv
                if argv and argv[0] == "--":
                    argv = argv[1:]
                if not argv:
                    argv = [sys.executable, "-c", "print('session bridge launch fallback')"]
                result = run_launch_mode(
                    command,
                    argv=argv,
                    cwd=Path(args.repo_root),
                    snapshot_scope=args.snapshot_scope,
                    snapshot_mode=args.snapshot_mode,
                    timeout_seconds=args.timeout_seconds,
                    timeout_exempt=args.timeout_exempt,
                )
        else:
            result = handle_session_bridge_command(
                command,
                task_root=Path(args.task_root),
                repo_root=Path(args.repo_root),
                attachment_root=getattr(args, "attachment_root", None),
                attachment_runtime_state_root=getattr(args, "attachment_runtime_state_root", None),
            )
    except EntrypointPolicyViolation as exc:
        payload = {
            "status": "entrypoint_policy_denied",
            "entrypoint_policy": exc.evaluation,
            "reason": exc.evaluation.get("reason"),
            "remediation_hint": exc.evaluation.get("remediation_hint"),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    if result.status == "denied":
        entrypoint_policy = result.payload.get("entrypoint_policy")
        if isinstance(entrypoint_policy, dict) and entrypoint_policy.get("blocked") is True:
            return 1
    return 0


def _add_common(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--command-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--repo-binding-id", required=True)
    parser.add_argument("--adapter-id", default="manual-handoff")
    parser.add_argument("--risk-tier", choices=["low", "medium", "high"], default="low")
    parser.add_argument("--session-id")
    parser.add_argument("--resume-id")
    parser.add_argument("--continuation-id")
    parser.add_argument("--entrypoint-id")
    return parser


def _gate_command_type_for_mode(mode: str) -> str:
    if mode in {"quick", "l1"}:
        return "run_quick_gate"
    return "run_full_gate"


if __name__ == "__main__":
    raise SystemExit(main())
