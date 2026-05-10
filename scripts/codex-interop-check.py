from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import shutil
import sqlite3
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SHARED_CODEX_PROVIDER_ID = "openai"
COCKPIT_HTTP_PROVIDER_ID = "cockpit_http"
OFFICIAL_OPENAI_BASE_URL = "https://api.openai.com/v1"
CODEX_HISTORY_INDEXES = {
    "idx_threads_archived_provider_updated_at_ms": {
        "columns": ("archived", "model_provider", "updated_at_ms", "id"),
        "sql": (
            "create index if not exists idx_threads_archived_provider_updated_at_ms "
            "on threads(archived, model_provider, updated_at_ms desc, id desc)"
        ),
    },
    "idx_threads_archived_provider_updated_at": {
        "columns": ("archived", "model_provider", "updated_at", "id"),
        "sql": (
            "create index if not exists idx_threads_archived_provider_updated_at "
            "on threads(archived, model_provider, updated_at desc, id desc)"
        ),
    },
    "idx_threads_archived_updated_at_ms": {
        "columns": ("archived", "updated_at_ms", "id"),
        "sql": (
            "create index if not exists idx_threads_archived_updated_at_ms "
            "on threads(archived, updated_at_ms desc, id desc)"
        ),
    },
    "idx_threads_archived_updated_at": {
        "columns": ("archived", "updated_at", "id"),
        "sql": (
            "create index if not exists idx_threads_archived_updated_at "
            "on threads(archived, updated_at desc, id desc)"
        ),
    },
}
CODEX_PROVIDER_BUCKET_TRIGGERS = {
    "trg_threads_shared_provider_after_insert": (
        "create trigger if not exists trg_threads_shared_provider_after_insert "
        "after insert on threads "
        "when coalesce(new.model_provider, '') <> 'openai' "
        "begin "
        "update threads set model_provider = 'openai' where id = new.id; "
        "end"
    ),
    "trg_threads_shared_provider_after_update": (
        "create trigger if not exists trg_threads_shared_provider_after_update "
        "after update of model_provider on threads "
        "when coalesce(new.model_provider, '') <> 'openai' "
        "begin "
        "update threads set model_provider = 'openai' where id = new.id; "
        "end"
    ),
}
CODEX_TUI_LOG_ROTATE_BYTES = 100 * 1024 * 1024


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Codex Cockpit Tools shared-history interop.")
    parser.add_argument("--codex-home", required=True)
    parser.add_argument("--cc-switch-db", required=True)
    parser.add_argument("--cockpit-home", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--migrate-provider-bucket", action="store_true")
    parser.add_argument("--quick-launch", action="store_true")
    args = parser.parse_args()

    codex_home = Path(args.codex_home).expanduser().resolve()
    cc_switch_db = Path(args.cc_switch_db).expanduser()
    cockpit_home = Path(args.cockpit_home).expanduser()

    before = inspect_interop(
        codex_home=codex_home,
        cc_switch_db=cc_switch_db,
        cockpit_home=cockpit_home,
        include_session_scan=not args.quick_launch,
    )
    actions: list[dict[str, Any]] = []
    if args.apply:
        actions.extend(repair_cockpit(codex_home=codex_home, cockpit_home=cockpit_home, checks=before))
        if args.migrate_provider_bucket:
            actions.extend(
                migrate_codex_provider_bucket(
                    codex_home=codex_home,
                    target_provider=SHARED_CODEX_PROVIDER_ID,
                    migrate_sessions=not args.quick_launch,
                )
            )
    after = inspect_interop(
        codex_home=codex_home,
        cc_switch_db=cc_switch_db,
        cockpit_home=cockpit_home,
        include_session_scan=not args.quick_launch,
    )

    payload = {
        "status": after["status"],
        "apply": bool(args.apply),
        "migrate_provider_bucket": bool(args.migrate_provider_bucket),
        "quick_launch": bool(args.quick_launch),
        "codex_home": str(codex_home),
        "cc_switch_db": str(cc_switch_db),
        "cockpit_home": str(cockpit_home),
        "before": before,
        "actions": actions,
        "after": after,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 2 if after["status"] == "fail" else 0


def inspect_interop(
    *,
    codex_home: Path,
    cc_switch_db: Path,
    cockpit_home: Path,
    include_session_scan: bool = True,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    provider_state = inspect_codex_provider_buckets(
        codex_home=codex_home,
        cockpit_home=cockpit_home,
        include_session_scan=include_session_scan,
    )
    checks.extend(provider_state["checks"])
    checks.extend(inspect_cc_switch(codex_home=codex_home, db_path=cc_switch_db))
    checks.extend(inspect_cockpit(codex_home=codex_home, cockpit_home=cockpit_home))
    status = aggregate_status(checks)
    return {"status": status, "checks": checks}


def aggregate_status(checks: list[dict[str, Any]]) -> str:
    if any(check.get("status") == "fail" for check in checks):
        return "fail"
    if any(check.get("status") in {"warn", "platform_na"} for check in checks):
        return "attention"
    return "pass"


def inspect_cc_switch(*, codex_home: Path, db_path: Path) -> list[dict[str, Any]]:
    if not db_path.exists():
        return [
            {
                "id": "cc_switch_installed",
                "tool": "cc_switch",
                "status": "platform_na",
                "reason": "CC Switch database not found.",
                "path": str(db_path),
            }
        ]
    try:
        connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
    except sqlite3.Error as exc:
        return [
            {
                "id": "cc_switch_db_open",
                "tool": "cc_switch",
                "status": "fail",
                "reason": f"Cannot open CC Switch database: {exc}",
                "path": str(db_path),
            }
        ]

    try:
        providers = connection.execute(
            "select id, name, settings_config, is_current from providers where app_type = 'codex'"
        ).fetchall()
    except sqlite3.Error as exc:
        return [
            {
                "id": "cc_switch_schema",
                "tool": "cc_switch",
                "status": "fail",
                "reason": f"Unexpected CC Switch schema: {exc}",
                "path": str(db_path),
            }
        ]
    finally:
        connection.close()

    return [
        {
            "id": "cc_switch_codex_boundary",
            "tool": "cc_switch",
            "status": "pass",
            "reason": "CC Switch is not the Codex switching source on this host; Cockpit Tools owns Codex auth/API switching.",
            "path": str(db_path),
            "codex_provider_count": len(providers),
            "codex_home": str(codex_home),
        }
    ]


def inspect_codex_provider_buckets(
    *,
    codex_home: Path,
    cockpit_home: Path,
    include_session_scan: bool = True,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    state_path = codex_home / "state_5.sqlite"
    config_path = codex_home / "config.toml"
    distribution, distribution_error = _read_codex_thread_provider_distribution(state_path)
    dominant_provider = _dominant_provider(distribution)
    unexpected_providers = {
        provider: count
        for provider, count in distribution.items()
        if provider != SHARED_CODEX_PROVIDER_ID and int(count) > 0
    }

    checks.append(
        {
            "id": "codex_thread_provider_distribution",
            "tool": "codex",
            "status": "fail" if distribution_error or unexpected_providers else "pass",
            "reason": distribution_error
            or (
                "Active Codex threads still use non-shared provider buckets; run repair with migrate-provider-bucket."
                if unexpected_providers
                else "Codex local history visibility is bucketed by threads.model_provider; all active threads use the shared provider bucket."
            ),
            "path": str(state_path),
            "distribution": distribution,
            "dominant_provider": dominant_provider,
            "expected_shared_provider": SHARED_CODEX_PROVIDER_ID,
            "unexpected_providers": unexpected_providers,
        }
    )
    if include_session_scan:
        checks.append(_inspect_codex_session_provider_bucket(codex_home))
    else:
        checks.append(
            {
                "id": "codex_session_provider_distribution",
                "tool": "codex",
                "status": "pass",
                "reason": "Quick launch skipped full session JSONL scan; SQLite trigger guard protects active history from stale session metadata repopulation.",
                "path": str(codex_home / "sessions"),
                "session_scan_skipped": True,
                "expected_shared_provider": SHARED_CODEX_PROVIDER_ID,
            }
        )

    config_text = _read_text(config_path)
    active_provider = _toml_top_level_string(config_text, "model_provider") or "openai"
    current = _cockpit_current_account(cockpit_home)
    current_auth_mode = str(current.get("auth_mode") or "") if current else ""
    active_status = "pass"
    active_reason = "Codex live config uses the same provider bucket as the dominant local history bucket."
    if dominant_provider and active_provider != dominant_provider:
        if current_auth_mode == "apikey" and active_provider == COCKPIT_HTTP_PROVIDER_ID:
            active_status = "pass"
            active_reason = "Codex API relay uses a custom HTTP-only provider to disable unsupported Responses WebSocket transport; SQLite trigger guards keep active history in the shared provider bucket."
        else:
            active_status = "fail" if _is_custom_provider_id(active_provider) else "warn"
            active_reason = "Codex live config points at a different provider bucket than the dominant local history bucket."
    checks.append(
        {
            "id": "codex_live_provider_bucket",
            "tool": "codex",
            "status": active_status,
            "reason": active_reason,
            "path": str(config_path),
            "active_provider": active_provider,
            "dominant_provider": dominant_provider,
        }
    )

    checks.extend(
        _inspect_cockpit_current_provider_bucket(
            cockpit_home,
            dominant_provider,
            config_text,
            active_provider,
        )
    )
    return {"checks": checks, "distribution": distribution, "dominant_provider": dominant_provider}


def _inspect_cockpit_current_provider_bucket(
    cockpit_home: Path,
    dominant_provider: str | None,
    config_text: str,
    active_provider: str,
) -> list[dict[str, Any]]:
    current = _cockpit_current_account(cockpit_home)
    if not current:
        return []
    provider_bucket = SHARED_CODEX_PROVIDER_ID
    auth_mode = str(current.get("auth_mode") or "")
    base_url = _cockpit_account_base_url(current)
    has_key = bool(str(current.get("openai_api_key") or "").strip())
    key_status = "pass"
    key_reason = "Current Cockpit Codex account can be projected into Codex."
    if auth_mode == "apikey" and not has_key:
        key_status = "fail"
        key_reason = "Current Cockpit Codex API account has no API key to project into Codex CLI/App."
    elif auth_mode == "apikey" and not base_url:
        key_status = "fail"
        key_reason = "Current Cockpit Codex API account has no API base URL."
    bucket_status = "pass"
    bucket_reason = "Current Cockpit Codex account will use the stable shared Codex provider bucket."
    if dominant_provider and dominant_provider != provider_bucket:
        bucket_status = "fail"
        bucket_reason = "Existing Codex history is still in a different provider bucket and should be migrated."
    expected_forced_login = "api" if auth_mode == "apikey" else "chatgpt"
    active_forced_login = _toml_top_level_string(config_text, "forced_login_method") or "chatgpt"
    provider_info = _model_provider_info(config_text, active_provider)
    requires_openai_auth = provider_info.get("requires_openai_auth") if isinstance(provider_info, dict) else None
    login_issues: list[str] = []
    if active_forced_login != expected_forced_login:
        login_issues.append(
            f"forced_login_method is {active_forced_login}, expected {expected_forced_login}"
        )
    if active_provider != "openai" and expected_forced_login == "api" and requires_openai_auth is not False:
        login_issues.append("active provider still requires OpenAI auth while current Cockpit account is API key mode")
    if active_provider != "openai" and expected_forced_login == "chatgpt" and requires_openai_auth is False:
        login_issues.append("active provider disables OpenAI auth while current Cockpit account is ChatGPT auth mode")
    login_status = "fail" if login_issues else "pass"
    return [
        {
            "id": "cockpit_current_account_projectable",
            "tool": "cockpit_tools",
            "status": key_status,
            "reason": key_reason,
            "path": str(cockpit_home),
            "account_id": current.get("id"),
            "auth_mode": auth_mode,
            "api_provider_id": current.get("api_provider_id"),
            "api_provider_name": current.get("api_provider_name"),
            "base_url": base_url,
        },
        {
            "id": "cockpit_current_provider_bucket",
            "tool": "cockpit_tools",
            "status": bucket_status,
            "reason": bucket_reason,
            "path": str(cockpit_home),
            "provider_bucket": provider_bucket,
            "dominant_provider": dominant_provider,
            "expected_shared_provider": SHARED_CODEX_PROVIDER_ID,
            "repair_strategy": "stable_openai_provider" if bucket_status == "fail" else "none",
        },
        {
            "id": "cockpit_live_login_mode_matches_current_account",
            "tool": "cockpit_tools",
            "status": login_status,
            "reason": "Codex direct CLI/App startup must use the same login mode as the current Cockpit Codex account.",
            "path": str(cockpit_home),
            "active_provider": active_provider,
            "active_forced_login_method": active_forced_login,
            "expected_forced_login_method": expected_forced_login,
            "requires_openai_auth": requires_openai_auth,
            "issues": login_issues,
        },
    ]


def inspect_cockpit(*, codex_home: Path, cockpit_home: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    if not cockpit_home.exists():
        return [
            {
                "id": "cockpit_installed",
                "tool": "cockpit_tools",
                "status": "platform_na",
                "reason": "Cockpit Tools state directory not found.",
                "path": str(cockpit_home),
            }
        ]

    accounts_path = cockpit_home / "codex_accounts.json"
    providers_path = cockpit_home / "codex_model_providers.json"
    instances_path = cockpit_home / "codex_instances.json"
    accounts = _read_json(accounts_path)
    providers = _read_json(providers_path)
    instances = _read_json(instances_path)
    cockpit_config = _read_json(cockpit_home / "config.json")
    current = _cockpit_current_account(cockpit_home)

    checks.append(
        {
            "id": "cockpit_codex_accounts_present",
            "tool": "cockpit_tools",
            "status": "pass" if _list_len(accounts.get("accounts")) > 0 else "warn",
            "reason": "Cockpit Tools should expose its Codex account inventory for account switching.",
            "path": str(accounts_path),
            "account_count": _list_len(accounts.get("accounts")),
            "current_account_present": bool(accounts.get("current_account_id")),
        }
    )
    checks.append(
        {
            "id": "cockpit_codex_providers_present",
            "tool": "cockpit_tools",
            "status": "pass" if _list_len(providers) > 0 else "warn",
            "reason": "Cockpit Tools should expose its Codex provider inventory for relay/API switching.",
            "path": str(providers_path),
            "provider_count": _list_len(providers),
        }
    )
    checks.append(
        {
            "id": "cockpit_codex_current_account_present",
            "tool": "cockpit_tools",
            "status": "pass" if current else "fail",
            "reason": "Cockpit Tools current Codex account is the Codex auth/API switching source.",
            "path": str(accounts_path),
            "current_account_id": accounts.get("current_account_id") if isinstance(accounts, dict) else None,
            "auth_mode": current.get("auth_mode") if current else None,
            "api_provider_id": current.get("api_provider_id") if current else None,
        }
    )
    restart_on_switch = bool(cockpit_config.get("codex_restart_specified_app_on_switch")) if isinstance(cockpit_config, dict) else False
    specified_app_path = (
        str(cockpit_config.get("codex_specified_app_path") or "") if isinstance(cockpit_config, dict) else ""
    )
    expected_restart_wrapper = str(_expected_cockpit_restart_wrapper(codex_home))
    managed_restart_enabled = restart_on_switch and _same_path(specified_app_path, expected_restart_wrapper)
    checks.append(
        {
            "id": "cockpit_codex_app_restart_semantics",
            "tool": "cockpit_tools",
            "status": "pass" if managed_restart_enabled else "fail",
            "reason": (
                "Cockpit Codex switches must launch through the governed restart wrapper so Codex App receives the current account auth, API base URL, and pre-launch validation instead of reusing stale process state."
            ),
            "path": str(cockpit_home / "config.json"),
            "codex_restart_specified_app_on_switch": restart_on_switch,
            "codex_specified_app_path": specified_app_path,
            "expected_restart_wrapper": expected_restart_wrapper,
            "managed_restart_enabled": managed_restart_enabled,
            "repair_strategy": "configure_restart_wrapper" if not managed_restart_enabled else "none",
        }
    )

    isolation_findings = _cockpit_instance_isolation_findings(instances, codex_home)
    account_binding_findings = _cockpit_account_binding_findings(instances)
    stale_last_pid = _cockpit_stale_last_pid(instances)
    last_pid = _cockpit_default_last_pid(instances)
    last_pid_status = "pass"
    if stale_last_pid is not None:
        last_pid_status = "warn"
    checks.append(
        {
            "id": "cockpit_codex_instances_share_state",
            "tool": "cockpit_tools",
            "status": "fail" if isolation_findings else "pass",
            "reason": "Cockpit Codex instances must not force a different CODEX_HOME/sqlite_home/log_dir when shared history is expected.",
            "path": str(instances_path),
            "findings": isolation_findings,
            "expected_codex_home": str(codex_home),
            "instance_count": _list_len(instances.get("instances")) if isinstance(instances, dict) else 0,
        }
    )
    checks.append(
        {
            "id": "cockpit_codex_instances_follow_current_account",
            "tool": "cockpit_tools",
            "status": "fail" if account_binding_findings else "pass",
            "reason": "Cockpit Codex default launch settings must follow the current account; a fixed bindAccountId can relaunch an old OAuth account after the user switches to an API account.",
            "path": str(instances_path),
            "findings": account_binding_findings,
        }
    )
    checks.append(
        {
            "id": "cockpit_codex_instances_last_pid_current",
            "tool": "cockpit_tools",
            "status": last_pid_status,
            "reason": "Cockpit Tools persists the last Codex App PID; stale values can produce repeated process-not-found noise during CLI/App startup.",
            "path": str(instances_path),
            "lastPid": last_pid,
            "stale_lastPid": stale_last_pid,
        }
    )
    return checks


def repair_cockpit(*, codex_home: Path, cockpit_home: Path, checks: dict[str, Any]) -> list[dict[str, Any]]:
    actions = repair_cockpit_stale_last_pid(cockpit_home=cockpit_home)
    actions.extend(repair_cockpit_restart_wrapper_config(codex_home=codex_home, cockpit_home=cockpit_home))
    actions.extend(repair_cockpit_default_account_binding(cockpit_home=cockpit_home))
    actions.extend(repair_cockpit_current_api_provider_metadata(codex_home=codex_home, cockpit_home=cockpit_home))
    current = _cockpit_current_account(cockpit_home)
    if not current:
        return actions
    actions.extend(repair_codex_live_config_for_cockpit(codex_home=codex_home, account=current))
    actions.extend(repair_codex_auth_for_cockpit(codex_home=codex_home, account=current))
    actions.extend(ensure_codex_history_indexes(codex_home=codex_home))
    actions.extend(ensure_codex_provider_bucket_triggers(codex_home=codex_home))
    actions.extend(rotate_large_codex_tui_log(codex_home=codex_home))
    return actions


def repair_cockpit_stale_last_pid(*, cockpit_home: Path) -> list[dict[str, Any]]:
    instances_path = cockpit_home / "codex_instances.json"
    instances = _read_json(instances_path)
    stale_last_pid = _cockpit_stale_last_pid(instances)
    if stale_last_pid is None:
        return []
    if not isinstance(instances, dict):
        return []
    default_settings = instances.get("defaultSettings")
    if not isinstance(default_settings, dict):
        return []
    backup_path = _backup_file(instances_path, suffix="cockpit_lastpid") if instances_path.exists() else None
    default_settings["lastPid"] = None
    instances_path.parent.mkdir(parents=True, exist_ok=True)
    instances_path.write_text(json.dumps(instances, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return [
        {
            "id": "cockpit_codex_stale_last_pid_cleared",
            "tool": "cockpit_tools",
            "status": "changed",
            "path": str(instances_path),
            "backup_path": str(backup_path) if backup_path else None,
            "cleared_lastPid": stale_last_pid,
        }
    ]


def repair_cockpit_restart_wrapper_config(*, codex_home: Path, cockpit_home: Path) -> list[dict[str, Any]]:
    config_path = cockpit_home / "config.json"
    config = _read_json(config_path)
    if not isinstance(config, dict):
        config = {}
    expected_wrapper = str(_expected_cockpit_restart_wrapper(codex_home))
    already_configured = (
        bool(config.get("codex_launch_on_switch"))
        and bool(config.get("codex_restart_specified_app_on_switch"))
        and _same_path(str(config.get("codex_specified_app_path") or ""), expected_wrapper)
    )
    if already_configured:
        return [
            {
                "id": "cockpit_codex_restart_wrapper_configured",
                "tool": "cockpit_tools",
                "status": "ok",
                "path": str(config_path),
                "codex_specified_app_path": expected_wrapper,
            }
        ]
    backup_path = _backup_file(config_path, suffix="cockpit_restart_wrapper") if config_path.exists() else None
    config["codex_launch_on_switch"] = True
    config["codex_restart_specified_app_on_switch"] = True
    config["codex_specified_app_path"] = expected_wrapper
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return [
        {
            "id": "cockpit_codex_restart_wrapper_configured",
            "tool": "cockpit_tools",
            "status": "changed",
            "path": str(config_path),
            "backup_path": str(backup_path) if backup_path else None,
            "codex_specified_app_path": expected_wrapper,
        }
    ]


def repair_cockpit_default_account_binding(*, cockpit_home: Path) -> list[dict[str, Any]]:
    instances_path = cockpit_home / "codex_instances.json"
    instances = _read_json(instances_path)
    findings = _cockpit_account_binding_findings(instances)
    if not findings or not isinstance(instances, dict):
        return []
    default_settings = instances.get("defaultSettings")
    if not isinstance(default_settings, dict):
        return []
    backup_path = _backup_file(instances_path, suffix="cockpit_follow_current_account") if instances_path.exists() else None
    default_settings["followLocalAccount"] = True
    default_settings["bindAccountId"] = None
    instances_path.parent.mkdir(parents=True, exist_ok=True)
    instances_path.write_text(json.dumps(instances, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return [
        {
            "id": "cockpit_codex_instances_follow_current_account_repaired",
            "tool": "cockpit_tools",
            "status": "changed",
            "path": str(instances_path),
            "backup_path": str(backup_path) if backup_path else None,
            "findings": findings,
        }
    ]


def repair_cockpit_current_api_provider_metadata(*, codex_home: Path, cockpit_home: Path) -> list[dict[str, Any]]:
    account = _cockpit_current_account(cockpit_home)
    if str(account.get("auth_mode") or "").strip() != "apikey":
        return []
    if _cockpit_account_base_url(account):
        return []
    account_key = str(account.get("openai_api_key") or "").strip()
    if not account_key:
        return []

    auth = _read_json(codex_home / "auth.json")
    auth_key = str(auth.get("OPENAI_API_KEY") or "").strip() if isinstance(auth, dict) else ""
    if auth_key and auth_key != account_key:
        return []

    config = _read_text(codex_home / "config.toml")
    base_url = (
        _json_string(auth, "api_base_url")
        or _json_string(auth, "base_url")
        or _toml_top_level_string(config, "openai_base_url")
    )
    if not base_url:
        return []
    base_url = base_url.strip().rstrip("/")
    provider = _cockpit_provider_for_base_url(cockpit_home, base_url)
    provider_id = provider.get("id") or _json_string(auth, "api_provider_id") or _provider_id_from_base_url(base_url)
    provider_name = provider.get("name") or _json_string(auth, "api_provider_name") or _provider_name_from_base_url(base_url)

    account_id = str(account.get("id") or "").strip()
    if not account_id:
        return []
    account_path = cockpit_home / "codex_accounts" / f"{account_id}.json"
    if not account_path.exists():
        return []

    updated = dict(account)
    updated["api_provider_mode"] = "custom"
    updated["api_base_url"] = base_url
    updated["api_provider_id"] = provider_id
    updated["api_provider_name"] = provider_name
    if updated == account:
        return []

    backup_path = _backup_file(account_path, suffix="cockpit_api_provider")
    account_path.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return [
        {
            "id": "cockpit_current_api_provider_metadata_restored",
            "tool": "cockpit_tools",
            "status": "changed",
            "path": str(account_path),
            "backup_path": str(backup_path),
            "account_id": account_id,
            "api_provider_id": provider_id,
            "api_provider_name": provider_name,
            "base_url": base_url,
        }
    ]


def repair_codex_auth_for_cockpit(*, codex_home: Path, account: dict[str, Any]) -> list[dict[str, Any]]:
    auth_mode = str(account.get("auth_mode") or "").strip()
    if auth_mode == "apikey":
        api_key = str(account.get("openai_api_key") or "").strip()
        if not api_key:
            return []
        base_url = _cockpit_account_base_url(account)
        if not base_url:
            return []
        payload: dict[str, Any] = {
            "OPENAI_API_KEY": api_key,
            "auth_mode": "apikey",
        }
        if base_url:
            payload["base_url"] = base_url
            payload["api_base_url"] = base_url
            payload["api_provider_mode"] = "custom"
            if account.get("api_provider_id"):
                payload["api_provider_id"] = account.get("api_provider_id")
            if account.get("api_provider_name"):
                payload["api_provider_name"] = account.get("api_provider_name")
    else:
        tokens = account.get("tokens")
        if not isinstance(tokens, dict) or not tokens.get("access_token"):
            return []
        tokens = dict(tokens)
        account_id = account.get("account_id")
        if account_id and not tokens.get("account_id"):
            tokens["account_id"] = account_id
        payload = {
            "auth_mode": "chatgpt",
            "OPENAI_API_KEY": None,
            "tokens": tokens,
        }
        updated_at = account.get("token_updated_at")
        if isinstance(updated_at, (int, float)) and updated_at > 0:
            payload["last_refresh"] = datetime.fromtimestamp(updated_at, tz=timezone.utc).isoformat()
    auth_path = codex_home / "auth.json"
    current_text = _read_text(auth_path).strip()
    updated_text = json.dumps(payload, ensure_ascii=False, indent=2)
    if _json_semantically_equal(current_text, payload):
        return []
    backup_path = _backup_file(auth_path, suffix="cockpit_auth") if auth_path.exists() else None
    auth_path.parent.mkdir(parents=True, exist_ok=True)
    auth_path.write_text(updated_text + "\n", encoding="utf-8")
    return [
        {
            "id": "codex_auth_cockpit_projected",
            "tool": "codex",
            "status": "changed",
            "path": str(auth_path),
            "backup_path": str(backup_path) if backup_path else None,
            "account_id": account.get("id"),
            "auth_mode": auth_mode,
            "api_provider_id": account.get("api_provider_id"),
            "api_provider_name": account.get("api_provider_name"),
        }
    ]


def repair_codex_live_config_for_cockpit(*, codex_home: Path, account: dict[str, Any]) -> list[dict[str, Any]]:
    base_url = _cockpit_account_base_url(account)
    if not base_url:
        return []
    forced_login = "api" if account.get("auth_mode") == "apikey" else "chatgpt"
    target_provider = COCKPIT_HTTP_PROVIDER_ID if forced_login == "api" else SHARED_CODEX_PROVIDER_ID
    config_path = codex_home / "config.toml"
    current = _read_text(config_path)
    lines = current.splitlines()
    lines = _remove_top_level_key(lines, "openai_base_url")
    if forced_login == "api" and target_provider == SHARED_CODEX_PROVIDER_ID:
        lines = _set_top_level(lines, "openai_base_url", _toml_string(base_url))
    lines = _set_top_level(lines, "forced_login_method", _toml_string(forced_login))
    lines = _set_top_level(lines, "model_provider", _toml_string(target_provider))
    lines = _remove_toml_table(lines, "[model_providers.cockpit]")
    lines = _remove_toml_table(lines, "[model_providers.openai]")
    lines = _remove_toml_table(lines, "[model_providers.ccswitch]")
    lines = _replace_toml_table(
        lines,
        f"[model_providers.{COCKPIT_HTTP_PROVIDER_ID}]",
        _cockpit_http_provider_lines(base_url),
    )
    lines = _replace_toml_table(
        lines,
        "[profiles.shared-current-provider]",
        _cockpit_profile_lines("shared-current-provider", forced_login=forced_login, base_url=base_url),
    )
    lines = _replace_toml_table(
        lines,
        "[profiles.shared-cockpit-api]",
        _cockpit_profile_lines("shared-cockpit-api", forced_login="api", base_url=base_url),
    )
    lines = _replace_toml_table(
        lines,
        "[profiles.shared-cockpit-auth]",
        _cockpit_profile_lines("shared-cockpit-auth", forced_login="chatgpt", base_url=base_url),
    )
    lines = _replace_toml_table(
        lines,
        "[profiles.shared-relay]",
        _cockpit_profile_lines("shared-relay", forced_login=forced_login, base_url=base_url),
    )
    updated = "\n".join(lines).rstrip() + "\n"
    if updated == current:
        return []
    backup_path = _backup_file(config_path, suffix="cockpit_provider") if config_path.exists() else None
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(updated, encoding="utf-8")
    return [
        {
            "id": "codex_live_config_cockpit_provider",
            "tool": "codex",
            "status": "changed",
            "path": str(config_path),
            "backup_path": str(backup_path) if backup_path else None,
            "target_provider": target_provider,
            "history_provider_bucket": SHARED_CODEX_PROVIDER_ID,
            "forced_login_method": forced_login,
            "base_url": base_url,
            "account_id": account.get("id"),
            "api_provider_id": account.get("api_provider_id"),
            "api_provider_name": account.get("api_provider_name"),
        }
    ]


def _cockpit_profile_lines(name: str, *, forced_login: str, base_url: str) -> list[str]:
    provider = COCKPIT_HTTP_PROVIDER_ID if forced_login == "api" else SHARED_CODEX_PROVIDER_ID
    lines = [
        f"[profiles.{name}]",
        f"forced_login_method = {_toml_string(forced_login)}",
        f"model_provider = {_toml_string(provider)}",
    ]
    if forced_login == "api" and provider == SHARED_CODEX_PROVIDER_ID:
        lines.append(f"openai_base_url = {_toml_string(base_url)}")
    return lines


def _cockpit_http_provider_lines(base_url: str) -> list[str]:
    return [
        f"[model_providers.{COCKPIT_HTTP_PROVIDER_ID}]",
        'name = "Cockpit HTTP Relay"',
        f"base_url = {_toml_string(base_url)}",
        'wire_api = "responses"',
        'env_key = "OPENAI_API_KEY"',
        "requires_openai_auth = false",
        "supports_websockets = false",
    ]


def migrate_codex_provider_bucket(
    *,
    codex_home: Path,
    target_provider: str,
    migrate_sessions: bool = True,
) -> list[dict[str, Any]]:
    state_path = codex_home / "state_5.sqlite"
    actions: list[dict[str, Any]] = []
    if migrate_sessions:
        actions.extend(_migrate_codex_session_provider_bucket(codex_home=codex_home, target_provider=target_provider))
    else:
        actions.append(
            {
                "id": "codex_session_provider_bucket_migrated",
                "tool": "codex",
                "status": "ok",
                "path": str(codex_home / "sessions"),
                "target_provider": target_provider,
                "session_scan_skipped": True,
                "reason": "Quick launch skips full session JSONL migration; SQLite trigger guard handles active history writes.",
            }
        )
    if not state_path.exists():
        return actions
    connection = sqlite3.connect(str(state_path), timeout=15)
    try:
        thread_columns = _sqlite_table_columns(connection, "threads")
        required_columns = {"model_provider"}
        missing_columns = sorted(required_columns - thread_columns)
        if not thread_columns:
            return [
                {
                    "id": "codex_threads_provider_bucket_migrated",
                    "tool": "codex",
                    "status": "fail",
                    "path": str(state_path),
                    "reason": "Codex state database has no threads table; provider bucket migration cannot run.",
                }
            ]
        if missing_columns:
            return [
                {
                    "id": "codex_threads_provider_bucket_migrated",
                    "tool": "codex",
                    "status": "fail",
                    "path": str(state_path),
                    "reason": "Codex state database threads table is missing required columns.",
                    "missing_columns": missing_columns,
                }
            ]
        pending = connection.execute(
            """
            select count(*)
            from threads
            where coalesce(model_provider, '') <> ?
            """,
            (target_provider,),
        ).fetchone()[0]
        if int(pending or 0) > 0:
            connection.close()
            backup_path = _backup_file(state_path, suffix="provider_bucket")
            connection = sqlite3.connect(str(state_path), timeout=15)
            actions.append(
                {
                    "id": "codex_state_db_backup",
                    "tool": "codex",
                    "status": "ok",
                    "backup_path": str(backup_path),
                }
            )
        updated = connection.execute(
            """
            update threads
            set model_provider = ?
            where coalesce(model_provider, '') <> ?
            """,
            (target_provider, target_provider),
        ).rowcount
        connection.commit()
        actions.append(
            {
                "id": "codex_threads_provider_bucket_migrated",
                "tool": "codex",
                "status": "changed" if updated else "ok",
                "target_provider": target_provider,
                "updated_rows": int(updated or 0),
            }
        )
    finally:
        connection.close()
    return actions


def _migrate_codex_session_provider_bucket(*, codex_home: Path, target_provider: str) -> list[dict[str, Any]]:
    sessions_dir = codex_home / "sessions"
    if not sessions_dir.exists():
        return []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = codex_home / "backups" / f"session_provider_bucket_{timestamp}"
    manifest_path = backup_dir / "changed-lines.jsonl"
    files_scanned = 0
    files_changed = 0
    lines_changed = 0
    provider_updates = 0
    errors: list[dict[str, str]] = []
    backup_dir_created = False
    for path in sorted(sessions_dir.rglob("*.jsonl")):
        files_scanned += 1
        try:
            changed = _rewrite_session_jsonl_provider_bucket(
                path,
                sessions_dir=sessions_dir,
                manifest_path=manifest_path,
                target_provider=target_provider,
                ensure_backup_dir=lambda: _ensure_backup_dir(backup_dir),
            )
        except OSError as exc:
            errors.append({"path": str(path), "reason": str(exc)})
            continue
        if not changed:
            continue
        backup_dir_created = True
        files_changed += 1
        lines_changed += int(changed["lines_changed"])
        provider_updates += int(changed["provider_updates"])
    all_errors_locked = bool(errors) and all(
        _file_locked_for_exclusive_access(Path(error["path"])) for error in errors
    )
    status = "warn" if all_errors_locked else ("fail" if errors else ("changed" if files_changed else "ok"))
    action: dict[str, Any] = {
        "id": "codex_session_provider_bucket_migrated",
        "tool": "codex",
        "status": status,
        "path": str(sessions_dir),
        "target_provider": target_provider,
        "files_scanned": files_scanned,
        "files_changed": files_changed,
        "lines_changed": lines_changed,
        "provider_updates": provider_updates,
    }
    if backup_dir_created:
        action["backup_manifest"] = str(manifest_path)
    if errors:
        action["errors"] = errors[:10]
        action["error_count"] = len(errors)
    return [action]


def _rewrite_session_jsonl_provider_bucket(
    path: Path,
    *,
    sessions_dir: Path,
    manifest_path: Path,
    target_provider: str,
    ensure_backup_dir: Any,
) -> dict[str, int] | None:
    temp_path = path.with_name(f".{path.name}.provider-bucket.tmp")
    original_stat = path.stat()
    lines_changed = 0
    provider_updates = 0
    changed_records: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as source, temp_path.open(
            "w", encoding="utf-8", newline=""
        ) as target:
            for line_number, line in enumerate(source, start=1):
                if "model_provider" not in line:
                    target.write(line)
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    target.write(line)
                    continue
                updated = _replace_json_model_provider(payload, target_provider)
                if updated <= 0:
                    target.write(line)
                    continue
                lines_changed += 1
                provider_updates += updated
                changed_records.append(
                    {
                        "path": str(path.relative_to(sessions_dir)),
                        "line": line_number,
                        "old": line.rstrip("\n"),
                    }
                )
                target.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        if lines_changed <= 0:
            temp_path.unlink(missing_ok=True)
            return None
        ensure_backup_dir()
        with manifest_path.open("a", encoding="utf-8", newline="\n") as manifest:
            for record in changed_records:
                manifest.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path.replace(path)
        os.utime(path, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    return {"lines_changed": lines_changed, "provider_updates": provider_updates}


def _ensure_backup_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _replace_json_model_provider(value: Any, target_provider: str) -> int:
    updates = 0
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "model_provider" and isinstance(child, str) and child != target_provider:
                value[key] = target_provider
                updates += 1
                continue
            updates += _replace_json_model_provider(child, target_provider)
    elif isinstance(value, list):
        for child in value:
            updates += _replace_json_model_provider(child, target_provider)
    return updates


def ensure_codex_history_indexes(*, codex_home: Path) -> list[dict[str, Any]]:
    state_path = codex_home / "state_5.sqlite"
    if not state_path.exists():
        return []
    connection = sqlite3.connect(str(state_path), timeout=15)
    try:
        tables = {
            str(row[0])
            for row in connection.execute(
                "select name from sqlite_master where type = 'table'"
            ).fetchall()
        }
        if "threads" not in tables:
            return []
        thread_columns = {
            str(row[1])
            for row in connection.execute("pragma table_info(threads)").fetchall()
        }
        existing_indexes = {
            str(row[0])
            for row in connection.execute(
                "select name from sqlite_master where type = 'index'"
            ).fetchall()
        }
        missing: list[str] = []
        skipped: dict[str, list[str]] = {}
        for name, definition in CODEX_HISTORY_INDEXES.items():
            columns = tuple(definition["columns"])
            missing_columns = [column for column in columns if column not in thread_columns]
            if missing_columns:
                skipped[name] = missing_columns
                continue
            if name in existing_indexes:
                continue
            connection.execute(str(definition["sql"]))
            missing.append(name)
        connection.commit()
    finally:
        connection.close()
    return [
        {
            "id": "codex_history_indexes_ensured",
            "tool": "codex",
            "status": "changed" if missing else "ok",
            "path": str(state_path),
            "created_indexes": missing,
            "skipped_indexes": skipped,
            "target_indexes": list(CODEX_HISTORY_INDEXES),
        }
    ]


def ensure_codex_provider_bucket_triggers(*, codex_home: Path) -> list[dict[str, Any]]:
    state_path = codex_home / "state_5.sqlite"
    if not state_path.exists():
        return []
    connection = sqlite3.connect(str(state_path), timeout=15)
    try:
        tables = {
            str(row[0])
            for row in connection.execute(
                "select name from sqlite_master where type = 'table'"
            ).fetchall()
        }
        if "threads" not in tables:
            return []
        thread_columns = _sqlite_table_columns(connection, "threads")
        missing_columns = sorted({"id", "model_provider"} - thread_columns)
        if missing_columns:
            return [
                {
                    "id": "codex_provider_bucket_triggers_ensured",
                    "tool": "codex",
                    "status": "fail",
                    "path": str(state_path),
                    "reason": "Codex state database threads table is missing required columns.",
                    "missing_columns": missing_columns,
                }
            ]
        existing_triggers = {
            str(row[0])
            for row in connection.execute(
                "select name from sqlite_master where type = 'trigger'"
            ).fetchall()
        }
        missing = [name for name in CODEX_PROVIDER_BUCKET_TRIGGERS if name not in existing_triggers]
        for name in missing:
            connection.execute(CODEX_PROVIDER_BUCKET_TRIGGERS[name])
        connection.commit()
    finally:
        connection.close()
    return [
        {
            "id": "codex_provider_bucket_triggers_ensured",
            "tool": "codex",
            "status": "changed" if missing else "ok",
            "path": str(state_path),
            "created_triggers": missing,
            "target_provider": SHARED_CODEX_PROVIDER_ID,
        }
    ]


def rotate_large_codex_tui_log(*, codex_home: Path) -> list[dict[str, Any]]:
    log_path = codex_home / "log" / "codex-tui.log"
    if not log_path.exists():
        return []
    try:
        size_bytes = log_path.stat().st_size
    except OSError as exc:
        return [
            {
                "id": "codex_tui_log_rotation",
                "tool": "codex",
                "status": "platform_na",
                "path": str(log_path),
                "reason": f"Cannot stat Codex TUI log: {exc}",
            }
        ]
    if size_bytes <= CODEX_TUI_LOG_ROTATE_BYTES:
        return [
            {
                "id": "codex_tui_log_rotation",
                "tool": "codex",
                "status": "ok",
                "path": str(log_path),
                "size_bytes": size_bytes,
                "threshold_bytes": CODEX_TUI_LOG_ROTATE_BYTES,
            }
        ]
    backup_dir = log_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"codex-tui.{timestamp}.log"
    try:
        log_path.replace(backup_path)
        log_path.write_text(
            (
                "rotated by codex interop repair "
                f"at {datetime.now(timezone.utc).isoformat()} "
                f"from {backup_path}\n"
            ),
            encoding="utf-8",
        )
    except OSError as exc:
        return [
            {
                "id": "codex_tui_log_rotation",
                "tool": "codex",
                "status": "platform_na",
                "path": str(log_path),
                "size_bytes": size_bytes,
                "threshold_bytes": CODEX_TUI_LOG_ROTATE_BYTES,
                "reason": f"Cannot rotate Codex TUI log, likely because another Codex process holds it: {exc}",
            }
        ]
    return [
        {
            "id": "codex_tui_log_rotation",
            "tool": "codex",
            "status": "changed",
            "path": str(log_path),
            "backup_path": str(backup_path),
            "size_bytes": size_bytes,
            "threshold_bytes": CODEX_TUI_LOG_ROTATE_BYTES,
        }
    ]


def _backup_file(path: Path, *, suffix: str) -> Path:
    backup_dir = path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{path.name}.{timestamp}_{suffix}.bak"
    shutil.copy2(path, backup_path)
    return backup_path


def _expected_cockpit_restart_wrapper(codex_home: Path) -> Path:
    return codex_home.parent / ".local" / "bin" / "codex-cockpit-app-restart.cmd"


def _same_path(left: str, right: str) -> bool:
    if not left or not right:
        return False
    try:
        return Path(left).expanduser().resolve() == Path(right).expanduser().resolve()
    except OSError:
        return left.strip().lower() == right.strip().lower()


def _remove_top_level_key(lines: list[str], key: str) -> list[str]:
    result: list[str] = []
    in_top_level = True
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("["):
            in_top_level = False
        if in_top_level and stripped.startswith(f"{key} ="):
            continue
        result.append(line)
    return result


def _remove_toml_table(lines: list[str], header: str) -> list[str]:
    result: list[str] = []
    in_target = False
    for line in lines:
        stripped = line.strip()
        if stripped == header:
            in_target = True
            continue
        if in_target and stripped.startswith("["):
            in_target = False
        if not in_target:
            result.append(line)
    return result


def _replace_toml_table(lines: list[str], header: str, replacement: list[str]) -> list[str]:
    result = _remove_toml_table(lines, header)
    if result and result[-1].strip():
        result.append("")
    result.extend(replacement)
    return result


def _read_codex_thread_provider_distribution(state_path: Path) -> tuple[dict[str, int], str | None]:
    if not state_path.exists():
        return {}, None
    try:
        connection = sqlite3.connect(f"file:{state_path}?mode=ro", uri=True)
        thread_columns = _sqlite_table_columns(connection, "threads")
        required_columns = {"model_provider", "archived"}
        if not thread_columns:
            return {}, "Codex state database has no threads table; cannot inspect history provider buckets."
        missing_columns = sorted(required_columns - thread_columns)
        if missing_columns:
            return (
                {},
                "Codex state database threads table is missing required columns: "
                + ", ".join(missing_columns),
            )
        rows = connection.execute(
            """
            select coalesce(model_provider, '') as provider, count(*) as n
            from threads
            where coalesce(archived, 0) = 0
            group by coalesce(model_provider, '')
            order by n desc, provider asc
            """
        ).fetchall()
    except sqlite3.Error as exc:
        return {}, f"Cannot read Codex thread provider distribution from threads table: {exc}"
    finally:
        try:
            connection.close()
        except UnboundLocalError:
            pass
    return {str(provider or "<empty>"): int(count) for provider, count in rows}, None


def _inspect_codex_session_provider_bucket(codex_home: Path) -> dict[str, Any]:
    session_distribution, session_error, session_stats = _read_codex_session_provider_distribution(codex_home)
    unexpected_session_providers = {
        provider: count
        for provider, count in session_distribution.items()
        if provider != SHARED_CODEX_PROVIDER_ID and int(count) > 0
    }
    session_unexpected_status = "pass"
    if session_error:
        session_unexpected_status = "fail"
    elif unexpected_session_providers:
        if (
            int(session_stats.get("stale_provider_files", 0)) > 0
            and session_stats.get("stale_provider_files") == session_stats.get("locked_stale_provider_files")
        ):
            session_unexpected_status = "warn"
        else:
            session_unexpected_status = "fail"
    return {
        "id": "codex_session_provider_distribution",
        "tool": "codex",
        "status": session_unexpected_status,
        "reason": session_error
        or (
            "Codex session JSONL metadata still contains non-shared provider buckets, but the remaining stale files are locked by a live Codex process; repair will retry on the next launch."
            if session_unexpected_status == "warn"
            else "Codex session JSONL metadata still contains non-shared provider buckets and can repopulate state_5.sqlite during resume."
            if unexpected_session_providers
            else "Codex session JSONL metadata uses the shared provider bucket."
        ),
        "path": str(codex_home / "sessions"),
        "distribution": session_distribution,
        "expected_shared_provider": SHARED_CODEX_PROVIDER_ID,
        "unexpected_providers": unexpected_session_providers,
        **session_stats,
    }


def _read_codex_session_provider_distribution(codex_home: Path) -> tuple[dict[str, int], str | None, dict[str, int]]:
    sessions_dir = codex_home / "sessions"
    stats = {
        "files_scanned": 0,
        "files_with_model_provider": 0,
        "json_lines_scanned": 0,
        "stale_provider_files": 0,
        "locked_stale_provider_files": 0,
    }
    if not sessions_dir.exists():
        return {}, None, stats
    distribution: dict[str, int] = {}
    errors: list[str] = []
    for path in sorted(sessions_dir.rglob("*.jsonl")):
        stats["files_scanned"] += 1
        file_has_provider = False
        file_has_stale_provider = False
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    if "model_provider" not in line:
                        continue
                    file_has_provider = True
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    stats["json_lines_scanned"] += 1
                    for provider in _json_model_provider_values(payload):
                        bucket = provider if provider else "<empty>"
                        distribution[bucket] = distribution.get(bucket, 0) + 1
                        if bucket != SHARED_CODEX_PROVIDER_ID:
                            file_has_stale_provider = True
        except OSError as exc:
            errors.append(f"{path}: {exc}")
        if file_has_provider:
            stats["files_with_model_provider"] += 1
        if file_has_stale_provider:
            stats["stale_provider_files"] += 1
            if _file_locked_for_exclusive_access(path):
                stats["locked_stale_provider_files"] += 1
    error = None
    if errors:
        error = "Cannot inspect some Codex session JSONL files: " + "; ".join(errors[:3])
    return dict(sorted(distribution.items(), key=lambda item: (-item[1], item[0]))), error, stats


def _json_model_provider_values(value: Any) -> list[str]:
    providers: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "model_provider" and isinstance(child, str):
                providers.append(child)
                continue
            providers.extend(_json_model_provider_values(child))
    elif isinstance(value, list):
        for child in value:
            providers.extend(_json_model_provider_values(child))
    return providers


def _file_locked_for_exclusive_access(path: Path) -> bool:
    if os.name != "nt":
        return False
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_file = kernel32.CreateFileW
    create_file.argtypes = [
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    ]
    create_file.restype = ctypes.c_void_p
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [ctypes.c_void_p]
    close_handle.restype = ctypes.c_int
    generic_read = 0x80000000
    generic_write = 0x40000000
    open_existing = 3
    invalid_handle_value = ctypes.c_void_p(-1).value
    handle = create_file(str(path), generic_read | generic_write, 0, None, open_existing, 0, None)
    if handle == invalid_handle_value:
        return True
    close_handle(handle)
    return False


def _sqlite_table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    try:
        return {str(row[1]) for row in connection.execute(f"pragma table_info({table_name})").fetchall()}
    except sqlite3.Error:
        return set()


def _dominant_provider(distribution: dict[str, int]) -> str | None:
    if not distribution:
        return None
    provider, count = max(distribution.items(), key=lambda item: item[1])
    return provider if count > 0 and provider != "<empty>" else None


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _toml_top_level_string(config: str, key: str) -> str | None:
    try:
        value = tomllib.loads(config or "").get(key)
    except (tomllib.TOMLDecodeError, TypeError):
        return None
    return value.strip() if isinstance(value, str) and value.strip() else None


def _model_provider_info(config: str, provider_id: str) -> dict[str, Any]:
    try:
        payload = tomllib.loads(config or "")
    except tomllib.TOMLDecodeError:
        return {}
    model_providers = payload.get("model_providers")
    if not isinstance(model_providers, dict):
        return {}
    info = model_providers.get(provider_id)
    return info if isinstance(info, dict) else {}


def _is_custom_provider_id(provider_id: str) -> bool:
    reserved = {"amazon-bedrock", "openai", "ollama", "lmstudio", "oss", "ollama-chat"}
    return bool(provider_id.strip()) and provider_id.strip().lower() not in reserved


def _set_top_level(lines: list[str], key: str, value: str) -> list[str]:
    replacement = f"{key} = {value}"
    result: list[str] = []
    inserted = False
    updated = False
    for line in lines:
        if line.strip().startswith("[") and not inserted and not updated:
            result.append(replacement)
            inserted = True
        if not inserted and not updated and line.strip().startswith(f"{key} ="):
            result.append(replacement)
            updated = True
            continue
        result.append(line)
    if not inserted and not updated:
        result.append(replacement)
    return result


def _cockpit_instance_isolation_findings(instances: Any, codex_home: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not isinstance(instances, dict):
        return findings
    candidates = []
    default_settings = instances.get("defaultSettings")
    if isinstance(default_settings, dict):
        candidates.append(("defaultSettings", default_settings))
    for index, instance in enumerate(instances.get("instances") or []):
        if isinstance(instance, dict):
            candidates.append((f"instances[{index}]", instance))

    expected_home = str(codex_home).lower()
    for label, item in candidates:
        text = " ".join(
            str(value)
            for key, value in item.items()
            if key.lower() in {"extraargs", "extra_args", "env", "codexhome", "codex_home", "config", "args"}
        )
        lowered = text.lower()
        if "disable_response_storage" in lowered:
            findings.append({"instance": label, "issue": "disable_response_storage"})
        if "codex_home" in lowered and expected_home not in lowered:
            findings.append({"instance": label, "issue": "different_codex_home", "expected": str(codex_home)})
        if "sqlite_home" in lowered and expected_home not in lowered:
            findings.append({"instance": label, "issue": "different_sqlite_home", "expected": str(codex_home)})
    return findings


def _cockpit_account_binding_findings(instances: Any) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not isinstance(instances, dict):
        return findings
    default_settings = instances.get("defaultSettings")
    if not isinstance(default_settings, dict):
        return findings
    follow_current = bool(default_settings.get("followLocalAccount"))
    bind_account_id = default_settings.get("bindAccountId")
    if not follow_current:
        findings.append({"setting": "defaultSettings.followLocalAccount", "issue": "not_following_current_account"})
    if isinstance(bind_account_id, str) and bind_account_id.strip():
        findings.append(
            {
                "setting": "defaultSettings.bindAccountId",
                "issue": "fixed_account_binding",
                "bindAccountId": bind_account_id,
            }
        )
    return findings


def _cockpit_stale_last_pid(instances: Any) -> int | None:
    last_pid = _cockpit_default_last_pid(instances)
    if last_pid is None:
        return None
    return None if _process_exists(last_pid) else last_pid


def _cockpit_default_last_pid(instances: Any) -> int | None:
    if not isinstance(instances, dict):
        return None
    default_settings = instances.get("defaultSettings")
    if not isinstance(default_settings, dict):
        return None
    raw = default_settings.get("lastPid")
    if isinstance(raw, int):
        return raw if raw > 0 else None
    if isinstance(raw, str) and raw.strip().isdigit():
        value = int(raw.strip())
        return value if value > 0 else None
    return None


def _process_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        return _windows_process_exists(pid)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _windows_process_exists(pid: int) -> bool:
    try:
        import ctypes
        from ctypes import wintypes
    except ImportError:
        return True

    process_query_limited_information = 0x1000
    handle = ctypes.windll.kernel32.OpenProcess(process_query_limited_information, False, wintypes.DWORD(pid))
    if not handle:
        return False
    ctypes.windll.kernel32.CloseHandle(handle)
    return True


def _read_json(path: Path) -> Any:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _json_semantically_equal(text: str, expected: dict[str, Any]) -> bool:
    try:
        current = json.loads(text or "{}")
    except json.JSONDecodeError:
        return False
    return current == expected


def _json_string(value: Any, key: str) -> str:
    if not isinstance(value, dict):
        return ""
    raw = value.get(key)
    return raw.strip() if isinstance(raw, str) else ""


def _cockpit_provider_for_base_url(cockpit_home: Path, base_url: str) -> dict[str, str]:
    providers = _read_json(cockpit_home / "codex_model_providers.json")
    if not isinstance(providers, list):
        return {}
    normalized = base_url.strip().rstrip("/")
    for provider in providers:
        if not isinstance(provider, dict):
            continue
        provider_base = str(provider.get("baseUrl") or provider.get("base_url") or "").strip().rstrip("/")
        if provider_base == normalized:
            return {
                "id": str(provider.get("id") or "").strip(),
                "name": str(provider.get("name") or "").strip(),
            }
    return {}


def _provider_name_from_base_url(base_url: str) -> str:
    without_scheme = re.sub(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", "", base_url.strip())
    host = without_scheme.split("/", 1)[0].strip()
    return host or "custom"


def _provider_id_from_base_url(base_url: str) -> str:
    name = _provider_name_from_base_url(base_url).lower()
    normalized = re.sub(r"[^a-z0-9_-]+", "_", name).strip("_-")
    if not normalized or not normalized[0].isalpha() or normalized == "openai":
        normalized = f"provider_{normalized or 'custom'}"
    return normalized


def _cockpit_current_account(cockpit_home: Path) -> dict[str, Any]:
    index = _read_json(cockpit_home / "codex_accounts.json")
    if not isinstance(index, dict):
        return {}
    account_id = index.get("current_account_id")
    if not isinstance(account_id, str) or not account_id.strip():
        return {}
    account = _read_json(cockpit_home / "codex_accounts" / f"{account_id}.json")
    return account if isinstance(account, dict) else {}


def _cockpit_account_base_url(account: dict[str, Any]) -> str:
    base_url = account.get("api_base_url")
    if isinstance(base_url, str) and base_url.strip():
        return base_url.strip().rstrip("/")
    if account.get("auth_mode") == "apikey":
        return ""
    return OFFICIAL_OPENAI_BASE_URL


def _list_len(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def _toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


if __name__ == "__main__":
    raise SystemExit(main())
