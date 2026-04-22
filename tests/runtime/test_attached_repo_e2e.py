import json
import os
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
            self.assertEqual(payload["dependency_baseline"]["status"], "pass")
            self.assertEqual(payload["write_execute"]["execution_status"], "executed")
            self.assertTrue(payload["write_execute"]["handoff_ref"])
            self.assertTrue(payload["write_execute"]["replay_ref"])
            self.assertEqual(payload["summary"]["continuation_id"], payload["write_execute"]["continuation_id"])
            self.assertEqual(payload["summary"]["session_id"], payload["write_execute"]["session_identity"]["session_id"])
            self.assertEqual(payload["summary"]["resume_id"], payload["write_execute"]["session_identity"]["resume_id"])
            self.assertTrue(payload["live_loop"]["session_identity_continuity"])
            self.assertTrue(payload["live_loop"]["resume_identity_continuity"])
            self.assertTrue(payload["live_loop"]["continuation_continuity"])
            self.assertTrue(payload["live_loop"]["evidence_linkage_complete"])
            self.assertIn(payload["live_loop"]["flow_kind"], {"live_attach", "process_bridge", "manual_handoff"})
            self.assertIn(payload["live_loop"]["closure_state"], {"live_closure_ready", "fallback_explicit"})
            if payload["live_loop"]["flow_kind"] != "live_attach":
                self.assertTrue(payload["live_loop"]["fallback_explicit"])
            self.assertTrue(payload["write_status"])
            self.assertTrue(payload["inspect_evidence"])
            self.assertTrue(payload["inspect_handoff"])
            self.assertIn(payload["write_execute"]["handoff_ref"], payload["live_loop"]["runtime_refs"])
            self.assertIn(payload["write_execute"]["replay_ref"], payload["live_loop"]["runtime_refs"])
            self.assertTrue((runtime_state_root / payload["write_execute"]["handoff_ref"]).exists())
            self.assertTrue((runtime_state_root / payload["write_execute"]["replay_ref"]).exists())
            self.assertEqual((target_repo / target_path).read_text(encoding="utf-8"), "attached e2e write")

    def test_runtime_check_default_write_tool_executes_attached_write(self) -> None:
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

            target_path = "docs/e2e-default-tool-probe.txt"
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
                    "task-attached-default-tool",
                    "-RunId",
                    "run-attached-default-tool",
                    "-CommandId",
                    "cmd-attached-default-tool",
                    "-WriteTargetPath",
                    target_path,
                    "-WriteTier",
                    "low",
                    "-RollbackReference",
                    f"git checkout -- {target_path}",
                    "-WriteContent",
                    "attached default tool write",
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
            self.assertEqual(payload["summary"]["continuation_id"], payload["write_execute"]["continuation_id"])
            self.assertTrue(payload["live_loop"]["session_identity_continuity"])
            self.assertTrue(payload["live_loop"]["continuation_continuity"])
            self.assertTrue(payload["live_loop"]["evidence_linkage_complete"])
            self.assertIn(payload["live_loop"]["flow_kind"], {"live_attach", "process_bridge", "manual_handoff"})
            self.assertIn(payload["live_loop"]["closure_state"], {"live_closure_ready", "fallback_explicit"})
            self.assertEqual((target_repo / target_path).read_text(encoding="utf-8"), "attached default tool write")

    def test_runtime_check_marks_fallback_explicit_when_codex_probe_is_blocked(self) -> None:
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

            target_path = "docs/e2e-fallback-probe.txt"
            env = os.environ.copy()
            env["GOVERNED_RUNTIME_CODEX_BIN"] = "__missing_codex_binary_for_fallback_test__"
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
                    "task-attached-fallback",
                    "-RunId",
                    "run-attached-fallback",
                    "-CommandId",
                    "cmd-attached-fallback",
                    "-WriteTargetPath",
                    target_path,
                    "-WriteTier",
                    "low",
                    "-RollbackReference",
                    f"git checkout -- {target_path}",
                    "-WriteContent",
                    "attached fallback write",
                    "-ExecuteWriteFlow",
                    "-Json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
                env=env,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["overall_status"], "pass")
            self.assertEqual(payload["write_execute"]["execution_status"], "executed")
            self.assertTrue(payload["live_loop"]["fallback_explicit"])
            self.assertEqual(payload["live_loop"]["closure_state"], "fallback_explicit")
            self.assertIn(payload["live_loop"]["flow_kind"], {"process_bridge", "manual_handoff"})
            self.assertTrue(payload["live_loop"]["fallback_reason"])
            self.assertTrue(payload["live_loop"]["session_identity_continuity"])
            self.assertTrue(payload["live_loop"]["continuation_continuity"])
            self.assertTrue(payload["live_loop"]["evidence_linkage_complete"])
            self.assertEqual(payload["summary"]["flow_kind"], payload["live_loop"]["flow_kind"])
            self.assertEqual((target_repo / target_path).read_text(encoding="utf-8"), "attached fallback write")

    def test_runtime_check_preflight_blocks_denied_write_and_emits_retry_action(self) -> None:
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
                    "task-attached-preflight",
                    "-RunId",
                    "run-attached-preflight",
                    "-CommandId",
                    "cmd-attached-preflight",
                    "-WriteTargetPath",
                    "secrets/prod.env",
                    "-WriteTier",
                    "medium",
                    "-WriteToolName",
                    "write_file",
                    "-RollbackReference",
                    "git diff -- secrets/prod.env",
                    "-WriteContent",
                    "should not write",
                    "-ExecuteWriteFlow",
                    "-Json",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertNotEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["overall_status"], "fail")
            self.assertEqual(payload["write_governance"]["policy_status"], "deny")
            self.assertTrue(payload["write_preflight"]["blocked"])
            self.assertTrue(payload["write_preflight"]["retry_command"])
            self.assertIsNone(payload["write_execute"])
            self.assertTrue(payload["next_actions"])

    def test_runtime_check_fails_when_target_repo_dependency_baseline_is_missing(self) -> None:
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
            (target_repo / ".governed-ai" / "dependency-baseline.json").unlink(missing_ok=True)

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
                    "task-attached-missing-baseline",
                    "-RunId",
                    "run-attached-missing-baseline",
                    "-CommandId",
                    "cmd-attached-missing-baseline",
                    "-Json",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertNotEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["overall_status"], "fail")
            baseline_steps = [step for step in payload["steps"] if step["label"] == "dependency-baseline-target-repo"]
            self.assertEqual(len(baseline_steps), 1)
            self.assertNotEqual(baseline_steps[0]["exit_code"], 0)
            self.assertTrue(payload["next_actions"])
            self.assertIn("create or refresh target repo baseline metadata", payload["next_actions"][0])


if __name__ == "__main__":
    unittest.main()
