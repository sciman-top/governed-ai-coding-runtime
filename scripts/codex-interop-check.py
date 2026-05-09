from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any


SHARED_HISTORY_KEYS = {
    "history_persistence": 'persistence = "save-all"',
    "history_max_bytes": "max_bytes = 104857600",
}
SHARED_RELAY_PROVIDER_ID = "ccswitch"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Codex third-party switcher shared-history interop.")
    parser.add_argument("--codex-home", required=True)
    parser.add_argument("--cc-switch-db", required=True)
    parser.add_argument("--cockpit-home", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--migrate-provider-bucket", action="store_true")
    args = parser.parse_args()

    codex_home = Path(args.codex_home).expanduser().resolve()
    cc_switch_db = Path(args.cc_switch_db).expanduser()
    cockpit_home = Path(args.cockpit_home).expanduser()

    before = inspect_interop(codex_home=codex_home, cc_switch_db=cc_switch_db, cockpit_home=cockpit_home)
    actions: list[dict[str, Any]] = []
    if args.apply:
        actions.extend(repair_cc_switch(codex_home=codex_home, db_path=cc_switch_db, checks=before))
        if args.migrate_provider_bucket:
            actions.extend(
                migrate_codex_provider_bucket(codex_home=codex_home, target_provider=SHARED_RELAY_PROVIDER_ID)
            )
    after = inspect_interop(codex_home=codex_home, cc_switch_db=cc_switch_db, cockpit_home=cockpit_home)

    payload = {
        "status": after["status"],
        "apply": bool(args.apply),
        "migrate_provider_bucket": bool(args.migrate_provider_bucket),
        "codex_home": str(codex_home),
        "cc_switch_db": str(cc_switch_db),
        "cockpit_home": str(cockpit_home),
        "before": before,
        "actions": actions,
        "after": after,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 2 if args.apply and after["status"] == "fail" else 0


def inspect_interop(*, codex_home: Path, cc_switch_db: Path, cockpit_home: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    provider_state = inspect_codex_provider_buckets(codex_home=codex_home, cc_switch_db=cc_switch_db)
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
    checks: list[dict[str, Any]] = []
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
        common_config_row = connection.execute(
            "select value from settings where key = 'common_config_codex'"
        ).fetchone()
        common_config = str(common_config_row["value"] or "") if common_config_row else ""
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

    checks.append(
        {
            "id": "cc_switch_common_sqlite_home",
            "tool": "cc_switch",
            "status": "pass" if _has_exact_top_level(common_config, "sqlite_home", str(codex_home)) else "fail",
            "reason": "CC Switch common Codex config must keep sqlite-backed state in the shared Codex home.",
            "path": str(db_path),
            "expected": str(codex_home),
        }
    )
    checks.append(
        {
            "id": "cc_switch_common_log_dir",
            "tool": "cc_switch",
            "status": "pass" if _has_exact_top_level(common_config, "log_dir", str(codex_home / "log")) else "fail",
            "reason": "CC Switch common Codex config must keep logs in the shared Codex home.",
            "path": str(db_path),
            "expected": str(codex_home / "log"),
        }
    )
    checks.append(
        {
            "id": "cc_switch_common_history",
            "tool": "cc_switch",
            "status": "pass" if _has_history_save_all(common_config) else "fail",
            "reason": "CC Switch common Codex config must keep transcript persistence enabled.",
            "path": str(db_path),
            "expected": SHARED_HISTORY_KEYS,
        }
    )

    if not providers:
        checks.append(
            {
                "id": "cc_switch_codex_provider_present",
                "tool": "cc_switch",
                "status": "warn",
                "reason": "No Codex provider is configured in CC Switch.",
                "path": str(db_path),
            }
        )
        return checks

    for provider in providers:
        provider_id = str(provider["id"])
        provider_name = str(provider["name"] or provider_id)
        provider_config = _settings_config_provider_text(provider["settings_config"])
        has_disable_storage = any(
            line.strip().startswith("disable_response_storage") for line in provider_config.splitlines()
        )
        checks.append(
            {
                "id": f"cc_switch_provider_storage_{provider_id}",
                "tool": "cc_switch",
                "status": "fail" if has_disable_storage else "pass",
                "reason": "CC Switch provider config must not disable Codex response/session storage.",
                "path": str(db_path),
                "provider_id": provider_id,
                "provider_name": provider_name,
                "is_current": bool(provider["is_current"]),
            }
        )
    return checks


def inspect_codex_provider_buckets(*, codex_home: Path, cc_switch_db: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    state_path = codex_home / "state_5.sqlite"
    config_path = codex_home / "config.toml"
    distribution = _read_codex_thread_provider_distribution(state_path)
    dominant_provider = _dominant_provider(distribution)

    checks.append(
        {
            "id": "codex_thread_provider_distribution",
            "tool": "codex",
            "status": "pass",
            "reason": "Codex local history visibility is bucketed by threads.model_provider; this distribution must be considered when switching relays.",
            "path": str(state_path),
            "distribution": distribution,
            "dominant_provider": dominant_provider,
        }
    )

    config_text = _read_text(config_path)
    active_provider = _toml_top_level_string(config_text, "model_provider") or "openai"
    active_status = "pass"
    active_reason = "Codex live config uses the same provider bucket as the dominant local history bucket."
    if dominant_provider and active_provider != dominant_provider:
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

    checks.extend(_inspect_cc_switch_current_provider_bucket(cc_switch_db, dominant_provider))
    return {"checks": checks, "distribution": distribution, "dominant_provider": dominant_provider}


def _inspect_cc_switch_current_provider_bucket(
    db_path: Path, dominant_provider: str | None
) -> list[dict[str, Any]]:
    if not db_path.exists():
        return []
    try:
        connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        providers = connection.execute(
            "select id, name, settings_config, is_current from providers where app_type = 'codex' and is_current = 1"
        ).fetchall()
    except sqlite3.Error as exc:
        return [
            {
                "id": "cc_switch_current_provider_bucket",
                "tool": "cc_switch",
                "status": "fail",
                "reason": f"Cannot inspect current CC Switch Codex provider bucket: {exc}",
                "path": str(db_path),
            }
        ]
    finally:
        try:
            connection.close()
        except UnboundLocalError:
            pass

    checks: list[dict[str, Any]] = []
    for provider in providers:
        provider_config = _settings_config_provider_text(provider["settings_config"])
        provider_bucket = _toml_top_level_string(provider_config, "model_provider") or "openai"
        relay_source_provider = _custom_provider_id_for_openai_base_url(provider_config)
        provider_info = _model_provider_info(provider_config, provider_bucket)
        if relay_source_provider and provider_bucket == "openai":
            provider_info = _model_provider_info(provider_config, relay_source_provider)
        can_normalize = bool(provider_info.get("base_url")) or provider_bucket == "openai"
        status = "pass"
        reason = "Current CC Switch Codex provider keeps the same visible history bucket."
        if relay_source_provider and provider_bucket == "openai":
            status = "fail"
            reason = "Current CC Switch Codex provider maps a relay endpoint onto the reserved openai provider, which can send relay credentials to the official OpenAI endpoint."
        elif dominant_provider and provider_bucket != dominant_provider:
            status = "fail" if can_normalize else "warn"
            reason = (
                "Current CC Switch Codex provider would switch Codex App/CLI history visibility to a different model_provider bucket."
            )
        checks.append(
            {
                "id": f"cc_switch_current_provider_bucket_{provider['id']}",
                "tool": "cc_switch",
                "status": status,
                "reason": reason,
                "path": str(db_path),
                "provider_id": provider["id"],
                "provider_name": provider["name"] or provider["id"],
                "provider_bucket": provider_bucket,
                "dominant_provider": dominant_provider,
                "expected_shared_provider": SHARED_RELAY_PROVIDER_ID,
                "repair_strategy": "stable_ccswitch_provider" if status == "fail" and can_normalize else "manual_review",
                "relay_source_provider": relay_source_provider,
                "base_url": provider_info.get("base_url"),
                "requires_openai_auth": provider_info.get("requires_openai_auth"),
            }
        )
    return checks


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

    isolation_findings = _cockpit_instance_isolation_findings(instances, codex_home)
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
    return checks


def repair_cc_switch(*, codex_home: Path, db_path: Path, checks: dict[str, Any]) -> list[dict[str, Any]]:
    if not db_path.exists():
        return []
    needs_cc_switch_repair = any(
        str(check.get("tool")) == "cc_switch" and check.get("status") == "fail"
        for check in checks.get("checks", [])
    )
    connection = sqlite3.connect(str(db_path), timeout=15)
    connection.row_factory = sqlite3.Row
    actions: list[dict[str, Any]] = []
    if needs_cc_switch_repair:
        backup_path = _backup_cc_switch_db(db_path)
        actions.append(
            {
                "id": "cc_switch_db_backup",
                "tool": "cc_switch",
                "status": "ok",
                "backup_path": str(backup_path),
            }
        )
    try:
        row = connection.execute("select value from settings where key = 'common_config_codex'").fetchone()
        common_config = str(row["value"] or "") if row else ""
        repaired_common = ensure_common_config_shared(common_config, codex_home)
        if needs_cc_switch_repair and repaired_common != common_config:
            if row:
                connection.execute(
                    "update settings set value = ? where key = 'common_config_codex'",
                    (repaired_common,),
                )
            else:
                connection.execute(
                    "insert into settings(key, value) values(?, ?)",
                    ("common_config_codex", repaired_common),
                )
            actions.append(
                {
                    "id": "cc_switch_common_config_shared_history",
                    "tool": "cc_switch",
                    "status": "changed",
                    "details": ["sqlite_home", "log_dir", "history.persistence"],
                }
            )

        current_provider_config = ""
        providers = connection.execute(
            "select id, settings_config, is_current from providers where app_type = 'codex'"
        ).fetchall()
        for provider in providers:
            raw_settings = str(provider["settings_config"] or "")
            repaired_settings = repair_provider_settings_config(raw_settings)
            if needs_cc_switch_repair and repaired_settings != raw_settings:
                connection.execute(
                    "update providers set settings_config = ? where id = ?",
                    (repaired_settings, provider["id"]),
                )
                actions.append(
                    {
                        "id": "cc_switch_provider_storage_enabled",
                        "tool": "cc_switch",
                        "status": "changed",
                        "provider_id": provider["id"],
                    }
                )
            if bool(provider["is_current"]):
                current_provider_config = _settings_config_provider_text(repaired_settings)
        connection.commit()
    finally:
        connection.close()
    if current_provider_config:
        actions.extend(repair_codex_live_config(codex_home=codex_home, provider_config=current_provider_config))
    return actions


def _backup_cc_switch_db(db_path: Path) -> Path:
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"db_backup_{timestamp}_codex_interop.db"
    shutil.copy2(db_path, backup_path)
    return backup_path


def repair_codex_live_config(*, codex_home: Path, provider_config: str) -> list[dict[str, Any]]:
    provider_bucket = _toml_top_level_string(provider_config, "model_provider")
    if provider_bucket != SHARED_RELAY_PROVIDER_ID:
        return []
    provider_table = _extract_model_provider_table(provider_config, SHARED_RELAY_PROVIDER_ID)
    if not provider_table:
        return []
    config_path = codex_home / "config.toml"
    current = _read_text(config_path)
    lines = current.splitlines()
    lines = _remove_top_level_key(lines, "openai_base_url")
    lines = _set_top_level(lines, "model_provider", _toml_string(SHARED_RELAY_PROVIDER_ID))
    provider_model = _toml_top_level_string(provider_config, "model")
    if provider_model:
        lines = _set_top_level(lines, "model", _toml_string(provider_model))
    lines = _remove_toml_table(lines, f"[model_providers.{SHARED_RELAY_PROVIDER_ID}]")
    lines = _replace_toml_table(
        lines,
        "[profiles.shared-current-provider]",
        [
            "[profiles.shared-current-provider]",
            'forced_login_method = "chatgpt"',
            f"model_provider = {_toml_string(SHARED_RELAY_PROVIDER_ID)}",
        ],
    )
    lines = _replace_toml_table(
        lines,
        "[profiles.shared-relay]",
        [
            "[profiles.shared-relay]",
            'forced_login_method = "chatgpt"',
            f"model_provider = {_toml_string(SHARED_RELAY_PROVIDER_ID)}",
        ],
    )
    if lines and lines[-1].strip():
        lines.append("")
    lines.extend(provider_table)
    updated = "\n".join(lines).rstrip() + "\n"
    if updated == current:
        return []
    backup_path = _backup_file(config_path, suffix="provider_bucket") if config_path.exists() else None
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(updated, encoding="utf-8")
    return [
        {
            "id": "codex_live_config_provider_bucket",
            "tool": "codex",
            "status": "changed",
            "path": str(config_path),
            "backup_path": str(backup_path) if backup_path else None,
            "target_provider": SHARED_RELAY_PROVIDER_ID,
        }
    ]


def ensure_common_config_shared(config: str, codex_home: Path) -> str:
    lines = [line for line in config.splitlines() if not line.strip().startswith("disable_response_storage")]
    lines = _set_top_level(lines, "sqlite_home", _toml_string(str(codex_home)))
    lines = _set_top_level(lines, "log_dir", _toml_string(str(codex_home / "log")))
    lines = _set_history(lines)
    return "\n".join(lines).rstrip() + "\n"


def repair_provider_settings_config(raw_settings: str) -> str:
    try:
        payload = json.loads(raw_settings)
    except json.JSONDecodeError:
        return raw_settings
    if not isinstance(payload, dict):
        return raw_settings
    config = payload.get("config")
    if not isinstance(config, str):
        return raw_settings
    repaired_lines = [
        line for line in config.splitlines() if not line.strip().startswith("disable_response_storage")
    ]
    repaired = _normalize_stable_relay_provider_bucket("\n".join(repaired_lines).rstrip() + "\n")
    if repaired == config:
        return raw_settings
    payload["config"] = repaired
    return json.dumps(payload, ensure_ascii=False)


def _normalize_stable_relay_provider_bucket(config: str) -> str:
    provider_id = _toml_top_level_string(config, "model_provider")
    if provider_id == SHARED_RELAY_PROVIDER_ID:
        return config
    source_provider_id = provider_id if provider_id and _is_custom_provider_id(provider_id) else _custom_provider_id_for_openai_base_url(config)
    if not source_provider_id:
        return config
    provider_info = _model_provider_info(config, source_provider_id)
    if not provider_info:
        return config
    lines = _remove_top_level_key(config.splitlines(), "openai_base_url")
    lines = _rename_model_provider_table(lines, source_provider_id, SHARED_RELAY_PROVIDER_ID)
    lines = _replace_model_provider_refs(lines, source_provider_id, SHARED_RELAY_PROVIDER_ID)
    lines = _set_top_level(lines, "model_provider", _toml_string(SHARED_RELAY_PROVIDER_ID))
    return "\n".join(lines).rstrip() + "\n"


def migrate_codex_provider_bucket(*, codex_home: Path, target_provider: str) -> list[dict[str, Any]]:
    state_path = codex_home / "state_5.sqlite"
    if not state_path.exists():
        return []
    backup_path = _backup_file(state_path, suffix="provider_bucket")
    connection = sqlite3.connect(str(state_path), timeout=15)
    actions: list[dict[str, Any]] = [
        {
            "id": "codex_state_db_backup",
            "tool": "codex",
            "status": "ok",
            "backup_path": str(backup_path),
        }
    ]
    try:
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


def _backup_file(path: Path, *, suffix: str) -> Path:
    backup_dir = path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{path.name}.{timestamp}_{suffix}.bak"
    shutil.copy2(path, backup_path)
    return backup_path


def _custom_provider_id_for_openai_base_url(config: str) -> str | None:
    base_url = _toml_top_level_string(config, "openai_base_url")
    if not base_url:
        return None
    try:
        payload = tomllib.loads(config or "")
    except tomllib.TOMLDecodeError:
        return None
    model_providers = payload.get("model_providers")
    if not isinstance(model_providers, dict):
        return None
    for provider_id, provider_info in model_providers.items():
        if not _is_custom_provider_id(str(provider_id)) or not isinstance(provider_info, dict):
            continue
        if provider_info.get("base_url") == base_url:
            return str(provider_id)
    custom_ids = [
        str(provider_id)
        for provider_id, provider_info in model_providers.items()
        if _is_custom_provider_id(str(provider_id)) and isinstance(provider_info, dict)
    ]
    return custom_ids[0] if len(custom_ids) == 1 else None


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


def _rename_model_provider_table(lines: list[str], old_provider: str, new_provider: str) -> list[str]:
    old_header = f"[model_providers.{old_provider}]"
    new_header = f"[model_providers.{new_provider}]"
    return [new_header if line.strip() == old_header else line for line in lines]


def _replace_model_provider_refs(lines: list[str], old_provider: str, new_provider: str) -> list[str]:
    old_value = _toml_string(old_provider)
    new_value = _toml_string(new_provider)
    result: list[str] = []
    for line in lines:
        if line.strip() == f"model_provider = {old_value}":
            result.append(f"model_provider = {new_value}")
        else:
            result.append(line)
    return result


def _extract_model_provider_table(config: str, provider_id: str) -> list[str]:
    header = f"[model_providers.{provider_id}]"
    result: list[str] = []
    in_target = False
    for line in config.splitlines():
        stripped = line.strip()
        if stripped == header:
            in_target = True
            result.append(header)
            continue
        if in_target and stripped.startswith("["):
            break
        if in_target:
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


def _settings_config_provider_text(raw_settings: Any) -> str:
    try:
        payload = json.loads(str(raw_settings or ""))
    except json.JSONDecodeError:
        return ""
    if not isinstance(payload, dict):
        return ""
    config = payload.get("config")
    return config if isinstance(config, str) else ""


def _read_codex_thread_provider_distribution(state_path: Path) -> dict[str, int]:
    if not state_path.exists():
        return {}
    try:
        connection = sqlite3.connect(f"file:{state_path}?mode=ro", uri=True)
        rows = connection.execute(
            """
            select coalesce(model_provider, '') as provider, count(*) as n
            from threads
            where coalesce(archived, 0) = 0
            group by coalesce(model_provider, '')
            order by n desc, provider asc
            """
        ).fetchall()
    except sqlite3.Error:
        return {}
    finally:
        try:
            connection.close()
        except UnboundLocalError:
            pass
    return {str(provider or "<empty>"): int(count) for provider, count in rows}


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


def _has_exact_top_level(config: str, key: str, value: str) -> bool:
    expected = f"{key} = {_toml_string(value)}"
    for line in config.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            return False
        if stripped == expected:
            return True
    return False


def _has_history_save_all(config: str) -> bool:
    in_history = False
    persistence_ok = False
    max_bytes_ok = False
    for raw_line in config.splitlines():
        line = raw_line.strip()
        if line == "[history]":
            in_history = True
            continue
        if in_history and line.startswith("["):
            break
        if in_history and line == SHARED_HISTORY_KEYS["history_persistence"]:
            persistence_ok = True
        if in_history and line == SHARED_HISTORY_KEYS["history_max_bytes"]:
            max_bytes_ok = True
    return persistence_ok and max_bytes_ok


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


def _set_history(lines: list[str]) -> list[str]:
    result: list[str] = []
    in_history = False
    seen_history = False
    seen_persistence = False
    seen_max_bytes = False

    for line in lines:
        stripped = line.strip()
        if stripped == "[history]":
            seen_history = True
            in_history = True
            result.append(line)
            continue
        if in_history and stripped.startswith("["):
            if not seen_persistence:
                result.append(SHARED_HISTORY_KEYS["history_persistence"])
            if not seen_max_bytes:
                result.append(SHARED_HISTORY_KEYS["history_max_bytes"])
            in_history = False
        if in_history and stripped.startswith("persistence ="):
            result.append(SHARED_HISTORY_KEYS["history_persistence"])
            seen_persistence = True
            continue
        if in_history and stripped.startswith("max_bytes ="):
            result.append(SHARED_HISTORY_KEYS["history_max_bytes"])
            seen_max_bytes = True
            continue
        result.append(line)

    if in_history:
        if not seen_persistence:
            result.append(SHARED_HISTORY_KEYS["history_persistence"])
        if not seen_max_bytes:
            result.append(SHARED_HISTORY_KEYS["history_max_bytes"])
    if not seen_history:
        result.extend(["", "[history]", SHARED_HISTORY_KEYS["history_persistence"], SHARED_HISTORY_KEYS["history_max_bytes"]])
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


def _read_json(path: Path) -> Any:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _list_len(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def _toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


if __name__ == "__main__":
    raise SystemExit(main())
