import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_module():
    path = ROOT / "packages" / "agent-runtime" / "persistence.py"
    spec = importlib.util.spec_from_file_location("test_service_persistence_data_plane", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["test_service_persistence_data_plane"] = module
    spec.loader.exec_module(module)
    return module


class DataPlanePersistenceTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("test_service_persistence_data_plane", None)

    def test_sqlite_store_records_migration_and_exports_replay_bundle(self) -> None:
        persistence = _load_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = persistence.SqliteMetadataStore(Path(tmp_dir) / "runtime.db")
            store.upsert(namespace="tasks", key="task-1", payload={"state": "ready"})
            store.upsert(namespace="artifacts", key="artifact-1", payload={"ref": "artifacts/task/run/evidence.json"})
            store.upsert(namespace="replay", key="replay-1", payload={"command": "python -m unittest"})
            store.upsert(namespace="provenance", key="attestation-1", payload={"verification_status": "verified"})

            bundle = store.export_replay_bundle(namespaces=["tasks", "artifacts", "replay", "provenance"])

            self.assertIn("001_runtime_metadata", bundle["migrations"])
            self.assertEqual(bundle["namespaces"]["tasks"][0]["payload"], {"state": "ready"})
            self.assertEqual(bundle["namespaces"]["provenance"][0]["payload"]["verification_status"], "verified")

    def test_sqlite_store_prune_returns_rollback_records_and_can_restore(self) -> None:
        persistence = _load_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = persistence.SqliteMetadataStore(Path(tmp_dir) / "runtime.db")
            store.upsert(namespace="evidence", key="old", payload={"ref": "old"})
            store.upsert(namespace="evidence", key="new", payload={"ref": "new"})

            result = store.prune_namespace(namespace="evidence", retain_latest=1)

            self.assertEqual(result.pruned_keys, ["old"])
            self.assertEqual([record.key for record in result.rollback_records], ["old"])
            self.assertIsNone(store.get(namespace="evidence", key="old"))

            store.restore(result.rollback_records[0])

            self.assertEqual(store.get(namespace="evidence", key="old").payload, {"ref": "old"})


if __name__ == "__main__":
    unittest.main()
