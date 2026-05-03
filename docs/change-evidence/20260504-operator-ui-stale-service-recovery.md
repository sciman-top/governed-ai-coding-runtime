# 2026-05-04 operator UI stale-service recovery

- rule_id: R3/R6/R8
- risk_level: low
- current_landing: `scripts/serve-operator-ui.py` stale-service branch
- target_landing: operator UI localhost service returns a controlled stale page or a fresh UI response instead of dropping the HTTP connection
- rollback: revert `scripts/serve-operator-ui.py` and `tests/runtime/test_operator_entrypoint.py` to the previous git revision, then restart `scripts/operator-ui-service.ps1`

## Root Cause

- symptom: `http://127.0.0.1:8770/` failed with `The response ended prematurely. (ResponseEnded)` while port `8770` was still listening.
- root_cause: stale-service GET handling called `maybe_request_operator_ui_restart(language=language, host=host, port=port)` inside a handler created by `_build_handler(default_language=...)`; `host` and `port` were not in that closure, so stale detection raised before `_send_text()` could return the intended conflict page.
- recent_change_relation: visual UI edits updated a watched source file, which made the existing long-running service stale and exercised the broken stale branch.

## Change

- pass `host` and `port` into `_build_handler(...)` from `serve_operator_ui(...)`.
- add a regression test that forces the stale branch through a real `ThreadingHTTPServer` request and verifies the response is HTTP `409`, not a dropped connection.

## Commands And Evidence

- `Invoke-WebRequest http://127.0.0.1:8770/`
  - before: failed with `The response ended prematurely. (ResponseEnded)`.
- `python -m unittest tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_stale_handler_returns_conflict_without_dropping_connection tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_server_refuses_stale_content_and_disables_cache`
  - result: pass, `Ran 2 tests in 0.146s`.
- `python scripts\serve-operator-ui.py --output .runtime\artifacts\operator-ui\debug-index.html --lang zh-CN`
  - result: generated static HTML successfully.
- temporary service on port `8773`
  - result: `StatusCode=200`, `Title=Governed Runtime 控制台`, `Length=117170`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -HostAddress 127.0.0.1 -Port 8770`
  - result: restarted service.
- `Invoke-WebRequest http://127.0.0.1:8770/`
  - after: `StatusCode=200`, `Title=Governed Runtime 控制台`, `Cache-Control=no-store, max-age=0`, `x-governed-runtime-ui-stale=false`, `Length=112260`.
- `Invoke-RestMethod http://127.0.0.1:8770/api/ui-process`
  - after: `status=ok`, `stale=false`, `restart_request=null`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: pass, `OK python-bytecode`, `OK python-import`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: pass, `Completed 103 test files in 103.371s; failures=0`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass, including `OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK pre-change-review`, `OK functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass with existing warning `WARN codex-capability-degraded`; all other checks OK.
- Playwright browser verification on `http://127.0.0.1:8770/`
  - after: page title `Governed Runtime 控制台`, console errors `0`, accessibility snapshot contains the main console layout.
  - screenshot: `docs/change-evidence/operator-ui-recovered-8770.png`.

## Compatibility

- public CLI flags and URLs are unchanged.
- the fix only supplies existing server address values to the existing handler factory.
- no new dependency, asset, animation, or runtime service model was added.
