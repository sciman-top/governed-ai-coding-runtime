from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROVIDER_PROFILES_FILE = "provider-profiles.json"
CLAUDE_USAGE_NOTE = "Third-party provider usage and quota data is not exposed through a stable Claude Code local API."

COMMON_RECOMMENDED_ENV = {
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1",
    "CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK": "1",
    "DISABLE_INTERLEAVED_THINKING": "1",
    "DISABLE_LOGIN_COMMAND": "1",
    "DISABLE_LOGOUT_COMMAND": "1",
    "DISABLE_UPGRADE_COMMAND": "1",
    "DISABLE_EXTRA_USAGE_COMMAND": "1",
    "CLAUDE_CODE_MAX_RETRIES": "6",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "8192",
    "BASH_DEFAULT_TIMEOUT_MS": "300000",
    "BASH_MAX_TIMEOUT_MS": "1200000",
    "BASH_MAX_OUTPUT_LENGTH": "30000",
    "MAX_MCP_OUTPUT_TOKENS": "25000",
}

RECOMMENDED_PERMISSIONS_ALLOW = [
    "Read",
    "Edit",
    "MultiEdit",
    "Write",
    "Bash(*)",
    "WebSearch",
    "WebFetch",
    "mcp__context7__*",
    "mcp__github__*",
    "mcp__microsoft-learn__*",
    "mcp__playwright__*",
    "mcp__zai-mcp-server__*",
    "mcp__web-search-prime__*",
    "mcp__web_reader__*",
    "mcp__zread__*",
]

RECOMMENDED_PERMISSIONS_DENY = [
    "Read(**/.env)",
    "Read(**/.env.*)",
    "Read(**/target.json)",
    "Read(**/*id_rsa*)",
    "Read(**/*id_ed25519*)",
    "Read(**/*credentials*)",
    "Read(**/*token*)",
    "Bash(git reset --hard*)",
    "Bash(git clean -*)",
    "Bash(rm -rf*)",
    "Bash(del /s*)",
    "Bash(format *)",
    "Bash(reg delete*)",
    "Bash(powershell:*)",
    "Bash(powershell.exe:*)",
]

DEFAULT_PROVIDER_PROFILES = [
    {
        "name": "bigmodel-glm",
        "label": "智谱 GLM",
        "provider": "bigmodel",
        "base_url": "https://open.bigmodel.cn/api/anthropic",
        "auth_env": "ANTHROPIC_AUTH_TOKEN",
        "docs_url": "https://docs.bigmodel.cn/cn/guide/develop/claude",
        "models": {
            "opus": "glm-5.1",
            "sonnet": "glm-5-turbo",
            "haiku": "glm-4.5-air",
        },
        "env": {
            "API_TIMEOUT_MS": "3000000",
            "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5.1",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-5-turbo",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
        },
        "note": "Recommended local default for this machine: quality-first GLM mapping with the existing Zhipu token kept only in ~/.claude/settings.json.",
    },
    {
        "name": "deepseek-v4",
        "label": "DeepSeek v4",
        "provider": "deepseek",
        "base_url": "https://api.deepseek.com/anthropic",
        "auth_env": "ANTHROPIC_API_KEY",
        "docs_url": "https://api-docs.deepseek.com/guides/anthropic_api",
        "models": {
            "opus": "deepseek-v4-pro",
            "sonnet": "deepseek-v4-flash",
            "haiku": "deepseek-v4-flash",
        },
        "env": {
            "API_TIMEOUT_MS": "900000",
            "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-flash",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash",
        },
        "note": "DeepSeek supports an Anthropic-compatible endpoint; add ANTHROPIC_API_KEY before switching.",
    },
]

PROVIDER_AUTH_KEYS = ("ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY")


@dataclass(frozen=True)
class ClaudeProviderProfile:
    name: str
    label: str
    provider: str
    base_url: str
    auth_env: str
    docs_url: str
    models: dict[str, str]
    env: dict[str, str]
    note: str
    active: bool = False
    credential_present: bool = False
    credential_source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "provider": self.provider,
            "base_url": self.base_url,
            "auth_env": self.auth_env,
            "docs_url": self.docs_url,
            "models": self.models,
            "env": self.env,
            "note": self.note,
            "active": self.active,
            "credential_present": self.credential_present,
            "credential_source": self.credential_source,
        }


