# Codex Single Default Config Alignment

## Goal
- Align the repository-managed Codex recommendation with the live single-default user config.
- Preserve `model_context_window = 272000` and `model_auto_compact_token_limit = 220000`.
- Remove the stale `gpt-5.4` recommendation from active optimizer, status, tests, README, and quickstart surfaces.

## Commands
- `rg -n "gpt-5\\.5|gpt-5\\.4|model_reasoning_effort|model_context_window|model_auto_compact_token_limit|auto_compact|272000|220000|230000|profiles\\.full|outside_temp|config\\.toml" .`
- `python -m unittest tests.runtime.test_codex_local`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Optimize-CodexLocal.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`

## Key Output
- Repository-managed current default is now `gpt-5.5 + medium + never`.
- Context window remains `272000`.
- Automatic compaction threshold remains `220000`.
- The optimizer dry-run reports `model = gpt-5.5`, `model_reasoning_effort = medium`, `model_context_window = 272000`, and `model_auto_compact_token_limit = 220000`.
- Targeted `tests.runtime.test_codex_local` passed.
- Full Runtime, Contract, and Docs checks passed.
- Doctor passed with the existing `WARN codex-capability-degraded` host capability warning.

## Compatibility
- This is a default recommendation alignment only.
- The long-lived principle remains `efficiency_first`; the exact model remains a replaceable implementation detail.
- Existing safety, evidence, rollback, sandbox, and gate constraints are unchanged.

## Rollback
- Revert this file plus the active `gpt-5.5` recommendation updates in the optimizer, Python status helper, tests, README, and quickstart docs.
- Re-run `python -m unittest tests.runtime.test_codex_local` and the optimizer dry-run after rollback.
