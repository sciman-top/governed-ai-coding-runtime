# CCHS-003 Codex CLI Continuity Runner Evidence

## Scope
- Rule ID: CCHS-003
- Risk: low in default mode; live `codex exec` remains opt-in behind `--execute`
- Landing: `scripts/codex-cli-continuity-runner.py`, `tests/runtime/test_codex_cli_continuity_runner.py`
- Target: classify quota/auth/account-limit failures and generate a resumable handoff for a fresh CLI segment
- Rollback: revert this evidence file, runner, focused test, and dry-run handoff artifact

## Commands
- `python -m unittest tests.runtime.test_codex_cli_continuity_runner`
- `python scripts/codex-cli-continuity-runner.py --task-id cchs-003-dry --repo D:\CODE\governed-ai-coding-runtime --prompt "CCHS dry run" --simulate-exit-code 1 --simulate-stderr "429 insufficient_quota" --wait-seconds 0 --json`
- `git diff --check`

## Key Output
- Focused tests: `Ran 3 tests ... OK`
- Dry-run mode: `mode=dry_run`
- Failure classification: `failure_reason=quota`, `retryable=true`
- Generated handoff: `docs/change-evidence/codex-cli-continuity/cchs-003-dry-segment-1-handoff.md`
- Live command execution: not performed; `--execute` was not used

## Compatibility
- Default mode never starts `codex exec`.
- The runner only writes evidence/handoff files under the requested evidence directory.
- The runner records account suffixes only.
- The runner does not restart Codex App and does not modify Cockpit or Codex auth/config files.

## Remaining Live Boundary
- A real quota-triggered continuity run still requires an explicit operator-approved live smoke with `--execute`.
- This slice proves command construction, failure classification, account-change waiting, and handoff generation against tests and simulated failure output.
