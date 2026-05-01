import importlib.util
import json
import shutil
import subprocess
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


class ControlPackExecutionTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("verify_control_pack_execution_script", None)
        sys.modules.pop("materialize_control_pack_script", None)

    def test_execution_verifier_passes_for_repository_pack(self) -> None:
        module = _load_script("scripts/verify-control-pack-execution.py", "verify_control_pack_execution_script")
        result = module.inspect_control_pack_execution()
        self.assertEqual("pass", result["status"])
        self.assertGreaterEqual(result["pack_count"], 1)
        self.assertFalse(result["errors"])

    def test_execution_verifier_fails_for_metadata_only_pack(self) -> None:
        module = _load_script("scripts/verify-control-pack-execution.py", "verify_control_pack_execution_script")

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            for relative in [
                "schemas/control-packs/minimum-governance-kernel.control-pack.json",
                "schemas/examples/control-pack/minimum-governance-kernel.example.json",
                "docs/specs/core-principles-spec.md",
                "docs/specs/verification-gates-spec.md",
                "docs/specs/hook-contract-spec.md",
                "docs/specs/interaction-evidence-spec.md",
                "docs/specs/runtime-operator-surface-spec.md",
                "docs/specs/skill-manifest-spec.md",
                "docs/specs/knowledge-source-spec.md",
                "docs/specs/evidence-bundle-spec.md",
                "docs/runbooks/control-rollback.md",
                "docs/plans/runtime-evolution-review-plan.md",
                "docs/architecture/core-principles-policy.json",
                ".githooks/pre-commit",
                "scripts/verify-repo.ps1",
                "scripts/install-repo-hooks.ps1",
                "scripts/host-feedback-summary.py",
                "scripts/operator.ps1",
                "scripts/extract-ai-coding-experience.py",
                "schemas/examples/skill-manifest/repo-map-audit.example.json",
                "schemas/examples/knowledge-source/docs-index-authoritative.example.json",
                "docs/change-evidence/20260422-interaction-evidence-trace-and-runtime-projection.md",
            ]:
                source = ROOT / relative
                target = repo_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)

            pack_path = repo_root / "schemas/control-packs/minimum-governance-kernel.control-pack.json"
            pack = json.loads(pack_path.read_text(encoding="utf-8"))
            pack["execution_contract"]["workflows"] = []
            pack_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            original_root = module.ROOT
            original_pack_root = module.PACK_ROOT
            module.ROOT = repo_root
            module.PACK_ROOT = repo_root / "schemas" / "control-packs"
            try:
                result = module.inspect_control_pack_execution(repo_root=repo_root)
            finally:
                module.ROOT = original_root
                module.PACK_ROOT = original_pack_root

            self.assertEqual("fail", result["status"])
            self.assertTrue(any("missing execution domain: workflows" in error for error in result["errors"]))

    def test_materializer_cli_dry_run_succeeds(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/materialize-control-pack.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("dry_run", payload["mode"])
        self.assertFalse(payload["written_files"])

    def test_materializer_apply_writes_runtime_pack_from_source_template(self) -> None:
        module = _load_script("scripts/materialize-control-pack.py", "materialize_control_pack_script")

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            for relative in [
                "schemas/examples/control-pack/minimum-governance-kernel.example.json",
            ]:
                source = ROOT / relative
                target = repo_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)

            result = module.materialize_control_pack(repo_root=repo_root, apply=True)
            self.assertEqual("apply", result["mode"])
            self.assertEqual(
                ["schemas/control-packs/minimum-governance-kernel.control-pack.json"],
                result["written_files"],
            )
            generated = json.loads(
                (repo_root / "schemas/control-packs/minimum-governance-kernel.control-pack.json").read_text(
                    encoding="utf-8"
                )
            )
            template = json.loads(
                (repo_root / "schemas/examples/control-pack/minimum-governance-kernel.example.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(template, generated)


if __name__ == "__main__":
    unittest.main()
