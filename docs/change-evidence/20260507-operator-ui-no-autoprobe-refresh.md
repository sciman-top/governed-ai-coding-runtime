# 2026-05-07 Operator UI No-Autoprobe Refresh Evidence

- rule_id: `R3/R6/R8`
- risk_level: `low`
- current_home: `http://127.0.0.1:8770/?lang=zh-CN page refresh path`
- target_home: `browser refresh renders the operator UI without automatically running process-backed Codex/Claude/feedback/next-work probes`
- rollback: `git revert` the changes to `operator_ui_script.py`, `operator_ui_text.py`, `serve-operator-ui.py`, and matching tests

## Root Cause

The 8770 page itself did not run `run.ps1` on a normal browser refresh, but the interactive script automatically requested Codex, Claude, feedback, and next-work status after load and on focus/visibility/interval resume.
Those status paths can start local CLI probes such as `codex.cmd`, `claude`, and host feedback inspection. Even with Windows `CREATE_NO_WINDOW` protections in the backend, page refresh remained too noisy because it still triggered process-backed local probes without an explicit operator action.

## Change

- Removed page-load `setTimeout` calls that automatically requested Codex, Claude, feedback, and next-work status.
- Removed focus, visibility, and interval based Codex auto-refresh.
- Removed panel-open auto-refresh for Codex, Claude, and feedback.
- Kept manual refresh buttons and explicit run actions available.
- Allowed cached Codex snapshots to hydrate even when stale, so reloads can show prior local data without triggering a fresh probe.
- Changed cold state labels to `等待手动刷新` / `Waiting for manual refresh`.

## Verification

```powershell
python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_next_work_panel_does_not_block_initial_html
```

Result: `Ran 8 tests ... OK`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -Port 8770
```

Result: `status=running`, `ready=true`, `stale=false`, `pid=33896`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

Result: `OK python-bytecode`, `OK python-import`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

Result: failed in existing selector/host-feedback posture checks unrelated to this UI refresh change:

- `test_evidence_recovery_posture`: selector currently returns `defer_ltp_and_refresh_evidence` where the live recovery posture test still requires `wait_for_host_capability_recovery`.
- `test_host_feedback_summary`: generated recommendations no longer include the expected `native_attach` recovery wording.

The focused operator UI tests above passed before and after removing panel-open auto-refresh; full gate remains blocked until the pre-existing selector/host-feedback drift is reconciled.

Playwright live check against `http://127.0.0.1:8770/?lang=zh-CN`:

- page title: `Governed Runtime 控制台`
- `#next-work-panel`: `未自动刷新`, `AI 推荐: 点击刷新后显示`, `状态: 等待手动刷新`
- network requests after navigation: only `GET http://127.0.0.1:8770/?lang=zh-CN => 200`; no automatic `/api/codex/status`, `/api/claude/status`, `/api/feedback/summary`, or `/api/next-work` calls
