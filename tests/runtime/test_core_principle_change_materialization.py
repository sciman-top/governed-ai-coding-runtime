import datetime as dt
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_materializer():
    script_path = ROOT / "scripts" / "materialize-core-principle-change.py"
    spec = importlib.util.spec_from_file_location("materialize_core_principle_change_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["materialize_core_principle_change_script"] = module
    spec.loader.exec_module(module)
    return module


class CorePrincipleChangeMaterializationTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("materialize_core_principle_change_script", None)

    def test_materializer_dry_run_does_not_write_active_policy_or_proposals(self) -> None:
        module = _load_materializer()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            result = module.materialize_core_principle_change(
                repo_root=repo_root,
                as_of=dt.date(2026, 5, 1),
                apply=False,
            )

            self.assertEqual("pass", result["status"])
            self.assertEqual("dry_run", result["mode"])
            self.assertFalse(result["written_files"])
            self.assertFalse(result["guard"]["active_policy_auto_apply"])
            self.assertTrue(result["guard"]["requires_human_review_before_effective_change"])
            self.assertFalse((repo_root / "docs/architecture/core-principles-policy.json").exists())
            self.assertFalse((repo_root / "docs/change-evidence/core-principle-change-proposals").exists())

    def test_materializer_apply_writes_reviewable_proposal_and_manifest_only(self) -> None:
        module = _load_materializer()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            result = module.materialize_core_principle_change(
                repo_root=repo_root,
                as_of=dt.date(2026, 5, 1),
                apply=True,
            )

            self.assertEqual("pass", result["status"])
            self.assertEqual("apply", result["mode"])
            self.assertFalse(result["guard"]["active_policy_auto_apply"])
            self.assertIn(
                "docs/change-evidence/core-principle-change-proposals/20260501-governance-hub-reusable-contract-final-state.json",
                result["written_files"],
            )
            self.assertIn(
                "docs/change-evidence/core-principle-change-patches/20260501-core-principle-change-materialization.json",
                result["written_files"],
            )
            proposal = json.loads(
                (
                    repo_root
                    / "docs/change-evidence/core-principle-change-proposals/20260501-governance-hub-reusable-contract-final-state.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual("governance_hub_reusable_contract_final_state", proposal["principle_id"])
            self.assertEqual("add", proposal["change_action"])
            self.assertIn("Governance Hub", proposal["summary"])
            self.assertIn("Reusable Contract", proposal["summary"])
            self.assertIn("Controlled Evolution", proposal["summary"])
            self.assertIn("outer AI", proposal["summary"])
            self.assertFalse(proposal["guard"]["active_policy_auto_apply"])

    def test_materializer_cli_dry_run_succeeds(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/materialize-core-principle-change.py", "--as-of", "2026-05-01"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("dry_run", payload["mode"])
        self.assertEqual(2, payload["operation_count"])
        self.assertFalse(payload["guard"]["active_policy_auto_apply"])

    def test_operator_dry_run_exposes_core_principle_materialize_flow(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/operator.ps1",
                "-Action",
                "CorePrincipleMaterialize",
                "-DryRun",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("materialize-core-principle-change.ps1", completed.stdout)
        self.assertIn("DRY-RUN core-principle-change-materialize", completed.stdout)

    def test_operator_core_principle_materialize_reports_before_writing_by_default(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/operator.ps1",
                "-Action",
                "CorePrincipleMaterialize",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("-Apply", completed.stdout)
        payload_start = completed.stdout.find("{")
        self.assertGreaterEqual(payload_start, 0)
        payload = json.loads(completed.stdout[payload_start:])
        self.assertEqual("dry_run", payload["mode"])
        self.assertFalse(payload["written_files"])
        self.assertFalse(payload["guard"]["active_policy_auto_apply"])
        self.assertTrue(payload["guard"]["requires_human_review_before_effective_change"])

    def test_operator_core_principle_materialize_requires_explicit_write_confirmation(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/operator.ps1",
                "-Action",
                "CorePrincipleMaterialize",
                "-ConfirmCorePrincipleProposalWrite",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("-Apply", completed.stdout)
        payload_start = completed.stdout.find("{")
        self.assertGreaterEqual(payload_start, 0)
        payload = json.loads(completed.stdout[payload_start:])
        self.assertEqual("apply", payload["mode"])
        self.assertTrue(payload["written_files"])
        self.assertFalse(payload["guard"]["active_policy_auto_apply"])


if __name__ == "__main__":
    unittest.main()
