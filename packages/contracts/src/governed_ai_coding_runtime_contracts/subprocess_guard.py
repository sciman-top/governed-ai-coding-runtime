"""Subprocess timeout and exemption guardrails."""

from __future__ import annotations

from dataclasses import dataclass
import fnmatch
import os
from pathlib import Path
import subprocess
from typing import Sequence


DEFAULT_TIMEOUT_EXEMPT_ALLOWLIST = (
    "git status*",
    "git diff*",
    "git log*",
    "*pip list*",
    "*pip check*",
)
_TIMEOUT_EXPIRED_EXIT_CODE = 124


@dataclass(frozen=True, slots=True)
class TimeoutPolicy:
    timeout_seconds: float | None
    timeout_exempt: bool


@dataclass(frozen=True, slots=True)
class SubprocessResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool


def resolve_timeout_policy(
    *,
    command_text: str,
    timeout_seconds: object = None,
    timeout_exempt: object = False,
    allowlist_patterns: Sequence[str] | None = None,
) -> TimeoutPolicy:
    normalized_command = _required_string(command_text, "command_text")
    resolved_timeout = _optional_positive_number(timeout_seconds, "timeout_seconds")
    if not isinstance(timeout_exempt, bool):
        raise ValueError("timeout_exempt must be a boolean")
    if not timeout_exempt:
        return TimeoutPolicy(timeout_seconds=resolved_timeout, timeout_exempt=False)
    combined_allowlist = list(DEFAULT_TIMEOUT_EXEMPT_ALLOWLIST)
    combined_allowlist.extend(_normalize_allowlist_patterns(allowlist_patterns))
    if not _matches_any_pattern(normalized_command, combined_allowlist):
        raise ValueError("timeout_exempt is only allowed for allowlisted commands")
    return TimeoutPolicy(timeout_seconds=None, timeout_exempt=True)


def run_subprocess(
    *,
    command: str | list[str],
    shell: bool,
    cwd: str | Path | None = None,
    timeout_seconds: float | None = None,
) -> SubprocessResult:
    env = _subprocess_environment()
    kwargs = {
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "cwd": cwd,
        "check": False,
        "shell": shell,
        "env": env,
    }
    if shell and os.name == "nt" and env.get("ComSpec"):
        kwargs["executable"] = env["ComSpec"]
    try:
        completed = subprocess.run(
            command,
            timeout=timeout_seconds,
            **kwargs,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = _coerce_output_text(exc.stdout)
        stderr = _coerce_output_text(exc.stderr)
        timeout_label = _timeout_label(timeout_seconds)
        timeout_message = f"command timed out after {timeout_label}"
        merged_stderr = "\n".join(part for part in [stderr, timeout_message] if part).strip()
        return SubprocessResult(
            returncode=_TIMEOUT_EXPIRED_EXIT_CODE,
            stdout=stdout,
            stderr=merged_stderr,
            timed_out=True,
        )
    return SubprocessResult(
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
        timed_out=False,
    )


def parse_optional_positive_timeout(value: object, field_name: str) -> float | None:
    return _optional_positive_number(value, field_name)


def _optional_positive_number(value: object, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive number")
    if isinstance(value, (int, float)):
        numeric = float(value)
    elif isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            numeric = float(raw)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a positive number") from exc
    else:
        raise ValueError(f"{field_name} must be a positive number")
    if numeric <= 0:
        raise ValueError(f"{field_name} must be a positive number")
    return numeric


def _normalize_allowlist_patterns(patterns: Sequence[str] | None) -> list[str]:
    if patterns is None:
        return []
    normalized: list[str] = []
    for index, pattern in enumerate(patterns):
        if not isinstance(pattern, str) or not pattern.strip():
            raise ValueError(f"timeout_exempt_allowlist[{index}] must be a non-empty string")
        normalized.append(pattern.strip())
    return normalized


def _matches_any_pattern(command_text: str, patterns: Sequence[str]) -> bool:
    normalized_command = command_text.strip().lower()
    for pattern in patterns:
        if fnmatch.fnmatch(normalized_command, pattern.strip().lower()):
            return True
    return False


def _required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _coerce_output_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, str):
        return value
    return ""


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
    user_profile = env.get("USERPROFILE")
    if user_profile:
        profile_path = Path(user_profile)
        if "HOMEDRIVE" not in env:
            env["HOMEDRIVE"] = profile_path.drive or env["SystemDrive"]
        if "HOMEPATH" not in env:
            try:
                env["HOMEPATH"] = "\\" + str(profile_path.relative_to(profile_path.anchor)).rstrip("\\/")
            except ValueError:
                env["HOMEPATH"] = str(profile_path)
        if "LOCALAPPDATA" not in env:
            env["LOCALAPPDATA"] = str(profile_path / "AppData" / "Local")
        if "APPDATA" not in env:
            env["APPDATA"] = str(profile_path / "AppData" / "Roaming")
    return env


def _timeout_label(value: float | None) -> str:
    if value is None:
        return "timeout limit"
    if value.is_integer():
        return f"{int(value)}s"
    return f"{value:.3f}s".rstrip("0").rstrip(".")
