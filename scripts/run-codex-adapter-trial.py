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
    codex_adapter_trial_to_dict,
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
    args = parser.parse_args()

    result = build_codex_adapter_trial_result(
        repo_id=args.repo_id,
        task_id=args.task_id,
        binding_id=args.binding_id,
        native_attach_available=args.native_attach,
        process_bridge_available=not args.no_process_bridge,
        structured_events_available=args.structured_events,
        evidence_export_available=args.evidence_export,
        resume_available=args.resume,
        mode=args.mode,
        run_id=args.run_id,
    )
    print(json.dumps(codex_adapter_trial_to_dict(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
