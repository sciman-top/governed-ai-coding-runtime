#!/usr/bin/env python3
"""Read-only Cockpit Tools Codex account switching health report."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


TOKEN_INVALIDATED_RE = re.compile(r"(401\s+Unauthorized|token_invalidated)", re.IGNORECASE)


def default_cockpit_home() -> Path:
    return Path.home() / ".antigravity_cockpit"


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {"_read_error": f"{type(exc).__name__}: {exc}"}


def suffix(value: Any, keep: int = 4) -> str | None:
    if value is None:
        return None
    text = str(value)
    if not text:
        return ""
    if len(text) <= keep:
        return text
    return f"...{text[-keep:]}"


def suffix_sample(values: list[str], limit: int = 20) -> dict[str, Any]:
    return {
        "items": [suffix(item) for item in values[:limit]],
        "limit": limit,
        "truncated_count": max(0, len(values) - limit),
    }


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def account_items(accounts_doc: Any) -> list[dict[str, Any]]:
    if not isinstance(accounts_doc, dict):
        return []
    raw_accounts = accounts_doc.get("accounts")
    if isinstance(raw_accounts, list):
        return [item for item in raw_accounts if isinstance(item, dict)]
    if isinstance(raw_accounts, dict):
        return [item for item in raw_accounts.values() if isinstance(item, dict)]
    return [item for item in accounts_doc.values() if isinstance(item, dict) and item.get("id")]


def account_id(account: dict[str, Any]) -> str | None:
    raw = account.get("id") or account.get("account_id") or account.get("accountId")
    return str(raw) if raw else None


def account_plan(account: dict[str, Any]) -> str | None:
    raw = (
        account.get("plan_type")
        or account.get("planType")
        or account.get("plan")
        or account.get("group")
        or account.get("group_name")
        or account.get("groupName")
    )
    return str(raw) if raw else None


def current_account_id(accounts_doc: Any, config: Any) -> str | None:
    for doc in (accounts_doc, config):
        if isinstance(doc, dict):
            raw = (
                doc.get("currentAccountId")
                or doc.get("current_account_id")
                or doc.get("activeAccountId")
                or doc.get("current")
            )
            if raw:
                return str(raw)
    return None


def scan_recent_401(cockpit_home: Path, max_files: int = 3) -> dict[str, Any]:
    log_dir = cockpit_home / "logs"
    if not log_dir.exists():
        return {"token_invalidated_count": 0, "log_files_scanned": []}
    candidates = [path for path in log_dir.glob("*.log*") if path.is_file()]
    candidates.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    scanned: list[str] = []
    count = 0
    for path in candidates[:max_files]:
        scanned.append(path.name)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        count += sum(1 for line in text.splitlines() if TOKEN_INVALIDATED_RE.search(line))
    return {"token_invalidated_count": count, "log_files_scanned": scanned}


def summarize_config(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {"exists": config is not None, "shape": type(config).__name__}
    selected_ids = as_list(config.get("codex_auto_switch_selected_account_ids"))
    return {
        "exists": True,
        "codex_auto_switch_enabled": bool(config.get("codex_auto_switch_enabled")),
        "codex_auto_switch_strategy": config.get("codex_auto_switch_strategy"),
        "codex_auto_switch_free_only": bool(config.get("codex_auto_switch_free_only")),
        "codex_auto_refresh_minutes": config.get("codex_auto_refresh_minutes"),
        "codex_auto_switch_threshold_total_percent": config.get("codex_auto_switch_threshold_total_percent"),
        "codex_auto_switch_threshold_model_percent": config.get("codex_auto_switch_threshold_model_percent"),
        "codex_auto_switch_selected_count": len(selected_ids),
        "codex_launch_on_switch": bool(config.get("codex_launch_on_switch")),
        "codex_restart_specified_app_on_switch": bool(config.get("codex_restart_specified_app_on_switch")),
        "codex_has_app_path": bool(config.get("codex_app_path")),
        "codex_has_specified_app_path": bool(config.get("codex_specified_app_path")),
    }


def evaluate(cockpit_home: Path, target_surface: str = "codex_app") -> dict[str, Any]:
    config = read_json(cockpit_home / "config.json")
    accounts_doc = read_json(cockpit_home / "codex_accounts.json")
    accounts = account_items(accounts_doc)
    accounts_by_id = {account_id(item): item for item in accounts if account_id(item)}

    selected_ids = as_list(config.get("codex_auto_switch_selected_account_ids")) if isinstance(config, dict) else []
    selected_found = [str(item) for item in selected_ids if str(item) in accounts_by_id]
    selected_missing = [str(item) for item in selected_ids if str(item) not in accounts_by_id]
    selected_plans = sorted({account_plan(accounts_by_id[item]) or "unknown" for item in selected_found})

    warnings: list[str] = []
    if isinstance(config, dict) and config.get("codex_auto_switch_enabled") and not selected_ids:
        warnings.append("selected_scope_empty")
    if selected_missing:
        warnings.append("selected_accounts_missing")
    if target_surface == "codex_app":
        warnings.append("codex_app_requires_restart_or_native_hot_reload_for_account_change")

    log_health = scan_recent_401(cockpit_home)
    if log_health["token_invalidated_count"]:
        warnings.append("recent_token_invalidated_or_401_seen")

    return {
        "schema_version": 1,
        "timestamp": _dt.datetime.now().isoformat(timespec="seconds"),
        "cockpit_home": str(cockpit_home),
        "target_surface": target_surface,
        "current_account_id_suffix": suffix(current_account_id(accounts_doc, config)),
        "account_catalog": {
            "total_accounts": len(accounts),
            "plan_types": sorted({account_plan(item) or "unknown" for item in accounts}),
        },
        "auto_switch": summarize_config(config),
        "selected_scope": {
            "selected_count": len(selected_ids),
            "selected_found_count": len(selected_found),
            "selected_missing_count": len(selected_missing),
            "selected_id_suffix_sample": suffix_sample(selected_found),
            "missing_id_suffix_sample": suffix_sample(selected_missing),
            "selected_plan_types": selected_plans,
        },
        "recent_auth_errors": log_health,
        "runtime_boundary": {
            "codex_app_account_change_hot_reload_confirmed": False,
            "codex_app_restart_required_for_account_change": target_surface == "codex_app",
            "codex_cli_new_process_reads_projected_auth": target_surface == "codex_cli",
        },
        "status": "warn" if warnings else "pass",
        "warnings": warnings,
        "write_actions": [],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cockpit-home", type=Path, default=default_cockpit_home())
    parser.add_argument("--target-surface", choices=["codex_app", "codex_cli"], default="codex_app")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default output format.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = evaluate(args.cockpit_home, args.target_surface)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
