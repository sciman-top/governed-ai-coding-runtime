# Operator UI Polish

## Goal
- Improve the local operator UI so it feels like a refined runtime control console instead of a plain report surface.
- Preserve the existing server-rendered UI model, action allowlist, API routes, status loading, history, target selection, evidence preview, and provider/account switching behavior.
- Keep performance stable by avoiding external assets, web fonts, frontend frameworks, heavy JavaScript, polling changes, or image-based chrome.

## Risk
- Level: low.
- Reason: the change is limited to the operator HTML renderer's visual system and short operator-facing labels, plus matching renderer tests. It does not change runtime commands, persistence, target governance behavior, auth/profile switching semantics, or localhost API routing.

## Changes
- Updated `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`.
- Rebalanced the UI from a one-note teal report style into a neutral operations console with a darker header, refined card elevation, gold/accent detail lines, clearer section hierarchy, and denser but more readable control copy.
- Kept the implementation as inline CSS and existing JavaScript only.
- Updated `tests/runtime/test_operator_ui.py` for the revised bilingual title.
- Updated `scripts/operator-ui-service.ps1` so `Start` no longer blindly reuses an already running localhost UI process when UI source files have changed after the process started.
- Updated `scripts/serve-operator-ui.py` so live HTML/API responses disable browser caching, expose `/api/ui-process`, and refuse to render the normal UI when the running process is older than UI source files.
- Updated `tests/runtime/test_operator_entrypoint.py` to assert the service status exposes stale-source metadata and that the service script contains stale-process detection.

## Visual Evidence
- Runtime view: `docs/change-evidence/operator-ui-after-runtime-polish.png`
- Codex view: `docs/change-evidence/operator-ui-after-codex-polish.png`
- Claude view: `docs/change-evidence/operator-ui-after-claude-polish.png`
- Feedback view: `docs/change-evidence/operator-ui-after-feedback-polish.png`
- Mobile 390px: `docs/change-evidence/operator-ui-after-mobile-polish.png`
- Live 8770 after stale-service fix: `docs/change-evidence/operator-ui-live-8770-after-stale-fix.png`

## Stale Service Fix
- Symptom: `http://127.0.0.1:8770/?lang=zh-CN` could remain visually stale even after code changed because the long-running `serve-operator-ui.py` process kept old Python module code in memory.
- Root cause: `scripts/operator-ui-service.ps1 -Action Start` returned early whenever `/api/status` was ready; it did not compare the service process start time with UI source file modification times.
- Fix: `Status` now reports `stale`, `process_start_utc`, and `source_last_write_utc`; `Start` automatically stops and restarts the service when source files are newer than the running process.
- HTTP freshness guard: live responses now send `Cache-Control: no-store, max-age=0`, `Pragma: no-cache`, `Expires: 0`, and `x-governed-runtime-ui-stale`; `/api/ui-process` reports process/source timestamps. If the source files become newer than the running process, `/` and `/index.html` return a stale-service diagnostic page instead of silently rendering old UI.
- Live evidence before restart: `stale=true`, `pid=17176`, `process_start_utc=2026-05-01T00:46:28.5490301Z`, `source_last_write_utc=2026-05-01T08:29:24.3630054Z`.
- Live evidence after restart: `stale=false`, `pid=29424`, `process_start_utc=2026-05-01T08:30:09.6141160Z`, `source_last_write_utc=2026-05-01T08:29:24.3630054Z`.
- Live evidence after HTTP freshness guard: service `stale=false`, `pid=13548`, `process_start_utc=2026-05-01T08:54:32.5332341Z`, `source_last_write_utc=2026-05-01T08:49:32.2420605Z`.
- `/api/ui-process` evidence after HTTP freshness guard: `status=ok`, `stale=false`, `Cache-Control=no-store, max-age=0`, `x-governed-runtime-ui-stale=false`.
- HTML evidence after HTTP freshness guard and final restart: `StatusCode=200`, `x-governed-runtime-ui-stale=false`, `Cache-Control=no-store, max-age=0`, title content includes `Governed Runtime 控制台`, stale diagnostic content absent.
- Browser evidence after restart: page title and H1 both rendered `Governed Runtime 控制台` at `http://127.0.0.1:8770/?lang=zh-CN`.

## Verification
- Browser inspection at `http://127.0.0.1:8790/?lang=zh-CN`.
- Checked Runtime, Codex, Claude, Feedback, and 390px mobile layouts.
- Browser metric check: `clientWidth=390`, `scrollWidth=390`, `overflow=false`, `cssBytes=16363`.
- `python -m unittest tests.runtime.test_operator_ui tests.service.test_operator_api`
  - Result: pass, 7 tests.
- `python -m unittest tests.runtime.test_operator_ui tests.service.test_operator_api tests.runtime.test_repo_map_context_artifact`
  - Result: pass, 9 tests.
- `python -m unittest tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_service_status_succeeds tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_service_detects_stale_source_processes`
  - Result: pass, 2 tests.
- `python -m unittest tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_server_helpers_are_bounded_to_repo_actions_and_files tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_server_refuses_stale_content_and_disables_cache tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_service_status_succeeds tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_service_detects_stale_source_processes`
  - Result: pass, 4 tests.
- `python -m unittest tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui tests.service.test_operator_api`
  - Result: pass, 19 tests.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - Result: pass, `OK python-bytecode`, `OK python-import`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - First run: timed out after 304 seconds before returning a result.
  - Second run: failed in `tests.runtime.test_repo_map_context_artifact` because subprocess stdout was decoded with `gbk` while receiving UTF-8 bytes.
  - Fix: set the test subprocess decoding to `encoding="utf-8"`.
  - Final run: pass, 93 test files, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- After stale-service fix:
  - Result: pass, 93 test files, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - Result: pass, including dependency baseline, target governance consistency, repo-map context artifact, agent rule sync, and functional effectiveness.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - Result: pass with existing `WARN codex-capability-degraded`; doctor checks returned `OK` for runtime paths, gate commands, hooks, runtime status surface, and adapter posture.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Status`
  - Final result: `status=running`, `ready=true`, `stale=false`, `pid=13548`, `url=http://127.0.0.1:8770/?lang=zh-CN`.

## Compatibility
- No external network dependency was added.
- No image, web font, or JavaScript package dependency was added.
- Existing action ids, API endpoints, local storage keys, and file preview safety boundaries are unchanged.

## Rollback
- Revert `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py` and `tests/runtime/test_operator_ui.py`.
- Remove this evidence file and the `operator-ui-after-*-polish.png` screenshots if the visual direction is rejected.
