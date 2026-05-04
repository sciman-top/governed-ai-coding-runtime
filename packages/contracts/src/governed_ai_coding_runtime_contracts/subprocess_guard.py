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
_SAFE_CODEX_ENV_POLICY_KEYS = (
    "WINDIR",
    "windir",
    "SYSTEMROOT",
    "SystemRoot",
    "APPDATA",
    "LOCALAPPDATA",
    "PROGRAMDATA",
    "ProgramFiles",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "no_proxy",
)
_WINDOWS_PERSISTED_ENV_REGISTRY_PATHS = (
    ("user", "Environment"),
    (
        "machine",
        r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
    ),
)


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

    _merge_codex_shell_environment_policy(env)
    _merge_persisted_windows_environment(env)

    windows_root = _resolved_windows_root(env)
    _force_canonical_env_key(env, "SystemRoot", windows_root)
    _force_canonical_env_key(env, "WINDIR", windows_root)
    _force_canonical_env_key(env, "ComSpec", _resolved_windows_comspec(env, windows_root))
    if _env_get(env, "SystemDrive") is None:
        env["SystemDrive"] = Path(windows_root).drive or "C:"
    user_profile = _env_get(env, "USERPROFILE")
    if user_profile:
        profile_path = Path(user_profile)
        _set_env_if_missing(env, "HOMEDRIVE", profile_path.drive or _env_get(env, "SystemDrive") or "C:")
        if _env_get(env, "HOMEPATH") is None:
            try:
                env["HOMEPATH"] = "\\" + str(profile_path.relative_to(profile_path.anchor)).rstrip("\\/")
            except ValueError:
                env["HOMEPATH"] = str(profile_path)
        _set_env_if_missing(env, "LOCALAPPDATA", str(profile_path / "AppData" / "Local"))
        _set_env_if_missing(env, "APPDATA", str(profile_path / "AppData" / "Roaming"))
    if _env_get(env, "PROGRAMDATA") is None and Path(r"C:\ProgramData").exists():
        env["PROGRAMDATA"] = r"C:\ProgramData"
    if _env_get(env, "ProgramFiles") is None and Path(r"C:\Program Files").exists():
        env["ProgramFiles"] = r"C:\Program Files"
    _prepend_path_entry(env, str(Path(windows_root) / "System32"))
    _prepend_path_entry(env, windows_root)
    program_files = _env_get(env, "ProgramFiles")
    if program_files:
        _prepend_path_entry(env, str(Path(program_files) / "PowerShell" / "7"))
        _prepend_path_entry(env, str(Path(program_files) / "Git" / "cmd"))
        _prepend_path_entry(env, str(Path(program_files) / "GitHub CLI"))
    _prepend_path_entry(env, str(Path(windows_root) / "System32" / "WindowsPowerShell" / "v1.0"))
    return env


def _merge_codex_shell_environment_policy(env: dict[str, str]) -> None:
    for key, value in _read_codex_shell_environment_policy_set(env).items():
        _set_env_if_missing(env, key, value)


def _read_codex_shell_environment_policy_set(env: dict[str, str]) -> dict[str, str]:
    try:
        import tomllib
    except ModuleNotFoundError:
        return {}

    for config_path in _codex_config_candidates(env):
        if not config_path.exists():
            continue
        try:
            data = tomllib.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            continue
        shell_policy = data.get("shell_environment_policy")
        if not isinstance(shell_policy, dict):
            continue
        policy_set = shell_policy.get("set")
        if not isinstance(policy_set, dict):
            continue
        safe_values: dict[str, str] = {}
        for key in _SAFE_CODEX_ENV_POLICY_KEYS:
            value = policy_set.get(key)
            if isinstance(value, str) and value.strip():
                safe_values[key] = value
        return safe_values
    return {}


def _codex_config_candidates(env: dict[str, str]) -> list[Path]:
    candidates: list[Path] = []
    codex_home = _env_get(env, "CODEX_HOME")
    if codex_home:
        candidates.append(Path(codex_home) / "config.toml")
    user_profile = _env_get(env, "USERPROFILE") or _env_get(env, "HOME")
    if user_profile:
        candidates.append(Path(user_profile) / ".codex" / "config.toml")
    return candidates


def _merge_persisted_windows_environment(env: dict[str, str]) -> None:
    for key, value in _read_persisted_windows_environment().items():
        _set_env_if_missing(env, key, _expand_windows_env_value(value, env))


