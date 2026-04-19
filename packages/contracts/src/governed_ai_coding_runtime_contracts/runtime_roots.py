"""Runtime root placement and compatibility migration helpers."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RuntimeRoots:
    runtime_root: str
    tasks_root: str
    artifacts_root: str
    replay_root: str
    workspaces_root: str
    compatibility_mode: bool


def resolve_runtime_roots(
    *,
    repo_root: str | Path,
    runtime_root: str | Path | None = None,
    compatibility_mode: bool | None = None,
) -> RuntimeRoots:
    repo_root_path = Path(repo_root).resolve(strict=False)
    compatibility_root = repo_root_path / ".runtime"

    explicit_runtime_root = _optional_path(runtime_root)
    compat_from_env = _env_flag("GOVERNED_RUNTIME_COMPAT_MODE")
    compatibility = bool(compatibility_mode) if compatibility_mode is not None else compat_from_env
    if explicit_runtime_root is not None:
        root = explicit_runtime_root
        compatibility = root == compatibility_root
    elif compatibility:
        root = compatibility_root
    else:
        runtime_home = _runtime_home_root()
        root = runtime_home / _safe_repo_slug(repo_root_path.name)

    tasks_root = root / "tasks"
    artifacts_root = root / "artifacts"
    replay_root = root / "replay"
    workspaces_root = root / "workspaces"
    return RuntimeRoots(
        runtime_root=root.as_posix(),
        tasks_root=tasks_root.as_posix(),
        artifacts_root=artifacts_root.as_posix(),
        replay_root=replay_root.as_posix(),
        workspaces_root=workspaces_root.as_posix(),
        compatibility_mode=compatibility,
    )


def ensure_runtime_roots(roots: RuntimeRoots) -> RuntimeRoots:
    for path in [
        roots.runtime_root,
        roots.tasks_root,
        roots.artifacts_root,
        roots.replay_root,
        roots.workspaces_root,
    ]:
        Path(path).mkdir(parents=True, exist_ok=True)
    return roots


def build_runtime_root_migration(
    *,
    repo_root: str | Path,
    target_runtime_root: str | Path,
) -> dict:
    repo_root_path = Path(repo_root).resolve(strict=False)
    source = repo_root_path / ".runtime"
    target = Path(target_runtime_root).resolve(strict=False)
    return {
        "source_runtime_root": source.as_posix(),
        "target_runtime_root": target.as_posix(),
        "rollback_runtime_root": source.as_posix(),
        "compatible": source != target,
    }


def _runtime_home_root() -> Path:
    override = os.environ.get("GOVERNED_RUNTIME_HOME")
    if isinstance(override, str) and override.strip():
        return Path(override).expanduser().resolve(strict=False)
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if isinstance(local_app_data, str) and local_app_data.strip():
            return Path(local_app_data).resolve(strict=False) / "governed-ai-coding-runtime"
    return Path.home().resolve(strict=False) / ".governed-ai-coding-runtime"


def _safe_repo_slug(name: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_", "."} else "-" for char in name).strip("-")
    if cleaned:
        return cleaned
    return "runtime"


def _optional_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return Path(text).expanduser().resolve(strict=False)


def _env_flag(name: str) -> bool:
    raw = os.environ.get(name)
    if not isinstance(raw, str):
        return False
    return raw.strip().lower() in {"1", "true", "yes", "on"}
