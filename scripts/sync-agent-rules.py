from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_PATH = ROOT / "rules" / "manifest.json"
DEFAULT_CATALOG_PATH = ROOT / "docs" / "targets" / "target-repos-catalog.json"


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json object required: {path}")
    return data


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _expand_template(value: str, variables: dict[str, str]) -> str:
    expanded = value
    for key, raw in variables.items():
        expanded = expanded.replace("${" + key + "}", raw)
    return expanded


def _load_targets(catalog_path: Path) -> dict[str, dict[str, Any]]:
    catalog = _load_json(catalog_path)
    targets = catalog.get("targets")
    if not isinstance(targets, dict) or not targets:
        raise ValueError("target catalog must define a non-empty targets object")
    return targets


def _validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("manifest.entries must be a non-empty list")

    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            raise ValueError(f"manifest.entries[{index}] must be an object")
        entry = dict(raw)
        entry_id = entry.get("id")
        scope = entry.get("scope")
        tool = entry.get("tool")
        source = entry.get("source")
        target_path = entry.get("target_path")
        version = entry.get("version") or manifest.get("default_version")

        if not isinstance(entry_id, str) or not entry_id.strip():
            raise ValueError(f"manifest.entries[{index}].id must be a non-empty string")
        if entry_id in seen:
            raise ValueError(f"duplicate manifest entry id: {entry_id}")
        seen.add(entry_id)
        if scope not in {"global", "project"}:
            raise ValueError(f"manifest.entries[{index}].scope must be global or project")
        if tool not in {"codex", "claude", "gemini"}:
            raise ValueError(f"manifest.entries[{index}].tool must be codex, claude, or gemini")
        if not isinstance(version, str) or not version.strip():
            raise ValueError(f"manifest.entries[{index}].version must be a non-empty string")
        if not isinstance(source, str) or not source.strip():
            raise ValueError(f"manifest.entries[{index}].source must be a non-empty string")
        if not isinstance(target_path, str) or not target_path.strip():
            raise ValueError(f"manifest.entries[{index}].target_path must be a non-empty string")
        if scope == "project":
            target_repo_id = entry.get("target_repo_id")
            if not isinstance(target_repo_id, str) or not target_repo_id.strip():
                raise ValueError(f"manifest.entries[{index}].target_repo_id is required for project entries")
        entry["version"] = version
        validated.append(entry)
    return validated


def _resolve_source_path(raw_path: str) -> Path:
    source = Path(raw_path)
    if not source.is_absolute():
        source = ROOT / source
    resolved = source.resolve(strict=False)
    try:
        resolved.relative_to(ROOT.resolve(strict=False))
    except ValueError as exc:
        raise ValueError(f"source path must stay inside this repo: {raw_path}") from exc
    return resolved


def _target_relative_path(target_repo: Path, raw_path: str) -> Path:
    relative = Path(raw_path)
    if relative.is_absolute():
        raise ValueError(f"project target path must be repo-relative: {raw_path}")
    if any(part == ".." for part in relative.parts):
        raise ValueError(f"project target path must not contain '..': {raw_path}")
    resolved = (target_repo / relative).resolve(strict=False)
    try:
        resolved.relative_to(target_repo.resolve(strict=False))
    except ValueError as exc:
        raise ValueError(f"project target path escapes target repo: {raw_path}") from exc
    return resolved


