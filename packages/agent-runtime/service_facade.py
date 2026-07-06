"""Service-shaped facade over repo-local read-only runtime surfaces."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.agent_continuity import LocalAgentContinuityIndex
from governed_ai_coding_runtime_contracts.operator_queries import query_operator_task_surface
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeStatusStore, runtime_snapshot_to_dict


class RuntimeServiceFacade:
    def __init__(
        self,
        *,
        repo_root: str | Path,
        task_root: str | Path | None = None,
        tracer: Any | None = None,
    ) -> None:
        self._repo_root = Path(repo_root)
        self._task_root = Path(task_root) if task_root else self._repo_root / ".runtime" / "tasks"
        self._runtime_root = self._task_root.parent
        self._tracer = tracer

    def operator_status(self) -> dict:
        snapshot = RuntimeStatusStore(
            self._task_root,
            self._repo_root,
            runtime_root=self._runtime_root,
        ).snapshot()
        return {
            "status": "ok",
            "payload": runtime_snapshot_to_dict(snapshot),
            "service_boundary": "control-plane",
            "read_only": True,
        }

    def operator_inspect_evidence(
        self,
        *,
        task_id: str,
        run_id: str | None = None,
    ) -> dict:
        query = query_operator_task_surface(
            task_root=self._task_root,
            task_id=task_id,
            run_id=run_id,
            runtime_root=self._runtime_root,
        )
        return {
            "status": "ok",
            "payload": {
                "task_id": query.task_id,
                "run_id": query.run_id,
                "task_found": query.task_found,
                "current_state": query.current_state,
                "active_run_id": query.active_run_id,
                "evidence_refs": query.evidence_refs,
                "verification_refs": query.verification_refs,
                "interaction_posture": query.interaction_posture,
                "latest_task_restatement": query.latest_task_restatement,
                "interaction_budget_status": query.interaction_budget_status,
                "clarification_active": query.clarification_active,
                "latest_compression_action": query.latest_compression_action,
                "outstanding_observation_items_count": query.outstanding_observation_items_count,
            },
            "service_boundary": "control-plane",
            "read_only": True,
        }

    def operator_inspect_handoff(
        self,
        *,
        task_id: str,
        run_id: str | None = None,
        handoff_ref: str | None = None,
    ) -> dict:
        query = query_operator_task_surface(
            task_root=self._task_root,
            task_id=task_id,
            run_id=run_id,
            runtime_root=self._runtime_root,
        )
        handoff_refs = query.handoff_refs
        if handoff_ref:
            handoff_refs = [ref for ref in handoff_refs if ref == handoff_ref]
        return {
            "status": "ok",
            "payload": {
                "task_id": query.task_id,
                "run_id": query.run_id,
                "task_found": query.task_found,
                "current_state": query.current_state,
                "active_run_id": query.active_run_id,
                "handoff_refs": handoff_refs,
                "replay_refs": query.replay_refs,
                "artifact_refs": query.artifact_refs,
            },
            "service_boundary": "control-plane",
            "read_only": True,
        }

    def operator_search_context(
        self,
        *,
        index_root: str | Path | None = None,
        repo_id: str | None = None,
        tool_family: str | None = None,
        account_alias: str | None = None,
        provider_alias: str | None = None,
        include_expired: bool = False,
    ) -> dict:
        root = Path(index_root) if index_root else self._repo_root / ".runtime" / "agent-continuity"
        result = LocalAgentContinuityIndex(root).search(
            repo_id=repo_id,
            tool_family=tool_family,
            account_alias=account_alias,
            provider_alias=provider_alias,
            include_expired=include_expired,
        )
        result["service_boundary"] = "control-plane"
        result["read_only"] = True
        return result

    def operator_write_handoff(
        self,
        *,
        record: dict,
        index_root: str | Path | None = None,
    ) -> dict:
        root = Path(index_root) if index_root else self._repo_root / ".runtime" / "agent-continuity"
        result = LocalAgentContinuityIndex(root).write_record(record).to_dict()
        result["service_boundary"] = "control-plane"
        return result

    def health(self) -> dict:
        return {
            "service": "control-plane",
            "repo_root": self._repo_root.as_posix(),
            "task_root": self._task_root.as_posix(),
            "status": "ok",
        }