def claude_home(value: str | None = None) -> Path:
    raw = value or os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    path = Path(raw).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Claude home does not exist: {path}")
    return path.resolve()


def settings_path(home: Path | None = None) -> Path:
    return claude_home(str(home) if home else None) / "settings.json"


def provider_profiles_path(home: Path | None = None) -> Path:
    return claude_home(str(home) if home else None) / PROVIDER_PROFILES_FILE


def load_settings(home: Path | None = None) -> dict[str, Any]:
    path = settings_path(home)
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid Claude settings JSON: {path}")
    return payload


def load_provider_profiles(home: Path | None = None) -> list[ClaudeProviderProfile]:
    home = claude_home(str(home) if home else None)
    settings = load_settings(home)
    active_name = _detect_active_provider_name(settings)
    payload = _load_provider_profiles_payload(home)
    raw_profiles = payload.get("profiles") if isinstance(payload.get("profiles"), list) else DEFAULT_PROVIDER_PROFILES
    if isinstance(payload.get("active"), str) and payload["active"]:
        active_name = payload["active"]
    profiles = [_provider_from_payload(profile, settings, active_name) for profile in raw_profiles if isinstance(profile, dict)]
    return profiles


def write_default_provider_profiles(home: Path | None = None, *, active: str | None = None, overwrite: bool = False) -> dict[str, Any]:
    home = claude_home(str(home) if home else None)
    path = provider_profiles_path(home)
    if path.exists() and not overwrite:
        payload = _load_provider_profiles_payload(home)
        if "active" not in payload:
            payload["active"] = active or _detect_active_provider_name(load_settings(home)) or DEFAULT_PROVIDER_PROFILES[0]["name"]
            _write_json(path, payload)
        return {"status": "ok", "changed": False, "path": str(path)}
    payload = {
        "schema_version": 1,
        "active": active or _detect_active_provider_name(load_settings(home)) or DEFAULT_PROVIDER_PROFILES[0]["name"],
        "profiles": DEFAULT_PROVIDER_PROFILES,
    }
    _write_json(path, payload)
    return {"status": "ok", "changed": True, "path": str(path)}


def claude_status(home: Path | None = None) -> dict[str, Any]:
    home = claude_home(str(home) if home else None)
    return {
        "claude_home": str(home),
        "command": _run_command(["claude", "--version"], timeout_seconds=15),
        "settings": settings_summary(home),
        "providers": [profile.to_dict() for profile in load_provider_profiles(home)],
        "active_provider": active_provider(home),
        "config": config_health(home),
        "mcp": _run_command(["claude", "mcp", "list"], timeout_seconds=30),
        "usage": {
            "source": "provider",
            "windows": [],
            "note": CLAUDE_USAGE_NOTE,
        },
    }


def settings_summary(home: Path | None = None) -> dict[str, Any]:
    home = claude_home(str(home) if home else None)
    path = settings_path(home)
    settings = load_settings(home)
    permissions = _dict(settings.get("permissions"))
    env = _dict(settings.get("env"))
    return {
        "path": str(path),
        "exists": path.exists(),
        "model": settings.get("model"),
        "cleanupPeriodDays": settings.get("cleanupPeriodDays"),
        "statusLine": "configured" if settings.get("statusLine") else "missing",
        "skipDangerousModePermissionPrompt": settings.get("skipDangerousModePermissionPrompt"),
        "additionalDirectories": settings.get("additionalDirectories") if isinstance(settings.get("additionalDirectories"), list) else [],
        "permissions": {
            "defaultMode": permissions.get("defaultMode"),
            "disableBypassPermissionsMode": permissions.get("disableBypassPermissionsMode"),
            "allow_count": len(_list(permissions.get("allow"))),
            "deny_count": len(_list(permissions.get("deny"))),
        },
        "env": [_safe_env_item(name, env.get(name), source="settings.env") for name in sorted(env.keys())],
    }


