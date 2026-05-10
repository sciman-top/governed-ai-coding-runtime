# Agent Continuity Portable Index

- date: 2026-05-10
- rules: R1, R2, R6, R8, E4, E6
- risk: low
- current_landing: `packages/contracts/src/governed_ai_coding_runtime_contracts/agent_continuity.py`
- target_home: `D:\CODE\governed-ai-coding-runtime`
- rollback: revert the continuity index code, CLI commands, tests, backlog/plan status updates, and this evidence file with git; no user-local Codex, Claude, Claude Desktop, provider, or auth state was modified

## Scope
- Implemented `GAP-162` as a runtime-owned portable continuity index.
- Added `LocalAgentContinuityIndex` for writing classified `agent-continuity-record` payloads under an index root.
- Added index search by repo id, tool family, account alias, provider alias, expiry, and secret-blocked posture.
- Added CLI commands:
  - `python scripts/agent-continuity.py write-record --index-root <path> --record-json <path> --json`
  - `python scripts/agent-continuity.py search --index-root <path> --repo-id <id> --json`

## Security Boundary
- The index stores governed JSON records and search metadata; it does not mutate native Codex, Claude, or Claude Desktop state.
- Write operations fail closed when `sensitivity.contains_secret_material=True`, `sensitivity.redaction_status=blocked`, or secret-like text is detected.
- Search excludes secret-blocked records by default.
- Retention metadata is preserved in records and index entries so later retirement can skip expired records while preserving audit history.

## Changes
- Extended `packages/contracts/src/governed_ai_coding_runtime_contracts/agent_continuity.py` with:
  - `LocalAgentContinuityIndex`
  - `ContinuityIndexWriteResult`
  - `validate_portable_continuity_record`
  - secret-like payload checks
- Extended `scripts/agent-continuity.py` with `write-record` and `search`.
- Extended package exports in `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`.
- Extended `tests/runtime/test_agent_continuity.py` for write/search, CLI round trip, schema coverage, package exports, and secret-like rejection.
- Updated `docs/plans/agent-continuity-and-shared-context-plan.md` and `docs/backlog/issue-ready-backlog.md` to mark `GAP-162` complete.

## Verification
- `python -m unittest tests.runtime.test_agent_continuity -v`
  - `Ran 9 tests in 3.374s`
  - `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`
  - `Ran 53 tests in 31.859s`
  - `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `OK python-bytecode`
  - `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `Completed 107 test files in 189.208s; failures=0`
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
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - `rendered_tasks=142`
  - `rendered_issue_creation_tasks=2`
  - `rendered_epics=14`
  - `completed_task_count=140`
