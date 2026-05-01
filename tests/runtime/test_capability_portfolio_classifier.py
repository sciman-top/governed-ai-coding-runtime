import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_script():
    script_path = ROOT / "scripts" / "verify-capability-portfolio.py"
    spec = importlib.util.spec_from_file_location("verify_capability_portfolio_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_capability_portfolio_script"] = module
    spec.loader.exec_module(module)
    return module


class CapabilityPortfolioClassifierTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("verify_capability_portfolio_script", None)

    def test_verifier_passes_for_repository_classifier(self) -> None:
        module = _load_script()
        result = module.verify_capability_portfolio()
        self.assertEqual("pass", result["status"])
        self.assertGreaterEqual(result["entry_count"], 20)
        self.assertFalse(result["errors"])

    def test_verifier_fails_when_required_doc_reference_is_missing(self) -> None:
        module = _load_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            for relative in [
                "docs/architecture/capability-portfolio-classifier.json",
                "docs/specs/capability-portfolio-classifier-spec.md",
                "docs/plans/governance-hub-reuse-and-controlled-evolution-plan.md",
                "docs/research/runtime-governance-borrowing-matrix.md",
                "docs/research/2026-04-27-hybrid-final-state-external-benchmark-review.md",
                "docs/architecture/core-principles-policy.json",
                "docs/change-evidence/20260501-governance-hub-reuse-plan.md",
                "docs/change-evidence/20260501-gap-131-capability-portfolio-classifier.md",
                "docs/change-evidence/20260427-gap-112-current-source-compatibility-guard.md",
                "docs/change-evidence/20260421-gap-084-claim-drift-guard-closeout.md",
                "docs/change-evidence/20260430-host-feedback-loop-surface.md",
                "docs/targets/target-repo-governance-baseline.json",
                "docs/targets/target-repo-rollout-contract.json",
                "docs/specs/core-principles-spec.md",
                "docs/specs/controlled-improvement-proposal-spec.md",
                "docs/specs/interaction-evidence-spec.md",
                "docs/plans/runtime-evolution-review-plan.md",
                "docs/architecture/runtime-evolution-policy.json",
                "docs/architecture/current-source-compatibility-policy.json",
            ]:
                source = ROOT / relative
                target = repo_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)

            (repo_root / "docs/specs/capability-portfolio-classifier-spec.md").unlink()
            result = module.verify_capability_portfolio(
                repo_root=repo_root,
                portfolio_path=repo_root / "docs/architecture/capability-portfolio-classifier.json",
            )

            self.assertEqual("fail", result["status"])
            self.assertTrue(any("missing doc refs" in error for error in result["errors"]))

    def test_verifier_cli_succeeds(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-capability-portfolio.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertGreaterEqual(payload["entry_count"], 20)


if __name__ == "__main__":
    unittest.main()
