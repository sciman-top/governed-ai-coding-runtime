import importlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class RuntimeRootsTests(unittest.TestCase):
    def test_runtime_roots_default_to_machine_local_mode(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_roots")

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir) / "repo"
            repo_root.mkdir()
            roots = module.resolve_runtime_roots(repo_root=repo_root)

            self.assertFalse(roots.compatibility_mode)
            self.assertNotEqual(Path(roots.runtime_root), (repo_root / ".runtime").resolve())
            self.assertTrue(Path(roots.tasks_root).as_posix().endswith("/tasks"))
            self.assertTrue(Path(roots.workspaces_root).as_posix().endswith("/workspaces"))

    def test_runtime_roots_compatibility_mode_uses_repo_runtime(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_roots")

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir) / "repo"
            repo_root.mkdir()
            roots = module.resolve_runtime_roots(repo_root=repo_root, compatibility_mode=True)

            self.assertTrue(roots.compatibility_mode)
            self.assertEqual(Path(roots.runtime_root), (repo_root / ".runtime").resolve())

    def test_ensure_runtime_roots_creates_expected_directories(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_roots")

        with tempfile.TemporaryDirectory() as tmp_dir:
            runtime_root = Path(tmp_dir) / "machine-runtime"
            roots = module.resolve_runtime_roots(repo_root=ROOT, runtime_root=runtime_root)
            module.ensure_runtime_roots(roots)

            self.assertTrue(Path(roots.runtime_root).exists())
            self.assertTrue(Path(roots.tasks_root).exists())
            self.assertTrue(Path(roots.artifacts_root).exists())
            self.assertTrue(Path(roots.replay_root).exists())
            self.assertTrue(Path(roots.workspaces_root).exists())

    def test_migration_payload_records_source_target_and_rollback(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_roots")

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir) / "repo"
            repo_root.mkdir()
            target = Path(tmp_dir) / "machine-runtime"
            migration = module.build_runtime_root_migration(repo_root=repo_root, target_runtime_root=target)

            self.assertEqual(migration["source_runtime_root"], (repo_root / ".runtime").resolve().as_posix())
            self.assertEqual(migration["target_runtime_root"], target.resolve().as_posix())
            self.assertEqual(migration["rollback_runtime_root"], (repo_root / ".runtime").resolve().as_posix())
            self.assertTrue(migration["compatible"])


if __name__ == "__main__":
    unittest.main()
