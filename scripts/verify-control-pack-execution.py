from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "schemas" / "control-packs"
DOMAIN_NAMES = (
    "policies",
    "gates",
    "hooks",
    "evals",
    "workflows",
    "skills",
    "knowledge",
    "memory",
    "evidence",
    "rollback",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _looks_like_command(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered.startswith(("python ", "pwsh ", "powershell ", "git ", "node "))


def _path_exists(repo_root: Path, ref: str) -> bool:
    return (repo_root / ref).exists()


def inspect_control_pack_execution(*, repo_root: Path | None = None) -> dict[str, Any]:
    repo_root = repo_root or ROOT
    packs = sorted(PACK_ROOT.glob("*.json"))
    errors: list[str] = []
    inspected: list[dict[str, Any]] = []

    if not packs:
      errors.append("no runtime-consumable control packs found")

    for pack_path in packs:
        pack = _load_json(pack_path)
        pack_errors: list[str] = []

        ownership = pack.get("field_ownership", {})
        unified = ownership.get("unified_kernel_fields", [])
        target = ownership.get("target_repo_input_fields", [])
        overlap = sorted(set(unified) & set(target))
        if overlap:
            pack_errors.append("field ownership overlap: " + ", ".join(overlap))
        if any(str(field).startswith("repo_profile_requirements.") for field in unified):
            pack_errors.append("unified kernel fields must not claim repo_profile_requirements.*")
        if any(not str(field).startswith("repo_profile_requirements.") for field in target):
            pack_errors.append("target repo input fields must stay under repo_profile_requirements.*")

        execution = pack.get("execution_contract", {})
        mode_counts = {"runnable": 0, "verifiable": 0}
        for domain in DOMAIN_NAMES:
            refs = execution.get(domain)
            if not isinstance(refs, list) or not refs:
                pack_errors.append(f"missing execution domain: {domain}")
                continue
            for ref in refs:
                ref_id = ref.get("id", "<missing-id>")
                source_ref = str(ref.get("source_ref", "")).strip()
                runtime_ref = str(ref.get("runtime_ref", "")).strip()
                verification_ref = str(ref.get("verification_ref", "")).strip()
                mode = str(ref.get("mode", "")).strip()
                if mode in mode_counts:
                    mode_counts[mode] += 1
                if not source_ref or not runtime_ref or not verification_ref or not mode:
                    pack_errors.append(f"incomplete execution ref: {domain}::{ref_id}")
                    continue
                if not _path_exists(repo_root, source_ref):
                    pack_errors.append(f"missing source_ref: {domain}::{ref_id}::{source_ref}")
                if not (_path_exists(repo_root, runtime_ref) or _looks_like_command(runtime_ref)):
                    pack_errors.append(f"missing runtime_ref: {domain}::{ref_id}::{runtime_ref}")
                if not (_path_exists(repo_root, verification_ref) or _looks_like_command(verification_ref)):
                    pack_errors.append(f"missing verification_ref: {domain}::{ref_id}::{verification_ref}")

        if mode_counts["runnable"] == 0 or mode_counts["verifiable"] == 0:
            pack_errors.append("metadata-only control pack: missing runnable or verifiable execution coverage")

        materialization = pack.get("materialization", {})
        source_template = str(materialization.get("source_template_ref", "")).strip()
        generated_pack = str(materialization.get("generated_pack_ref", "")).strip()
        verification_command = str(materialization.get("verification_command", "")).strip()
        apply_command = str(materialization.get("apply_command", "")).strip()
        if not _path_exists(repo_root, source_template):
            pack_errors.append(f"missing materialization source template: {source_template}")
        if generated_pack != pack_path.relative_to(repo_root).as_posix():
            pack_errors.append(
                f"generated pack path mismatch: expected {pack_path.relative_to(repo_root).as_posix()} got {generated_pack}"
            )
        if not verification_command:
            pack_errors.append("missing materialization verification command")
        if not apply_command:
            pack_errors.append("missing materialization apply command")
        if source_template and _path_exists(repo_root, source_template):
            source_payload = _load_json(repo_root / source_template)
            if source_payload != pack:
                pack_errors.append("generated control pack drifted from source template")

        if pack_errors:
            errors.extend(f"{pack_path.relative_to(repo_root).as_posix()}::{error}" for error in pack_errors)

        inspected.append(
            {
                "pack_path": pack_path.relative_to(repo_root).as_posix(),
                "status": "pass" if not pack_errors else "fail",
                "runnable_refs": mode_counts["runnable"],
                "verifiable_refs": mode_counts["verifiable"],
            }
        )

    return {
        "status": "pass" if not errors else "fail",
        "pack_count": len(packs),
        "packs": inspected,
        "errors": errors,
    }


def main() -> int:
    result = inspect_control_pack_execution()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
