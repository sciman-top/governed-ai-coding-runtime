from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs/change-evidence/runtime-evolution-patches/20260501-runtime-evolution-materialization.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a review-gated runtime evolution PR plan.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--as-of", default=None)
    args = parser.parse_args()

    try:
        as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
        result = prepare_runtime_evolution_pr(
            repo_root=Path(args.repo_root),
            manifest_path=Path(args.manifest),
            as_of=as_of,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def prepare_runtime_evolution_pr(*, repo_root: Path, manifest_path: Path, as_of: dt.date) -> dict:
    root = repo_root.resolve(strict=False)
    manifest = _load_manifest(manifest_path)
    operation_paths = manifest.get("operation_paths")
    if not isinstance(operation_paths, list) or not operation_paths:
        raise ValueError("materialization manifest must include operation_paths")

    missing = [path for path in operation_paths if not (root / path).exists()]
    if missing:
        raise ValueError("materialized files are missing: " + ", ".join(missing))

    branch = f"codex/runtime-evolution-materialization-{as_of.strftime('%Y%m%d')}"
    return {
        "status": "pass",
        "as_of": as_of.isoformat(),
        "mode": "review_plan",
        "mutation_allowed": False,
        "recommended_branch": branch,
        "commit_message": "Materialize runtime evolution candidates",
        "pr_title": "Materialize runtime evolution candidates",
        "pr_body": _render_pr_body(operation_paths),
        "operation_paths": operation_paths,
        "required_gates": [
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1",
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime",
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract",
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1",
        ],
        "guard": {
            "auto_branch_created": False,
            "auto_commit_created": False,
            "auto_push_created": False,
            "auto_pr_created": False,
            "requires_explicit_git_execution": True,
        },
    }


def _load_manifest(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"materialization manifest is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"materialization manifest is invalid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("materialization manifest must be an object")
    return payload


def _render_pr_body(operation_paths: list[str]) -> str:
    file_list = "\n".join(f"- `{path}`" for path in operation_paths)
    return (
        "Materializes reviewed runtime-evolution candidates as proposal and disabled skill candidate files.\n\n"
        "Generated files:\n"
        f"{file_list}\n\n"
        "Guards:\n"
        "- Does not enable skills.\n"
        "- Does not auto-apply policy.\n"
        "- Does not sync target repos.\n"
        "- Requires full gates before merge.\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
