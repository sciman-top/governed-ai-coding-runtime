# 2026-05-02 Local Agent Config Audit Hardening

## Goal
Extend the existing `GAP-138` policy/tool/credential audit so local Codex, Claude, and Gemini user settings are checked without overriding accepted operator preferences.

Accepted preference exceptions:
- Claude plaintext login token may remain for convenience when credential-bearing config files are denied to agents.
- Codex `approval_policy = "never"` may remain for automation when deterministic `.codex/rules/*.rules` guards are present.
- MCP config may remain managed by automatic sync when credentials are referenced through environment variables instead of expanded token values.

## Changes
- Updated `scripts/build-policy-tool-credential-audit.py` to add `local_agent_config_audit`.
- Updated `scripts/verify-policy-tool-credential-audit.py` so local agent config failures fail closed, while missing local agent tools on non-operator hosts are `platform_na`.
- Updated `tests/runtime/test_policy_tool_credential_audit.py` with a temp-home regression test that proves accepted convenience settings pass without exposing token values.
- Updated `docs/specs/policy-tool-credential-audit-spec.md` with the local configuration invariants.
- Regenerated `docs/change-evidence/policy-tool-credential-audit-report.json`.

## Verification
Command:

```powershell
python -m unittest tests.runtime.test_policy_tool_credential_audit
```

Result: pass. Key output: `Ran 4 tests ... OK`.

Command:

```powershell
python scripts/verify-policy-tool-credential-audit.py
```

Result: pass. Key output includes `local_agent_config_audit.status = pass` and all local checks passing:
- `codex_analytics_disabled`
- `codex_never_policy_has_rules_guard`
- `claude_sensitive_settings_read_denied`
- `gemini_secure_mode_enabled`
- `gemini_secret_redaction_configured`
- `gemini_sensitive_files_ignored`
- `codex_mcp_tokens_use_env_refs`
- `claude_mcp_tokens_use_env_refs`
- `gemini_mcp_tokens_use_env_refs`

## Rollback
- Revert `scripts/build-policy-tool-credential-audit.py`.
- Revert `scripts/verify-policy-tool-credential-audit.py`.
- Revert `tests/runtime/test_policy_tool_credential_audit.py`.
- Revert `docs/specs/policy-tool-credential-audit-spec.md`.
- Regenerate or revert `docs/change-evidence/policy-tool-credential-audit-report.json`.
