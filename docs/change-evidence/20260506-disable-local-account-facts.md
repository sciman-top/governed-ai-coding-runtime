# 2026-05-06 disable local account facts for Codex account display

- current_landing: Codex account plan display could be overridden by `C:\Users\sciman\.codex\account-facts.json`, which is an operator-asserted local file rather than objective account evidence.
- target_landing: local `account-facts.json` no longer participates in plan resolution, and Codex account display falls back to usage/auth-derived evidence only.
- verification_scope: targeted unit test, live local file removal, and live status probe.
- rollback: revert `scripts/lib/codex_local.py` and `tests/runtime/test_codex_local.py`, then recreate `C:\Users\sciman\.codex\account-facts.json` only if a later objective-backed design is intentionally restored.

## Changes

1. Disabled `account-facts.json` as a runtime input in `scripts/lib/codex_local.py`.
   - `_load_account_facts()` now reports `status = disabled_ignored`
   - returned `accounts` is always empty, even if the local file exists
2. Kept the path/status in the payload so the operator UI and diagnostics can still show that a local override file exists but is ignored.
3. Replaced the old test that preferred local account facts with a regression test that proves the runtime now ignores them and resolves the plan from usage/auth evidence.

## Verification

```powershell
python -m unittest tests.runtime.test_codex_local.CodexLocalTests.test_status_ignores_local_account_facts_for_plan_resolution
```

Observed result:

- pass

```powershell
Remove-Item "$env:USERPROFILE\.codex\account-facts.json" -Force
python -B scripts\codex-account.py status
```

Observed result:

- local override file removed from `C:\Users\sciman\.codex`
- status payload no longer reports `plan_source = local_operator_asserted`
