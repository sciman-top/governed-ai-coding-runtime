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


OPENAI_SHARED_PROVIDER_ID = "openai"
SHARED_CODEX_PROVIDER_ID = OPENAI_SHARED_PROVIDER_ID
OFFICIAL_OPENAI_BASE_URL = "https://api.openai.com/v1"
CODEX_BUILTIN_PROVIDER_IDS = {"openai", "ollama", "lmstudio"}
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
CODEX_TUI_LOG_ROTATE_BYTES = 100 * 1024 * 1024
DEPRECATED_WRITE_REPAIR_REASON = (
    "Project-managed Codex/Cockpit interop repair is disabled. Cockpit Tools owns "
    "Codex auth/API switching and launch-on-switch; this script is read-only "
    "diagnostics only. Use Disable-CodexProjectInterop.ps1 for reversible cleanup "
    "of old project guard/wrapper artifacts."
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Codex Cockpit Tools provider/auth interop.")
    parser.add_argument("--codex-home", required=True)
    parser.add_argument("--cc-switch-db", required=True)
    parser.add_argument("--cockpit-home", required=True)
    parser.add_argument("--cockpit-account-id")
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
        cockpit_account_id=args.cockpit_account_id,
        include_session_scan=not args.quick_launch,
    )
    actions: list[dict[str, Any]] = []
    if args.apply:
        actions.append(
            {
                "id": "codex_interop_write_repair_deprecated",
                "tool": "codex",
                "status": "blocked",
                "reason": DEPRECATED_WRITE_REPAIR_REASON,
            }
        )
        if args.migrate_provider_bucket:
            actions.append(
                {
                    "id": "codex_provider_bucket_migration_deprecated",
                    "tool": "codex",
                    "status": "blocked",
                    "reason": "Provider bucket migration is disabled because API connectivity is primary and history sharing is secondary.",
                }
            )
    after = inspect_interop(
        codex_home=codex_home,
        cc_switch_db=cc_switch_db,
        cockpit_home=cockpit_home,
        cockpit_account_id=args.cockpit_account_id,
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
    return 2 if args.apply or after["status"] == "fail" else 0


def inspect_interop(
    *,
    codex_home: Path,
    cc_switch_db: Path,
    cockpit_home: Path,
    cockpit_account_id: str | None = None,
    include_session_scan: bool = True,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    provider_state = inspect_codex_provider_buckets(
        codex_home=codex_home,
        cockpit_home=cockpit_home,
        cockpit_account_id=cockpit_account_id,
        include_session_scan=include_session_scan,
    )
    checks.extend(provider_state["checks"])
    checks.extend(inspect_cc_switch(codex_home=codex_home, db_path=cc_switch_db))
    checks.extend(
        inspect_cockpit(
            codex_home=codex_home,
            cockpit_home=cockpit_home,
            cockpit_account_id=cockpit_account_id,
        )
    )
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
    cockpit_account_id: str | None = None,
    include_session_scan: bool = True,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    state_path = codex_home / "state_5.sqlite"
    config_path = codex_home / "config.toml"
    current_account = _cockpit_account(cockpit_home, account_id=cockpit_account_id)
    history_secondary = _cockpit_account_is_api(current_account)
    expected_provider = _expected_cockpit_provider_bucket(cockpit_home, account_id=cockpit_account_id)
    distribution, distribution_error = _read_codex_thread_provider_distribution(state_path)
    dominant_provider = _dominant_provider(distribution)
    unexpected_providers = {
        provider: count
        for provider, count in distribution.items()
        if provider != expected_provider and int(count) > 0
    }

    thread_status = "pass"
    if distribution_error:
        thread_status = "fail"
    elif unexpected_providers:
        thread_status = "warn" if history_secondary else "fail"
    checks.append(
        {
            "id": "codex_thread_provider_distribution",
            "tool": "codex",
            "status": thread_status,
            "reason": distribution_error
            or (
                "Active Codex threads use a different provider bucket than the current account. API connectivity is primary; run migration only when history sharing is explicitly desired."
                if unexpected_providers and history_secondary
                else "Active Codex threads use a different provider bucket than the current ChatGPT account; migrate or switch provider before relying on shared history."
                if unexpected_providers
                else "Codex local history visibility is bucketed by threads.model_provider; active threads match the expected provider bucket."
            ),
            "path": str(state_path),
            "distribution": distribution,
            "dominant_provider": dominant_provider,
            "expected_provider": expected_provider,
            "unexpected_providers": unexpected_providers,
        }
    )
    if include_session_scan:
        checks.append(
            _inspect_codex_session_provider_bucket(
                codex_home,
                expected_provider=expected_provider,
                history_secondary=history_secondary,
            )
        )
    else:
        checks.append(
            {
                "id": "codex_session_provider_distribution",
                "tool": "codex",
                "status": "pass",
                "reason": "Quick launch skipped full session JSONL scan. Project-managed SQLite trigger guards are disabled because API connectivity is primary and history sharing is secondary.",
                "path": str(codex_home / "sessions"),
                "session_scan_skipped": True,
                "expected_provider": expected_provider,
            }
        )

    config_text = _read_text(config_path)
    checks.append(_inspect_builtin_provider_overrides(config_text=config_text, config_path=config_path))
    active_provider = _toml_top_level_string(config_text, "model_provider") or "openai"
    active_status = "pass"
    active_reason = "Codex live config uses the same provider bucket as the dominant local history bucket."
    if dominant_provider and active_provider != dominant_provider:
        active_status = "warn" if _is_custom_provider_id(expected_provider) else ("fail" if _is_custom_provider_id(active_provider) else "warn")
        active_reason = "Codex live config points at a different provider bucket than the dominant local history bucket."
    if active_provider != expected_provider:
        active_status = "fail" if _is_custom_provider_id(expected_provider) else active_status
        active_reason = "Codex live config does not match the provider bucket required by the current Cockpit account."
    checks.append(
        {
            "id": "codex_live_provider_bucket",
            "tool": "codex",
            "status": active_status,
            "reason": active_reason,
            "path": str(config_path),
            "active_provider": active_provider,
            "dominant_provider": dominant_provider,
            "expected_provider": expected_provider,
        }
    )

    checks.extend(
        _inspect_cockpit_current_provider_bucket(
            cockpit_home,
            dominant_provider,
            config_text,
            active_provider,
            account_id=cockpit_account_id,
        )
    )
    return {"checks": checks, "distribution": distribution, "dominant_provider": dominant_provider}


def _inspect_cockpit_current_provider_bucket(
    cockpit_home: Path,
    dominant_provider: str | None,
    config_text: str,
    active_provider: str,
    account_id: str | None = None,
) -> list[dict[str, Any]]:
    current = _cockpit_account(cockpit_home, account_id=account_id)
    if not current:
        return []
    provider_bucket = _provider_bucket_for_cockpit_account(current)
    auth_mode = str(current.get("auth_mode") or "")
    codex_login_mode = _codex_login_mode_for_cockpit_auth(auth_mode)
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
    bucket_reason = "Current Cockpit Codex account will use the provider bucket required for its auth mode."
    if dominant_provider and dominant_provider != provider_bucket:
        bucket_status = "warn" if auth_mode == "apikey" else "fail"
        bucket_reason = (
            "Existing Codex history is in a different bucket. API provider connectivity is primary; history sharing is secondary for API accounts."
            if auth_mode == "apikey"
            else "Existing Codex history is still in a different provider bucket and should be migrated."
        )
    expected_forced_login = codex_login_mode or "chatgpt"
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
            "expected_provider": provider_bucket,
            "repair_strategy": "current_account_provider_bucket" if bucket_status == "fail" else "none",
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


def inspect_cockpit(
    *,
    codex_home: Path,
    cockpit_home: Path,
    cockpit_account_id: str | None = None,
) -> list[dict[str, Any]]:
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
    config_text = _read_text(codex_home / "config.toml")
    accounts = _read_json(accounts_path)
    providers = _read_json(providers_path)
    instances = _read_json(instances_path)
    cockpit_config = _read_json(cockpit_home / "config.json")
    current = _cockpit_account(cockpit_home, account_id=cockpit_account_id)

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
            "inspected_account_id": current.get("id") if current else None,
            "auth_mode": current.get("auth_mode") if current else None,
            "api_provider_id": current.get("api_provider_id") if current else None,
        }
    )
    checks.append(_inspect_codex_auth_projection(codex_home=codex_home, account=current))
    checks.append(_inspect_cockpit_saved_api_provider_profiles(cockpit_home=cockpit_home, config_text=config_text))
    codex_app_path = str(cockpit_config.get("codex_app_path") or "") if isinstance(cockpit_config, dict) else ""
    restart_on_switch = bool(cockpit_config.get("codex_restart_specified_app_on_switch")) if isinstance(cockpit_config, dict) else False
    specified_app_path = (
        str(cockpit_config.get("codex_specified_app_path") or "") if isinstance(cockpit_config, dict) else ""
    )
    expected_restart_wrapper = str(_expected_cockpit_restart_wrapper(codex_home))
    managed_restart_enabled = restart_on_switch and _same_path(specified_app_path, expected_restart_wrapper)
    noop_launcher_configured = "codex-cockpit-noop-launcher" in codex_app_path.lower()
    checks.append(
        {
            "id": "cockpit_codex_app_restart_semantics",
            "tool": "cockpit_tools",
            "status": "fail" if managed_restart_enabled or noop_launcher_configured else "pass",
            "reason": (
                "Cockpit Tools should use its native Codex App launch path on account/provider switch; project-managed restart wrappers and no-op launchers break the normal Cockpit repair/startup flow."
            ),
            "path": str(cockpit_home / "config.json"),
            "codex_app_path": codex_app_path,
            "codex_restart_specified_app_on_switch": restart_on_switch,
            "codex_specified_app_path": specified_app_path,
            "expected_restart_wrapper": expected_restart_wrapper,
            "managed_restart_enabled": managed_restart_enabled,
            "noop_launcher_configured": noop_launcher_configured,
            "repair_strategy": "restore_native_cockpit_launch" if managed_restart_enabled or noop_launcher_configured else "none",
        }
    )
    raw_launch_on_switch = bool(cockpit_config.get("codex_launch_on_switch")) if isinstance(cockpit_config, dict) else False
    checks.append(
        {
            "id": "cockpit_codex_native_launch_on_switch_enabled",
            "tool": "cockpit_tools",
            "status": "pass",
            "reason": (
                "Cockpit Tools native launch-on-switch is user-controlled. Project code must not force this setting on or off."
            ),
            "path": str(cockpit_home / "config.json"),
            "codex_launch_on_switch": raw_launch_on_switch,
            "repair_strategy": "none",
        }
    )
    dual_switch_no_restart = (
        bool(cockpit_config.get("antigravity_dual_switch_no_restart_enabled"))
        if isinstance(cockpit_config, dict)
        else False
    )
    checks.append(
        {
            "id": "cockpit_codex_dual_switch_no_restart_enabled",
            "tool": "cockpit_tools",
            "status": "fail" if dual_switch_no_restart else "pass",
            "reason": (
                "Cockpit Tools native Codex launch/recovery semantics should not be replaced by the project no-restart shim; API connectivity depends on the normal Cockpit startup path plus provider-first projection."
            ),
            "path": str(cockpit_home / "config.json"),
            "antigravity_dual_switch_no_restart_enabled": dual_switch_no_restart,
            "repair_strategy": "restore_native_cockpit_launch" if dual_switch_no_restart else "none",
        }
    )
    recent_raw_start = _cockpit_recent_codex_start_after_switch(cockpit_home)
    checks.append(
        {
            "id": "cockpit_codex_recent_native_start_after_switch_observed",
            "tool": "cockpit_tools",
            "status": "pass",
            "reason": (
                "Cockpit Tools may natively start Codex App after account switch; project code must repair provider/auth projection without replacing that launch path."
            ),
            "path": str(cockpit_home / "logs"),
            **recent_raw_start,
        }
    )
    recent_ag_close = _cockpit_recent_codex_log_event_after_switch(
        cockpit_home,
        patterns=("[AG Close] taskkill",),
    )
    checks.append(
        {
            "id": "cockpit_codex_recent_taskkill_after_switch_absent",
            "tool": "cockpit_tools",
            "status": "fail" if recent_ag_close.get("detected") else "pass",
            "reason": (
                "Cockpit Tools logs must not show AG Close/taskkill after a Codex account switch; "
                "that kills the app-server process group and causes Reconnecting or empty history in the UI."
            ),
            "path": str(cockpit_home / "logs"),
            **recent_ag_close,
        }
    )
    recent_cli_failure = _cockpit_recent_codex_log_event_after_switch(
        cockpit_home,
        patterns=("当前系统暂不支持生成 Codex CLI 启动命令",),
    )
    checks.append(
        {
            "id": "cockpit_codex_recent_cli_launch_failure_after_switch_absent",
            "tool": "cockpit_tools",
            "status": "fail" if recent_cli_failure.get("detected") else "pass",
            "reason": (
                "Cockpit Tools launchMode=cli is not a safe Windows workaround here; "
                "the switch path enters CodexWakeup CLI and then fails before the App can recover."
            ),
            "path": str(cockpit_home / "logs"),
            **recent_cli_failure,
        }
    )

    isolation_findings = _cockpit_instance_isolation_findings(instances, codex_home)
    account_binding_findings = _cockpit_account_binding_findings(instances)
    cli_launch_mode_findings = _cockpit_cli_launch_mode_findings(instances)
    stale_last_pid = _cockpit_stale_last_pid(instances)
    last_pid = _cockpit_default_last_pid(instances)
    last_pid_status = "fail" if last_pid is not None else "pass"
    checks.append(
        {
            "id": "cockpit_codex_instances_share_state",
            "tool": "cockpit_tools",
            "status": "fail" if isolation_findings else "pass",
            "reason": "Cockpit Codex instances must not force a different CODEX_HOME/sqlite_home/log_dir unless account isolation is intentional.",
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
            "id": "cockpit_codex_default_cli_launch_mode_absent",
            "tool": "cockpit_tools",
            "status": "fail" if cli_launch_mode_findings else "pass",
            "reason": (
                "Cockpit Codex default launchMode=cli is unsupported on this Windows host; "
                "use app launch mode only with no-restart switch semantics enabled."
            ),
            "path": str(instances_path),
            "findings": cli_launch_mode_findings,
            "repair_strategy": "switch_default_launch_mode_to_app" if cli_launch_mode_findings else "none",
        }
    )
    checks.append(
        {
            "id": "cockpit_codex_instances_last_pid_current",
            "tool": "cockpit_tools",
            "status": last_pid_status,
            "reason": (
                "Cockpit Tools persists the last Codex App PID and later uses it for AG Close/taskkill; "
                "provider/auth switching must not leave any Codex App PID under Cockpit ownership."
            ),
            "path": str(instances_path),
            "lastPid": last_pid,
            "stale_lastPid": stale_last_pid,
            "repair_strategy": "clear_lastPid" if last_pid is not None else "none",
        }
    )
    return checks


