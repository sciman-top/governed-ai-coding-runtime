#!/usr/bin/env python3
"""Verify sensitive governance changes have pre-change review evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SENSITIVE_PREFIXES = (
    "rules/",
    ".github/workflows/",
)
SENSITIVE_EXACT = {
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".governed-ai/repo-profile.json",
    "docs/targets/target-repo-governance-baseline.json",
    "docs/targets/target-repos-catalog.json",
    "scripts/sync-agent-rules.py",
    "scripts/sync-agent-rules.ps1",
    "scripts/apply-target-repo-governance.py",
    "scripts/runtime-flow-preset.ps1",
    "scripts/verify-target-repo-governance-consistency.py",
    "scripts/verify-repo.ps1",
    "scripts/verify-pre-change-review.py",
}
SENSITIVE_NAME_PARTS = (
    "gate",
    "baseline",
    "profile",
)
REQUIRED_EVIDENCE_TOKENS = (
    "pre_change_review",
    "control_repo_manifest_and_rule_sources",
    "user_level_deployed_rule_files",
    "target_repo_deployed_rule_files",
    "target_repo_gate_scripts_and_ci",
    "target_repo_repo_profile",
    "target_repo_readme_and_operator_docs",
    "current_official_tool_loading_docs",
    "drift-integration decision",
)


def _run_git(args: list[str], *, repo_root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def _changed_paths(repo_root: Path) -> list[str]:
    paths: set[str] = set()
    paths.update(_run_git(["diff", "--name-only", "HEAD", "--"], repo_root=repo_root))
    paths.update(_run_git(["ls-files", "--others", "--exclude-standard"], repo_root=repo_root))
    return sorted(paths)


def _is_evidence_path(path: str) -> bool:
    return (
        path.startswith("docs/change-evidence/")
        and path.endswith(".md")
        and "/rule-sync-backups/" not in path
        and "/snapshots/" not in path
    )


def _is_sensitive_path(path: str) -> bool:
    if _is_evidence_path(path):
        return False
    if path in SENSITIVE_EXACT:
        return True
    if any(path.startswith(prefix) for prefix in SENSITIVE_PREFIXES):
        return True
    lowered = path.lower()
    if lowered.startswith(("scripts/", "docs/targets/", ".governed-ai/")):
        return any(part in lowered for part in SENSITIVE_NAME_PARTS)
    return False


def _evidence_files(paths: list[str], repo_root: Path) -> list[Path]:
    return [repo_root / path for path in paths if _is_evidence_path(path)]


def _find_matching_evidence(evidence_paths: list[Path]) -> Path | None:
    for path in sorted(evidence_paths):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if all(token in text for token in REQUIRED_EVIDENCE_TOKENS):
            return path
    return None


def verify(repo_root: Path) -> tuple[int, dict[str, object]]:
    changed = _changed_paths(repo_root)
    sensitive = [path for path in changed if _is_sensitive_path(path)]
    evidence = _evidence_files(changed, repo_root)
    matching = _find_matching_evidence(evidence)

    payload: dict[str, object] = {
        "status": "pass",
        "changed_paths": changed,
        "sensitive_paths": sensitive,
        "evidence_candidates": [str(path.relative_to(repo_root)).replace("\\", "/") for path in evidence],
        "required_tokens": list(REQUIRED_EVIDENCE_TOKENS),
    }
    if not sensitive:
        payload["reason"] = "no_sensitive_pre_change_review_paths"
        return 0, payload
    if matching is None:
        payload["status"] = "fail"
        payload["reason"] = "missing_pre_change_review_evidence"
        return 1, payload

    payload["matched_evidence"] = str(matching.relative_to(repo_root)).replace("\\", "/")
    return 0, payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(ROOT))
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve(strict=False)
    try:
        exit_code, payload = verify(repo_root)
    except Exception as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
