import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class RepoAttachmentBindingTests(unittest.TestCase):
    def test_repo_attachment_api_exists(self) -> None:
        module = self._module()
        if not hasattr(module, "RepoAttachmentBinding"):
            self.fail("RepoAttachmentBinding is not implemented")
        if not hasattr(module, "build_repo_attachment_binding"):
            self.fail("build_repo_attachment_binding is not implemented")
        if not hasattr(module, "is_machine_local_state_path"):
            self.fail("is_machine_local_state_path is not implemented")
        if not hasattr(module, "attach_target_repo"):
            self.fail("attach_target_repo is not implemented")
        if not hasattr(module, "validate_light_pack"):
            self.fail("validate_light_pack is not implemented")

    def test_binding_records_repo_inputs_and_machine_local_state(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as workspace:
            repo_root, runtime_root = self._make_workspace(Path(workspace))

            binding = module.build_repo_attachment_binding(
                binding_id="binding-python-service",
                target_repo_root=str(repo_root),
                repo_profile_ref=".governed-ai/repo-profile.json",
                light_pack_path=".governed-ai/light-pack.json",
                runtime_state_root=str(runtime_root),
                adapter_preference="native_attach",
                gate_profile="default",
                doctor_posture="healthy",
            )

            self.assertEqual(binding.schema_version, "1.0")
            self.assertEqual(binding.binding_id, "binding-python-service")
            self.assertEqual(Path(binding.target_repo_root), repo_root.resolve())
            self.assertEqual(Path(binding.repo_profile_ref), (repo_root / ".governed-ai" / "repo-profile.json").resolve())
            self.assertEqual(Path(binding.light_pack_path), (repo_root / ".governed-ai" / "light-pack.json").resolve())
            self.assertEqual(Path(binding.runtime_state_root), runtime_root.resolve())
            self.assertEqual(binding.adapter_preference, "native_attach")
            self.assertEqual(binding.gate_profile, "default")
            self.assertEqual(binding.doctor_posture, "healthy")

            self.assertEqual(
                set(binding.mutable_state_roots),
                {"tasks", "runs", "approvals", "artifacts", "replay"},
            )
            for state_root in binding.mutable_state_roots.values():
                state_path = Path(state_root)
                self.assertTrue(self._is_under(state_path, runtime_root))
                self.assertFalse(self._is_under(state_path, repo_root))
                self.assertTrue(module.is_machine_local_state_path(state_path, binding))

    def test_repo_local_declarations_cannot_escape_target_repo(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as workspace:
            repo_root, runtime_root = self._make_workspace(Path(workspace))
            outside_profile = Path(workspace) / "outside-repo-profile.json"
            outside_profile.write_text("{}", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "repo_profile_ref"):
                module.build_repo_attachment_binding(
                    binding_id="binding-escape",
                    target_repo_root=str(repo_root),
                    repo_profile_ref=str(outside_profile),
                    light_pack_path=".governed-ai/light-pack.json",
                    runtime_state_root=str(runtime_root),
                    adapter_preference="native_attach",
                    gate_profile="default",
                    doctor_posture="healthy",
                )

    def test_runtime_state_root_cannot_live_inside_target_repo(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as workspace:
            repo_root, _runtime_root = self._make_workspace(Path(workspace))

            with self.assertRaisesRegex(ValueError, "runtime_state_root"):
                module.build_repo_attachment_binding(
                    binding_id="binding-local-state",
                    target_repo_root=str(repo_root),
                    repo_profile_ref=".governed-ai/repo-profile.json",
                    light_pack_path=".governed-ai/light-pack.json",
                    runtime_state_root=str(repo_root / ".runtime"),
                    adapter_preference="native_attach",
                    gate_profile="default",
                    doctor_posture="healthy",
                )

    def test_mutable_state_roots_cannot_live_inside_target_repo(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as workspace:
            repo_root, runtime_root = self._make_workspace(Path(workspace))

            with self.assertRaisesRegex(ValueError, "tasks"):
                module.build_repo_attachment_binding(
                    binding_id="binding-bad-mutable-state",
                    target_repo_root=str(repo_root),
                    repo_profile_ref=".governed-ai/repo-profile.json",
                    light_pack_path=".governed-ai/light-pack.json",
                    runtime_state_root=str(runtime_root),
                    adapter_preference="native_attach",
                    gate_profile="default",
                    doctor_posture="healthy",
                    mutable_state_roots={
                        "tasks": str(repo_root / ".runtime" / "tasks"),
                        "runs": str(runtime_root / "runs"),
                        "approvals": str(runtime_root / "approvals"),
                        "artifacts": str(runtime_root / "artifacts"),
                        "replay": str(runtime_root / "replay"),
                    },
                )

    def test_schema_and_python_required_fields_and_enums_match(self) -> None:
        module = self._module()
        schema = json.loads(
            (ROOT / "schemas" / "jsonschema" / "repo-attachment-binding.schema.json").read_text(encoding="utf-8")
        )

        dataclass_fields = {field.name for field in fields(module.RepoAttachmentBinding)}
        for required_field in schema["required"]:
            self.assertIn(required_field, dataclass_fields)

        self.assertEqual(set(schema["properties"]["doctor_posture"]["enum"]), module.DOCTOR_POSTURES)
        self.assertEqual(set(schema["properties"]["adapter_preference"]["enum"]), module.ADAPTER_PREFERENCES)
        self.assertEqual(
            set(schema["properties"]["mutable_state_roots"]["required"]),
            module.MUTABLE_STATE_ROOT_KEYS,
        )

    def test_schema_accepts_valid_binding_payload(self) -> None:
        payload = {
            "schema_version": "1.0",
            "binding_id": "binding-python-service",
            "target_repo_root": "D:/repos/python-service",
            "repo_profile_ref": "D:/repos/python-service/.governed-ai/repo-profile.json",
            "light_pack_path": "D:/repos/python-service/.governed-ai/light-pack.json",
            "runtime_state_root": "D:/runtime/state/python-service",
            "mutable_state_roots": {
                "tasks": "D:/runtime/state/python-service/tasks",
                "runs": "D:/runtime/state/python-service/runs",
                "approvals": "D:/runtime/state/python-service/approvals",
                "artifacts": "D:/runtime/state/python-service/artifacts",
                "replay": "D:/runtime/state/python-service/replay",
            },
            "adapter_preference": "native_attach",
            "gate_profile": "default",
            "doctor_posture": "healthy",
        }

        self.assertTrue(self._schema_accepts(payload))

    def test_repo_attachment_binding_exports_from_package_root(self) -> None:
        package = importlib.import_module("governed_ai_coding_runtime_contracts")
        if not hasattr(package, "RepoAttachmentBinding"):
            self.fail("RepoAttachmentBinding is not exported from package root")
        if not hasattr(package, "build_repo_attachment_binding"):
            self.fail("build_repo_attachment_binding is not exported from package root")

    def test_attach_target_repo_generates_minimal_declarative_light_pack(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as workspace:
            repo_root = Path(workspace) / "new-target"
            repo_root.mkdir()
            runtime_root = Path(workspace) / "runtime-state" / "new-target"

            result = module.attach_target_repo(
                target_repo_root=str(repo_root),
                runtime_state_root=str(runtime_root),
                repo_id="new-target",
                display_name="New Target",
                primary_language="python",
                build_command="python -m compileall src",
                test_command="python -m unittest discover",
                contract_command="python -m unittest discover -s tests/contracts",
                adapter_preference="manual_handoff",
                gate_profile="default",
            )

            governed_dir = repo_root / ".governed-ai"
            profile_path = governed_dir / "repo-profile.json"
            light_pack_path = governed_dir / "light-pack.json"
            self.assertEqual(result.operation, "created")
            self.assertTrue(profile_path.exists())
            self.assertTrue(light_pack_path.exists())
            self.assertFalse((repo_root / ".runtime").exists())
            self.assertEqual(Path(result.binding.light_pack_path), light_pack_path.resolve())
            self.assertEqual(Path(result.binding.runtime_state_root), runtime_root.resolve())
            self.assertFalse(self._is_under(Path(result.binding.runtime_state_root), repo_root))

            light_pack = json.loads(light_pack_path.read_text(encoding="utf-8"))
            self.assertEqual(light_pack["pack_kind"], "repo_attachment_light_pack")
            self.assertEqual(light_pack["repo_profile_ref"], ".governed-ai/repo-profile.json")
            self.assertNotIn("runtime_code", light_pack)
            self.assertNotIn("task_store", light_pack)

    def test_existing_light_pack_is_validated_without_overwrite(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as workspace:
            repo_root = Path(workspace) / "existing-target"
            governed_dir = repo_root / ".governed-ai"
            governed_dir.mkdir(parents=True)
            runtime_root = Path(workspace) / "runtime-state" / "existing-target"

            (governed_dir / "repo-profile.json").write_text(
                json.dumps(self._minimal_repo_profile("existing-target"), indent=2, sort_keys=True),
                encoding="utf-8",
            )
            light_pack_payload = self._light_pack_payload("existing-target")
            light_pack_payload["custom_note"] = "preserve-existing-light-pack"
            original_light_pack = json.dumps(light_pack_payload, indent=2, sort_keys=True)
            (governed_dir / "light-pack.json").write_text(original_light_pack, encoding="utf-8")

            result = module.attach_target_repo(
                target_repo_root=str(repo_root),
                runtime_state_root=str(runtime_root),
                repo_id="ignored-new-id",
                display_name="Ignored",
                primary_language="python",
                build_command="ignored build",
                test_command="ignored test",
                contract_command="ignored contract",
                adapter_preference="native_attach",
                gate_profile="ignored",
            )

            self.assertEqual(result.operation, "validated")
            self.assertEqual((governed_dir / "light-pack.json").read_text(encoding="utf-8"), original_light_pack)
            self.assertEqual(result.binding.binding_id, "binding-existing-target")

    def test_validate_light_pack_rejects_repo_profile_ref_outside_target_repo(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as workspace:
            repo_root = Path(workspace) / "bad-ref-target"
            governed_dir = repo_root / ".governed-ai"
            governed_dir.mkdir(parents=True)
            runtime_root = Path(workspace) / "runtime-state" / "bad-ref-target"
            outside_profile = Path(workspace) / "outside-profile.json"
            outside_profile.write_text("{}", encoding="utf-8")

            payload = self._light_pack_payload("bad-ref-target")
            payload["repo_profile_ref"] = "../outside-profile.json"
            (governed_dir / "light-pack.json").write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "repo_profile_ref"):
                module.validate_light_pack(
                    target_repo_root=str(repo_root),
                    light_pack_path=".governed-ai/light-pack.json",
                    runtime_state_root=str(runtime_root),
                )

    def test_validate_light_pack_rejects_empty_gate_command(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as workspace:
            repo_root, runtime_root = self._make_light_pack_workspace(Path(workspace), "empty-gate")
            profile = self._minimal_repo_profile("empty-gate")
            profile["build_commands"][0]["command"] = ""
            self._write_light_pack_inputs(repo_root, profile, self._light_pack_payload("empty-gate"))

            with self.assertRaisesRegex(ValueError, "build_commands"):
                module.validate_light_pack(
                    target_repo_root=str(repo_root),
                    light_pack_path=".governed-ai/light-pack.json",
                    runtime_state_root=str(runtime_root),
                )

    def test_validate_light_pack_rejects_escaping_path_scope(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as workspace:
            repo_root, runtime_root = self._make_light_pack_workspace(Path(workspace), "bad-path-scope")
            profile = self._minimal_repo_profile("bad-path-scope")
            profile["path_policies"]["read_allow"] = ["../secrets/**"]
            self._write_light_pack_inputs(repo_root, profile, self._light_pack_payload("bad-path-scope"))

            with self.assertRaisesRegex(ValueError, "path_policies.read_allow"):
                module.validate_light_pack(
                    target_repo_root=str(repo_root),
                    light_pack_path=".governed-ai/light-pack.json",
                    runtime_state_root=str(runtime_root),
                )

    def test_attach_target_repo_cli_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/attach-target-repo.py", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Attach or validate a target repository light pack", completed.stdout)

    def _module(self):
        try:
            return importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")
        except ModuleNotFoundError as exc:
            self.fail(f"repo_attachment module is not implemented: {exc}")

    def _make_workspace(self, workspace: Path) -> tuple[Path, Path]:
        repo_root = workspace / "target-repo"
        governed_dir = repo_root / ".governed-ai"
        governed_dir.mkdir(parents=True)
        (governed_dir / "repo-profile.json").write_text("{}", encoding="utf-8")
        (governed_dir / "light-pack.json").write_text("{}", encoding="utf-8")

        runtime_root = workspace / "machine-runtime-state" / "target-repo"
        runtime_root.mkdir(parents=True)
        return repo_root, runtime_root

    def _make_light_pack_workspace(self, workspace: Path, repo_id: str) -> tuple[Path, Path]:
        repo_root = workspace / repo_id
        (repo_root / ".governed-ai").mkdir(parents=True)
        runtime_root = workspace / "runtime-state" / repo_id
        runtime_root.mkdir(parents=True)
        return repo_root, runtime_root

    def _write_light_pack_inputs(self, repo_root: Path, profile: dict, light_pack: dict) -> None:
        governed_dir = repo_root / ".governed-ai"
        governed_dir.mkdir(parents=True, exist_ok=True)
        (governed_dir / "repo-profile.json").write_text(json.dumps(profile), encoding="utf-8")
        (governed_dir / "light-pack.json").write_text(json.dumps(light_pack), encoding="utf-8")

    def _minimal_repo_profile(self, repo_id: str) -> dict:
        return {
            "schema_version": "1.0",
            "repo_id": repo_id,
            "display_name": repo_id,
            "primary_language": "python",
            "repo_root_locator": {"kind": "local_path", "value": "."},
            "rollout_posture": {"current_mode": "observe", "target_mode": "advisory"},
            "build_commands": [{"id": "build", "command": "python -m compileall src", "required": True}],
            "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
            "lint_commands": [],
            "typecheck_commands": [],
            "contract_commands": [
                {"id": "contract", "command": "python -m unittest discover -s tests/contracts", "required": True}
            ],
            "invariant_commands": [],
            "risk_defaults": {"default_write_tier": "medium", "blocked_command_patterns": []},
            "approval_defaults": {"medium_write_requires_approval": True, "high_requires_explicit_approval": True},
            "tool_allowlist": ["shell"],
            "path_policies": {"read_allow": ["**/*"], "write_allow": ["src/**", "tests/**"], "blocked": [".git/**"]},
            "branch_policy": {"default_branch": "main", "working_branch_prefix": "governed/", "allow_direct_push": False},
            "delivery_format": {"summary_template": "default", "include_patch": True, "include_pr_body": True},
        }

    def _light_pack_payload(self, repo_id: str) -> dict:
        return {
            "schema_version": "1.0",
            "pack_kind": "repo_attachment_light_pack",
            "binding_id": f"binding-{repo_id}",
            "repo_profile_ref": ".governed-ai/repo-profile.json",
            "adapter_preference": "manual_handoff",
            "gate_profile": "default",
            "runtime_contract_refs": {
                "repo_attachment_binding_schema": "schemas/jsonschema/repo-attachment-binding.schema.json",
                "repo_profile_schema": "schemas/jsonschema/repo-profile.schema.json",
            },
        }

    def _schema_accepts(self, payload: dict) -> bool:
        schema_path = ROOT / "schemas" / "jsonschema" / "repo-attachment-binding.schema.json"
        command = (
            "$json = [Console]::In.ReadToEnd(); "
            f"if (Test-Json -Json $json -SchemaFile '{schema_path}') "
            "{ Write-Output 'true' } else { Write-Output 'false' }"
        )
        completed = subprocess.run(
            ["pwsh", "-NoProfile", "-Command", command],
            input=json.dumps(payload),
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        return completed.stdout.strip().lower() == "true"

    def _is_under(self, path: Path, parent: Path) -> bool:
        try:
            path.resolve().relative_to(parent.resolve())
        except ValueError:
            return False
        return True


if __name__ == "__main__":
    unittest.main()
