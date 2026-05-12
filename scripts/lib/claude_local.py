from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROVIDER_PROFILES_FILE = "provider-profiles.json"
CLAUDE_USAGE_NOTE = "Third-party provider usage and quota data is not exposed through a stable Claude Code local API."
CLAUDE_SESSION_CONTINUITY_NOTE = (
    "Claude Code resume continuity is anchored in the Claude home transcript directories. "
    "CC Switch owns provider switching; this repository only verifies that the same Claude home remains visible unless isolation is intentional."
)


def _windows_no_window_kwargs() -> dict[str, Any]:
    if os.name != "nt":
        return {}
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return {"creationflags": creationflags} if creationflags else {}

COMMON_RECOMMENDED_ENV = {
    "CLAUDE_CODE_EFFORT_LEVEL": "high",
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
            "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "70",
            "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "100000",
            "CLAUDE_CODE_SUBAGENT_MODEL": "glm-4.5-air",
        },
        "note": "Recommended GLM profile for this machine: keep effective coding context around 80k-120k and compact early instead of pushing the full 200k window.",
    },
    {
        "name": "deepseek-v4",
        "label": "DeepSeek v4",
        "provider": "deepseek",
        "base_url": "https://api.deepseek.com/anthropic",
        "auth_env": "ANTHROPIC_AUTH_TOKEN",
        "docs_url": "https://api-docs.deepseek.com/guides/anthropic_api",
        "models": {
            "opus": "deepseek-v4-pro",
            "sonnet": "deepseek-v4-pro",
            "haiku": "deepseek-v4-flash",
        },
        "env": {
            "API_TIMEOUT_MS": "1800000",
            "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-pro",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash",
            "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "70",
            "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "450000",
            "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-v4-flash",
        },
        "note": "Recommended DeepSeek profile for this machine: use the 1M alias as headroom, but keep the effective coding context around 250k-500k with early compaction.",
    },
]

CLAUDE_PROVIDER_MANAGEMENT_DISABLED_ERROR = "project_managed_claude_switching_disabled"
CLAUDE_PROVIDER_MANAGEMENT_DISABLED_MESSAGE = (
    "Project-managed Claude Code/Desktop account/API switching is disabled. "
    "Use CC Switch for Claude Code and Claude Desktop account/API/provider changes; "
    "this repository only performs read-only Claude status and session-continuity diagnostics."
)


def provider_management_disabled(action: str, *, home: Path | None = None, dry_run: bool | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": "error",
        "error": CLAUDE_PROVIDER_MANAGEMENT_DISABLED_ERROR,
        "action": action,
        "message": CLAUDE_PROVIDER_MANAGEMENT_DISABLED_MESSAGE,
        "owner": "CC Switch",
        "repo_policy": "read_only_diagnostics_only",
        "changed": False,
    }
    if home is not None:
        payload["claude_home"] = str(claude_home(str(home)))
    if dry_run is not None:
        payload["dry_run"] = dry_run
    return payload

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
    if isinstance(payload.get("active"), str) and payload["active"]:
        active_name = payload["active"]
    profiles = [_provider_from_payload(profile, settings, active_name) for profile in _provider_payloads(payload)]
    return profiles


def write_default_provider_profiles(home: Path | None = None, *, active: str | None = None, overwrite: bool = False) -> dict[str, Any]:
    return provider_management_disabled("write_default_provider_profiles", home=home)


def claude_status(home: Path | None = None, *, cc_switch_db: Path | None = None) -> dict[str, Any]:
    home = claude_home(str(home) if home else None)
    payload = {
        "claude_home": str(home),
        "command": _run_command(["claude", "--version"], timeout_seconds=15),
        "settings": settings_summary(home),
        "providers": [profile.to_dict() for profile in load_provider_profiles(home)],
        "active_provider": active_provider(home),
        "session_continuity": session_continuity_status(home),
        "config": config_health(home),
        "mcp": _run_command(["claude", "mcp", "list"], timeout_seconds=30),
        "usage": {
            "source": "provider",
            "windows": [],
            "note": CLAUDE_USAGE_NOTE,
        },
    }
    if cc_switch_db:
        payload["cc_switch"] = cc_switch_status(cc_switch_db)
    return payload


