"""Synchronous local worker primitives for governed execution."""

from collections.abc import Callable

from governed_ai_coding_runtime_contracts.execution_runtime import GovernedRunContext, WorkerExecutionResult


class SynchronousLocalWorker:
    def __init__(
        self,
        *,
        worker_id: str,
        handler: Callable[[GovernedRunContext], WorkerExecutionResult],
    ) -> None:
        if not worker_id.strip():
            msg = "worker_id is required"
            raise ValueError(msg)
        self.worker_id = worker_id
        self._handler = handler

    def execute(self, context: GovernedRunContext) -> WorkerExecutionResult:
        return self._handler(context)
