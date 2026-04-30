from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = {
    "cli_auth_credentials_store": "file",
    "model": "gpt-5.4",
    "model_reasoning_effort": "medium",
    "model_verbosity": "medium",
    "model_context_window": 272000,
    "model_auto_compact_token_limit": 220000,
    "sandbox_mode": "workspace-write",
    "approval_policy": "never",
    "web_search": "cached",
}
DEFAULT_CONFIG_PROFILE = {
    "strategy": "efficiency_first",
    "strategy_label": "综合效率优先",
    "strategy_principles": [
        "少打扰",
        "自动连续执行",
        "节省 token / 成本",
        "高效率",
    ],
    "current_combo": "gpt-5.4 + medium + never",
    "current_combo_status": "current_temporary_choice",
    "compact_policy": "220000 on a 272000 window",
    "compact_ratio": "81%",
    "manual_upgrade": "Switch to a stronger model or reasoning level manually when a task genuinely needs deeper reasoning.",
    "change_rule": "Future model or parameter updates should preserve the efficiency-first principle rather than the current combo itself.",
}
USAGE_DASHBOARD_URL = "https://chatgpt.com/codex/settings/usage"


@dataclass(frozen=True)
class CodexAuthProfile:
    name: str
    file: str
    active: bool
    auth_mode: str
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
    account_hash: str
    sha256: str
    full_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "file": self.file,
            "active": self.active,
            "auth_mode": self.auth_mode,
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


def switch_auth_profile(name: str, home: Path | None = None, *, dry_run: bool = False) -> dict[str, Any]:
    normalized_name = str(name or "").strip()
    if not normalized_name:
        return {"status": "error", "error": "missing auth profile name"}
    home = codex_home(str(home) if home else None)
    profiles = list_auth_profiles(home)
    matches = [
        profile
        for profile in profiles
        if profile.name == normalized_name or profile.file == normalized_name or profile.full_name == normalized_name
    ]
    if not matches:
        return {"status": "error", "error": f"unknown auth profile: {normalized_name}"}
    if len(matches) > 1:
        return {"status": "error", "error": f"ambiguous auth profile: {normalized_name}"}
    target = matches[0]
    active_path = home / "auth.json"
    if target.active:
        return {"status": "ok", "changed": False, "active_profile": target.to_dict()}
    if dry_run:
        return {"status": "ok", "changed": False, "dry_run": True, "target_profile": target.to_dict()}

    backup_path = backup_active_auth(home)
    shutil.copyfile(target.full_name, active_path)
    new_active = _auth_profile_from_path(active_path, _short_file_hash(active_path))
    return {
        "status": "ok",
        "changed": True,
        "backup_path": str(backup_path),
        "active_profile": new_active.to_dict(),
        "target_profile": target.to_dict(),
    }


def backup_active_auth(home: Path | None = None) -> Path:
    home = codex_home(str(home) if home else None)
    active_path = home / "auth.json"
    if not active_path.exists():
        raise FileNotFoundError(f"missing active auth: {active_path}")
    backup_dir = home / "auth-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = backup_dir / f"auth-{timestamp}.json"
    shutil.copyfile(active_path, backup_path)
    return backup_path


def codex_status(home: Path | None = None, *, refresh_online: bool = False) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    accounts = _display_auth_profiles(list_auth_profiles(home))
    usage_refresh = {
        "attempted": False,
        "status": "idle",
        "mode": "local_snapshot",
        "consumes_quota": False,
    }
    usage = _codex_usage_status(home)
    if refresh_online:
        usage, usage_refresh = _refresh_codex_usage_online(home, fallback_usage=usage)
    usage_cache = _load_usage_cache(home)
    active_account = next((account for account in accounts if account.get("active")), None)
    if active_account and usage.get("source") != "unknown":
        usage_cache = _update_usage_cache(usage_cache, active_account, usage)
        _save_usage_cache(home, usage_cache)
    accounts = _attach_cached_usage(accounts, usage_cache)
    payload: dict[str, Any] = {
        "codex_home": str(home),
        "auth": active_auth_status(home),
        "accounts": accounts,
        "config": config_health(home),
        "recommended_defaults": DEFAULT_CONFIG_PROFILE,
        "usage": usage,
        "usage_refresh": usage_refresh,
    }
    payload["active_account"] = next((account for account in accounts if account.get("active")), None)
    payload["login_status"] = _run_codex_login_status()
    return payload


