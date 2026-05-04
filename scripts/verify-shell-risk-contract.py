from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = ("packages", "scripts")
PYTHON_SUFFIXES = {".py"}
POWERSHELL_SUFFIXES = {".ps1", ".psm1"}
SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".runtime",
    "__pycache__",
    "bin",
    "node_modules",
    "obj",
}
POWERSHELL_RISK_PATTERNS = (
    ("powershell_remove_item", re.compile(r"(^|[;{])\s*Remove-Item\b", re.IGNORECASE)),
    ("powershell_move_item", re.compile(r"(^|[;{])\s*Move-Item\b", re.IGNORECASE)),
    ("powershell_start_process", re.compile(r"(^|[;{])\s*(?:\$\w+\s*=\s*)?Start-Process\b", re.IGNORECASE)),
)
START_PROCESS_BOUNDING_MARKERS = (
    "-WindowStyle Hidden",
    "-NoNewWindow",
    "-PassThru",
    "-Wait",
    "RedirectStandardOutput",
    "RedirectStandardError",
    ".WaitForExit(",
)


ALLOWLIST = (
    {
        "kind": "python_shell_true",
        "path": "packages/contracts/src/governed_ai_coding_runtime_contracts/subprocess_guard.py",
        "line_contains": "shell=True",
        "expected_count": 1,
        "reason": "central governed gate command runner preserves existing shell-style gate contracts and applies timeout handling",
    },
    {
        "kind": "python_shell_true",
        "path": "packages/contracts/src/governed_ai_coding_runtime_contracts/tool_runner.py",
        "line_contains": "shell=True",
        "expected_count": 1,
        "reason": "governed tool execution normalizes timeout policy before invoking the configured command string",
    },
    {
        "kind": "powershell_remove_item",
        "path": "scripts/codex-account.ps1",
        "line_contains": "Remove-Item -LiteralPath $candidate.FullName -Force",
        "expected_count": 1,
        "reason": "auth snapshot deletion is guarded by active-profile checks, home-root containment, backup, and ShouldProcess",
    },
    {
        "kind": "powershell_remove_item",
        "path": "scripts/git-acl-guard.ps1",
        "line_contains": "Remove-Item -LiteralPath $indexLock -Force",
        "expected_count": 1,
        "reason": "git index lock cleanup is scoped to the detected lock file and uses LiteralPath",
    },
    {
        "kind": "powershell_remove_item",
        "path": "scripts/github/create-roadmap-issues.ps1",
        "line_contains": "Remove-Item $tmp -ErrorAction SilentlyContinue",
        "expected_count": 1,
        "reason": "GitHub issue body cleanup removes a temporary file created for the current command",
    },
    {
        "kind": "powershell_remove_item",
        "path": "scripts/operator-ui-service.ps1",
        "line_contains": "Remove-Item -LiteralPath $PidPath -ErrorAction SilentlyContinue",
        "expected_count": 1,
        "reason": "operator UI service cleanup removes only the managed runtime pid file",
    },
    {
        "kind": "powershell_start_process",
        "path": "scripts/operator-ui-service.ps1",
        "line_contains": "Start-Process $Url | Out-Null",
        "expected_count": 3,
        "reason": "operator UI browser launch is user-facing by design and only opens the computed local UI URL",
    },
    {
        "kind": "powershell_remove_item",
        "path": "scripts/governance/gate-runner-common.ps1",
        "line_contains": "Remove-Item -LiteralPath $stdoutPath -ErrorAction SilentlyContinue",
        "expected_count": 1,
        "reason": "gate runner deletes temporary stdout capture files after bounded process execution",
    },
    {
        "kind": "powershell_remove_item",
        "path": "scripts/governance/gate-runner-common.ps1",
        "line_contains": "Remove-Item -LiteralPath $stderrPath -ErrorAction SilentlyContinue",
        "expected_count": 1,
        "reason": "gate runner deletes temporary stderr capture files after bounded process execution",
    },
    {
        "kind": "powershell_remove_item",
        "path": "scripts/package-runtime.ps1",
        "line_contains": "Remove-Item -Recurse -Force $distRoot",
        "expected_count": 1,
        "reason": "package refresh deletes only the resolved .runtime/dist/public-usable-release output tree before rebuilding it",
    },
    {
        "kind": "powershell_remove_item",
        "path": "scripts/runtime-flow-preset.ps1",
        "line_contains": "Remove-Item -LiteralPath $stdoutPath -ErrorAction SilentlyContinue",
        "expected_count": 1,
        "reason": "runtime command runner deletes temporary stdout capture files after bounded process execution",
    },
    {
        "kind": "powershell_remove_item",
        "path": "scripts/runtime-flow-preset.ps1",
        "line_contains": "Remove-Item -LiteralPath $stderrPath -ErrorAction SilentlyContinue",
        "expected_count": 1,
        "reason": "runtime command runner deletes temporary stderr capture files after bounded process execution",
    },
    {
        "kind": "powershell_remove_item",
        "path": "scripts/runtime-flow-preset.ps1",
        "line_contains": "Remove-Item -LiteralPath $entry.stdout_path -ErrorAction SilentlyContinue",
        "expected_count": 2,
        "reason": "parallel runtime flow deletes per-target temporary stdout capture files after process completion or timeout",
    },
    {
        "kind": "powershell_remove_item",
        "path": "scripts/runtime-flow-preset.ps1",
        "line_contains": "Remove-Item -LiteralPath $entry.stderr_path -ErrorAction SilentlyContinue",
        "expected_count": 2,
        "reason": "parallel runtime flow deletes per-target temporary stderr capture files after process completion or timeout",
    },
)