def session_continuity_status(home: Path | None = None) -> dict[str, Any]:
    home = claude_home(str(home) if home else None)
    projects_dir = home / "projects"
    sessions_dir = home / "sessions"
    history_path = home / "history.jsonl"
    file_history_dir = home / "file-history"
    claude_config_dir = os.environ.get("CLAUDE_CONFIG_DIR") or ""

    project_transcript_count = _count_files(projects_dir, "*.jsonl")
    session_record_count = _count_files(sessions_dir, "*.jsonl")
    checks = [
        _check_value("claude_home.exists", True, home.exists()),
        _check_value("projects.exists", True, projects_dir.exists()),
        _check_value("history_jsonl.exists", True, history_path.exists()),
        {
            "key": "provider_switch_preserves_home",
            "expected": "same Claude home remains visible across CC Switch provider changes",
            "actual": "read-only continuity diagnostic; project-managed switch_provider is disabled",
            "ok": True,
        },
    ]
    has_resume_artifact = bool(project_transcript_count or session_record_count or history_path.exists())
    checks.append(
        {
            "key": "resume_artifacts.present",
            "expected": "projects/*.jsonl, sessions/*.jsonl, or history.jsonl",
            "actual": {
                "project_transcript_count": project_transcript_count,
                "session_record_count": session_record_count,
                "history_jsonl": history_path.exists(),
            },
            "ok": has_resume_artifact,
        }
    )

    return {
        "status": "ok" if all(check["ok"] for check in checks) else "attention",
        "note": CLAUDE_SESSION_CONTINUITY_NOTE,
        "claude_home": str(home),
        "claude_config_dir_env": claude_config_dir or None,
        "provider_switch_policy": "preserve_claude_home",
        "resume_commands": ["claude --continue", "claude --resume", "/resume"],
        "paths": {
            "projects": {"path": str(projects_dir), "exists": projects_dir.exists(), "jsonl_count": project_transcript_count},
            "sessions": {"path": str(sessions_dir), "exists": sessions_dir.exists(), "jsonl_count": session_record_count},
            "history": {"path": str(history_path), "exists": history_path.exists(), "bytes": history_path.stat().st_size if history_path.exists() else 0},
            "file_history": {"path": str(file_history_dir), "exists": file_history_dir.exists()},
        },
        "checks": checks,
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


def switch_provider(
    name: str,
    home: Path | None = None,
    *,
    dry_run: bool = False,
    cc_switch_db: Path | None = None,
) -> dict[str, Any]:
    normalized = str(name or "").strip()
    if not normalized:
        return {"status": "error", "error": "missing provider profile name"}
    return provider_management_disabled("switch", home=home, dry_run=dry_run)


def cc_switch_status(db_path: Path) -> dict[str, Any]:
    providers = _load_cc_switch_claude_providers(db_path)
    return {
        "path": str(db_path),
        "exists": db_path.exists(),
        "provider_count": len(providers),
        "current": next((_redacted_cc_switch_provider(provider) for provider in providers if provider.get("is_current")), None),
        "providers": [_redacted_cc_switch_provider(provider) for provider in providers],
    }


def delete_provider_profile(name: str, home: Path | None = None, *, dry_run: bool = False) -> dict[str, Any]:
    normalized = str(name or "").strip()
    if not normalized:
        return {"status": "error", "error": "missing provider profile name"}
    return provider_management_disabled("delete", home=home, dry_run=dry_run)


def optimize_claude_local(
    home: Path | None = None,
    *,
    provider_name: str = "bigmodel-glm",
    apply: bool = False,
    install_switcher: bool = True,
) -> dict[str, Any]:
    return provider_management_disabled("optimize", home=home, dry_run=not apply)


def preview_default_provider_profiles(home: Path | None = None, *, active: str | None = None) -> dict[str, Any]:
    home = claude_home(str(home) if home else None)
    path = provider_profiles_path(home)
    if path.exists():
        payload = _load_provider_profiles_payload(home)
    else:
        payload = {
            "schema_version": 1,
            "profiles": DEFAULT_PROVIDER_PROFILES,
        }
    updated = _default_provider_profiles_payload(home, payload, active=active)
    return {
        "status": "dry_run",
        "changed": (not path.exists()) or payload != updated,
        "path": str(path),
        "active": updated.get("active"),
        "profile_count": len(_provider_payloads(updated)),
    }


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


def backup_provider_profiles(home: Path | None = None) -> Path:
    home = claude_home(str(home) if home else None)
    path = provider_profiles_path(home)
    if not path.exists():
        raise FileNotFoundError(f"missing Claude provider profiles: {path}")
    backup_dir = home / "provider-profiles-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"provider-profiles-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    shutil.copyfile(path, backup_path)
    return backup_path


def install_provider_switcher(home: Path | None = None, bin_dir: Path | None = None) -> dict[str, Any]:
    return provider_management_disabled("install", home=home)


def _optimized_settings(settings: dict[str, Any], profile: ClaudeProviderProfile) -> dict[str, Any]:
    updated = deepcopy(settings)
    env = dict(_dict(updated.get("env")))
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


def _default_provider_profiles_payload(home: Path, payload: dict[str, Any], *, active: str | None = None) -> dict[str, Any]:
    updated = dict(payload)
    retired_profiles = _retired_provider_names(updated)
    if active and active in retired_profiles:
        retired_profiles.remove(active)
        updated["retired_profiles"] = sorted(retired_profiles)
    expected_active = active or updated.get("active") or _detect_active_provider_name(load_settings(home)) or DEFAULT_PROVIDER_PROFILES[0]["name"]
    updated["active"] = expected_active
    updated["schema_version"] = updated.get("schema_version") or 1
    updated["profiles"] = _merge_provider_profiles(updated.get("profiles"), retired_names=retired_profiles)
    return updated


def _set_active_provider_name(home: Path, name: str) -> None:
    payload = _load_provider_profiles_payload(home)
    payload["active"] = name
    if "profiles" not in payload:
        payload["profiles"] = DEFAULT_PROVIDER_PROFILES
    retired_profiles = _retired_provider_names(payload)
    if name in retired_profiles:
        retired_profiles.remove(name)
        payload["retired_profiles"] = sorted(retired_profiles)
        payload["profiles"] = _merge_provider_profiles(payload.get("profiles"), retired_names=retired_profiles)
    _write_json(provider_profiles_path(home), payload)


def _detect_active_provider_name(settings: dict[str, Any]) -> str:
    env = _dict(settings.get("env"))
    base_url = str(env.get("ANTHROPIC_BASE_URL") or "").rstrip("/")
    for profile in DEFAULT_PROVIDER_PROFILES:
        if base_url == str(profile["base_url"]).rstrip("/"):
            return str(profile["name"])
    return ""


def _retired_provider_names(payload: dict[str, Any]) -> set[str]:
    raw = payload.get("retired_profiles")
    if not isinstance(raw, list):
        return set()
    return {name for name in (str(item).strip() for item in raw) if name}


def _provider_payloads(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_profiles = payload.get("profiles") if isinstance(payload.get("profiles"), list) else DEFAULT_PROVIDER_PROFILES
    retired_names = _retired_provider_names(payload)
    return [
        profile
        for profile in raw_profiles
        if isinstance(profile, dict) and str(profile.get("name") or "") not in retired_names
    ]


def _merge_provider_profiles(existing: Any, *, retired_names: set[str] | None = None) -> list[dict[str, Any]]:
    retired_names = set(retired_names or set())
    existing_list = existing if isinstance(existing, list) else []
    existing_by_name = {
        str(item.get("name")): deepcopy(item)
        for item in existing_list
        if isinstance(item, dict) and item.get("name") and str(item.get("name")) not in retired_names
    }
    merged: list[dict[str, Any]] = []
    for default_profile in DEFAULT_PROVIDER_PROFILES:
        name = str(default_profile["name"])
        if name in retired_names:
            continue
        current = existing_by_name.pop(name, {})
        merged_profile = deepcopy(default_profile)
        if isinstance(current, dict):
            if isinstance(current.get("models"), dict):
                for key, value in current["models"].items():
                    key_text = str(key)
                    if key_text not in merged_profile["models"]:
                        merged_profile["models"][key_text] = str(value)
            if isinstance(current.get("env"), dict):
                for key, value in current["env"].items():
                    key_text = str(key)
                    if key_text not in merged_profile["env"]:
                        merged_profile["env"][key_text] = str(value)
            for key, value in current.items():
                if key not in merged_profile:
                    merged_profile[str(key)] = deepcopy(value)
        merged.append(merged_profile)
    for leftover in existing_by_name.values():
        merged.append(deepcopy(leftover))
    return merged


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


def _load_cc_switch_claude_providers(db_path: Path) -> list[dict[str, Any]]:
    path = Path(db_path).expanduser()
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    conn = sqlite3.connect(path)
    try:
        conn.row_factory = sqlite3.Row
        for row in conn.execute(
            """
            select id, name, settings_config, website_url, category, is_current
            from providers
            where app_type = 'claude'
            order by is_current desc, name
            """
        ):
            config = _loads_json_object(row["settings_config"])
            env = _dict(config.get("env"))
            rows.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "website_url": row["website_url"],
                    "category": row["category"],
                    "is_current": bool(row["is_current"]),
                    "model": config.get("model"),
                    "env": env,
                    "base_url": str(env.get("ANTHROPIC_BASE_URL") or ""),
                }
            )
    finally:
        conn.close()
    return rows


