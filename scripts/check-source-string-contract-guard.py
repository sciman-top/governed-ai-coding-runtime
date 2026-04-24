from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SOURCE_ASSERTION_MARKERS = (
    "source.Should().Contain(",
    "source.Should().NotContain(",
)
NAMESPACE_FILE_SCOPED_PATTERN = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;\s*$", re.MULTILINE)
NAMESPACE_BLOCK_PATTERN = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*(?:\{|$)", re.MULTILINE)
CLASS_PATTERN = re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\b")


@dataclass(frozen=True, slots=True)
class SourceStringContractClass:
    file: str
    fqcn: str


def _resolve_root(value: str) -> Path:
    path = Path(value).resolve(strict=False)
    if not path.exists() or not path.is_dir():
        msg = f"target repo root does not exist: {path}"
        raise ValueError(msg)
    return path


def _extract_namespace(source: str) -> str:
    file_scoped_match = NAMESPACE_FILE_SCOPED_PATTERN.search(source)
    if file_scoped_match:
        return file_scoped_match.group(1)
    block_match = NAMESPACE_BLOCK_PATTERN.search(source)
    if block_match:
        return block_match.group(1)
    return ""


def _extract_class_names(source: str) -> list[str]:
    class_names = []
    for match in CLASS_PATTERN.finditer(source):
        name = match.group(1)
        if name.endswith("ContractTests"):
            class_names.append(name)
    return class_names


def discover_source_string_contract_classes(target_repo_root: Path) -> list[SourceStringContractClass]:
    tests_root = target_repo_root / "tests"
    if not tests_root.exists() or not tests_root.is_dir():
        return []

    discovered: list[SourceStringContractClass] = []
    for source_file in sorted(tests_root.rglob("*ContractTests.cs")):
        source = source_file.read_text(encoding="utf-8", errors="ignore")
        if not any(marker in source for marker in SOURCE_ASSERTION_MARKERS):
            continue
        namespace = _extract_namespace(source)
        class_names = _extract_class_names(source)
        for class_name in class_names:
            fqcn = f"{namespace}.{class_name}" if namespace else class_name
            discovered.append(
                SourceStringContractClass(
                    file=str(source_file.resolve(strict=False)),
                    fqcn=fqcn,
                )
            )

    # Deduplicate while preserving deterministic order.
    unique: list[SourceStringContractClass] = []
    seen = set()
    for item in discovered:
        key = (item.file, item.fqcn)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def resolve_test_project(target_repo_root: Path, explicit_project: str | None) -> Path | None:
    if explicit_project:
        candidate = Path(explicit_project)
        if not candidate.is_absolute():
            candidate = target_repo_root / candidate
        candidate = candidate.resolve(strict=False)
        if not candidate.exists():
            msg = f"test project does not exist: {candidate}"
            raise ValueError(msg)
        return candidate

    tests_root = target_repo_root / "tests"
    if not tests_root.exists() or not tests_root.is_dir():
        return None

    projects = sorted(tests_root.rglob("*.csproj"))
    if not projects:
        return None
    if len(projects) == 1:
        return projects[0]

    def score(path: Path) -> tuple[int, int, str]:
        name = path.name.lower()
        looks_like_tests = "test" in name
        return (0 if looks_like_tests else 1, len(path.parts), str(path).lower())

    return sorted(projects, key=score)[0]


def _chunk(values: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def run_source_string_contract_guard(
    *,
    target_repo_root: Path,
    dotnet_command: str,
    configuration: str,
    test_project: Path | None,
    classes: list[SourceStringContractClass],
) -> dict:
    class_names = [item.fqcn for item in classes]
    if not class_names:
        return {
            "status": "skip",
            "reason": "no_source_string_contract_tests_detected",
            "target_repo_root": str(target_repo_root),
            "test_project": str(test_project) if test_project else None,
            "detected_classes": [],
            "detected_files": [],
            "executed_batches": [],
            "failed_classes": [],
        }

    if test_project is None:
        return {
            "status": "fail",
            "reason": "source_string_contract_tests_detected_but_no_test_project_found",
            "target_repo_root": str(target_repo_root),
            "test_project": None,
            "detected_classes": class_names,
            "detected_files": sorted({item.file for item in classes}),
            "executed_batches": [],
            "failed_classes": class_names,
        }

    failed_classes: list[str] = []
    executed_batches: list[dict] = []
    for batch in _chunk(class_names, 20):
        filter_expr = "|".join(f"FullyQualifiedName~{name}" for name in batch)
        command = [
            dotnet_command,
            "test",
            str(test_project),
            "-c",
            configuration,
            "-m:1",
            "--filter",
            filter_expr,
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=target_repo_root,
                env=_subprocess_environment(),
            )
        except FileNotFoundError:
            return {
                "status": "fail",
                "reason": f"dotnet_command_not_found:{dotnet_command}",
                "target_repo_root": str(target_repo_root),
                "test_project": str(test_project),
                "detected_classes": class_names,
                "detected_files": sorted({item.file for item in classes}),
                "executed_batches": executed_batches,
                "failed_classes": class_names,
            }

        executed_batches.append(
            {
                "filter": filter_expr,
                "class_count": len(batch),
                "exit_code": int(completed.returncode),
            }
        )
        if completed.returncode != 0:
            failed_classes.extend(batch)

    return {
        "status": "pass" if not failed_classes else "fail",
        "reason": "all_source_string_contract_tests_passed" if not failed_classes else "source_string_contract_tests_failed",
        "target_repo_root": str(target_repo_root),
        "test_project": str(test_project),
        "detected_classes": class_names,
        "detected_files": sorted({item.file for item in classes}),
        "executed_batches": executed_batches,
        "failed_classes": failed_classes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run source-string contract tests for an attached target repository.")
    parser.add_argument("--target-repo-root", required=True)
    parser.add_argument("--test-project")
    parser.add_argument("--dotnet-command", default="dotnet")
    parser.add_argument("--configuration", default="Debug")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        target_repo_root = _resolve_root(args.target_repo_root)
        classes = discover_source_string_contract_classes(target_repo_root)
        test_project = resolve_test_project(target_repo_root, args.test_project)
        payload = run_source_string_contract_guard(
            target_repo_root=target_repo_root,
            dotnet_command=args.dotnet_command,
            configuration=args.configuration,
            test_project=test_project,
            classes=classes,
        )
    except ValueError as exc:
        payload = {
            "status": "fail",
            "reason": str(exc),
        }

    status = str(payload.get("status", "fail")).lower()
    exit_code = 0 if status in {"pass", "skip"} else 1

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"[source-string-contract-guard] {status.upper()}")
        reason = payload.get("reason")
        if reason:
            print(f"[source-string-contract-guard] reason={reason}")
        if payload.get("test_project"):
            print(f"[source-string-contract-guard] test_project={payload['test_project']}")
        if payload.get("failed_classes"):
            for class_name in payload["failed_classes"]:
                print(f"[source-string-contract-guard] failed={class_name}")
    return exit_code


def _subprocess_environment() -> dict[str, str]:
    env = os.environ.copy()
    if os.name != "nt":
        return env

    windows_root = env.get("SystemRoot") or env.get("WINDIR") or r"C:\Windows"
    if windows_root and "SystemRoot" not in env:
        env["SystemRoot"] = windows_root
    if windows_root and "WINDIR" not in env:
        env["WINDIR"] = windows_root
    if "ComSpec" not in env:
        cmd_path = str(Path(windows_root) / "System32" / "cmd.exe")
        if Path(cmd_path).exists():
            env["ComSpec"] = cmd_path
    if "SystemDrive" not in env:
        env["SystemDrive"] = Path(windows_root).drive or "C:"
    return env


if __name__ == "__main__":
    raise SystemExit(main())
