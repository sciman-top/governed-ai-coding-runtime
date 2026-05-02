import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


def _load_run_governed_task_module():
    module_path = ROOT / "scripts" / "run-governed-task.py"
    spec = importlib.util.spec_from_file_location("run_governed_task_cli_test_module", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RUN_GOVERNED_TASK = _load_run_governed_task_module()


class RunGovernedTaskCliTests(unittest.TestCase):
    def test_verify_attachment_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run-governed-task.py", "verify-attachment", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Execute declared verification gates", completed.stdout)

    def test_run_default_profile_executes_repo_local_quick_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            RUN_GOVERNED_TASK._configure_runtime_roots(
                runtime_root=str(Path(tmp_dir) / "runtime"),
                compat_runtime_root=False,
            )
            payload = RUN_GOVERNED_TASK.run_task(
                task_id="task-cli-default-profile",
                goal="CLI default profile smoke",
                scope="runtime cli",
                repo="governed-ai-coding-runtime",
                profile_path=str(ROOT / "schemas" / "examples" / "repo-profile" / "governed-ai-coding-runtime.example.json"),
                mode="quick",
            )

            self.assertEqual(payload["total_tasks"], 1)
            self.assertEqual(payload["tasks"][0]["task_id"], "task-cli-default-profile")
            self.assertEqual(payload["tasks"][0]["state"], "delivered")

    def test_verify_attachment_executes_declared_target_repo_gates(self) -> None:
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

            payload = RUN_GOVERNED_TASK.run_attachment_verification(
                attachment_root=str(target_repo),
                attachment_runtime_state_root=str(runtime_state_root),
                mode="quick",
                task_id="task-verify-attachment",
                run_id="run-verify-attachment",
            )

            self.assertEqual(payload["repo_id"], "target")
            self.assertEqual(payload["gate_order"], ["test", "contract"])
            self.assertEqual(payload["results"], {"test": "pass", "contract": "pass"})
            for artifact_ref in payload["result_artifact_refs"].values():
                self.assertTrue((runtime_state_root / artifact_ref).exists(), artifact_ref)

    def test_verify_attachment_supports_l2_layered_mode(self) -> None:
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

            payload = RUN_GOVERNED_TASK.run_attachment_verification(
                attachment_root=str(target_repo),
                attachment_runtime_state_root=str(runtime_state_root),
                mode="l2",
                task_id="task-verify-attachment-l2",
                run_id="run-verify-attachment-l2",
            )

            self.assertEqual(payload["repo_id"], "target")
            self.assertEqual(payload["mode"], "l2")
            self.assertEqual(payload["gate_order"], ["build", "test", "contract"])
            self.assertEqual(payload["results"], {"build": "pass", "test": "pass", "contract": "pass"})

    def test_verify_attachment_enforces_required_canonical_entrypoint_policy(self) -> None:
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

            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["required_entrypoint_policy"]["current_mode"] = "targeted_enforced"
            profile_path.write_text(json.dumps(profile, indent=2, sort_keys=True), encoding="utf-8")

            with self.assertRaises(RUN_GOVERNED_TASK.EntrypointPolicyViolation) as blocked:
                RUN_GOVERNED_TASK.run_attachment_verification(
                    attachment_root=str(target_repo),
                    attachment_runtime_state_root=str(runtime_state_root),
                    mode="quick",
                    task_id="task-verify-attachment-policy",
                    run_id="run-verify-attachment-policy",
                )
            self.assertTrue(blocked.exception.evaluation["blocked"])

            allowed_payload = RUN_GOVERNED_TASK.run_attachment_verification(
                attachment_root=str(target_repo),
                attachment_runtime_state_root=str(runtime_state_root),
                mode="quick",
                task_id="task-verify-attachment-policy",
                run_id="run-verify-attachment-policy",
                entrypoint_id="runtime-flow",
            )
            self.assertEqual(allowed_payload["results"], {"test": "pass", "contract": "pass"})
            self.assertFalse(allowed_payload["entrypoint_policy"]["blocked"])

    def test_govern_attachment_write_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run-governed-task.py", "govern-attachment-write", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Evaluate attached repo write governance", completed.stdout)

    def test_decide_attachment_write_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run-governed-task.py", "decide-attachment-write", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Approve or reject an attached write request", completed.stdout)

    def test_execute_attachment_write_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run-governed-task.py", "execute-attachment-write", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Execute an approved attached write request", completed.stdout)

    def test_status_json_reports_runtime_roots_and_runtime_root_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runtime_root = Path(tmp_dir) / "machine-runtime"
            RUN_GOVERNED_TASK._configure_runtime_roots(
                runtime_root=str(runtime_root),
                compat_runtime_root=False,
            )
            with (
                mock.patch.object(RUN_GOVERNED_TASK, "summarize_codex_capability_readiness", return_value=object()),
                mock.patch.object(
                    RUN_GOVERNED_TASK,
                    "codex_capability_readiness_to_dict",
                    return_value={"status": "ready", "adapter_tier": "test"},
                ),
            ):
                payload = RUN_GOVERNED_TASK.snapshot_payload()
            self.assertEqual(payload["runtime_roots"]["runtime_root"], runtime_root.resolve().as_posix())
            self.assertEqual(payload["runtime_roots"]["compatibility_mode"], False)
            self.assertIn("codex_capability", payload)
            self.assertIn("status", payload["codex_capability"])


if __name__ == "__main__":
    unittest.main()
