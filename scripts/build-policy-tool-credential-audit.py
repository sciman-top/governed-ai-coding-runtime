from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

from lib.codex_local import context_window_probe


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
    parser.add_argument("--home", default=str(Path.home()))
    args = parser.parse_args()

    try:
        result = build_policy_tool_credential_audit(
            repo_root=Path(args.repo_root),
            config_path=Path(args.config),
            repo_profile_path=Path(args.repo_profile),
            tool_contract_path=Path(args.tool_contract),
            output_path=Path(args.output),
            home_path=Path(args.home),
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
    home_path: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve(strict=False)
    home_path = (home_path or Path.home()).resolve(strict=False)
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

    local_agent_config_audit = _inspect_local_agent_config(home_path=home_path)

    status = "pass"
    if (
        unknown_tools
        or denied_allowlisted_tools
        or missing_policy_basis_refs
        or missing_evidence_refs
        or missing_registry_refs
        or overbroad_credential_refs
        or unsupported_override_refs
        or local_agent_config_audit["status"] not in {"pass", "platform_na"}
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
        "local_agent_config_audit": local_agent_config_audit,
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
            "local_agent_config_status": local_agent_config_audit["status"],
        },
        "rollback_ref": config.get("rollback_ref"),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _inspect_local_agent_config(*, home_path: Path) -> dict[str, Any]:
    codex_dir = home_path / ".codex"
    claude_dir = home_path / ".claude"
    gemini_dir = home_path / ".gemini"

    if not codex_dir.exists() and not claude_dir.exists() and not gemini_dir.exists():
        return {
            "status": "platform_na",
            "home_ref": "~",
            "reason": "No Codex, Claude, or Gemini user config directory is present under the inspected home path.",
            "checks": [],
            "failed_checks": [],
        }

    codex_config = _load_optional_toml(codex_dir / "config.toml")
    claude_settings = _load_optional_json(claude_dir / "settings.json")
    gemini_settings = _load_optional_json(gemini_dir / "settings.json")
    gemini_antigravity_settings = _load_optional_json(gemini_dir / "antigravity" / "settings.json")
    codex_context_probe = (
        context_window_probe(codex_dir, run_codex=False)
        if codex_dir.exists()
        else {"status": "platform_na", "reason": "Codex user config directory is not present.", "checks": []}
    )

    checks = [
        _check(
            check_id="codex_analytics_disabled",
            status=_nested_get(codex_config, ["analytics", "enabled"]) is False,
            reason="Codex analytics should be explicitly disabled for local governance runs.",
            evidence_ref="~/.codex/config.toml",
            remediation="Set analytics.enabled = false in ~/.codex/config.toml.",
        ),
        _check(
            check_id="codex_never_policy_has_rules_guard",
            status=(
                _nested_get(codex_config, ["approval_policy"]) != "never"
                or _has_nonempty_rules_file(codex_dir / "rules")
            ),
            reason="approval_policy=never is an accepted operator preference only when deterministic rules are present.",
            evidence_ref="~/.codex/config.toml + ~/.codex/rules/*.rules",
            remediation="Keep ~/.codex/rules/*.rules present and non-empty when using approval_policy=never.",
        ),
        _check(
            check_id="codex_context_window_policy_sane",
            status=codex_context_probe.get("status") in {"pass", "platform_na"},
            reason="Codex context window and auto-compact thresholds should remain coherent before changing model defaults.",
            evidence_ref="~/.codex/config.toml model_context_window + model_auto_compact_token_limit",
            remediation="Run `python scripts/codex-account.py context-probe --run-codex --all-catalogs --probe-exec` and align the configured context policy with the local Codex debug models catalogs before changing defaults.",
        ),
        _check(
            check_id="claude_sensitive_settings_read_denied",
            status=_claude_denies_sensitive_user_files(claude_settings),
            reason="Plaintext Claude login convenience is accepted, but agent reads of credential-bearing user config must be denied.",
            evidence_ref="~/.claude/settings.json permissions.deny",
            remediation="Add Read denies for Claude/Codex/Gemini credential-bearing user config files.",
        ),
        _check(
            check_id="gemini_secure_mode_enabled",
            status=_nested_get(gemini_settings, ["admin", "secureModeEnabled"]) is True,
            reason="Gemini secure mode should block YOLO and Always allow bypass paths for local governance runs.",
            evidence_ref="~/.gemini/settings.json admin.secureModeEnabled",
            remediation="Set admin.secureModeEnabled = true in ~/.gemini/settings.json.",
        ),
        _check(
            check_id="gemini_secret_redaction_configured",
            status=_gemini_redacts_secret_env(gemini_settings),
            reason="Gemini should redact and exclude known credential environment variables from model context.",
            evidence_ref="~/.gemini/settings.json security.environmentVariableRedaction + advanced.excludedEnvVars",
            remediation="Add common token variables to Gemini redaction and excludedEnvVars settings.",
        ),
        _check(
            check_id="gemini_sensitive_files_ignored",
            status=_gemini_ignores_sensitive_files(gemini_settings, gemini_dir / ".geminiignore"),
            reason="Gemini file discovery should respect a user-level ignore file for OAuth and account state.",
            evidence_ref="~/.gemini/settings.json context.fileFiltering + ~/.gemini/.geminiignore",
            remediation="Create ~/.gemini/.geminiignore and reference it from context.fileFiltering.customIgnoreFilePaths.",
        ),
        _check(
            check_id="gemini_antigravity_security_guarded_when_present",
            status=_gemini_antigravity_security_guarded(
                main_settings=gemini_settings,
                antigravity_settings=gemini_antigravity_settings,
                ignore_path=gemini_dir / ".geminiignore",
            ),
            reason="Gemini Antigravity settings, when present, should carry the same secure mode, secret redaction, file filtering, and GitHub MCP exclusion posture as the main Gemini CLI settings.",
            evidence_ref="~/.gemini/antigravity/settings.json + ~/.gemini/settings.json",
            remediation="Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-GeminiLocal.ps1 -Apply` to mirror the bounded security posture.",
        ),
    ]

    mcp_checks = _inspect_mcp_token_indirection(
        codex_config=codex_config,
        claude_mcp=_load_optional_json(claude_dir / ".mcp.json"),
        gemini_settings=gemini_settings,
        gemini_mcp=_load_optional_json(gemini_dir / ".mcp.json"),
        gemini_antigravity_settings=gemini_antigravity_settings,
    )
    checks.extend(mcp_checks)

    failed = [item["check_id"] for item in checks if item["status"] != "pass"]
    return {
        "status": "fail" if failed else "pass",
        "home_ref": "~",
        "personal_preference_exceptions": [
            {
                "exception_id": "claude_plaintext_token_for_login_convenience",
                "accepted_when": "credential-bearing settings files remain read-denied to agents and are not synchronized into repositories",
            },
            {
                "exception_id": "codex_approval_policy_never_for_automation",
                "accepted_when": "deterministic rules, project gates, and repository policies remain active",
            },
            {
                "exception_id": "managed_mcp_sync",
                "accepted_when": "synchronized MCP configs keep credential values indirect through environment-variable references",
            },
        ],
        "checks": checks,
        "failed_checks": failed,
        "codex_context_window_probe": codex_context_probe,
    }


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


def _load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return _load_json(path)


def _load_optional_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"toml file is not readable: {path} ({exc})") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"toml file is invalid: {path} ({exc})") from exc
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


