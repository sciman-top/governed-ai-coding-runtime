from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_GLOB = "*-functional-verification.md"
DEFAULT_MAX_AGE_DAYS = 30

REQUIRED_SECTIONS = (
    "## Goal",
    "## Root Cause And Changes",
    "## Verification",
    "## Rollback",
)


@dataclass(frozen=True)
class ProofCheck:
    check_id: str
    required_tokens: tuple[str, ...]


PROOF_CHECKS = (
    ProofCheck(
        "hard_gate_order",
        (
            "scripts/build-runtime.ps1",
            "verify-repo.ps1 -Check Runtime",
            "verify-repo.ps1 -Check Contract",
            "doctor-runtime.ps1",
            "verify-repo.ps1 -Check All",
        ),
    ),
    ProofCheck(
        "runtime_task_effect",
        (
            "run-governed-task.py",
            "task state `delivered`",
            "verification refs include `build/test/contract/doctor`",
        ),
    ),
    ProofCheck(
        "target_repo_batch_effect",
        (
            "runtime-flow-preset.ps1 -AllTargets",
            "5 targets, 0 failures",
            "0 changed fields",
        ),
    ),
    ProofCheck(
        "attached_write_closure",
        (
            "Temporary target attach/write smoke",
            "docs/write-smoke.txt",
            "live_closure_ready",
        ),
    ),
    ProofCheck(
        "trial_and_adapter_surfaces",
        (
            "run-readonly-trial.py",
            "run-codex-adapter-trial.py",
            "run-claude-code-adapter-trial.py",
            "run-multi-repo-trial.py",
            "2 repo profiles, 0 gate failures",
            "claude-code-native-attach-tier-parity.md",
        ),
    ),
    ProofCheck(
        "package_and_operator_surfaces",
        (
            "package-runtime.ps1",
            "provenance verification status `verified`",
            "serve-operator-ui.py",
            "sync-agent-rules.py",
        ),
    ),
    ProofCheck(
        "repo_hook_and_governance_surface",
        (
            "install-repo-hooks.ps1",
            "core.hooksPath=.githooks",
            "scripts/governance/fast-check.ps1",
        ),
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify functional-effectiveness evidence is fresh and complete.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--evidence", default=None, help="Evidence markdown file to verify.")
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=DEFAULT_MAX_AGE_DAYS,
        help="Maximum age for dated functional verification evidence.",
    )
    parser.add_argument("--as-of", default=None, help="ISO date used for freshness checks; defaults to today.")
    args = parser.parse_args()

    try:
        as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    except ValueError:
        print(f"invalid --as-of date: {args.as_of}", file=sys.stderr)
        return 1

    try:
        result = assert_functional_effectiveness(
            repo_root=Path(args.repo_root),
            evidence_path=Path(args.evidence) if args.evidence else None,
            max_age_days=args.max_age_days,
            as_of=as_of,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def assert_functional_effectiveness(
    *,
    repo_root: Path,
    evidence_path: Path | None = None,
    max_age_days: int = DEFAULT_MAX_AGE_DAYS,
    as_of: dt.date | None = None,
) -> dict:
    result = inspect_functional_effectiveness(
        repo_root=repo_root,
        evidence_path=evidence_path,
        max_age_days=max_age_days,
        as_of=as_of,
    )

    failures: list[str] = []
    if result["missing_sections"]:
        failures.append("missing sections: " + ", ".join(result["missing_sections"]))
    if result["evidence_date"] is None:
        failures.append("evidence filename must start with YYYYMMDD")
    if result["future_dated"]:
        failures.append(f"evidence is future-dated: {result['evidence_date']}")
    if result["expired"]:
        failures.append(
            f"evidence is stale: age {result['evidence_age_days']} days exceeds {result['max_age_days']} days"
        )

    failed_checks = [
        f"{check['check_id']} missing " + ", ".join(check["missing_tokens"])
        for check in result["proof_checks"]
        if check["missing_tokens"]
    ]
    failures.extend(failed_checks)

    if failures:
        raise ValueError("functional effectiveness evidence failed: " + "; ".join(failures))

    return result


def inspect_functional_effectiveness(
    *,
    repo_root: Path,
    evidence_path: Path | None = None,
    max_age_days: int = DEFAULT_MAX_AGE_DAYS,
    as_of: dt.date | None = None,
) -> dict:
    resolved_root = repo_root.resolve(strict=False)
    selected_evidence = _resolve_evidence_path(resolved_root, evidence_path)
    try:
        text = selected_evidence.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"functional evidence is not readable: {selected_evidence} ({exc})") from exc

    today = as_of or dt.date.today()
    evidence_date = _extract_evidence_date(selected_evidence)
    evidence_age_days = None if evidence_date is None else (today - evidence_date).days
    missing_sections = [section for section in REQUIRED_SECTIONS if section not in text]
    proof_checks = _inspect_proof_checks(text)
    future_dated = evidence_age_days is not None and evidence_age_days < 0
    expired = evidence_age_days is not None and evidence_age_days > max_age_days
    passed = not (
        missing_sections
        or evidence_date is None
        or future_dated
        or expired
        or any(check["missing_tokens"] for check in proof_checks)
    )

    return {
        "status": "pass" if passed else "fail",
        "evidence_path": selected_evidence.resolve(strict=False).as_posix(),
        "evidence_date": evidence_date.isoformat() if evidence_date else None,
        "as_of": today.isoformat(),
        "max_age_days": max_age_days,
        "evidence_age_days": evidence_age_days,
        "expired": expired,
        "future_dated": future_dated,
        "required_sections": list(REQUIRED_SECTIONS),
        "missing_sections": missing_sections,
        "proof_checks": proof_checks,
    }


def _resolve_evidence_path(repo_root: Path, evidence_path: Path | None) -> Path:
    if evidence_path is not None:
        path = evidence_path if evidence_path.is_absolute() else repo_root / evidence_path
        if not path.exists():
            raise ValueError(f"functional evidence file not found: {path}")
        return path

    evidence_root = repo_root / "docs" / "change-evidence"
    candidates = sorted(
        evidence_root.glob(DEFAULT_EVIDENCE_GLOB),
        key=lambda path: (_extract_evidence_date(path) or dt.date.min, path.name),
        reverse=True,
    )
    if not candidates:
        raise ValueError(f"no functional verification evidence found under {evidence_root}")
    return candidates[0]


def _inspect_proof_checks(text: str) -> list[dict]:
    normalized = _normalize(text)
    results: list[dict] = []
    for check in PROOF_CHECKS:
        missing = [token for token in check.required_tokens if _normalize(token) not in normalized]
        results.append(
            {
                "check_id": check.check_id,
                "status": "pass" if not missing else "fail",
                "required_tokens": list(check.required_tokens),
                "missing_tokens": missing,
            }
        )
    return results


def _normalize(value: str) -> str:
    return value.replace("\\", "/").lower()


def _extract_evidence_date(path: Path) -> dt.date | None:
    match = re.match(r"^(\d{8})-", path.name)
    if not match:
        return None
    try:
        return dt.datetime.strptime(match.group(1), "%Y%m%d").date()
    except ValueError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