def _cockpit_recent_codex_start_after_switch(cockpit_home: Path) -> dict[str, Any]:
    return _cockpit_recent_codex_log_event_after_switch(
        cockpit_home,
        patterns=("[Codex Start] 启动策略=",),
        event_key="last_start_after_switch",
    )


def _cockpit_recent_codex_log_event_after_switch(
    cockpit_home: Path,
    *,
    patterns: tuple[str, ...],
    event_key: str = "last_event_after_switch",
) -> dict[str, Any]:
    log_dir = cockpit_home / "logs"
    if not log_dir.exists():
        return {"detected": False, "reason": "logs directory missing"}
    switch_event: dict[str, Any] | None = None
    matched_event: dict[str, Any] | None = None
    for log_path in sorted(log_dir.glob("app.log*"), key=lambda path: path.stat().st_mtime if path.exists() else 0)[-4:]:
        try:
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines[-3000:]:
            timestamp = _parse_log_timestamp(line)
            timestamp_text = timestamp.isoformat() if timestamp else None
            if "[Codex切号] 开始切换账号" in line:
                switch_event = {"timestamp": timestamp_text, "line": line, "path": str(log_path)}
                matched_event = None
            elif switch_event and any(pattern in line for pattern in patterns):
                matched_event = {"timestamp": timestamp_text, "line": line, "path": str(log_path)}
    if not switch_event or not matched_event:
        return {
            "detected": False,
            "last_switch": switch_event,
            event_key: matched_event,
        }
    delta_seconds = None
    switch_timestamp = _parse_log_timestamp(str(switch_event.get("line") or ""))
    matched_timestamp = _parse_log_timestamp(str(matched_event.get("line") or ""))
    if switch_timestamp and matched_timestamp:
        delta_seconds = (matched_timestamp - switch_timestamp).total_seconds()
    state_mtime = _latest_existing_mtime(
        [
            cockpit_home / "config.json",
            cockpit_home / "codex_instances.json",
            cockpit_home / "codex_accounts.json",
        ]
    )
    matched_epoch = matched_timestamp.timestamp() if matched_timestamp else None
    superseded_by_state_write = bool(matched_epoch and state_mtime and state_mtime > matched_epoch + 5)
    detected = delta_seconds is None or 0 <= delta_seconds <= 120
    return {
        "detected": detected,
        "seconds_after_switch": delta_seconds,
        "superseded_by_state_write": superseded_by_state_write,
        "last_switch": switch_event,
        event_key: matched_event,
    }


