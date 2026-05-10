# Agent Continuity Read-Only Auditor

- date: 2026-05-10
- rules: R1, R2, R6, R8, E4, E6
- risk: low
- current_landing: `scripts/agent-continuity.py`
- target_home: `D:\CODE\governed-ai-coding-runtime`
- rollback: revert the auditor, tests, schema/spec extension, backlog status updates, and this evidence file with git; no user-local Codex, Claude, Claude Desktop, provider, or auth state was modified

## Scope
- Implemented `GAP-161` as a read-only continuity auditor.
- Added Codex shared-home posture records for config path, history persistence, SQLite state presence, session transcript refs, profile names, and shared launcher presence.
- Added Claude Code shared-home posture records for settings path, provider alias, project transcript count, `history.jsonl`, file-history presence, and `preserve_claude_home` provider switch policy.
- Added Claude Desktop boundary output as `referenced_only` with structured `platform_na` because native Desktop chat history is not a supported shared writable continuity store.

## Security Boundary
- The auditor reads posture metadata and path refs only.
- It does not write `~/.codex`, `~/.claude`, Claude Desktop state, provider profiles, API keys, auth snapshots, or MCP credentials.
- It does not output raw tokens, cookies, auth files, full transcripts, or API key values.
- `config_summary` is limited to non-secret counts, booleans, labels, and storage refs.

## Changes
- Added `packages/contracts/src/governed_ai_coding_runtime_contracts/agent_continuity.py`.
- Added `scripts/agent-continuity.py`.
- Added `tests/runtime/test_agent_continuity.py`.
- Exported the contract from `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`.
- Extended `schemas/jsonschema/agent-continuity-record.schema.json` and `docs/specs/agent-continuity-record-spec.md` with optional `config_summary`.
- Updated `docs/plans/agent-continuity-and-shared-context-plan.md` and `docs/backlog/issue-ready-backlog.md` to mark `GAP-159..161` complete.

## Live Read-Only Audit Evidence
- `python scripts/agent-continuity.py audit --json --repo-root D:\CODE\governed-ai-coding-runtime`
  - `status`: `ok`
  - `record_count`: `3`
  - records: `codex-shared-home`, `claude-shared-home`, `claude-desktop-boundary`
  - Codex summary: `history_persistence=save-all`, `state_sqlite_exists=True`, `sessions_jsonl_count=1614`, `shared_launchers_present=4`
  - Claude summary: `provider_alias=bigmodel-glm`, `projects_jsonl_count=237`, `history_exists=True`, `provider_switch_policy=preserve_claude_home`
  - Claude Desktop boundary: `continuity_class=referenced_only`, `platform_na.applies=True`

## Verification
- `python -m unittest tests.runtime.test_agent_continuity -v`
  - `Ran 6 tests in 1.839s`
  - `OK`
- `python -m unittest tests.runtime.test_issue_seeding -v`
  - `Ran 9 tests in 15.467s`
  - `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`
  - `Ran 53 tests in 22.257s`
  - `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `OK python-bytecode`
  - `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `Completed 107 test files in 144.601s; failures=0`
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
  - `OK schema-catalog-visible`
  - `OK adapter-posture-visible`
  - `WARN codex-capability-degraded`

## Self-Repair
- Initial full `Runtime` rerun failed in `tests.runtime.test_issue_seeding` because completed `GAP-159..161` backlog bullets had incorrect indentation and the issue renderer could not parse their acceptance criteria.
- The backlog indentation was corrected, then `scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll` passed with `rendered_tasks=142`, `rendered_issue_creation_tasks=3`, `rendered_epics=14`, and `completed_task_count=139`.
