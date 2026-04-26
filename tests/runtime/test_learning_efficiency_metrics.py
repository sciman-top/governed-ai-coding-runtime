import importlib
import json
import sys
import tempfile
import unittest
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class LearningEfficiencyMetricsTests(unittest.TestCase):
    def test_build_learning_efficiency_metrics_from_interaction_trace(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.learning_efficiency_metrics")

        record = module.build_learning_efficiency_metrics(
            task_id="task-1",
            run_id="run-1",
            metrics_source_ref="artifacts/task-1/run-1/evidence/bundle.json",
            evidence_bundle={
                "final_outcome": {"status": "completed"},
                "interaction_trace": {
                    "signals": [
                        {"signal_kind": "term_confusion"},
                        {"signal_kind": "goal_scope_mismatch"},
                    ],
                    "task_restatements": ["Confirm task scope."],
                    "clarification_rounds": [{"scenario": "bugfix"}],
                    "terms_explained": [{"term": "root cause"}],
                    "observation_checklists": [{"items": ["logs", "request"]}],
                    "compression_actions": [{"compression_mode": "stage_summary"}],
                    "budget_snapshots": [
                        {
                            "budget_status": "warning",
                            "used_explanation_tokens": 10,
                            "used_clarification_tokens": 5,
                            "used_compaction_tokens": 2,
                        }
                    ],
                    "alignment_outcome": "user confirmed scope",
                },
            },
        )

        self.assertEqual(record.task_id, "task-1")
        self.assertEqual(record.restatement_count, 1)
        self.assertEqual(record.clarification_rounds, 1)
        self.assertEqual(record.term_explanation_count, 1)
        self.assertEqual(record.observation_prompt_count, 1)
        self.assertEqual(record.compression_count, 1)
        self.assertEqual(record.budget_downgrade_count, 1)
        self.assertEqual(record.token_spend_total, 17)
        self.assertEqual(record.repeated_misunderstanding_count, 1)
        self.assertEqual(record.rework_after_misalignment_count, 1)
        self.assertEqual(record.user_confirmed_alignment_count, 1)
        self.assertEqual(record.issue_resolution_without_repeated_question, 1)

    def test_persist_learning_efficiency_metrics_writes_schema_shaped_json(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.learning_efficiency_metrics")
        record = module.build_learning_efficiency_metrics(
            task_id="task-1",
            run_id="run-1",
            metrics_source_ref="artifacts/task-1/run-1/evidence/bundle.json",
            evidence_bundle={"final_outcome": {"status": "completed"}},
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = module.persist_learning_efficiency_metrics(
                output_root=tmp_dir,
                run_id="run-1",
                record=record,
            )

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["task_id"], "task-1")
            self.assertEqual(payload["run_id"], "run-1")
            self.assertEqual(payload["metrics_source_ref"], "artifacts/task-1/run-1/evidence/bundle.json")
            self.assertEqual(payload["issue_resolution_without_repeated_question"], 1)

    def test_persist_learning_efficiency_metrics_rejects_unsafe_path_segments(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.learning_efficiency_metrics")
        record = module.build_learning_efficiency_metrics(
            task_id="task-1",
            evidence_bundle={"final_outcome": {"status": "completed"}},
        )
        unsafe_record = module.LearningEfficiencyMetricsRecord(
            **{**record.to_dict(), "task_id": "../escape"}
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaisesRegex(ValueError, "task_id"):
                module.persist_learning_efficiency_metrics(
                    output_root=tmp_dir,
                    run_id="run-1",
                    record=unsafe_record,
                )

    def test_persist_learning_efficiency_metrics_rejects_symlinked_output_outside_root(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.learning_efficiency_metrics")
        record = module.build_learning_efficiency_metrics(
            task_id="task-1",
            run_id="run-1",
            metrics_source_ref="artifacts/task-1/run-1/evidence/bundle.json",
            evidence_bundle={"final_outcome": {"status": "completed"}},
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "metrics-root"
            outside = Path(tmp_dir) / "outside"
            outside.mkdir()
            root.mkdir()
            try:
                os.symlink(outside, root / "task-1")
            except (OSError, NotImplementedError):
                self.skipTest("directory symlinks are not available in this environment")

            with self.assertRaisesRegex(ValueError, "metrics output path"):
                module.persist_learning_efficiency_metrics(
                    output_root=root,
                    run_id="run-1",
                    record=record,
                )

            self.assertFalse((outside / "run-1" / "metrics" / "learning-efficiency.json").exists())

    def test_summarize_learning_efficiency_metrics_baseline_rates(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.learning_efficiency_metrics")
        first = module.build_learning_efficiency_metrics(
            task_id="task-1",
            evidence_bundle={
                "final_outcome": {"status": "completed"},
                "interaction_trace": {
                    "alignment_outcome": "user confirmed target",
                    "observation_checklists": [{"items": ["logs"]}],
                    "budget_snapshots": [{"used_explanation_tokens": 4, "used_clarification_tokens": 6}],
                },
            },
        )
        second = module.build_learning_efficiency_metrics(
            task_id="task-2",
            evidence_bundle={
                "final_outcome": {"status": "failed"},
                "interaction_trace": {
                    "signals": [{"signal_kind": "repeated_question_no_progress"}],
                    "clarification_rounds": [{"scenario": "bugfix"}],
                    "terms_explained": [{"term": "symptom"}],
                    "budget_snapshots": [{"used_explanation_tokens": 6, "used_clarification_tokens": 4}],
                },
            },
        )

        snapshot = module.summarize_learning_efficiency_metrics([first, second])

        self.assertEqual(snapshot.record_count, 2)
        self.assertEqual(snapshot.baseline_metrics["alignment_confirm_rate"], 0.5)
        self.assertEqual(snapshot.baseline_metrics["observation_gap_prompt_rate"], 0.5)
        self.assertEqual(snapshot.baseline_metrics["term_explanation_trigger_rate"], 0.5)
        self.assertEqual(snapshot.baseline_metrics["repeated_failure_before_clarify"], 0.5)
        self.assertEqual(snapshot.baseline_metrics["explanation_token_share"], 0.5)

    def test_learning_efficiency_metrics_are_exported_from_package_root(self) -> None:
        package = importlib.import_module("governed_ai_coding_runtime_contracts")
        self.assertTrue(hasattr(package, "build_learning_efficiency_metrics"))
        self.assertTrue(hasattr(package, "persist_learning_efficiency_metrics"))
        self.assertTrue(hasattr(package, "summarize_learning_efficiency_metrics"))


if __name__ == "__main__":
    unittest.main()
