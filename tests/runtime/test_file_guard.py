import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]


def _load_contract_file_guard():
    script_path = ROOT / "packages" / "contracts" / "src" / "governed_ai_coding_runtime_contracts" / "file_guard.py"
    spec = importlib.util.spec_from_file_location("contract_file_guard_module", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["contract_file_guard_module"] = module
    spec.loader.exec_module(module)
    return module


def _load_service_artifact_store():
    script_path = ROOT / "packages" / "agent-runtime" / "artifact_store.py"
    spec = importlib.util.spec_from_file_location("service_artifact_store_module", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["service_artifact_store_module"] = module
    spec.loader.exec_module(module)
    return module


class FileGuardAtomicWriteTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("contract_file_guard_module", None)
        sys.modules.pop("service_artifact_store_module", None)

    def test_contract_atomic_write_retries_transient_permission_error(self) -> None:
        module = _load_contract_file_guard()

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "state.json"
            real_replace = module.os.replace
            attempts = {"count": 0}

            def flaky_replace(source, target):
                attempts["count"] += 1
                if attempts["count"] == 1:
                    raise PermissionError(5, "access denied", str(target))
                return real_replace(source, target)

            with (
                mock.patch.object(module.os, "replace", side_effect=flaky_replace),
                mock.patch.object(module.time, "sleep", return_value=None),
            ):
                module.atomic_write_text(path, '{"status":"ok"}')

            self.assertEqual('{"status":"ok"}', path.read_text(encoding="utf-8"))
            self.assertEqual(2, attempts["count"])

    def test_service_artifact_store_retries_transient_permission_error(self) -> None:
        module = _load_service_artifact_store()

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = module.FilesystemArtifactStore(Path(tmp_dir) / "artifacts")
            real_replace = module.os.replace
            attempts = {"count": 0}

            def flaky_replace(source, target):
                attempts["count"] += 1
                if attempts["count"] == 1:
                    raise PermissionError(5, "access denied", str(target))
                return real_replace(source, target)

            with (
                mock.patch.object(module.os, "replace", side_effect=flaky_replace),
                mock.patch.object(module.time, "sleep", return_value=None),
            ):
                artifact = store.write_text(relative_path="logs/run.txt", content="hello")

            self.assertEqual("hello", (store.root / artifact.relative_path).read_text(encoding="utf-8"))
            self.assertEqual(2, attempts["count"])


if __name__ == "__main__":
    unittest.main()
