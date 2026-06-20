from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib.parse import urlparse
from urllib import request as urllib_request


REQUIRED_CONFIG = {
    "cli_auth_credentials_store": "file",
    "model_context_window": 1000000,
    "model_auto_compact_token_limit": 810000,
    "sandbox_mode": "workspace-write",
    "approval_policy": "never",
    "web_search": "cached",
    "check_for_update_on_startup": False,
}
REFERENCE_CONFIG = {
    "model": "gpt-5.5",
    "model_reasoning_effort": "xhigh",
    "model_verbosity": "medium",
}
DEFAULT_CONFIG = {**REQUIRED_CONFIG, **REFERENCE_CONFIG}
DEFAULT_CONFIG_PROFILE = {
    "strategy": "efficiency_first",
    "strategy_label": "综合效率优先",
    "strategy_principles": [
        "少打扰",
        "自动连续执行",
        "节省 token / 成本",
        "保留必要解释",
        "高效率",
    ],
    "current_combo": "gpt-5.5 + xhigh + never",
    "current_combo_status": "current_default_choice",
    "compact_policy": "810000 on a 1000000 window",
    "compact_ratio": "81%",
    "manual_upgrade": "Switch to a stronger model or reasoning level manually when a task genuinely needs deeper reasoning.",
    "change_rule": "Future model or parameter updates should preserve the efficiency-first principle and necessary explanation rather than the current combo itself; existing safety and gate constraints continue to apply.",
}


def _windows_no_window_kwargs() -> dict[str, Any]:
    if os.name != "nt":
        return {}
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return {"creationflags": creationflags} if creationflags else {}
USAGE_DASHBOARD_URL = "https://chatgpt.com/codex/settings/usage"
USAGE_STALE_AFTER_SECONDS = 300
CHATGPT_ACCOUNT_CHECK_URL = "https://chatgpt.com/backend-api/wham/accounts/check"
CODEX_API_AUTH_MODE = "apikey"
COCKPIT_CODEX_DIR = Path.home() / ".antigravity_cockpit"
CONTEXT_COMPACT_RATIO_MIN = 0.75
CONTEXT_COMPACT_RATIO_MAX = 0.90
DEFAULT_CONTEXT_COMPACT_RATIO = 0.81
CONTEXT_COMPACT_GRANULARITY = 1000
GPT_53_CODEX_CONTEXT_REFERENCE = {
    "model": "gpt-5.3-codex",
    "codex_context_window_tokens": 400000,
    "source_ref": "https://openai.com/index/introducing-gpt-5-3-codex",
    "enforcement": "informational_only_refresh_before_changing_defaults",
}
ACCOUNT_FACTS_FILENAME = "account-facts.json"


@dataclass(frozen=True)
class CodexAuthProfile:
    name: str
    file: str
    active: bool
    auth_mode: str
    api_base_url: str
    last_refresh: str
    email: str
    display_name: str
    account_label: str
    plan_type: str
    subscription_active_start: str
    subscription_active_until: str
    subscription_last_checked: str
    id_token_expires_at: str
    access_token_expires_at: str
    account_id: str
    account_hash: str
    sha256: str
    full_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "file": self.file,
            "active": self.active,
            "auth_mode": self.auth_mode,
            "api_base_url": self.api_base_url,
            "last_refresh": self.last_refresh,
            "email": self.email,
            "display_name": self.display_name,
            "account_label": self.account_label,
            "plan_type": self.plan_type,
            "subscription_active_start": self.subscription_active_start,
            "subscription_active_until": self.subscription_active_until,
            "subscription_last_checked": self.subscription_last_checked,
            "id_token_expires_at": self.id_token_expires_at,
            "access_token_expires_at": self.access_token_expires_at,
            "account_id": self.account_id,
            "account_hash": self.account_hash,
            "sha256": self.sha256,
            "full_name": self.full_name,
        }


def codex_home(value: str | None = None) -> Path:
    raw = value or os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    path = Path(raw).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Codex home does not exist: {path}")
    return path.resolve()


def list_auth_profiles(home: Path | None = None) -> list[CodexAuthProfile]:
    home = codex_home(str(home) if home else None)
    active_path = home / "auth.json"
    active_hash = _short_file_hash(active_path) if active_path.exists() else ""
    candidates: list[Path] = []
    candidates.extend(sorted(home.glob("auth*.json")))
    profiles_dir = home / "auth-profiles"
    if profiles_dir.exists():
        candidates.extend(sorted(profiles_dir.glob("*.json")))
    unique = sorted({path.resolve() for path in candidates})
    return [_auth_profile_from_path(path, active_hash) for path in unique]


def active_auth_status(home: Path | None = None) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    active_path = home / "auth.json"
    if not active_path.exists():
        return {"status": "missing", "error": f"missing active auth: {active_path}"}
    profile = _auth_profile_from_path(active_path, _short_file_hash(active_path))
    return {"status": "ok", "active_profile": profile.to_dict()}


def cockpit_codex_source_status(cockpit_dir: Path | None = None) -> dict[str, Any]:
    source_dir = (cockpit_dir or COCKPIT_CODEX_DIR).expanduser()
    index_path = source_dir / "codex_accounts.json"
    accounts_dir = source_dir / "codex_accounts"
    if not index_path.exists():
        return {
            "status": "missing",
            "source": "cockpit",
            "source_dir": str(source_dir),
            "index_path": str(index_path),
            "accounts": [],
            "error": "missing Cockpit Codex account index",
        }
    try:
        accounts = _load_cockpit_codex_accounts(source_dir)
    except Exception as exc:
        return {
            "status": "error",
            "source": "cockpit",
            "source_dir": str(source_dir),
            "index_path": str(index_path),
            "accounts_dir": str(accounts_dir),
            "accounts": [],
            "error": str(exc),
        }
    current_id = _load_cockpit_current_account_id(source_dir)
    summaries = [_summarize_import_candidate(candidate, current_id=current_id) for candidate in accounts]
    return {
        "status": "ok",
        "source": "cockpit",
        "source_dir": str(source_dir),
        "index_path": str(index_path),
        "accounts_dir": str(accounts_dir),
        "current_account_id": current_id,
        "total": len(summaries),
        "api_key_count": sum(1 for item in summaries if item.get("auth_mode") == CODEX_API_AUTH_MODE),
        "oauth_count": sum(1 for item in summaries if item.get("auth_mode") == "chatgpt"),
        "accounts": summaries,
    }


def probe_auth_profiles(
    home: Path | None = None,
    *,
    names: list[str] | None = None,
    include_oauth: bool = True,
    include_api: bool = True,
) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    selected = {str(name).strip() for name in (names or []) if str(name).strip()}
    results = []
    for profile in list_auth_profiles(home):
        if profile.file == "auth.json":
            continue
        if selected and profile.name not in selected and profile.file not in selected and profile.account_id not in selected:
            continue
        if profile.auth_mode == CODEX_API_AUTH_MODE and not include_api:
            continue
        if profile.auth_mode != CODEX_API_AUTH_MODE and not include_oauth:
            continue
        payload = _read_auth_json(Path(profile.full_name))
        results.append(_probe_codex_auth_payload(payload, label=profile.account_label or profile.name))
    ok_count = sum(1 for item in results if item.get("status") == "ok")
    return {
        "status": "ok" if ok_count == len(results) else "attention",
        "total": len(results),
        "ok": ok_count,
        "failed": len(results) - ok_count,
        "results": results,
    }


def probe_codex_api_account(base_url: str, api_key: str, *, timeout_seconds: int = 15) -> dict[str, Any]:
    normalized_base_url = _normalize_api_base_url(base_url)
    if not normalized_base_url:
        return {"attempted": True, "status": "error", "error": "missing API base URL"}
    if not _first_string(api_key):
        return {"attempted": True, "status": "error", "error": "missing OPENAI_API_KEY"}
    url = normalized_base_url.rstrip("/") + "/models"
    request = urllib_request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "governed-runtime-codex-api-probe",
        },
        method="GET",
    )
    started = time.time()
    try:
        with urllib_request.urlopen(request, timeout=timeout_seconds) as response:
            status_code = int(getattr(response, "status", 0) or 0)
            raw = response.read(256 * 1024)
    except urllib_error.HTTPError as exc:
        body = exc.read(4096).decode("utf-8", errors="replace")
        return {
            "attempted": True,
            "status": "error",
            "url": url,
            "http_status": exc.code,
            "elapsed_seconds": round(time.time() - started, 3),
            "error": _first_non_empty_line(body) or str(exc),
        }
    except (urllib_error.URLError, TimeoutError, OSError) as exc:
        return {
            "attempted": True,
            "status": "error",
            "url": url,
            "elapsed_seconds": round(time.time() - started, 3),
            "error": str(exc),
        }

    model_count = None
    try:
        payload = json.loads(raw.decode("utf-8", errors="replace"))
        if isinstance(payload, dict) and isinstance(payload.get("data"), list):
            model_count = len(payload["data"])
    except json.JSONDecodeError:
        payload = None
    return {
        "attempted": True,
        "status": "ok" if 200 <= status_code < 300 else "error",
        "url": url,
        "http_status": status_code,
        "elapsed_seconds": round(time.time() - started, 3),
        "model_count": model_count,
    }


