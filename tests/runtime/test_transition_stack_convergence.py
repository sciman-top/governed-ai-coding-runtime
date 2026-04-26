import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_transition_script():
    script_path = ROOT / "scripts" / "verify-transition-stack-convergence.py"
    spec = importlib.util.spec_from_file_location("verify_transition_stack_convergence_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_transition_stack_convergence_script"] = module
    spec.loader.exec_module(module)
    return module


class TransitionStackConvergenceTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("verify_transition_stack_convergence_script", None)

    def test_transition_stack_policy_succeeds_for_repo(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-transition-stack-convergence.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["policy_id"], "default-runtime-transition-stack")
        self.assertEqual(payload["observed_modules"], [])
        self.assertTrue(payload["runtime_guards"]["json_schema_truth"])

    def test_transition_stack_policy_fails_closed_for_unapproved_import(self) -> None:
        module = _load_transition_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "apps").mkdir(parents=True)
            (repo_root / "apps" / "api.py").write_text("import fastapi\n", encoding="utf-8")
            policy_path = self._write_policy(repo_root, adoption_status="not_present")

            with self.assertRaisesRegex(ValueError, "without active boundary"):
                module.assert_transition_stack_convergence(repo_root=repo_root, policy_path=policy_path)

    def test_transition_stack_policy_allows_active_boundary_import_with_refs(self) -> None:
        module = _load_transition_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "apps").mkdir(parents=True)
            (repo_root / "apps" / "api.py").write_text("import fastapi\n", encoding="utf-8")
            policy_path = self._write_policy(repo_root, adoption_status="active_boundary")

            result = module.assert_transition_stack_convergence(repo_root=repo_root, policy_path=policy_path)

            self.assertEqual(result["observed_modules"], ["fastapi"])
            self.assertEqual(result["inactive_observed_modules"], [])

    def test_verify_repo_contract_runs_transition_stack_policy(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/verify-repo.ps1",
                "-Check",
                "Contract",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("OK transition-stack-convergence", completed.stdout)

    def _write_policy(self, repo_root: Path, *, adoption_status: str) -> Path:
        for path in [
            "docs/evidence.md",
            "apps/api.py",
            "tests/service/test_control_plane_cli.py",
            "tests/runtime/test_run_governed_task_service_wrapper.py",
            "packages/observability/runtime_tracing.py",
            "tests/service/test_session_api.py",
            "scripts/run-governed-task.py",
        ]:
            target = repo_root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text("", encoding="utf-8")
        policy = {
            "schema_version": "1.0",
            "policy_id": "test-transition-stack",
            "status": "enforced",
            "components": [
                {
                    "component_id": "fastapi-control-plane",
                    "module_roots": ["fastapi"],
                    "adoption_status": adoption_status,
                    "owner_boundary": "control-plane API routes",
                    "allowed_when": "active service boundary exists",
                    "implementation_refs": ["apps/api.py"],
                    "evidence_refs": ["docs/evidence.md"],
                    "rollback_ref": "git revert test slice",
                }
            ],
            "runtime_guards": {
                "local_mode": {
                    "filesystem_allowed": True,
                    "sqlite_allowed": True,
                },
                "postgres_scope": {
                    "requires_service_metadata_pressure": True,
                    "requires_rollback": True,
                },
                "json_schema_truth": True,
                "pydantic_scope": "boundary only",
                "cli_api_parity_tests": [
                    "tests/service/test_control_plane_cli.py",
                    "tests/runtime/test_run_governed_task_service_wrapper.py",
                ],
                "tracing_hook_refs": [
                    "packages/observability/runtime_tracing.py",
                    "tests/service/test_session_api.py",
                ],
                "wrapper_drift_guard": {
                    "path": "scripts/run-governed-task.py",
                    "forbidden_tokens": ["build_session_bridge_command("],
                },
            },
            "evidence_refs": ["docs/evidence.md"],
            "rollback_ref": "git revert test policy",
        }
        policy_path = repo_root / "policy.json"
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        return policy_path


if __name__ == "__main__":
    unittest.main()
