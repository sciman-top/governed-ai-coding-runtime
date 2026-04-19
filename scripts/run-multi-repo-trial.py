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

from governed_ai_coding_runtime_contracts.multi_repo_trial import run_multi_repo_trial


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a multi-repo trial for profiles or attached repositories.")
    parser.add_argument("--repo-profile", action="append", dest="repo_profiles")
    parser.add_argument("--attachment-root", action="append", dest="attachment_roots")
    parser.add_argument("--attachment-runtime-state-root", action="append", dest="attachment_runtime_state_roots")
    parser.add_argument("--trial-id", default="multi-repo-trial")
    parser.add_argument("--adapter-id", default="codex-cli")
    parser.add_argument(
        "--adapter-tier",
        choices=["native_attach", "process_bridge", "manual_handoff"],
        default="process_bridge",
    )
    parser.add_argument("--unsupported-capability", action="append", dest="unsupported_capabilities")
    parser.add_argument("--execute-write-probe", action="store_true")
    args = parser.parse_args()

    repo_profiles = args.repo_profiles or []
    attachment_roots = args.attachment_roots or []
    if not repo_profiles and not attachment_roots:
        repo_profiles = [
            str(ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"),
            str(ROOT / "schemas" / "examples" / "repo-profile" / "typescript-webapp.example.json"),
        ]
    unsupported_capabilities = args.unsupported_capabilities or ["native_attach"]
    result = run_multi_repo_trial(
        adapter_id=args.adapter_id,
        adapter_tier=args.adapter_tier,
        unsupported_capabilities=unsupported_capabilities,
        trial_id=args.trial_id,
        repo_profile_paths=repo_profiles,
        attachment_roots=attachment_roots,
        attachment_runtime_state_roots=args.attachment_runtime_state_roots or [],
        execute_write_probe=bool(args.execute_write_probe),
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
