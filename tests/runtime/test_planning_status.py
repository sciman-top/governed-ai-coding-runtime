import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_planning_status_script():
    script_path = ROOT / "scripts" / "verify-planning-status.py"
    spec = importlib.util.spec_from_file_location("verify_planning_status_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_planning_status_script"] = module
    spec.loader.exec_module(module)
    return module


class PlanningStatusTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("verify_planning_status_script", None)

    def test_planning_status_succeeds_for_repo(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-planning-status.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["current_active_queue"], "Continuous-Execution")
        self.assertEqual(payload["current_decision_gate"], "defer_ltp_and_refresh_evidence")
        self.assertEqual(payload["current_live_posture"], "ready")

    def test_planning_status_fails_when_required_token_missing(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-06",
                        "current_active_queue": {"queue_id": "GAP-159..164"},
                        "current_decision_gate": {"selector": "refresh_evidence_first"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {"status": "attention"},
                        "authoritative_docs": ["docs/README.md"],
                        "required_consistency_tokens": ["single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "README.md").write_text("wrong text", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required tokens"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)

    def test_verify_repo_docs_runs_planning_status_check(self) -> None:
        verifier = (ROOT / "scripts" / "verify-repo.ps1").read_text(encoding="utf-8")
        self.assertIn("Invoke-PlanningStatusChecks", verifier)
        self.assertIn('Write-CheckOk "planning-status"', verifier)

    def test_planning_status_fails_when_conditional_queue_guard_is_missing(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "plans").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "backlog").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-14",
                        "current_active_queue": {"queue_id": "GAP-159..164"},
                        "current_decision_gate": {"selector": "defer_ltp_and_refresh_evidence"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {
                            "status": "ready",
                            "target_run_freshness": "fresh",
                            "codex_target_run_adapter_tier": "native_attach",
                            "codex_target_run_capability_status": "ready",
                            "claude_workload_adapter_tier": "native_attach",
                            "claude_workload_status": "ready",
                        },
                        "authoritative_docs": ["docs/README.md", "docs/plans/README.md", "docs/backlog/README.md"],
                        "required_consistency_tokens": ["single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "certified baseline",
                        "current live posture",
                        "`current decision gate`: `defer_ltp_and_refresh_evidence`",
                        "target-run freshness is `fresh`",
                        "`native_attach` / ready",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "plans" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "current active queue",
                        "do not treat it as active work unless `planning-status.json` is promoted",
                        "do not treat it as the current active queue unless the status file promotes it",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "backlog" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "current decision gate",
                        "`defer_ltp_and_refresh_evidence`",
                        "`fresh`",
                        "`native_attach` / ready",
                        "both packages stay outside the current active queue until `planning-status.json` explicitly promotes a later follow-on",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "plans" / "host-family-capability-operationalization-plan.md").write_text(
                "Activation requires explicit promotion evidence and rollback.\n",
                encoding="utf-8",
            )
            (repo_root / "docs" / "plans" / "continuous-execution-readiness-and-rollout-plan.md").write_text(
                "Task 8: Promote Continuous Rollout To Active\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "conditional promotion guard"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)

    def test_planning_status_fails_when_plans_index_keeps_old_active_queue_text(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "plans").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "strategy").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "backlog").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-17",
                        "current_active_queue": {"queue_id": "Continuous-Execution"},
                        "current_decision_gate": {"selector": "defer_ltp_and_refresh_evidence"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {
                            "status": "ready",
                            "target_run_freshness": "fresh",
                            "codex_target_run_adapter_tier": "native_attach",
                            "codex_target_run_capability_status": "ready",
                            "claude_workload_adapter_tier": "native_attach",
                            "claude_workload_status": "ready",
                        },
                        "authoritative_docs": ["docs/README.md", "docs/plans/README.md", "docs/backlog/README.md"],
                        "required_consistency_tokens": ["single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "certified baseline",
                        "current live posture",
                        "`current decision gate`: `defer_ltp_and_refresh_evidence`",
                        "target-run freshness is `fresh`",
                        "`native_attach` / ready",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "plans" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "current active queue",
                        "Status: `GAP-165..168` are complete as an owner-directed conditional planning package; the queue still must not be treated as the current active queue while `planning-status.json` keeps `GAP-159..164` active and the selector at `defer_ltp_and_refresh_evidence`",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "strategy" / "current-best-end-state-blueprint.md").write_text(
                "\n".join(
                    [
                        "## Current Live Posture Rule",
                        "Current practical reading:",
                        "historical certification: `GAP-104..111`",
                        "current active queue: `GAP-159..164`",
                        "current decision gate: `defer_ltp_and_refresh_evidence`",
                        "current live posture: Codex target runs are now `native_attach / ready`",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "backlog" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "current decision gate",
                        "`defer_ltp_and_refresh_evidence`",
                        "`fresh`",
                        "`native_attach` / ready",
                        "both packages stay outside the current active queue until `planning-status.json` explicitly promotes a later follow-on",
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unexpected stale posture text"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)

    def test_planning_status_fails_when_host_family_plan_keeps_old_active_queue_text(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "plans").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "backlog").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-17",
                        "current_active_queue": {"queue_id": "Continuous-Execution"},
                        "current_decision_gate": {"selector": "defer_ltp_and_refresh_evidence"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {
                            "status": "ready",
                            "target_run_freshness": "fresh",
                            "codex_target_run_adapter_tier": "native_attach",
                            "codex_target_run_capability_status": "ready",
                            "claude_workload_adapter_tier": "native_attach",
                            "claude_workload_status": "ready",
                        },
                        "authoritative_docs": ["docs/README.md", "docs/plans/README.md", "docs/backlog/README.md"],
                        "required_consistency_tokens": ["single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "certified baseline",
                        "current live posture",
                        "`current decision gate`: `defer_ltp_and_refresh_evidence`",
                        "target-run freshness is `fresh`",
                        "`native_attach` / ready",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "plans" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "current active queue",
                        "Status: `GAP-165..168` are complete as an owner-directed conditional planning package; the queue still must not be treated as the current active queue while `planning-status.json` keeps `Continuous-Execution` active and the selector at `defer_ltp_and_refresh_evidence`",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "plans" / "host-family-capability-operationalization-plan.md").write_text(
                "\n".join(
                    [
                        "## Status",
                        "- `GAP-165..168` are complete as an owner-directed conditional planning package on `2026-06-07`; see `docs/change-evidence/20260607-gap-166-168-host-capability-claim-contract-closeout.md`",
                        "- This closeout does not change the current active queue or current decision gate. `docs/architecture/planning-status.json` remains the single source of active work posture while the prepared follow-on queue stays inactive until a later promotion explicitly opens stronger live-host execution work.",
                        "",
                        "## Goal",
                        "Turn the refreshed best-end-state definition, host-family posture, and capability-first blueprint into a bounded executable queue that can start only after current gate conditions permit promotion.",
                        "",
                        "## Activation Trigger",
                        "Promote this plan only when all of the following are true:",
                        "1. the owner explicitly chooses to promote it, or the status file is updated to a new non-blocking next action that permits bounded follow-on planning work",
                        "2. `GAP-159..164` no longer needs to be treated as the current active queue reference",
                        "",
                        "## Immediate Rule",
                        "Use this plan as a prepared follow-on queue, not as permission to start new implementation work while `planning-status.json` still keeps `GAP-159..164` as the active queue and this follow-on package inactive.",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "backlog" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "current decision gate",
                        "`defer_ltp_and_refresh_evidence`",
                        "`fresh`",
                        "`native_attach` / ready",
                        "both packages stay outside the current active queue until `planning-status.json` explicitly promotes a later follow-on",
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unexpected stale posture text"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)

    def test_planning_status_requires_20260617_live_posture_proof_points(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "strategy").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "plans").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "backlog").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "product").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-17",
                        "current_active_queue": {"queue_id": "Continuous-Execution"},
                        "current_decision_gate": {"selector": "defer_ltp_and_refresh_evidence"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {
                            "status": "ready",
                            "target_run_freshness": "fresh",
                            "codex_target_run_adapter_tier": "native_attach",
                            "codex_target_run_capability_status": "ready",
                            "claude_workload_adapter_tier": "native_attach",
                            "claude_workload_status": "ready",
                        },
                        "authoritative_docs": [
                            "docs/README.md",
                            "docs/strategy/positioning-and-competitive-layering.md",
                            "docs/strategy/current-best-end-state-blueprint.md",
                        ],
                        "required_consistency_tokens": ["single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "certified baseline",
                        "current live posture",
                        "`current decision gate`: `defer_ltp_and_refresh_evidence`",
                        "target-run freshness is `fresh`",
                        "`native_attach` / ready",
                        "latest 2026-06-09 recovery batch",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "strategy" / "positioning-and-competitive-layering.md").write_text(
                "\n".join(
                    [
                        "## Current Phase",
                        "- The current active queue is `Continuous-Execution`, as recorded in `docs/architecture/planning-status.json`.",
                        "- The current live posture is `fresh`, and the latest 2026-06-09 recovery batch now shows both Codex target runs and the Claude workload probe at `native_attach` / ready.",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "strategy" / "current-best-end-state-blueprint.md").write_text(
                "\n".join(
                    [
                        "## Current Live Posture Rule",
                        "Current practical reading:",
                        "historical certification: `GAP-104..111`",
                        "current active queue: `Continuous-Execution`",
                        "current decision gate: `defer_ltp_and_refresh_evidence`",
                        "current live posture: Codex target runs are now `native_attach / ready`",
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing required tokens"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)

    def test_planning_status_fails_when_docs_index_keeps_20260609_as_latest_posture_proof(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-17",
                        "current_active_queue": {"queue_id": "Continuous-Execution"},
                        "current_decision_gate": {"selector": "defer_ltp_and_refresh_evidence"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {
                            "status": "ready",
                            "target_run_freshness": "fresh",
                            "codex_target_run_adapter_tier": "native_attach",
                            "codex_target_run_capability_status": "ready",
                            "claude_workload_adapter_tier": "native_attach",
                            "claude_workload_status": "ready",
                        },
                        "authoritative_docs": ["docs/README.md"],
                        "required_consistency_tokens": ["single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "certified baseline",
                        "current live posture",
                        "`current decision gate`: `defer_ltp_and_refresh_evidence`",
                        "target-run freshness is `fresh`",
                        "`native_attach` / ready",
                        "Latest posture proof:",
                        "- [20260609 Live Posture Recovery](./change-evidence/20260609-live-posture-recovery.md)",
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing required tokens"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)

    def test_planning_status_fails_when_latest_lists_keep_20260609_with_latest_proof_entries(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-17",
                        "current_active_queue": {"queue_id": "Continuous-Execution"},
                        "current_decision_gate": {"selector": "defer_ltp_and_refresh_evidence"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {
                            "status": "ready",
                            "target_run_freshness": "fresh",
                            "codex_target_run_adapter_tier": "native_attach",
                            "codex_target_run_capability_status": "ready",
                            "claude_workload_adapter_tier": "native_attach",
                            "claude_workload_status": "ready",
                        },
                        "authoritative_docs": ["docs/README.md"],
                        "required_consistency_tokens": ["single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "README.md").write_text(
                "\n".join(
                    [
                        "Current evidence baseline",
                        "- [20260617 Active Queue Evidence-Upkeep Refresh](./change-evidence/20260617-active-queue-evidence-upkeep-refresh.md)",
                        "- [20260609 Live Posture Recovery](./change-evidence/20260609-live-posture-recovery.md) (historical recovery milestone)",
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing required tokens|unexpected stale posture text"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)

    def test_planning_status_requires_20260609_to_be_held_as_history_only(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-17",
                        "current_active_queue": {"queue_id": "Continuous-Execution"},
                        "current_decision_gate": {"selector": "defer_ltp_and_refresh_evidence"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {
                            "status": "ready",
                            "target_run_freshness": "fresh",
                            "codex_target_run_adapter_tier": "native_attach",
                            "codex_target_run_capability_status": "ready",
                            "claude_workload_adapter_tier": "native_attach",
                            "claude_workload_status": "ready",
                        },
                        "authoritative_docs": ["README.md"],
                        "required_consistency_tokens": ["Single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "README.md").write_text(
                "\n".join(
                    [
                        "Current navigation entry points:",
                        "  - [20260617 Active Queue Evidence-Upkeep Refresh](docs/change-evidence/20260617-active-queue-evidence-upkeep-refresh.md)",
                        "  - [20260609 Live Posture Recovery](docs/change-evidence/20260609-live-posture-recovery.md)（历史恢复里程碑）",
                        "Latest posture proof:",
                        "  - [20260617 Active Queue Evidence-Upkeep Refresh](docs/change-evidence/20260617-active-queue-evidence-upkeep-refresh.md)",
                        "  - [20260609 Live Posture Recovery](docs/change-evidence/20260609-live-posture-recovery.md)（历史恢复里程碑）",
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unexpected stale posture text|missing required tokens"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)

    def test_planning_status_requires_entrypoint_proof_refresh_to_be_indexed(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "change-evidence").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-17",
                        "current_active_queue": {"queue_id": "Continuous-Execution"},
                        "current_decision_gate": {"selector": "defer_ltp_and_refresh_evidence"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {
                            "status": "ready",
                            "target_run_freshness": "fresh",
                            "codex_target_run_adapter_tier": "native_attach",
                            "codex_target_run_capability_status": "ready",
                            "claude_workload_adapter_tier": "native_attach",
                            "claude_workload_status": "ready",
                        },
                        "authoritative_docs": ["docs/README.md", "docs/change-evidence/README.md"],
                        "required_consistency_tokens": ["single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "README.md").write_text(
                "\n".join(
                    [
                        "Current evidence proof:",
                        "  - [20260617 Active Queue Evidence-Upkeep Refresh](./change-evidence/20260617-active-queue-evidence-upkeep-refresh.md)",
                    ]
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "change-evidence" / "README.md").write_text(
                "\n".join(
                    [
                        "# Change Evidence Index",
                        "## Current Evidence Baseline",
                        "- [20260617 Active Queue Evidence-Upkeep Refresh](./20260617-active-queue-evidence-upkeep-refresh.md)",
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing required tokens"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)

    def test_planning_status_fails_when_history_entry_lacks_archived_marker(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-17",
                        "current_active_queue": {"queue_id": "Continuous-Execution"},
                        "current_decision_gate": {"selector": "defer_ltp_and_refresh_evidence"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {
                            "status": "ready",
                            "target_run_freshness": "fresh",
                            "codex_target_run_adapter_tier": "native_attach",
                            "codex_target_run_capability_status": "ready",
                            "claude_workload_adapter_tier": "native_attach",
                            "claude_workload_status": "ready",
                        },
                        "authoritative_docs": ["README.md"],
                        "required_consistency_tokens": ["Single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "README.md").write_text(
                "\n".join(
                    [
                        "Current navigation entry points:",
                        "- [20260617 Active Queue Evidence-Upkeep Refresh](docs/change-evidence/20260617-active-queue-evidence-upkeep-refresh.md)",
                        "- [20260609 Live Posture Recovery](docs/change-evidence/20260609-live-posture-recovery.md)（历史恢复里程碑）",
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing required tokens|unexpected stale posture text"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)

    def test_planning_status_fails_when_backlog_summary_keeps_20260609_recovery_batch_as_current(self) -> None:
        module = _load_planning_status_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "backlog").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs").mkdir(exist_ok=True)
            status_path = repo_root / "docs" / "architecture" / "planning-status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "status_id": "test",
                        "updated_on": "2026-06-17",
                        "current_active_queue": {"queue_id": "Continuous-Execution"},
                        "current_decision_gate": {"selector": "defer_ltp_and_refresh_evidence"},
                        "certified_baseline": {"queue_id": "GAP-104..111"},
                        "current_live_posture": {
                            "status": "ready",
                            "target_run_freshness": "fresh",
                            "codex_target_run_adapter_tier": "native_attach",
                            "codex_target_run_capability_status": "ready",
                            "claude_workload_adapter_tier": "native_attach",
                            "claude_workload_status": "ready",
                        },
                        "authoritative_docs": ["docs/backlog/README.md"],
                        "required_consistency_tokens": ["single source of planning truth"],
                        "rollback_ref": "git revert",
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "docs" / "backlog" / "README.md").write_text(
                "\n".join(
                    [
                        "Single source of planning truth",
                        "current decision gate",
                        "`defer_ltp_and_refresh_evidence`",
                        "`fresh`",
                        "`native_attach` / ready",
                        "The 2026-06-09 recovery batch now proves Codex target-run recovery at `codex_capability_status=ready` plus `adapter_tier=native_attach`.",
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing required tokens|unexpected stale posture text"):
                module.assert_planning_status(repo_root=repo_root, status_path=status_path)


if __name__ == "__main__":
    unittest.main()
