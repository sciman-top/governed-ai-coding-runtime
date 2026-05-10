# Agent Continuity Operator Surface

- date: 2026-05-10
- rules: R1, R2, R6, R8, E4, E6
- risk: low
- current_landing: `apps/control-plane/routes/operator.py`
- target_home: `D:\CODE\governed-ai-coding-runtime`
- rollback: revert the operator route/facade/server/UI updates, tests, backlog/plan status updates, and this evidence file with git; no Codex, Claude, Claude Desktop, provider, or auth credential state was modified

## Scope
- Implemented `GAP-163` as a local operator-visible continuity surface.
- Added control-plane `/operator` actions:
  - `search_context`
  - `write_handoff`
- Added live operator server endpoints:
  - `GET /api/continuity/search`
  - `POST /api/continuity/write-handoff`
- Added a new operator UI tab: `连续性` / `Continuity`.
- Added UI refresh behavior that reads the runtime-owned continuity index and displays record posture without rendering credentials or full transcripts.

## Security Boundary
- The UI and API read from `.runtime/agent-continuity`, not vendor-owned history stores.
- `write_handoff` uses `LocalAgentContinuityIndex.write_record`, so secret-like payloads fail closed before persistence.
- Search results expose metadata such as `record_id`, `repo_id`, `tool_family`, `provider_alias`, `continuity_class`, `secret_blocked`, and refs, not credential values.

## Live Browser Evidence
- Existing `http://127.0.0.1:8770/?lang=zh-CN` process initially returned `Operator UI 服务已过期`.
- Restarted with:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -HostAddress 127.0.0.1 -Port 8770 -UiLanguage zh-CN`
  - result: `status=running`, `ready=True`, `stale=False`, `pid=38064`
- Seeded repo-local continuity index from the read-only audit:
  - `.runtime/agent-continuity`
  - records written: `3`
- Browser verification:
  - opened `http://127.0.0.1:8770/?lang=zh-CN`
  - page title: `Governed Runtime 控制台`
  - clicked tab: `连续性`
  - observed: `连续性状态: ok · 3`
  - records: `codex-shared-home`, `claude-shared-home`, `claude-desktop-boundary`
- Direct API verification:
  - opened `http://127.0.0.1:8770/api/continuity/search`
  - observed JSON: `status=ok`, `record_count=3`, `secret_blocked=false` for returned records

## Verification
- `python -m unittest tests.service.test_operator_api -v`
  - `Ran 1 test in 8.576s`
  - `OK`
- `python -m unittest tests.runtime.test_operator_ui -v`
  - `Ran 7 tests in 0.255s`
  - `OK`
- `python -m unittest tests.runtime.test_agent_continuity -v`
  - `Ran 9 tests in 3.866s`
  - `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`
  - `Ran 53 tests in 22.368s`
  - `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `OK python-bytecode`
  - `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `Completed 107 test files in 143.963s; failures=0`
  - `OK runtime-unittest`
  - `OK runtime-service-parity`
  - `OK runtime-service-wrapper-drift-guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `OK schema-json-parse`
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
  - `rendered_issue_creation_tasks=1`
  - `rendered_epics=14`
  - `completed_task_count=141`
