# CCHS-003 Codex CLI Continuity Auto-Resume Evidence

## Scope
- Rule ID: CCHS-003
- Risk: low in default mode; real `codex exec` still requires `--execute`
- Landing: `scripts/codex-cli-continuity-runner.py`, `scripts/Start-CodexContinuity.ps1`, `tests/runtime/test_codex_cli_continuity_runner.py`
- Target: make an explicit continuity entrypoint auto-start the next CLI segment after quota/auth/account-limit failure and observed Cockpit account change
- Rollback: revert this evidence file, `scripts/Start-CodexContinuity.ps1`, and the runner/test changes

## Commands
- `python -m unittest tests.runtime.test_codex_cli_continuity_runner`
- `python scripts/codex-cli-continuity-runner.py --task-id cchs-loop-smoke --repo D:\CODE\governed-ai-coding-runtime --prompt "finish smoke" --max-segments 2 --wait-seconds 1 --simulate-results "[...]" --json`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Start-CodexContinuity.ps1 -TaskId cchs-wrapper-smoke -Repo D:\CODE\governed-ai-coding-runtime -Prompt "wrapper smoke" -MaxSegments 1`
- `git diff --check`

## Key Output
- Focused tests: `Ran 5 tests ... OK`
- Wrapper dry-run: `status=success`, `mode=dry_run`, `max_segments=1`
- Simulated no-change smoke: `status=waiting_for_account_change`, handoff written to `docs/change-evidence/codex-cli-continuity/cchs-loop-smoke-segment-1-handoff.md`

## Compatibility
- Bare `codex` is not replaced or wrapped.
- `Start-CodexContinuity.ps1` is an explicit opt-in entrypoint.
- Default Python runner mode remains dry-run unless `--execute` is provided.
- Multi-segment continuation only proceeds when the previous segment failed with quota/auth/account-limit and a Cockpit account change is observed.
- The runner does not restart Codex App and does not write Cockpit or Codex auth/config files.

## Result
- `pass`: bounded multi-segment continuation is implemented and covered by unit tests.
- `pending_live_execute`: a real quota-triggered live run still requires explicit use of `-Execute`.
