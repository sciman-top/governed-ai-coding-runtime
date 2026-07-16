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
DEFAULT_SOURCE_MANIFEST = ROOT / "rules" / "global" / "source-manifest.json"
RULE_SCRIPTS = (
    SCRIPTS / "rulesctl.py",
    SCRIPTS / "build-global-rules.py",
    SCRIPTS / "verify-agent-rule-family.py",
    SCRIPTS / "verify-target-project-rules.py",
    SCRIPTS / "sync-agent-rules.py",
    SCRIPTS / "export-target-rule-ci-matrix.py",
)
RULE_TEST_MODULES = (
    "tests.runtime.test_agent_rule_sync",
    "tests.runtime.test_build_global_rules",
    "tests.runtime.test_rulesctl",
    "tests.runtime.test_rulesctl_gates",
    "tests.runtime.test_target_rule_ci",
    "tests.runtime.test_verify_agent_rule_family",
    "tests.runtime.test_verify_target_project_rules",
)
FORBIDDEN_TRACKED_PATHS = (
    ".agents/",
    ".claude/",
    ".codex/",
    ".governed-ai/",
    ".playwright-mcp/",
    ".runtime/",
    ".tmp-test/",
    ".vs/",
    ".worktrees/",
    "apps/",
    "infra/",
    "packages/",
    "rules/global/gemini/",
    "skills/",
    "tmp_runtime_runner_",
)
FORBIDDEN_TRACKED_FILES = {
    ".geminiignore",
    ".github/workflows/runtime-evolution.yml",
    "GEMINI.md",
    "install.ps1",
    "release.ps1",
    "run.ps1",
}


def _run_process(arguments: list[str], *, cwd: Path = ROOT) -> dict[str, Any]:
    completed = subprocess.run(
        arguments,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "status": "pass" if completed.returncode == 0 else "fail",
        "exit_code": completed.returncode,
        "command": arguments,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _run_json_script(script_name: str, arguments: list[str]) -> dict[str, Any]:
    completed = _run_process([sys.executable, str(SCRIPTS / script_name), *arguments])
    try:
        payload = json.loads(completed["stdout"])
    except json.JSONDecodeError:
        payload = {
            "status": "error",
            "reason": "invalid_json_output",
            "stdout": completed["stdout"],
            "stderr": completed["stderr"],
        }
    if not isinstance(payload, dict):
        payload = {"status": "error", "reason": "json_object_required"}
    payload["exit_code"] = completed["exit_code"]
    payload.setdefault("status", "pass" if completed["exit_code"] == 0 else "fail")
    return payload


def _gate_result(gate: str, checks: list[dict[str, Any]]) -> dict[str, Any]:
    passed = all(check.get("status") in {"pass", "skipped"} for check in checks)
    return {
        "status": "pass" if passed else "fail",
        "gate": gate,
        "checks": checks,
    }


def build_gate() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for path in RULE_SCRIPTS:
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
        except (OSError, SyntaxError, UnicodeError) as exc:
            checks.append(
                {
                    "status": "fail",
                    "check": "python_syntax",
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "reason": str(exc),
                }
            )
        else:
            checks.append(
                {
                    "status": "pass",
                    "check": "python_syntax",
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                }
            )
    for path in (DEFAULT_MANIFEST, DEFAULT_COORDINATION, DEFAULT_SOURCE_MANIFEST):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON object required")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            checks.append(
                {
                    "status": "fail",
                    "check": "json_parse",
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "reason": str(exc),
                }
            )
        else:
            checks.append(
                {
                    "status": "pass",
                    "check": "json_parse",
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                }
            )
    assembly = _run_json_script(
        "build-global-rules.py",
        ["--manifest-path", str(DEFAULT_SOURCE_MANIFEST), "--check"],
    )
    assembly["check"] = "global_rule_assembly"
    checks.append(assembly)
    return _gate_result("build", checks)


def test_gate() -> dict[str, Any]:
    check = _run_process(
        [sys.executable, "-m", "unittest", *RULE_TEST_MODULES],
    )
    check["check"] = "focused_rule_tests"
    return _gate_result("test", [check])


def _skipped_check(check: str, reason: str) -> dict[str, Any]:
    return {
        "status": "skipped",
        "check": check,
        "reason": reason,
    }


