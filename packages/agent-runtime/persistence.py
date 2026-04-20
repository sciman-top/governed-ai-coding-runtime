"""Service-shaped metadata persistence primitives."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import sqlite3

try:
    import psycopg
except ImportError:  # pragma: no cover - exercised through runtime fallback tests
    psycopg = None


@dataclass(frozen=True, slots=True)
class MetadataRecord:
    namespace: str
    key: str
    payload: dict
    updated_at: str


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

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self._db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


class PostgresMetadataStore:
    def __init__(self, dsn: str) -> None:
        dsn_value = _required_string(dsn, "dsn")
        if psycopg is None:
            raise RuntimeError("psycopg is required for PostgresMetadataStore")
        self._dsn = dsn_value
        self._init_schema()

    def upsert(self, *, namespace: str, key: str, payload: dict) -> MetadataRecord:
        namespace_value = _required_string(namespace, "namespace")
        key_value = _required_string(key, "key")
        updated_at = datetime.now(UTC).isoformat()
        payload_json = json.dumps(payload, sort_keys=True)
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO runtime_metadata(namespace, key, payload, updated_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (namespace, key) DO UPDATE SET
                    payload = EXCLUDED.payload,
                    updated_at = EXCLUDED.updated_at
                """,
                (namespace_value, key_value, payload_json, updated_at),
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
            payload=_load_payload(row[2]),
            updated_at=_load_text(row[3]),
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
            MetadataRecord(namespace=row[0], key=row[1], payload=_load_payload(row[2]), updated_at=_load_text(row[3]))
            for row in rows
        ]

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

    @contextmanager
    def _connection(self):
        conn = psycopg.connect(self._dsn)
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


def _load_payload(payload: object) -> dict:
    if isinstance(payload, str):
        return json.loads(payload)
    return dict(payload)


def _load_text(value: object) -> str:
    return value if isinstance(value, str) else str(value)