def _extract_rule_version(text: str) -> str | None:
    patterns = (
        r"GlobalUser/(?:AGENTS|CLAUDE|GEMINI)\.md v([0-9][0-9A-Za-z_.-]*)",
        r"\*\*版本\*\*:\s*([0-9][0-9A-Za-z_.-]*)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _version_tuple(value: str | None) -> tuple[int, ...] | None:
    if not value:
        return None
    parts = re.findall(r"\d+", value)
    if not parts:
        return None
    return tuple(int(part) for part in parts)


def _compare_versions(left: str | None, right: str | None) -> int | None:
    left_tuple = _version_tuple(left)
    right_tuple = _version_tuple(right)
    if left_tuple is None or right_tuple is None:
        return None
    width = max(len(left_tuple), len(right_tuple))
    left_tuple = left_tuple + (0,) * (width - len(left_tuple))
    right_tuple = right_tuple + (0,) * (width - len(right_tuple))
    return (left_tuple > right_tuple) - (left_tuple < right_tuple)


def _resolve_project_roots(
    *,
    catalog_path: Path,
    repo_root: Path,
    code_root: Path,
    runtime_state_base: Path,
) -> dict[str, Path]:
    targets = _load_targets(catalog_path)
    variables = {
        "repo_root": str(repo_root),
        "code_root": str(code_root),
        "runtime_state_base": str(runtime_state_base),
    }
    roots: dict[str, Path] = {}
    for target_name, target in targets.items():
        attachment_root = target.get("attachment_root")
        if not isinstance(attachment_root, str) or not attachment_root.strip():
            raise ValueError(f"target '{target_name}' missing attachment_root")
        roots[target_name] = Path(_expand_template(attachment_root, variables)).resolve(strict=False)
    return roots


def _backup_existing(target_path: Path, backup_root: Path, target_text: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    anchor = target_path.anchor
    drive = target_path.drive.replace(":", "") if target_path.drive else "relative"
    safe_parts = [drive]
    for part in target_path.parts:
        if part in {target_path.drive, target_path.root, anchor, "\\", "/"}:
            continue
        safe_parts.append(part.replace(":", "_"))
    backup_path = backup_root / timestamp / Path(*safe_parts)
    if backup_path.resolve(strict=False) == target_path.resolve(strict=False):
        raise ValueError(f"backup path resolves to target path: {target_path}")
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_text(target_text, encoding="utf-8")
    return backup_path


def _split_markdown_sections(text: str, prefix: str) -> tuple[str, list[tuple[str, str]]]:
    pattern = re.compile(rf"(?m)^(?P<heading>{re.escape(prefix)}[^\n]*\n)")
    matches = list(pattern.finditer(text))
    if not matches:
        return text, []

    preamble = text[: matches[0].start()]
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group("heading"), text[start:end]))
    return preamble, sections


def _tokenize_markdown_body(body: str) -> list[str]:
    tokens: list[str] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            tokens.append("\n".join(paragraph_lines).strip())
            paragraph_lines = []

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            continue
        if re.match(r"^([-*] |\d+\. )", stripped):
            flush_paragraph()
            tokens.append(stripped)
            continue
        paragraph_lines.append(line)

    flush_paragraph()
    return [token for token in tokens if token.strip()]


def _normalize_token(token: str) -> str:
    return " ".join(token.split())


def _merge_markdown_body(source_body: str, target_body: str) -> tuple[str, int]:
    source_tokens = _tokenize_markdown_body(source_body)
    target_tokens = _tokenize_markdown_body(target_body)
    source_seen = {_normalize_token(token) for token in source_tokens}
    target_only = [token for token in target_tokens if _normalize_token(token) not in source_seen]
    if not target_only:
        return source_body, 0

    merged = source_body.rstrip()
    addition_block = "\n".join(target_only)
    if merged:
        merged += "\n\n"
    merged += "<!-- auto-merged target-local additions -->\n" + addition_block + "\n"
    return merged, len(target_only)


