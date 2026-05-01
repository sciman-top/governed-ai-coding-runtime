from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "docs" / "architecture" / "policy-tool-credential-audit-boundary.json"
DEFAULT_OUTPUT = ROOT / "docs" / "change-evidence" / "policy-tool-credential-audit-report.json"
DEFAULT_REPO_PROFILE = ROOT / ".governed-ai" / "repo-profile.json"
DEFAULT_TOOL_CONTRACT = ROOT / "schemas" / "examples" / "tool-contract" / "default-runtime.example.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a fail-closed policy/tool/credential audit report.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--repo-profile", default=str(DEFAULT_REPO_PROFILE))
    parser.add_argument("--tool-contract", default=str(DEFAULT_TOOL_CONTRACT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    try:
        result = build_policy_tool_credential_audit(
            repo_root=Path(args.repo_root),
            config_path=Path(args.config),
            repo_profile_path=Path(args.repo_profile),
            tool_contract_path=Path(args.tool_contract),
            output_path=Path(args.output),
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def build_policy_tool_credential_audit(
    *,
    repo_root: Path,
    config_path: Path,
    repo_profile_path: Path,
    tool_contract_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    repo_root = repo_root.resolve(strict=False)
    config = _load_json(config_path)
    repo_profile = _load_json(repo_profile_path)
    tool_contract = _load_json(tool_contract_path)

    entries = config.get("entries", [])
    if not isinstance(entries, list) or not entries:
        raise ValueError("audit config entries must be a non-empty list")

    override_entries = config.get("target_repo_override_entries", [])
    if not isinstance(override_entries, list) or not override_entries:
        raise ValueError("audit config target_repo_override_entries must be a non-empty list")

    known_tools = {str(entry["tool_name"]).strip().lower() for entry in entries}
    tool_decisions = {
        str(entry["tool_name"]).strip().lower(): str(entry.get("decision", "")).strip().lower()
        for entry in entries
    }
    allowlist = repo_profile.get("tool_allowlist", [])
    if not isinstance(allowlist, list):
        raise ValueError("repo profile tool_allowlist must be a list")
    normalized_allowlist = sorted({str(item).strip().lower() for item in allowlist if str(item).strip()})
    unknown_tools = [tool for tool in normalized_allowlist if tool not in known_tools]
    denied_allowlisted_tools = [
        tool
        for tool in normalized_allowlist
        if tool in known_tools and tool_decisions.get(tool) != "allow"
    ]

    registry_declared_tools = sorted(
        {
            str(item.get("tool_name", "")).strip().lower()
            for item in tool_contract.get("tools", [])
            if isinstance(item, dict) and str(item.get("tool_name", "")).strip()
        }
    )

    missing_policy_basis_refs: list[str] = []
    missing_evidence_refs: list[str] = []
    missing_registry_refs: list[str] = []
    overbroad_credential_refs: list[str] = []
    unsupported_override_refs: list[str] = []

    audited_tools: list[dict[str, Any]] = []
    for entry in entries:
        tool_name = str(entry["tool_name"]).strip().lower()
        policy_refs = _string_list(entry.get("policy_basis_refs"))
        evidence_refs = _string_list(entry.get("evidence_refs"))
        registry_refs = _string_list(entry.get("registry_refs"))
        credential_scope = entry.get("credential_scope", {})
        if not isinstance(credential_scope, dict):
            credential_scope = {}

        entry_missing_policy = [ref for ref in policy_refs if not (repo_root / ref).exists()]
        entry_missing_evidence = [ref for ref in evidence_refs if not (repo_root / ref).exists()]
        entry_missing_registry = [ref for ref in registry_refs if not (repo_root / ref).exists()]

        missing_policy_basis_refs.extend(f"{tool_name}:{ref}" for ref in entry_missing_policy)
        missing_evidence_refs.extend(f"{tool_name}:{ref}" for ref in entry_missing_evidence)
        missing_registry_refs.extend(f"{tool_name}:{ref}" for ref in entry_missing_registry)

        overbroad = _is_overbroad_scope(credential_scope)
        denied_but_allowlisted = tool_name in denied_allowlisted_tools
        if overbroad:
            overbroad_credential_refs.append(tool_name)

        audited_tools.append(
            {
                "tool_name": tool_name,
                "host_surface": entry.get("host_surface"),
                "decision": entry.get("decision"),
                "credential_scope": {
                    "scope_id": credential_scope.get("scope_id"),
                    "scope_kind": credential_scope.get("scope_kind"),
                    "resource_boundary": credential_scope.get("resource_boundary"),
                    "owner_boundary": credential_scope.get("owner_boundary"),
                    "allowed_actions": _string_list(credential_scope.get("allowed_actions")),
                },
                "policy_basis_refs": policy_refs,
                "evidence_refs": evidence_refs,
                "registry_refs": registry_refs,
                "remediation": entry.get("remediation"),
                "repo_profile_allowlisted": tool_name in normalized_allowlist,
                "status": "fail"
                if entry_missing_policy or entry_missing_evidence or entry_missing_registry or overbroad or denied_but_allowlisted
                else "pass",
            }
        )

    override_audit: list[dict[str, Any]] = []
    for entry in override_entries:
        surface_id = str(entry.get("surface_id", "")).strip()
        declared_rule = str(entry.get("declared_rule", "")).strip()
        basis_refs = _string_list(entry.get("basis_refs"))
        missing_basis = [ref for ref in basis_refs if not (repo_root / ref).exists()]
        if declared_rule not in {"tighten_only", "platform_limit_only"}:
            unsupported_override_refs.append(surface_id or "<missing-surface>")
        if missing_basis:
            missing_policy_basis_refs.extend(f"{surface_id}:{ref}" for ref in missing_basis)
        override_audit.append(
            {
                "surface_id": surface_id,
                "declared_rule": declared_rule,
                "limitation_note": entry.get("limitation_note"),
                "basis_refs": basis_refs,
                "status": "fail" if missing_basis or declared_rule not in {"tighten_only", "platform_limit_only"} else "pass",
            }
        )

    status = "pass"
    if (
        unknown_tools
        or denied_allowlisted_tools
        or missing_policy_basis_refs
        or missing_evidence_refs
        or missing_registry_refs
        or overbroad_credential_refs
        or unsupported_override_refs
    ):
        status = "fail"

    report = {
        "status": status,
        "schema_version": config.get("schema_version"),
        "audit_id": config.get("audit_id"),
        "reviewed_on": config.get("reviewed_on"),
        "verification_command": config.get("verification_command"),
        "report_path": output_path.resolve(strict=False).as_posix(),
        "fail_closed_defaults": config.get("fail_closed_defaults", {}),
        "registry_declared_tools": registry_declared_tools,
        "repo_profile_allowlist": normalized_allowlist,
        "audited_tools": audited_tools,
        "override_audit": override_audit,
        "unknown_tools": unknown_tools,
        "denied_allowlisted_tools": denied_allowlisted_tools,
        "missing_policy_basis_refs": sorted(set(missing_policy_basis_refs)),
        "missing_evidence_refs": sorted(set(missing_evidence_refs)),
        "missing_registry_refs": sorted(set(missing_registry_refs)),
        "overbroad_credential_refs": sorted(set(overbroad_credential_refs)),
        "unsupported_override_refs": sorted(set(unsupported_override_refs)),
        "summary": {
            "known_tool_count": len(known_tools),
            "registry_declared_tool_count": len(registry_declared_tools),
            "repo_profile_allowlist_count": len(normalized_allowlist),
            "audited_tool_count": len(audited_tools),
            "override_surface_count": len(override_audit),
            "unknown_tool_count": len(unknown_tools),
            "denied_allowlisted_tool_count": len(denied_allowlisted_tools),
            "missing_policy_basis_count": len(set(missing_policy_basis_refs)),
            "overbroad_credential_count": len(set(overbroad_credential_refs)),
            "unsupported_override_count": len(set(unsupported_override_refs)),
        },
        "rollback_ref": config.get("rollback_ref"),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"json file is not readable: {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"json file is invalid: {path} ({exc.msg})") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"json object required: {path}")
    return payload


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            result.append(text)
    return result


def _is_overbroad_scope(scope: dict[str, Any]) -> bool:
    boundary = str(scope.get("resource_boundary", "")).strip().lower()
    owner_boundary = str(scope.get("owner_boundary", "")).strip().lower()
    actions = [item.lower() for item in _string_list(scope.get("allowed_actions"))]
    if "*" in boundary or "*" in owner_boundary:
        return True
    overbroad_markers = ("all credentials", "all providers", "all tools", "unbounded", "any provider", "any tool")
    if any(marker in boundary for marker in overbroad_markers):
        return True
    if any(marker in owner_boundary for marker in overbroad_markers):
        return True
    return any("*" in action or "all " in action for action in actions)


if __name__ == "__main__":
    raise SystemExit(main())