def _latest_existing_mtime(paths: list[Path]) -> float | None:
    mtimes: list[float] = []
    for path in paths:
        try:
            mtimes.append(path.stat().st_mtime)
        except FileNotFoundError:
            pass
    return max(mtimes) if mtimes else None


def _parse_log_timestamp(line: str) -> datetime | None:
    match = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d+))?([+-]\d{2}:\d{2}|Z)", line)
    if not match:
        return None
    fraction = (match.group(2) or "")[:6].ljust(6, "0")
    suffix = "+00:00" if match.group(3) == "Z" else match.group(3)
    try:
        return datetime.fromisoformat(f"{match.group(1)}.{fraction}{suffix}")
    except ValueError:
        return None


def _inspect_codex_auth_projection(*, codex_home: Path, account: dict[str, Any]) -> dict[str, Any]:
    auth_path = codex_home / "auth.json"
    auth = _read_json(auth_path)
    auth_mode = str(account.get("auth_mode") or "").strip() if isinstance(account, dict) else ""
    expected_codex_auth_mode = _codex_auth_mode_for_cockpit_auth(auth_mode)
    if not account:
        return {
            "id": "codex_auth_matches_cockpit_current_account",
            "tool": "codex",
            "status": "fail",
            "reason": "Codex auth projection cannot be checked because Cockpit has no current Codex account.",
            "path": str(auth_path),
            "expected_auth_mode": None,
            "actual_auth_mode": _json_string(auth, "auth_mode") if isinstance(auth, dict) else "",
            "key_present": bool(_json_string(auth, "OPENAI_API_KEY")) if isinstance(auth, dict) else False,
            "issues": ["missing_cockpit_current_account"],
            "repair_strategy": "select_cockpit_account",
        }
    issues: list[str] = []
    actual_auth_mode = _codex_auth_mode_from_auth_json(auth)
    key_present = bool(_json_string(auth, "OPENAI_API_KEY")) if isinstance(auth, dict) else False
    actual_base_url = (
        _json_string(auth, "api_base_url")
        or _json_string(auth, "base_url")
        if isinstance(auth, dict)
        else ""
    )
    expected_base_url = _cockpit_account_base_url(account)
    if auth_mode == "apikey":
        if actual_auth_mode != "apikey":
            issues.append(f"auth_mode is {actual_auth_mode or '<missing>'}, expected apikey")
        if not key_present:
            issues.append("OPENAI_API_KEY is missing from auth.json")
        account_key = str(account.get("openai_api_key") or "").strip()
        if key_present and account_key and _json_string(auth, "OPENAI_API_KEY") != account_key:
            issues.append("OPENAI_API_KEY does not match current Cockpit API account")
        if expected_base_url and actual_base_url.rstrip("/") != expected_base_url.rstrip("/"):
            issues.append("auth.json API base URL does not match current Cockpit API account")
    elif expected_codex_auth_mode == "chatgpt":
        if actual_auth_mode != "chatgpt":
            issues.append(f"auth_mode is {actual_auth_mode or '<missing>'}, expected chatgpt")
        tokens = auth.get("tokens") if isinstance(auth, dict) else None
        if not isinstance(tokens, dict) or not tokens.get("access_token"):
            issues.append("ChatGPT tokens are missing from auth.json")
    else:
        issues.append(f"unsupported Cockpit auth_mode: {auth_mode or '<missing>'}")

    return {
        "id": "codex_auth_matches_cockpit_current_account",
        "tool": "codex",
        "status": "fail" if issues else "pass",
        "reason": "Codex auth.json must match the current Cockpit Codex account before Codex CLI/App startup; config-only API switching can otherwise reuse stale ChatGPT tokens or fail auth.",
        "path": str(auth_path),
        "cockpit_auth_mode": auth_mode,
        "expected_auth_mode": expected_codex_auth_mode or auth_mode,
        "actual_auth_mode": actual_auth_mode,
        "expected_base_url": expected_base_url if auth_mode == "apikey" else None,
        "actual_base_url": actual_base_url if auth_mode == "apikey" else None,
        "key_present": key_present,
        "issues": issues,
        "repair_strategy": "project_cockpit_auth" if issues and expected_codex_auth_mode in {"apikey", "chatgpt"} else "none",
    }


