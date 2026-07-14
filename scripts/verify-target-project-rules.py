from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COORDINATION_PATH = ROOT / "rules" / "target-project-rule-coordination.json"
EXPECTED_TOOLS = ["codex", "claude"]
GITHUB_REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REQUIRED_SECTION_PATTERNS = {
    "1": r"(?m)^## 1(?:\.|\s)",
    "A": r"(?m)^## A(?:\.|\s)",
    "B": r"(?m)^## B(?:\.|\s)",
    "C": r"(?m)^## C(?:\.|\s)",
    "D": r"(?m)^## D(?:\.|\s)",
}
HOST_SPECIFIC_PROJECT_PATTERNS = {
    "codex_platform_section": r"(?im)^## B\.\s*Codex\b",
    "claude_platform_section": r"(?im)^## B\.\s*Claude\b",
    "codex_direct_read_claim": r"Codex\s*直接读取",
    "claude_wrapper_tutorial": r"Claude\s*(?:项目级\s*)?wrapper",
    "codex_loading_setting": r"project_doc_fallback_filenames",
    "claude_loading_setting": r"CLAUDE\.local\.md",
}
MANAGED_FAMILY_FORBIDDEN_TOKENS = ["Gemini", "GEMINI.md", ".gemini/"]
NA_REQUIRED_FIELDS = [
    "reason",
    "alternative_verification",
    "evidence_link",
    "expires_at",
    "recovery_condition",
]
WRAPPER_DUPLICATION_TOKENS = [
    "## 1.",
    "## A.",
    "## B.",
    "## C.",
    "## D.",
    "build -> test -> contract/invariant -> hotspot",
    "Global Rule -> Repo Action",
]
NESTED_RULE_EXCLUDED_DIRS = {
    ".git",
    ".txn",
    ".worktrees",
    ".venv",
    "agent",
    "imports",
    "node_modules",
    "vendor",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json object required: {path}")
    return payload


def _display_path(path: Path) -> str:
    return str(path.resolve(strict=False)).replace("\\", "/")


def _resolve_workspace_root(coordination_path: Path, raw_path: Any) -> Path:
    workspace_root = Path(str(raw_path or "").strip())
    if not workspace_root.is_absolute():
        workspace_root = coordination_path.parent / workspace_root
    return workspace_root.resolve(strict=False)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _extract_marker(text: str, label: str) -> str | None:
    match = re.search(
        rf"(?m)^\*\*{re.escape(label)}\*\*\s*:\s*`?([^`\s]+)`?\s*$",
        text,
    )
    return match.group(1) if match else None


def _configured_budget(target: dict[str, Any], key: str, default: int) -> int:
    budgets = target.get("budgets")
    if not isinstance(budgets, dict):
        return default
    value = budgets.get(key)
    return value if isinstance(value, int) and value > 0 else default


def _git_dirty(repo_root: Path) -> bool:
    try:
        completed = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return completed.returncode == 0 and bool(completed.stdout.strip())


def _git_root(candidate: Path) -> Path | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=candidate,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    return Path(completed.stdout.strip()).resolve(strict=False)


def _discover_direct_git_roots(workspace_root: Path, excluded: set[str]) -> list[str]:
    if not workspace_root.is_dir():
        return []
    discovered: list[str] = []
    for child in workspace_root.iterdir():
        if child.name in excluded or not child.is_dir():
            continue
        resolved = child.resolve(strict=False)
        if not _is_within(resolved, workspace_root):
            continue
        if _git_root(resolved) == resolved:
            discovered.append(child.name)
    return sorted(discovered, key=str.casefold)


def _normalize_utf8_lf(raw: bytes) -> bytes:
    text = raw.decode("utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _workflow_line_endings(raw: bytes) -> str:
    crlf_count = raw.count(b"\r\n")
    lf_count = raw.count(b"\n") - crlf_count
    cr_count = raw.count(b"\r") - crlf_count
    kinds = [
        name
        for name, count in (("crlf", crlf_count), ("lf", lf_count), ("cr", cr_count))
        if count
    ]
    return "+".join(kinds) if kinds else "none"


def _contains_contract_token(line: str, token: str) -> bool:
    return re.search(
        rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])",
        line,
    ) is not None


