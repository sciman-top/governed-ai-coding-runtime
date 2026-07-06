import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_script(path: str, module_name: str):
    script_path = ROOT / path
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class ControlPackInheritanceTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("verify_control_pack_inheritance_script", None)

    def test_inheritance_verifier_passes_for_repository_assets(self) -> None:
        module = _load_script("scripts/verify-control-pack-inheritance.py", "verify_control_pack_inheritance_script")
        result = module.inspect_control_pack_inheritance()
        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["errors"])
        self.assertEqual([], result["na_records"])
        self.assertGreaterEqual(result["inherited_field_count"], 6)

    def test_fails_when_repo_profile_is_missing_required_inherited_field(self) -> None:
        module = _load_script("scripts/verify-control-pack-inheritance.py", "verify_control_pack_inheritance_script")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_profile = json.loads((ROOT / ".governed-ai/repo-profile.json").read_text(encoding="utf-8"))
            repo_profile.pop("windows_process_environment_policy", None)
            repo_profile_path = workspace / "repo-profile.json"
            _write_json(repo_profile_path, repo_profile)

            result = module.inspect_control_pack_inheritance(repo_profile_path=repo_profile_path)

            self.assertEqual("fail", result["status"])
            codes = {error["code"] for error in result["errors"]}
            self.assertIn("missing_repo_profile_inherited_field", codes)

    def test_fails_when_schema_is_missing_inherited_field_path(self) -> None:
        module = _load_script("scripts/verify-control-pack-inheritance.py", "verify_control_pack_inheritance_script")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            schema = json.loads((ROOT / "schemas/jsonschema/repo-profile.schema.json").read_text(encoding="utf-8"))
            schema["properties"].pop("windows_process_environment_policy", None)
            schema_path = workspace / "repo-profile.schema.json"
            _write_json(schema_path, schema)

            result = module.inspect_control_pack_inheritance(repo_profile_schema_path=schema_path)

            self.assertEqual("fail", result["status"])
            codes = {error["code"] for error in result["errors"]}
            self.assertIn("missing_schema_path", codes)

    def test_fails_when_repo_profile_declares_forbidden_override(self) -> None:
        module = _load_script("scripts/verify-control-pack-inheritance.py", "verify_control_pack_inheritance_script")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_profile = json.loads((ROOT / ".governed-ai/repo-profile.json").read_text(encoding="utf-8"))
            repo_profile["hard_gate_order"] = ["build", "test"]
            repo_profile_path = workspace / "repo-profile.json"
            _write_json(repo_profile_path, repo_profile)

            result = module.inspect_control_pack_inheritance(repo_profile_path=repo_profile_path)

            self.assertEqual("fail", result["status"])
            codes = {error["code"] for error in result["errors"]}
            self.assertIn("forbidden_override_present_in_repo_profile", codes)


if __name__ == "__main__":
    unittest.main()
