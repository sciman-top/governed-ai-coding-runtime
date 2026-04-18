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

from governed_ai_coding_runtime_contracts.repo_attachment import attach_target_repo


def main() -> int:
    parser = argparse.ArgumentParser(description="Attach or validate a target repository light pack.")
    parser.add_argument("--target-repo", required=True, help="Existing target repository root.")
    parser.add_argument("--runtime-state-root", help="Machine-local runtime state root for this attachment.")
    parser.add_argument("--repo-id", help="Stable repository id. Defaults to the target directory name.")
    parser.add_argument("--display-name", help="Human-readable repository name. Defaults to repo id.")
    parser.add_argument("--primary-language", default="unknown")
    parser.add_argument("--build-command", required=True)
    parser.add_argument("--test-command", required=True)
    parser.add_argument("--contract-command", required=True)
    parser.add_argument(
        "--adapter-preference",
        choices=["native_attach", "process_bridge", "manual_handoff"],
        default="manual_handoff",
    )
    parser.add_argument("--gate-profile", default="default")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate existing repo-local attachment files.")
    args = parser.parse_args()

    target_repo = Path(args.target_repo).resolve(strict=False)
    repo_id = args.repo_id or target_repo.name
    runtime_state_root = (
        Path(args.runtime_state_root).resolve(strict=False)
        if args.runtime_state_root
        else ROOT / ".runtime" / "attachments" / repo_id
    )

    result = attach_target_repo(
        target_repo_root=str(target_repo),
        runtime_state_root=str(runtime_state_root),
        repo_id=repo_id,
        display_name=args.display_name or repo_id,
        primary_language=args.primary_language,
        build_command=args.build_command,
        test_command=args.test_command,
        contract_command=args.contract_command,
        adapter_preference=args.adapter_preference,
        gate_profile=args.gate_profile,
        overwrite=args.overwrite,
    )
    print(
        json.dumps(
            {
                "operation": result.operation,
                "binding": asdict(result.binding),
                "repo_profile_path": result.repo_profile_path,
                "light_pack_path": result.light_pack_path,
                "written_files": result.written_files,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
