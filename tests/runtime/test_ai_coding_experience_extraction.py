import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_extractor():
    script_path = ROOT / "scripts" / "extract-ai-coding-experience.py"
    spec = importlib.util.spec_from_file_location("extract_ai_coding_experience_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["extract_ai_coding_experience_script"] = module
    spec.loader.exec_module(module)
    return module


class AiCodingExperienceExtractionTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("extract_ai_coding_experience_script", None)

    def test_extractor_outputs_non_mutating_proposal_and_skill_candidate(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/extract-ai-coding-experience.py", "--as-of", "2026-05-01"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["mode"], "dry_run")
        self.assertFalse(payload["mutation_allowed"])
        self.assertGreaterEqual(payload["proposal_count"], 1)
        self.assertGreaterEqual(payload["skill_manifest_candidate_count"], 1)
        self.assertFalse(payload["invalid_reasons"])
        self.assertTrue(all(payload["quality_checks"].values()))
        self.assertTrue(any(item["signal_id"] == "ai-pattern.checklist-first-bugfix" for item in payload["signals"]))

    def test_generated_proposal_matches_required_controlled_proposal_shape(self) -> None:
        module = _load_extractor()

        result = module.inspect_ai_coding_experience(repo_root=ROOT)
        proposal = result["proposals"][0]

        for field in [
            "schema_version",
            "proposal_id",
            "source_refs",
            "proposal_category",
            "proposal_scope",
            "summary",
            "rationale",
            "expected_impact",
            "risk_posture",
            "human_review",
            "mutation_guard",
            "rollback_ref",
            "status",
        ]:
            self.assertIn(field, proposal)
        self.assertTrue(proposal["human_review"]["required"])
        self.assertFalse(proposal["mutation_guard"]["allows_direct_mutation"])
        self.assertEqual(proposal["status"], "proposed")
        for source_ref in proposal["source_refs"]:
            self.assertTrue((ROOT / source_ref).exists())

    def test_generated_skill_candidate_matches_required_skill_manifest_shape(self) -> None:
        module = _load_extractor()

        result = module.inspect_ai_coding_experience(repo_root=ROOT)
        skill = result["skill_manifest_candidates"][0]

        for field in [
            "schema_version",
            "skill_id",
            "display_name",
            "version",
            "description",
            "entrypoint",
            "input_modes",
            "risk_tier",
            "capabilities",
            "provenance",
            "compatibility",
        ]:
            self.assertIn(field, skill)
        self.assertFalse(skill["default_enabled"])
        self.assertIn("controlled-improvement-proposal", skill["compatibility"]["required_contracts"])
        self.assertNotEqual(skill["risk_tier"], "high")

    def test_signal_score_is_recomputable_and_explained(self) -> None:
        module = _load_extractor()

        result = module.inspect_ai_coding_experience(repo_root=ROOT)
        signal = result["signals"][0]

        expected = (
            signal["recurrence"] * 2
            + signal["time_saved"]
            + signal["risk_reduction"] * 2
            + signal["verification_strength"]
            + signal["reuse_scope"]
            - signal["maintenance_cost"]
            - signal["ambiguity"]
            - signal["staleness_risk"]
        )
        self.assertEqual(signal["value_score"], expected)
        self.assertIn("recurrence*2", signal["score_formula"])

    def test_low_score_signal_does_not_promote_to_proposal_or_skill(self) -> None:
        module = _load_extractor()

        signal = module._score_signal(
            signal_id="ai-pattern.one-off-note",
            pattern="one-off local note",
            source_refs=["schemas/examples/interaction-evidence/checklist-first-bugfix.example.json"],
            suggested_asset="skill",
            recurrence=1,
            time_saved=0,
            risk_reduction=0,
            verification_strength=0,
            reuse_scope=0,
            maintenance_cost=1,
            ambiguity=1,
            staleness_risk=1,
            min_proposal_score=5,
            min_skill_score=8,
        )

        self.assertEqual(signal["disposition"], "evidence_only")
        self.assertLess(signal["value_score"], 5)

    def test_quality_checks_reject_missing_source_ref(self) -> None:
        module = _load_extractor()
        signal = module._score_signal(
            signal_id="ai-pattern.missing-source",
            pattern="missing source",
            source_refs=["missing/evidence.json"],
            suggested_asset="skill",
            recurrence=3,
            time_saved=2,
            risk_reduction=2,
            verification_strength=2,
            reuse_scope=2,
            maintenance_cost=1,
            ambiguity=1,
            staleness_risk=1,
            min_proposal_score=5,
            min_skill_score=8,
        )
        proposal = module._build_proposal(signal=signal, as_of=__import__("datetime").date(2026, 5, 1))

        quality = module._build_quality_checks(
            root=ROOT,
            signals=[signal],
            proposals=[proposal],
            knowledge_candidates=[],
            pattern_candidates=[],
            memory_records=[],
            retirement_records=[],
            skill_candidates=[],
            min_proposal_score=5,
            min_skill_score=8,
            as_of=__import__("datetime").date(2026, 5, 1),
        )

        self.assertFalse(quality["source_refs_exist"])
        self.assertIn("source_refs_exist", module._collect_invalid_reasons(quality))

    def test_operator_experience_review_writes_artifacts(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/operator.ps1",
                "-Action",
                "ExperienceReview",
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
        self.assertIn("json", payload["artifact_refs"])
        self.assertTrue(Path(payload["artifact_refs"]["json"]).exists())


if __name__ == "__main__":
    unittest.main()
