# 2026-05-09 Codex provider bucket interop

- rules: R1/R4/R6/R8, E4/E6
- risk: medium, user-local CC Switch sqlite provider snippets are persisted but backed up before repair
- landing: `scripts/codex-interop-check.py`, `tests/runtime/test_codex_shared_launcher.py`, `README.md`, `README.zh-CN.md`
- destination: keep Cockpit Tools and CC Switch as account/provider managers while preventing provider switches from hiding Codex App/CLI history via `threads.model_provider` bucket drift

## Commands

- `python -m unittest tests.runtime.test_codex_shared_launcher`
- `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit"`
- `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --apply`
- `codex-interop-check`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`

## Evidence

- The checker now reads `state_5.sqlite.threads.model_provider` and reports the local thread provider distribution.
- The checker compares the live Codex `model_provider` and the current CC Switch Codex provider snippet against the dominant local history bucket.
- Repair remains conservative: for CC Switch relay providers with `requires_openai_auth = true` and a `base_url`, it rewrites the provider snippet to `model_provider = "openai"` plus `openai_base_url = <relay URL>`.
- Repair does not rewrite `state_5.sqlite`, `sessions`, `archived_sessions`, or message/history content.
- Unit coverage creates a temporary Codex state DB with `openai` history and verifies that a RightCode-style CC Switch provider is detected, repaired, and kept in the `openai` visibility bucket.
- Real local pre-repair check found `state_5.sqlite` distribution `{ "openai": 1578 }` and current CC Switch `RightCode` bucket `rightcode`, so `cc_switch_current_provider_bucket_a2398ca2-ed8f-4219-9d66-24db0cfd8e8e` failed with `repair_strategy = "openai_base_url"`.
- Real local repair backed up CC Switch sqlite state to `C:\Users\sciman\.cc-switch\backups\db_backup_20260509_133451_codex_interop.db`.
- Real local post-repair check returned `status = "pass"` and current CC Switch `RightCode` bucket `openai`.
- Installed shortcut script `C:\Users\sciman\.codex\scripts\codex-interop-check.py` was refreshed from this repo, and `codex-interop-check` returned `status = "pass"`.
- Build gate passed with `OK python-bytecode` and `OK python-import`.
- Runtime gate passed: 106 runtime/service test files, failures `0`.
- Contract gate passed, including schema, dependency baseline, governance consistency, agent rule sync, functional effectiveness, and policy checks.
- Doctor gate exited `0`; it retained the existing `WARN codex-capability-degraded` host capability warning.

## Rollback

- Restore `C:\Users\sciman\.cc-switch\backups\db_backup_20260509_133451_codex_interop.db` to `C:\Users\sciman\.cc-switch\cc-switch.db` if the local provider-bucket repair must be undone.
- Revert this commit from git history to remove provider-bucket detection and docs.
