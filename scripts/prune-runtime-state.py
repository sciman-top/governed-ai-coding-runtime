from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import stat


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET_RUN_ROOT = ROOT / "docs" / "change-evidence" / "target-repo-runs"
ARTIFACT_REF_PATTERN = re.compile(r"artifacts/[A-Za-z0-9._/\\:-]+")


@dataclass(frozen=True, slots=True)
class ArtifactEntry:
    name: str
    path: Path
    last_write_utc: str
    file_count: int
    size_bytes: int
    referenced_by_target_runs: bool


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prune machine-local runtime-state artifacts with backup manifests.")
    parser.add_argument("--runtime-state-root", required=True, help="Runtime state root to inspect and prune.")
    parser.add_argument(
        "--target-run-root",
        default=str(DEFAULT_TARGET_RUN_ROOT),
        help="Target-run JSON root used to protect referenced artifacts.",
    )
    parser.add_argument("--keep-latest-artifacts", type=int, default=30, help="Keep latest N artifact directories.")
    parser.add_argument(
        "--keep-latest-remediations",
        type=int,
        default=30,
        help="Keep latest N doctor/remediation-*.json files plus latest-remediation.json.",
    )
    parser.add_argument(
        "--backup-root",
        default="",
        help="Backup root for apply mode. Defaults to <runtime-state-root>/_prune-backups/<timestamp>.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report candidates without deleting files.")
    parser.add_argument("--apply", action="store_true", help="Back up and delete candidates.")
    parser.add_argument("--json", action="store_true", help="Accepted for CLI parity; output is always JSON.")
    return parser


