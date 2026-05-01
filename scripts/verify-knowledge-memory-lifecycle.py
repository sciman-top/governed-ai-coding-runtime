from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR_PATH = ROOT / "scripts" / "extract-ai-coding-experience.py"
ARCHITECTURE_PATH = ROOT / "docs" / "architecture" / "knowledge-memory-lifecycle.json"


def main() -> int:
    try:
        result = verify_knowledge_memory_lifecycle(repo_root=ROOT, as_of=dt.date.today())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def verify_knowledge_memory_lifecycle(*, repo_root: Path, as_of: dt.date) -> dict:
    extractor = _load_extractor()
    review = extractor.inspect_ai_coding_experience(repo_root=repo_root, as_of=as_of)
    architecture = json.loads(ARCHITECTURE_PATH.read_text(encoding="utf-8"))

    invalid_reasons: list[str] = []
    if not all(_candidate_promotion_ready(item) for item in review["knowledge_candidates"]):
        invalid_reasons.append("knowledge_candidates_missing_source_or_verification")
    if not all(_pattern_promotion_ready(item) for item in review["pattern_candidates"]):
        invalid_reasons.append("pattern_candidates_missing_source_or_verification")
    if not all(_memory_record_complete(item, as_of=as_of) for item in review["memory_records"]):
        invalid_reasons.append("memory_records_missing_required_fields")
    if not _retirement_capability_preserves_history(extractor, as_of=as_of):
        invalid_reasons.append("retirement_path_does_not_preserve_audit_history")

    if architecture.get("promotion_requirements", {}).get("requires_source_evidence") is not True:
        invalid_reasons.append("architecture_missing_source_evidence_requirement")
    if architecture.get("retirement_guard", {}).get("preserve_audit_history") is not True:
        invalid_reasons.append("architecture_missing_audit_history_guard")

    if invalid_reasons:
        raise ValueError("invalid knowledge memory lifecycle: " + ", ".join(invalid_reasons))

    return {
        "status": "pass",
        "as_of": as_of.isoformat(),
        "knowledge_candidate_count": len(review["knowledge_candidates"]),
        "pattern_candidate_count": len(review["pattern_candidates"]),
        "memory_record_count": len(review["memory_records"]),
        "retirement_record_count": len(review["retirement_records"]),
        "entrypoint": architecture["entrypoint"],
        "verification_command": architecture["verification_command"],
    }


def _load_extractor():
    spec = importlib.util.spec_from_file_location("extract_ai_coding_experience_for_lifecycle", EXTRACTOR_PATH)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load extractor: {EXTRACTOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["extract_ai_coding_experience_for_lifecycle"] = module
    spec.loader.exec_module(module)
    return module


def _candidate_promotion_ready(candidate: dict) -> bool:
    readiness = candidate.get("promotion_readiness", {})
    return (
        readiness.get("source_evidence_attached") is True
        and readiness.get("verification_attached") is True
        and bool(candidate.get("source_refs"))
        and bool(candidate.get("verification_refs"))
    )


def _pattern_promotion_ready(candidate: dict) -> bool:
    return bool(candidate.get("source_refs")) and bool(candidate.get("verification_refs"))


def _memory_record_complete(record: dict, *, as_of: dt.date) -> bool:
    try:
        expires_at = dt.date.fromisoformat(record["expires_at"])
    except (KeyError, ValueError):
        return False
    return (
        bool(record.get("scope"))
        and bool(record.get("provenance"))
        and isinstance(record.get("confidence"), (float, int))
        and expires_at > as_of
        and bool(record.get("retrieval_evidence", {}).get("source_refs"))
        and bool(record.get("retrieval_evidence", {}).get("verification_refs"))
    )


def _retirement_capability_preserves_history(extractor, *, as_of: dt.date) -> bool:
    signal = extractor._score_signal(
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
    retirement_records = extractor._build_retirement_records(
        signals=[signal],
        as_of=as_of,
        retirement_score_ceiling=4,
    )
    if len(retirement_records) != 1:
        return False
    record = retirement_records[0]
    return record.get("audit_history_retained") is True and record.get("delete_active_evidence") is False


if __name__ == "__main__":
    raise SystemExit(main())
