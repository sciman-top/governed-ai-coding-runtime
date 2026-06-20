from __future__ import annotations

from pathlib import Path
from typing import Any


WORKTREES_SEGMENT = ".worktrees"


def canonical_repo_root(repo_root: Path) -> Path:
    root = repo_root.resolve(strict=False)
    parts = root.parts
    if WORKTREES_SEGMENT not in parts:
        return root

    index = parts.index(WORKTREES_SEGMENT)
    if index == 0:
        return root
    return Path(*parts[:index])


def canonical_repo_id(repo_root: Path) -> str:
    return canonical_repo_root(repo_root).name


def canonicalize_repo_path(path: Path, *, repo_root: Path) -> str:
    resolved = path.resolve(strict=False)
    root = repo_root.resolve(strict=False)
    canonical_root = canonical_repo_root(root)
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        return resolved.as_posix()
    return (canonical_root / relative).as_posix()


def canonicalize_repo_refs(payload: Any, *, repo_root: Path) -> Any:
    if isinstance(payload, dict):
        return {key: canonicalize_repo_refs(value, repo_root=repo_root) for key, value in payload.items()}
    if isinstance(payload, list):
        return [canonicalize_repo_refs(value, repo_root=repo_root) for value in payload]
    if isinstance(payload, str):
        return _canonicalize_repo_ref_text(payload, repo_root=repo_root)
    return payload


def _canonicalize_repo_ref_text(value: str, *, repo_root: Path) -> str:
    root = repo_root.resolve(strict=False)
    canonical_root = canonical_repo_root(root)
    text = value.replace(root.as_posix(), canonical_root.as_posix())
    return text.replace(str(root), str(canonical_root))