def _read_persisted_windows_environment() -> dict[str, str]:
    try:
        import winreg
    except ImportError:
        return {}

    roots = {
        "user": winreg.HKEY_CURRENT_USER,
        "machine": winreg.HKEY_LOCAL_MACHINE,
    }
    values: dict[str, str] = {}
    for scope, subkey in _WINDOWS_PERSISTED_ENV_REGISTRY_PATHS:
        root = roots[scope]
        try:
            with winreg.OpenKey(root, subkey) as key_handle:
                for name in _SAFE_CODEX_ENV_POLICY_KEYS:
                    if name in values:
                        continue
                    try:
                        raw_value, _value_type = winreg.QueryValueEx(key_handle, name)
                    except OSError:
                        continue
                    if isinstance(raw_value, str) and raw_value.strip():
                        values[name] = raw_value
        except OSError:
            continue
    return values


def _expand_windows_env_value(value: str, env: dict[str, str]) -> str:
    expanded = value
    defaults = {
        "SystemRoot": _env_get(env, "SystemRoot") or _env_get(env, "WINDIR") or r"C:\Windows",
        "WINDIR": _env_get(env, "WINDIR") or _env_get(env, "SystemRoot") or r"C:\Windows",
        "USERPROFILE": _env_get(env, "USERPROFILE") or "",
        "PROGRAMDATA": _env_get(env, "PROGRAMDATA") or r"C:\ProgramData",
        "ProgramFiles": _env_get(env, "ProgramFiles") or r"C:\Program Files",
    }
    for key, replacement in defaults.items():
        if replacement:
            expanded = expanded.replace(f"%{key}%", replacement)
            expanded = expanded.replace(f"%{key.upper()}%", replacement)
    return expanded


def _resolved_windows_root(env: dict[str, str]) -> str:
    for key in ("SystemRoot", "WINDIR"):
        candidate = _env_get(env, key)
        if candidate and "%" not in candidate and _windows_cmd_path(candidate).exists():
            return candidate
    default_root = r"C:\Windows"
    if _windows_cmd_path(default_root).exists():
        return default_root
    for key in ("SystemRoot", "WINDIR"):
        candidate = _env_get(env, key)
        if candidate and "%" not in candidate:
            return candidate
    return default_root


def _resolved_windows_comspec(env: dict[str, str], windows_root: str) -> str | None:
    candidates = [
        _windows_cmd_path(windows_root),
        _windows_cmd_path(r"C:\Windows"),
    ]
    existing = _env_get(env, "ComSpec")
    if existing is not None:
        candidates.append(Path(_expand_windows_env_value(existing, env)))
    for candidate in candidates:
        if candidate.name.lower() == "cmd.exe" and candidate.exists():
            return str(candidate)
    first = candidates[0]
    return str(first) if first.name.lower() == "cmd.exe" else None


def _windows_cmd_path(windows_root: str) -> Path:
    return Path(windows_root) / "System32" / "cmd.exe"


def _env_get(env: dict[str, str], key: str) -> str | None:
    value = env.get(key)
    if isinstance(value, str) and value:
        return value
    lowered = key.lower()
    for existing_key, existing_value in env.items():
        if existing_key.lower() == lowered and isinstance(existing_value, str) and existing_value:
            return existing_value
    return None


def _set_env_if_missing(env: dict[str, str], key: str, value: str | None) -> None:
    if not value or _env_get(env, key) is not None:
        return
    env[key] = value


def _force_canonical_env_key(env: dict[str, str], key: str, value: str | None) -> None:
    if not value:
        return
    for existing_key in list(env):
        if existing_key.lower() == key.lower() and existing_key != key:
            del env[existing_key]
    env[key] = value


def _timeout_label(value: float | None) -> str:
    if value is None:
        return "timeout limit"
    if value.is_integer():
        return f"{int(value)}s"
    return f"{value:.3f}s".rstrip("0").rstrip(".")


def _prepend_path_entry(env: dict[str, str], path_entry: str) -> None:
    if not path_entry or not Path(path_entry).exists():
        return
    current = env.get("PATH", "")
    parts = [part for part in current.split(os.pathsep) if part]
    if any(os.path.normcase(part) == os.path.normcase(path_entry) for part in parts):
        return
    env["PATH"] = os.pathsep.join([path_entry, *parts])