def _codex_auth_mode_from_auth_json(auth: Any) -> str:
    if not isinstance(auth, dict):
        return ""
    explicit = _json_string(auth, "auth_mode")
    if explicit:
        return explicit
    if _json_string(auth, "OPENAI_API_KEY"):
        return "apikey"
    tokens = auth.get("tokens")
    if isinstance(tokens, dict) and tokens.get("access_token"):
        return "chatgpt"
    return ""


def repair_cockpit(
    *,
    codex_home: Path,
    cockpit_home: Path,
    checks: dict[str, Any],
    cockpit_account_id: str | None = None,
) -> list[dict[str, Any]]:
    return [
        {
            "id": "codex_interop_write_repair_deprecated",
            "tool": "codex",
            "status": "blocked",
            "reason": DEPRECATED_WRITE_REPAIR_REASON,
        }
    ]


def _expected_cockpit_provider_bucket(cockpit_home: Path, *, account_id: str | None = None) -> str:
    current = _cockpit_account(cockpit_home, account_id=account_id)
    return _provider_bucket_for_cockpit_account(current)


def _provider_bucket_for_cockpit_account(account: dict[str, Any] | None) -> str:
    if _cockpit_account_is_api(account):
        explicit = str(account.get("api_provider_id") or "").strip()
        if explicit and explicit.lower() not in CODEX_BUILTIN_PROVIDER_IDS:
            return explicit
        base_url = _cockpit_account_base_url(account)
        if base_url:
            return _provider_id_from_base_url(base_url)
    return OPENAI_SHARED_PROVIDER_ID