def config_health(home: Path | None = None) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    config_path = home / "config.toml"
    if not config_path.exists():
        return {"status": "missing", "path": str(config_path), "checks": []}
    text = config_path.read_text(encoding="utf-8", errors="replace")
    checks = []
    for key, expected in DEFAULT_CONFIG.items():
        actual = _find_top_level_value(text, key)
        checks.append(
            {
                "key": key,
                "expected": expected,
                "actual": actual,
                "ok": str(actual) == str(expected),
            }
        )
    secret_hits = []
    for marker in ("ANTHROPIC_AUTH_TOKEN", "ctx7" + "sk", "sk-"):
        if marker in text:
            secret_hits.append(marker)
    return {
        "status": "ok" if all(check["ok"] for check in checks) and not secret_hits else "attention",
        "path": str(config_path),
        "checks": checks,
        "secret_like_markers": secret_hits,
    }


def install_account_switcher(home: Path | None = None, bin_dir: Path | None = None) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    bin_dir = (bin_dir or (Path.home() / ".local" / "bin")).expanduser()
    scripts_dir = home / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / "scripts" / "codex-account.ps1"
    target = scripts_dir / "Switch-CodexAccount.ps1"
    shim = bin_dir / "codex-account.cmd"
    shutil.copyfile(source, target)
    shim.write_text(
        '@echo off\npwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\\.codex\\scripts\\Switch-CodexAccount.ps1" %*\n',
        encoding="utf-8",
    )
    return {"status": "ok", "script": str(target), "shim": str(shim)}


def _auth_profile_from_path(path: Path, active_hash: str) -> CodexAuthProfile:
    payload = _read_auth_json(path)
    tokens = payload.get("tokens") if isinstance(payload.get("tokens"), dict) else {}
    account_id = str(tokens.get("account_id") or "")
    file_hash = _short_file_hash(path)
    claims = _auth_claims(payload, tokens)
    account_hash = _short_string_hash(account_id) if account_id else ""
    account_label = claims["email"] or claims["display_name"] or account_hash or path.stem
    return CodexAuthProfile(
        name=path.stem,
        file=path.name,
        active=file_hash == active_hash,
        auth_mode=str(payload.get("auth_mode") or ""),
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
        account_hash=account_hash,
        sha256=file_hash,
        full_name=str(path),
    )


def _display_auth_profiles(profiles: list[CodexAuthProfile]) -> list[dict[str, Any]]:
    grouped: dict[str, list[CodexAuthProfile]] = {}
    for profile in profiles:
        group_key = profile.sha256 or profile.full_name
        grouped.setdefault(group_key, []).append(profile)

    rendered: list[dict[str, Any]] = []
    for duplicates in grouped.values():
        preferred = min(duplicates, key=_display_profile_rank)
        rendered_profile = preferred.to_dict()
        rendered_profile["active"] = any(profile.active for profile in duplicates)
        rendered.append(rendered_profile)

    return sorted(rendered, key=lambda item: (0 if item.get("active") else 1, item.get("name") or item.get("file") or ""))


def _display_profile_rank(profile: CodexAuthProfile) -> tuple[int, int, str]:
    # Prefer named saved profiles over the auth.json live mirror when both point to the same account snapshot.
    return (
        1 if profile.name == "auth" else 0,
        0 if profile.active else 1,
        profile.name,
    )


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
        "captured_at": _first_string(usage.get("captured_at")) or datetime.now().astimezone().isoformat(),
        "windows": usage.get("windows") if isinstance(usage.get("windows"), list) else [],
    }
    updated[account_hash] = entry
    return updated


def _attach_cached_usage(accounts: list[dict[str, Any]], cache: dict[str, Any]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for account in accounts:
        item = dict(account)
        account_hash = _first_string(item.get("account_hash"))
        cached = cache.get(account_hash) if account_hash else None
        item["usage_snapshot"] = cached if isinstance(cached, dict) else None
        enriched.append(item)
    return enriched


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
        "subscription_active_until": _claim_time_iso(nested_auth.get("chatgpt_subscription_active_until")),
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
    return {
        "source": "unknown",
        "dashboard_url": USAGE_DASHBOARD_URL,
        "windows": [
            {"window": "5h", "remaining": None, "remaining_percent": None, "reset_at": None},
            {"window": "7d", "remaining": None, "remaining_percent": None, "reset_at": None},
        ],
        "note": note,
    }


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
            )
            if usage.get("source") == "unknown":
                continue
            usage["evidence_path"] = str(path)
            timestamp = entry.get("timestamp")
            if isinstance(timestamp, str) and timestamp.strip():
                usage["captured_at"] = timestamp.strip()
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
    return {
        "source": source,
        "dashboard_url": USAGE_DASHBOARD_URL,
        "plan_type": _first_string(plan_type),
        "allowed": allowed,
        "limit_reached": limit_reached,
        "windows": windows,
        "note": note,
    }


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
            SELECT feedback_log_body
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
    for (body,) in rows:
        for event in _extract_rate_limit_events(str(body or "")):
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
            try:
                return int(value)
            except ValueError:
                return value
    return None


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
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": 127, "summary": str(exc)}
    return {
        "exit_code": completed.returncode,
        "summary": "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part),
    }
