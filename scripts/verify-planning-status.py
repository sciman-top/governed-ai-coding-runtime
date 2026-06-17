from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS_PATH = ROOT / "docs" / "architecture" / "planning-status.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify planning status source-of-truth alignment.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--status-path", default=str(DEFAULT_STATUS_PATH))
    args = parser.parse_args()

    try:
        result = assert_planning_status(repo_root=Path(args.repo_root), status_path=Path(args.status_path))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def assert_planning_status(*, repo_root: Path, status_path: Path) -> dict:
    result = inspect_planning_status(repo_root=repo_root, status_path=status_path)
    failures: list[str] = []
    if result["missing_fields"]:
        failures.append("missing fields: " + ", ".join(result["missing_fields"]))
    if result["missing_files"]:
        failures.append("missing files: " + ", ".join(result["missing_files"]))
    if result["missing_tokens"]:
        failures.append("missing required tokens: " + ", ".join(result["missing_tokens"]))
    if result["unexpected_tokens"]:
        failures.append("unexpected stale posture text: " + ", ".join(result["unexpected_tokens"]))
    if failures:
        raise ValueError("planning status verification failed: " + "; ".join(failures))
    return result


def inspect_planning_status(*, repo_root: Path, status_path: Path) -> dict:
    root = repo_root.resolve(strict=False)
    payload = _load_json(status_path)

    required_fields = [
        "status_id",
        "updated_on",
        "current_active_queue",
        "current_decision_gate",
        "certified_baseline",
        "current_live_posture",
        "authoritative_docs",
        "required_consistency_tokens",
        "rollback_ref",
    ]
    missing_fields = [field for field in required_fields if field not in payload]

    queue_id = str(payload.get("current_active_queue", {}).get("queue_id") or "").strip()
    decision_gate = str(payload.get("current_decision_gate", {}).get("selector") or "").strip()
    live_posture = payload.get("current_live_posture", {})
    target_run_freshness = str(live_posture.get("target_run_freshness") or "").strip()
    codex_adapter_tier = str(live_posture.get("codex_target_run_adapter_tier") or "").strip()
    codex_capability_status = str(live_posture.get("codex_target_run_capability_status") or "").strip()
    claude_adapter_tier = str(live_posture.get("claude_workload_adapter_tier") or "").strip()
    claude_workload_status = str(live_posture.get("claude_workload_status") or "").strip()

    doc_paths = payload.get("authoritative_docs", [])
    missing_files = [path for path in doc_paths if not (root / path).exists()]

    required_tokens = {
        "docs/README.md": [
            "Single source of planning truth",
            "certified baseline",
            "current live posture",
            f"`current decision gate`: `{decision_gate}`",
            f"target-run freshness is `{target_run_freshness}`",
            f"`{codex_adapter_tier}` / {codex_capability_status}",
            f"`{claude_adapter_tier}` / {claude_workload_status}",
            "20260617 Active Queue Evidence-Upkeep Refresh",
            "20260617 Planning EntryPoint Proof Refresh",
        ],
        "docs/change-evidence/README.md": [
            "20260617 Planning EntryPoint Proof Refresh",
        ],
        "docs/plans/README.md": ["Single source of planning truth", "current active queue"],
        "docs/backlog/README.md": [
            "Single source of planning truth",
            "current decision gate",
            f"`{decision_gate}`",
            f"`{target_run_freshness}`",
            f"`{codex_adapter_tier}` / {codex_capability_status}",
            "2026-06-17",
        ],
        "docs/backlog/issue-ready-backlog.md": [
            f"active queue reference: `{queue_id}`",
            "current authority for live posture and decision gate: `docs/architecture/planning-status.json`",
        ],
        "docs/prd/governed-ai-coding-runtime-prd.md": [
            "The single source of current planning and live-posture truth is `docs/architecture/planning-status.json`.",
            f"The current active queue is `{queue_id}`, and the current decision gate remains `{decision_gate}`.",
        ],
        "docs/strategy/positioning-and-competitive-layering.md": [
            f"The current active queue is `{queue_id}`",
            f"The current live posture is `{target_run_freshness}`",
            "2026-06-17",
        ],
        "docs/strategy/current-best-end-state-blueprint.md": [
            f"current active queue: `{queue_id}`",
            f"current decision gate: `{decision_gate}`",
            "2026-06-17",
        ],
        "docs/product/interaction-model.md": [
            f"The current active queue is `{queue_id}`",
            f"current decision gate remains `{decision_gate}`",
        ],
        "README.md": [
            "当前唯一状态真源",
            f"`current decision gate`：`{decision_gate}`",
            f"target-run freshness 为 `{target_run_freshness}`",
            f"`{codex_adapter_tier}` / {codex_capability_status}",
            f"`{claude_adapter_tier}` / {claude_workload_status}",
            "Single source of planning truth",
            f"`current decision gate`: `{decision_gate}`",
            f"target-run freshness is `{target_run_freshness}`",
            "20260617 Active Queue Evidence-Upkeep Refresh",
            "20260617 Planning EntryPoint Proof Refresh",
        ],
        "README.en.md": [
            "Single source of planning truth",
            f"`current decision gate`: `{decision_gate}`",
            f"target-run freshness is `{target_run_freshness}`",
            f"`{codex_adapter_tier}` / {codex_capability_status}",
            f"`{claude_adapter_tier}` / {claude_workload_status}",
            "20260617 Active Queue Evidence-Upkeep Refresh",
            "20260617 Planning EntryPoint Proof Refresh",
        ],
        "README.zh-CN.md": [
            "唯一状态真源",
            f"`current decision gate`：`{decision_gate}`",
            f"target-run freshness 为 `{target_run_freshness}`",
            f"`{codex_adapter_tier}` / {codex_capability_status}",
            f"`{claude_adapter_tier}` / {claude_workload_status}",
            "20260617 Active Queue Evidence-Upkeep Refresh",
            "20260617 Planning EntryPoint Proof Refresh",
        ],
    }

    missing_tokens: list[str] = []
    for relative_path, tokens in required_tokens.items():
        path = root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in [item for item in tokens if item]:
            if token not in text:
                missing_tokens.append(f"{relative_path}:{token}")

    unexpected_tokens: list[str] = []
    stale_checks: dict[str, list[str]] = {
        "docs/strategy/positioning-and-competitive-layering.md": [
            "The active next-step implementation queue remains `Interactive Session Productization / GAP-035` through `GAP-039`.",
            "The next active product queue is generic, interactive, attach-first session productization.",
            "The current live posture is still `stale`",
            "latest 2026-06-09 recovery batch",
        ],
        "docs/strategy/current-best-end-state-blueprint.md": [
            "current active queue: `GAP-159..164`" if queue_id != "GAP-159..164" else "",
        ],
        "docs/product/interaction-model.md": [
            "The next active product queue is generic, interactive, attach-first session productization.",
            "current decision gate remains `refresh_evidence_first`" if decision_gate != "refresh_evidence_first" else "",
        ],
        "docs/README.md": [
            "`current decision gate`: `refresh_evidence_first`" if decision_gate != "refresh_evidence_first" else "",
            "`current live posture`: target-run freshness is `stale`" if target_run_freshness != "stale" else "",
            "Latest posture proof:\n- [20260609 Live Posture Recovery]" if queue_id == "Continuous-Execution" else "",
        ],
        "docs/backlog/README.md": [
            "`current decision gate` remains `refresh_evidence_first`" if decision_gate != "refresh_evidence_first" else "",
            "current live posture remains `stale`" if target_run_freshness != "stale" else "",
            "2026-06-09 recovery batch now proves Codex target-run recovery",
        ],
        "docs/plans/README.md": [
            "queue still must not be treated as the current active queue while `planning-status.json` keeps `GAP-159..164` active",
        ],
        "docs/plans/host-family-capability-operationalization-plan.md": [
            "Use this plan as a prepared follow-on queue, not as permission to start new implementation work while `planning-status.json` still keeps `GAP-159..164` as the active queue and this follow-on package inactive.",
            "current active queue: `GAP-159..164`",
        ],
        "docs/backlog/issue-ready-backlog.md": [
            "active queue reference: `GAP-159..164`" if queue_id != "GAP-159..164" else "",
        ],
        "docs/prd/governed-ai-coding-runtime-prd.md": [
            "The current active queue remains `GAP-159..164`" if queue_id != "GAP-159..164" else "",
        ],
        "README.md": [
            "`current decision gate`：`refresh_evidence_first`" if decision_gate != "refresh_evidence_first" else "",
            "`current live posture`：target-run freshness 为 `stale`" if target_run_freshness != "stale" else "",
            "`current decision gate`: `refresh_evidence_first`" if decision_gate != "refresh_evidence_first" else "",
            "`current live posture`: target-run freshness is `stale`" if target_run_freshness != "stale" else "",
        ],
        "README.en.md": [
            "`current decision gate`: `refresh_evidence_first`" if decision_gate != "refresh_evidence_first" else "",
            "`current live posture`: target-run freshness is `stale`" if target_run_freshness != "stale" else "",
        ],
        "README.zh-CN.md": [
            "`current decision gate`：`refresh_evidence_first`" if decision_gate != "refresh_evidence_first" else "",
            "`current live posture`：target-run freshness 为 `stale`" if target_run_freshness != "stale" else "",
        ],
    }
    for relative_path, tokens in stale_checks.items():
        path = root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in [item for item in tokens if item]:
            if token in text:
                unexpected_tokens.append(f"{relative_path}:{token}")

    promotion_guard_failures = _inspect_conditional_queue_promotion_guards(
        root=root,
        queue_id=queue_id,
        decision_gate=decision_gate,
    )
    unexpected_tokens.extend(promotion_guard_failures)

    return {
        "status": "pass",
        "status_path": status_path.resolve(strict=False).as_posix(),
        "status_id": payload.get("status_id"),
        "current_active_queue": payload.get("current_active_queue", {}).get("queue_id"),
        "current_decision_gate": payload.get("current_decision_gate", {}).get("selector"),
        "current_live_posture": payload.get("current_live_posture", {}).get("status"),
        "missing_fields": missing_fields,
        "missing_files": missing_files,
        "missing_tokens": missing_tokens,
        "unexpected_tokens": unexpected_tokens,
    }


