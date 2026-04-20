import importlib.util
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class FakeCursor:
    def __init__(self, connection: "FakeConnection", query: str, params: tuple[object, ...]) -> None:
        self._connection = connection
        self.query = query
        self.params = params

    def fetchone(self):
        namespace = self.params[0]
        key = self.params[1]
        return self._connection.records.get((namespace, key))

    def fetchall(self):
        namespace = self.params[0]
        rows = [
            record
            for (record_namespace, _), record in self._connection.records.items()
            if record_namespace == namespace
        ]
        return sorted(rows, key=lambda row: row[1])


class FakeConnection:
    def __init__(self) -> None:
        self.records: dict[tuple[str, str], tuple[str, str, str, str]] = {}
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.commit_calls = 0
        self.close_calls = 0
        self.last_dsn = ""

    def execute(self, query: str, params: tuple[object, ...] | None = None):
        params = () if params is None else params
        self.executed.append((query, params))
        normalized = " ".join(query.split())
        if normalized.startswith("INSERT INTO runtime_metadata"):
            namespace, key, payload, updated_at = params
            self.records[(namespace, key)] = (namespace, key, payload, updated_at)
        return FakeCursor(self, query, params)

    def commit(self):
        self.commit_calls += 1

    def close(self):
        self.close_calls += 1


class FakePsycopgModule(types.SimpleNamespace):
    def __init__(self, connection: FakeConnection) -> None:
        super().__init__()
        self._connection = connection

    def connect(self, dsn: str):
        self._connection.last_dsn = dsn
        return self._connection


class PostgresPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._original_psycopg = sys.modules.get("psycopg")

    def tearDown(self) -> None:
        if self._original_psycopg is None:
            sys.modules.pop("psycopg", None)
        else:
            sys.modules["psycopg"] = self._original_psycopg
        sys.modules.pop("test_service_persistence_postgres", None)

    def test_postgres_metadata_store_supports_upsert_get_and_list_namespace(self) -> None:
        connection = FakeConnection()
        sys.modules["psycopg"] = FakePsycopgModule(connection)
        persistence_module = _load_module("packages/agent-runtime/persistence.py", "test_service_persistence_postgres")

        self.assertTrue(hasattr(persistence_module, "PostgresMetadataStore"))
        store = persistence_module.PostgresMetadataStore("postgresql://example/db")
        first = store.upsert(namespace="verification_runs", key="b", payload={"status": "pass"})
        second = store.upsert(namespace="verification_runs", key="a", payload={"status": "queued"})

        record = store.get(namespace="verification_runs", key="b")
        records = store.list_namespace(namespace="verification_runs")

        self.assertEqual(first.namespace, "verification_runs")
        self.assertEqual(second.key, "a")
        self.assertEqual(record.payload, {"status": "pass"})
        self.assertIsInstance(record.updated_at, str)
        self.assertEqual([item.key for item in records], ["a", "b"])
        self.assertTrue(all(isinstance(item.updated_at, str) for item in records))
        self.assertEqual(connection.commit_calls, 5)
        self.assertEqual(connection.close_calls, 5)
        self.assertIn("payload JSONB", connection.executed[0][0])
        self.assertIn("updated_at TIMESTAMPTZ", connection.executed[0][0])
        self.assertIn("CREATE INDEX IF NOT EXISTS idx_runtime_metadata_namespace", connection.executed[1][0])
        self.assertIn("ON runtime_metadata(namespace)", connection.executed[1][0])
        self.assertIn("%s::jsonb", connection.executed[2][0])
        self.assertIn("%s::timestamptz", connection.executed[2][0])
        self.assertIn("%s::jsonb", connection.executed[3][0])
        self.assertIn("%s::timestamptz", connection.executed[3][0])
        self.assertIn("payload::text", connection.executed[4][0])
        self.assertIn("updated_at::text", connection.executed[4][0])
        self.assertIn("payload::text", connection.executed[5][0])
        self.assertIn("updated_at::text", connection.executed[5][0])
        self.assertEqual(connection.last_dsn, "postgresql://example/db")

    def test_postgres_metadata_store_requires_dsn_and_psycopg(self) -> None:
        persistence_module = _load_module("packages/agent-runtime/persistence.py", "test_service_persistence_postgres")
        persistence_module.psycopg = None

        with self.assertRaises(ValueError):
            persistence_module.PostgresMetadataStore("")

        with self.assertRaises(RuntimeError):
            persistence_module.PostgresMetadataStore("postgresql://example/db")


if __name__ == "__main__":
    unittest.main()