def contract_gate(
    *,
    manifest_path: Path,
    coordination_path: Path,
    workspace_root: Path | None,
    default_ref: str,
    user_profile: Path | None,
    skip_projection: bool,
    skip_targets: bool,
) -> dict[str, Any]:
    family = _run_json_script(
        "verify-agent-rule-family.py",
        ["--manifest-path", str(manifest_path)],
    )
    family["check"] = "global_rule_family"
    checks = [family]

    if skip_projection:
        checks.append(
            _skipped_check(
                "global_projection",
                "explicitly skipped for an isolated CI home; sync behavior remains unit-tested",
            )
        )
    else:
        projection_arguments = [
            "--manifest-path",
            str(manifest_path),
            "--scope",
            "All",
            "--fail-on-change",
        ]
        if user_profile is not None:
            projection_arguments.extend(["--user-profile", str(user_profile)])
        projection = _run_json_script("sync-agent-rules.py", projection_arguments)
        projection["check"] = "global_projection"
        checks.append(projection)

    if skip_targets:
        checks.append(
            _skipped_check(
                "target_default_branches",
                "aggregate agent-rule-coordination CI owns cross-repository audits",
            )
        )
    else:
        targets = _run_json_script(
            "verify-target-project-rules.py",
            _target_arguments(coordination_path, workspace_root, default_ref),
        )
        targets["check"] = "target_default_branches"
        checks.append(targets)

    matrix = _run_json_script(
        "export-target-rule-ci-matrix.py",
        ["--coordination-path", str(coordination_path)],
    )
    matrix["check"] = "target_ci_matrix"
    checks.append(matrix)
    return _gate_result("contract", checks)


def product_boundary_findings(paths: list[str]) -> list[str]:
    findings: list[str] = []
    for raw_path in paths:
        path = raw_path.replace("\\", "/")
        while path.startswith("./"):
            path = path[2:]
        if path in FORBIDDEN_TRACKED_FILES:
            findings.append(path)
            continue
        if path.startswith("operator-ui-") and path.lower().endswith(".png"):
            findings.append(path)
            continue
        if any(path.startswith(prefix) for prefix in FORBIDDEN_TRACKED_PATHS):
            findings.append(path)
    return sorted(set(findings), key=str.casefold)


def _tracked_paths() -> tuple[list[str], dict[str, Any] | None]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        return [], {
            "status": "fail",
            "check": "tracked_product_boundary",
            "reason": completed.stderr.decode("utf-8", errors="replace").strip(),
        }
    return [item.decode("utf-8") for item in completed.stdout.split(b"\0") if item], None


def hotspot_gate() -> dict[str, Any]:
    paths, error = _tracked_paths()
    if error is not None:
        return _gate_result("hotspot", [error])
    findings = product_boundary_findings(paths)
    check = {
        "status": "fail" if findings else "pass",
        "check": "tracked_product_boundary",
        "forbidden_count": len(findings),
        "findings": findings[:100],
        "truncated": len(findings) > 100,
    }
    return _gate_result("hotspot", [check])


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
    assembly = _run_json_script(
        "build-global-rules.py",
        ["--manifest-path", str(DEFAULT_SOURCE_MANIFEST), "--check"],
    )
    family = _run_json_script(
        "verify-agent-rule-family.py",
        ["--manifest-path", str(manifest_path)],
    )
    source = {
        "status": (
            "pass"
            if assembly.get("status") == "pass" and family.get("status") == "pass"
            else "fail"
        ),
        "assembly": assembly,
        "family": family,
    }
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


def _emit(result: dict[str, Any]) -> int:
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result.get("status") == "pass" else 1


def _build_command(args: argparse.Namespace) -> int:
    del args
    return _emit(build_gate())


def _test_command(args: argparse.Namespace) -> int:
    del args
    return _emit(test_gate())


def _contract_gate_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return contract_gate(
        manifest_path=Path(args.manifest_path),
        coordination_path=Path(args.coordination_path),
        workspace_root=Path(args.workspace_root) if args.workspace_root else None,
        default_ref=args.default_ref,
        user_profile=Path(args.user_profile) if args.user_profile else None,
        skip_projection=args.skip_projection,
        skip_targets=args.skip_targets,
    )


def _contract_command(args: argparse.Namespace) -> int:
    return _emit(_contract_gate_from_args(args))