@dataclass(frozen=True, slots=True)
class Finding:
    kind: str
    path: str
    line: int
    text: str
    reason: str

    def to_json(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "path": self.path,
            "line": self.line,
            "text": self.text,
            "reason": self.reason,
        }


def _normalize_repo_path(path: Path, repo_root: Path) -> str:
    return str(path.resolve(strict=False).relative_to(repo_root.resolve(strict=False))).replace("\\", "/")


def _iter_scan_files(repo_root: Path) -> Iterable[Path]:
    for scan_root_name in SCAN_ROOTS:
        scan_root = repo_root / scan_root_name
        if not scan_root.exists():
            continue
        for path in sorted(scan_root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(repo_root)
            if any(part in SKIP_PARTS for part in relative.parts):
                continue
            if path.suffix.lower() not in PYTHON_SUFFIXES | POWERSHELL_SUFFIXES:
                continue
            yield path


def _source_line(lines: list[str], line_number: int) -> str:
    if line_number < 1 or line_number > len(lines):
        return ""
    return lines[line_number - 1].strip()


def _python_findings(path: Path, repo_root: Path) -> list[Finding]:
    relative_path = _normalize_repo_path(path, repo_root)
    source = path.read_text(encoding="utf-8", errors="ignore")
    lines = source.splitlines()
    try:
        tree = ast.parse(source, filename=relative_path)
    except SyntaxError as exc:
        return [
            Finding(
                kind="python_syntax_error",
                path=relative_path,
                line=exc.lineno or 1,
                text=exc.msg,
                reason="Python source could not be parsed before shell-risk inspection",
            )
        ]

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg != "shell":
                continue
            if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                findings.append(
                    Finding(
                        kind="python_shell_true",
                        path=relative_path,
                        line=keyword.value.lineno,
                        text=_source_line(lines, keyword.value.lineno),
                        reason="shell=True must be explicitly governed or removed",
                    )
                )
    return findings


def _powershell_findings(path: Path, repo_root: Path) -> list[Finding]:
    relative_path = _normalize_repo_path(path, repo_root)
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    findings: list[Finding] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for kind, pattern in POWERSHELL_RISK_PATTERNS:
            if not pattern.search(line):
                continue
            if kind == "powershell_start_process" and _is_bounded_start_process(lines, index):
                continue
            findings.append(
                Finding(
                    kind=kind,
                    path=relative_path,
                    line=index + 1,
                    text=stripped,
                    reason=_powershell_reason(kind),
                )
            )
    return findings


def _is_bounded_start_process(lines: list[str], index: int) -> bool:
    line = lines[index].strip()
    if re.search(r"\bStart-Process\s+@\w+", line, re.IGNORECASE):
        start = max(0, index - 14)
        context = "\n".join(lines[start : index + 1])
        return any(marker in context for marker in START_PROCESS_BOUNDING_MARKERS)

    block = [lines[index]]
    cursor = index
    while block[-1].rstrip().endswith("`") and cursor + 1 < len(lines) and len(block) < 14:
        cursor += 1
        block.append(lines[cursor])
    context = "\n".join(block)
    return any(marker in context for marker in START_PROCESS_BOUNDING_MARKERS)


def _powershell_reason(kind: str) -> str:
    if kind == "powershell_start_process":
        return "Start-Process must be bounded by hidden/no-new-window, timeout/wait, or an explicit user-facing allowlist"
    if kind == "powershell_move_item":
        return "Move-Item is a destructive filesystem operation and must be explicitly scoped"
    return "Remove-Item is a destructive filesystem operation and must be explicitly scoped"


def collect_findings(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _iter_scan_files(repo_root):
        suffix = path.suffix.lower()
        if suffix in PYTHON_SUFFIXES:
            findings.extend(_python_findings(path, repo_root))
        elif suffix in POWERSHELL_SUFFIXES:
            findings.extend(_powershell_findings(path, repo_root))
    return sorted(findings, key=lambda item: (item.path, item.line, item.kind))


def _allowlist_key(entry: dict[str, object]) -> tuple[str, str, str]:
    return (
        str(entry["kind"]),
        str(entry["path"]).replace("\\", "/"),
        str(entry["line_contains"]),
    )


def apply_allowlist(
    findings: list[Finding],
    *,
    enforce_expected_counts: bool,
) -> tuple[list[Finding], list[dict[str, object]], list[dict[str, object]]]:
    allowlist_counts = {_allowlist_key(entry): 0 for entry in ALLOWLIST}
    remaining: list[Finding] = []
    for finding in findings:
        matched_key = None
        for entry in ALLOWLIST:
            key = _allowlist_key(entry)
            if finding.kind == key[0] and finding.path == key[1] and key[2] in finding.text:
                matched_key = key
                break
        if matched_key is None:
            remaining.append(finding)
        else:
            allowlist_counts[matched_key] += 1

    allowlist_status: list[dict[str, object]] = []
    stale: list[dict[str, object]] = []
    for entry in ALLOWLIST:
        key = _allowlist_key(entry)
        actual_count = allowlist_counts[key]
        expected_count = int(entry.get("expected_count", 1))
        record = {
            "kind": key[0],
            "path": key[1],
            "line_contains": key[2],
            "expected_count": expected_count,
            "actual_count": actual_count,
            "reason": str(entry["reason"]),
        }
        allowlist_status.append(record)
        if enforce_expected_counts and actual_count != expected_count:
            stale.append(record)
    return remaining, allowlist_status, stale


def build_payload(repo_root: Path) -> dict[str, object]:
    findings = collect_findings(repo_root)
    enforce_allowlist_counts = repo_root.resolve(strict=False) == ROOT.resolve(strict=False)
    unapproved_findings, allowlist_status, stale_allowlist = apply_allowlist(
        findings,
        enforce_expected_counts=enforce_allowlist_counts,
    )
    checked_files = [_normalize_repo_path(path, repo_root) for path in _iter_scan_files(repo_root)]
    status = "pass" if not unapproved_findings and not stale_allowlist else "fail"
    return {
        "status": status,
        "repo_root": str(repo_root),
        "scan_roots": list(SCAN_ROOTS),
        "checked_file_count": len(checked_files),
        "finding_count": len(unapproved_findings),
        "findings": [finding.to_json() for finding in unapproved_findings],
        "allowlist_count": len(ALLOWLIST),
        "allowlist_expected_counts_enforced": enforce_allowlist_counts,
        "allowlist_status": allowlist_status,
        "stale_allowlist_count": len(stale_allowlist),
        "stale_allowlist": stale_allowlist,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify governed shell and destructive filesystem risks stay explicit.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve(strict=False)
    if not repo_root.exists() or not repo_root.is_dir():
        raise SystemExit(f"repo root does not exist: {repo_root}")

    payload = build_payload(repo_root)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        status = str(payload["status"]).upper()
        print(f"[shell-risk-contract] {status}")
        print(f"[shell-risk-contract] checked_file_count={payload['checked_file_count']}")
        print(f"[shell-risk-contract] finding_count={payload['finding_count']}")
        print(f"[shell-risk-contract] stale_allowlist_count={payload['stale_allowlist_count']}")
        for finding in payload["findings"]:
            print(
                "[shell-risk-contract] finding={path}:{line} {kind} {text}".format(
                    path=finding["path"],
                    line=finding["line"],
                    kind=finding["kind"],
                    text=finding["text"],
                )
            )
        for entry in payload["stale_allowlist"]:
            print(
                "[shell-risk-contract] stale_allowlist={path} {kind} expected={expected_count} actual={actual_count} contains={line_contains}".format(
                    **entry
                )
            )
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
