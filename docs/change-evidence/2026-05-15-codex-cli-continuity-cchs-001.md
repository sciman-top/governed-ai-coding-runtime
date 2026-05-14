# 2026-05-15 Codex CLI Continuity CCHS-001 Evidence

## Goal
Capture the first read-only evidence slice for `CCHS-001 Native Boundary And Probe Evidence`.

## Commands
- `python scripts/codex-cockpit-switch-trace.py --label cchs-001-current --out docs/change-evidence/2026-05-15-codex-cli-continuity-current-snapshot.json --json`
- `codex exec --cd D:\CODE\governed-ai-coding-runtime --sandbox read-only --output-last-message docs/change-evidence/2026-05-15-codex-cli-exec-smoke-last-message.txt "Reply with exactly: CCHS-001-CODEX-EXEC-OK"`

## Key Output
- The trace command completed and showed Cockpit/Codex state alignment at snapshot time.
- Current Cockpit account, default instance binding, `auth.json`, and `.cockpit_codex_auth.json` pointed to the same redacted Codex account id suffix: `...43e`.
- Cockpit launch flags remained interruption-safe:
  - `codex_launch_on_switch = false`
  - `codex_restart_specified_app_on_switch = false`
- Codex state DB remained in the shared `openai` provider bucket.
- `codex exec` started a new CLI process with:
  - `model: gpt-5.5`
  - `provider: openai`
  - `sandbox: read-only`
  - `reasoning effort: medium`
  - `session id: 019e2767-a3ae-7c01-aae4-1d7b041e77f3`
- The CLI smoke final message was `CCHS-001-CODEX-EXEC-OK`.

## Privacy Handling
- The raw trace JSON included local account emails and was deleted instead of being committed.
- This evidence file keeps only redacted account suffixes and non-secret configuration conclusions.

## Findings
- New Codex CLI process startup works against the current Cockpit/Codex account projection.
- This slice does not prove post-switch behavior because no new Cockpit account switch was triggered during the trace window.
- Already-open Codex App runtime behavior still needs either manual operator-observed evidence or a future operator-approved trace around an actual switch/restart boundary.

## Rollback
- Remove this evidence file and `docs/change-evidence/2026-05-15-codex-cli-exec-smoke-last-message.txt`.
