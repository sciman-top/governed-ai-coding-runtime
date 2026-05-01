import importlib.util
import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_extractor():
    script_path = ROOT / "scripts" / "extract-ai-coding-experience.py"
    spec = importlib.util.spec_from_file_location("extract_ai_coding_experience_lifecycle_test", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["extract_ai_coding_experience_lifecycle_test"] = module
    spec.loader.exec_module(module)
    return module


class KnowledgeMemoryLifecycleTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("extract_ai_coding_experience_lifecycle_test", None)

    def test_extractor_outputs_knowledge_pattern_and_memory_records(self) -> None:
        module = _load_extractor()

        result = module.inspect_ai_coding_experience(repo_root=ROOT, as_of=date(2026, 5, 1))

        self.assertGreaterEqual(result["knowledge_candidate_count"], 1)
        self.assertGreaterEqual(result["pattern_candidate_count"], 1)
        self.assertGreaterEqual(result["memory_record_count"], 1)
        self.assertTrue(result["quality_checks"]["knowledge_candidates_have_source_and_verification"])
        self.assertTrue(result["quality_checks"]["pattern_candidates_have_source_and_verification"])
        self.assertTrue(result["quality_checks"]["memory_records_have_required_fields"])

    def test_memory_records_include_scope_provenance_confidence_expiry_and_retrieval_evidence(self) -> None:
        module = _load_extractor()

        result = module.inspect_ai_coding_experience(repo_root=ROOT, as_of=date(2026, 5, 1))
        record = result["memory_records"][0]

        self.assertIn("scope", record)
        self.assertIn("provenance", record)
        self.assertIn("confidence", record)
        self.assertIn("expires_at", record)
        self.assertIn("retrieval_evidence", record)
        self.assertGreater(date.fromisoformat(record["expires_at"]), date(2026, 5, 1))
        self.assertTrue(record["retrieval_evidence"]["verification_refs"])

    def test_retirement_records_preserve_audit_history(self) -> None:
        module = _load_extractor()

        signal = module._score_signal(
            signal_id="ai-pattern.one-off-note",
            pattern="one-off local note",
            source_refs=["schemas/examples/interaction-evidence/checklist-first-bugfix.example.json"],
            suggested_asset="knowledge",
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
        retirement_records = module._build_retirement_records(
            signals=[signal],
            as_of=date(2026, 5, 1),
            retirement_score_ceiling=4,
        )

        self.assertEqual(len(retirement_records), 1)
        self.assertTrue(retirement_records[0]["audit_history_retained"])
        self.assertFalse(retirement_records[0]["delete_active_evidence"])

    def test_lifecycle_verifier_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-knowledge-memory-lifecycle.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["knowledge_candidate_count"], 1)
        self.assertGreaterEqual(payload["memory_record_count"], 1)


if __name__ == "__main__":
    unittest.main()
