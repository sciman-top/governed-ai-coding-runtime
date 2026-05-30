import datetime as dt
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_script():
    script_path = ROOT / "scripts" / "evaluate-self-evolution-readiness.py"
    spec = importlib.util.spec_from_file_location("evaluate_self_evolution_readiness_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["evaluate_self_evolution_readiness_script"] = module
    spec.loader.exec_module(module)
    return module


def _load_recommend_script():
    script_path = ROOT / "scripts" / "recommend-self-evolution.py"
    spec = importlib.util.spec_from_file_location("recommend_self_evolution_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["recommend_self_evolution_script"] = module
    spec.loader.exec_module(module)
    return module


class SelfEvolutionReadinessTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("evaluate_self_evolution_readiness_script", None)
        sys.modules.pop("recommend_self_evolution_script", None)

    def test_readiness_reports_truthful_complete_state_without_unattended_mutation(self) -> None:
        module = _load_script()

        result = module.inspect_self_evolution_readiness(
            repo_root=ROOT,
            policy_path=ROOT / "docs" / "architecture" / "self-evolution-readiness-policy.json",
            as_of=dt.date(2026, 5, 29),
        )

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["overall_state"], "complete")
        self.assertFalse(result["ready_for_unattended_self_update"])
        self.assertGreaterEqual(result["capability_counts"]["implemented"], 1)
        self.assertEqual(result["capability_counts"]["missing"], 0)
        self.assertEqual(result["capability_counts"]["partial"], 0)
        self.assertIsNone(result["next_gap"])
        self.assertIn("refuses unattended active mutation", result["truth_statement"])

    def test_write_artifacts_emits_readiness_json(self) -> None:
        module = _load_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = module.inspect_self_evolution_readiness(
                repo_root=ROOT,
                policy_path=ROOT / "docs" / "architecture" / "self-evolution-readiness-policy.json",
                as_of=dt.date(2026, 5, 29),
                write_artifacts=True,
                artifact_root=Path(tmp_dir),
            )

            artifact_path = Path(result["artifact_refs"]["json"])
            self.assertTrue(artifact_path.exists())
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

        self.assertIsNone(artifact["next_gap"])
        self.assertFalse(artifact["guards"]["automatic_policy_mutation"])

    def test_eval_dataset_generator_outputs_cases(self) -> None:
        generator_path = ROOT / "scripts" / "generate-self-evolution-eval-dataset.py"
        spec = importlib.util.spec_from_file_location("generate_self_evolution_eval_dataset_script", generator_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"unable to load module: {generator_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules["generate_self_evolution_eval_dataset_script"] = module
        spec.loader.exec_module(module)
        self.addCleanup(sys.modules.pop, "generate_self_evolution_eval_dataset_script", None)

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = module.generate_self_evolution_eval_dataset(
                repo_root=ROOT,
                as_of=dt.date(2026, 5, 29),
                write_artifacts=True,
                artifact_root=Path(tmp_dir),
            )

            artifact_path = Path(result["artifact_refs"]["json"])
            self.assertTrue(artifact_path.exists())
            dataset = json.loads(artifact_path.read_text(encoding="utf-8"))

        self.assertEqual(dataset["artifact_type"], "self_evolution_eval_dataset")
        self.assertFalse(dataset["mutation_allowed"])
        self.assertGreaterEqual(dataset["case_count"], 1)
        self.assertTrue(all(case["mutation_allowed"] is False for case in dataset["cases"]))

    def test_trajectory_optimizer_and_variant_evaluator_form_non_mutating_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            eval_root = Path(tmp_dir) / "evals"
            variant_root = Path(tmp_dir) / "variants"
            evaluation_root = Path(tmp_dir) / "variant-evaluations"
            dataset_completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/generate-self-evolution-eval-dataset.py",
                    "--as-of",
                    "2026-05-29",
                    "--write-artifacts",
                    "--artifact-root",
                    str(eval_root),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(dataset_completed.returncode, 0, dataset_completed.stderr)
            dataset_payload = json.loads(dataset_completed.stdout)

            variant_completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/optimize-runtime-evolution-trajectory.py",
                    "--as-of",
                    "2026-05-29",
                    "--dataset",
                    dataset_payload["artifact_refs"]["json"],
                    "--write-artifacts",
                    "--artifact-root",
                    str(variant_root),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(variant_completed.returncode, 0, variant_completed.stderr)
            variant_payload = json.loads(variant_completed.stdout)
            self.assertEqual(variant_payload["artifact_type"], "self_evolution_candidate_variants")
            self.assertFalse(variant_payload["mutation_allowed"])
            self.assertGreaterEqual(variant_payload["variant_count"], 1)

            evaluation_completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/evaluate-runtime-evolution-variant.py",
                    "--as-of",
                    "2026-05-29",
                    "--variants",
                    variant_payload["artifact_refs"]["json"],
                    "--write-artifacts",
                    "--artifact-root",
                    str(evaluation_root),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(evaluation_completed.returncode, 0, evaluation_completed.stderr)
            evaluation_payload = json.loads(evaluation_completed.stdout)

        self.assertEqual(evaluation_payload["artifact_type"], "self_evolution_variant_evaluation")
        self.assertFalse(evaluation_payload["mutation_allowed"])
        self.assertEqual(evaluation_payload["variant_count"], variant_payload["variant_count"])
        self.assertGreaterEqual(evaluation_payload["review_candidate_count"], 1)
        self.assertTrue(all(item["mutation_allowed"] is False for item in evaluation_payload["evaluations"]))

    def test_cli_and_operator_wrappers_succeed(self) -> None:
        cli_completed = subprocess.run(
            [
                sys.executable,
                "scripts/evaluate-self-evolution-readiness.py",
                "--as-of",
                "2026-05-29",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(cli_completed.returncode, 0, cli_completed.stderr)
        cli_payload = json.loads(cli_completed.stdout)
        self.assertIsNone(cli_payload["next_gap"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            operator_completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    "scripts/evaluate-self-evolution-readiness.ps1",
                    "-AsOf",
                    "2026-05-29",
                    "-WriteArtifacts",
                    "-ArtifactRoot",
                    tmp_dir,
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(operator_completed.returncode, 0, operator_completed.stderr)
            operator_payload = json.loads(operator_completed.stdout)
            self.assertTrue(Path(operator_payload["artifact_refs"]["json"]).exists())

        eval_completed = subprocess.run(
            [
                sys.executable,
                "scripts/generate-self-evolution-eval-dataset.py",
                "--as-of",
                "2026-05-29",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(eval_completed.returncode, 0, eval_completed.stderr)
        eval_payload = json.loads(eval_completed.stdout)
        self.assertEqual(eval_payload["artifact_type"], "self_evolution_eval_dataset")

    def test_recommendation_report_surfaces_trigger_and_action_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            eval_root = Path(tmp_dir) / "evals"
            variant_root = Path(tmp_dir) / "variants"
            evaluation_root = Path(tmp_dir) / "variant-evaluations"
            recommendation_root = Path(tmp_dir) / "recommendations"
            dataset_completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/generate-self-evolution-eval-dataset.py",
                    "--as-of",
                    "2026-05-29",
                    "--write-artifacts",
                    "--artifact-root",
                    str(eval_root),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(dataset_completed.returncode, 0, dataset_completed.stderr)
            dataset_payload = json.loads(dataset_completed.stdout)

            variant_completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/optimize-runtime-evolution-trajectory.py",
                    "--as-of",
                    "2026-05-29",
                    "--dataset",
                    dataset_payload["artifact_refs"]["json"],
                    "--write-artifacts",
                    "--artifact-root",
                    str(variant_root),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(variant_completed.returncode, 0, variant_completed.stderr)
            variant_payload = json.loads(variant_completed.stdout)

            evaluation_completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/evaluate-runtime-evolution-variant.py",
                    "--as-of",
                    "2026-05-29",
                    "--variants",
                    variant_payload["artifact_refs"]["json"],
                    "--write-artifacts",
                    "--artifact-root",
                    str(evaluation_root),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(evaluation_completed.returncode, 0, evaluation_completed.stderr)
            evaluation_payload = json.loads(evaluation_completed.stdout)

            module = _load_recommend_script()
            report = module.recommend_self_evolution(
                repo_root=ROOT,
                variant_evaluation_path=Path(evaluation_payload["artifact_refs"]["json"]),
                as_of=dt.date(2026, 5, 29),
                write_artifacts=True,
                artifact_root=recommendation_root,
                next_work_override={
                    "next_action": "wait_for_host_capability_recovery",
                    "why": "fixture bounded host capability defer",
                },
            )

            artifact_path = Path(report["artifact_refs"]["json"])
            self.assertTrue(artifact_path.exists())
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

        self.assertEqual(artifact["artifact_type"], "self_evolution_recommendation_report")
        self.assertFalse(artifact["mutation_allowed"])
        self.assertEqual(artifact["trigger_model"]["recommended_operator_action"], "SelfEvolutionRecommend")
        self.assertEqual(artifact["trigger_model"]["proactive_operator_triggers"], ["FeedbackReport", "DailyAll"])
        self.assertEqual(artifact["recommended_next_action"], "report_only_until_wait_for_host_capability_recovery")
        self.assertTrue(artifact["materialization_blocked"])
        self.assertEqual(
            {item["lane"] for item in artifact["recommendations"]},
            {"add", "optimize", "delete_or_retire"},
        )
        self.assertIn(
            "optimize.review_candidate_variants",
            {item["recommendation_id"] for item in artifact["recommendations"]},
        )
        self.assertTrue(all(item["mutation_allowed"] is False for item in artifact["recommendations"]))


if __name__ == "__main__":
    unittest.main()
