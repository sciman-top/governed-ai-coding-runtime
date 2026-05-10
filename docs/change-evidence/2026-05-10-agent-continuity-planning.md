# Agent Continuity Planning Baseline

- date: 2026-05-10
- rules: R1, R2, R6, R8, E4, E6
- risk: low
- current_landing: `docs/plans/agent-continuity-and-shared-context-plan.md`
- target_home: `D:\CODE\governed-ai-coding-runtime`
- rollback: revert this documentation and schema planning slice with git; no user-local Codex, Claude, Claude Desktop, provider, or auth state was modified

## Source Evidence
- Codex shared history local optimization already landed with `sqlite_home`, `log_dir`, `[history] persistence = "save-all"`, shared profiles, launchers, operator action, and full gate evidence in `docs/change-evidence/2026-05-08-codex-shared-history-local-optimize.md`.
- Claude provider session continuity diagnostics already landed with `claude-provider continuity`, `CLAUDE_CONFIG_DIR`, `~/.claude/projects`, `history.jsonl`, provider switch policy, and operator UI evidence in `docs/change-evidence/2026-05-10-claude-provider-session-continuity.md`.
- Existing backlog already completed `GAP-115..119` for Codex plus Claude Code dual first-class governance-result posture and `GAP-135` for governed knowledge-memory lifecycle.
- The remaining gap is a dedicated cross-host continuity queue for Codex App, Codex CLI, Claude Code, Claude Desktop, multi-account/provider labels, classified memory/handoff records, and operator/MCP exposure.

## Changes
- Added `docs/plans/agent-continuity-and-shared-context-plan.md` for `GAP-159..164`.
- Added `docs/specs/agent-continuity-record-spec.md`.
- Added `schemas/jsonschema/agent-continuity-record.schema.json`.
- Updated `schemas/catalog/schema-catalog.yaml` and `schemas/README.md`.
- Added `GAP-159..164` to `docs/backlog/issue-ready-backlog.md` and `docs/backlog/issue-seeds.yaml`.
- Updated `docs/plans/README.md` to list the new plan.

## Compatibility
- This planning slice does not alter `~/.codex`, `~/.claude`, Claude Desktop state, app SQLite, provider profiles, API keys, auth snapshots, or MCP credentials.
- The new schema stores portable metadata, refs, sensitivity labels, and rollback refs. It does not authorize copying raw transcripts or secrets.
- The queue preserves Codex and Claude Code as host-owned tools and treats Claude Desktop native history sharing limits as explicit boundary facts.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `OK python-bytecode`
  - `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `Completed 106 test files in 133.624s; failures=0`
  - `OK runtime-unittest`
  - `OK runtime-service-parity`
  - `OK runtime-service-wrapper-drift-guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `OK schema-json-parse`
  - `OK schema-example-validation`
  - `OK schema-catalog-pairing`
  - `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - `OK active-markdown-links`
  - `OK backlog-yaml-ids`
  - `OK post-closeout-queue-sync`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - `OK adapter-posture-visible`
  - `WARN codex-capability-degraded`
- `python -m unittest tests.runtime.test_issue_seeding -v`
  - `Ran 9 tests`
  - `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - `rendered_tasks=142`
  - `rendered_issue_creation_tasks=0`
  - `rendered_epics=14`
  - `completed_task_count=142`
- Initial `Runtime` run failed on `test_issue_seeding` because `scripts/github/create-roadmap-issues.ps1` intentionally had no task label mapping for new `GAP-159`. The fix added a precise `GAP-159..164` mapping and preserved the fail-closed default for unknown future GAP ids.

## Rollback
- Revert:
  - `docs/plans/agent-continuity-and-shared-context-plan.md`
  - `docs/specs/agent-continuity-record-spec.md`
  - `schemas/jsonschema/agent-continuity-record.schema.json`
  - `schemas/catalog/schema-catalog.yaml`
  - `schemas/README.md`
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/backlog/issue-seeds.yaml`
  - `docs/plans/README.md`
  - this evidence file
