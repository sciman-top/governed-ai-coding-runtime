import sys
import tempfile
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class ReplayTests(unittest.TestCase):
    def test_replay_reference_captures_failure_signature_and_artifacts(self) -> None:
        artifact_store = importlib.import_module("governed_ai_coding_runtime_contracts.artifact_store")
        replay = importlib.import_module("governed_ai_coding_runtime_contracts.replay")

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = artifact_store.LocalArtifactStore(Path(tmp_dir))
            artifact = store.write_text(
                task_id="task-failed",
                run_id="run-failed",
                kind="verification-output",
                label="test-log",
                content="tests failed",
            )

            reference = replay.build_replay_reference(
                task_id="task-failed",
                run_id="run-failed",
                failure_reason="unit test failure",
                artifact_refs=[artifact.relative_path],
                verification_artifact_refs=["artifacts/task-failed/run-failed/verification-output/test-log.txt"],
            )

            self.assertEqual(reference.failure_signature.failure_reason, "unit test failure")
            self.assertEqual(reference.artifact_refs, [artifact.relative_path])
            self.assertEqual(reference.run_id, "run-failed")


if __name__ == "__main__":
    unittest.main()
