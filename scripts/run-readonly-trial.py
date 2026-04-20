from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.trial_entrypoint import run_scripted_readonly_trial


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a governed read-only trial without owning agent auth.")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--acceptance", action="append", required=True)
    parser.add_argument("--repo-profile", required=True)
    parser.add_argument("--target-path", required=True)
    parser.add_argument("--max-steps", type=int, required=True)
    parser.add_argument("--max-minutes", type=int, required=True)
    parser.add_argument("--probe-live", action="store_true")
    args = parser.parse_args()

    result = run_scripted_readonly_trial(
        goal=args.goal,
        scope=args.scope,
        acceptance=args.acceptance,
        repo_profile_path=args.repo_profile,
        target_path=args.target_path,
        budgets={"max_steps": args.max_steps, "max_minutes": args.max_minutes},
        probe_live=args.probe_live,
    )
    print(
        json.dumps(
            {
                "repo_id": result.task.repo,
                "accepted_count": result.session.accepted_count,
                "summary": result.output.latest_summary,
                "auth_ownership": result.adapter["auth_ownership"],
                "adapter_tier": result.adapter["adapter_tier"],
                "invocation_mode": result.adapter["invocation_mode"],
                "probe_source": result.adapter["probe_source"],
                "unsupported_capabilities": result.adapter["unsupported_capabilities"],
                "unsupported_capability_behavior": result.adapter["unsupported_capability_behavior"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
