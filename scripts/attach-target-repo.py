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


def _resolve_gate_commands(
    *,
    primary_language: str,
    build_command: str | None,
    test_command: str | None,
    contract_command: str | None,
    infer_gate_defaults: bool,
) -> tuple[str, str, str, str]:
    build = (build_command or "").strip()
    test = (test_command or "").strip()
    contract = (contract_command or "").strip()

    missing = [name for name, value in (("build", build), ("test", test), ("contract", contract)) if not value]
    if not missing:
        return build, test, contract, "explicit"

    if not infer_gate_defaults:
        missing_args = ", ".join(f"--{name}-command" for name in missing)
        raise ValueError(f"missing required gate commands: {missing_args}; pass --infer-gate-defaults to use defaults")

    normalized_language = primary_language.strip().lower()
    defaults = {
        "python": (
            "python -m compileall src",
            "python -m unittest discover",
            "python -m unittest discover -s tests/contracts",
        ),
        "javascript": ("npm run build --if-present", "npm test -- --watch=false", "npm run contract --if-present"),
        "typescript": ("npm run build --if-present", "npm test -- --watch=false", "npm run contract --if-present"),
        "node": ("npm run build --if-present", "npm test -- --watch=false", "npm run contract --if-present"),
        "go": ("go build ./...", "go test ./...", "go test ./..."),
        "dotnet": ("dotnet build", "dotnet test", "dotnet test"),
        "csharp": ("dotnet build", "dotnet test", "dotnet test"),
        "cs": ("dotnet build", "dotnet test", "dotnet test"),
    }
    if normalized_language not in defaults:
        supported = ", ".join(sorted(defaults))
        raise ValueError(
            f"cannot infer gate defaults for primary_language={primary_language!r}; supported: {supported}. "
            "Provide explicit --build-command/--test-command/--contract-command."
        )

    default_build, default_test, default_contract = defaults[normalized_language]
    return (
        build or default_build,
        test or default_test,
        contract or default_contract,
        "inferred_defaults",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Attach or validate a target repository light pack.")
    parser.add_argument("--target-repo", required=True, help="Existing target repository root.")
    parser.add_argument("--runtime-state-root", help="Machine-local runtime state root for this attachment.")
    parser.add_argument("--repo-id", help="Stable repository id. Defaults to the target directory name.")
    parser.add_argument("--display-name", help="Human-readable repository name. Defaults to repo id.")
    parser.add_argument("--primary-language", default="unknown")
    parser.add_argument("--build-command")
    parser.add_argument("--test-command")
    parser.add_argument("--contract-command")
    parser.add_argument(
        "--infer-gate-defaults",
        action="store_true",
        help="Infer missing build/test/contract commands from primary language.",
    )
    parser.add_argument(
        "--adapter-preference",
        choices=["native_attach", "process_bridge", "manual_handoff"],
        default="native_attach",
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
    try:
        build_command, test_command, contract_command, gate_command_source = _resolve_gate_commands(
            primary_language=args.primary_language,
            build_command=args.build_command,
            test_command=args.test_command,
            contract_command=args.contract_command,
            infer_gate_defaults=args.infer_gate_defaults,
        )
    except ValueError as exc:
        parser.error(str(exc))

    result = attach_target_repo(
        target_repo_root=str(target_repo),
        runtime_state_root=str(runtime_state_root),
        repo_id=repo_id,
        display_name=args.display_name or repo_id,
        primary_language=args.primary_language,
        build_command=build_command,
        test_command=test_command,
        contract_command=contract_command,
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
                "context_pack_summary": result.context_pack_summary,
                "gate_command_source": gate_command_source,
                "inferred_gate_defaults_used": gate_command_source == "inferred_defaults",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
