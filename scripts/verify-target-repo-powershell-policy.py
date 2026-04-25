from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG_PATH = ROOT / "docs" / "targets" / "target-repos-catalog.json"
DEFAULT_CODE_ROOT = ROOT.parent
DEFAULT_RUNTIME_STATE_BASE = DEFAULT_CODE_ROOT / "governed-ai-runtime-state"

DIRECT_WINDOWS_POWERSHELL_PATTERNS = (
    re.compile(r"(^|\s)&\s*powershell(?:\.exe)?\b", re.IGNORECASE),
    re.compile(r"\bpowershell(?:\.exe)?\s+-(NoProfile|ExecutionPolicy|File|Command)\b", re.IGNORECASE),
    re.compile(r"shell\s*:\s*powershell\b", re.IGNORECASE),
    re.compile(r"^-\s*powershell\s*:", re.IGNORECASE),
    re.compile(r"FilePath\s*=\s*['\"]powershell\.exe['\"]", re.IGNORECASE),
)
TEXT_SUFFIXES = {".ps1", ".psm1", ".cmd", ".bat", ".yml", ".yaml"}
SKIP_PARTS = {
    ".git",
    ".runtime",
    ".worktrees",
    "artifacts",
    "bin",
    "imports",
    "node_modules",
    "obj",
    "packages",
}


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json object required: {path}")
    return data


def _resolve_template_path(raw: str, repo_root: Path, code_root: Path, runtime_state_base: Path) -> Path:
    value = (
        raw.replace("${repo_root}", str(repo_root))
        .replace("${code_root}", str(code_root))
        .replace("${runtime_state_base}", str(runtime_state_base))
    )
    return Path(value).resolve(strict=False)


def _iter_policy_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(repo_root)
        if any(part in SKIP_PARTS for part in relative.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        files.append(path)
    return files


def _line_is_comment(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("rem ")


def _scan_repo(target: str, repo_root: Path) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for path in _iter_policy_files(repo_root):
        relative = path.relative_to(repo_root)
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if _line_is_comment(line):
                continue
            if any(pattern.search(line) for pattern in DIRECT_WINDOWS_POWERSHELL_PATTERNS):
                violations.append(
                    {
                        "target": target,
                        "path": str(relative).replace("\\", "/"),
                        "line": str(line_number),
                        "text": line.strip(),
                    }
                )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify target repos prefer pwsh instead of direct Windows PowerShell 5.1 invocation."
    )
    parser.add_argument("--catalog-path", default=str(DEFAULT_CATALOG_PATH))
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--code-root", default=str(DEFAULT_CODE_ROOT))
    parser.add_argument("--runtime-state-base", default=str(DEFAULT_RUNTIME_STATE_BASE))
    args = parser.parse_args()

    catalog_path = Path(args.catalog_path).resolve(strict=False)
    repo_root = Path(args.repo_root).resolve(strict=False)
    code_root = Path(args.code_root).resolve(strict=False)
    runtime_state_base = Path(args.runtime_state_base).resolve(strict=False)

    catalog = _load_json(catalog_path)
    targets = catalog.get("targets")
    if not isinstance(targets, dict):
        raise SystemExit("catalog.targets must be an object")

    checked: list[str] = []
    skipped: list[str] = []
    violations: list[dict[str, str]] = []
    for target, config in targets.items():
        if not isinstance(config, dict):
            continue
        attachment_root_raw = config.get("attachment_root")
        if not isinstance(attachment_root_raw, str) or not attachment_root_raw.strip():
            continue
        attachment_root = _resolve_template_path(attachment_root_raw, repo_root, code_root, runtime_state_base)
        if not attachment_root.exists():
            skipped.append(target)
            continue
        checked.append(target)
        violations.extend(_scan_repo(target, attachment_root))

    output = {
        "status": "pass" if not violations else "fail",
        "catalog_path": str(catalog_path),
        "checked_targets": checked,
        "skipped_targets": skipped,
        "violation_count": len(violations),
        "violations": violations,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
