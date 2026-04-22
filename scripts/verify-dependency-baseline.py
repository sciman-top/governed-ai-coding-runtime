from __future__ import annotations

import argparse
import ast
import json
import shutil
import sys
import sysconfig
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that declared dependency baselines match actual imports and runtime tooling."
    )
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--baseline", default=str(ROOT / "docs" / "dependency-baseline.json"))
    parser.add_argument("--target-repo-root")
    parser.add_argument("--require-target-repo-baseline", action="store_true")
    args = parser.parse_args()

    target_repo_root = Path(args.target_repo_root) if args.target_repo_root else None
    if args.require_target_repo_baseline and target_repo_root is None:
        print("--require-target-repo-baseline requires --target-repo-root", file=sys.stderr)
        return 1

    try:
        result = assert_dependency_baseline(
            repo_root=Path(args.repo_root),
            baseline_path=Path(args.baseline),
            target_repo_root=target_repo_root,
            require_target_repo_baseline=bool(args.require_target_repo_baseline),
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def assert_dependency_baseline(
    *,
    repo_root: Path,
    baseline_path: Path,
    target_repo_root: Path | None = None,
    require_target_repo_baseline: bool = False,
) -> dict:
    result = inspect_dependency_baseline(
        repo_root=repo_root,
        baseline_path=baseline_path,
        target_repo_root=target_repo_root,
        require_target_repo_baseline=require_target_repo_baseline,
    )
    if result["undeclared_imports"]:
        undeclared = ", ".join(
            f"{path}: {', '.join(modules)}" for path, modules in sorted(result["undeclared_imports"].items())
        )
        msg = f"undeclared external modules detected: {undeclared}"
        raise ValueError(msg)
    if result["missing_required_tools"]:
        missing_tools = ", ".join(sorted(result["missing_required_tools"]))
        msg = f"required host tools are missing: {missing_tools}"
        raise ValueError(msg)
    target_repo_status = result["target_repo_baseline"]
    if require_target_repo_baseline and not bool(target_repo_status.get("present")):
        msg = "target_repo_dependency_baseline is required but missing"
        raise ValueError(msg)
    return result


def inspect_dependency_baseline(
    *,
    repo_root: Path,
    baseline_path: Path,
    target_repo_root: Path | None = None,
    require_target_repo_baseline: bool = False,
) -> dict:
    baseline = load_dependency_baseline(baseline_path)
    observed_imports = scan_python_import_roots(repo_root=repo_root, scan_roots=baseline["scan_roots"])
    stdlib_modules = _stdlib_modules()
    undeclared_imports: dict[str, list[str]] = {}
    observed_external_modules = set()

    for path, module_roots in observed_imports.items():
        unknown = [
            module_root
            for module_root in module_roots
            if module_root not in stdlib_modules
            and module_root not in baseline["allowed_local_modules"]
            and module_root not in baseline["allowed_external_modules"]
        ]
        if unknown:
            undeclared_imports[path] = unknown
        for module_root in module_roots:
            if module_root in baseline["allowed_external_modules"]:
                observed_external_modules.add(module_root)

    host_tooling_status = inspect_host_tooling(baseline["host_tooling"])
    missing_required_tools = sorted(
        status["name"]
        for status in host_tooling_status
        if bool(status["required"]) and not bool(status["found"])
    )
    target_repo_status = inspect_target_repo_baseline(
        target_repo_root=target_repo_root,
        expected_paths=baseline["target_repo_baseline_paths"],
        required=require_target_repo_baseline,
    )

    overall_status = "pass"
    if undeclared_imports or missing_required_tools:
        overall_status = "fail"
    elif require_target_repo_baseline and not bool(target_repo_status.get("present")):
        overall_status = "fail"

    return {
        "status": overall_status,
        "baseline_path": baseline_path.resolve(strict=False).as_posix(),
        "scan_roots": baseline["scan_roots"],
        "allowed_local_modules": sorted(baseline["allowed_local_modules"]),
        "allowed_external_modules": sorted(baseline["allowed_external_modules"]),
        "observed_external_modules": sorted(observed_external_modules),
        "observed_import_roots": sorted({name for names in observed_imports.values() for name in names}),
        "undeclared_imports": undeclared_imports,
        "host_tooling": host_tooling_status,
        "missing_required_tools": missing_required_tools,
        "target_repo_baseline": target_repo_status,
    }


def load_dependency_baseline(baseline_path: Path) -> dict:
    payload = _load_json_object(baseline_path, "dependency baseline")
    python_block = payload.get("python")
    if not isinstance(python_block, dict):
        raise ValueError("dependency baseline must define a python object")

    scan_roots = _normalize_relative_paths(
        _required_string_list(python_block.get("scan_roots"), "python.scan_roots"),
        field_name="python.scan_roots",
    )
    allowed_local_modules = _optional_string_list(
        python_block.get("allowed_local_modules"),
        "python.allowed_local_modules",
    )
    allowed_external_modules = _optional_string_list(
        python_block.get("allowed_external_modules"),
        "python.allowed_external_modules",
    )
    host_tooling = _normalize_host_tooling(payload.get("host_tooling"))
    target_repo_baseline_paths = _normalize_target_repo_baseline_paths(payload.get("target_repo"))
    return {
        "scan_roots": scan_roots,
        "allowed_local_modules": set(allowed_local_modules),
        "allowed_external_modules": set(allowed_external_modules),
        "host_tooling": host_tooling,
        "target_repo_baseline_paths": target_repo_baseline_paths,
    }


def scan_python_import_roots(*, repo_root: Path, scan_roots: list[str]) -> dict[str, list[str]]:
    observed: dict[str, list[str]] = {}
    for relative_root in scan_roots:
        root = repo_root / relative_root
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            try:
                module_roots = sorted(_imports_for_file(path))
            except ValueError as exc:
                relative_path = path.relative_to(repo_root).as_posix()
                raise ValueError(f"failed to parse imports in {relative_path}: {exc}") from exc
            if module_roots:
                observed[path.relative_to(repo_root).as_posix()] = module_roots
    return observed


def inspect_host_tooling(host_tooling: list[dict]) -> list[dict]:
    status_list: list[dict] = []
    for entry in host_tooling:
        name = entry["name"]
        required = bool(entry["required"])
        status_list.append(
            {
                "name": name,
                "required": required,
                "found": shutil.which(name) is not None,
            }
        )
    return status_list


def inspect_target_repo_baseline(
    *,
    target_repo_root: Path | None,
    expected_paths: list[str],
    required: bool,
) -> dict:
    if target_repo_root is None:
        return {
            "checked": False,
            "required": required,
            "target_repo_root": None,
            "expected_paths": expected_paths,
            "present": False,
            "matched_paths": [],
        }

    resolved_root = Path(target_repo_root).resolve(strict=False)
    matched_paths = [path for path in expected_paths if (resolved_root / path).exists()]
    return {
        "checked": True,
        "required": required,
        "target_repo_root": resolved_root.as_posix(),
        "expected_paths": expected_paths,
        "present": bool(matched_paths),
        "matched_paths": matched_paths,
    }


def _imports_for_file(path: Path) -> set[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"unable to read file ({exc})") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"file is not valid utf-8 ({exc})") from exc
    try:
        tree = ast.parse(source, filename=path.as_posix())
    except SyntaxError as exc:
        line = exc.lineno if isinstance(exc.lineno, int) else "unknown"
        raise ValueError(f"syntax error at line {line}") from exc
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.add(node.module.split(".", 1)[0])
    return imports


