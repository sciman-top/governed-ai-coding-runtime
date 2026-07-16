from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DEFAULT_MANIFEST = ROOT / "rules" / "manifest.json"
DEFAULT_COORDINATION = ROOT / "rules" / "target-project-rule-coordination.json"


def _run_json_script(script_name: str, arguments: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(SCRIPTS / script_name), *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {
            "status": "error",
            "reason": "invalid_json_output",
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    if not isinstance(payload, dict):
        payload = {"status": "error", "reason": "json_object_required"}
    payload["exit_code"] = completed.returncode
    return payload


def _target_arguments(
    coordination_path: Path,
    workspace_root: Path | None,
    git_ref: str | None,
) -> list[str]:
    arguments = [
        "--coordination-path",
        str(coordination_path),
        "--require-all",
    ]
    if workspace_root is not None:
        arguments.extend(["--workspace-root", str(workspace_root)])
    if git_ref is not None:
        arguments.extend(["--git-ref", git_ref])
    return arguments


def build_status(
    *,
    manifest_path: Path,
    coordination_path: Path,
    workspace_root: Path | None,
    default_ref: str,
) -> dict[str, Any]:
    source = _run_json_script(
        "verify-agent-rule-family.py",
        ["--manifest-path", str(manifest_path)],
    )
    projection = _run_json_script(
        "sync-agent-rules.py",
        ["--manifest-path", str(manifest_path), "--scope", "All", "--fail-on-change"],
    )
    default_branch = _run_json_script(
        "verify-target-project-rules.py",
        _target_arguments(coordination_path, workspace_root, default_ref),
    )
    workspace = _run_json_script(
        "verify-target-project-rules.py",
        _target_arguments(coordination_path, workspace_root, None),
    )

    states = {
        "source_ready": source.get("status") == "pass",
        "global_projected": projection.get("status") == "pass",
        "default_branch_effective": default_branch.get("status") == "pass",
        "workspace_effective": workspace.get("status") == "pass",
        "host_loaded": None,
        "hosted_accepted": None,
    }
    required_states = (
        states["source_ready"],
        states["global_projected"],
        states["default_branch_effective"],
    )
    return {
        "status": "pass" if all(required_states) else "fail",
        "states": states,
        "components": {
            "source": source,
            "global_projection": projection,
            "default_branch": default_branch,
            "workspace": workspace,
        },
        "completion_boundary": (
            "workspace state is reported but does not override published default-branch state; "
            "native host loading and hosted acceptance require separate probes"
        ),
    }


def _status_command(args: argparse.Namespace) -> int:
    result = build_status(
        manifest_path=Path(args.manifest_path),
        coordination_path=Path(args.coordination_path),
        workspace_root=Path(args.workspace_root) if args.workspace_root else None,
        default_ref=args.default_ref,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["status"] == "pass" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build, audit, project, and report Codex/Claude rule governance state."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    status = subparsers.add_parser("status", help="Report each rule-release state separately.")
    status.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST))
    status.add_argument("--coordination-path", default=str(DEFAULT_COORDINATION))
    status.add_argument("--workspace-root", default=None)
    status.add_argument("--default-ref", default="origin/main")
    status.set_defaults(handler=_status_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