def _nested_get(payload: dict[str, Any], keys: list[str]) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _check(*, check_id: str, status: bool, reason: str, evidence_ref: str, remediation: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "status": "pass" if status else "fail",
        "reason": reason,
        "evidence_ref": evidence_ref,
        "remediation": remediation,
    }


def _has_nonempty_rules_file(rules_dir: Path) -> bool:
    if not rules_dir.exists():
        return False
    return any(path.is_file() and path.suffix == ".rules" and path.stat().st_size > 0 for path in rules_dir.glob("*.rules"))


def _claude_denies_sensitive_user_files(settings: dict[str, Any]) -> bool:
    deny_entries = {
        item.replace("\\", "/").lower()
        for item in _string_list(_nested_get(settings, ["permissions", "deny"]))
    }
    required_suffixes = [
        "/.claude/settings.json)",
        "/.codex/auth*.json)",
        "/.gemini/oauth_creds.json)",
        "/.gemini/google_accounts.json)",
    ]
    return all(any(entry.endswith(suffix) for entry in deny_entries) for suffix in required_suffixes)


def _gemini_redacts_secret_env(settings: dict[str, Any]) -> bool:
    required = {"ANTHROPIC_AUTH_TOKEN", "GITHUB_PERSONAL_ACCESS_TOKEN", "OPENAI_API_KEY", "GEMINI_API_KEY"}
    blocked = set(_string_list(_nested_get(settings, ["security", "environmentVariableRedaction", "blocked"])))
    excluded = set(_string_list(_nested_get(settings, ["advanced", "excludedEnvVars"])))
    return _nested_get(settings, ["security", "environmentVariableRedaction", "enabled"]) is True and required <= blocked and required <= excluded