def active_provider(home: Path | None = None) -> dict[str, Any] | None:
    profiles = load_provider_profiles(home)
    for profile in profiles:
        if profile.active:
            return profile.to_dict()
    return None


def config_health(home: Path | None = None) -> dict[str, Any]:
    home = claude_home(str(home) if home else None)
    settings = load_settings(home)
    env = _dict(settings.get("env"))
    permissions = _dict(settings.get("permissions"))
    provider = active_provider(home)
    checks: list[dict[str, Any]] = []

    checks.append(_check_value("model", "opus", settings.get("model")))
    checks.append(_check_value("cleanupPeriodDays", 60, settings.get("cleanupPeriodDays")))
    checks.append(_check_value("permissions.defaultMode", "dontAsk", permissions.get("defaultMode")))
    checks.append(_check_value("permissions.disableBypassPermissionsMode", "disable", permissions.get("disableBypassPermissionsMode")))
    checks.append(_check_value("skipDangerousModePermissionPrompt", False, bool(settings.get("skipDangerousModePermissionPrompt"))))

    allow = set(str(value) for value in _list(permissions.get("allow")))
    deny = set(str(value) for value in _list(permissions.get("deny")))
    for rule in ("Read", "Edit", "Write", "Bash(*)"):
        checks.append(_check_value(f"permissions.allow[{rule}]", True, rule in allow))
    for rule in ("Read(**/.env)", "Read(**/.env.*)", "Bash(git reset --hard*)", "Bash(rm -rf*)"):
        checks.append(_check_value(f"permissions.deny[{rule}]", True, rule in deny))

    expected_env = dict(COMMON_RECOMMENDED_ENV)
    if provider:
        expected_env.update(_dict(provider.get("env")))
        credential_present = _credential_present(str(provider.get("auth_env") or ""), env)[0]
        checks.append(_check_value(f"credential[{provider.get('auth_env')}]", True, credential_present))
    for key, expected in expected_env.items():
        checks.append(_check_value(f"env.{key}", expected, env.get(key)))

    profile_payload = _load_provider_profiles_payload(home)
    secret_hits = _scan_object_for_secret_values(profile_payload)
    model = str(settings.get("model") or "")
    if "[1m]" in model:
        checks.append({"key": "model_context_alias", "expected": "no [1m] alias for 200K third-party profiles", "actual": model, "ok": False})

    return {
        "status": "ok" if all(check["ok"] for check in checks) and not secret_hits else "attention",
        "checks": checks,
        "provider_profiles_path": str(provider_profiles_path(home)),
        "secret_like_profile_markers": secret_hits,
    }


def switch_provider(name: str, home: Path | None = None, *, dry_run: bool = False) -> dict[str, Any]:
    normalized = str(name or "").strip()
    if not normalized:
        return {"status": "error", "error": "missing provider profile name"}
    home = claude_home(str(home) if home else None)
    profiles = load_provider_profiles(home)
    matches = [profile for profile in profiles if profile.name == normalized or profile.provider == normalized or profile.label == normalized]
    if not matches:
        return {"status": "error", "error": f"unknown provider profile: {normalized}"}
    if len(matches) > 1:
        return {"status": "error", "error": f"ambiguous provider profile: {normalized}"}
    target = matches[0]
    settings = load_settings(home)
    env = _dict(settings.get("env"))
    credential_present, credential_source = _credential_present(target.auth_env, env)
    if not credential_present:
        return {
            "status": "error",
            "error": f"missing credential: {target.auth_env}",
            "provider": target.to_dict(),
            "next": f"Set {target.auth_env} in ~/.claude/settings.json env or in the shell before switching.",
        }
    updated = _optimized_settings(settings, target)
    if dry_run:
        return {
            "status": "ok",
            "changed": settings != updated,
            "dry_run": True,
            "provider": target.to_dict(),
            "credential_source": credential_source,
        }

    backup_path = backup_settings(home)
    _write_json(settings_path(home), updated)
    _set_active_provider_name(home, target.name)
    return {
        "status": "ok",
        "changed": True,
        "backup_path": str(backup_path),
        "provider": target.to_dict(),
        "credential_source": credential_source,
    }


