import sys
import tempfile
import unittest
import os
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class ArtifactStoreTests(unittest.TestCase):
    def test_artifact_store_persists_text_output_under_task_and_run(self) -> None:
        artifact_store = importlib.import_module("governed_ai_coding_runtime_contracts.artifact_store")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = artifact_store.LocalArtifactStore(Path(tmp_dir))
            artifact = store.write_text(
                task_id="task-001",
                run_id="run-001",
                kind="command-output",
                label="build-log",
                content="build succeeded",
            )

            self.assertTrue((Path(tmp_dir) / artifact.relative_path).exists())
            self.assertEqual(artifact.kind, "command-output")
            self.assertEqual(artifact.task_id, "task-001")
            self.assertEqual(artifact.run_id, "run-001")
            self.assertFalse(artifact.risky)

    def test_artifact_store_flags_risky_release_adjacent_outputs(self) -> None:
        artifact_store = importlib.import_module("governed_ai_coding_runtime_contracts.artifact_store")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = artifact_store.LocalArtifactStore(Path(tmp_dir))
            artifact = store.write_text(
                task_id="task-002",
                run_id="run-002",
                kind="release-output",
                label="publish-report",
                content="publishing package",
            )

            self.assertTrue(artifact.risky)
            self.assertEqual(artifact.risk_classification, "release_adjacent")

    def test_release_adjacent_json_requires_provenance_or_waiver(self) -> None:
        artifact_store = importlib.import_module("governed_ai_coding_runtime_contracts.artifact_store")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = artifact_store.LocalArtifactStore(Path(tmp_dir))

            with self.assertRaisesRegex(ValueError, "provenance or waiver_ref"):
                store.write_release_json(
                    task_id="task-release",
                    run_id="run-release",
                    kind="release-output",
                    label="package-manifest",
                    payload={"status": "ready"},
                )

    def test_release_adjacent_json_writes_provenance_reference(self) -> None:
        artifact_store = importlib.import_module("governed_ai_coding_runtime_contracts.artifact_store")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = artifact_store.LocalArtifactStore(Path(tmp_dir))
            artifact = store.write_release_json(
                task_id="task-release",
                run_id="run-release",
                kind="release-output",
                label="package-manifest",
                payload={"status": "ready"},
                provenance={"attestation_id": "attestation-1", "verification_status": "verified"},
            )

            self.assertTrue(artifact.risky)
            self.assertTrue(artifact.provenance_ref)
            self.assertTrue((Path(tmp_dir) / artifact.provenance_ref).exists())

    def test_release_adjacent_json_accepts_explicit_waiver_reference(self) -> None:
        artifact_store = importlib.import_module("governed_ai_coding_runtime_contracts.artifact_store")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = artifact_store.LocalArtifactStore(Path(tmp_dir))
            artifact = store.write_release_json(
                task_id="task-release",
                run_id="run-release",
                kind="release-output",
                label="package-manifest",
                payload={"status": "ready"},
                waiver_ref="docs/waivers/release-provenance.md",
            )

            self.assertEqual(artifact.waiver_ref, "docs/waivers/release-provenance.md")
            self.assertIsNone(artifact.provenance_ref)

    def test_artifact_store_rejects_symlinked_artifact_path_outside_root(self) -> None:
        artifact_store = importlib.import_module("governed_ai_coding_runtime_contracts.artifact_store")

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "store"
            outside = Path(tmp_dir) / "outside.txt"
            outside.write_text("before", encoding="utf-8")
            symlink_path = root / "artifacts" / "task-003" / "run-003" / "command-output" / "build-log.txt"
            symlink_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.symlink(outside, symlink_path)
            except (OSError, NotImplementedError):
                self.skipTest("file symlinks are not available in this environment")

            store = artifact_store.LocalArtifactStore(root)
            with self.assertRaisesRegex(ValueError, "artifact path"):
                store.write_text(
                    task_id="task-003",
                    run_id="run-003",
                    kind="command-output",
                    label="build-log",
                    content="after",
                )

            self.assertEqual(outside.read_text(encoding="utf-8"), "before")


if __name__ == "__main__":
    unittest.main()
