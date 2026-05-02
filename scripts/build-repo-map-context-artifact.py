from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STRATEGY_PATH = ROOT / ".governed-ai" / "repo-map-context-shaping.json"
DEFAULT_OUTPUT_PATH = ROOT / "docs" / "change-evidence" / "repo-map-context-artifact.json"
REQUIRED_GOVERNANCE_FILES = [
    "README.md",
    "docs/README.md",
    "docs/backlog/issue-ready-backlog.md",
    "scripts/verify-repo.ps1",
]
ARCHIVE_CANDIDATE_PREFIXES = (
    "docs/change-evidence/snapshots/",
    "docs/change-evidence/rule-sync-backups/",
)
ARCHIVE_CANDIDATE_PREFIX_FILES = (
    "docs/change-evidence/operator-ui",
    "operator-ui-",
)
TARGET_REPO_RUNS_PREFIX = "docs/change-evidence/target-repo-runs/"
TARGET_REPO_RUNS_KEEP = {
    "kpi-latest.json",
    "kpi-rolling.json",
    "summary-latest.json",
    "summary-active-targets-latest.json",
    "summary-active-targets-rows-20260422191507.json",
    "summary-active-targets-20260422191507.json",
    "summary-allowedscope.json",
    "summary-github-vps.json",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a governed repo-map context artifact.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--strategy-path", default=str(DEFAULT_STRATEGY_PATH))
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    result = build_repo_map_context_artifact(
        repo_root=Path(args.repo_root),
        strategy_path=Path(args.strategy_path),
        output_path=Path(args.output_path),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def build_repo_map_context_artifact(*, repo_root: Path, strategy_path: Path, output_path: Path) -> dict:
    root = repo_root.resolve(strict=False)
    strategy = json.loads(strategy_path.read_text(encoding="utf-8"))
    files = _collect_repo_files(root)
    included = [path for path in files if _matches_any(path, strategy.get("include_rules", ["**/*"]))]
    filtered = [path for path in included if not _matches_any(path, strategy.get("exclude_rules", []))]
    excluded = [path for path in included if path not in filtered]

    selected = _rank_files(filtered, strategy.get("fallback_files", []))
    forced_required = [path for path in REQUIRED_GOVERNANCE_FILES if path not in selected and (root / path).exists()]
    selected = forced_required + selected
    selected = _dedupe_preserve_order(selected)
    selected = _truncate_to_budget(root=root, selected=selected, max_tokens=int(strategy["max_tokens"]))

    required_present = [path for path in REQUIRED_GOVERNANCE_FILES if path in selected]
    file_selection_accuracy = len(required_present) / len(REQUIRED_GOVERNANCE_FILES)
    clarification_reduction_proxy = _clarification_reduction_proxy(selected)
    estimated_token_cost = _estimate_token_cost(root, selected)
    decision = _decision(
        max_tokens=int(strategy["max_tokens"]),
        estimated_token_cost=estimated_token_cost,
        file_selection_accuracy=file_selection_accuracy,
        clarification_reduction_proxy=clarification_reduction_proxy,
    )

    payload = {
        "schema_version": "0.1-draft",
        "repo_id": root.name,
        "strategy_id": strategy["strategy_id"],
        "strategy_path": strategy_path.relative_to(root).as_posix() if strategy_path.is_relative_to(root) else str(strategy_path),
        "required_governance_files": REQUIRED_GOVERNANCE_FILES,
        "selected_files": selected,
        "governance_override_enforced": len(forced_required) > 0,
        "metrics": {
            "estimated_token_cost": estimated_token_cost,
            "max_tokens": int(strategy["max_tokens"]),
            "selected_file_count": len(selected),
            "file_selection_accuracy": round(file_selection_accuracy, 2),
            "clarification_reduction_proxy": round(clarification_reduction_proxy, 2),
            "excluded_archive_candidate_count": len([path for path in excluded if _is_archive_candidate(path)]),
            "required_file_override_count": len(forced_required),
        },
        "decision": decision,
        "rollback_ref": "Delete the generated artifact and repo-local strategy override; no runtime behavior is enabled by this file.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _collect_repo_files(root: Path) -> list[str]:
    files: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative.startswith(".git/"):
            continue
        files.append(relative)
    return files


def _matches_any(path: str, patterns: list[str]) -> bool:
    if not patterns:
        return False
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _rank_files(paths: list[str], fallback_files: list[str]) -> list[str]:
    def score(path: str) -> tuple[int, str]:
        priority = 0
        if path in fallback_files:
            priority -= 5
        if path.endswith("README.md") or path.endswith("README.en.md") or path.endswith("README.zh-CN.md"):
            priority -= 4
        if path.startswith("scripts/"):
            priority -= 3
        if path.startswith("docs/"):
            priority -= 2
        if path.startswith(".governed-ai/"):
            priority -= 2
        if path.startswith("tests/"):
            priority -= 1
        return (priority, path)

    return [path for _, path in sorted((score(path) for path in paths))]


def _estimate_token_cost(root: Path, selected: list[str]) -> int:
    total_chars = 0
    for relative in selected:
        path = root / relative
        try:
            snippet = path.read_text(encoding="utf-8", errors="ignore")[:800]
        except OSError:
            snippet = relative
        total_chars += len(relative) + len(snippet)
    return max(1, total_chars // 4)


def _truncate_to_budget(*, root: Path, selected: list[str], max_tokens: int) -> list[str]:
    kept: list[str] = []
    for path in selected:
        candidate = kept + [path]
        if _estimate_token_cost(root, candidate) > max_tokens and path not in REQUIRED_GOVERNANCE_FILES:
            continue
        kept.append(path)
    return kept


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _clarification_reduction_proxy(selected: list[str]) -> float:
    expected = {
        "README.md",
        "docs/README.md",
        "docs/backlog/issue-ready-backlog.md",
        "scripts/verify-repo.ps1",
    }
    present = len([path for path in expected if path in selected])
    return present / len(expected)


def _decision(*, max_tokens: int, estimated_token_cost: int, file_selection_accuracy: float, clarification_reduction_proxy: float) -> str:
    if file_selection_accuracy < 1.0:
        return "adjust"
    if estimated_token_cost > max_tokens:
        return "adjust"
    if clarification_reduction_proxy < 0.75:
        return "adjust"
    return "keep"


def _is_archive_candidate(path: str) -> bool:
    if path.startswith(ARCHIVE_CANDIDATE_PREFIXES):
        return True
    if path.startswith(ARCHIVE_CANDIDATE_PREFIX_FILES):
        return True
    if not path.startswith(TARGET_REPO_RUNS_PREFIX):
        return False
    filename = path.rsplit("/", 1)[-1]
    if filename in TARGET_REPO_RUNS_KEEP:
        return False
    return filename.endswith(".json")


if __name__ == "__main__":
    raise SystemExit(main())