def optimize_claude_local(
    home: Path | None = None,
    *,
    provider_name: str = "bigmodel-glm",
    apply: bool = False,
    install_switcher: bool = True,
) -> dict[str, Any]:
    home = claude_home(str(home) if home else None)
    profile_result = write_default_provider_profiles(home, active=provider_name)
    plan: dict[str, Any] = {
        "status": "dry_run",
        "apply": apply,
        "claude_home": str(home),
        "provider_profiles": profile_result,
        "provider": provider_name,
    }
    if not apply:
        plan["current"] = claude_status(home)
        plan["next"] = "Re-run with -Apply to write ~/.claude/settings.json and install claude-provider."
        return plan

    switch_result = switch_provider(provider_name, home)
    plan["settings"] = switch_result
    if switch_result.get("status") != "ok":
        plan["status"] = "error"
        return plan
    if install_switcher:
        plan["switcher"] = install_provider_switcher(home)
    plan["status"] = "ok"
    plan["current"] = claude_status(home)
    return plan


def backup_settings(home: Path | None = None) -> Path:
    home = claude_home(str(home) if home else None)
    path = settings_path(home)
    if not path.exists():
        raise FileNotFoundError(f"missing Claude settings: {path}")
    backup_dir = home / "settings-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"settings-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    shutil.copyfile(path, backup_path)
    return backup_path


def install_provider_switcher(home: Path | None = None, bin_dir: Path | None = None) -> dict[str, Any]:
    home = claude_home(str(home) if home else None)
    bin_dir = (bin_dir or (Path.home() / ".local" / "bin")).expanduser()
    scripts_dir = home / "scripts"
    user_lib_dir = scripts_dir / "lib"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    user_lib_dir.mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)
    source_dir = Path(__file__).resolve().parents[1]
    source = source_dir / "claude-provider.ps1"
    source_py = source_dir / "claude-provider.py"
    source_lib = source_dir / "lib" / "claude_local.py"
    target = scripts_dir / "Switch-ClaudeProvider.ps1"
    target_py = scripts_dir / "claude-provider.py"
    target_lib = user_lib_dir / "claude_local.py"
    shim = bin_dir / "claude-provider.cmd"
    shutil.copyfile(source, target)
    shutil.copyfile(source_py, target_py)
    shutil.copyfile(source_lib, target_lib)
    shim.write_text(
        '@echo off\npwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\\.claude\\scripts\\Switch-ClaudeProvider.ps1" %*\n',
        encoding="utf-8",
    )
    return {"status": "ok", "script": str(target), "python": str(target_py), "library": str(target_lib), "shim": str(shim)}


def _optimized_settings(settings: dict[str, Any], profile: ClaudeProviderProfile) -> dict[str, Any]:
    updated = deepcopy(settings)
    env = dict(_dict(updated.get("env")))
    existing_credential = env.get(profile.auth_env)
    for key in PROVIDER_AUTH_KEYS:
        if key != profile.auth_env:
            env.pop(key, None)
    if existing_credential:
        env[profile.auth_env] = existing_credential
    env.update(COMMON_RECOMMENDED_ENV)
    env.update(profile.env)
    updated["env"] = env

    permissions = dict(_dict(updated.get("permissions")))
    permissions["defaultMode"] = "dontAsk"
    permissions["disableBypassPermissionsMode"] = "disable"
    permissions["allow"] = _merge_unique(_list(permissions.get("allow")), RECOMMENDED_PERMISSIONS_ALLOW)
    permissions["deny"] = _merge_unique(_list(permissions.get("deny")), RECOMMENDED_PERMISSIONS_DENY)
    updated["permissions"] = permissions
    updated["model"] = "opus"
    updated["cleanupPeriodDays"] = 60
    updated["skipDangerousModePermissionPrompt"] = False
    return updated


