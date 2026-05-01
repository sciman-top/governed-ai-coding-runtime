from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORTFOLIO = ROOT / "docs" / "architecture" / "capability-portfolio-classifier.json"

REQUIRED_EXTERNAL_IDS = {
    "external-codex-host-surface",
    "external-claude-code-provider-surface",
    "external-mcp-adapter-boundary",
    "external-opa-policy-boundary",
    "external-langgraph-workflow-vocabulary",
    "external-openhands-execution-boundary",
    "external-swe-agent-repair-loop",
    "external-hermes-governed-skill-memory",
    "external-letta-memory-blocks",
    "external-mem0-memory-lifecycle",
    "external-aider-repo-map",
    "external-cline-permission-surface",
    "external-openai-cookbook-evals",
    "external-agent-skills-governed-surface",
}

REQUIRED_EXISTING_IDS = {
    "existing-borrowing-matrix-research",
    "existing-benchmark-borrowing-notes",
    "existing-core-principles-policy",
    "existing-current-source-compatibility-guard",
    "existing-target-repo-governance-baseline",
    "existing-runtime-evolution-review",
    "existing-ai-coding-experience-extraction",
    "existing-claim-drift-sentinel",
    "existing-host-feedback-surface",
}

REQUIRED_OUTCOMES = {
    "add",
    "keep",
    "improve",
    "merge",
    "deprecate",
    "retire",
    "delete_candidate",
}

SPECIAL_OUTCOMES = {"deprecate", "retire", "delete_candidate"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _check_local_refs(repo_root: Path, entry_id: str, refs: list[str], bucket: str, errors: list[str]) -> None:
    for ref in refs:
      if _is_url(ref):
          continue
      if not (repo_root / ref).exists():
          errors.append(f"missing {bucket}: {entry_id}::{ref}")


def verify_capability_portfolio(repo_root: Path | None = None, portfolio_path: Path | None = None) -> dict[str, Any]:
    repo_root = repo_root or ROOT
    portfolio_path = portfolio_path or DEFAULT_PORTFOLIO
    portfolio = _load_json(portfolio_path)
    errors: list[str] = []

    entries = portfolio.get("entries", [])
    by_id = {entry.get("id"): entry for entry in entries if isinstance(entry, dict)}
    outcomes = {entry.get("lifecycle_outcome") for entry in entries if isinstance(entry, dict)}

    missing_external = sorted(REQUIRED_EXTERNAL_IDS - set(by_id))
    if missing_external:
        errors.append(f"missing external entries: {', '.join(missing_external)}")

    missing_existing = sorted(REQUIRED_EXISTING_IDS - set(by_id))
    if missing_existing:
        errors.append(f"missing existing entries: {', '.join(missing_existing)}")

    missing_outcomes = sorted(REQUIRED_OUTCOMES - outcomes)
    if missing_outcomes:
        errors.append(f"missing lifecycle outcomes: {', '.join(missing_outcomes)}")

    for doc_ref in portfolio.get("required_doc_refs", []):
        path = doc_ref.get("path")
        if path and not (repo_root / path).exists():
            errors.append(f"missing doc refs: {path}:missing")

    for evidence_ref in portfolio.get("evidence_refs", []):
        if evidence_ref and not (repo_root / evidence_ref).exists():
            errors.append(f"missing evidence refs: {evidence_ref}")

    for entry in entries:
        entry_id = entry.get("id", "<missing-id>")
        effect = entry.get("effect_hypothesis", {})
        missing_effect_fields = [
            field
            for field in (
                "expected_benefit",
                "expected_cost",
                "expected_risk",
                "effect_metric",
                "verification_command",
            )
            if not effect.get(field)
        ]
        if missing_effect_fields:
            errors.append(f"invalid effect hypothesis: {entry_id}::{', '.join(missing_effect_fields)}")

        if entry.get("lifecycle_outcome") in SPECIAL_OUTCOMES:
            for field in ("retention_rule", "future_trigger"):
                if not entry.get(field):
                    errors.append(f"invalid special outcome entry: {entry_id}::{field}")

        source_refs = entry.get("source_refs", [])
        review_refs = entry.get("review_refs", [])
        _check_local_refs(repo_root, entry_id, source_refs, "source refs", errors)
        _check_local_refs(repo_root, entry_id, review_refs, "review refs", errors)

    result = {
        "status": "pass" if not errors else "fail",
        "portfolio_path": str(portfolio_path.relative_to(repo_root)),
        "entry_count": len(entries),
        "errors": errors,
    }
    return result


def main() -> int:
    result = verify_capability_portfolio()
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
