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

from governed_ai_coding_runtime_contracts.policy_decision import build_policy_decision
from governed_ai_coding_runtime_contracts.adapter_registry import resolve_launch_fallback
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

    gate_parser = _add_common(subparsers.add_parser("request-gate", help="Request a quick or full verification gate plan."))
    gate_parser.add_argument("--mode", choices=["quick", "full"], required=True)
    gate_parser.add_argument("--run-id", default="session-bridge-request")
    gate_parser.add_argument("--policy-status", choices=["allow", "escalate", "deny"], default="allow")
    gate_parser.add_argument("--approval-ref")
    gate_parser.add_argument("--remediation-hint")
    gate_parser.add_argument("--attachment-root")
    gate_parser.add_argument("--attachment-runtime-state-root")
    gate_parser.set_defaults(command_type="run_gate")

    launch_parser = _add_common(
        subparsers.add_parser(
            "launch",
            help="Launch a process bridge fallback.",
            description="Launch a process bridge fallback.",
        )
    )
    launch_parser.add_argument("--process-bridge-unavailable", action="store_true")
    launch_parser.add_argument("argv", nargs=argparse.REMAINDER)
    launch_parser.set_defaults(command_type="launch")

    args = parser.parse_args()
    command_type = args.command_type
    payload = {}
    policy_decision = None
    if command_type == "run_gate":
        command_type = "run_quick_gate" if args.mode == "quick" else "run_full_gate"
        payload = {"run_id": args.run_id}
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
    )
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
            result = run_launch_mode(command, argv=argv, cwd=Path(args.repo_root))
    else:
        result = handle_session_bridge_command(
            command,
            task_root=Path(args.task_root),
            repo_root=Path(args.repo_root),
            attachment_root=getattr(args, "attachment_root", None),
            attachment_runtime_state_root=getattr(args, "attachment_runtime_state_root", None),
        )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0


def _add_common(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--command-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--repo-binding-id", required=True)
    parser.add_argument("--adapter-id", default="manual-handoff")
    parser.add_argument("--risk-tier", choices=["low", "medium", "high"], default="low")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