def _load_provider_profiles_payload(home: Path) -> dict[str, Any]:
    path = provider_profiles_path(home)
    if not path.exists():
        return {"schema_version": 1, "profiles": DEFAULT_PROVIDER_PROFILES}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid provider profiles JSON: {path}")
    return payload


def _set_active_provider_name(home: Path, name: str) -> None:
    payload = _load_provider_profiles_payload(home)
    payload["active"] = name
    if "profiles" not in payload:
        payload["profiles"] = DEFAULT_PROVIDER_PROFILES
    _write_json(provider_profiles_path(home), payload)


def _detect_active_provider_name(settings: dict[str, Any]) -> str:
    env = _dict(settings.get("env"))
    base_url = str(env.get("ANTHROPIC_BASE_URL") or "").rstrip("/")
    for profile in DEFAULT_PROVIDER_PROFILES:
        if base_url == str(profile["base_url"]).rstrip("/"):
            return str(profile["name"])
    return ""


def _provider_from_payload(payload: dict[str, Any], settings: dict[str, Any], active_name: str) -> ClaudeProviderProfile:
    env = _dict(settings.get("env"))
    auth_env = str(payload.get("auth_env") or "ANTHROPIC_AUTH_TOKEN")
    credential_present, credential_source = _credential_present(auth_env, env)
    return ClaudeProviderProfile(
        name=str(payload.get("name") or ""),
        label=str(payload.get("label") or payload.get("name") or ""),
        provider=str(payload.get("provider") or ""),
        base_url=str(payload.get("base_url") or ""),
        auth_env=auth_env,
        docs_url=str(payload.get("docs_url") or ""),
        models={str(k): str(v) for k, v in _dict(payload.get("models")).items()},
        env={str(k): str(v) for k, v in _dict(payload.get("env")).items()},
        note=str(payload.get("note") or ""),
        active=str(payload.get("name") or "") == active_name,
        credential_present=credential_present,
        credential_source=credential_source,
    )


def _credential_present(auth_env: str, settings_env: dict[str, Any]) -> tuple[bool, str]:
    if auth_env and settings_env.get(auth_env):
        return True, "settings.env"
    if auth_env and os.environ.get(auth_env):
        return True, "process.env"
    return False, ""


def _safe_env_item(name: str, value: Any, *, source: str) -> dict[str, Any]:
    text = "" if value is None else str(value)
    item: dict[str, Any] = {"name": name, "source": source, "set": bool(text)}
    if _is_secret_name(name):
        item.update({"value": "<redacted>" if text else None, "length": len(text), "sha256": _short_hash(text) if text else ""})
    else:
        item["value"] = text if text else None
    return item


def _is_secret_name(name: str) -> bool:
    upper = name.upper()
    if any(marker in upper for marker in ("API_KEY", "AUTH_TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")):
        return True
    return upper.endswith("_TOKEN")


def _scan_object_for_secret_values(payload: Any) -> list[str]:
    hits: list[str] = []

    def visit(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                visit(child_value, str(child_key))
        elif isinstance(value, list):
            for item in value:
                visit(item, key)
        elif isinstance(value, str) and _is_secret_name(key) and value and value not in PROVIDER_AUTH_KEYS:
            hits.append(key)

    visit(payload)
    return sorted(set(hits))


def _check_value(key: str, expected: Any, actual: Any) -> dict[str, Any]:
    return {"key": key, "expected": expected, "actual": actual, "ok": str(actual) == str(expected)}


def _run_command(command: list[str], *, timeout_seconds: int) -> dict[str, Any]:
    executable = shutil.which(command[0])
    if not executable:
        return {"exit_code": 127, "summary": f"{command[0]} command not found", "command": command}
    try:
        completed = subprocess.run(
            [executable, *command[1:]],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": 127, "summary": str(exc), "command": command}
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return {"exit_code": completed.returncode, "summary": output, "command": command}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _merge_unique(current: list[Any], additions: list[str]) -> list[str]:
    result = [str(item) for item in current]
    seen = set(result)
    for item in additions:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
