# CCHS-002 Codex Cockpit Switch Health Evidence

## Scope
- Rule ID: CCHS-002
- Risk: low, read-only diagnostics
- Landing: `scripts/codex-cockpit-switch-health.py`, `tests/runtime/test_codex_cockpit_switch_health.py`
- Target: explain Cockpit Tools Codex auto-switch state without changing Cockpit or Codex config
- Rollback: revert this evidence file, script, and focused test

## Commands
- `python -m unittest tests.runtime.test_codex_cockpit_switch_health`
- `python scripts/codex-cockpit-switch-health.py --target-surface codex_app --json`
- `git diff --check`

## Key Output
- Focused tests: `Ran 2 tests ... OK`
- Live account catalog: `total_accounts=328`
- Live auto switch: `codex_auto_switch_enabled=true`
- Live refresh interval: `codex_auto_refresh_minutes=15`
- Live selected scope: `selected_count=320`, `selected_found_count=320`, `selected_missing_count=0`, `selected_plan_types=["free"]`
- Live restart flags: `codex_launch_on_switch=false`, `codex_restart_specified_app_on_switch=false`
- Live runtime boundary: `codex_app_restart_required_for_account_change=true`
- Live recent auth errors: `token_invalidated_count=921` across the latest three Cockpit log files scanned
- Write actions: `[]`

## Compatibility
- The checker reads only `config.json`, `codex_accounts.json`, and recent Cockpit log files.
- The checker reports account id suffix samples only and does not emit email, token, authorization, or full account objects.
- The checker does not restart, stop, kill, launch, or reconfigure Codex App, Codex CLI, or Cockpit Tools.

## Result
- `pass`: read-only guard implemented and verified.
- `warn`: the live App target still requires restart or native hot reload for account changes, and recent Cockpit logs contain 401/token invalidation evidence.