def _hotspot_command(args: argparse.Namespace) -> int:
    del args
    return _emit(hotspot_gate())


def verify_gates(args: argparse.Namespace) -> dict[str, Any]:
    gates: list[dict[str, Any]] = []
    for gate in (
        build_gate,
        test_gate,
        lambda: _contract_gate_from_args(args),
        hotspot_gate,
    ):
        result = gate()
        gates.append(result)
        if result["status"] != "pass":
            return {
                "status": "fail",
                "fixed_order": ["build", "test", "contract", "hotspot"],
                "gates": gates,
                "stopped_after": result["gate"],
            }
    return {
        "status": "pass",
        "fixed_order": ["build", "test", "contract", "hotspot"],
        "gates": gates,
        "stopped_after": None,
    }


def _verify_command(args: argparse.Namespace) -> int:
    return _emit(verify_gates(args))


def _audit_command(args: argparse.Namespace) -> int:
    git_ref = args.default_ref if args.state == "default" else None
    result = _run_json_script(
        "verify-target-project-rules.py",
        _target_arguments(
            Path(args.coordination_path),
            Path(args.workspace_root) if args.workspace_root else None,
            git_ref,
        ),
    )
    return _emit(result)


def _sync_command(args: argparse.Namespace) -> int:
    assembly = _run_json_script(
        "build-global-rules.py",
        ["--manifest-path", str(DEFAULT_SOURCE_MANIFEST), "--check"],
    )
    if assembly.get("status") != "pass":
        assembly["reason"] = "canonical source drift must be resolved before projection"
        return _emit(assembly)
    arguments = [
        "--manifest-path",
        args.manifest_path,
        "--scope",
        "All",
    ]
    if args.user_profile:
        arguments.extend(["--user-profile", args.user_profile])
    if args.apply:
        arguments.append("--apply")
    if args.check:
        arguments.append("--fail-on-change")
    return _emit(_run_json_script("sync-agent-rules.py", arguments))


def _matrix_command(args: argparse.Namespace) -> int:
    return _emit(
        _run_json_script(
            "export-target-rule-ci-matrix.py",
            ["--coordination-path", args.coordination_path],
        )
    )


def _add_contract_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--coordination-path", default=str(DEFAULT_COORDINATION))
    parser.add_argument("--workspace-root", default=None)
    parser.add_argument("--default-ref", default="origin/main")
    parser.add_argument("--user-profile", default=None)
    parser.add_argument("--skip-projection", action="store_true")
    parser.add_argument("--skip-targets", action="store_true")


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

    build = subparsers.add_parser("build", help="Compile the retained rule toolchain.")
    build.set_defaults(handler=_build_command)

    test = subparsers.add_parser("test", help="Run focused rule-governance tests.")
    test.set_defaults(handler=_test_command)

    contract = subparsers.add_parser(
        "contract", help="Verify global sources, projection, targets, and CI matrix."
    )
    _add_contract_arguments(contract)
    contract.set_defaults(handler=_contract_command)

    hotspot = subparsers.add_parser(
        "hotspot", help="Reject tracked runtime, Gemini, UI, and orchestration surfaces."
    )
    hotspot.set_defaults(handler=_hotspot_command)

    verify = subparsers.add_parser(
        "verify", help="Run build, test, contract, and hotspot in fixed order."
    )
    _add_contract_arguments(verify)
    verify.set_defaults(handler=_verify_command)

    audit = subparsers.add_parser("audit", help="Audit target rule contracts.")
    audit.add_argument("--coordination-path", default=str(DEFAULT_COORDINATION))
    audit.add_argument("--workspace-root", default=None)
    audit.add_argument("--state", choices=("default", "workspace"), default="default")
    audit.add_argument("--default-ref", default="origin/main")
    audit.set_defaults(handler=_audit_command)

    sync = subparsers.add_parser("sync", help="Dry-run or apply protected global sync.")
    sync.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST))
    sync.add_argument("--user-profile", default=None)
    sync.add_argument("--apply", action="store_true")
    sync.add_argument("--check", action="store_true")
    sync.set_defaults(handler=_sync_command)

    matrix = subparsers.add_parser("matrix", help="Export the target CI matrix.")
    matrix.add_argument("--coordination-path", default=str(DEFAULT_COORDINATION))
    matrix.set_defaults(handler=_matrix_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
