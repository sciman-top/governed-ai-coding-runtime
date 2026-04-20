from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.codex_adapter import (
    build_codex_adapter_trial_result,
    codex_probe_to_dict,
    codex_adapter_trial_to_dict,
    probe_codex_surface,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a safe-mode Codex direct adapter smoke trial.")
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--binding-id", required=True)
    parser.add_argument("--mode", default="safe")
    parser.add_argument("--run-id", default="codex-trial-safe")
    parser.add_argument("--native-attach", action="store_true")
    parser.add_argument("--no-process-bridge", action="store_true")
    parser.add_argument("--structured-events", action="store_true")
    parser.add_argument("--evidence-export", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--codex-bin",
        help="Optional Codex executable path or command name used by --probe-live.",
    )
    parser.add_argument(
        "--probe-cwd",
        help="Optional working directory for live probe commands.",
    )
    parser.add_argument(
        "--probe-live",
        action="store_true",
        help="Probe the local Codex surface (codex --version/--help/status) and derive adapter posture from live results.",
    )
    args = parser.parse_args()

    live_probe = (
        probe_codex_surface(
            cwd=args.probe_cwd,
            codex_executable=args.codex_bin,
        )
        if args.probe_live
        else None
    )
    native_attach_available = live_probe.native_attach_available if live_probe else args.native_attach
    process_bridge_available = live_probe.process_bridge_available if live_probe else not args.no_process_bridge
    structured_events_available = live_probe.structured_events_available if live_probe else args.structured_events
    evidence_export_available = live_probe.evidence_export_available if live_probe else args.evidence_export
    resume_available = live_probe.resume_available if live_probe else args.resume

    result = build_codex_adapter_trial_result(
        repo_id=args.repo_id,
        task_id=args.task_id,
        binding_id=args.binding_id,
        native_attach_available=native_attach_available,
        process_bridge_available=process_bridge_available,
        structured_events_available=structured_events_available,
        evidence_export_available=evidence_export_available,
        resume_available=resume_available,
        mode=args.mode,
        run_id=args.run_id,
    )
    payload = codex_adapter_trial_to_dict(result)
    if live_probe is not None:
        payload["live_probe"] = codex_probe_to_dict(live_probe)
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