def _audit_na_contract(project_text: str, blocking: list[str]) -> None:
    for line in project_text.splitlines():
        if not any(
            _contains_contract_token(line, token)
            for token in ("gate_na", "platform_na")
        ):
            continue
        missing = [
            field
            for field in NA_REQUIRED_FIELDS
            if not _contains_contract_token(line, field)
        ]
        if missing:
            finding = "na_contract_fields_missing:" + ",".join(missing)
            if finding not in blocking:
                blocking.append(finding)


def _nested_rule_files(repo_root: Path, project_rule: str, wrapper_rule: str) -> list[str]:
    try:
        completed = subprocess.run(
            [
                "git",
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "--",
                ":(glob)**/AGENTS.md",
                ":(glob)**/CLAUDE.md",
            ],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        completed = None
    if completed is not None and completed.returncode == 0:
        matches = []
        for raw_path in completed.stdout.splitlines():
            normalized = raw_path.replace("\\", "/").strip()
            if not normalized or normalized in {project_rule, wrapper_rule}:
                continue
            if any(part in NESTED_RULE_EXCLUDED_DIRS for part in Path(normalized).parts):
                continue
            matches.append(normalized)
        return sorted(matches)[:20]

    matches: list[str] = []
    for current_root, dir_names, file_names in os.walk(repo_root):
        dir_names[:] = [name for name in dir_names if name not in NESTED_RULE_EXCLUDED_DIRS]
        current = Path(current_root)
        if current == repo_root:
            continue
        for file_name in file_names:
            if file_name not in {project_rule, wrapper_rule}:
                continue
            matches.append(str((current / file_name).relative_to(repo_root)).replace("\\", "/"))
            if len(matches) >= 20:
                return matches
    return matches


def _new_audit(target: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    return {
        "repo_id": str(target.get("repo_id") or "").strip(),
        "repo_root": _display_path(repo_root),
        "tools": target.get("tools") or [],
        "coordination_mode": str(target.get("coordination_mode") or "").strip(),
        "status": "pass",
        "blocking_findings": [],
        "observations": [],
        "details": {},
        "rollback_boundary": (
            "revert only this repository's AGENTS.md, CLAUDE.md, and rollout-evidence slice; "
            "preserve unrelated worktree changes"
        ),
    }


def _audit_wrapper(
    *,
    wrapper_path: Path,
    wrapper_mode: str,
    wrapper_max_lines: int,
    audit: dict[str, Any],
) -> tuple[str, int]:
    if not wrapper_path.exists():
        audit["blocking_findings"].append("wrapper_missing")
        return "", 0

    raw = wrapper_path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        audit["blocking_findings"].append("wrapper_utf8_bom")
    try:
        text = raw.decode("utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8")
    except UnicodeDecodeError:
        audit["blocking_findings"].append("wrapper_not_utf8")
        return "", len(raw.splitlines())

    physical_lines = text.splitlines()
    line_count = len(physical_lines)
    first_line = physical_lines[0] if physical_lines else ""
    if first_line != "@AGENTS.md":
        audit["blocking_findings"].append("wrapper_first_line_invalid")

    nonempty_lines = [line.strip() for line in physical_lines if line.strip()]
    import_lines = [line for line in nonempty_lines if line.startswith("@")]
    if import_lines != ["@AGENTS.md"]:
        audit["blocking_findings"].append("wrapper_import_set_invalid")
    if wrapper_mode == "import_only" and nonempty_lines != ["@AGENTS.md"]:
        audit["blocking_findings"].append("wrapper_not_import_only")
    if any(token in text for token in WRAPPER_DUPLICATION_TOKENS):
        audit["blocking_findings"].append("wrapper_duplicates_project_contract")
    forbidden_hits = [token for token in MANAGED_FAMILY_FORBIDDEN_TOKENS if token in text]
    if forbidden_hits:
        audit["blocking_findings"].append("wrapper_managed_family_residue")
    if line_count > wrapper_max_lines:
        audit["blocking_findings"].append(
            f"wrapper_line_budget_exceeded:{line_count}>{wrapper_max_lines}"
        )
    return text, line_count


def _classify_target(
    target: dict[str, Any],
    *,
    workspace_root: Path,
    rule_release: str,
    project_contract_version: str,
    expected_ci_workflow_sha256: str,
) -> dict[str, Any]:
    repo_path_raw = str(target.get("repo_path") or "").strip()
    candidate = Path(repo_path_raw)
    repo_root = (workspace_root / candidate).resolve(strict=False)
    audit = _new_audit(target, repo_root)
    blocking: list[str] = audit["blocking_findings"]
    observations: list[str] = audit["observations"]

    if not repo_path_raw or candidate.is_absolute() or not _is_within(repo_root, workspace_root):
        blocking.append("repo_path_not_relative_to_workspace")
        audit["status"] = "fail"
        return audit
    if not repo_root.is_dir():
        audit["status"] = "unavailable"
        observations.append("repo_root_unavailable")
        return audit
    if _git_root(repo_root) != repo_root:
        blocking.append("target_not_git_root")

    tools = target.get("tools")
    if tools != EXPECTED_TOOLS:
        blocking.append("managed_tools_invalid")
    if target.get("coordination_mode") != "audit_only":
        blocking.append("coordination_mode_invalid")
    github_repository = str(target.get("github_repository") or "").strip()
    if not GITHUB_REPOSITORY_PATTERN.fullmatch(github_repository):
        blocking.append("github_repository_invalid")
    target_contract = str(target.get("project_contract_version") or "").strip()
    if target_contract != project_contract_version:
        blocking.append(
            f"manifest_project_contract_mismatch:{target_contract or 'missing'}->{project_contract_version}"
        )

    project_rule = str(target.get("project_common_rule") or "AGENTS.md")
    wrapper_rule = str(target.get("claude_wrapper_rule") or "CLAUDE.md")
    ci_workflow_rule = str(target.get("ci_workflow_path") or "").strip()
    project_path = (repo_root / project_rule).resolve(strict=False)
    wrapper_path = (repo_root / wrapper_rule).resolve(strict=False)
    ci_workflow_path = (repo_root / ci_workflow_rule).resolve(strict=False)
    if (
        not _is_within(project_path, repo_root)
        or not _is_within(wrapper_path, repo_root)
        or not ci_workflow_rule
        or not _is_within(ci_workflow_path, repo_root)
    ):
        blocking.append("rule_path_escapes_repository")
        audit["status"] = "fail"
        return audit
    if not project_path.exists():
        blocking.append("project_rule_missing")
        audit["status"] = "fail"
        return audit

    ci_workflow_sha256 = None
    ci_workflow_raw_sha256 = None
    ci_workflow_line_endings = None
    if not ci_workflow_path.is_file():
        blocking.append("ci_workflow_missing")
    else:
        ci_workflow_raw = ci_workflow_path.read_bytes()
        ci_workflow_raw_sha256 = hashlib.sha256(ci_workflow_raw).hexdigest()
        ci_workflow_line_endings = _workflow_line_endings(ci_workflow_raw)
        try:
            ci_workflow_sha256 = hashlib.sha256(
                _normalize_utf8_lf(ci_workflow_raw)
            ).hexdigest()
        except UnicodeDecodeError:
            blocking.append("ci_workflow_not_utf8")
        else:
            if ci_workflow_sha256 != expected_ci_workflow_sha256:
                blocking.append("ci_workflow_hash_mismatch")

    project_raw = project_path.read_bytes()
    try:
        project_text = project_raw.decode("utf-8")
    except UnicodeDecodeError:
        blocking.append("project_rule_not_utf8")
        audit["status"] = "fail"
        return audit

    project_line_count = len(project_text.splitlines())
    project_max_bytes = _configured_budget(target, "project_max_bytes", 16384)
    project_max_lines = _configured_budget(target, "project_max_lines", 140)
    wrapper_max_lines = _configured_budget(target, "wrapper_max_lines", 20)
    effective_warning_lines = _configured_budget(
        target, "effective_context_warning_lines", project_max_lines + wrapper_max_lines
    )
    if len(project_raw) > project_max_bytes:
        blocking.append(f"project_byte_budget_exceeded:{len(project_raw)}>{project_max_bytes}")
    if project_line_count > project_max_lines:
        blocking.append(
            f"project_line_budget_exceeded:{project_line_count}>{project_max_lines}"
        )

    project_version = _extract_marker(project_text, "项目契约")
    reviewed_release = _extract_marker(project_text, "全局规则复核")
    expected_reviewed_release = str(target.get("reviewed_global_release") or "").strip()
    if project_version != target_contract:
        blocking.append(
            f"project_contract_mismatch:{project_version or 'missing'}->{target_contract or 'missing'}"
        )
    if reviewed_release != expected_reviewed_release:
        blocking.append(
            "reviewed_global_release_mismatch:"
            f"{reviewed_release or 'missing'}->{expected_reviewed_release or 'missing'}"
        )
    elif reviewed_release != rule_release:
        observations.append(f"global_review_lag:{reviewed_release}->{rule_release}")

    missing_sections = [
        section
        for section, pattern in REQUIRED_SECTION_PATTERNS.items()
        if not re.search(pattern, project_text)
    ]
    if missing_sections:
        blocking.append("project_structure_missing:" + ",".join(missing_sections))
    host_specific_hits = [
        finding
        for finding, pattern in HOST_SPECIFIC_PROJECT_PATTERNS.items()
        if re.search(pattern, project_text)
    ]
    if host_specific_hits:
        blocking.append("project_rule_not_host_neutral")
    managed_family_hits = [
        token for token in MANAGED_FAMILY_FORBIDDEN_TOKENS if token in project_text
    ]
    if managed_family_hits:
        blocking.append("project_managed_family_residue")
    _audit_na_contract(project_text, blocking)

    required_contract_tokens = [
        "当前落点",
        "目标归宿",
        "build -> test -> contract/invariant -> hotspot",
        "回滚",
    ]
    evidence_path = str(target.get("evidence_path") or "").strip()
    if evidence_path:
        required_contract_tokens.append(evidence_path.rstrip("/\\"))
    required_contract_tokens.append(ci_workflow_rule)
    for token in required_contract_tokens:
        if token not in project_text:
            blocking.append(f"project_contract_token_missing:{token}")

    anchors = target.get("required_anchors")
    if not isinstance(anchors, list) or not anchors:
        blocking.append("required_anchors_missing")
        anchors = []
    for anchor in anchors:
        anchor_text = str(anchor)
        if anchor_text not in project_text:
            blocking.append(f"required_anchor_missing:{anchor_text}")

    wrapper_mode = str(target.get("claude_wrapper_mode") or "import_only")
    _, wrapper_line_count = _audit_wrapper(
        wrapper_path=wrapper_path,
        wrapper_mode=wrapper_mode,
        wrapper_max_lines=wrapper_max_lines,
        audit=audit,
    )
    effective_lines = project_line_count + wrapper_line_count
    if effective_lines > effective_warning_lines:
        observations.append(
            f"effective_context_warning:{effective_lines}>{effective_warning_lines}"
        )
    if _git_dirty(repo_root):
        observations.append("dirty_worktree")
    nested_rules = _nested_rule_files(repo_root, project_rule, wrapper_rule)
    if nested_rules:
        observations.append(f"nested_rule_files:{len(nested_rules)}")

    audit["details"] = {
        "project_rule": str(project_path.relative_to(repo_root)).replace("\\", "/"),
        "claude_wrapper_rule": str(wrapper_path.relative_to(repo_root)).replace("\\", "/"),
        "github_repository": github_repository,
        "ci_workflow_path": str(ci_workflow_path.relative_to(repo_root)).replace("\\", "/"),
        "ci_workflow_sha256": ci_workflow_sha256,
        "ci_workflow_raw_sha256": ci_workflow_raw_sha256,
        "ci_workflow_line_endings": ci_workflow_line_endings,
        "project_contract_version": project_version,
        "reviewed_global_release": reviewed_release,
        "project_bytes": len(project_raw),
        "project_lines": project_line_count,
        "wrapper_lines": wrapper_line_count,
        "host_specific_hits": host_specific_hits,
        "managed_family_hits": managed_family_hits,
        "nested_rule_files": nested_rules,
    }
    audit["status"] = "fail" if blocking else "pass"
    return audit


def verify(
    *,
    coordination_path: Path,
    target_filters: list[str] | None = None,
    require_all: bool = False,
    workspace_root_override: Path | None = None,
) -> dict[str, Any]:
    coordination_path = coordination_path.resolve(strict=False)
    payload = _load_json(coordination_path)
    top_level_blocking: list[str] = []
    schema_version = str(payload.get("schema_version") or "").strip()
    rule_release = str(payload.get("rule_release") or "").strip()
    project_contract_version = str(payload.get("project_contract_version") or "").strip()
    if schema_version != "2.3":
        top_level_blocking.append(f"schema_version_unsupported:{schema_version or 'missing'}")
    if payload.get("coordination_id") != "target-project-rule-coordination":
        top_level_blocking.append("coordination_id_invalid")
    if not rule_release:
        top_level_blocking.append("rule_release_missing")
    if not project_contract_version:
        top_level_blocking.append("project_contract_version_missing")

    ci_contract = payload.get("ci_contract")
    if not isinstance(ci_contract, dict):
        top_level_blocking.append("ci_contract_missing")
        ci_contract = {}
    if ci_contract.get("contract_id") != "agent-rule-contract-ci":
        top_level_blocking.append("ci_contract_id_invalid")
    if ci_contract.get("version") != "2.1":
        top_level_blocking.append("ci_contract_version_invalid")
    workflow_hash_mode = str(ci_contract.get("workflow_hash_mode") or "").strip()
    if workflow_hash_mode != "utf8_lf_v1":
        top_level_blocking.append("ci_workflow_hash_mode_invalid")
    expected_ci_workflow_sha256 = str(ci_contract.get("workflow_sha256") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_ci_workflow_sha256):
        top_level_blocking.append("ci_workflow_sha256_invalid")

    workspace_root_raw = str(payload.get("workspace_root") or "").strip()
    if not workspace_root_raw:
        top_level_blocking.append("workspace_root_missing")
    updated_on = str(payload.get("updated_on") or "").strip()
    try:
        date.fromisoformat(updated_on)
    except ValueError:
        top_level_blocking.append(f"updated_on_invalid:{updated_on or 'missing'}")

    workspace_root = (
        workspace_root_override.resolve(strict=False)
        if workspace_root_override is not None
        else _resolve_workspace_root(coordination_path, payload.get("workspace_root"))
    )
    targets = payload.get("targets", [])
    if not isinstance(targets, list):
        raise ValueError("coordination targets must be an array")

    target_by_id: dict[str, dict[str, Any]] = {}
    for target in targets:
        if not isinstance(target, dict):
            top_level_blocking.append("target_entry_not_object")
            continue
        repo_id = str(target.get("repo_id") or "").strip()
        if not repo_id:
            top_level_blocking.append("target_repo_id_missing")
        elif repo_id in target_by_id:
            top_level_blocking.append(f"target_repo_id_duplicate:{repo_id}")
        else:
            target_by_id[repo_id] = target

    inventory_contract = payload.get("workspace_inventory")
    if not isinstance(inventory_contract, dict):
        top_level_blocking.append("workspace_inventory_missing")
        inventory_contract = {}
    inventory_mode = str(inventory_contract.get("mode") or "").strip()
    excluded_directories_raw = inventory_contract.get("excluded_directories")
    unlisted_policy = str(
        inventory_contract.get("unlisted_repository_policy") or ""
    ).strip()
    missing_policy = str(
        inventory_contract.get("missing_allowlisted_repository_policy") or ""
    ).strip()
    if inventory_mode != "direct_git_roots":
        top_level_blocking.append("workspace_inventory_mode_invalid")
    if not isinstance(excluded_directories_raw, list) or not all(
        isinstance(item, str) and item.strip() for item in excluded_directories_raw
    ):
        top_level_blocking.append("workspace_inventory_exclusions_invalid")
        excluded_directories: set[str] = set()
    else:
        excluded_directories = {item.strip() for item in excluded_directories_raw}
    if unlisted_policy != "block":
        top_level_blocking.append("workspace_inventory_unlisted_policy_invalid")
    if missing_policy != "block_on_require_all":
        top_level_blocking.append("workspace_inventory_missing_policy_invalid")

    wanted = list(dict.fromkeys(target_filters or []))
    unknown_filters = [repo_id for repo_id in wanted if repo_id not in target_by_id]
    if unknown_filters:
        top_level_blocking.append("unknown_target_filters:" + ",".join(unknown_filters))
    selected = (
        [target_by_id[repo_id] for repo_id in wanted if repo_id in target_by_id]
        if wanted
        else list(target_by_id.values())
    )
    listed_repo_paths = sorted(
        {
            str(target.get("repo_path") or "").strip().replace("\\", "/")
            for target in target_by_id.values()
            if str(target.get("repo_path") or "").strip()
        },
        key=str.casefold,
    )
    if wanted:
        inventory_result: dict[str, Any] = {
            "status": "skipped",
            "reason": "target_filters",
            "mode": inventory_mode,
            "excluded_directories": sorted(excluded_directories, key=str.casefold),
            "discovered_repositories": [],
            "unlisted_repositories": [],
            "allowlisted_not_discovered": [],
        }
    elif not workspace_root.is_dir():
        inventory_result = {
            "status": "unavailable",
            "reason": "workspace_root_unavailable",
            "mode": inventory_mode,
            "excluded_directories": sorted(excluded_directories, key=str.casefold),
            "discovered_repositories": [],
            "unlisted_repositories": [],
            "allowlisted_not_discovered": listed_repo_paths,
        }
    else:
        discovered_repositories = _discover_direct_git_roots(
            workspace_root, excluded_directories
        )
        unlisted_repositories = sorted(
            set(discovered_repositories) - set(listed_repo_paths), key=str.casefold
        )
        allowlisted_not_discovered = sorted(
            set(listed_repo_paths) - set(discovered_repositories), key=str.casefold
        )
        if unlisted_policy == "block":
            top_level_blocking.extend(
                f"unlisted_workspace_repository:{repo_path}"
                for repo_path in unlisted_repositories
            )
        if require_all and missing_policy == "block_on_require_all":
            top_level_blocking.extend(
                f"allowlisted_repository_not_discovered:{repo_path}"
                for repo_path in allowlisted_not_discovered
            )
        inventory_result = {
            "status": "fail" if unlisted_repositories or (require_all and allowlisted_not_discovered) else "pass",
            "reason": None,
            "mode": inventory_mode,
            "excluded_directories": sorted(excluded_directories, key=str.casefold),
            "discovered_repositories": discovered_repositories,
            "unlisted_repositories": unlisted_repositories,
            "allowlisted_not_discovered": allowlisted_not_discovered,
        }
    def classify(target: dict[str, Any]) -> dict[str, Any]:
        return _classify_target(
            target,
            workspace_root=workspace_root,
            rule_release=rule_release,
            project_contract_version=project_contract_version,
            expected_ci_workflow_sha256=expected_ci_workflow_sha256,
        )

    with ThreadPoolExecutor(max_workers=min(4, max(1, len(selected)))) as executor:
        audits = list(executor.map(classify, selected))
    failures = [item for item in audits if item["status"] == "fail"]
    unavailable = [item for item in audits if item["status"] == "unavailable"]
    if require_all:
        top_level_blocking.extend(
            f"target_unavailable:{item['repo_id']}" for item in unavailable
        )
    aggregate_observations = [
        f"{item['repo_id']}:{observation}"
        for item in audits
        for observation in item["observations"]
    ]

    status = "fail" if top_level_blocking or failures else "pass"
    return {
        "status": status,
        "coordination_path": _display_path(coordination_path),
        "schema_version": schema_version,
        "rule_release": rule_release,
        "project_contract_version": project_contract_version,
        "ci_contract": {
            "contract_id": ci_contract.get("contract_id"),
            "version": ci_contract.get("version"),
            "workflow_hash_mode": workflow_hash_mode,
            "workflow_sha256": expected_ci_workflow_sha256,
        },
        "workspace_root": _display_path(workspace_root),
        "workspace_inventory": inventory_result,
        "require_all": require_all,
        "selected_target_count": len(audits),
        "failed_target_count": len(failures),
        "unavailable_target_count": len(unavailable),
        "blocking_findings": top_level_blocking,
        "observations": aggregate_observations,
        "results": audits,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit explicit target repositories for host-neutral project rule coordination."
    )
    parser.add_argument("--coordination-path", default=str(DEFAULT_COORDINATION_PATH))
    parser.add_argument("--targets", nargs="*", default=None)
    parser.add_argument(
        "--workspace-root",
        default=None,
        help="Override the manifest workspace root for CI or isolated checkout layouts.",
    )
    parser.add_argument(
        "--require-all",
        action="store_true",
        help="Treat unavailable allowlisted target repositories as blocking.",
    )
    args = parser.parse_args(argv)

    result = verify(
        coordination_path=Path(args.coordination_path),
        target_filters=list(args.targets) if args.targets else None,
        require_all=args.require_all,
        workspace_root_override=Path(args.workspace_root) if args.workspace_root else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
