"""Guards for file-backed runtime state."""

from __future__ import annotations

import os
from pathlib import Path
import re
from uuid import uuid4


_CONTROL_CHARS = re.compile(r"[\x00-\x1f]")
_INVALID_FILE_CHARS = set('<>:"/\\|?*')
_RESERVED_SEGMENTS = {".", ".."}
_WINDOWS_RESERVED_BASENAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


def validate_file_component(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    normalized = value.strip()
    if normalized in _RESERVED_SEGMENTS:
        msg = f"{field_name} must be a safe file component"
        raise ValueError(msg)
    if "/" in normalized or "\\" in normalized:
        msg = f"{field_name} must not contain path separators"
        raise ValueError(msg)
    if normalized.endswith((" ", ".")):
        msg = f"{field_name} must not end with space or dot"
        raise ValueError(msg)
    if _CONTROL_CHARS.search(normalized):
        msg = f"{field_name} contains control characters"
        raise ValueError(msg)
    if any(character in _INVALID_FILE_CHARS for character in normalized):
        msg = f"{field_name} contains unsupported path characters"
        raise ValueError(msg)
    basename = normalized.split(".", 1)[0].upper()
    if basename in _WINDOWS_RESERVED_BASENAMES:
        msg = f"{field_name} uses a reserved device name"
        raise ValueError(msg)
    return normalized


def atomic_write_text(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        target.write_text(content, encoding=encoding)
        return
    temporary = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(content, encoding=encoding)
        os.replace(temporary, target)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def is_resolved_under(path: Path, parent: Path) -> bool:
    try:
        Path(path).resolve(strict=False).relative_to(Path(parent).resolve(strict=False))
    except ValueError:
        return False
    return True


def ensure_resolved_under(path: Path, parent: Path, *, field_name: str, message: str | None = None) -> None:
    if is_resolved_under(path, parent):
        return
    if isinstance(message, str) and message.strip():
        raise ValueError(message.strip())
    raise ValueError(f"{field_name} resolves outside allowed parent")
