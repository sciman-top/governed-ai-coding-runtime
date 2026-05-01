from __future__ import annotations

import datetime as dt
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATERIALIZER_PATH = ROOT / "scripts" / "materialize-runtime-evolution.py"
RETIREMENT_PATH = ROOT / "scripts" / "review-runtime-evolution-retirements.py"
ARCHITECTURE_PATH = ROOT / "docs" / "architecture" / "promotion-lifecycle.json"


def main() -> int:
    try:
        result = verify_promotion_lifecycle(repo_root=ROOT, as_of=dt.date.today())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def verify_promotion_lifecycle(*, repo_root: Path, as_of: dt.date) -> dict:
    materializer = _load_script(MATERIALIZER_PATH, "materialize_runtime_evolution_for_promotion")
    retirement = _load_script(RETIREMENT_PATH, "review_runtime_evolution_retirements_for_promotion")
    architecture = json.loads(ARCHITECTURE_PATH.read_text(encoding="utf-8"))

    invalid_reasons: list[str] = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_root = Path(tmp_dir)
        _copy_minimal_repo(repo_root=repo_root, temp_root=temp_root)
        apply_result = materializer.materialize_runtime_evolution(repo_root=temp_root, as_of=as_of, apply=True)
        lifecycle_manifest_path = (
            temp_root
            / "docs/change-evidence/runtime-evolution-promotions"
            / f"{as_of.strftime('%Y%m%d')}-runtime-evolution-promotion-lifecycle.json"
        )
        lifecycle_manifest = json.loads(lifecycle_manifest_path.read_text(encoding="utf-8"))

        if not all(_entry_is_safely_disabled_or_promotable(entry) for entry in lifecycle_manifest["entries"]):
            invalid_reasons.append("entries_missing_promotion_or_disable_guards")
        if not _retirement_guard_is_safe(lifecycle_manifest["retirement_guard"]):
            invalid_reasons.append("retirement_guard_is_unsafe")

        retirement_result = retirement.review_runtime_evolution_retirements(
            repo_root=temp_root,
            as_of=as_of + dt.timedelta(days=120),
            stale_after_days=30,
        )
        if retirement_result["retire_proposal_count"] < 1:
            invalid_reasons.append("retirement_review_did_not_produce_candidate_cleanup")
        guard = retirement_result["guard"]
        if guard.get("reviewed_asset_delete") is not False or guard.get("evidence_history_delete") is not False:
            invalid_reasons.append("retirement_guard_allows_reviewed_or_evidence_delete")

    if architecture.get("verification_command") != "python scripts/verify-promotion-lifecycle.py":
        invalid_reasons.append("architecture_verification_command_drift")

    if invalid_reasons:
        raise ValueError("invalid promotion lifecycle: " + ", ".join(invalid_reasons))

    return {
        "status": "pass",
        "as_of": as_of.isoformat(),
        "entrypoint": architecture["materialization_entrypoint"],
        "verification_command": architecture["verification_command"],
        "retirement_entrypoint": architecture["retirement_entrypoint"],
        "lifecycle_entry_count": len(lifecycle_manifest["entries"]),
        "retire_proposal_count": retirement_result["retire_proposal_count"],
    }


def _load_script(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _copy_minimal_repo(*, repo_root: Path, temp_root: Path) -> None:
    for relative in [
        "scripts/extract-ai-coding-experience.py",
        "scripts/materialize-runtime-evolution.py",
        "scripts/review-runtime-evolution-retirements.py",
        "schemas/examples/learning-efficiency-metrics/baseline.example.json",
        "schemas/examples/interaction-evidence/checklist-first-bugfix.example.json",
    ]:
        source = repo_root / relative
        target = temp_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def _entry_is_safely_disabled_or_promotable(entry: dict) -> bool:
    status = entry.get("status")
    kind = entry.get("asset_kind")
    enabled = entry.get("enabled_by_default")
    if kind in {"skill", "hook"} and status in {"disabled", "review", "test_ready"} and enabled is not False:
        return False
    return bool(entry.get("promotion_gate_refs")) and bool(entry.get("effect_metric_refs")) and bool(entry.get("rollback_ref"))


def _retirement_guard_is_safe(guard: dict) -> bool:
    return (
        guard.get("candidate_cleanup_only") is True
        and guard.get("preserve_evidence_history") is True
        and guard.get("reviewed_asset_delete") is False
    )


if __name__ == "__main__":
    raise SystemExit(main())
