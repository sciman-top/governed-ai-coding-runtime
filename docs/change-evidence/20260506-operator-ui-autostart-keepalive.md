# 2026-05-06 operator UI autostart keepalive recovery

- current_landing: `scripts/operator-ui-service.ps1` autostart registration left the scheduled task with the Windows default `Stop Task If Runs X Hours and X Mins: 72:00:00`, so the localhost UI could disappear after a few days even when autostart was enabled.
- target_landing: the `GovernedRuntimeOperatorUi-8770` scheduled task runs without a 72-hour execution cap and requests restart-on-failure so `http://127.0.0.1:8770/?lang=zh-CN` stays available without manual restarts.
- verification_scope: service script regression test, live task re-registration, and live HTTP probe on `127.0.0.1:8770`.
- rollback: revert `scripts/operator-ui-service.ps1` and `tests/runtime/test_operator_entrypoint.py`, then rerun `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action EnableAutoStart`.

## Changes

1. Added `New-OperatorUiTaskSettings()` in `scripts/operator-ui-service.ps1`.
   - forces `ExecutionTimeLimit = 0` so the scheduled task no longer auto-stops after 72 hours
   - requests `RestartCount = 999` and `RestartInterval = 1 minute` when the host supports those settings
   - falls back cleanly to the no-time-limit setting on hosts that reject restart metadata
2. Routed both the S4U autostart path and the interactive logon fallback through the same keepalive task settings.
3. Added a regression assertion in `tests/runtime/test_operator_entrypoint.py` so the keepalive settings stay present in the service launcher script.

## Verification

```powershell
python -m unittest tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_service_detects_stale_source_processes
```

Observed result:

- pass

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action EnableAutoStart
schtasks /Query /TN "GovernedRuntimeOperatorUi-8770" /V /FO LIST
```

Observed result:

- autostart task recreated successfully
- current host still registers the task as `logon_only_fallback` / `Interactive only`
- `Task To Run` points at `-Action RunForeground`
- `Stop Task If Runs X Hours and X Mins` no longer reports the previous `72:00:00` limit

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -HostAddress 127.0.0.1 -Port 8770
Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8770/?lang=zh-CN" -TimeoutSec 5
Invoke-RestMethod -Uri "http://127.0.0.1:8770/api/ui-process" -TimeoutSec 5
```

Observed result:

- HTTP 200 from the UI root
- `/api/ui-process` returned `status = ok`
