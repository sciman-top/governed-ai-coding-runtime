from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COORDINATION_PATH = ROOT / "rules" / "target-project-rule-coordination.json"
REQUIRED_PROJECT_TOKENS = [
    "runtime/host-orchestrator",
    ".ai/state/control-plane.db",
    ".ai/runs/<run_id>/<task_id>/",
    "docs/change-evidence/README.md",
    "Global Rule -> Repo Action",
    "回滚",
]
THIN_WRAPPER_FORBIDDEN_TOKENS = [
    "## A.",
    "## C.",
    "runtime/host-orchestrator",
    ".ai/state/control-plane.db",
    ".ai/runs/<run_id>/<task_id>/",
    "Global Rule -> Repo Action",
]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json object required: {path}")
    return payload


def _extract_version(text: str) -> str | None:
    patterns = (
        r"GlobalUser/(?:AGENTS|CLAUDE|GEMINI)\.md v([0-9][0-9A-Za-z_.-]*)",
        r"\*\*版本\*\*:\s*([0-9][0-9A-Za-z_.-]*)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _classify_target(target: dict[str, Any], *, manifest_version: str) -> dict[str, Any]:
    repo_id = str(target.get("repo_id") or "").strip()
    repo_root = Path(str(target.get("repo_root") or "")).resolve(strict=False)
    project_rule = str(target.get("project_common_rule") or "AGENTS.md")
    wrapper_rule = str(target.get("claude_wrapper_rule") or "CLAUDE.md")
    coordination_mode = str(target.get("coordination_mode") or "").strip()
    audit = {
        "repo_id": repo_id,
        "repo_root": str(repo_root).replace("\\", "/"),
        "tools": target.get("tools") or [],
        "coordination_mode": coordination_mode,
        "shared_body_model": False,
        "status": "pass",
        "drift_category": None,
        "next_action": "none",
        "rollback_boundary": "revert only the target repo AGENTS.md / CLAUDE.md integration slice; do not blindly overwrite target truth from the control repo.",
        "details": {},
    }

    if not repo_root.exists():
        audit["status"] = "target_unavailable"
        audit["next_action"] = "verify the target repo path and rerun the coordination audit"
        audit["details"] = {"reason": "repo_root_missing"}
        return audit

    project_path = repo_root / project_rule
    wrapper_path = repo_root / wrapper_rule

    if not project_path.exists():
        audit["status"] = "fail"
        audit["drift_category"] = "project_contract_missing"
        audit["next_action"] = "add the shared project AGENTS.md body before attempting wrapper integration"
        audit["details"] = {"missing_path": project_rule}
        return audit

    project_text = project_path.read_text(encoding="utf-8")
    project_version = _extract_version(project_text)
    missing_project_tokens = [token for token in REQUIRED_PROJECT_TOKENS if token not in project_text]
    if missing_project_tokens:
        audit["status"] = "fail"
        audit["drift_category"] = "project_contract_missing"
        audit["next_action"] = "restore repo truth, gate, evidence, and rollback tokens in AGENTS.md"
        audit["details"] = {
            "missing_project_tokens": missing_project_tokens,
            "project_rule": project_rule,
        }
        return audit

    if project_version != manifest_version:
        audit["status"] = "fail"
        audit["drift_category"] = "global_sync_drift"
        audit["next_action"] = "re-align the target project rule with the current global rule version before further wrapper work"
        audit["details"] = {
            "project_version": project_version,
            "expected_version": manifest_version,
        }
        return audit

    if not wrapper_path.exists():
        audit["status"] = "fail"
        audit["drift_category"] = "project_wrapper_missing"
        audit["next_action"] = "add a root CLAUDE.md thin wrapper with a standalone @AGENTS.md import"
        audit["details"] = {"missing_path": wrapper_rule}
        return audit

    wrapper_text = wrapper_path.read_text(encoding="utf-8")
    wrapper_lines = [line.strip() for line in wrapper_text.splitlines() if line.strip()]
    wrapper_version = _extract_version(wrapper_text)
    wrapper_forbidden_hits = [token for token in THIN_WRAPPER_FORBIDDEN_TOKENS if token in wrapper_text]
    has_import = bool(wrapper_lines) and wrapper_lines[0] == "@AGENTS.md"
    has_allowed_sections = "## B." in wrapper_text and "## D." in wrapper_text
    has_disallowed_sections = "## A." in wrapper_text or "## C." in wrapper_text

    if wrapper_version != manifest_version:
        audit["status"] = "fail"
        audit["drift_category"] = "global_sync_drift"
        audit["next_action"] = "re-align the CLAUDE.md wrapper version with the current global Claude rule"
        audit["details"] = {
            "wrapper_version": wrapper_version,
            "expected_version": manifest_version,
        }
        return audit

    if (not has_import) or has_disallowed_sections or (not has_allowed_sections) or wrapper_forbidden_hits:
        audit["status"] = "fail"
        audit["drift_category"] = "project_wrapper_nonthin"
        audit["next_action"] = "shrink CLAUDE.md to a thin wrapper: first-line @AGENTS.md, only 1/B/D, and no duplicated project truth"
        audit["details"] = {
            "has_import": has_import,
            "has_allowed_sections": has_allowed_sections,
            "has_disallowed_sections": has_disallowed_sections,
            "forbidden_hits": wrapper_forbidden_hits,
        }
        return audit

    tools = target.get("tools")
    if tools != ["codex", "claude"] or coordination_mode != "wrapper_and_contract_audit":
        audit["status"] = "fail"
        audit["drift_category"] = "manual_integration_required"
        audit["next_action"] = "reconcile the control-repo coordination contract before claiming this target is governed"
        audit["details"] = {
            "tools": tools,
            "coordination_mode": coordination_mode,
        }
        return audit

    audit["shared_body_model"] = True
    audit["details"] = {
        "project_rule": project_rule,
        "wrapper_rule": wrapper_rule,
        "project_version": project_version,
        "wrapper_version": wrapper_version,
    }
    return audit


def verify(*, coordination_path: Path, target_filters: list[str] | None = None) -> dict[str, Any]:
    payload = _load_json(coordination_path)
    manifest = _load_json(ROOT / "rules" / "manifest.json")
    manifest_version = str(manifest.get("default_version") or "").strip()
    targets = payload.get("targets", [])
    if not isinstance(targets, list):
        raise ValueError("coordination targets must be an array")

    selected: list[dict[str, Any]] = []
    wanted = set(target_filters or [])
    for target in targets:
        if not isinstance(target, dict):
            continue
        repo_id = str(target.get("repo_id") or "").strip()
        if wanted and repo_id not in wanted:
            continue
        selected.append(target)

    audits = [_classify_target(target, manifest_version=manifest_version) for target in selected]
    failures = [item for item in audits if item["status"] == "fail"]
    unavailable = [item for item in audits if item["status"] == "target_unavailable"]

    return {
        "status": "pass" if not failures else "fail",
        "coordination_path": str(coordination_path.resolve(strict=False)).replace("\\", "/"),
        "manifest_version": manifest_version,
        "selected_target_count": len(audits),
        "failed_target_count": len(failures),
        "unavailable_target_count": len(unavailable),
        "results": audits,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit target repos for thin-wrapper project rule coordination.")
    parser.add_argument("--coordination-path", default=str(DEFAULT_COORDINATION_PATH))
    parser.add_argument("--targets", nargs="*", default=None)
    args = parser.parse_args(argv)

    result = verify(
        coordination_path=Path(args.coordination_path),
        target_filters=list(args.targets) if args.targets else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
