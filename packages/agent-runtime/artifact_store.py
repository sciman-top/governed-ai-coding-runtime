"""Service-level artifact store abstraction backed by filesystem paths."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import json
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class StoredArtifact:
    absolute_path: str
    relative_path: str
    content_type: str


class FilesystemArtifactStore:
    def __init__(self, root: str | Path) -> None:
        self._root = Path(root).resolve(strict=False)
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def write_json(self, *, relative_path: str, payload: dict) -> StoredArtifact:
        path = self._resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return StoredArtifact(
            absolute_path=path.as_posix(),
            relative_path=path.relative_to(self._root).as_posix(),
            content_type="application/json",
        )

    def write_text(self, *, relative_path: str, content: str) -> StoredArtifact:
        path = self._resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_text(path, content, encoding="utf-8")
        return StoredArtifact(
            absolute_path=path.as_posix(),
            relative_path=path.relative_to(self._root).as_posix(),
            content_type="text/plain",
        )

    def read_json(self, *, relative_path: str) -> dict:
        path = self._resolve(relative_path)
        return json.loads(path.read_text(encoding="utf-8"))

    def _resolve(self, relative_path: str) -> Path:
        candidate = self._root / _required_string(relative_path, "relative_path")
        resolved = candidate.resolve(strict=False)
        if not _is_under(resolved, self._root):
            msg = "artifact path must stay under store root"
            raise ValueError(msg)
        return resolved


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip().replace("\\", "/")


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
    except ValueError:
        return False
    return True


def _atomic_write_text(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(content, encoding=encoding)
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
