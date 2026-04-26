from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "docs" / "architecture" / "transition-stack-convergence-policy.json"
DEFAULT_SCAN_ROOTS = ["apps", "packages", "scripts", "tests"]
ACTIVE_IMPORT_STATUSES = {"active_boundary", "local_only"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify transition-stack dependency convergence policy.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    args = parser.parse_args()

    try:
        result = assert_transition_stack_convergence(repo_root=Path(args.repo_root), policy_path=Path(args.policy))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def assert_transition_stack_convergence(*, repo_root: Path, policy_path: Path) -> dict:
    result = inspect_transition_stack_convergence(repo_root=repo_root, policy_path=policy_path)
    failures = []
    if result["unmapped_observed_modules"]:
        failures.append("unmapped observed transition modules: " + ", ".join(result["unmapped_observed_modules"]))
    if result["inactive_observed_modules"]:
        failures.append(
            "observed transition modules without active boundary: "
            + ", ".join(
                f"{entry['module']}({entry['component_id']}:{entry['adoption_status']})"
                for entry in result["inactive_observed_modules"]
            )
        )
    if result["missing_refs"]:
        failures.append("missing policy refs: " + ", ".join(result["missing_refs"]))
    if result["wrapper_drift_tokens"]:
        failures.append("wrapper drift tokens found: " + ", ".join(result["wrapper_drift_tokens"]))
    if not result["runtime_guards"]["local_mode_allowed"]:
        failures.append("local filesystem/sqlite mode is not preserved")
    if not result["runtime_guards"]["json_schema_truth"]:
        failures.append("JSON Schema source-of-truth guard is not enabled")
    if not result["runtime_guards"]["postgres_requires_service_pressure"]:
        failures.append("PostgreSQL scope guard is not enabled")

    if failures:
        raise ValueError("; ".join(failures))
    return result


def inspect_transition_stack_convergence(*, repo_root: Path, policy_path: Path) -> dict:
    resolved_root = repo_root.resolve(strict=False)
    policy = _load_policy(policy_path)
    components = policy["components"]
    component_by_module = {
        module: component for component in components for module in component["module_roots"]
    }
    watched_modules = sorted(component_by_module)
    observed_imports = _scan_imports(repo_root=resolved_root, scan_roots=DEFAULT_SCAN_ROOTS)
    observed_modules = sorted(
        {module for modules in observed_imports.values() for module in modules if module in watched_modules}
    )
    unmapped_observed_modules = sorted(module for module in observed_modules if module not in component_by_module)
    inactive_observed_modules = []
    for module in observed_modules:
        component = component_by_module[module]
        status = component["adoption_status"]
        if status not in ACTIVE_IMPORT_STATUSES:
            inactive_observed_modules.append(
                {
                    "module": module,
                    "component_id": component["component_id"],
                    "adoption_status": status,
                }
            )

    missing_refs = _collect_missing_refs(resolved_root, policy)
    wrapper_drift_tokens = _find_wrapper_drift_tokens(resolved_root, policy["runtime_guards"]["wrapper_drift_guard"])
    runtime_guards = policy["runtime_guards"]
    local_mode = runtime_guards["local_mode"]
    postgres_scope = runtime_guards["postgres_scope"]

    return {
        "status": "pass",
        "policy_path": policy_path.resolve(strict=False).as_posix(),
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "watched_modules": watched_modules,
        "observed_modules": observed_modules,
        "observed_import_refs": {
            path: [module for module in modules if module in watched_modules]
            for path, modules in observed_imports.items()
            if any(module in watched_modules for module in modules)
        },
        "unmapped_observed_modules": unmapped_observed_modules,
        "inactive_observed_modules": inactive_observed_modules,
        "missing_refs": missing_refs,
        "wrapper_drift_tokens": wrapper_drift_tokens,
        "runtime_guards": {
            "local_mode_allowed": bool(local_mode["filesystem_allowed"]) and bool(local_mode["sqlite_allowed"]),
            "json_schema_truth": bool(runtime_guards["json_schema_truth"]),
            "postgres_requires_service_pressure": bool(postgres_scope["requires_service_metadata_pressure"])
            and bool(postgres_scope["requires_rollback"]),
            "cli_api_parity_tests": runtime_guards["cli_api_parity_tests"],
            "tracing_hook_refs": runtime_guards["tracing_hook_refs"],
        },
    }


def _load_policy(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"transition-stack policy is not readable: {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"transition-stack policy is invalid JSON: {path} ({exc.msg})") from exc
    if not isinstance(payload, dict):
        raise ValueError("transition-stack policy must be a JSON object")
    _require_string(payload, "policy_id")
    _require_string(payload, "status")
    if payload["status"] not in {"observe", "enforced", "waived"}:
        raise ValueError("transition-stack policy status is invalid")
    components = payload.get("components")
    if not isinstance(components, list) or not components:
        raise ValueError("transition-stack policy components must be a non-empty list")
    seen_modules: set[str] = set()
    for index, component in enumerate(components):
        if not isinstance(component, dict):
            raise ValueError(f"components[{index}] must be an object")
        for field in ("component_id", "adoption_status", "owner_boundary", "allowed_when", "rollback_ref"):
            _require_string(component, field, prefix=f"components[{index}]")
        if component["adoption_status"] not in {"not_present", "local_only", "active_boundary", "watch", "deferred"}:
            raise ValueError(f"components[{index}].adoption_status is invalid")
        modules = _require_string_list(component.get("module_roots"), f"components[{index}].module_roots")
        duplicate_modules = seen_modules.intersection(modules)
        if duplicate_modules:
            raise ValueError(f"duplicate transition-stack module roots: {', '.join(sorted(duplicate_modules))}")
        seen_modules.update(modules)
        _require_string_list(component.get("evidence_refs"), f"components[{index}].evidence_refs")
    _validate_runtime_guards(payload.get("runtime_guards"))
    _require_string_list(payload.get("evidence_refs"), "evidence_refs")
    _require_string(payload, "rollback_ref")
    return payload


def _validate_runtime_guards(value: object) -> None:
    if not isinstance(value, dict):
        raise ValueError("runtime_guards must be an object")
    local_mode = value.get("local_mode")
    if not isinstance(local_mode, dict):
        raise ValueError("runtime_guards.local_mode must be an object")
    for field in ("filesystem_allowed", "sqlite_allowed"):
        if not isinstance(local_mode.get(field), bool):
            raise ValueError(f"runtime_guards.local_mode.{field} must be boolean")
    postgres_scope = value.get("postgres_scope")
    if not isinstance(postgres_scope, dict):
        raise ValueError("runtime_guards.postgres_scope must be an object")
    for field in ("requires_service_metadata_pressure", "requires_rollback"):
        if not isinstance(postgres_scope.get(field), bool):
            raise ValueError(f"runtime_guards.postgres_scope.{field} must be boolean")
    if not isinstance(value.get("json_schema_truth"), bool):
        raise ValueError("runtime_guards.json_schema_truth must be boolean")
    _require_string(value, "pydantic_scope", prefix="runtime_guards")
    _require_string_list(value.get("cli_api_parity_tests"), "runtime_guards.cli_api_parity_tests")
    _require_string_list(value.get("tracing_hook_refs"), "runtime_guards.tracing_hook_refs")
    drift_guard = value.get("wrapper_drift_guard")
    if not isinstance(drift_guard, dict):
        raise ValueError("runtime_guards.wrapper_drift_guard must be an object")
    _require_string(drift_guard, "path", prefix="runtime_guards.wrapper_drift_guard")
    _require_string_list(
        drift_guard.get("forbidden_tokens"),
        "runtime_guards.wrapper_drift_guard.forbidden_tokens",
    )


def _scan_imports(*, repo_root: Path, scan_roots: list[str]) -> dict[str, list[str]]:
    observed: dict[str, list[str]] = {}
    for relative_root in scan_roots:
        root = repo_root / relative_root
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            modules = sorted(_imports_for_file(path))
            if modules:
                observed[path.relative_to(repo_root).as_posix()] = modules
    return observed


def _imports_for_file(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    except SyntaxError as exc:
        line = exc.lineno if isinstance(exc.lineno, int) else "unknown"
        raise ValueError(f"failed to parse imports in {path}: syntax error at line {line}") from exc
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module.split(".", 1)[0])
    return modules


def _collect_missing_refs(repo_root: Path, policy: dict) -> list[str]:
    refs = []
    refs.extend(policy.get("evidence_refs", []))
    for component in policy["components"]:
        refs.extend(component.get("implementation_refs", []))
        refs.extend(component["evidence_refs"])
    guards = policy["runtime_guards"]
    refs.extend(guards["cli_api_parity_tests"])
    refs.extend(guards["tracing_hook_refs"])
    refs.append(guards["wrapper_drift_guard"]["path"])
    missing = []
    for ref in sorted(set(refs)):
        if _looks_like_freeform_ref(ref):
            continue
        if not (repo_root / ref).exists():
            missing.append(ref)
    return missing


def _find_wrapper_drift_tokens(repo_root: Path, guard: dict) -> list[str]:
    path = repo_root / guard["path"]
    if not path.exists():
        return [f"missing:{guard['path']}"]
    text = path.read_text(encoding="utf-8")
    return [token for token in guard["forbidden_tokens"] if token in text]


def _looks_like_freeform_ref(value: str) -> bool:
    stripped = value.strip()
    if not stripped or " " in stripped or stripped.startswith("git "):
        return True
    path = PurePosixPath(stripped.replace("\\", "/"))
    return path.is_absolute() or ".." in path.parts or ":" in stripped


def _require_string(payload: dict, field: str, *, prefix: str | None = None) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        name = f"{prefix}.{field}" if prefix else field
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _require_string_list(value: object, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    normalized = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    if len(normalized) != len(value):
        raise ValueError(f"{field_name} must contain only non-empty strings")
    return normalized


if __name__ == "__main__":
    raise SystemExit(main())