def prune_runtime_state(
    *,
    runtime_state_root: str | Path,
    target_run_root: str | Path,
    keep_latest_artifacts: int,
    keep_latest_remediations: int,
    backup_root: str | Path | None,
    dry_run: bool,
    apply: bool,
) -> tuple[dict, int]:
    if dry_run and apply:
        raise ValueError("--dry-run and --apply are mutually exclusive")
    if keep_latest_artifacts < 0:
        raise ValueError("--keep-latest-artifacts must be >= 0")
    if keep_latest_remediations < 0:
        raise ValueError("--keep-latest-remediations must be >= 0")

    root = Path(runtime_state_root).resolve(strict=False)
    runs_root = Path(target_run_root).resolve(strict=False)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    resolved_backup_root = _resolve_backup_root(root=root, backup_root=backup_root, timestamp=timestamp)

    if not root.exists():
        return _missing_root_payload(
            root=root,
            runs_root=runs_root,
            keep_latest_artifacts=keep_latest_artifacts,
            keep_latest_remediations=keep_latest_remediations,
            backup_root=resolved_backup_root,
            dry_run=dry_run or not apply,
            apply=apply,
        ), 0

    refs = _collect_artifact_refs(runs_root)
    artifact_entries = _collect_artifact_entries(root / "artifacts", refs)
    latest_artifact_names = {entry.name for entry in artifact_entries[:keep_latest_artifacts]}
    artifact_candidates = [
        entry
        for entry in artifact_entries
        if entry.name not in latest_artifact_names and not entry.referenced_by_target_runs
    ]

    remediation_files = _collect_remediation_files(root / "doctor")
    remediation_candidates = remediation_files[keep_latest_remediations:]
    remediation_candidate_sizes = {path: path.stat().st_size for path in remediation_candidates}

    deleted_artifacts: list[dict[str, str | int]] = []
    deleted_remediations: list[dict[str, str | int]] = []
    failed_deletions: list[dict[str, str]] = []
    manifest_path = resolved_backup_root / "manifest.json"
    apply_requested = bool(apply)
    dry_run_effective = bool(dry_run or not apply)

    if apply_requested:
        resolved_backup_root.mkdir(parents=True, exist_ok=True)
        for entry in artifact_candidates:
            try:
                backup_path = resolved_backup_root / "artifacts" / entry.name
                shutil.copytree(entry.path, backup_path)
                _remove_tree(entry.path)
                deleted_artifacts.append(
                    {
                        "name": entry.name,
                        "size_bytes": entry.size_bytes,
                        "backup_path": str(backup_path),
                    }
                )
            except OSError as exc:
                failed_deletions.append({"path": str(entry.path), "error": str(exc)})
        for path in remediation_candidates:
            try:
                backup_path = resolved_backup_root / "doctor" / path.name
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, backup_path)
                size_bytes = remediation_candidate_sizes[path]
                path.unlink()
                deleted_remediations.append(
                    {
                        "name": path.name,
                        "size_bytes": size_bytes,
                        "backup_path": str(backup_path),
                    }
                )
            except OSError as exc:
                failed_deletions.append({"path": str(path), "error": str(exc)})

    status = "pass" if not failed_deletions else "fail"
    payload = {
        "operation_type": "runtime_state_prune",
        "deletion_policy": "delete_only_unreferenced_artifacts_and_old_doctor_remediations_after_backup",
        "status": status,
        "reason": "ok" if status == "pass" else "delete_failed",
        "runtime_state_root": str(root),
        "target_run_root": str(runs_root),
        "dry_run": dry_run_effective,
        "apply": apply_requested,
        "backup_root": str(resolved_backup_root),
        "manifest_path": str(manifest_path) if apply_requested else "",
        "retention_policy": _retention_policy(
            keep_latest_artifacts=keep_latest_artifacts,
            keep_latest_remediations=keep_latest_remediations,
        ),
        "summary": {
            "total_files": sum(1 for path in root.rglob("*") if path.is_file()),
            "total_size_bytes": sum(path.stat().st_size for path in root.rglob("*") if path.is_file()),
            "artifact_dirs_total": len(artifact_entries),
            "artifact_dirs_referenced_by_target_runs": sum(
                1 for entry in artifact_entries if entry.referenced_by_target_runs
            ),
            "artifact_dirs_kept_by_latest_window": min(keep_latest_artifacts, len(artifact_entries)),
            "artifact_dirs_delete_candidates": len(artifact_candidates),
            "artifact_delete_candidate_size_bytes": sum(entry.size_bytes for entry in artifact_candidates),
            "artifact_dirs_deleted": len(deleted_artifacts),
            "doctor_remediation_files_total": len(remediation_files),
            "doctor_remediation_delete_candidates": len(remediation_candidates),
            "doctor_remediation_candidate_size_bytes": sum(remediation_candidate_sizes.values()),
            "doctor_remediation_files_deleted": len(deleted_remediations),
            "approvals_total": _count_files(root / "approvals"),
            "context_files_total": _count_files(root / "context"),
            "failed_deletions": len(failed_deletions),
        },
        "artifact_delete_candidates": [_artifact_row(entry) for entry in artifact_candidates],
        "doctor_remediation_delete_candidates": [path.name for path in remediation_candidates],
        "deleted_artifacts": deleted_artifacts,
        "deleted_doctor_remediations": deleted_remediations,
        "failed_deletions": failed_deletions,
        "rollback_instructions": "Rollback by restoring deleted files from backup_root using manifest.json if this prune is rejected.",
    }

    if apply_requested:
        _write_manifest(manifest_path, payload)
    return payload, (0 if status == "pass" else 1)


def _missing_root_payload(
    *,
    root: Path,
    runs_root: Path,
    keep_latest_artifacts: int,
    keep_latest_remediations: int,
    backup_root: Path,
    dry_run: bool,
    apply: bool,
) -> dict:
    return {
        "operation_type": "runtime_state_prune",
        "status": "pass",
        "reason": "runtime_state_root_missing",
        "runtime_state_root": str(root),
        "target_run_root": str(runs_root),
        "dry_run": dry_run,
        "apply": apply,
        "backup_root": str(backup_root),
        "manifest_path": "",
        "retention_policy": _retention_policy(
            keep_latest_artifacts=keep_latest_artifacts,
            keep_latest_remediations=keep_latest_remediations,
        ),
        "summary": {
            "total_files": 0,
            "total_size_bytes": 0,
            "artifact_dirs_total": 0,
            "artifact_dirs_referenced_by_target_runs": 0,
            "artifact_dirs_kept_by_latest_window": 0,
            "artifact_dirs_delete_candidates": 0,
            "artifact_delete_candidate_size_bytes": 0,
            "artifact_dirs_deleted": 0,
            "doctor_remediation_files_total": 0,
            "doctor_remediation_delete_candidates": 0,
            "doctor_remediation_candidate_size_bytes": 0,
            "doctor_remediation_files_deleted": 0,
            "approvals_total": 0,
            "context_files_total": 0,
            "failed_deletions": 0,
        },
        "artifact_delete_candidates": [],
        "doctor_remediation_delete_candidates": [],
        "deleted_artifacts": [],
        "deleted_doctor_remediations": [],
        "failed_deletions": [],
    }