def _matching_cc_switch_provider(name: str, target: ClaudeProviderProfile, db_path: Path | None) -> dict[str, Any] | None:
    if not db_path:
        return None
    normalized = name.casefold()
    target_base_url = target.base_url.rstrip("/")
    for provider in _load_cc_switch_claude_providers(db_path):
        provider_name = str(provider.get("name") or "").casefold()
        provider_base_url = str(provider.get("base_url") or "").rstrip("/")
        if normalized in {provider_name, provider_base_url.casefold()}:
            return provider
        if target.provider and target.provider.casefold() in provider_name:
            return provider
        if target_base_url and provider_base_url == target_base_url:
            return provider
    return None


def _redacted_cc_switch_provider(provider: dict[str, Any] | None) -> dict[str, Any] | None:
    if not provider:
        return None
    redacted = {key: value for key, value in provider.items() if key != "env"}
    redacted["env"] = [_safe_env_item(str(key), value, source="cc-switch.db") for key, value in sorted(_dict(provider.get("env")).items())]
    return redacted


def _loads_json_object(value: Any) -> dict[str, Any]:
    if not isinstance(value, str) or not value.strip():
        return {}
    try:
        payload = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


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
            **_windows_no_window_kwargs(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": 127, "summary": str(exc), "command": command}
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return {"exit_code": completed.returncode, "summary": output, "command": command}


def _count_files(root: Path, pattern: str) -> int:
    if not root.exists():
        return 0
    count = 0
    try:
        for _ in root.rglob(pattern):
            count += 1
            if count >= 10000:
                return count
    except OSError:
        return count
    return count


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
