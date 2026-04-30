from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_ROOT = ROOT / ".runtime" / "artifacts" / "ai-coding-experience"
DEFAULT_MIN_PROPOSAL_SCORE = 5
DEFAULT_MIN_SKILL_SCORE = 8


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract dry-run AI coding experience proposals.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--as-of", default=None, help="ISO date used for generated records; defaults to today.")
    parser.add_argument("--write-artifacts", action="store_true")
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    parser.add_argument("--min-proposal-score", type=int, default=DEFAULT_MIN_PROPOSAL_SCORE)
    parser.add_argument("--min-skill-score", type=int, default=DEFAULT_MIN_SKILL_SCORE)
    args = parser.parse_args()

    try:
        as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    except ValueError:
        print(f"invalid --as-of date: {args.as_of}", file=sys.stderr)
        return 1

    try:
        result = inspect_ai_coding_experience(
            repo_root=Path(args.repo_root),
            as_of=as_of,
            write_artifacts=args.write_artifacts,
            artifact_root=Path(args.artifact_root),
            min_proposal_score=args.min_proposal_score,
            min_skill_score=args.min_skill_score,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def inspect_ai_coding_experience(
    *,
    repo_root: Path,
    as_of: dt.date | None = None,
    write_artifacts: bool = False,
    artifact_root: Path | None = None,
    min_proposal_score: int = DEFAULT_MIN_PROPOSAL_SCORE,
    min_skill_score: int = DEFAULT_MIN_SKILL_SCORE,
) -> dict:
    if min_skill_score < min_proposal_score:
        raise ValueError("min_skill_score must be greater than or equal to min_proposal_score")

    root = repo_root.resolve(strict=False)
    today = as_of or dt.date.today()
    metrics_records = _load_json_records(
        root=root,
        candidates=[
            "schemas/examples/learning-efficiency-metrics",
            ".runtime/artifacts",
        ],
        filename_filter="learning-efficiency",
    )
    interaction_records = _load_json_records(
        root=root,
        candidates=[
            "schemas/examples/interaction-evidence",
            ".runtime/artifacts",
        ],
        filename_filter="interaction",
    )

    signals = _build_signals(
        metrics_records=metrics_records,
        interaction_records=interaction_records,
        min_proposal_score=min_proposal_score,
        min_skill_score=min_skill_score,
    )
    proposals = [_build_proposal(signal=signal, as_of=today) for signal in signals if signal["value_score"] >= min_proposal_score]
    skill_candidates = [
        _build_skill_manifest_candidate(signal=signal, as_of=today)
        for signal in signals
        if signal["value_score"] >= min_skill_score and signal["suggested_asset"] == "skill"
    ]
    quality_checks = _build_quality_checks(
        root=root,
        signals=signals,
        proposals=proposals,
        skill_candidates=skill_candidates,
        min_proposal_score=min_proposal_score,
        min_skill_score=min_skill_score,
    )
    invalid_reasons = _collect_invalid_reasons(quality_checks)

    result = {
        "status": "pass" if not invalid_reasons else "fail",
        "as_of": today.isoformat(),
        "mode": "dry_run",
        "mutation_allowed": False,
        "thresholds": {
            "min_proposal_score": min_proposal_score,
            "min_skill_score": min_skill_score,
        },
        "source_counts": {
            "learning_efficiency_metrics": len(metrics_records),
            "interaction_evidence": len(interaction_records),
        },
        "signals": signals,
        "proposal_count": len(proposals),
        "skill_manifest_candidate_count": len(skill_candidates),
        "proposals": proposals,
        "skill_manifest_candidates": skill_candidates,
        "quality_checks": quality_checks,
        "invalid_reasons": invalid_reasons,
        "artifact_refs": {},
    }

    if invalid_reasons:
        raise ValueError("invalid AI coding experience extraction: " + ", ".join(invalid_reasons))

    if write_artifacts:
        result["artifact_refs"] = _write_artifacts(root=artifact_root or DEFAULT_ARTIFACT_ROOT, result=result, as_of=today)

    return result


def _load_json_records(*, root: Path, candidates: list[str], filename_filter: str) -> list[dict]:
    records: list[dict] = []
    seen: set[Path] = set()
    for candidate in candidates:
        base = root / candidate
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.json")):
            if filename_filter not in path.as_posix():
                continue
            resolved = path.resolve(strict=False)
            if resolved in seen:
                continue
            seen.add(resolved)
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(payload, dict):
                payload["_source_ref"] = path.relative_to(root).as_posix()
                records.append(payload)
    return records


def _build_signals(
    *,
    metrics_records: list[dict],
    interaction_records: list[dict],
    min_proposal_score: int,
    min_skill_score: int,
) -> list[dict]:
    signals: list[dict] = []
    checklist_refs = _refs_with_checklist_pattern(metrics_records, interaction_records)
    if checklist_refs:
        signals.append(
            _score_signal(
                signal_id="ai-pattern.checklist-first-bugfix",
                pattern="checklist-first bug diagnosis before root-cause reasoning",
                source_refs=checklist_refs,
                suggested_asset="skill",
                recurrence=max(1, len(checklist_refs)),
                time_saved=2,
                risk_reduction=2,
                verification_strength=2,
                reuse_scope=2,
                maintenance_cost=1,
                ambiguity=1,
                staleness_risk=1,
                min_proposal_score=min_proposal_score,
                min_skill_score=min_skill_score,
            )
        )

    clarification_refs = [
        item["_source_ref"]
        for item in metrics_records
        if int(item.get("repeated_misunderstanding_count", 0)) > 0 or int(item.get("clarification_rounds", 0)) > 1
    ]
    if clarification_refs:
        signals.append(
            _score_signal(
                signal_id="ai-pattern.early-clarification",
                pattern="ask bounded clarification before repeated misalignment",
                source_refs=clarification_refs,
                suggested_asset="policy",
                recurrence=max(1, len(clarification_refs)),
                time_saved=1,
                risk_reduction=2,
                verification_strength=1,
                reuse_scope=2,
                maintenance_cost=1,
                ambiguity=1,
                staleness_risk=1,
                min_proposal_score=min_proposal_score,
                min_skill_score=min_skill_score,
            )
        )

    return signals


def _refs_with_checklist_pattern(metrics_records: list[dict], interaction_records: list[dict]) -> list[str]:
    refs: list[str] = []
    for item in metrics_records:
        if int(item.get("observation_prompt_count", 0)) > 0 or int(item.get("term_explanation_count", 0)) > 0:
            refs.append(item["_source_ref"])
    for item in interaction_records:
        if item.get("observation_checklist") or item.get("terms_explained"):
            refs.append(item["_source_ref"])
    return sorted(set(refs))


def _score_signal(
    *,
    signal_id: str,
    pattern: str,
    source_refs: list[str],
    suggested_asset: str,
    recurrence: int,
    time_saved: int,
    risk_reduction: int,
    verification_strength: int,
    reuse_scope: int,
    maintenance_cost: int,
    ambiguity: int,
    staleness_risk: int,
    min_proposal_score: int,
    min_skill_score: int,
) -> dict:
    value_score = (
        recurrence * 2
        + time_saved
        + risk_reduction * 2
        + verification_strength
        + reuse_scope
        - maintenance_cost
        - ambiguity
        - staleness_risk
    )
    if value_score >= min_skill_score:
        disposition = "skill_candidate" if suggested_asset == "skill" else "proposal_candidate"
    elif value_score >= min_proposal_score:
        disposition = "proposal_candidate"
    else:
        disposition = "evidence_only"
    return {
        "signal_id": signal_id,
        "source_refs": source_refs,
        "pattern": pattern,
        "suggested_asset": suggested_asset,
        "score_formula": "recurrence*2 + time_saved + risk_reduction*2 + verification_strength + reuse_scope - maintenance_cost - ambiguity - staleness_risk",
        "recurrence": recurrence,
        "time_saved": time_saved,
        "risk_reduction": risk_reduction,
        "verification_strength": verification_strength,
        "reuse_scope": reuse_scope,
        "maintenance_cost": maintenance_cost,
        "ambiguity": ambiguity,
        "staleness_risk": staleness_risk,
        "value_score": value_score,
        "disposition": disposition,
    }


def _build_quality_checks(
    *,
    root: Path,
    signals: list[dict],
    proposals: list[dict],
    skill_candidates: list[dict],
    min_proposal_score: int,
    min_skill_score: int,
) -> dict:
    return {
        "source_refs_exist": _all_source_refs_exist(root, signals, proposals),
        "scores_recomputable": all(_score_is_recomputable(signal) for signal in signals),
        "proposal_thresholds_respected": _proposal_thresholds_respected(
            signals=signals,
            proposals=proposals,
            min_proposal_score=min_proposal_score,
        ),
        "skill_thresholds_respected": _skill_thresholds_respected(
            signals=signals,
            skill_candidates=skill_candidates,
            min_skill_score=min_skill_score,
        ),
        "proposals_non_mutating": all(
            proposal.get("mutation_guard", {}).get("allows_direct_mutation") is False for proposal in proposals
        ),
        "proposals_human_review_required": all(
            proposal.get("human_review", {}).get("required") is True for proposal in proposals
        ),
        "skill_candidates_disabled": all(skill.get("default_enabled") is False for skill in skill_candidates),
        "skill_candidates_low_or_medium_risk_only": all(
            skill.get("risk_tier") in {"low", "medium"} for skill in skill_candidates
        ),
    }


def _collect_invalid_reasons(quality_checks: dict) -> list[str]:
    return [name for name, passed in quality_checks.items() if passed is not True]


def _all_source_refs_exist(root: Path, signals: list[dict], proposals: list[dict]) -> bool:
    refs: set[str] = set()
    for item in signals + proposals:
        for ref in item.get("source_refs", []):
            if isinstance(ref, str):
                refs.add(ref)
    return bool(refs) and all((root / ref).exists() for ref in refs)


def _score_is_recomputable(signal: dict) -> bool:
    expected = (
        int(signal.get("recurrence", 0)) * 2
        + int(signal.get("time_saved", 0))
        + int(signal.get("risk_reduction", 0)) * 2
        + int(signal.get("verification_strength", 0))
        + int(signal.get("reuse_scope", 0))
        - int(signal.get("maintenance_cost", 0))
        - int(signal.get("ambiguity", 0))
        - int(signal.get("staleness_risk", 0))
    )
    return signal.get("value_score") == expected


def _proposal_thresholds_respected(*, signals: list[dict], proposals: list[dict], min_proposal_score: int) -> bool:
    proposal_signal_ids = {
        "ai-pattern." + proposal["proposal_id"].replace("proposal.", "", 1)
        for proposal in proposals
        if isinstance(proposal.get("proposal_id"), str)
    }
    promoted_signal_ids = {signal["signal_id"] for signal in signals if signal.get("value_score", 0) >= min_proposal_score}
    low_signal_ids = {signal["signal_id"] for signal in signals if signal.get("value_score", 0) < min_proposal_score}
    return promoted_signal_ids.issubset(proposal_signal_ids) and proposal_signal_ids.isdisjoint(low_signal_ids)


def _skill_thresholds_respected(*, signals: list[dict], skill_candidates: list[dict], min_skill_score: int) -> bool:
    skill_signal_ids = {
        "ai-pattern." + skill["skill_id"].replace("skill.", "", 1)
        for skill in skill_candidates
        if isinstance(skill.get("skill_id"), str)
    }
    expected_skill_ids = {
        signal["signal_id"]
        for signal in signals
        if signal.get("value_score", 0) >= min_skill_score and signal.get("suggested_asset") == "skill"
    }
    low_skill_ids = {signal["signal_id"] for signal in signals if signal.get("value_score", 0) < min_skill_score}
    return expected_skill_ids.issubset(skill_signal_ids) and skill_signal_ids.isdisjoint(low_skill_ids)


def _build_proposal(*, signal: dict, as_of: dt.date) -> dict:
    category = "skill" if signal["suggested_asset"] == "skill" else "policy"
    return {
        "schema_version": "0.1-draft",
        "proposal_id": "proposal." + signal["signal_id"].replace("ai-pattern.", "").replace("_", "-"),
        "source_refs": signal["source_refs"],
        "proposal_category": category,
        "proposal_scope": "unified_governance",
        "summary": f"Promote repeated AI coding pattern: {signal['pattern']}.",
        "rationale": (
            f"Signal scored {signal['value_score']} from recurrence, time saved, risk reduction, "
            "verification strength, reuse scope, and maintenance risk."
        ),
        "expected_impact": "Reduce repeated reasoning drift and make the pattern reusable without hidden memory authority.",
        "risk_posture": "low" if signal["value_score"] >= 8 else "medium",
        "human_review": {
            "required": True,
            "reviewer_role": "runtime maintainer",
            "approval_ref": "not-approved",
        },
        "mutation_guard": {
            "allows_direct_mutation": False,
            "enforcement_note": "Proposal records are advisory and cannot mutate policy, skills, hooks, or controls directly.",
        },
        "rollback_ref": "Remove generated proposal artifacts; no runtime behavior is changed by proposal generation.",
        "status": "proposed",
        "related_task_ids": ["runtime-evolution-ai-coding-experience"],
        "proposed_changes": [
            f"Create or update a governed {category} asset after human review.",
            "Add tests or gates before enabling any executable behavior.",
        ],
        "notes": f"Generated on {as_of.isoformat()} by dry-run AI coding experience extraction.",
    }


def _build_skill_manifest_candidate(*, signal: dict, as_of: dt.date) -> dict:
    slug = signal["signal_id"].replace("ai-pattern.", "").replace("_", "-")
    return {
        "schema_version": "0.1-draft",
        "skill_id": "skill." + slug,
        "display_name": "Checklist-first bug diagnosis",
        "version": "0.1.0-draft",
        "description": "Use checklist-first observation before root-cause reasoning when bug evidence is incomplete.",
        "entrypoint": f"skills/{slug}/SKILL.md",
        "input_modes": ["prompt_only", "file_context"],
        "risk_tier": "low",
        "capabilities": [
            "Restate the bug target before proposing a fix.",
            "Ask for request, log, repro, and last-known-good observations when missing.",
            "Keep the pattern advisory until project gates validate the fix.",
        ],
        "provenance": {
            "source": ", ".join(signal["source_refs"]),
            "version_or_digest": as_of.isoformat(),
        },
        "compatibility": {
            "minimum_kernel_version": "0.1-draft",
            "required_contracts": [
                "interaction-evidence",
                "learning-efficiency-metrics",
                "controlled-improvement-proposal",
            ],
        },
        "default_enabled": False,
        "requires_approval": False,
        "repo_scopes": ["all"],
        "tags": ["ai-coding-experience", "bugfix", "skill-candidate"],
        "notes": "Candidate only; install no skill until human review and tests approve it.",
    }


def _write_artifacts(*, root: Path, result: dict, as_of: dt.date) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / f"{as_of.strftime('%Y%m%d')}-ai-coding-experience-review.json"
    md_path = root / f"{as_of.strftime('%Y%m%d')}-ai-coding-experience-review.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(result), encoding="utf-8")
    return {
        "json": json_path.resolve(strict=False).as_posix(),
        "markdown": md_path.resolve(strict=False).as_posix(),
    }


def _render_markdown(result: dict) -> str:
    signal_lines = [
        f"- `{item['signal_id']}`: score `{item['value_score']}` / `{item['disposition']}` / {item['pattern']}"
        for item in result["signals"]
    ]
    proposal_lines = [
        f"- `{item['proposal_id']}`: `{item['proposal_category']}` / `{item['risk_posture']}` / `{item['status']}`"
        for item in result["proposals"]
    ]
    skill_lines = [
        f"- `{item['skill_id']}`: `{item['risk_tier']}` / default_enabled=`{str(item.get('default_enabled')).lower()}`"
        for item in result["skill_manifest_candidates"]
    ]
    return (
        "# AI Coding Experience Review\n\n"
        "## Summary\n"
        f"- as_of: `{result['as_of']}`\n"
        f"- mode: `{result['mode']}`\n"
        f"- mutation_allowed: `{str(result['mutation_allowed']).lower()}`\n"
        f"- proposal_count: `{result['proposal_count']}`\n"
        f"- skill_manifest_candidate_count: `{result['skill_manifest_candidate_count']}`\n\n"
        "## Signals\n"
        + ("\n".join(signal_lines) if signal_lines else "- none")
        + "\n\n## Proposals\n"
        + ("\n".join(proposal_lines) if proposal_lines else "- none")
        + "\n\n## Skill Manifest Candidates\n"
        + ("\n".join(skill_lines) if skill_lines else "- none")
        + "\n\n## Guard\n"
        "- Generated proposals and skill manifests are advisory; they do not install or enable behavior.\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
