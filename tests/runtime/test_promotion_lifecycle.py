import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
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


class PromotionLifecycleTests(unittest.TestCase):
    def tearDown(self) -> None:
        for name in [
            "materialize_runtime_evolution_promotion_test",
            "review_runtime_evolution_retirements_promotion_test",
        ]:
            sys.modules.pop(name, None)

    def test_materializer_apply_writes_promotion_lifecycle_manifest(self) -> None:
        materializer = _load_script(
            "scripts/materialize-runtime-evolution.py",
            "materialize_runtime_evolution_promotion_test",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            verifier = _load_script("scripts/verify-promotion-lifecycle.py", "verify_promotion_helper")
            verifier._copy_minimal_repo(repo_root=ROOT, temp_root=repo_root)
            result = materializer.materialize_runtime_evolution(repo_root=repo_root, as_of=date(2026, 5, 1), apply=True)

            self.assertEqual(result["status"], "pass")
            self.assertIn(
                "docs/change-evidence/runtime-evolution-promotions/20260501-runtime-evolution-promotion-lifecycle.json",
                result["written_files"],
            )
            manifest = json.loads(
                (
                    repo_root
                    / "docs/change-evidence/runtime-evolution-promotions/20260501-runtime-evolution-promotion-lifecycle.json"
                ).read_text(encoding="utf-8")
            )
            self.assertGreaterEqual(len(manifest["entries"]), 2)
            self.assertTrue(all(entry["promotion_gate_refs"] for entry in manifest["entries"]))

    def test_retirement_review_keeps_reviewed_assets_and_evidence_history_out_of_delete_scope(self) -> None:
        materializer = _load_script(
            "scripts/materialize-runtime-evolution.py",
            "materialize_runtime_evolution_promotion_test",
        )
        retirement = _load_script(
            "scripts/review-runtime-evolution-retirements.py",
            "review_runtime_evolution_retirements_promotion_test",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            verifier = _load_script("scripts/verify-promotion-lifecycle.py", "verify_promotion_helper_retire")
            verifier._copy_minimal_repo(repo_root=ROOT, temp_root=repo_root)
            materializer.materialize_runtime_evolution(repo_root=repo_root, as_of=date(2026, 5, 1), apply=True)
            result = retirement.review_runtime_evolution_retirements(
                repo_root=repo_root,
                as_of=date(2026, 5, 1) + timedelta(days=120),
                stale_after_days=30,
            )

            self.assertGreaterEqual(result["retire_proposal_count"], 1)
            self.assertFalse(result["guard"]["reviewed_asset_delete"])
            self.assertFalse(result["guard"]["evidence_history_delete"])

    def test_promotion_lifecycle_verifier_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-promotion-lifecycle.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["lifecycle_entry_count"], 2)
        self.assertGreaterEqual(payload["retire_proposal_count"], 1)


if __name__ == "__main__":
    unittest.main()
