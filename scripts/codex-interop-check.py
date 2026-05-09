from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


SHARED_HISTORY_KEYS = {
    "history_persistence": 'persistence = "save-all"',
    "history_max_bytes": "max_bytes = 104857600",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Codex third-party switcher shared-history interop.")
    parser.add_argument("--codex-home", required=True)
    parser.add_argument("--cc-switch-db", required=True)
    parser.add_argument("--cockpit-home", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    codex_home = Path(args.codex_home).expanduser().resolve()
    cc_switch_db = Path(args.cc_switch_db).expanduser()
    cockpit_home = Path(args.cockpit_home).expanduser()

    before = inspect_interop(codex_home=codex_home, cc_switch_db=cc_switch_db, cockpit_home=cockpit_home)
    actions: list[dict[str, Any]] = []
    if args.apply:
        actions.extend(repair_cc_switch(codex_home=codex_home, db_path=cc_switch_db, checks=before))
    after = inspect_interop(codex_home=codex_home, cc_switch_db=cc_switch_db, cockpit_home=cockpit_home)

    payload = {
        "status": after["status"],
        "apply": bool(args.apply),
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
    needs_repair = any(
        str(check.get("tool")) == "cc_switch" and check.get("status") == "fail"
        for check in checks.get("checks", [])
    )
    if not needs_repair:
        return []

    backup_path = _backup_cc_switch_db(db_path)
    connection = sqlite3.connect(str(db_path), timeout=15)
    connection.row_factory = sqlite3.Row
    actions: list[dict[str, Any]] = [
        {
            "id": "cc_switch_db_backup",
            "tool": "cc_switch",
            "status": "ok",
            "backup_path": str(backup_path),
        }
    ]
    try:
        row = connection.execute("select value from settings where key = 'common_config_codex'").fetchone()
        common_config = str(row["value"] or "") if row else ""
        repaired_common = ensure_common_config_shared(common_config, codex_home)
        if repaired_common != common_config:
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

        providers = connection.execute(
            "select id, settings_config from providers where app_type = 'codex'"
        ).fetchall()
        for provider in providers:
            raw_settings = str(provider["settings_config"] or "")
            repaired_settings = repair_provider_settings_config(raw_settings)
            if repaired_settings != raw_settings:
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
        connection.commit()
    finally:
        connection.close()
    return actions


def _backup_cc_switch_db(db_path: Path) -> Path:
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"db_backup_{timestamp}_codex_interop.db"
    shutil.copy2(db_path, backup_path)
    return backup_path


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
    repaired = "\n".join(repaired_lines).rstrip() + "\n"
    if repaired == config:
        return raw_settings
    payload["config"] = repaired
    return json.dumps(payload, ensure_ascii=False)


def _settings_config_provider_text(raw_settings: Any) -> str:
    try:
        payload = json.loads(str(raw_settings or ""))
    except json.JSONDecodeError:
        return ""
    if not isinstance(payload, dict):
        return ""
    config = payload.get("config")
    return config if isinstance(config, str) else ""


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
