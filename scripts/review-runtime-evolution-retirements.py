from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL_ROOT = ROOT / "skills" / "candidates"
DEFAULT_PROPOSAL_ROOT = ROOT / "docs" / "change-evidence" / "runtime-evolution-proposals"
DEFAULT_PROMOTION_ROOT = ROOT / "docs" / "change-evidence" / "runtime-evolution-promotions"


def main() -> int:
    parser = argparse.ArgumentParser(description="Review runtime evolution candidates for retire/delete proposals.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--as-of", default=None)
    parser.add_argument("--stale-after-days", type=int, default=90)
    args = parser.parse_args()

    try:
        as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
        result = review_runtime_evolution_retirements(
            repo_root=Path(args.repo_root),
            as_of=as_of,
            stale_after_days=args.stale_after_days,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def review_runtime_evolution_retirements(*, repo_root: Path, as_of: dt.date, stale_after_days: int = 90) -> dict:
    if stale_after_days < 1:
        raise ValueError("stale_after_days must be positive")
    root = repo_root.resolve(strict=False)
    skill_root = root / "skills" / "candidates"
    candidates = []
    retire_proposals = []
    seen_asset_ids: set[str] = set()
    for manifest_path in sorted(skill_root.glob("*/skill-manifest.json")) if skill_root.exists() else []:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        generated_on = _parse_generated_on(manifest)
        age_days = (as_of - generated_on).days if generated_on else 0
        candidate = {
            "skill_id": manifest.get("skill_id"),
            "path": manifest_path.relative_to(root).as_posix(),
            "default_enabled": manifest.get("default_enabled"),
            "risk_tier": manifest.get("risk_tier"),
            "generated_on": generated_on.isoformat() if generated_on else None,
            "age_days": age_days,
            "stale": age_days > stale_after_days,
            "reviewed_asset": False,
        }
        candidates.append(candidate)
        duplicate = candidate["skill_id"] in seen_asset_ids
        if candidate["skill_id"]:
            seen_asset_ids.add(candidate["skill_id"])
        if candidate["stale"] and candidate["default_enabled"] is False:
            retire_proposals.append(
                {
                    "proposal_id": "proposal.retire." + str(candidate["skill_id"]).replace("skill.", "", 1),
                    "source_refs": [candidate["path"]],
                    "proposal_category": "skill",
                    "proposal_scope": "unified_governance",
                    "summary": f"Retire stale disabled skill candidate {candidate['skill_id']}.",
                    "risk_posture": "low",
                    "allows_direct_delete": False,
                    "status": "proposed",
                }
            )
        elif duplicate:
            retire_proposals.append(
                {
                    "proposal_id": "proposal.retire.duplicate." + str(candidate["skill_id"]).replace("skill.", "", 1),
                    "source_refs": [candidate["path"]],
                    "proposal_category": "skill",
                    "proposal_scope": "unified_governance",
                    "summary": f"Retire duplicate skill candidate {candidate['skill_id']}.",
                    "risk_posture": "low",
                    "allows_direct_delete": False,
                    "status": "proposed",
                }
            )

    retire_proposals.extend(_review_proposal_candidates(root=root, as_of=as_of, stale_after_days=stale_after_days))
    retire_proposals.extend(_review_promotion_lifecycle(root=root))
    return {
        "status": "pass",
        "as_of": as_of.isoformat(),
        "mode": "dry_run",
        "mutation_allowed": False,
        "stale_after_days": stale_after_days,
        "candidate_count": len(candidates),
        "retire_proposal_count": len(retire_proposals),
        "candidates": candidates,
        "retire_proposals": retire_proposals,
        "guard": {
            "direct_delete": False,
            "enabled_asset_delete": False,
            "reviewed_asset_delete": False,
            "evidence_history_delete": False,
            "requires_proposal_before_delete": True,
        },
    }


def _parse_generated_on(manifest: dict) -> dt.date | None:
    value = manifest.get("provenance", {}).get("version_or_digest")
    if not isinstance(value, str):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def _review_proposal_candidates(*, root: Path, as_of: dt.date, stale_after_days: int) -> list[dict]:
    proposal_root = root / "docs" / "change-evidence" / "runtime-evolution-proposals"
    proposals: list[dict] = []
    for proposal_path in sorted(proposal_root.glob("*.json")) if proposal_root.exists() else []:
        proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
        generated_on = _parse_generated_on_from_notes(proposal.get("notes"))
        age_days = (as_of - generated_on).days if generated_on else 0
        if age_days <= stale_after_days and proposal.get("risk_posture") != "high":
            continue
        reason = "stale" if age_days > stale_after_days else "harmful"
        proposals.append(
            {
                "proposal_id": "proposal.retire." + str(proposal["proposal_id"]).replace("proposal.", "", 1),
                "source_refs": [proposal_path.relative_to(root).as_posix()],
                "proposal_category": proposal.get("proposal_category", "policy"),
                "proposal_scope": "unified_governance",
                "summary": f"Retire {reason} proposal candidate {proposal['proposal_id']}.",
                "risk_posture": "low" if reason == "stale" else "medium",
                "allows_direct_delete": False,
                "status": "proposed",
            }
        )
    return proposals


def _review_promotion_lifecycle(*, root: Path) -> list[dict]:
    promotion_root = root / "docs" / "change-evidence" / "runtime-evolution-promotions"
    proposals: list[dict] = []
    for manifest_path in sorted(promotion_root.glob("*.json")) if promotion_root.exists() else []:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest.get("entries", [])
        duplicate_paths: dict[str, list[str]] = {}
        for entry in entries:
            key = str(entry.get("asset_id"))
            duplicate_paths.setdefault(key, []).append(str(entry.get("materialized_path")))
            if entry.get("replaced_by"):
                proposals.append(
                    {
                        "proposal_id": "proposal.retire.replaced." + key.replace(".", "-", 1),
                        "source_refs": [manifest_path.relative_to(root).as_posix()],
                        "proposal_category": entry.get("asset_kind", "skill"),
                        "proposal_scope": "unified_governance",
                        "summary": f"Retire replaced candidate {key}.",
                        "risk_posture": "low",
                        "allows_direct_delete": False,
                        "status": "proposed",
                    }
                )
        for asset_id, paths in duplicate_paths.items():
            if len(paths) < 2:
                continue
            proposals.append(
                {
                    "proposal_id": "proposal.retire.duplicate." + asset_id.replace(".", "-", 1),
                    "source_refs": [manifest_path.relative_to(root).as_posix()],
                    "proposal_category": "skill",
                    "proposal_scope": "unified_governance",
                    "summary": f"Retire duplicate lifecycle entries for {asset_id}.",
                    "risk_posture": "low",
                    "allows_direct_delete": False,
                    "status": "proposed",
                }
            )
    return proposals


def _parse_generated_on_from_notes(notes: object) -> dt.date | None:
    if not isinstance(notes, str):
        return None
    for token in notes.split():
        try:
            return dt.date.fromisoformat(token)
        except ValueError:
            continue
    return None


if __name__ == "__main__":
    raise SystemExit(main())
