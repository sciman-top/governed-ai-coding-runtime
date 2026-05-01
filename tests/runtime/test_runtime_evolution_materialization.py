import importlib.util
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_materializer():
    script_path = ROOT / "scripts" / "materialize-runtime-evolution.py"
    spec = importlib.util.spec_from_file_location("materialize_runtime_evolution_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["materialize_runtime_evolution_script"] = module
    spec.loader.exec_module(module)
    return module


def _load_script(path: str, module_name: str):
    script_path = ROOT / path
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class RuntimeEvolutionMaterializationTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("materialize_runtime_evolution_script", None)
        sys.modules.pop("prepare_runtime_evolution_pr_script", None)
        sys.modules.pop("review_runtime_evolution_retirements_script", None)

    def test_materializer_dry_run_does_not_write_files(self) -> None:
        module = _load_materializer()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = self._copy_minimal_repo(Path(tmp_dir))
            result = module.materialize_runtime_evolution(repo_root=repo_root, apply=False)

            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["mode"], "dry_run")
            self.assertFalse(result["written_files"])
            self.assertFalse((repo_root / "skills").exists())

    def test_materializer_apply_writes_proposal_skill_candidate_and_manifest(self) -> None:
        module = _load_materializer()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = self._copy_minimal_repo(Path(tmp_dir))
            result = module.materialize_runtime_evolution(
                repo_root=repo_root,
                as_of=dt.date(2026, 5, 1),
                apply=True,
            )

            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["mode"], "apply")
            self.assertIn("skills/candidates/checklist-first-bugfix/skill-manifest.json", result["written_files"])
            skill_manifest = json.loads(
                (repo_root / "skills/candidates/checklist-first-bugfix/skill-manifest.json").read_text(encoding="utf-8")
            )
            self.assertFalse(skill_manifest["default_enabled"])
            self.assertEqual(skill_manifest["risk_tier"], "low")
            proposal = json.loads(
                (
                    repo_root
                    / "docs/change-evidence/runtime-evolution-proposals/proposal.checklist-first-bugfix.json"
                ).read_text(encoding="utf-8")
            )
            self.assertFalse(proposal["mutation_guard"]["allows_direct_mutation"])
            self.assertTrue(proposal["human_review"]["required"])

    def test_materializer_cli_dry_run_succeeds(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/materialize-runtime-evolution.py", "--as-of", "2026-05-01"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "dry_run")
        self.assertGreaterEqual(payload["operation_count"], 1)

    def test_pr_preparation_requires_existing_materialized_files(self) -> None:
        materializer = _load_materializer()
        pr_prepare = _load_script("scripts/prepare-runtime-evolution-pr.py", "prepare_runtime_evolution_pr_script")

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = self._copy_minimal_repo(Path(tmp_dir))
            materializer.materialize_runtime_evolution(
                repo_root=repo_root,
                as_of=dt.date(2026, 5, 1),
                apply=True,
            )
            manifest_path = repo_root / "docs/change-evidence/runtime-evolution-patches/20260501-runtime-evolution-materialization.json"
            result = pr_prepare.prepare_runtime_evolution_pr(
                repo_root=repo_root,
                manifest_path=manifest_path,
                as_of=dt.date(2026, 5, 1),
            )

            self.assertEqual(result["status"], "pass")
            self.assertFalse(result["mutation_allowed"])
            self.assertFalse(result["guard"]["auto_push_created"])
            self.assertTrue(result["guard"]["requires_explicit_git_execution"])

    def test_retirement_review_proposes_only_stale_disabled_candidates(self) -> None:
        materializer = _load_materializer()
        retire = _load_script(
            "scripts/review-runtime-evolution-retirements.py",
            "review_runtime_evolution_retirements_script",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = self._copy_minimal_repo(Path(tmp_dir))
            materializer.materialize_runtime_evolution(
                repo_root=repo_root,
                as_of=dt.date(2026, 5, 1),
                apply=True,
            )
            result = retire.review_runtime_evolution_retirements(
                repo_root=repo_root,
                as_of=dt.date(2026, 9, 1),
                stale_after_days=30,
            )

            self.assertEqual(result["status"], "pass")
            self.assertFalse(result["mutation_allowed"])
            self.assertGreaterEqual(result["retire_proposal_count"], 1)
            self.assertFalse(result["guard"]["direct_delete"])
            self.assertFalse(result["guard"]["reviewed_asset_delete"])
            self.assertFalse(result["guard"]["evidence_history_delete"])

    def _copy_minimal_repo(self, repo_root: Path) -> Path:
        for relative in [
            "scripts/extract-ai-coding-experience.py",
            "scripts/materialize-runtime-evolution.py",
            "schemas/examples/learning-efficiency-metrics/baseline.example.json",
            "schemas/examples/interaction-evidence/checklist-first-bugfix.example.json",
        ]:
            source = ROOT / relative
            target = repo_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        return repo_root


if __name__ == "__main__":
    unittest.main()
