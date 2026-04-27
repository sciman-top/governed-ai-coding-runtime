from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.claude_code_adapter import (
    build_claude_code_adapter_trial_result,
    claude_code_adapter_trial_to_dict,
    claude_code_probe_to_dict,
    probe_claude_code_surface,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a safe-mode Claude Code adapter smoke trial.")
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--binding-id", required=True)
    parser.add_argument("--mode", default="safe")
    parser.add_argument("--run-id", default="claude-code-trial-safe")
    parser.add_argument("--native-attach", action="store_true")
    parser.add_argument("--no-process-bridge", action="store_true")
    parser.add_argument("--settings", action="store_true")
    parser.add_argument("--hooks", action="store_true")
    parser.add_argument("--session-id", action="store_true")
    parser.add_argument("--structured-events", action="store_true")
    parser.add_argument("--evidence-export", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--claude-bin", help="Optional Claude Code executable path or command name used by --probe-live.")
    parser.add_argument("--probe-cwd", help="Optional working directory for live probe commands.")
    parser.add_argument("--probe-live", action="store_true", help="Probe the local Claude Code surface.")
    args = parser.parse_args()

    live_probe = (
        probe_claude_code_surface(
            cwd=args.probe_cwd,
            claude_executable=args.claude_bin,
        )
        if args.probe_live
        else None
    )
    result = build_claude_code_adapter_trial_result(
        repo_id=args.repo_id,
        task_id=args.task_id,
        binding_id=args.binding_id,
        process_bridge_available=live_probe.process_bridge_available if live_probe else not args.no_process_bridge,
        settings_available=live_probe.settings_available if live_probe else args.settings,
        hooks_available=live_probe.hooks_available if live_probe else args.hooks,
        session_id_available=live_probe.session_id_available if live_probe else args.session_id,
        structured_events_available=live_probe.structured_events_available if live_probe else args.structured_events,
        evidence_export_available=live_probe.evidence_export_available if live_probe else args.evidence_export,
        resume_available=live_probe.resume_available if live_probe else args.resume,
        native_attach_available=live_probe.native_attach_available if live_probe else args.native_attach,
        mode=args.mode,
        run_id=args.run_id,
        probe=live_probe,
    )
    payload = claude_code_adapter_trial_to_dict(result)
    if live_probe is not None:
        payload["live_probe"] = claude_code_probe_to_dict(live_probe)
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
