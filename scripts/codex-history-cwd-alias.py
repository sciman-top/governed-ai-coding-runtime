from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect or repair Codex App history cwd aliases in state_5.sqlite."
    )
    parser.add_argument("--codex-home", required=True)
    parser.add_argument(
        "--alias",
        action="append",
        default=[],
        metavar="FROM=>TO",
        help="Rewrite threads.cwd from FROM to TO. Repeat for multiple aliases.",
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    codex_home = Path(args.codex_home).expanduser().resolve()
    state_path = codex_home / "state_5.sqlite"
    aliases = parse_aliases(args.alias)

    payload: dict[str, Any] = {
        "status": "pass",
        "apply": bool(args.apply),
        "codex_home": str(codex_home),
        "state_path": str(state_path),
        "aliases": [{"from": source, "to": target} for source, target in aliases],
        "checks": [],
        "actions": [],
    }

    if not state_path.exists():
        payload["status"] = "fail"
        payload["checks"].append(
            {
                "id": "codex_state_sqlite_exists",
                "status": "fail",
                "reason": "state_5.sqlite was not found.",
                "path": str(state_path),
            }
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2

    connection = sqlite3.connect(state_path, timeout=30)
    connection.row_factory = sqlite3.Row
    try:
        columns = table_columns(connection, "threads")
        if "cwd" not in columns or "id" not in columns:
            payload["status"] = "fail"
            payload["checks"].append(
                {
                    "id": "codex_threads_cwd_columns",
                    "status": "fail",
                    "reason": "threads table is missing required id/cwd columns.",
                    "columns": sorted(columns),
                }
            )
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 2

        before = inspect_aliases(connection, aliases)
        payload["checks"].append(
            {
                "id": "codex_history_cwd_aliases",
                "status": "pass",
                "reason": "Codex history cwd alias buckets were inspected.",
                "summary": before,
            }
        )

        if args.apply:
            backup_path = backup_sqlite(connection, state_path)
            payload["actions"].append(
                {
                    "id": "codex_state_sqlite_backup",
                    "status": "pass",
                    "path": str(backup_path),
                }
            )
            updated = apply_aliases(connection, aliases)
            payload["actions"].append(
                {
                    "id": "codex_threads_cwd_aliases_updated",
                    "status": "pass",
                    "updated_rows": updated,
                }
            )
            payload["checks"].append(
                {
                    "id": "codex_history_cwd_aliases_after",
                    "status": "pass",
                    "reason": "Codex history cwd alias buckets were inspected after repair.",
                    "summary": inspect_aliases(connection, aliases),
                }
            )
    finally:
        connection.close()

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def parse_aliases(raw_aliases: list[str]) -> list[tuple[str, str]]:
    aliases: list[tuple[str, str]] = []
    for raw in raw_aliases:
        if "=>" not in raw:
            raise SystemExit(f"Alias must use FROM=>TO syntax: {raw}")
        source, target = raw.split("=>", 1)
        source = source.strip()
        target = target.strip()
        if not source or not target:
            raise SystemExit(f"Alias source and target must be non-empty: {raw}")
        aliases.append((source, target))
    return aliases


def table_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {str(row["name"]) for row in connection.execute(f"pragma table_info({table})")}


def inspect_aliases(connection: sqlite3.Connection, aliases: list[tuple[str, str]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for source, target in aliases:
        source_count = count_cwd(connection, source)
        target_count = count_cwd(connection, target)
        summary.append(
            {
                "from": source,
                "to": target,
                "from_count": source_count,
                "to_count": target_count,
                "would_update_rows": source_count if source != target else 0,
            }
        )
    return summary


def count_cwd(connection: sqlite3.Connection, cwd: str) -> int:
    row = connection.execute("select count(*) as count from threads where cwd = ?", (cwd,)).fetchone()
    return int(row["count"])


def backup_sqlite(connection: sqlite3.Connection, state_path: Path) -> Path:
    backup_dir = state_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{state_path.name}.{timestamp}_cwd_alias.bak"
    backup_connection = sqlite3.connect(backup_path)
    try:
        connection.backup(backup_connection)
    finally:
        backup_connection.close()
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(state_path) + suffix)
        if sidecar.exists():
            shutil.copy2(sidecar, backup_dir / f"{sidecar.name}.{timestamp}_cwd_alias.bak")
    return backup_path


def apply_aliases(connection: sqlite3.Connection, aliases: list[tuple[str, str]]) -> int:
    total = 0
    with connection:
        for source, target in aliases:
            if source == target:
                continue
            cursor = connection.execute("update threads set cwd = ? where cwd = ?", (target, source))
            total += int(cursor.rowcount)
    return total


if __name__ == "__main__":
    sys.exit(main())