def _merge_project_rule_text(source_text: str, target_text: str) -> tuple[str, int] | None:
    source_preamble, source_sections = _split_markdown_sections(source_text, "## ")
    target_preamble, target_sections = _split_markdown_sections(target_text, "## ")
    if [heading for heading, _ in source_sections] != [heading for heading, _ in target_sections]:
        return None

    merged_parts = [source_preamble]
    added_count = 0
    for (source_heading, source_body), (_, target_body) in zip(source_sections, target_sections):
        source_intro, source_subsections = _split_markdown_sections(source_body, "### ")
        target_intro, target_subsections = _split_markdown_sections(target_body, "### ")
        if [heading for heading, _ in source_subsections] != [heading for heading, _ in target_subsections]:
            return None

        merged_section_parts = []
        merged_intro, intro_additions = _merge_markdown_body(source_intro, target_intro)
        added_count += intro_additions
        merged_section_parts.append(merged_intro)

        for (source_subheading, source_subbody), (_, target_subbody) in zip(source_subsections, target_subsections):
            merged_subbody, sub_additions = _merge_markdown_body(source_subbody, target_subbody)
            added_count += sub_additions
            merged_section_parts.append(source_subheading + merged_subbody)

        merged_parts.append(source_heading + "".join(merged_section_parts))

    return "".join(merged_parts), added_count