def _stdlib_modules() -> set[str]:
    stdlib = set(sys.builtin_module_names)
    stdlib.update(getattr(sys, "stdlib_module_names", ()))
    stdlib.add("__future__")
    if stdlib:
        return stdlib

    stdlib_root = Path(sysconfig.get_path("stdlib"))
    for path in stdlib_root.iterdir():
        name = path.stem if path.is_file() else path.name
        if name == "__pycache__":
            continue
        stdlib.add(name)
    return stdlib


def _required_string_list(value: object, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    normalized = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    if len(normalized) != len(value):
        raise ValueError(f"{field_name} must contain only non-empty strings")
    return normalized


def _optional_string_list(value: object, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided")
    normalized = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    if len(normalized) != len(value):
        raise ValueError(f"{field_name} must contain only non-empty strings")
    return normalized


def _normalize_host_tooling(value: object) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("host_tooling must be a list when provided")

    normalized: list[dict] = []
    for index, entry in enumerate(value):
        if not isinstance(entry, dict):
            raise ValueError(f"host_tooling[{index}] must be an object")
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"host_tooling[{index}].name must be a non-empty string")
        required = entry.get("required", False)
        if not isinstance(required, bool):
            raise ValueError(f"host_tooling[{index}].required must be a boolean")
        normalized.append({"name": name.strip(), "required": required})
    return normalized


def _normalize_target_repo_baseline_paths(value: object) -> list[str]:
    default_paths = ["docs/dependency-baseline.md", ".governed-ai/dependency-baseline.json"]
    if value is None:
        return default_paths
    if not isinstance(value, dict):
        raise ValueError("target_repo must be an object when provided")
    return _normalize_relative_paths(
        _required_string_list(value.get("baseline_paths"), "target_repo.baseline_paths"),
        field_name="target_repo.baseline_paths",
    )


def _normalize_relative_paths(values: list[str], *, field_name: str) -> list[str]:
    normalized: list[str] = []
    for index, value in enumerate(values):
        candidate = value.replace("\\", "/").strip()
        path = PurePosixPath(candidate)
        if path.is_absolute() or ".." in path.parts or ":" in candidate:
            raise ValueError(f"{field_name}[{index}] must stay repo-relative")
        normalized.append(path.as_posix())
    return normalized


def _load_json_object(path: Path, field_name: str) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"{field_name} file is not readable: {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field_name} file is not valid JSON: {path} ({exc.msg})") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{field_name} must be a JSON object")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