def _cockpit_account_is_api(account: dict[str, Any] | None) -> bool:
    return bool(account and str(account.get("auth_mode") or "").strip().lower() == "apikey")


def _codex_login_mode_for_cockpit_auth(auth_mode: str) -> str | None:
    auth_mode = str(auth_mode or "").strip().lower()
    if auth_mode == "apikey":
        return "api"
    if auth_mode in {"chatgpt", "oauth"}:
        return "chatgpt"
    return None


def _codex_auth_mode_for_cockpit_auth(auth_mode: str) -> str | None:
    auth_mode = str(auth_mode or "").strip().lower()
    if auth_mode == "apikey":
        return "apikey"
    if auth_mode in {"chatgpt", "oauth"}:
        return "chatgpt"
    return None


def _cockpit_api_provider_profiles(cockpit_home: Path, *, preferred_account: dict[str, Any] | None = None) -> list[dict[str, str]]:
    profiles: list[dict[str, str]] = []
    seen: set[str] = set()

    def add_from_account(account: dict[str, Any] | None) -> None:
        if not isinstance(account, dict):
            return
        if not _cockpit_account_is_api(account):
            return
        base_url = _cockpit_account_base_url(account)
        if not base_url:
            return
        provider_id = _provider_bucket_for_cockpit_account(account)
        if not provider_id or provider_id == OPENAI_SHARED_PROVIDER_ID or provider_id in seen:
            return
        provider_name = str(account.get("api_provider_name") or "").strip() or _provider_name_from_base_url(base_url)
        profiles.append({"provider_id": provider_id, "provider_name": provider_name, "base_url": base_url})
        seen.add(provider_id)

    add_from_account(preferred_account)
    index = _read_json(cockpit_home / "codex_accounts.json")
    accounts = index.get("accounts") if isinstance(index, dict) else []
    if isinstance(accounts, list):
        for item in accounts:
            account_id = item.get("id") if isinstance(item, dict) else None
            if not isinstance(account_id, str) or not account_id.strip():
                continue
            add_from_account(_read_json(cockpit_home / "codex_accounts" / f"{account_id}.json"))

    providers = _read_json(cockpit_home / "codex_model_providers.json")
    if isinstance(providers, list):
        for provider in providers:
            if not isinstance(provider, dict):
                continue
            provider_id = str(provider.get("id") or "").strip()
            base_url = _normalize_base_url(str(provider.get("baseUrl") or provider.get("base_url") or ""))
            if (
                not provider_id
                or provider_id == OPENAI_SHARED_PROVIDER_ID
                or provider_id in CODEX_BUILTIN_PROVIDER_IDS
                or provider_id in seen
                or not base_url
            ):
                continue
            provider_name = str(provider.get("name") or "").strip() or _provider_name_from_base_url(base_url)
            profiles.append({"provider_id": provider_id, "provider_name": provider_name, "base_url": base_url})
            seen.add(provider_id)
    return profiles


