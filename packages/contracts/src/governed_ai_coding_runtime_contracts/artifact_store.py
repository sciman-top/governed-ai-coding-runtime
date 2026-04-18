"""Local artifact persistence for governed runtime runs."""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import json
import re


_SLUG = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    task_id: str
    run_id: str
    kind: str
    label: str
    relative_path: str
    created_at: str
    risky: bool
    risk_classification: str | None = None


class LocalArtifactStore:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def write_text(self, *, task_id: str, run_id: str, kind: str, label: str, content: str) -> ArtifactRef:
        relative_path = self._relative_path(task_id=task_id, run_id=run_id, kind=kind, label=label, suffix=".txt")
        path = self._root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return self._build_ref(task_id=task_id, run_id=run_id, kind=kind, label=label, relative_path=relative_path)

    def write_json(self, *, task_id: str, run_id: str, kind: str, label: str, payload: dict) -> ArtifactRef:
        relative_path = self._relative_path(task_id=task_id, run_id=run_id, kind=kind, label=label, suffix=".json")
        path = self._root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return self._build_ref(task_id=task_id, run_id=run_id, kind=kind, label=label, relative_path=relative_path)

    def _build_ref(self, *, task_id: str, run_id: str, kind: str, label: str, relative_path: str) -> ArtifactRef:
        risk_classification = classify_artifact(kind=kind, label=label)
        return ArtifactRef(
            task_id=task_id,
            run_id=run_id,
            kind=kind,
            label=label,
            relative_path=relative_path,
            created_at=datetime.now(UTC).isoformat(),
            risky=risk_classification is not None,
            risk_classification=risk_classification,
        )

    def _relative_path(self, *, task_id: str, run_id: str, kind: str, label: str, suffix: str) -> str:
        return "/".join(
            [
                _clean("artifacts"),
                _clean(task_id),
                _clean(run_id),
                _clean(kind),
                f"{_clean(label)}{suffix}",
            ]
        )


def classify_artifact(*, kind: str, label: str) -> str | None:
    normalized = f"{kind}:{label}".lower()
    if "release" in normalized or "publish" in normalized or "package" in normalized:
        return "release_adjacent"
    if "dependency" in normalized or "lockfile" in normalized:
        return "dependency"
    if "ci" in normalized or "workflow" in normalized:
        return "ci"
    return None


def _clean(value: str) -> str:
    cleaned = _SLUG.sub("-", value.strip()).strip("-")
    return cleaned or "artifact"