def _gemini_ignores_sensitive_files(settings: dict[str, Any], ignore_path: Path) -> bool:
    if not ignore_path.exists():
        return False
    ignore_text = ignore_path.read_text(encoding="utf-8")
    required_patterns = ("oauth_creds.json", "google_accounts.json", "*credentials*")
    custom_ignores = {
        item.replace("\\", "/").lower()
        for item in _string_list(_nested_get(settings, ["context", "fileFiltering", "customIgnoreFilePaths"]))
    }
    return (
        _nested_get(settings, ["context", "fileFiltering", "respectGeminiIgnore"]) is True
        and ignore_path.as_posix().lower() in custom_ignores
        and all(pattern in ignore_text for pattern in required_patterns)
    )


def _gemini_antigravity_security_guarded(
    *,
    main_settings: dict[str, Any],
    antigravity_settings: dict[str, Any],
    ignore_path: Path,
) -> bool:
    if not antigravity_settings:
        return True
    if _nested_get(antigravity_settings, ["admin", "secureModeEnabled"]) is not True:
        return False
    if not _gemini_redacts_secret_env(antigravity_settings):
        return False
    if not _gemini_ignores_sensitive_files(antigravity_settings, ignore_path):
        return False
    main_mcp_excluded = set(_string_list(_nested_get(main_settings, ["mcp", "excluded"])))
    antigravity_mcp_excluded = set(_string_list(_nested_get(antigravity_settings, ["mcp", "excluded"])))
    return "github" not in main_mcp_excluded or "github" in antigravity_mcp_excluded


def _inspect_mcp_token_indirection(
    *,
    codex_config: dict[str, Any],
    claude_mcp: dict[str, Any],
    gemini_settings: dict[str, Any],
    gemini_mcp: dict[str, Any],
    gemini_antigravity_settings: dict[str, Any],
) -> list[dict[str, str]]:
    return [
        _check(
            check_id="codex_mcp_tokens_use_env_refs",
            status=_codex_mcp_tokens_are_indirect(codex_config),
            reason="Codex MCP credentials should be referenced through env vars, not expanded into config.toml.",
            evidence_ref="~/.codex/config.toml mcp_servers.*.bearer_token_env_var",
            remediation="Use bearer_token_env_var for Codex MCP credentials.",
        ),
        _check(
            check_id="claude_mcp_tokens_use_env_refs",
            status=_json_mcp_tokens_are_indirect(claude_mcp),
            reason="Claude MCP config should not contain expanded bearer tokens.",
            evidence_ref="~/.claude/.mcp.json",
            remediation="Keep MCP Authorization headers as environment-variable references.",
        ),
        _check(
            check_id="gemini_mcp_tokens_use_env_refs",
            status=_json_mcp_tokens_are_indirect({"mcpServers": gemini_settings.get("mcpServers", {})})
            and _json_mcp_tokens_are_indirect(gemini_mcp)
            and _json_mcp_tokens_are_indirect({"mcpServers": gemini_antigravity_settings.get("mcpServers", {})}),
            reason="Gemini MCP config should not contain expanded bearer tokens.",
            evidence_ref="~/.gemini/settings.json + ~/.gemini/.mcp.json + ~/.gemini/antigravity/settings.json",
            remediation="Keep MCP Authorization headers as environment-variable references.",
        ),
    ]


def _codex_mcp_tokens_are_indirect(config: dict[str, Any]) -> bool:
    servers = config.get("mcp_servers", {})
    if not isinstance(servers, dict):
        return True
    for server in servers.values():
        if not isinstance(server, dict):
            continue
        if "bearer_token" in server:
            return False
        if any("token" in str(key).lower() for key in server) and "bearer_token_env_var" not in server:
            return False
    return True


def _json_mcp_tokens_are_indirect(config: dict[str, Any]) -> bool:
    servers = config.get("mcpServers", {})
    if not isinstance(servers, dict):
        return True
    for server in servers.values():
        if not isinstance(server, dict):
            continue
        headers = server.get("headers", {})
        if not isinstance(headers, dict):
            continue
        for key, value in headers.items():
            if str(key).lower() != "authorization":
                continue
            text = str(value)
            if "Bearer " in text and "$" not in text and "${" not in text:
                return False
    return True


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