def _inspect_cockpit_saved_api_provider_profiles(*, cockpit_home: Path, config_text: str) -> dict[str, Any]:
    profiles = _cockpit_api_provider_profiles(cockpit_home)
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for profile in profiles:
        provider_id = profile["provider_id"]
        expected_base_url = _normalize_base_url(profile["base_url"])
        info = _model_provider_info(config_text, provider_id)
        issues: list[str] = []
        actual_base_url = _normalize_base_url(str(info.get("base_url") or "")) if info else ""
        if not info:
            issues.append("provider table missing")
        elif actual_base_url != expected_base_url:
            issues.append(f"base_url is {actual_base_url or '<empty>'}, expected {expected_base_url}")
        if info and info.get("wire_api") != "responses":
            issues.append(f"wire_api is {info.get('wire_api')!r}, expected 'responses'")
        if info and info.get("requires_openai_auth") is not False:
            issues.append("requires_openai_auth must be false for Cockpit API providers")
        if info and info.get("supports_websockets") is not False:
            issues.append("supports_websockets must be false for Cockpit API relays")
        if issues:
            findings.append(
                {
                    "provider_id": provider_id,
                    "provider_name": profile["provider_name"],
                    "expected_base_url": expected_base_url,
                    "actual_base_url": actual_base_url or None,
                    "requires_openai_auth": info.get("requires_openai_auth") if info else None,
                    "supports_websockets": info.get("supports_websockets") if info else None,
                    "issues": issues,
                }
            )

    shared_api_profile = _profile_info(config_text, "shared-cockpit-api")
    preferred = profiles[0] if profiles else None
    shared_api_issues: list[str] = []
    if preferred:
        if not shared_api_profile:
            shared_api_issues.append("profiles.shared-cockpit-api missing")
        elif shared_api_profile.get("forced_login_method") != "api":
            shared_api_issues.append(
                f"forced_login_method is {shared_api_profile.get('forced_login_method')!r}, expected 'api'"
            )
        if shared_api_profile and shared_api_profile.get("model_provider") != preferred["provider_id"]:
            shared_api_issues.append(
                f"model_provider is {shared_api_profile.get('model_provider')!r}, expected {preferred['provider_id']!r}"
            )
        if (
            shared_api_profile
            and shared_api_profile.get("model_provider") != OPENAI_SHARED_PROVIDER_ID
            and shared_api_profile.get("openai_base_url")
        ):
            shared_api_issues.append("openai_base_url must not be used with a custom Cockpit API provider bucket")
    if shared_api_issues:
        warnings.append(
            {
                "provider_id": preferred["provider_id"] if preferred else None,
                "profile": "shared-cockpit-api",
                "expected_model_provider": preferred["provider_id"] if preferred else None,
                "actual_model_provider": shared_api_profile.get("model_provider") if shared_api_profile else None,
                "issues": shared_api_issues,
            }
        )

    return {
        "id": "cockpit_saved_api_provider_profiles_projectable",
        "tool": "cockpit_tools",
        "status": "fail" if findings else "pass",
        "reason": (
            "Saved Cockpit API providers must stay projected as custom provider buckets even when the current account is OAuth; API provider connectivity is primary and history sharing is secondary."
        ),
        "path": str(cockpit_home / "codex_accounts.json"),
        "profile_count": len(profiles),
        "provider_ids": [profile["provider_id"] for profile in profiles],
        "findings": findings,
        "warnings": warnings,
        "repair_strategy": "normalize_saved_api_provider_profiles" if findings else "none",
    }


