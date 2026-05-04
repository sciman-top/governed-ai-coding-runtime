# 2026-05-04 Local Agent Context and Antigravity Hardening

- rule_id: `R6`, `R8`, `E4`, `E5`
- risk_level: medium
- landing: local agent configuration audit chain and user-level Gemini Antigravity settings
- target_state: Codex context-window changes require a local catalog probe; Gemini Antigravity carries the same security/context posture as the main Gemini CLI settings.
- compatibility: no auth/login/provider change; no Codex default change; Gemini Antigravity keeps existing MCP server definitions and uses environment-variable credential references.

## Changes

- Added `context_window_probe` to `scripts/lib/codex_local.py` and exposed it through `python scripts/codex-account.py context-probe --run-codex`.
- Integrated `codex_context_window_policy_sane` and `gemini_antigravity_security_guarded_when_present` into `scripts/build-policy-tool-credential-audit.py`.
- Added `scripts/Optimize-GeminiLocal.ps1` for dry-run/apply hardening of `~/.gemini/antigravity/settings.json`.
- Applied the Gemini Antigravity hardening locally. Backup for the pre-change file: `C:\Users\sciman\.gemini\settings-backups\antigravity-settings-20260504-205053.json`.

## Evidence

- `python scripts/codex-account.py context-probe --run-codex`
  - status: `pass`
  - local bundled catalog for `gpt-5.5`: `context_window=272000`, `max_context_window=272000`, `effective_context_window_percent=95`
  - configured policy: `model_context_window=272000`, `model_auto_compact_token_limit=220000`, `compact_ratio=0.8088`
  - recommendation: `keep_current`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-GeminiLocal.ps1`
  - dry-run changes before apply: `admin.secureModeEnabled=true`, `security.environmentVariableRedaction.blocked`, `advanced.excludedEnvVars`, `context.fileFiltering.*`, `mcp.excluded=github`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-GeminiLocal.ps1 -Apply`
  - status: `ok`
  - wrote `C:\Users\sciman\.gemini\antigravity\settings.json`
- `pwsh -NoProfile -Command '& { ... Test-Json -Schema ... }'`
  - result: `True`
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_policy_tool_credential_audit`
  - result: `OK`
- `python scripts/build-policy-tool-credential-audit.py`
  - result: `status=pass`, `local_agent_config_status=pass`, `failed_checks=[]`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
  - scope: 104 runtime/service test files, failures: `0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: `OK policy-tool-credential-audit`, `OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: exit code `0`; `OK` checks passed with existing `WARN codex-capability-degraded` for native attach/status handshake limitation.

## Rollback

- Repository code/report rollback:
  - `git checkout -- scripts/lib/codex_local.py scripts/codex-account.py scripts/build-policy-tool-credential-audit.py scripts/Optimize-GeminiLocal.ps1 tests/runtime/test_codex_local.py tests/runtime/test_policy_tool_credential_audit.py docs/change-evidence/policy-tool-credential-audit-report.json docs/change-evidence/20260504-local-agent-context-and-antigravity-hardening.md`
- Local Gemini Antigravity rollback:
  - Restore `C:\Users\sciman\.gemini\settings-backups\antigravity-settings-20260504-205053.json` to `C:\Users\sciman\.gemini\antigravity\settings.json`.