def probe_codex_oauth_account(access_token: str, *, account_id: str = "", timeout_seconds: int = 15) -> dict[str, Any]:
    access_token = _first_string(access_token)
    if not access_token:
        return {"attempted": True, "status": "error", "error": "missing access_token"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "User-Agent": "governed-runtime-codex-oauth-probe",
    }
    if _first_string(account_id):
        headers["ChatGPT-Account-Id"] = _first_string(account_id)
    request = urllib_request.Request(CHATGPT_ACCOUNT_CHECK_URL, headers=headers, method="GET")
    started = time.time()
    try:
        with urllib_request.urlopen(request, timeout=timeout_seconds) as response:
            status_code = int(getattr(response, "status", 0) or 0)
            raw = response.read(256 * 1024)
    except urllib_error.HTTPError as exc:
        body = exc.read(4096).decode("utf-8", errors="replace")
        return {
            "attempted": True,
            "status": "error",
            "url": CHATGPT_ACCOUNT_CHECK_URL,
            "http_status": exc.code,
            "elapsed_seconds": round(time.time() - started, 3),
            "error": _first_non_empty_line(body) or str(exc),
        }
    except (urllib_error.URLError, TimeoutError, OSError) as exc:
        return {
            "attempted": True,
            "status": "error",
            "url": CHATGPT_ACCOUNT_CHECK_URL,
            "elapsed_seconds": round(time.time() - started, 3),
            "error": str(exc),
        }

    account_count = None
    try:
        payload = json.loads(raw.decode("utf-8", errors="replace"))
        if isinstance(payload, dict) and isinstance(payload.get("accounts"), list):
            account_count = len(payload["accounts"])
    except json.JSONDecodeError:
        pass
    return {
        "attempted": True,
        "status": "ok" if 200 <= status_code < 300 else "error",
        "url": CHATGPT_ACCOUNT_CHECK_URL,
        "http_status": status_code,
        "elapsed_seconds": round(time.time() - started, 3),
        "account_count": account_count,
    }


def codex_status(
    home: Path | None = None,
    *,
    refresh_online: bool = False,
    refresh_if_stale: bool = False,
) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    profiles = list_auth_profiles(home)
    accounts = _display_auth_profiles(profiles)
    usage_refresh = {
        "attempted": False,
        "status": "idle",
        "mode": "local_snapshot",
        "consumes_quota": False,
    }
    usage = _codex_usage_status(home)
    usage_cache = _load_usage_cache(home)
    active_account = next((account for account in accounts if account.get("active")), None)
    snapshot_status = active_auth_snapshot_status(home, profiles=profiles)
    if active_account:
        active_account["snapshot_status"] = snapshot_status
    accounts = _attach_cached_usage(accounts, usage_cache)
    active_account = next((account for account in accounts if account.get("active")), None)

    if refresh_online or (refresh_if_stale and _account_usage_needs_refresh(active_account)):
        usage, usage_refresh = _refresh_codex_usage_online(home, fallback_usage=usage)
        if active_account and _should_update_usage_cache_from_usage(usage=usage, usage_refresh=usage_refresh):
            usage_cache = _update_usage_cache(usage_cache, active_account, usage)
            _save_usage_cache(home, usage_cache)
            accounts = _attach_cached_usage(accounts, usage_cache)
            active_account = next((account for account in accounts if account.get("active")), None)

    if isinstance(active_account, dict) and not isinstance(active_account.get("usage_snapshot"), dict):
        if isinstance(usage, dict) and _usage_is_safe_for_account_display(usage):
            active_account["usage_snapshot"] = dict(usage)
    account_facts = _load_account_facts(home)
    accounts = _resolve_account_plan_types(accounts, account_facts)
    active_account = next((account for account in accounts if account.get("active")), None)
    resolved_plan_type = _resolve_active_plan_type(active_account, usage)
    if active_account and resolved_plan_type:
        active_account["plan_type"] = resolved_plan_type
    official_app_account = _discover_official_codex_app_account(accounts)
    if isinstance(official_app_account, dict):
        official_account_id = _first_string(official_app_account.get("account_id"))
        for account in accounts:
            account["official_app_current"] = bool(official_account_id and account.get("account_id") == official_account_id)
    payload: dict[str, Any] = {
        "codex_home": str(home),
        "auth": active_auth_status(home),
        "accounts": accounts,
        "config": config_health(home),
        "startup_health": codex_startup_health(home),
        "context_window_probe": context_window_probe(home, run_codex=False),
        "recommended_defaults": DEFAULT_CONFIG_PROFILE,
        "usage": usage,
        "usage_refresh": usage_refresh,
        "account_facts": {
            "path": str(_account_facts_path(home)),
            "status": account_facts.get("status", "missing") if isinstance(account_facts, dict) else "missing",
        },
        "snapshot_status": snapshot_status,
        "official_app_account": official_app_account,
    }
    payload["active_account"] = next((account for account in accounts if account.get("active")), None)
    payload["login_status"] = _run_codex_login_status()
    return payload


def active_auth_snapshot_status(home: Path | None = None, *, profiles: list[CodexAuthProfile] | None = None) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    profiles = profiles or list_auth_profiles(home)
    active_profile = next((profile for profile in profiles if profile.file == "auth.json"), None)
    if active_profile is None:
        return {"status": "missing_active_auth"}

    named_profiles = [profile for profile in profiles if profile.file != "auth.json" and profile.name != "auth"]
    matched = _find_named_snapshot_match(active_profile, named_profiles)
    if matched is None:
        return {
            "status": "missing_named_snapshot",
            "active_name": active_profile.name,
            "active_file": active_profile.file,
            "active_full_name": active_profile.full_name,
            "account_label": active_profile.account_label,
        }
    if matched.sha256 == active_profile.sha256:
        return {
            "status": "synced",
            "profile_name": matched.name,
            "profile_file": matched.file,
            "profile_full_name": matched.full_name,
            "account_label": active_profile.account_label,
        }
    return {
        "status": "drifted",
        "profile_name": matched.name,
        "profile_file": matched.file,
        "profile_full_name": matched.full_name,
        "active_last_refresh": active_profile.last_refresh,
        "saved_last_refresh": matched.last_refresh,
        "account_label": active_profile.account_label,
    }


def config_health(home: Path | None = None) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    config_path = home / "config.toml"
    if not config_path.exists():
        return {"status": "missing", "path": str(config_path), "checks": []}
    text = config_path.read_text(encoding="utf-8", errors="replace")
    checks = []
    for key, expected in REQUIRED_CONFIG.items():
        actual = _find_top_level_value(text, key)
        checks.append(
            {
                "key": key,
                "expected": expected,
                "actual": actual,
                "ok": str(actual) == str(expected),
            }
        )
    advisory_checks = []
    for key, expected in REFERENCE_CONFIG.items():
        actual = _find_top_level_value(text, key)
        advisory_checks.append(
            {
                "key": key,
                "reference": expected,
                "actual": actual,
                "matches_reference": str(actual) == str(expected),
                "blocking": False,
            }
        )
    secret_hits = []
    for marker in ("ANTHROPIC_AUTH_TOKEN", "ctx7" + "sk", "sk-"):
        if marker in text:
            secret_hits.append(marker)
    return {
        "status": "ok" if all(check["ok"] for check in checks) and not secret_hits else "attention",
        "path": str(config_path),
        "auth_projection": {
            "model_provider": _find_top_level_value(text, "model_provider"),
            "forced_login_method": _find_top_level_value(text, "forced_login_method"),
            "openai_base_url": _find_top_level_value(text, "openai_base_url"),
            "history_bucket": _find_top_level_value(text, "model_provider") or "unknown",
        },
        "checks": checks,
        "advisory_checks": advisory_checks,
        "secret_like_markers": secret_hits,
    }


def codex_startup_health(home: Path | None = None) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    config_path = home / "config.toml"
    text = config_path.read_text(encoding="utf-8", errors="replace") if config_path.exists() else ""
    checks = [
        _startup_check_remote_plugin_sync(text),
        _startup_check_invalid_chrome_plugin(home, text),
        _startup_check_stdio_mcp_count(text),
        _startup_check_postgres_mcp_secret_exposure(text),
        _startup_check_logs_db_size(home),
        _startup_check_recent_log_failures(home),
    ]
    attention = [check for check in checks if check["status"] == "attention"]
    return {
        "status": "attention" if attention else "ok",
        "path": str(config_path),
        "checks": checks,
        "summary": [check["id"] for check in attention],
    }


def _startup_check_remote_plugin_sync(text: str) -> dict[str, Any]:
    actual = _find_top_level_value(text, "check_for_update_on_startup")
    return {
        "id": "startup_update_check_disabled",
        "status": "pass" if actual is False else "attention",
        "actual": actual,
        "reason": "Startup update checks should stay disabled on this host because failed remote plugin/app sync adds startup latency.",
        "remediation": 'Set top-level check_for_update_on_startup = false.',
    }


def _startup_check_invalid_chrome_plugin(home: Path, text: str) -> dict[str, Any]:
    enabled = _plugin_enabled(text, "chrome@openai-bundled")
    plugin_dir = home / "plugins" / "cache" / "openai-bundled" / "chrome"
    has_plugin_json = any(path.name == "plugin.json" for path in plugin_dir.glob("*/plugin.json")) if plugin_dir.exists() else False
    invalid_enabled = enabled is True and not has_plugin_json
    return {
        "id": "invalid_chrome_plugin_disabled",
        "status": "attention" if invalid_enabled else "pass",
        "enabled": enabled,
        "has_plugin_json": has_plugin_json,
        "path": str(plugin_dir),
        "reason": "The bundled chrome plugin should not be enabled when its cached plugin.json is missing.",
        "remediation": 'Set [plugins."chrome@openai-bundled"].enabled = false or refresh the bundled plugin cache.',
    }


