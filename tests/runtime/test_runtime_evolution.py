import datetime as dt
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_runtime_evolution_script():
    script_path = ROOT / "scripts" / "evaluate-runtime-evolution.py"
    spec = importlib.util.spec_from_file_location("evaluate_runtime_evolution_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["evaluate_runtime_evolution_script"] = module
    spec.loader.exec_module(module)
    return module


class RuntimeEvolutionTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("evaluate_runtime_evolution_script", None)

    def test_repo_runtime_evolution_dry_run_succeeds(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/evaluate-runtime-evolution.py", "--as-of", "2026-05-01"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["policy_id"], "default-runtime-evolution-review")
        self.assertFalse(payload["mutation_allowed"])
        self.assertEqual(payload["mode"], "dry_run")
        self.assertFalse(payload["online_source_check"])
        self.assertGreaterEqual(payload["candidate_count"], 1)
        self.assertIn("evidence_snapshot", payload)
        self.assertEqual(payload["evidence_snapshot"]["current_source"]["status"], "pass")
        self.assertTrue(any(item["retrieval_mode"] == "dry_run_catalog" for item in payload["source_records"]))
        self.assertTrue(any(item["source_type"] == "internal_ai_coding_experience" for item in payload["source_records"]))
        self.assertTrue(any(item["candidate_id"] == "EVOL-AI-EXPERIENCE" for item in payload["candidates"]))
        self.assertTrue(any(item["candidate_id"] == "EVOL-EFFECT-FEEDBACK" for item in payload["candidates"]))
        self.assertTrue(all(item["patch_plan"] for item in payload["candidates"]))

    def test_internal_ai_coding_experience_sources_are_local_checks(self) -> None:
        module = _load_runtime_evolution_script()

        result = module.inspect_runtime_evolution_policy(
            repo_root=ROOT,
            policy_path=ROOT / "docs" / "architecture" / "runtime-evolution-policy.json",
            as_of=dt.date(2026, 5, 1),
            online_source_check=True,
        )

        internal_sources = [
            item
            for item in result["source_records"]
            if item["source_type"] == "internal_ai_coding_experience"
            and not item["source_id"].startswith("policy-source-")
        ]
        self.assertTrue(internal_sources)
        self.assertTrue(all(item["retrieval_mode"] == "local_file_check" for item in internal_sources))
        self.assertTrue(all(item["local_ref_exists"] for item in internal_sources))
        self.assertTrue(all(item["online_probe"] is None for item in internal_sources))

    def test_runtime_evolution_marks_stale_after_30_days(self) -> None:
        module = _load_runtime_evolution_script()

        result = module.inspect_runtime_evolution_policy(
            repo_root=ROOT,
            policy_path=ROOT / "docs" / "architecture" / "runtime-evolution-policy.json",
            as_of=dt.date(2026, 6, 2),
        )

        self.assertTrue(result["stale"])
        self.assertTrue(any(item["candidate_id"] == "EVOL-REVIEW-FRESHNESS" for item in result["candidates"]))
        refresh = next(item for item in result["candidates"] if item["candidate_id"] == "EVOL-REVIEW-FRESHNESS")
        self.assertEqual(refresh["proposed_action"], "modify")

    def test_runtime_evolution_rejects_invalid_candidate_action(self) -> None:
        module = _load_runtime_evolution_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._copy_required_files(repo_root)
            policy = json.loads((repo_root / "docs/architecture/runtime-evolution-policy.json").read_text(encoding="utf-8"))
            policy["candidate_actions"] = ["unsupported"]
            policy_path = repo_root / "docs/architecture/runtime-evolution-policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "candidate action is invalid"):
                module.assert_runtime_evolution_policy(
                    repo_root=repo_root,
                    policy_path=policy_path,
                    as_of=dt.date(2026, 5, 1),
                )

    def test_evolve_runtime_wrapper_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    "scripts/evolve-runtime.ps1",
                    "-AsOf",
                    "2026-05-01",
                    "-WriteArtifacts",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertIn("json", payload["artifact_refs"])
        self.assertTrue(Path(payload["artifact_refs"]["json"]).exists())

    def test_operator_evolution_review_supports_online_source_check_flag(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/operator.ps1",
                "-Action",
                "EvolutionReview",
                "-OnlineSourceCheck",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload_start = completed.stdout.find("{")
        self.assertGreaterEqual(payload_start, 0)
        payload = json.loads(completed.stdout[payload_start:])
        self.assertTrue(payload["online_source_check"])

    def test_verify_repo_docs_runs_runtime_evolution_gate(self) -> None:
        verifier = (ROOT / "scripts" / "verify-repo.ps1").read_text(encoding="utf-8")

        self.assertIn("function Invoke-DocsChecks", verifier)
        self.assertIn("Invoke-RuntimeEvolutionReviewChecks", verifier)
        self.assertIn('Write-CheckOk "runtime-evolution-review"', verifier)

    def _copy_required_files(self, repo_root: Path) -> None:
        for relative in [
            "docs/architecture/runtime-evolution-policy.json",
            "docs/plans/runtime-evolution-review-plan.md",
            "docs/change-evidence/20260501-runtime-evolution-planning.md",
            "scripts/build-runtime.ps1",
            "scripts/verify-repo.ps1",
            "scripts/doctor-runtime.ps1",
        ]:
            source = ROOT / relative
            target = repo_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
