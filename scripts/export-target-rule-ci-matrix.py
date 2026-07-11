from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COORDINATION_PATH = ROOT / "rules" / "target-project-rule-coordination.json"
GITHUB_REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("coordination manifest must be a JSON object")
    return payload


def build_matrix(payload: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    targets = payload.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError("coordination manifest must contain targets")

    include: list[dict[str, str]] = []
    seen: set[str] = set()
    for target in targets:
        if not isinstance(target, dict):
            raise ValueError("target entries must be JSON objects")
        repo_id = str(target.get("repo_id") or "").strip()
        repo_path = str(target.get("repo_path") or "").strip().replace("\\", "/")
        repository = str(target.get("github_repository") or "").strip()
        visibility = str(target.get("github_visibility") or "").strip()
        aggregate_mode = str(target.get("aggregate_mode") or "").strip()
        path = PurePosixPath(repo_path)
        if not repo_id or repo_id in seen:
            raise ValueError(f"invalid or duplicate repo_id: {repo_id or 'missing'}")
        if not repo_path or path.is_absolute() or ".." in path.parts:
            raise ValueError(f"repo_path must be relative and contained: {repo_path or 'missing'}")
        if not GITHUB_REPOSITORY_PATTERN.fullmatch(repository):
            raise ValueError(f"invalid github_repository for {repo_id}: {repository or 'missing'}")
        expected_mode = "checkout" if visibility == "public" else "target_local_only"
        if visibility not in {"public", "private"} or aggregate_mode != expected_mode:
            raise ValueError(
                f"invalid aggregate boundary for {repo_id}: "
                f"visibility={visibility or 'missing'}, mode={aggregate_mode or 'missing'}"
            )
        seen.add(repo_id)
        include.append(
            {
                "repo_id": repo_id,
                "repo_path": repo_path,
                "repository": repository,
                "github_visibility": visibility,
                "aggregate_mode": aggregate_mode,
            }
        )
    return {"include": include}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export the target-rule GitHub Actions matrix.")
    parser.add_argument("--coordination-path", default=str(DEFAULT_COORDINATION_PATH))
    args = parser.parse_args(argv)

    matrix = build_matrix(_load_json(Path(args.coordination_path).resolve(strict=False)))
    print(json.dumps(matrix, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