def _inspect_conditional_queue_promotion_guards(*, root: Path, queue_id: str, decision_gate: str) -> list[str]:
    if queue_id != "GAP-159..164":
        return []

    guarded_expectations: dict[str, list[str]] = {
        "docs/plans/README.md": [
            "do not treat it as active work unless `planning-status.json` is promoted",
            "do not treat it as the current active queue unless the status file promotes it",
        ],
        "docs/backlog/README.md": [
            "both packages stay outside the current active queue until `planning-status.json` explicitly promotes a later follow-on",
            "The package stays inactive as current active work until a later promotion explicitly updates `planning-status.json`.",
        ],
        "docs/plans/host-family-capability-operationalization-plan.md": [
            "Activation requires explicit promotion evidence and rollback.",
            "Use this plan as a prepared follow-on queue, not as permission to start new implementation work while `planning-status.json` still keeps `Continuous-Execution` as the active queue and this follow-on package inactive.",
        ],
        "docs/plans/continuous-execution-readiness-and-rollout-plan.md": [
            "Continuous rollout starts only when all conditions are met:",
            "Task 8: Promote Continuous Rollout To Active",
        ],
    }

    failures: list[str] = []
    for relative_path, required_snippets in guarded_expectations.items():
        path = root / relative_path
        if not path.exists():
            failures.append(f"{relative_path}:missing conditional promotion guard file")
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in required_snippets:
            if snippet not in text:
                failures.append(f"{relative_path}:missing conditional promotion guard snippet `{snippet}`")

    if decision_gate == "defer_ltp_and_refresh_evidence":
        docs_readme = root / "docs" / "README.md"
        if docs_readme.exists():
            docs_text = docs_readme.read_text(encoding="utf-8")
            required = "current active queue: `GAP-159..164`"
            if required not in docs_text:
                failures.append(f"docs/README.md:missing active queue marker `{required}`")

    readme_history_requirement = {
        "README.md": "（历史恢复里程碑）",
        "README.en.md": "(historical recovery milestone)",
        "README.zh-CN.md": "（历史恢复里程碑）",
        "docs/README.md": "(historical recovery milestone)",
    }
    for relative_path, marker in readme_history_requirement.items():
        path = root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "20260609 Live Posture Recovery" not in text or marker not in text:
            failures.append(f"{relative_path}:missing historical recovery milestone marker for 20260609")

    return failures


def _load_json(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"planning status file is not readable: {path} ({exc})") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"planning status file is invalid JSON: {path} ({exc.msg})") from exc
    if not isinstance(payload, dict):
        raise ValueError("planning status file must be a JSON object")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