def _startup_check_stdio_mcp_count(text: str) -> dict[str, Any]:
    stdio_count = len(re.findall(r'(?ms)^\[mcp_servers\.[^\]]+\].*?^\s*transport\s*=\s*"stdio"', text))
    return {
        "id": "stdio_mcp_startup_surface",
        "status": "attention" if stdio_count > 4 else "pass",
        "stdio_server_count": stdio_count,
        "threshold": 4,
        "reason": "Each stdio MCP server can spawn cold-start subprocesses during Codex session startup.",
        "remediation": "Keep frequently used stdio MCP servers enabled and move rarely used ones to on-demand profiles.",
    }


def _startup_check_postgres_mcp_secret_exposure(text: str) -> dict[str, Any]:
    block = _toml_table_block(text, "mcp_servers.postgres")
    unsafe = "server-postgres $conn" in block or "POSTGRES_CONNECTION_STRING" in block and "pwsh" in block
    return {
        "id": "postgres_mcp_connection_string_not_in_process_args",
        "status": "attention" if unsafe else "pass",
        "configured": bool(block),
        "reason": "The postgres MCP connection string should not be expanded into long-lived process command lines.",
        "remediation": "Use the local mcp-postgres-env-wrapper.mjs wrapper so only POSTGRES_CONNECTION_STRING environment state carries the secret.",
    }


def _startup_check_logs_db_size(home: Path) -> dict[str, Any]:
    db = home / "logs_2.sqlite"
    size = db.stat().st_size if db.exists() else 0
    threshold = 1024 * 1024 * 1024
    return {
        "id": "logs_sqlite_size_under_1gb",
        "status": "attention" if size > threshold else "pass",
        "path": str(db),
        "bytes": size,
        "threshold_bytes": threshold,
        "reason": "Large local Codex logs increase backup, scan, and startup-adjacent I/O risk even when SQLite integrity is healthy.",
        "remediation": "Archive or compact old logs after stopping Codex App/CLI processes.",
    }


def _startup_check_recent_log_failures(home: Path) -> dict[str, Any]:
    log = home / "log" / "codex-tui.log"
    if not log.exists():
        return {
            "id": "recent_startup_log_failures",
            "status": "pass",
            "path": str(log),
            "matches": {},
        }
    try:
        with log.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - 1_000_000))
            tail = handle.read().decode("utf-8", errors="replace")
    except OSError:
        tail = ""
    patterns = {
        "remote_plugin_sync_failed": "startup remote plugin sync failed",
        "cloudflare_403": "403 Forbidden",
        "invalid_chrome_plugin": "missing or invalid plugin.json plugin=\"chrome@openai-bundled\"",
        "apps_list_fallback": "failed to load full apps list",
    }
    matches = {key: tail.count(pattern) for key, pattern in patterns.items()}
    failed = any(count > 0 for count in matches.values())
    return {
        "id": "recent_startup_log_failures",
        "status": "attention" if failed else "pass",
        "path": str(log),
        "matches": matches,
        "reason": "Recent startup logs should not contain repeated plugin sync, Cloudflare 403, invalid plugin, or apps-list fallback failures.",
        "remediation": "Disable invalid local plugins and keep remote plugin/app sync out of the startup critical path.",
    }


def _plugin_enabled(text: str, plugin_id: str) -> bool | None:
    block = _toml_table_block(text, f'plugins."{plugin_id}"')
    if not block:
        return None
    value = re.search(r'(?m)^\s*enabled\s*=\s*(true|false)\s*$', block)
    if not value:
        return None
    return value.group(1) == "true"


def _toml_table_block(text: str, table: str) -> str:
    match = re.search(rf'(?m)^\[{re.escape(table)}\]\s*$', text)
    if not match:
        return ""
    next_header = re.search(r"(?m)^\[", text[match.end() :])
    end = match.end() + next_header.start() if next_header else len(text)
    return text[match.start() : end]


