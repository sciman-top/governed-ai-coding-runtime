# 2026-05-23 Token-Efficient Search Ignore

- rules: R1/R6/R8, context_budget_and_instruction_minimalism
- risk: low
- current_location: `D:\CODE\governed-ai-coding-runtime`
- target_destination: repo-local search/context hygiene for daily coding

## Basis
- Live Codex config inspected read-only:
  - `model_context_window = 516000`
  - `model_auto_compact_token_limit = 460000`
  - `model_reasoning_effort = "xhigh"`
- Repo-owned recommended defaults remain:
  - `scripts/lib/codex_local.py`: `272000 / 220000 / medium`
  - `tests.runtime.test_codex_local`: verifies the same recommended context and compact values
- One broad `rg ... .` search produced an original tool-output estimate over `553000` tokens because historical evidence and archive-heavy paths were included before the search surface was narrowed.

## Change
- Added root `.ignore` so daily `rg` searches skip archive-heavy and binary-heavy context by default:
  - `docs/change-evidence/**`
  - `docs/archive/**`
  - long backlog history files
  - operator UI screenshots and generated/local runtime caches
- Archived evidence remains available with explicit paths or `rg -u`.
- Adjusted live Codex user config after backup:
  - backup: `C:\Users\sciman\.codex\config.toml.bak-token-efficiency-20260523-162106`
  - `model_context_window`: `516000 -> 272000`
  - `model_auto_compact_token_limit`: `460000 -> 220000`
  - `model_reasoning_effort`: `xhigh -> medium`
  - unchanged fields verified in readback: `model_provider = "openai"`, `model = "gpt-5.3-codex"`, `sandbox_mode = "workspace-write"`, `approval_policy = "never"`

## Verification
- `rg -l <token/context pattern> .` after the change:
  - matched files: `310`
  - `docs/change-evidence` matches: `0`
  - `docs/archive` matches: `0`
  - heavy backlog matches: `0`
- `rg --files` after the change: `596` default files.
- `git diff --check -- .ignore`: pass.
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_policy_tool_credential_audit`: pass, `31` tests.
- Fresh readback of `C:\Users\sciman\.codex\config.toml` showed `272000 / 220000 / medium`.
- Backup diff showed only the intended three token-efficiency lines changed.

## Rollback
- Remove `.ignore`.
- Restore live config from `C:\Users\sciman\.codex\config.toml.bak-token-efficiency-20260523-162106` if the lower context profile causes a concrete regression.
- Re-run:
  - `rg --files`
  - `python -m unittest tests.runtime.test_codex_local tests.runtime.test_policy_tool_credential_audit`
