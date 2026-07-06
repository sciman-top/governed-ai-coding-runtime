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


def _load_promotion_plan_script():
    script_path = ROOT / "scripts" / "plan-self-evolution-promotion.py"
    spec = importlib.util.spec_from_file_location("plan_self_evolution_promotion_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["plan_self_evolution_promotion_script"] = module
    spec.loader.exec_module(module)
    return module


def _load_promotion_verify_script():
    script_path = ROOT / "scripts" / "verify-self-evolution-promotion.py"
    spec = importlib.util.spec_from_file_location("verify_self_evolution_promotion_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_self_evolution_promotion_script"] = module
    spec.loader.exec_module(module)
    return module


class SelfEvolutionReadinessTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("evaluate_self_evolution_readiness_script", None)
        sys.modules.pop("recommend_self_evolution_script", None)
        sys.modules.pop("plan_self_evolution_promotion_script", None)
        sys.modules.pop("verify_self_evolution_promotion_script", None)

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
        runtime_cases = [case for case in dataset["cases"] if case["source_kind"] == "runtime_evolution_candidate"]
        self.assertTrue(runtime_cases)
        self.assertTrue(all(case["verification_refs"] for case in runtime_cases))

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
        self.assertEqual(artifact["trigger_model"]["proactive_operator_triggers"], ["SelfEvolutionRecommend", "FeedbackReport"])
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

    def test_promotion_controller_blocks_effective_change_when_selector_waits_for_host_recovery(self) -> None:
        module = _load_promotion_plan_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            recommendation_path = Path(tmp_dir) / "20260530-self-evolution-recommendations.json"
            recommendation_path.write_text(
                json.dumps(
                    {
                        "schema_version": "0.1-draft",
                        "artifact_type": "self_evolution_recommendation_report",
                        "status": "pass",
                        "as_of": "2026-05-30",
                        "recommended_next_action": "report_only_until_wait_for_host_capability_recovery",
                        "selector_next_action": "wait_for_host_capability_recovery",
                        "selector_why": "fixture bounded host capability defer",
                        "materialization_blocked": True,
                        "guards": {
                            "automatic_policy_mutation": False,
                            "automatic_skill_enablement": False,
                            "automatic_push_or_merge": False,
                            "requires_human_review_before_effective_change": True,
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            artifact_root = Path(tmp_dir) / "promotion"

            report = module.plan_self_evolution_promotion(
                repo_root=ROOT,
                recommendation_path=recommendation_path,
                as_of=dt.date(2026, 5, 30),
                write_artifacts=True,
                artifact_root=artifact_root,
            )

            artifact_path = Path(report["artifact_refs"]["json"])
            self.assertTrue(artifact_path.exists())
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

        self.assertEqual("self_evolution_promotion_controller_report", artifact["artifact_type"])
        self.assertEqual("blocked", artifact["status"])
        self.assertEqual("blocked_by_selector", artifact["promotion_stage"])
        self.assertFalse(artifact["effective_change_allowed"])
        self.assertEqual("wait_for_host_capability_recovery", artifact["selector_next_action"])
        self.assertEqual(
            {"policy_mutation", "skill_enablement", "push_or_merge"},
            {lane["lane"] for lane in artifact["control_lanes"]},
        )
        self.assertTrue(all(lane["status"] == "blocked" for lane in artifact["control_lanes"]))
        self.assertTrue(all(lane["automatic_enabled"] is False for lane in artifact["control_lanes"]))
        self.assertEqual(
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action SelfEvolutionPromotionPlan",
            artifact["trigger_model"]["recommended_operator_action_command"],
        )

    def test_promotion_controller_missing_recommendation_reports_non_mutating_trigger(self) -> None:
        module = _load_promotion_plan_script()

        report = module.plan_self_evolution_promotion(
            repo_root=ROOT,
            recommendation_path=None,
            as_of=dt.date(2026, 5, 30),
            recommendation_override=None,
        )

        self.assertEqual("missing_recommendation", report["status"])
        self.assertEqual("run_self_evolution_recommend", report["recommended_next_action"])
        self.assertFalse(report["effective_change_allowed"])
        self.assertEqual("SelfEvolutionRecommend", report["trigger_model"]["prerequisite_operator_action"])
        self.assertTrue(all(lane["automatic_enabled"] is False for lane in report["control_lanes"]))

    def test_promotion_controller_verifier_rejects_automatic_effective_changes(self) -> None:
        module = _load_promotion_verify_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact = Path(tmp_dir) / "bad-self-evolution-promotion-controller.json"
            artifact.write_text(
                json.dumps(
                    {
                        "artifact_type": "self_evolution_promotion_controller_report",
                        "status": "ready_for_review",
                        "promotion_stage": "review_required",
                        "effective_change_allowed": True,
                        "control_lanes": [
                            {
                                "lane": "policy_mutation",
                                "status": "review_required",
                                "automatic_enabled": True,
                                "guard_key": "automatic_policy_mutation",
                                "reason": "bad fixture",
                                "next_action": "auto_apply",
                            }
                        ],
                        "guards": {
                            "automatic_policy_mutation": True,
                            "automatic_skill_enablement": False,
                            "automatic_push_or_merge": False,
                            "requires_human_review_before_effective_change": False,
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "effective_change_allowed_must_be_false"):
                module.verify_self_evolution_promotion_artifact(artifact_path=artifact)

    def test_promotion_controller_schema_is_catalogued(self) -> None:
        schema_path = ROOT / "schemas" / "jsonschema" / "self-evolution-promotion-controller.schema.json"
        spec_path = ROOT / "docs" / "specs" / "self-evolution-promotion-controller-spec.md"
        catalog = (ROOT / "schemas" / "catalog" / "schema-catalog.yaml").read_text(encoding="utf-8")

        self.assertTrue(schema_path.exists())
        self.assertTrue(spec_path.exists())
        self.assertIn("name: self-evolution-promotion-controller", catalog)
        self.assertIn("path: schemas/jsonschema/self-evolution-promotion-controller.schema.json", catalog)
        self.assertIn("source_spec: docs/specs/self-evolution-promotion-controller-spec.md", catalog)

    def test_promotion_controller_example_is_documented(self) -> None:
        example_path = (
            ROOT
            / "schemas"
            / "examples"
            / "self-evolution-promotion-controller"
            / "blocked-by-selector.example.json"
        )
        examples_readme = (ROOT / "schemas" / "examples" / "README.md").read_text(encoding="utf-8")

        self.assertTrue(example_path.exists())
        self.assertIn("self-evolution-promotion-controller/", examples_readme)
        self.assertIn("self-evolution-promotion-controller/blocked-by-selector.example.json", examples_readme)

    def test_promotion_controller_verifier_rejects_schema_invalid_artifact(self) -> None:
        module = _load_promotion_verify_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact = Path(tmp_dir) / "schema-invalid-self-evolution-promotion-controller.json"
            artifact.write_text(
                json.dumps(
                    {
                        "artifact_type": "self_evolution_promotion_controller_report",
                        "status": "blocked",
                        "as_of": "2026-05-30",
                        "promotion_stage": "blocked_by_selector",
                        "effective_change_allowed": False,
                        "selector_next_action": "wait_for_host_capability_recovery",
                        "selector_why": "fixture bounded host capability defer",
                        "recommended_next_action": "report_only_until_wait_for_host_capability_recovery",
                        "rollback": "Delete the generated promotion controller artifact.",
                        "guards": {
                            "automatic_policy_mutation": False,
                            "automatic_skill_enablement": False,
                            "automatic_push_or_merge": False,
                            "requires_human_review_before_effective_change": True,
                        },
                        "control_lanes": [
                            {
                                "lane": "policy_mutation",
                                "status": "blocked",
                                "automatic_enabled": False,
                                "guard_key": "automatic_policy_mutation",
                                "reason": "fixture",
                                "next_action": "wait_for_host_capability_recovery",
                            },
                            {
                                "lane": "skill_enablement",
                                "status": "blocked",
                                "automatic_enabled": False,
                                "guard_key": "automatic_skill_enablement",
                                "reason": "fixture",
                                "next_action": "wait_for_host_capability_recovery",
                            },
                            {
                                "lane": "push_or_merge",
                                "status": "blocked",
                                "automatic_enabled": False,
                                "guard_key": "automatic_push_or_merge",
                                "reason": "fixture",
                                "next_action": "wait_for_host_capability_recovery",
                            },
                        ],
                        "trigger_model": {
                            "automatic_effective_change": False,
                            "prerequisite_operator_action": "SelfEvolutionRecommend",
                            "proactive_operator_triggers": [
                                "SelfEvolutionRecommend",
                                "FeedbackReport",
                            ],
                            "recommended_operator_action": "SelfEvolutionPromotionPlan",
                            "recommended_operator_action_command": (
                                "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 "
                                "-Action SelfEvolutionPromotionPlan"
                            ),
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "schema_validation_failed"):
                module.verify_self_evolution_promotion_artifact(artifact_path=artifact)

    def test_promotion_controller_verifier_passes_current_generated_artifact(self) -> None:
        module = _load_promotion_verify_script()

        result = module.verify_self_evolution_promotion(repo_root=ROOT)

        self.assertEqual("pass", result["status"])
        self.assertFalse(result["effective_change_allowed"])
        self.assertEqual("blocked_by_selector", result["promotion_stage"])
        self.assertEqual("refresh_evidence_first", result["selector_next_action"])
        self.assertTrue(all(item["status"] == "blocked" for item in result["lane_status"].values()))
        self.assertEqual(
            {"policy_mutation", "skill_enablement", "push_or_merge"},
            set(result["lane_status"].keys()),
        )

    def test_verify_repo_docs_runs_self_evolution_promotion_gate(self) -> None:
        verifier = (ROOT / "scripts" / "verify-repo.ps1").read_text(encoding="utf-8")

        self.assertIn("Invoke-SelfEvolutionPromotionArtifactSchemaCheck", verifier)
        self.assertIn("Invoke-SelfEvolutionPromotionChecks", verifier)
        self.assertIn('Write-CheckOk "self-evolution-promotion-artifact-schema"', verifier)
        self.assertIn('Write-CheckOk "self-evolution-promotion-controller"', verifier)


if __name__ == "__main__":
    unittest.main()
