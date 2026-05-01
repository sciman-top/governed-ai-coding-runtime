from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        result = inspect_governance_hub_certification(repo_root=ROOT)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def inspect_governance_hub_certification(*, repo_root: Path) -> dict:
    builder = _load_builder()
    result = builder(
        repo_root=repo_root,
        config_path=repo_root / "docs" / "architecture" / "governance-hub-certification.json",
    )
    failures: list[str] = []
    if result["missing_artifact_refs"]:
        failures.append("missing_artifact_refs")
    if result["missing_host_statement_refs"]:
        failures.append("missing_host_statement_refs")
    if result["missing_outcomes"]:
        failures.append("missing_outcomes")
    if result["special_entries_without_future_trigger"]:
        failures.append("missing_future_trigger")
    if not all(result["loop_status"].values()):
        failures.append("non_executable_loop")
    if result["effect_feedback"]["after_overall_status"] != "pass":
        failures.append("target_repo_effect_not_passing")
    if not result["effect_feedback"]["after_evidence_complete"]:
        failures.append("target_repo_effect_evidence_incomplete")
    if not result["host_posture"]["no_host_competition_claim"]:
        failures.append("host_competition_claim_detected")

    result["status"] = "fail" if failures else "pass"
    result["invalid_reasons"] = failures
    result["final_status"] = "executable" if not failures else "partial"
    return result


def _load_builder():
    script_path = ROOT / "scripts" / "build-governance-hub-certification.py"
    spec = importlib.util.spec_from_file_location("build_governance_hub_certification_script", script_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_governance_hub_certification


if __name__ == "__main__":
    raise SystemExit(main())
