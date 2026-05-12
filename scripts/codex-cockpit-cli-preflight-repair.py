#!/usr/bin/env python3
"""Repair Cockpit Tools -> Codex CLI auth/provider projection before launching codex.

This script is intentionally user-level and independent of the Cockpit Tools
installation directory. It repairs only the shared Codex home selected by the
current Cockpit Codex account.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


OFFICIAL_OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_PROVIDER_ID = "openai"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--cockpit-home", type=Path, default=Path.home() / ".antigravity_cockpit")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        changes = repair(args.codex_home, args.cockpit_home, dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001 - wrapper preflight must never hide launch path details
        if not args.quiet:
            print(f"[codex-preflight] repair failed: {exc}", file=sys.stderr)
        return 2

    if changes and not args.quiet:
        print("[codex-preflight] repaired: " + ", ".join(changes), file=sys.stderr)
    return 0


def repair(codex_home: Path, cockpit_home: Path, *, dry_run: bool) -> list[str]:
    cockpit_metadata_changes = repair_cockpit_api_account_metadata(cockpit_home, dry_run=dry_run)
    if cockpit_metadata_changes:
        # Reload the account after metadata repair so the projection uses restored provider fields.
        pass
    current = read_current_cockpit_account(cockpit_home)
    auth_mode = str(current.get("auth_mode") or "oauth").lower()
    is_api = auth_mode in {"apikey", "api_key", "api-key"} or bool(current.get("openai_api_key"))
    changes: list[str] = []
    if cockpit_metadata_changes:
        changes.append(f"cockpit_accounts:{cockpit_metadata_changes}")

    codex_home.mkdir(parents=True, exist_ok=True)
    auth_path = codex_home / "auth.json"
    config_path = codex_home / "config.toml"

    existing_auth = read_json_or_none(auth_path)
    desired_auth = build_auth_json(current, is_api=is_api, existing_auth=existing_auth)
    if not auth_matches(existing_auth, desired_auth, is_api=is_api):
        changes.append("auth.json")
        if not dry_run:
            backup_file(auth_path)
            atomic_write_text(auth_path, json.dumps(desired_auth, ensure_ascii=False, indent=2) + "\n")

    existing_config = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    desired_config = repair_config_text(existing_config, current, is_api=is_api)
    if desired_config != existing_config:
        changes.append("config.toml")
        if not dry_run:
            backup_file(config_path)
            atomic_write_text(config_path, desired_config)

    sqlite_changes = repair_state_db(codex_home / "state_5.sqlite", dry_run=dry_run)
    if sqlite_changes:
        changes.append(f"state_5.sqlite:{sqlite_changes}")

    session_changes = repair_session_jsonl_providers(codex_home, dry_run=dry_run)
    if session_changes:
        changes.append(f"sessions:{session_changes}")

    return changes


def repair_cockpit_api_account_metadata(cockpit_home: Path, *, dry_run: bool) -> int:
    accounts_dir = cockpit_home / "codex_accounts"
    if not accounts_dir.exists():
        return 0
    providers = read_json_or_none(cockpit_home / "codex_model_providers.json")
    provider_items = providers if isinstance(providers, list) else []
    changed = 0

    for account_path in accounts_dir.glob("*.json"):
        if account_path.name.endswith(".bak"):
            continue
        account = read_json_or_none(account_path)
        if not isinstance(account, dict):
            continue
        auth_mode = str(account.get("auth_mode") or "").lower()
        if auth_mode not in {"apikey", "api_key", "api-key"} and not account.get("openai_api_key"):
            continue
        if first_string(account.get("api_base_url")) and account.get("api_provider_mode") == "custom":
            continue

        restored = restore_api_metadata_from_backup(account_path, account)
        if restored is None:
            restored = restore_api_metadata_from_provider_store(account, provider_items)
        if restored is None:
            continue

        updated = dict(account)
        updated.update(restored)
        if updated == account:
            continue
        changed += 1
        if not dry_run:
            backup_file(account_path)
            atomic_write_text(account_path, json.dumps(updated, ensure_ascii=False, indent=2) + "\n")

    return changed


def restore_api_metadata_from_backup(account_path: Path, account: dict[str, Any]) -> dict[str, Any] | None:
    backup_path = Path(str(account_path) + ".bak")
    backup = read_json_or_none(backup_path)
    if not isinstance(backup, dict):
        return None
    if backup.get("id") != account.get("id"):
        return None
    base_url = first_string(backup.get("api_base_url"))
    provider_id = first_string(backup.get("api_provider_id"))
    provider_name = first_string(backup.get("api_provider_name"))
    if not base_url:
        return None
    return {
        "api_base_url": base_url,
        "api_provider_mode": "custom" if provider_id else backup.get("api_provider_mode") or "custom",
        "api_provider_id": provider_id,
        "api_provider_name": provider_name,
    }


def restore_api_metadata_from_provider_store(
    account: dict[str, Any],
    providers: list[Any],
) -> dict[str, Any] | None:
    api_key = first_string(account.get("openai_api_key"), account.get("OPENAI_API_KEY"))
    if not api_key:
        return None
    for provider in providers:
        if not isinstance(provider, dict):
            continue
        if not provider_contains_api_key(provider.get("apiKeys"), api_key):
            continue
        base_url = first_string(provider.get("baseUrl"), provider.get("base_url"))
        provider_id = first_string(provider.get("id"))
        if not base_url or not provider_id:
            continue
        return {
            "api_base_url": normalize_base_url(base_url),
            "api_provider_mode": "custom",
            "api_provider_id": provider_id,
            "api_provider_name": first_string(provider.get("name")) or provider_id,
        }
    return None


def provider_contains_api_key(value: Any, api_key: str) -> bool:
    if isinstance(value, str):
        return value == api_key
    if isinstance(value, dict):
        return any(provider_contains_api_key(child, api_key) for child in value.values())
    if isinstance(value, list):
        return any(provider_contains_api_key(child, api_key) for child in value)
    return False


def read_current_cockpit_account(cockpit_home: Path) -> dict[str, Any]:
    index = read_json(cockpit_home / "codex_accounts.json")
    current_id = index.get("current_account_id") or index.get("currentAccountId")
    if not current_id:
        raise RuntimeError("Cockpit current Codex account is missing")

    account_path = cockpit_home / "codex_accounts" / f"{current_id}.json"
    account = read_json(account_path)
    if account.get("id") != current_id:
        raise RuntimeError(f"Cockpit account id mismatch: {account_path}")
    return account


def build_auth_json(
    account: dict[str, Any],
    *,
    is_api: bool,
    existing_auth: Any,
) -> dict[str, Any]:
    if is_api:
        api_key = first_string(account.get("openai_api_key"), account.get("OPENAI_API_KEY"))
        if not api_key:
            raise RuntimeError("Current Cockpit API account has no OPENAI_API_KEY")
        return {
            "auth_mode": "apikey",
            "OPENAI_API_KEY": api_key,
        }

    tokens = account.get("tokens")
    if not isinstance(tokens, dict):
        raise RuntimeError("Current Cockpit OAuth account has no tokens")
    id_token = first_string(tokens.get("id_token"))
    access_token = first_string(tokens.get("access_token"))
    if not id_token or not access_token:
        raise RuntimeError("Current Cockpit OAuth account lacks id_token/access_token")
    codex_tokens: dict[str, Any] = {
        "id_token": id_token,
        "access_token": access_token,
        "refresh_token": tokens.get("refresh_token"),
    }
    account_id = first_string(account.get("account_id"), tokens.get("account_id"))
    if account_id:
        codex_tokens["account_id"] = account_id
    last_refresh = None
    if isinstance(existing_auth, dict):
        last_refresh = existing_auth.get("last_refresh")
    if not isinstance(last_refresh, str) or not last_refresh.strip():
        last_refresh = datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")

    return {
        "OPENAI_API_KEY": None,
        "tokens": codex_tokens,
        "last_refresh": last_refresh,
    }


def auth_matches(existing_auth: Any, desired_auth: dict[str, Any], *, is_api: bool) -> bool:
    if not isinstance(existing_auth, dict):
        return False
    if is_api:
        return existing_auth == desired_auth
    existing = dict(existing_auth)
    desired = dict(desired_auth)
    existing.pop("last_refresh", None)
    desired.pop("last_refresh", None)
    return existing == desired


def repair_config_text(config: str, account: dict[str, Any], *, is_api: bool) -> str:
    text = config
    text = set_top_level_key(text, "forced_login_method", "api" if is_api else "chatgpt")
    text = set_top_level_key(text, "model_provider", OPENAI_PROVIDER_ID)

    if is_api:
        base_url = normalize_base_url(
            first_string(
                account.get("api_base_url"),
                account.get("base_url"),
                account.get("baseUrl"),
                account.get("OPENAI_BASE_URL"),
            )
        )
        if base_url and base_url != OFFICIAL_OPENAI_BASE_URL:
            text = set_top_level_key(text, "openai_base_url", base_url)
        else:
            text = remove_top_level_key(text, "openai_base_url")
    else:
        text = remove_top_level_key(text, "openai_base_url")

    text = repair_custom_provider_auth_flags(text, account)
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def repair_custom_provider_auth_flags(config: str, account: dict[str, Any]) -> str:
    provider_ids = {
        str(value).strip()
        for value in (account.get("api_provider_id"), "provider_openai")
        if isinstance(value, str) and value.strip()
    }
    if not provider_ids:
        return config

    lines = config.splitlines()
    out: list[str] = []
    active_provider: str | None = None
    seen_requires: dict[str, bool] = {}
    seen_websocket: dict[str, bool] = {}
    table_re = re.compile(r'^\s*\[model_providers\.(?:"([^"]+)"|([A-Za-z0-9_-]+))\]\s*$')
    any_table_re = re.compile(r"^\s*\[.*\]\s*$")

    for line in lines:
        match = table_re.match(line)
        if match:
            active_provider = match.group(1) or match.group(2)
        elif any_table_re.match(line):
            if active_provider in provider_ids:
                if not seen_requires.get(active_provider, False):
                    out.append("requires_openai_auth = false")
                if not seen_websocket.get(active_provider, False):
                    out.append("supports_websockets = false")
            active_provider = None

        if active_provider in provider_ids:
            if re.match(r"^\s*requires_openai_auth\s*=", line):
                out.append("requires_openai_auth = false")
                seen_requires[active_provider] = True
                continue
            if re.match(r"^\s*supports_websockets\s*=", line):
                out.append("supports_websockets = false")
                seen_websocket[active_provider] = True
                continue

        out.append(line)

    if active_provider in provider_ids:
        if not seen_requires.get(active_provider, False):
            out.append("requires_openai_auth = false")
        if not seen_websocket.get(active_provider, False):
            out.append("supports_websockets = false")

    return "\n".join(out) + ("\n" if config.endswith("\n") else "")


def set_top_level_key(config: str, key: str, value: str) -> str:
    assignment = f'{key} = "{escape_toml_string(value)}"'
    lines = config.splitlines()
    out: list[str] = []
    in_table = False
    replaced = False
    inserted = False

    for line in lines:
        if not in_table and re.match(rf"^\s*{re.escape(key)}\s*=", line):
            if not replaced:
                out.append(assignment)
                replaced = True
            continue
        if not inserted and not replaced and re.match(r"^\s*\[.*\]\s*$", line):
            out.append(assignment)
            inserted = True
        if re.match(r"^\s*\[.*\]\s*$", line):
            in_table = True
        out.append(line)

    if not replaced and not inserted:
        out.append(assignment)
    return "\n".join(out) + ("\n" if config.endswith("\n") or not config else "")


def remove_top_level_key(config: str, key: str) -> str:
    lines = config.splitlines()
    out: list[str] = []
    in_table = False
    for line in lines:
        if re.match(r"^\s*\[.*\]\s*$", line):
            in_table = True
        if not in_table and re.match(rf"^\s*{re.escape(key)}\s*=", line):
            continue
        out.append(line)
    return "\n".join(out) + ("\n" if config.endswith("\n") and out else "")


def repair_state_db(db_path: Path, *, dry_run: bool) -> int:
    if not db_path.exists():
        return 0
    try:
        with sqlite3.connect(str(db_path), timeout=3) as connection:
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(threads)").fetchall()
            }
            if "model_provider" not in columns:
                return 0
            count = connection.execute(
                "SELECT COUNT(*) FROM threads WHERE COALESCE(model_provider, '') <> ?",
                (OPENAI_PROVIDER_ID,),
            ).fetchone()[0]
            if not count:
                return 0
            if dry_run:
                return int(count)
            backup_file(db_path)
            connection.execute(
                "UPDATE threads SET model_provider = ? WHERE COALESCE(model_provider, '') <> ?",
                (OPENAI_PROVIDER_ID, OPENAI_PROVIDER_ID),
            )
            connection.commit()
            return int(count)
    except sqlite3.Error as exc:
        raise RuntimeError(f"SQLite repair failed: {db_path}: {exc}") from exc


def repair_session_jsonl_providers(codex_home: Path, *, dry_run: bool) -> int:
    sessions_dir = codex_home / "sessions"
    if not sessions_dir.exists():
        return 0
    changed = 0
    for path in sessions_dir.rglob("*.jsonl"):
        try:
            text = path.read_text(encoding="utf-8")
        except (PermissionError, OSError, UnicodeDecodeError):
            continue
        if '"model_provider"' not in text:
            continue
        repaired = re.sub(
            r'("model_provider"\s*:\s*")([^"]+)(")',
            lambda match: match.group(1) + OPENAI_PROVIDER_ID + match.group(3),
            text,
        )
        if repaired == text:
            continue
        changed += 1
        if not dry_run:
            backup_file(path)
            try:
                atomic_write_text(path, repaired)
            except (PermissionError, OSError):
                changed -= 1
                continue
    return changed


def normalize_base_url(value: str | None) -> str | None:
    if not value:
        return None
    trimmed = value.strip()
    while trimmed.endswith("/"):
        trimmed = trimmed[:-1]
    return trimmed or None


def first_string(*values: Any) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def escape_toml_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def read_json_or_none(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return None


def backup_file(path: Path) -> None:
    if not path.exists():
        return
    backup_dir = path.parent / "backups" / "codex-cockpit-cli-preflight"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    shutil.copy2(path, backup_dir / f"{path.name}.{stamp}.bak")


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="\n",
        delete=False,
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    ) as handle:
        handle.write(content)
        temp_name = handle.name
    os.replace(temp_name, path)


if __name__ == "__main__":
    raise SystemExit(main())