def migrate_codex_provider_bucket(
    *,
    codex_home: Path,
    target_provider: str,
    migrate_sessions: bool = True,
) -> list[dict[str, Any]]:
    return [
        {
            "id": "codex_provider_bucket_migration_deprecated",
            "tool": "codex",
            "status": "blocked",
            "path": str(codex_home / "state_5.sqlite"),
            "target_provider": target_provider,
            "migrate_sessions": bool(migrate_sessions),
            "reason": "Provider bucket migration is disabled because API connectivity is primary and history sharing is secondary.",
        }
    ]


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


def ensure_codex_provider_bucket_triggers(*, codex_home: Path, target_provider: str = SHARED_CODEX_PROVIDER_ID) -> list[dict[str, Any]]:
    return [
        {
            "id": "codex_provider_bucket_triggers_deprecated",
            "tool": "codex",
            "status": "blocked",
            "path": str(codex_home / "state_5.sqlite"),
            "target_provider": target_provider,
            "reason": "Provider bucket triggers are disabled; project code must not rewrite Codex thread provider buckets.",
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


def _inspect_codex_session_provider_bucket(
    codex_home: Path,
    *,
    expected_provider: str = SHARED_CODEX_PROVIDER_ID,
    history_secondary: bool = False,
) -> dict[str, Any]:
    session_distribution, session_error, session_stats = _read_codex_session_provider_distribution(codex_home)
    unexpected_session_providers = {
        provider: count
        for provider, count in session_distribution.items()
        if provider != expected_provider and int(count) > 0
    }
    session_unexpected_status = "pass"
    if session_error:
        session_unexpected_status = "fail"
    elif unexpected_session_providers:
        if history_secondary:
            session_unexpected_status = "warn"
        elif (
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
            "Codex session JSONL metadata uses a different provider bucket. API provider connectivity is primary; migrate sessions only when history sharing is explicitly desired."
            if session_unexpected_status == "warn" and history_secondary and unexpected_session_providers
            else
            "Codex session JSONL metadata still contains non-shared provider buckets, but the remaining stale files are locked by a live Codex process; repair will retry on the next launch."
            if session_unexpected_status == "warn"
            else "Codex session JSONL metadata still contains non-shared provider buckets and can repopulate state_5.sqlite during resume."
            if unexpected_session_providers
            else "Codex session JSONL metadata uses the expected provider bucket."
        ),
        "path": str(codex_home / "sessions"),
        "distribution": session_distribution,
        "expected_provider": expected_provider,
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


def _profile_info(config: str, profile_id: str) -> dict[str, Any]:
    try:
        payload = tomllib.loads(config or "")
    except tomllib.TOMLDecodeError:
        return {}
    profiles = payload.get("profiles")
    if not isinstance(profiles, dict):
        return {}
    info = profiles.get(profile_id)
    return info if isinstance(info, dict) else {}


def _is_custom_provider_id(provider_id: str) -> bool:
    reserved = {"amazon-bedrock", *CODEX_BUILTIN_PROVIDER_IDS, "oss", "ollama-chat"}
    return bool(provider_id.strip()) and provider_id.strip().lower() not in reserved


def _inspect_builtin_provider_overrides(*, config_text: str, config_path: Path) -> dict[str, Any]:
    configured_ids, parse_error = _configured_model_provider_ids(config_text)
    builtin_overrides = sorted(provider for provider in configured_ids if provider.lower() in CODEX_BUILTIN_PROVIDER_IDS)
    return {
        "id": "codex_builtin_provider_overrides_absent",
        "tool": "codex",
        "status": "fail" if builtin_overrides or parse_error else "pass",
        "reason": (
            f"Codex built-in provider IDs cannot be overridden in config.toml: {', '.join(builtin_overrides)}"
            if builtin_overrides
            else (
                f"Cannot parse config.toml while checking built-in provider overrides: {parse_error}"
                if parse_error
                else "Codex config does not override built-in provider IDs; relay routing must use openai_base_url or a non-built-in custom provider."
            )
        ),
        "path": str(config_path),
        "builtin_provider_ids": sorted(CODEX_BUILTIN_PROVIDER_IDS),
        "configured_builtin_overrides": builtin_overrides,
    }


def _configured_model_provider_ids(config_text: str) -> tuple[set[str], str | None]:
    configured: set[str] = set()
    parse_error: str | None = None
    try:
        payload = tomllib.loads(config_text or "")
        model_providers = payload.get("model_providers")
        if isinstance(model_providers, dict):
            configured.update(str(provider_id) for provider_id in model_providers)
    except tomllib.TOMLDecodeError as exc:
        parse_error = str(exc)

    table_pattern = re.compile(r'^\s*\[model_providers\.(?:"([^"]+)"|([A-Za-z0-9_-]+))\]\s*$')
    for line in (config_text or "").splitlines():
        match = table_pattern.match(line)
        if match:
            configured.add(match.group(1) or match.group(2) or "")
    return {provider for provider in configured if provider}, parse_error


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


def _cockpit_cli_launch_mode_findings(instances: Any) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not isinstance(instances, dict):
        return findings
    default_settings = instances.get("defaultSettings")
    if not isinstance(default_settings, dict):
        return findings
    launch_mode = str(default_settings.get("launchMode") or "").strip().lower()
    if launch_mode == "cli":
        findings.append(
            {
                "setting": "defaultSettings.launchMode",
                "issue": "cli_launch_mode_unsupported_on_windows",
                "launchMode": default_settings.get("launchMode"),
                "expected": "app",
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


def _json_string(value: Any, key: str) -> str:
    if not isinstance(value, dict):
        return ""
    raw = value.get(key)
    return raw.strip() if isinstance(raw, str) else ""


def _normalize_base_url(base_url: str) -> str:
    return str(base_url or "").strip().rstrip("/")


def _cockpit_provider_for_base_url(cockpit_home: Path, base_url: str) -> dict[str, str]:
    providers = _read_json(cockpit_home / "codex_model_providers.json")
    if not isinstance(providers, list):
        return {}
    normalized = _normalize_base_url(base_url)
    for provider in providers:
        if not isinstance(provider, dict):
            continue
        provider_base = _normalize_base_url(str(provider.get("baseUrl") or provider.get("base_url") or ""))
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
    return _cockpit_account(cockpit_home, account_id=None)


def _cockpit_account(cockpit_home: Path, *, account_id: str | None = None) -> dict[str, Any]:
    index = _read_json(cockpit_home / "codex_accounts.json")
    if not isinstance(index, dict):
        return {}
    resolved_account_id = account_id or index.get("current_account_id")
    if not isinstance(resolved_account_id, str) or not resolved_account_id.strip():
        return {}
    account = _read_json(cockpit_home / "codex_accounts" / f"{resolved_account_id}.json")
    return account if isinstance(account, dict) else {}


def _cockpit_account_base_url(account: dict[str, Any]) -> str:
    for key in ("api_base_url", "base_url", "baseUrl", "apiBaseUrl", "OPENAI_BASE_URL"):
        base_url = account.get(key)
        if isinstance(base_url, str) and base_url.strip():
            return base_url.strip().rstrip("/")
    if account.get("auth_mode") == "apikey":
        return ""
    return OFFICIAL_OPENAI_BASE_URL


def _list_len(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


if __name__ == "__main__":
    raise SystemExit(main())