def context_window_probe(
    home: Path | None = None,
    *,
    run_codex: bool = False,
    bundled: bool = True,
    probe_all_catalogs: bool = False,
    probe_exec: bool = False,
    codex_binary: str | None = None,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    config_path = home / "config.toml"
    if not config_path.exists():
        return {
            "status": "platform_na",
            "reason": f"missing Codex config: {config_path}",
            "config_path": str(config_path),
            "checks": [],
        }

    text = config_path.read_text(encoding="utf-8", errors="replace")
    model = _first_string(_find_top_level_value(text, "model")) or str(DEFAULT_CONFIG["model"])
    configured_context = _coerce_int(_find_top_level_value(text, "model_context_window"))
    configured_compact = _coerce_int(_find_top_level_value(text, "model_auto_compact_token_limit"))
    compact_ratio = (
        round(configured_compact / configured_context, 4)
        if configured_context and configured_compact
        else None
    )

    checks = [
        {
            "check_id": "context_window_configured",
            "status": "pass" if configured_context and configured_context > 0 else "fail",
            "reason": "model_context_window must be present and positive.",
        },
        {
            "check_id": "auto_compact_configured",
            "status": "pass" if configured_compact and configured_compact > 0 else "fail",
            "reason": "model_auto_compact_token_limit must be present and positive.",
        },
        {
            "check_id": "auto_compact_below_context_window",
            "status": "pass" if configured_context and configured_compact and configured_compact < configured_context else "fail",
            "reason": "Auto compact must trigger before the configured context window is exhausted.",
        },
        {
            "check_id": "auto_compact_ratio_in_guard_band",
            "status": "pass"
            if compact_ratio is not None and CONTEXT_COMPACT_RATIO_MIN <= compact_ratio <= CONTEXT_COMPACT_RATIO_MAX
            else "fail",
            "reason": f"Auto compact ratio should stay between {CONTEXT_COMPACT_RATIO_MIN:.0%} and {CONTEXT_COMPACT_RATIO_MAX:.0%}.",
        },
    ]

    catalog_probe = {
        "status": "not_run",
        "reason": "Run with run_codex=true to inspect the local Codex model catalog.",
        "command": None,
    }
    catalog_probes: list[dict[str, Any]] = []
    context_settings_decision = _context_settings_decision(
        model=model,
        configured_context=configured_context,
        configured_compact=configured_compact,
        catalog_probes=catalog_probes,
    )
    exec_probe = {
        "status": "not_run",
        "reason": "Run with probe_exec=true to validate the configured context settings through a minimal Codex exec request.",
        "command": None,
        "consumes_quota": True,
    }
    recommendation = "keep_current" if all(check["status"] == "pass" for check in checks) else "fix_config"
    if run_codex:
        catalog_modes = ["bundled", "refreshed"] if probe_all_catalogs else ["bundled" if bundled else "refreshed"]
        for catalog_mode in catalog_modes:
            probe = _probe_codex_model_catalog(
                model=model,
                bundled=catalog_mode == "bundled",
                codex_binary=codex_binary,
                timeout_seconds=timeout_seconds,
            )
            catalog_probes.append(probe)
            checks.append(
                {
                    "check_id": f"local_{catalog_mode}_catalog_probe_available",
                    "status": "pass" if probe.get("status") == "pass" else "platform_na",
                    "reason": "The local Codex debug models catalog must be readable before using catalog-derived context recommendations.",
                }
            )
            model_info = probe.get("model")
            if isinstance(model_info, dict):
                catalog_context = _coerce_int(model_info.get("context_window"))
                catalog_max_context = _coerce_int(model_info.get("max_context_window"))
                if catalog_max_context is not None and configured_context is not None:
                    checks.append(
                        {
                            "check_id": f"configured_context_within_{catalog_mode}_catalog_max",
                            "status": "pass" if configured_context <= catalog_max_context else "fail",
                            "reason": "Configured context must not exceed the model catalog maximum.",
                            "expected_max": catalog_max_context,
                            "actual": configured_context,
                        }
                    )
                if catalog_context is not None and configured_context is not None:
                    checks.append(
                        {
                            "check_id": f"configured_context_matches_{catalog_mode}_catalog",
                            "status": "pass" if configured_context == catalog_context else "fail",
                            "reason": "Configured context should match the local Codex debug models catalog before changing defaults.",
                            "expected": catalog_context,
                            "actual": configured_context,
                        }
                    )
        if len(catalog_probes) > 1:
            checks.append(_catalogs_agree_check(catalog_probes))
        catalog_probe = catalog_probes[0] if catalog_probes else catalog_probe
        context_settings_decision = _context_settings_decision(
            model=model,
            configured_context=configured_context,
            configured_compact=configured_compact,
            catalog_probes=catalog_probes,
        )
        if context_settings_decision.get("model_context_window") is not None and configured_context is not None:
            checks.append(
                {
                    "check_id": "configured_context_matches_context_settings_decision",
                    "status": "pass" if configured_context == context_settings_decision.get("model_context_window") else "fail",
                    "reason": "Configured context should match the value selected from bundled/refreshed debug models evidence.",
                    "expected": context_settings_decision.get("model_context_window"),
                    "actual": configured_context,
                }
            )
        if context_settings_decision.get("model_auto_compact_token_limit") is not None and configured_compact is not None:
            checks.append(
                {
                    "check_id": "configured_auto_compact_matches_context_settings_decision",
                    "status": "pass"
                    if configured_compact == context_settings_decision.get("model_auto_compact_token_limit")
                    else "fail",
                    "reason": "Configured auto compact threshold should match the value selected from the context settings decision.",
                    "expected": context_settings_decision.get("model_auto_compact_token_limit"),
                    "actual": configured_compact,
                }
            )

    if probe_exec:
        exec_probe = _probe_codex_context_settings_exec(
            model=model,
            configured_context=configured_context,
            configured_compact=configured_compact,
            codex_binary=codex_binary,
            timeout_seconds=max(timeout_seconds, 90),
        )
        checks.append(
            {
                "check_id": "codex_exec_accepts_context_settings",
                "status": "pass" if exec_probe.get("status") == "pass" else "platform_na",
                "reason": "A minimal Codex exec probe should accept the configured context window and auto-compact values.",
            }
        )

    failed = [check for check in checks if check["status"] != "pass"]
    if failed:
        recommendation = "probe_before_changing_defaults" if run_codex or probe_exec else "run_catalog_probe"
    elif context_settings_decision.get("action") == "update_config":
        recommendation = "align_config_to_context_settings_decision"
    return {
        "status": "pass" if not failed else "attention",
        "config_path": str(config_path),
        "model": model,
        "configured_context_window": configured_context,
        "configured_auto_compact_token_limit": configured_compact,
        "compact_ratio": compact_ratio,
        "recommended_defaults": {
            "model_context_window": DEFAULT_CONFIG["model_context_window"],
            "model_auto_compact_token_limit": DEFAULT_CONFIG["model_auto_compact_token_limit"],
        },
        "external_reference": GPT_53_CODEX_CONTEXT_REFERENCE if model == "gpt-5.3-codex" else None,
        "catalog_probe": catalog_probe,
        "catalog_probes": catalog_probes,
        "exec_probe": exec_probe,
        "context_settings_decision": context_settings_decision,
        "checks": checks,
        "recommendation": recommendation,
    }


def _auth_profile_from_path(path: Path, active_hash: str) -> CodexAuthProfile:
    payload = _read_auth_json(path)
    tokens = payload.get("tokens") if isinstance(payload.get("tokens"), dict) else {}
    auth_mode = _auth_mode_from_payload(payload)
    api_key = _api_key_from_auth_payload(payload)
    account_id = _first_string(tokens.get("account_id"), payload.get("account_id"))
    if not account_id and auth_mode == CODEX_API_AUTH_MODE and api_key:
        account_id = f"codex_apikey_{hashlib.sha256(api_key.encode('utf-8')).hexdigest()[:24]}"
    file_hash = _short_file_hash(path)
    claims = _auth_claims(payload, tokens)
    account_hash = _short_string_hash(account_id) if account_id else ""
    api_base_url = _normalize_api_base_url(
        _first_string(payload.get("api_base_url"), payload.get("base_url"), payload.get("OPENAI_BASE_URL"))
    )
    account_label = _first_string(
        payload.get("api_provider_name") if auth_mode == CODEX_API_AUTH_MODE else "",
        _api_base_url_display_name(api_base_url) if auth_mode == CODEX_API_AUTH_MODE else "",
        payload.get("account_label"),
        payload.get("label"),
        claims["email"],
        claims["display_name"],
        path.stem if auth_mode == CODEX_API_AUTH_MODE and path.stem != "auth" else "",
        account_hash,
        path.stem,
    )
    return CodexAuthProfile(
        name=path.stem,
        file=path.name,
        active=file_hash == active_hash,
        auth_mode=auth_mode,
        api_base_url=api_base_url,
        last_refresh=str(payload.get("last_refresh") or ""),
        email=claims["email"],
        display_name=claims["display_name"],
        account_label=account_label,
        plan_type=claims["plan_type"],
        subscription_active_start=claims["subscription_active_start"],
        subscription_active_until=claims["subscription_active_until"],
        subscription_last_checked=claims["subscription_last_checked"],
        id_token_expires_at=claims["id_token_expires_at"],
        access_token_expires_at=claims["access_token_expires_at"],
        account_id=account_id,
        account_hash=account_hash,
        sha256=file_hash,
        full_name=str(path),
    )


def _display_auth_profiles(profiles: list[CodexAuthProfile]) -> list[dict[str, Any]]:
    grouped: dict[str, list[CodexAuthProfile]] = {}
    for profile in profiles:
        group_key = _display_group_key(profile)
        grouped.setdefault(group_key, []).append(profile)

    rendered: list[dict[str, Any]] = []
    for duplicates in grouped.values():
        preferred = _select_display_profile(duplicates)
        rendered_profile = preferred.to_dict()
        rendered_profile["active"] = any(profile.active for profile in duplicates)
        rendered_profile["switchable"] = _profile_is_switchable(preferred)
        if preferred.auth_mode == CODEX_API_AUTH_MODE and not preferred.api_base_url:
            rendered_profile["switch_block_reason"] = "missing_api_base_url"
        rendered_profile["duplicate_count"] = len(duplicates)
        rendered_profile["hidden_duplicate_names"] = [
            profile.name for profile in duplicates if profile.full_name != preferred.full_name
        ]
        rendered.append(rendered_profile)

    return sorted(rendered, key=lambda item: (0 if item.get("active") else 1, item.get("name") or item.get("file") or ""))


def _display_profile_rank(profile: CodexAuthProfile) -> tuple[int, int, str]:
    # Prefer named saved profiles over the auth.json live mirror when both point to the same account snapshot.
    return (
        0 if _profile_is_switchable(profile) else 1,
        1 if profile.name == "auth" else 0,
        0 if profile.active else 1,
        profile.name,
    )


def _display_group_key(profile: CodexAuthProfile) -> str:
    normalized_email = _normalized_profile_email(profile)
    if profile.auth_mode != CODEX_API_AUTH_MODE and normalized_email:
        return f"oauth-email:{normalized_email}"
    if profile.account_id:
        return f"account:{profile.account_id}"
    if profile.account_hash:
        return f"hash:{profile.account_hash}"
    return f"file:{profile.sha256 or profile.full_name}"


def _select_display_profile(duplicates: list[CodexAuthProfile]) -> CodexAuthProfile:
    active_profile = next((profile for profile in duplicates if profile.active), None)
    if active_profile is not None:
        exact_named_mirror = [
            profile
            for profile in duplicates
            if profile.name != "auth" and profile.sha256 == active_profile.sha256
        ]
        if exact_named_mirror:
            return min(exact_named_mirror, key=_display_profile_rank)
        if not _profile_is_switchable(active_profile):
            switchable = [profile for profile in duplicates if _profile_is_switchable(profile)]
            if switchable:
                return min(switchable, key=_display_profile_rank)
        return active_profile
    switchable = [profile for profile in duplicates if _profile_is_switchable(profile)]
    candidates = switchable or duplicates
    return max(candidates, key=lambda profile: (profile.last_refresh or "", 0 if profile.name != "auth" else 1, profile.name))


def _profile_is_switchable(profile: CodexAuthProfile) -> bool:
    if profile.auth_mode == CODEX_API_AUTH_MODE:
        return bool(profile.api_base_url)
    return bool(profile.auth_mode == "chatgpt" or profile.account_id or profile.last_refresh)


def _load_cockpit_codex_accounts(source_dir: Path) -> list[dict[str, Any]]:
    index_path = source_dir / "codex_accounts.json"
    accounts_dir = source_dir / "codex_accounts"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(index, dict):
        raise ValueError(f"invalid Cockpit Codex account index: {index_path}")
    raw_accounts = index.get("accounts")
    if not isinstance(raw_accounts, list):
        raw_accounts = []
    accounts = []
    for item in raw_accounts:
        if not isinstance(item, dict):
            continue
        account_id = _first_string(item.get("id"), item.get("account_id"))
        if not account_id:
            continue
        detail_path = accounts_dir / f"{account_id}.json"
        if not detail_path.exists():
            accounts.append({**item, "_source_path": str(detail_path), "_source_missing": True})
            continue
        detail = json.loads(detail_path.read_text(encoding="utf-8"))
        if not isinstance(detail, dict):
            raise ValueError(f"invalid Cockpit Codex account detail: {detail_path}")
        accounts.append({**item, **detail, "_source_path": str(detail_path)})
    return accounts


def _load_cockpit_current_account_id(source_dir: Path) -> str:
    index_path = source_dir / "codex_accounts.json"
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    if not isinstance(index, dict):
        return ""
    return _first_string(index.get("current_account_id"))


def _summarize_import_candidate(candidate: dict[str, Any], *, current_id: str = "") -> dict[str, Any]:
    auth_mode = _candidate_auth_mode(candidate)
    api_key = _candidate_api_key(candidate)
    account_id = _candidate_account_id(candidate)
    return {
        "id": account_id,
        "name": _candidate_profile_name(candidate, fallback_index=0),
        "label": _candidate_label(candidate),
        "email": _first_string(candidate.get("email"), candidate.get("account_email")),
        "auth_mode": auth_mode,
        "plan_type": _first_string(candidate.get("plan_type")),
        "api_base_url": _normalize_api_base_url(
            _first_string(candidate.get("api_base_url"), candidate.get("base_url"), candidate.get("OPENAI_BASE_URL"))
        ),
        "api_provider_id": _first_string(candidate.get("api_provider_id")),
        "api_provider_name": _first_string(candidate.get("api_provider_name")),
        "api_key_hash": _short_string_hash(api_key) if api_key else "",
        "has_api_key": bool(api_key),
        "has_tokens": isinstance(candidate.get("tokens"), dict)
        and bool(candidate["tokens"].get("id_token") or candidate["tokens"].get("access_token") or candidate["tokens"].get("refresh_token")),
        "current": bool(current_id and account_id == current_id),
        "source_path": _first_string(candidate.get("_source_path")),
        "source_missing": bool(candidate.get("_source_missing")),
    }


def _candidate_auth_mode(candidate: dict[str, Any]) -> str:
    if _candidate_api_key(candidate):
        return CODEX_API_AUTH_MODE
    raw_mode = _first_string(candidate.get("auth_mode"), candidate.get("authMode")).lower()
    if raw_mode in {"apikey", "api_key", "api-key", "api"}:
        return CODEX_API_AUTH_MODE
    return "chatgpt"


def _candidate_api_key(candidate: dict[str, Any]) -> str:
    return _first_string(
        candidate.get("OPENAI_API_KEY"),
        candidate.get("openai_api_key"),
        candidate.get("api_key"),
    )


def _candidate_account_id(candidate: dict[str, Any]) -> str:
    tokens = candidate.get("tokens") if isinstance(candidate.get("tokens"), dict) else {}
    api_key = _candidate_api_key(candidate)
    if api_key and not _first_string(candidate.get("id"), candidate.get("account_id"), tokens.get("account_id")):
        return f"codex_apikey_{hashlib.sha256(api_key.encode('utf-8')).hexdigest()[:24]}"
    return _first_string(candidate.get("id"), candidate.get("account_id"), tokens.get("account_id"))


def _candidate_label(candidate: dict[str, Any]) -> str:
    auth_mode = _candidate_auth_mode(candidate)
    if auth_mode == CODEX_API_AUTH_MODE:
        api_base_url = _normalize_api_base_url(
            _first_string(candidate.get("api_base_url"), candidate.get("base_url"), candidate.get("OPENAI_BASE_URL"))
        )
        return _first_string(
            candidate.get("api_provider_name"),
            _api_base_url_display_name(api_base_url),
            candidate.get("account_label"),
            candidate.get("account_name"),
            candidate.get("label"),
            candidate.get("email"),
            _candidate_account_id(candidate),
        )
    return _first_string(
        candidate.get("account_label"),
        candidate.get("account_name"),
        candidate.get("label"),
        candidate.get("email"),
        candidate.get("api_provider_name"),
        _candidate_account_id(candidate),
    )


def _normalized_profile_email(profile: CodexAuthProfile) -> str:
    value = _first_string(profile.email, profile.account_label)
    if "@" not in value:
        return ""
    return value.strip().lower()


def _api_base_url_display_name(api_base_url: str) -> str:
    if not api_base_url:
        return ""
    try:
        parsed = urlparse(api_base_url)
    except ValueError:
        return ""
    return parsed.hostname or ""


def _candidate_profile_name(candidate: dict[str, Any], *, fallback_index: int) -> str:
    account_id = _candidate_account_id(candidate)
    label = _candidate_label(candidate)
    if _candidate_auth_mode(candidate) == CODEX_API_AUTH_MODE:
        base = _first_string(candidate.get("api_provider_name"), label, account_id, f"api-{fallback_index + 1}")
        return _normalize_snapshot_name(f"cockpit-api-{_slugify_profile_segment(base)}")
    base = _first_string(label, account_id, f"oauth-{fallback_index + 1}")
    return _normalize_snapshot_name(f"cockpit-{_slugify_profile_segment(base)}")


def _slugify_profile_segment(value: str) -> str:
    raw = str(value or "").strip().lower()
    raw = re.sub(r"[^a-z0-9._-]+", "-", raw)
    raw = raw.strip(".-_")
    if not raw:
        return "account"
    return raw[:52].strip(".-_") or "account"


def _probe_codex_auth_payload(payload: dict[str, Any], *, label: str) -> dict[str, Any]:
    auth_mode = _auth_mode_from_payload(payload)
    if auth_mode == CODEX_API_AUTH_MODE:
        api_key = _api_key_from_auth_payload(payload)
        base_url = _normalize_api_base_url(
            _first_string(payload.get("api_base_url"), payload.get("base_url"), payload.get("OPENAI_BASE_URL"))
        )
        result = probe_codex_api_account(base_url, api_key)
        result["label"] = label
        result["auth_mode"] = auth_mode
        return result
    tokens = payload.get("tokens") if isinstance(payload.get("tokens"), dict) else {}
    access_token = _first_string(tokens.get("access_token"), payload.get("access_token"))
    account_id = _first_string(payload.get("account_id"), tokens.get("account_id"))
    result = probe_codex_oauth_account(access_token, account_id=account_id)
    result["label"] = label
    result["auth_mode"] = auth_mode
    return result


def _normalize_snapshot_name(value: str) -> str:
    normalized = str(value or "").strip()
    if normalized.lower().endswith(".json"):
        normalized = normalized[:-5]
    if not normalized:
        return ""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", normalized):
        return ""
    return normalized


def _api_key_from_auth_payload(payload: dict[str, Any]) -> str:
    return _first_string(payload.get("OPENAI_API_KEY"), payload.get("openai_api_key"), payload.get("api_key"))


def _auth_mode_from_payload(payload: dict[str, Any]) -> str:
    raw_mode = str(payload.get("auth_mode") or "").strip().lower()
    if raw_mode in {"apikey", "api_key", "api-key", "api"}:
        return CODEX_API_AUTH_MODE
    if _api_key_from_auth_payload(payload):
        return CODEX_API_AUTH_MODE
    tokens = payload.get("tokens")
    if isinstance(tokens, dict) and (tokens.get("id_token") or tokens.get("access_token") or tokens.get("refresh_token")):
        return "chatgpt"
    return raw_mode or "unknown"


def _normalize_api_base_url(value: Any) -> str:
    raw = _first_string(value)
    if not raw:
        return ""
    normalized = raw.rstrip("/")
    if normalized.endswith("/v1"):
        return normalized
    return normalized


def _find_named_snapshot_match(active_profile: CodexAuthProfile, named_profiles: list[CodexAuthProfile]) -> CodexAuthProfile | None:
    exact_hash = [profile for profile in named_profiles if profile.sha256 == active_profile.sha256]
    if exact_hash:
        return min(exact_hash, key=_display_profile_rank)

    if active_profile.account_hash:
        same_account = [profile for profile in named_profiles if profile.account_hash == active_profile.account_hash]
        if same_account:
            return max(same_account, key=lambda profile: (profile.last_refresh or "", profile.name))

    if active_profile.email:
        same_email = [profile for profile in named_profiles if profile.email and profile.email == active_profile.email]
        if same_email:
            return max(same_email, key=lambda profile: (profile.last_refresh or "", profile.name))

    return None


def _usage_cache_path(home: Path) -> Path:
    return home / "account-usage-cache.json"


def _load_usage_cache(home: Path) -> dict[str, Any]:
    path = _usage_cache_path(home)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _save_usage_cache(home: Path, payload: dict[str, Any]) -> None:
    path = _usage_cache_path(home)
    try:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    except OSError:
        return


def _update_usage_cache(cache: dict[str, Any], account: dict[str, Any], usage: dict[str, Any]) -> dict[str, Any]:
    account_hash = _first_string(account.get("account_hash"))
    if not account_hash:
        return cache
    updated = dict(cache)
    entry = {
        "account_hash": account_hash,
        "account_label": _first_string(account.get("account_label")),
        "plan_type": _first_string(usage.get("plan_type"), account.get("plan_type")),
        "source": _first_string(usage.get("source")),
        "account_binding": "active_account_after_online_refresh",
        "captured_at": _first_string(usage.get("captured_at")) or datetime.now().astimezone().isoformat(),
        "windows": usage.get("windows") if isinstance(usage.get("windows"), list) else [],
        "freshness": usage.get("freshness") if isinstance(usage.get("freshness"), dict) else None,
    }
    updated[account_hash] = entry
    return updated


def _attach_cached_usage(accounts: list[dict[str, Any]], cache: dict[str, Any]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for account in accounts:
        item = dict(account)
        account_hash = _first_string(item.get("account_hash"))
        cached = cache.get(account_hash) if account_hash else None
        if isinstance(cached, dict) and _first_string(cached.get("account_hash")) in {"", account_hash}:
            item["usage_snapshot"] = _with_usage_freshness(cached)
        else:
            item["usage_snapshot"] = None
        enriched.append(item)
    return enriched


def _account_facts_path(home: Path) -> Path:
    return home / ACCOUNT_FACTS_FILENAME


def _load_account_facts(home: Path) -> dict[str, Any]:
    path = _account_facts_path(home)
    if not path.exists():
        return {"status": "missing", "accounts": []}
    return {
        "status": "disabled_ignored",
        "accounts": [],
        "path": str(path),
        "reason": "local account facts are disabled because operator-asserted plan overrides are not objective enough for account display",
    }


def _resolve_account_plan_types(accounts: list[dict[str, Any]], account_facts: dict[str, Any]) -> list[dict[str, Any]]:
    facts = account_facts.get("accounts") if isinstance(account_facts, dict) else []
    if not isinstance(facts, list):
        facts = []
    resolved: list[dict[str, Any]] = []
    for account in accounts:
        item = dict(account)
        auth_plan = _canonical_plan_type(item.get("plan_type"))
        if auth_plan:
            item["auth_plan_type"] = auth_plan
        usage_snapshot = item.get("usage_snapshot")
        usage_plan = _canonical_plan_type(usage_snapshot.get("plan_type")) if isinstance(usage_snapshot, dict) else ""
        fact = _match_account_fact(item, facts)
        fact_plan = _canonical_plan_type(fact.get("plan_type")) if fact else ""

        candidates: list[tuple[str, str]] = []
        if fact_plan:
            candidates.append(("account_facts", fact_plan))
        if usage_plan and _usage_is_safe_for_plan_resolution(usage_snapshot):
            candidates.append(("usage_snapshot", usage_plan))
        if auth_plan:
            candidates.append(("auth_token", auth_plan))

        if candidates:
            source, plan_type = candidates[0]
            item["plan_type"] = plan_type
            item["plan_source"] = _first_string(fact.get("source")) if source == "account_facts" and fact else source
            conflicts = [
                {"source": candidate_source, "plan_type": candidate_plan}
                for candidate_source, candidate_plan in candidates
                if candidate_plan != plan_type
            ]
            if usage_plan and not _usage_is_safe_for_plan_resolution(usage_snapshot) and usage_plan != plan_type:
                conflicts.append({"source": "stale_or_unbound_usage_snapshot", "plan_type": usage_plan})
            if conflicts:
                item["plan_conflicts"] = conflicts
        else:
            item["plan_source"] = "unavailable"
        resolved.append(item)
    return resolved


def _match_account_fact(account: dict[str, Any], facts: list[dict[str, Any]]) -> dict[str, Any] | None:
    account_id = _first_string(account.get("account_id"))
    account_hash = _first_string(account.get("account_hash"))
    email = _first_string(account.get("email")).lower()
    name = _first_string(account.get("name"))
    file_name = _first_string(account.get("file"))
    for fact in facts:
        if account_id and _first_string(fact.get("account_id")) == account_id:
            return fact
        if account_hash and _first_string(fact.get("account_hash")) == account_hash:
            return fact
        if email and _first_string(fact.get("email")).lower() == email:
            return fact
        if name and _first_string(fact.get("name")) == name:
            return fact
        if file_name and _first_string(fact.get("file")) == file_name:
            return fact
    return None


def _canonical_plan_type(value: Any) -> str:
    raw = _first_string(value).lower()
    aliases = {
        "chatgpt plus": "plus",
        "plus": "plus",
        "chatgpt go": "prolite",
        "go": "prolite",
        "prolite": "prolite",
        "team": "team",
        "pro": "pro",
        "free": "free",
    }
    return aliases.get(raw, raw)


def _resolve_active_plan_type(active_account: dict[str, Any] | None, usage: dict[str, Any]) -> str:
    if not isinstance(active_account, dict):
        return ""
    configured_plan = _first_string(active_account.get("plan_type"))
    if configured_plan:
        return configured_plan
    snapshot = active_account.get("usage_snapshot")
    if isinstance(snapshot, dict):
        cached_plan = _first_string(snapshot.get("plan_type"))
        if cached_plan:
            freshness = snapshot.get("freshness")
            if isinstance(freshness, dict):
                try:
                    if not bool(freshness.get("is_stale")):
                        return cached_plan
                except (TypeError, ValueError):
                    pass
            else:
                return cached_plan
    usage_plan = _first_string(usage.get("plan_type")) if isinstance(usage, dict) else ""
    if usage_plan and _first_string(usage.get("source")) != "unknown":
        return usage_plan
    return _first_string(active_account.get("plan_type"))


def _usage_is_safe_for_account_display(usage: dict[str, Any]) -> bool:
    if not isinstance(usage, dict):
        return False
    if _first_string(usage.get("source")) in {"", "unknown", "codex_logs_2_sqlite"}:
        return False
    return _first_string(usage.get("account_binding")) in {"active_account_after_online_refresh", "online_refresh_current_auth"}


def _usage_is_safe_for_plan_resolution(usage: Any) -> bool:
    if not isinstance(usage, dict):
        return False
    if _usage_is_stale(usage):
        return False
    return _first_string(usage.get("account_binding")) in {"active_account_after_online_refresh", "online_refresh_current_auth"}


def _account_usage_needs_refresh(active_account: dict[str, Any] | None) -> bool:
    if not isinstance(active_account, dict):
        return False
    snapshot = active_account.get("usage_snapshot")
    if not isinstance(snapshot, dict):
        return True
    return not _usage_is_safe_for_plan_resolution(snapshot)


def _discover_official_codex_app_account(
    accounts: list[dict[str, Any]],
    *,
    app_storage_root: Path | None = None,
) -> dict[str, Any]:
    root = app_storage_root or _official_codex_app_storage_root()
    if root is None:
        return {"status": "platform_na", "reason": "official_codex_app_storage_missing"}

    candidate_files: list[Path] = []
    for relative in (
        Path("Local Storage") / "leveldb",
        Path("Session Storage"),
        Path("Partitions"),
        Path("Preferences"),
        Path("Local State"),
    ):
        candidate = root / relative
        if candidate.is_file():
            candidate_files.append(candidate)
        elif candidate.is_dir():
            candidate_files.extend(path for path in candidate.rglob("*") if path.is_file())

    known_accounts = [
        account
        for account in accounts
        if _first_string(account.get("account_id"))
    ]
    if not known_accounts:
        return {
            "status": "unavailable",
            "reason": "no_known_codex_account_ids",
            "storage_root": str(root),
        }

    newest_hit: dict[str, Any] | None = None
    for path in candidate_files:
        try:
            payload = path.read_bytes()
        except OSError:
            continue
        matched = [
            account
            for account in known_accounts
            if _first_string(account.get("account_id")).encode("utf-8") in payload
        ]
        if not matched:
            continue
        stat = path.stat()
        hit = {
            "path": str(path),
            "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "matched_accounts": [
                {
                    "name": _first_string(account.get("name")),
                    "file": _first_string(account.get("file")),
                    "email": _first_string(account.get("email")),
                    "account_id": _first_string(account.get("account_id")),
                }
                for account in matched
            ],
        }
        if newest_hit is None or hit["last_modified"] > newest_hit["last_modified"]:
            newest_hit = hit

    if newest_hit is None:
        return {
            "status": "unavailable",
            "reason": "official_codex_app_account_not_found",
            "storage_root": str(root),
        }

    matched_accounts = newest_hit["matched_accounts"]
    if len(matched_accounts) != 1:
        return {
            "status": "ambiguous",
            "reason": "multiple_accounts_matched_latest_storage_record",
            "limitation": "official_app_storage_currently_exposes_multiple_known_account_ids_without_a_safe_full_auth_payload_import",
            "storage_root": str(root),
            "storage_probe": newest_hit,
        }

    selected = matched_accounts[0]
    return {
        "status": "ok",
        "storage_root": str(root),
        "account_id": selected["account_id"],
        "name": selected["name"],
        "file": selected["file"],
        "email": selected["email"],
        "source": "official_codex_app_storage_scan",
        "storage_probe": newest_hit,
    }


def _official_codex_app_storage_root() -> Path | None:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return None
    root = Path(local_app_data) / "Packages" / "OpenAI.Codex_2p2nqsd0c76g0" / "LocalCache" / "Roaming" / "Codex"
    return root if root.exists() else None


def _should_update_usage_cache_from_usage(*, usage: dict[str, Any], usage_refresh: dict[str, Any]) -> bool:
    if not isinstance(usage, dict) or not isinstance(usage_refresh, dict):
        return False
    source = _first_string(usage.get("source"))
    # `codex_logs_2_sqlite` can contain another account's latest event.
    # Only promote account cache when online refresh actually succeeded.
    if source not in {"codex_exec_stdout", "codex_sessions_jsonl"}:
        return False
    return bool(usage_refresh.get("attempted")) and _first_string(usage_refresh.get("status")) == "ok"


def _read_auth_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid auth JSON: {path}")
    return payload


def _short_file_hash(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest[:12]


def _short_string_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _auth_claims(payload: dict[str, Any], tokens: dict[str, Any]) -> dict[str, str]:
    id_claims = _decode_jwt_payload(tokens.get("id_token"))
    access_claims = _decode_jwt_payload(tokens.get("access_token"))
    nested_auth = id_claims.get("https://api.openai.com/auth")
    if not isinstance(nested_auth, dict):
        nested_auth = {}
    return {
        "email": _first_string(
            payload.get("email"),
            payload.get("account_email"),
            tokens.get("email"),
            id_claims.get("email"),
        ),
        "display_name": _first_string(
            payload.get("name"),
            payload.get("display_name"),
            id_claims.get("name"),
            id_claims.get("preferred_username"),
        ),
        "plan_type": _first_string(
            payload.get("plan_type"),
            nested_auth.get("chatgpt_plan_type"),
            nested_auth.get("plan_type"),
        ),
        "subscription_active_start": _claim_time_iso(nested_auth.get("chatgpt_subscription_active_start")),
        "subscription_active_until": _first_string(
            _claim_time_iso(payload.get("subscription_active_until")),
            _claim_time_iso(nested_auth.get("chatgpt_subscription_active_until")),
        ),
        "subscription_last_checked": _claim_time_iso(nested_auth.get("chatgpt_subscription_last_checked")),
        "id_token_expires_at": _jwt_expiry_iso(id_claims.get("exp")),
        "access_token_expires_at": _jwt_expiry_iso(access_claims.get("exp")),
    }


def _decode_jwt_payload(token: Any) -> dict[str, Any]:
    if not isinstance(token, str) or token.count(".") < 2:
        return {}
    payload_part = token.split(".")[1]
    payload_part += "=" * (-len(payload_part) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload_part.encode("ascii"))
        payload = json.loads(decoded.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _first_string(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _jwt_expiry_iso(raw_exp: Any) -> str:
    try:
        exp = int(raw_exp)
    except (TypeError, ValueError):
        return ""
    if exp <= 0:
        return ""
    try:
        return datetime.fromtimestamp(exp, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except (OverflowError, OSError, ValueError):
        return ""


def _claim_time_iso(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, (int, float)):
        return _timestamp_iso(value)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return ""
        try:
            return _timestamp_iso(float(raw))
        except ValueError:
            pass
        normalized = raw.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return raw
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return ""


def _timestamp_iso(value: int | float) -> str:
    timestamp = float(value)
    if timestamp > 10_000_000_000:
        timestamp = timestamp / 1000
    if timestamp <= 0:
        return ""
    try:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except (OverflowError, OSError, ValueError):
        return ""


def _codex_usage_status(home: Path) -> dict[str, Any]:
    event = _latest_rate_limit_event(home)
    if not event:
        return _unknown_usage_status("No codex.rate_limits event was found in local Codex logs.")

    rate_limits = event.get("rate_limits")
    if not isinstance(rate_limits, dict):
        return _unknown_usage_status("Latest codex.rate_limits event did not contain rate_limits.")
    return _usage_status_from_rate_limits(
        source="codex_logs_2_sqlite",
        rate_limits=rate_limits,
        plan_type=_first_string(event.get("plan_type")),
        allowed=event.get("allowed", rate_limits.get("allowed")),
        limit_reached=event.get("limit_reached", rate_limits.get("limit_reached")),
        note="Best-effort local reading from recent Codex rate limit events.",
        captured_at=_claim_time_iso(event.get("captured_at")) or _timestamp_iso(event.get("captured_at")),
        account_binding="global_unbound_log_event",
    )


def _refresh_codex_usage_online(home: Path, *, fallback_usage: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    refresh = {
        "attempted": True,
        "status": "fallback",
        "mode": "online_exec",
        "consumes_quota": True,
    }
    codex_cmd = shutil.which("codex.cmd") or shutil.which("codex")
    if not codex_cmd:
        refresh["error"] = "codex command not found"
        return fallback_usage, refresh

    started_at = time.time()
    try:
        completed = subprocess.run(
            [codex_cmd, "exec", "--json", "Reply only ok."],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
            cwd=str(Path.cwd()),
            **_windows_no_window_kwargs(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        refresh["error"] = str(exc)
        return fallback_usage, refresh

    session_usage = _usage_status_from_exec_output(completed.stdout)
    if session_usage is None:
        session_usage = _latest_session_usage(home, min_mtime=started_at - 1)

    if session_usage is not None:
        refresh["status"] = "ok"
        refresh["source"] = session_usage.get("source")
        refresh["exit_code"] = completed.returncode
        return session_usage, refresh

    refresh["exit_code"] = completed.returncode
    refresh["error"] = _first_string(
        _first_non_empty_line(completed.stderr),
        _first_non_empty_line(completed.stdout),
        "online refresh did not produce a fresh rate limit snapshot",
    )
    return fallback_usage, refresh


def _unknown_usage_status(note: str) -> dict[str, Any]:
    return _with_usage_freshness({
        "source": "unknown",
        "dashboard_url": USAGE_DASHBOARD_URL,
        "windows": [
            {"window": "5h", "remaining": None, "remaining_percent": None, "reset_at": None},
            {"window": "7d", "remaining": None, "remaining_percent": None, "reset_at": None},
        ],
        "note": note,
        "captured_at": "",
    })


def _usage_status_from_exec_output(text: str) -> dict[str, Any] | None:
    for raw_line in reversed(text.splitlines()):
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        rate_limits = payload.get("rate_limits")
        if not isinstance(rate_limits, dict):
            continue
        usage = _usage_status_from_rate_limits(
            source="codex_exec_stdout",
            rate_limits=rate_limits,
            plan_type=_first_string(rate_limits.get("plan_type"), payload.get("plan_type")),
            limit_reached=bool(rate_limits.get("rate_limit_reached_type")) if rate_limits.get("rate_limit_reached_type") else False,
            note="Fresh online reading from a minimal Codex exec request.",
            captured_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            account_binding="online_refresh_current_auth",
        )
        if usage.get("source") != "unknown":
            return usage
    return None


def _latest_session_usage(home: Path, *, min_mtime: float | None = None) -> dict[str, Any] | None:
    sessions_root = home / "sessions"
    if not sessions_root.exists():
        return None
    try:
        files = sorted(
            sessions_root.rglob("rollout-*.jsonl"),
            key=lambda candidate: candidate.stat().st_mtime,
            reverse=True,
        )
    except OSError:
        return None
    for path in files[:80]:
        try:
            stat = path.stat()
        except OSError:
            continue
        if min_mtime is not None and stat.st_mtime < min_mtime:
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for raw_line in reversed(lines[-400:]):
            try:
                entry = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if not isinstance(entry, dict) or entry.get("type") != "event_msg":
                continue
            payload = entry.get("payload")
            if not isinstance(payload, dict) or payload.get("type") != "token_count":
                continue
            rate_limits = payload.get("rate_limits")
            if not isinstance(rate_limits, dict):
                continue
            usage = _usage_status_from_rate_limits(
                source="codex_sessions_jsonl",
                rate_limits=rate_limits,
                plan_type=_first_string(rate_limits.get("plan_type")),
                limit_reached=bool(rate_limits.get("rate_limit_reached_type")) if rate_limits.get("rate_limit_reached_type") else False,
                note="Fresh online reading from the latest Codex session snapshot.",
                captured_at=_first_string(entry.get("timestamp")),
                account_binding="online_refresh_current_auth",
            )
            if usage.get("source") == "unknown":
                continue
            usage["evidence_path"] = str(path)
            return usage
    return None


def _usage_status_from_rate_limits(
    *,
    source: str,
    rate_limits: dict[str, Any],
    plan_type: str = "",
    allowed: Any = None,
    limit_reached: Any = None,
    note: str,
    captured_at: str = "",
    account_binding: str = "",
) -> dict[str, Any]:
    windows = []
    for key in ("primary", "secondary"):
        raw_window = rate_limits.get(key)
        if not isinstance(raw_window, dict):
            continue
        window_minutes = _optional_int(raw_window.get("window_minutes"))
        used_percent = _optional_number(raw_window.get("used_percent"))
        remaining_percent = None
        if used_percent is not None:
            remaining_percent = _remaining_percent_from_used(used_percent)
        windows.append(
            {
                "kind": key,
                "window": _window_label(window_minutes),
                "window_minutes": window_minutes,
                "used_percent": used_percent,
                "remaining_percent": remaining_percent,
                "remaining": f"{remaining_percent}%" if remaining_percent is not None else None,
                "reset_after_seconds": _optional_int(raw_window.get("reset_after_seconds")),
                "reset_at": _optional_int(raw_window.get("reset_at") or raw_window.get("resets_at")),
            }
        )
    if not windows:
        return _unknown_usage_status("Latest rate limit payload did not contain usage windows.")
    payload = {
        "source": source,
        "dashboard_url": USAGE_DASHBOARD_URL,
        "plan_type": _first_string(plan_type),
        "allowed": allowed,
        "limit_reached": limit_reached,
        "windows": windows,
        "note": note,
        "captured_at": _first_string(captured_at),
        "account_binding": _first_string(account_binding),
    }
    return _with_usage_freshness(payload)


def _latest_rate_limit_event(home: Path) -> dict[str, Any] | None:
    log_db = home / "logs_2.sqlite"
    if not log_db.exists():
        return None
    try:
        connection = sqlite3.connect(f"file:{log_db}?mode=ro", uri=True)
    except sqlite3.Error:
        return None
    try:
        rows = connection.execute(
            """
            SELECT ts, feedback_log_body
            FROM logs
            WHERE feedback_log_body LIKE '%"type":"codex.rate_limits"%'
            ORDER BY id DESC
            LIMIT 100
            """
        ).fetchall()
    except sqlite3.Error:
        return None
    finally:
        connection.close()
    for ts, body in rows:
        for event in _extract_rate_limit_events(str(body or "")):
            event.setdefault("captured_at", ts)
            return event
    return None


def _extract_rate_limit_events(text: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    marker = '{"type":"codex.rate_limits"'
    start = 0
    while True:
        index = text.find(marker, start)
        if index < 0:
            break
        raw_json = _balanced_json_object(text, index)
        if raw_json:
            try:
                payload = json.loads(raw_json)
            except json.JSONDecodeError:
                payload = None
            if isinstance(payload, dict):
                events.append(payload)
        start = index + len(marker)
    return events


def _balanced_json_object(text: str, start: int) -> str:
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def _window_label(window_minutes: int | None) -> str:
    if window_minutes is None:
        return "unknown"
    if window_minutes % 1440 == 0:
        days = window_minutes // 1440
        return f"{days}d"
    if window_minutes % 60 == 0:
        hours = window_minutes // 60
        return f"{hours}h"
    return f"{window_minutes}m"


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_number(value: Any) -> int | float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else number


def _remaining_percent_from_used(used_percent: int | float) -> int | float:
    remaining_percent = 100 if 0 <= used_percent <= 1 else max(0, min(100, 100 - used_percent))
    return int(remaining_percent) if float(remaining_percent).is_integer() else remaining_percent


def _first_non_empty_line(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line:
            return line
    return ""


def _last_non_empty_lines(text: str, *, limit: int) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-limit:]


def _with_usage_freshness(payload: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(payload)
    captured_at = _first_string(enriched.get("captured_at"))
    captured_epoch = _iso_to_epoch_seconds(captured_at)
    age_seconds = None if captured_epoch is None else max(0, int(time.time() - captured_epoch))
    enriched["freshness"] = {
        "captured_at": captured_at or None,
        "age_seconds": age_seconds,
        "stale_after_seconds": USAGE_STALE_AFTER_SECONDS,
        "is_stale": True if age_seconds is None else age_seconds > USAGE_STALE_AFTER_SECONDS,
    }
    return enriched


def _usage_is_stale(usage: dict[str, Any]) -> bool:
    freshness = usage.get("freshness")
    if not isinstance(freshness, dict):
        return True
    return bool(freshness.get("is_stale", True))


def _iso_to_epoch_seconds(value: str) -> float | None:
    raw = _first_string(value)
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def _find_top_level_value(text: str, key: str) -> Any:
    current_section = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line
            continue
        if current_section:
            continue
        prefix = f"{key} ="
        if line.startswith(prefix):
            value = line[len(prefix) :].strip()
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            if value in {"true", "false"}:
                return value == "true"
            try:
                return int(value)
            except ValueError:
                return value
    return None


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _context_settings_decision(
    *,
    model: str,
    configured_context: int | None,
    configured_compact: int | None,
    catalog_probes: list[dict[str, Any]],
) -> dict[str, Any]:
    catalog_entries = []
    for probe in catalog_probes:
        model_info = probe.get("model")
        if probe.get("status") != "pass" or not isinstance(model_info, dict):
            continue
        catalog_entries.append(
            {
                "source": f"codex_debug_models_{probe.get('catalog_mode')}",
                "catalog_mode": probe.get("catalog_mode"),
                "context_window": _coerce_int(model_info.get("context_window")),
                "max_context_window": _coerce_int(model_info.get("max_context_window")),
                "effective_context_window_percent": _coerce_int(model_info.get("effective_context_window_percent")),
            }
        )

    catalog_contexts = [
        entry["context_window"]
        for entry in catalog_entries
        if isinstance(entry.get("context_window"), int) and entry["context_window"] > 0
    ]
    distinct_contexts = sorted(set(catalog_contexts))
    if distinct_contexts and len(distinct_contexts) == 1:
        selected_context = distinct_contexts[0]
        context_source = "catalog_agreement" if len(catalog_entries) > 1 else catalog_entries[0]["source"]
        basis_status = "catalog_consensus" if len(catalog_entries) > 1 else "single_catalog"
    else:
        selected_context = configured_context or _coerce_int(DEFAULT_CONFIG.get("model_context_window"))
        context_source = "configured_fallback" if configured_context else "default_fallback"
        basis_status = "catalog_disagreement" if distinct_contexts else "config_only"

    selected_compact = None
    compact_source = "unavailable"
    compact_ratio = None
    if selected_context:
        if configured_compact and configured_compact < selected_context:
            compact_ratio = round(configured_compact / selected_context, 4)
            if CONTEXT_COMPACT_RATIO_MIN <= compact_ratio <= CONTEXT_COMPACT_RATIO_MAX:
                selected_compact = configured_compact
                compact_source = "configured_guard_band"
        if selected_compact is None:
            selected_compact = _recommended_compact_limit(selected_context)
            compact_ratio = round(selected_compact / selected_context, 4) if selected_compact else None
            compact_source = "derived_ratio"

    action = "keep_current"
    if selected_context != configured_context or selected_compact != configured_compact:
        action = "update_config"
    if basis_status == "catalog_disagreement":
        action = "manual_review"

    return {
        "model": model,
        "status": "attention" if basis_status == "catalog_disagreement" else "pass",
        "action": action,
        "basis_status": basis_status,
        "model_context_window": selected_context,
        "model_auto_compact_token_limit": selected_compact,
        "compact_ratio": compact_ratio,
        "context_source": context_source,
        "compact_source": compact_source,
        "catalog_entries": catalog_entries,
        "decision_rule": "Prefer matching bundled/refreshed `codex debug models` context_window values; keep configured auto-compact when it is below the context window and inside the guard band; otherwise derive an 81% rounded threshold.",
    }


def _recommended_compact_limit(context_window: int) -> int:
    raw = int(context_window * DEFAULT_CONTEXT_COMPACT_RATIO)
    if CONTEXT_COMPACT_GRANULARITY <= 1:
        return raw
    rounded = (raw // CONTEXT_COMPACT_GRANULARITY) * CONTEXT_COMPACT_GRANULARITY
    return max(CONTEXT_COMPACT_GRANULARITY, rounded)


def _catalogs_agree_check(catalog_probes: list[dict[str, Any]]) -> dict[str, Any]:
    contexts_by_mode: dict[str, int | None] = {}
    for probe in catalog_probes:
        mode = _first_string(probe.get("catalog_mode")) or "unknown"
        model_info = probe.get("model")
        contexts_by_mode[mode] = _coerce_int(model_info.get("context_window")) if isinstance(model_info, dict) else None
    values = [value for value in contexts_by_mode.values() if value is not None]
    return {
        "check_id": "bundled_and_refreshed_catalogs_agree",
        "status": "pass" if values and len(values) == len(contexts_by_mode) and len(set(values)) == 1 else "fail",
        "reason": "Bundled and refreshed `codex debug models` catalogs should agree before using them to change context settings.",
        "contexts_by_mode": contexts_by_mode,
    }


def _probe_codex_model_catalog(
    *,
    model: str,
    bundled: bool,
    codex_binary: str | None,
    timeout_seconds: int,
) -> dict[str, Any]:
    codex_cmd = codex_binary or shutil.which("codex.cmd") or shutil.which("codex")
    if not codex_cmd:
        return {
            "status": "platform_na",
            "reason": "codex command not found",
            "command": None,
        }
    command = [codex_cmd, "debug", "models"]
    if bundled:
        command.append("--bundled")
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            **_windows_no_window_kwargs(),
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "platform_na",
            "reason": f"codex debug models timed out after {timeout_seconds}s",
            "command": command,
            "error": str(exc),
        }
    except OSError as exc:
        return {
            "status": "platform_na",
            "reason": str(exc),
            "command": command,
        }

    output = _strip_ansi(completed.stdout or "")
    model_entry, parse_status = _extract_model_catalog_entry(output, model)
    status = "pass" if completed.returncode == 0 and model_entry else "platform_na"
    return {
        "status": status,
        "command": command,
        "exit_code": completed.returncode,
        "catalog_mode": "bundled" if bundled else "refreshed",
        "model": model_entry,
        "parse_status": parse_status,
        "stderr_summary": (completed.stderr or "").strip()[:500],
    }


def _probe_codex_context_settings_exec(
    *,
    model: str,
    configured_context: int | None,
    configured_compact: int | None,
    codex_binary: str | None,
    timeout_seconds: int,
) -> dict[str, Any]:
    if configured_context is None or configured_compact is None:
        return {
            "status": "platform_na",
            "reason": "configured context window and auto-compact token limit are required before running an exec probe",
            "command": None,
            "consumes_quota": True,
        }
    codex_cmd = codex_binary or shutil.which("codex.cmd") or shutil.which("codex")
    if not codex_cmd:
        return {
            "status": "platform_na",
            "reason": "codex command not found",
            "command": None,
            "consumes_quota": True,
        }
    command = [
        codex_cmd,
        "exec",
        "--json",
        "--model",
        model,
        "-c",
        f"model_context_window={configured_context}",
        "-c",
        f"model_auto_compact_token_limit={configured_compact}",
        "Reply only ok.",
    ]
    try:
        completed = subprocess.run(
            command,
            input="",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            **_windows_no_window_kwargs(),
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "platform_na",
            "reason": f"codex exec context probe timed out after {timeout_seconds}s",
            "command": command,
            "error": str(exc),
            "consumes_quota": True,
        }
    except OSError as exc:
        return {
            "status": "platform_na",
            "reason": str(exc),
            "command": command,
            "consumes_quota": True,
        }

    stdout_summary = _last_non_empty_lines(completed.stdout or "", limit=4)
    stderr_summary = _last_non_empty_lines(completed.stderr or "", limit=4)
    return {
        "status": "pass" if completed.returncode == 0 else "platform_na",
        "command": command,
        "exit_code": completed.returncode,
        "stdout_summary": stdout_summary,
        "stderr_summary": stderr_summary,
        "consumes_quota": True,
    }


def _extract_model_catalog_entry(text: str, model: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        payload = None
        json_error = f"{exc.msg} at {exc.lineno}:{exc.colno}"
    else:
        json_error = None

    if isinstance(payload, dict) and isinstance(payload.get("models"), list):
        for item in payload["models"]:
            if isinstance(item, dict) and item.get("slug") == model:
                return _model_catalog_summary(item), {"method": "json", "json_error": None}

    fallback = _extract_model_catalog_entry_by_regex(text, model)
    return fallback, {"method": "regex" if fallback else "none", "json_error": json_error}


def _extract_model_catalog_entry_by_regex(text: str, model: str) -> dict[str, Any] | None:
    match = re.search(r'"slug"\s*:\s*"' + re.escape(model) + r'"', text)
    if not match:
        return None
    tail = text[match.start() :]
    entry = {"slug": model}
    for field in ("display_name", "context_window", "max_context_window", "effective_context_window_percent"):
        if field in {"display_name"}:
            field_match = re.search(rf'"{field}"\s*:\s*"([^"]*)"', tail)
            if field_match:
                entry[field] = field_match.group(1)
        else:
            field_match = re.search(rf'"{field}"\s*:\s*([0-9]+)', tail)
            if field_match:
                entry[field] = int(field_match.group(1))
    return entry


def _model_catalog_summary(item: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "slug",
        "display_name",
        "default_reasoning_level",
        "context_window",
        "max_context_window",
        "effective_context_window_percent",
        "supports_search_tool",
        "support_verbosity",
        "default_verbosity",
    )
    return {key: item.get(key) for key in keys if key in item}


def _strip_ansi(value: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", value)


def _run_codex_login_status() -> dict[str, Any]:
    codex_cmd = shutil.which("codex.cmd") or shutil.which("codex")
    if not codex_cmd:
        return {"exit_code": 127, "summary": "codex command not found"}
    try:
        completed = subprocess.run(
            [codex_cmd, "login", "status"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            **_windows_no_window_kwargs(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": 127, "summary": str(exc)}
    return {
        "exit_code": completed.returncode,
        "summary": "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part),
    }
