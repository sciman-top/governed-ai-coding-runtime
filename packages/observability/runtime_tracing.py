"""Lightweight runtime tracing hooks for service boundaries."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Iterator


@dataclass(frozen=True, slots=True)
class RuntimeTraceEvent:
    name: str
    started_at: str
    finished_at: str
    attributes: dict


@dataclass(slots=True)
class RuntimeTracer:
    """OpenTelemetry-shaped hook surface without requiring extra dependencies."""

    _events: list[RuntimeTraceEvent] = field(default_factory=list)

    @contextmanager
    def start_span(self, name: str, *, attributes: dict | None = None) -> Iterator[dict]:
        started_at = datetime.now(UTC).isoformat()
        carrier = {"name": name, "attributes": dict(attributes or {}), "started_at": started_at}
        try:
            yield carrier
        finally:
            finished_at = datetime.now(UTC).isoformat()
            self._events.append(
                RuntimeTraceEvent(
                    name=name,
                    started_at=started_at,
                    finished_at=finished_at,
                    attributes=dict(carrier["attributes"]),
                )
            )

    def events(self) -> list[RuntimeTraceEvent]:
        return list(self._events)
