import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class AttachedRepoE2ETests(unittest.TestCase):
    def test_runtime_check_executes_attached_write_e2e_with_handoff_and_replay_refs(self) -> None:
        from governed_ai_coding_runtime_contracts.repo_attachment import attach_target_repo

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "target"
            target_repo.mkdir()
            runtime_state_root = workspace / "runtime-state" / "target"
            attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_state_root),
                repo_id="target",
                display_name="Target",
                primary_language="python",
                build_command="cmd /c exit 0",
                test_command="cmd /c exit 0",
                contract_command="cmd /c exit 0",
                adapter_preference="process_bridge",
            )

            target_path = "docs/e2e-probe.txt"
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    "scripts/runtime-check.ps1",
                    "-AttachmentRoot",
                    str(target_repo),
                    "-AttachmentRuntimeStateRoot",
                    str(runtime_state_root),
                    "-Mode",
                    "quick",
                    "-TaskId",
                    "task-attached-e2e",
                    "-RunId",
                    "run-attached-e2e",
                    "-CommandId",
                    "cmd-attached-e2e",
                    "-WriteTargetPath",
                    target_path,
                    "-WriteTier",
                    "medium",
                    "-WriteToolName",
                    "write_file",
                    "-RollbackReference",
                    f"git checkout -- {target_path}",
                    "-WriteContent",
                    "attached e2e write",
                    "-ExecuteWriteFlow",
                    "-Json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["overall_status"], "pass")
            self.assertEqual(payload["write_execute"]["execution_status"], "executed")
            self.assertTrue(payload["write_execute"]["handoff_ref"])
            self.assertTrue(payload["write_execute"]["replay_ref"])
            self.assertTrue((runtime_state_root / payload["write_execute"]["handoff_ref"]).exists())
            self.assertTrue((runtime_state_root / payload["write_execute"]["replay_ref"]).exists())
            self.assertEqual((target_repo / target_path).read_text(encoding="utf-8"), "attached e2e write")


if __name__ == "__main__":
    unittest.main()