def _resolve_backup_root(*, root: Path, backup_root: str | Path | None, timestamp: str) -> Path:
    raw = "" if backup_root is None else str(backup_root).strip()
    if raw:
        return Path(raw).resolve(strict=False)
    return (root / "_prune-backups" / timestamp).resolve(strict=False)


def _collect_artifact_refs(runs_root: Path) -> set[str]:
    refs: set[str] = set()
    if not runs_root.exists():
        return refs
    for path in runs_root.glob("*.json"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in ARTIFACT_REF_PATTERN.finditer(text):
            refs.add(match.group(0).replace("\\", "/").rstrip(".,\"']})"))
    return refs


def _collect_artifact_entries(artifacts_root: Path, refs: set[str]) -> list[ArtifactEntry]:
    entries: list[ArtifactEntry] = []
    if not artifacts_root.exists():
        return entries
    for path in artifacts_root.iterdir():
        if not path.is_dir():
            continue
        relative_ref = f"artifacts/{path.name}"
        entries.append(
            ArtifactEntry(
                name=path.name,
                path=path,
                last_write_utc=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                file_count=sum(1 for item in path.rglob("*") if item.is_file()),
                size_bytes=sum(item.stat().st_size for item in path.rglob("*") if item.is_file()),
                referenced_by_target_runs=any(ref == relative_ref or ref.startswith(f"{relative_ref}/") for ref in refs),
            )
        )
    return sorted(entries, key=lambda item: (item.last_write_utc, item.name), reverse=True)


def _collect_remediation_files(doctor_root: Path) -> list[Path]:
    if not doctor_root.exists():
        return []
    return sorted(doctor_root.glob("remediation-*.json"), key=lambda path: (path.stat().st_mtime, path.name), reverse=True)


def _retention_policy(*, keep_latest_artifacts: int, keep_latest_remediations: int) -> dict[str, object]:
    return {
        "strategy": "keep_latest_or_target_run_referenced",
        "artifact_keep_latest_dirs": keep_latest_artifacts,
        "artifact_keep_all_target_run_refs": True,
        "doctor_keep_latest_remediation_files": keep_latest_remediations,
        "preserve_latest_remediation_alias": True,
        "preserve_approvals": True,
        "preserve_context": True,
        "apply_requires": ["--apply", "backup_root", "manifest.json"],
    }


def _artifact_row(entry: ArtifactEntry) -> dict[str, object]:
    return {
        "name": entry.name,
        "last_write_utc": entry.last_write_utc,
        "file_count": entry.file_count,
        "size_bytes": entry.size_bytes,
        "referenced_by_target_runs": entry.referenced_by_target_runs,
    }


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def _write_manifest(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _remove_tree(path: Path) -> None:
    def _chmod_and_retry(function, failed_path, _exc_info) -> None:
        os.chmod(failed_path, stat.S_IWRITE)
        function(failed_path)

    shutil.rmtree(path, onexc=_chmod_and_retry)


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    apply_requested = bool(args.apply)
    dry_run = bool(args.dry_run or not apply_requested)
    payload, exit_code = prune_runtime_state(
        runtime_state_root=args.runtime_state_root,
        target_run_root=args.target_run_root,
        keep_latest_artifacts=args.keep_latest_artifacts,
        keep_latest_remediations=args.keep_latest_remediations,
        backup_root=args.backup_root if args.backup_root else None,
        dry_run=dry_run,
        apply=apply_requested,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
