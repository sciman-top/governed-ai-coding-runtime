"""Service-shaped metadata persistence primitives."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
import importlib
import json
from pathlib import Path
import sqlite3


@dataclass(frozen=True, slots=True)
class MetadataRecord:
    namespace: str
    key: str
    payload: dict
    updated_at: str


@dataclass(frozen=True, slots=True)
class RetentionPruneResult:
    namespace: str
    retained_keys: list[str]
    pruned_keys: list[str]
    rollback_records: list[MetadataRecord]


class SqliteMetadataStore:
    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path).resolve(strict=False)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @property
    def db_path(self) -> Path:
        return self._db_path

    def upsert(self, *, namespace: str, key: str, payload: dict) -> MetadataRecord:
        namespace_value = _required_string(namespace, "namespace")
        key_value = _required_string(key, "key")
        updated_at = datetime.now(UTC).isoformat()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO runtime_metadata(namespace, key, payload, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(namespace, key) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (namespace_value, key_value, json.dumps(payload, sort_keys=True), updated_at),
            )
        return MetadataRecord(namespace=namespace_value, key=key_value, payload=dict(payload), updated_at=updated_at)

    def get(self, *, namespace: str, key: str) -> MetadataRecord | None:
        namespace_value = _required_string(namespace, "namespace")
        key_value = _required_string(key, "key")
        with self._connection() as conn:
            row = conn.execute(
                "SELECT namespace, key, payload, updated_at FROM runtime_metadata WHERE namespace = ? AND key = ?",
                (namespace_value, key_value),
            ).fetchone()
        if row is None:
            return None
        return MetadataRecord(
            namespace=row[0],
            key=row[1],
            payload=json.loads(row[2]),
            updated_at=row[3],
        )

    def list_namespace(self, *, namespace: str) -> list[MetadataRecord]:
        namespace_value = _required_string(namespace, "namespace")
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT namespace, key, payload, updated_at FROM runtime_metadata WHERE namespace = ? ORDER BY key",
                (namespace_value,),
            ).fetchall()
        return [
            MetadataRecord(namespace=row[0], key=row[1], payload=json.loads(row[2]), updated_at=row[3]) for row in rows
        ]

    def delete(self, *, namespace: str, key: str) -> MetadataRecord | None:
        namespace_value = _required_string(namespace, "namespace")
        key_value = _required_string(key, "key")
        record = self.get(namespace=namespace_value, key=key_value)
        if record is None:
            return None
        with self._connection() as conn:
            conn.execute(
                "DELETE FROM runtime_metadata WHERE namespace = ? AND key = ?",
                (namespace_value, key_value),
            )
        return record

    def restore(self, record: MetadataRecord) -> MetadataRecord:
        return self.upsert(namespace=record.namespace, key=record.key, payload=record.payload)

    def applied_migrations(self) -> list[str]:
        with self._connection() as conn:
            rows = conn.execute("SELECT migration_id FROM schema_migrations ORDER BY migration_id").fetchall()
        return [row[0] for row in rows]

    def export_replay_bundle(self, *, namespaces: list[str]) -> dict:
        namespace_values = [_required_string(namespace, "namespace") for namespace in namespaces]
        records = {
            namespace: [
                {
                    "key": record.key,
                    "payload": record.payload,
                    "updated_at": record.updated_at,
                }
                for record in self.list_namespace(namespace=namespace)
            ]
            for namespace in namespace_values
        }
        return {
            "schema_version": "1.0",
            "store_kind": "sqlite_metadata",
            "db_path": self._db_path.as_posix(),
            "namespaces": records,
            "migrations": self.applied_migrations(),
        }

    def prune_namespace(self, *, namespace: str, retain_latest: int) -> RetentionPruneResult:
        namespace_value = _required_string(namespace, "namespace")
        if not isinstance(retain_latest, int) or retain_latest < 1:
            raise ValueError("retain_latest must be a positive integer")
        records = sorted(self.list_namespace(namespace=namespace_value), key=lambda record: record.updated_at)
        pruned = records[:-retain_latest] if len(records) > retain_latest else []
        for record in pruned:
            self.delete(namespace=record.namespace, key=record.key)
        retained_keys = [record.key for record in self.list_namespace(namespace=namespace_value)]
        return RetentionPruneResult(
            namespace=namespace_value,
            retained_keys=retained_keys,
            pruned_keys=[record.key for record in pruned],
            rollback_records=pruned,
        )

    def _init_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runtime_metadata (
                    namespace TEXT NOT NULL,
                    key TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(namespace, key)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    migration_id TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO schema_migrations(migration_id, applied_at)
                VALUES (?, ?)
                """,
                ("001_runtime_metadata", datetime.now(UTC).isoformat()),
            )

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self._db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


class PostgresMetadataStore:
    """Optional Postgres-backed metadata store with the SqliteMetadataStore interface."""

    def __init__(self, dsn: str) -> None:
        self._dsn = _required_string(dsn, "dsn")
        try:
            self._psycopg = importlib.import_module("psycopg")
        except ImportError as exc:
            msg = "psycopg is required for PostgresMetadataStore"
            raise RuntimeError(msg) from exc

    def upsert(self, *, namespace: str, key: str, payload: dict) -> MetadataRecord:
        namespace_value = _required_string(namespace, "namespace")
        key_value = _required_string(key, "key")
        updated_at = datetime.now(UTC).isoformat()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO runtime_metadata(namespace, key, payload, updated_at)
                VALUES (%s, %s, %s::jsonb, %s::timestamptz)
                ON CONFLICT(namespace, key) DO UPDATE SET
                    payload = EXCLUDED.payload,
                    updated_at = EXCLUDED.updated_at
                """,
                (namespace_value, key_value, json.dumps(payload, sort_keys=True), updated_at),
            )
        return MetadataRecord(namespace=namespace_value, key=key_value, payload=dict(payload), updated_at=updated_at)

    def get(self, *, namespace: str, key: str) -> MetadataRecord | None:
        namespace_value = _required_string(namespace, "namespace")
        key_value = _required_string(key, "key")
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT namespace, key, payload::text, updated_at::text
                FROM runtime_metadata
                WHERE namespace = %s AND key = %s
                """,
                (namespace_value, key_value),
            ).fetchone()
        if row is None:
            return None
        return MetadataRecord(
            namespace=row[0],
            key=row[1],
            payload=json.loads(row[2]),
            updated_at=row[3],
        )

    def list_namespace(self, *, namespace: str) -> list[MetadataRecord]:
        namespace_value = _required_string(namespace, "namespace")
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT namespace, key, payload::text, updated_at::text
                FROM runtime_metadata
                WHERE namespace = %s
                ORDER BY key
                """,
                (namespace_value,),
            ).fetchall()
        return [
            MetadataRecord(namespace=row[0], key=row[1], payload=json.loads(row[2]), updated_at=row[3]) for row in rows
        ]

    @contextmanager
    def _connection(self):
        conn = self._psycopg.connect(self._dsn)
        try:
            setattr(conn, "last_dsn", self._dsn)
        except (AttributeError, TypeError):
            pass
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()