def _plan_entry(
    *,
    entry: dict[str, Any],
    target_path: Path,
    source_path: Path,
    source_text: str,
    apply: bool,
    force: bool,
    backup_root: Path,
) -> dict[str, Any]:
    source_hash = _sha256_text(source_text)
    source_version = _extract_rule_version(source_text) or entry["version"]
    result: dict[str, Any] = {
        "id": entry["id"],
        "scope": entry["scope"],
        "tool": entry["tool"],
        "version": entry["version"],
        "source": str(source_path),
        "target_path": str(target_path),
        "source_sha256": source_hash,
        "source_version": source_version,
    }

    if not target_path.exists():
        result["status"] = "created" if apply else "would_create"
        if apply:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(source_text, encoding="utf-8")
        return result

    target_text = target_path.read_text(encoding="utf-8")
    target_hash = _sha256_text(target_text)
    target_version = _extract_rule_version(target_text)
    result["target_sha256"] = target_hash
    result["target_version"] = target_version

    if target_hash == source_hash:
        result["status"] = "skipped_same_hash"
        return result

    comparison = _compare_versions(target_version, source_version)
    if (
        entry["scope"] == "project"
        and target_version == source_version
        and target_path.suffix.lower() == ".md"
    ):
        merged_text = _merge_project_rule_text(source_text, target_text)
        if merged_text is not None:
            integrated_text, integrated_additions = merged_text
            integrated_hash = _sha256_text(integrated_text)
            result["merge_strategy"] = "project_rule_structured_union"
            result["merged_target_additions"] = integrated_additions
            if integrated_hash == target_hash:
                result["status"] = "skipped_same_hash"
                return result
            result["status"] = "merged_same_version_drift" if apply else "would_merge_same_version_drift"
            result["merged_sha256"] = integrated_hash
            if apply:
                backup_path = _backup_existing(target_path, backup_root, target_text)
                result["backup_path"] = str(backup_path)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(integrated_text, encoding="utf-8")
            return result

    if not force and target_version == source_version:
        result["status"] = "blocked_same_version_drift"
        result["reason"] = "target has the same rule version but different content"
        return result
    if not force and comparison is not None and comparison > 0:
        result["status"] = "blocked_target_newer"
        result["reason"] = "target rule version is newer than the manifest source"
        return result
    if not force and target_version is None:
        result["status"] = "blocked_missing_target_version"
        result["reason"] = "target has no detectable rule version; use --force after review"
        return result

    result["status"] = "updated" if apply else "would_update"
    if apply:
        backup_path = _backup_existing(target_path, backup_root, target_text)
        result["backup_path"] = str(backup_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(source_text, encoding="utf-8")
    return result


def _scope_matches(entry_scope: str, selected_scope: str) -> bool:
    if selected_scope == "all":
        return True
    if selected_scope == "global":
        return entry_scope == "global"
    if selected_scope == "targets":
        return entry_scope == "project"
    raise ValueError(f"unknown scope: {selected_scope}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run or apply managed agent rule files.")
    parser.add_argument("--scope", choices=("All", "Global", "Targets", "all", "global", "targets"), default="All")
    parser.add_argument("--target", action="append", default=[], help="Limit project entries to one target repo id.")
    parser.add_argument("--apply", action="store_true", help="Write target files. Default is dry-run.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting same-version drift or unknown-version targets.")
    parser.add_argument("--fail-on-change", action="store_true", help="Return non-zero when dry-run detects create/update drift.")
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST_PATH))
    parser.add_argument("--catalog-path", default=str(DEFAULT_CATALOG_PATH))
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--code-root", default=None)
    parser.add_argument("--runtime-state-base", default=None)
    parser.add_argument("--user-profile", default=os.environ.get("USERPROFILE") or str(Path.home()))
    args = parser.parse_args()

    manifest_path = Path(args.manifest_path).resolve(strict=False)
    catalog_path = Path(args.catalog_path).resolve(strict=False)
    repo_root = Path(args.repo_root).resolve(strict=False)
    code_root = Path(args.code_root).resolve(strict=False) if args.code_root else repo_root.parent
    runtime_state_base = (
        Path(args.runtime_state_base).resolve(strict=False)
        if args.runtime_state_base
        else repo_root / ".runtime" / "attachments"
    )
    user_profile = Path(args.user_profile).resolve(strict=False)

    if not manifest_path.exists():
        raise SystemExit(f"manifest file not found: {manifest_path}")

    manifest = _load_json(manifest_path)
    entries = _validate_manifest(manifest)
    project_roots = _resolve_project_roots(
        catalog_path=catalog_path,
        repo_root=repo_root,
        code_root=code_root,
        runtime_state_base=runtime_state_base,
    )

    backup_root_raw = manifest.get("backup_policy", {}).get("root", "docs/change-evidence/rule-sync-backups")
    backup_root = Path(str(backup_root_raw))
    if not backup_root.is_absolute():
        backup_root = ROOT / backup_root
    variables = {
        "repo_root": str(repo_root),
        "code_root": str(code_root),
        "runtime_state_base": str(runtime_state_base),
        "user_profile": str(user_profile),
    }

    selected_scope = args.scope.lower()
    selected_targets = set(args.target)
    results: list[dict[str, Any]] = []
    for entry in entries:
        if not _scope_matches(str(entry["scope"]), selected_scope):
            continue
        if entry["scope"] == "project" and selected_targets and entry["target_repo_id"] not in selected_targets:
            continue

        source_path = _resolve_source_path(str(entry["source"]))
        if not source_path.exists():
            raise SystemExit(f"source rule file not found: {source_path}")
        source_text = source_path.read_text(encoding="utf-8")

        if entry["scope"] == "global":
            target_path = Path(_expand_template(str(entry["target_path"]), variables)).resolve(strict=False)
        else:
            target_repo_id = str(entry["target_repo_id"])
            if target_repo_id not in project_roots:
                raise SystemExit(f"target repo id not found in catalog: {target_repo_id}")
            target_repo = project_roots[target_repo_id]
            if not target_repo.exists():
                raise SystemExit(f"target repo not found: {target_repo}")
            target_path = _target_relative_path(target_repo, str(entry["target_path"]))

        results.append(
            _plan_entry(
                entry=entry,
                target_path=target_path,
                source_path=source_path,
                source_text=source_text,
                apply=args.apply,
                force=args.force,
                backup_root=backup_root,
            )
        )

    blocked = [item for item in results if str(item["status"]).startswith("blocked_")]
    changed = [
        item
        for item in results
        if item["status"] in {"would_create", "would_update", "created", "updated"}
    ]
    status = "blocked" if blocked else ("applied" if args.apply and changed else ("dry_run_changes" if changed else "pass"))
    output = {
        "status": status,
        "mode": "apply" if args.apply else "dry-run",
        "force": args.force,
        "manifest_path": str(manifest_path),
        "catalog_path": str(catalog_path),
        "scope": selected_scope,
        "entry_count": len(results),
        "changed_count": len(changed),
        "blocked_count": len(blocked),
        "results": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if blocked:
        return 2
    if args.fail_on_change and changed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
