# 2026-05-10 Codex Cockpit Switch Chain Root Cause

- rule_id: `local-codex-cockpit-auth-interop`
- risk: medium, because live Codex/Cockpit auth and launch configuration were repaired
- landing: `scripts/codex-interop-check.py`, `tests/runtime/test_codex_shared_launcher.py`, `README.md`, `README.zh-CN.md`, `docs/quickstart/ai-coding-usage-guide.zh-CN.md`, `C:\Users\sciman\.codex`, `C:\Users\sciman\.antigravity_cockpit`
- destination: make Cockpit API/OAuth switching stop bypassing the shared-history repair chain

## Root Cause

- Cockpit Tools switched the Codex account and then raw-launched Codex App through its own launch-on-switch path.
- That raw launch happened before `Start-CodexShared.ps1` / `codex-interop-check.py` could normalize `auth.json`, `config.toml`, `state_5.sqlite`, and Cockpit `codex_instances.json`.
- Live evidence before repair showed `forced_login_method = "api"` while the current Cockpit account was OAuth and expected Codex `chatgpt`.
- Live `codex_instances.json` also had `followLocalAccount = false` with a fixed `bindAccountId`, so Cockpit could relaunch stale account state after a switch.
- `codex-cockpit-resume` was calling an older installed `~/.codex/scripts/codex-interop-check.py`, so its OAuth auth detection lagged behind the repository fix.

## Actor Map

Observed Cockpit Tools switch chain from `C:\Users\sciman\.antigravity_cockpit\logs\app.log.2026-05-10`:

1. Cockpit selects a Codex account and writes `C:\Users\sciman\.codex\auth.json`.
2. Cockpit syncs `codex_instances.json` default instance binding to the selected account.
3. When launch-on-switch is enabled, Cockpit starts the Store Codex App entrypoint directly.
4. On OAuth switch, Cockpit can close the prior app PID and launch a new one if its restart path is active.

Codex App behavior:

- Reads `~/.codex/config.toml`, `~/.codex/auth.json`, and `state_5.sqlite` from the active process environment/startup state.
- Does not run this repository's `Start-CodexShared.ps1` normalization path.
- History visibility depends on both UI filters and `state_5.sqlite.threads.model_provider`; splitting API/OAuth into different provider buckets hides history.

Codex CLI behavior:

- `codex resume` follows `CODEX_HOME`, profile/config overrides, and CLI arguments.
- `codex-cockpit-resume` deliberately calls `Start-CodexShared.ps1 -UseCockpitCurrentAccount --all --include-non-interactive`, so it normalizes Cockpit state before invoking CLI resume.

Repository scripts behavior:

- `Start-CodexShared.ps1` reads the Cockpit current account, validates API relay reachability where applicable, calls `codex-interop-check.py --apply --migrate-provider-bucket --quick-launch`, then starts the requested Codex surface.
- `codex-interop-check.py` repairs the shared-history projection: built-in `model_provider = "openai"`, no reserved `[model_providers.openai]` override, matching `auth.json`, provider-bucket migration, and Cockpit launch/binding flags.
- The conflict was not a single bad file; it was a race between Cockpit's raw write/launch path and this repository's repair/projection path.

## Changes

- Added `cockpit_codex_raw_launch_on_switch_disabled` to fail closed when Cockpit `codex_launch_on_switch` is enabled.
- Changed repair to set:
  - `codex_launch_on_switch = false`
  - `codex_restart_specified_app_on_switch = false`
  - `codex_specified_app_path = ""`
  - `defaultSettings.followLocalAccount = true`
  - `defaultSettings.bindAccountId = null`
- Synced updated `scripts/codex-interop-check.py` and `scripts/Start-CodexShared.ps1` to `C:\Users\sciman\.codex\scripts`.
- Kept shared history on built-in `model_provider = "openai"`; API relays only vary top-level `openai_base_url`.
- Added `scripts/codex-cockpit-switch-trace.py` to capture before/after Cockpit switch side effects without restarting Codex App or exposing secrets.
- Added `scripts/Save-CodexCockpitSwitchRecord.ps1` and `scripts/Compare-CodexCockpitSwitchRecords.ps1` as operator-friendly fixed commands for restart/switch incident capture.
- Added regression coverage in `tests/runtime/test_codex_cockpit_switch_trace.py`.
- Documented the trace command in `README.md`, `README.zh-CN.md`, and `docs/quickstart/ai-coding-usage-guide.zh-CN.md`.

## Live Repair Evidence

Restart-guard backup:

```text
C:\Users\sciman\.codex\backups\codex-app-restart-guard\20260510-230651
```

Live apply:

```powershell
python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --apply --migrate-provider-bucket --quick-launch
```

Key result:

```text
status=pass
changed=cockpit_codex_switch_raw_launch_disabled,cockpit_codex_instances_follow_current_account_repaired,codex_live_config_cockpit_provider,codex_auth_cockpit_projected,codex_provider_bucket_triggers_ensured
threads.model_provider=openai:1637
```

Installed launcher check:

```powershell
codex-cockpit-resume --help
```

Key result:

```text
interop_repair_status=pass
profile=shared-cockpit-auth
forced_login_method=chatgpt
model_provider=openai
```

Explicit API account resume path:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File C:\Users\sciman\.codex\scripts\Start-CodexShared.ps1 -Surface resume -UseCockpitCurrentAccount -CockpitAccountId codex_apikey_8b8853f15e823dc53bd156163035bc78 --all --include-non-interactive --help
```

Key result:

```text
interop_repair_status=pass
profile=shared-cockpit-api
forced_login_method=api
provider_base_url=http://35.213.82.91:8003/v1
model_provider=openai
```

OAuth restored after the API probe:

```text
codex-interop-check --quick-launch -> status=pass
forced_login_method=chatgpt
auth_mode=chatgpt
has_tokens=true
has_openai_api_key=false
```

History visibility:

```powershell
python scripts\codex-history-view-diagnose.py --codex-home C:\Users\sciman\.codex --target-cwd D:\CODE\governed-ai-coding-runtime --target-cwd D:\CODE\k12-question-graph --target-cwd D:\CODE\skills-manager --target-cwd D:\CODE\ClassroomToolkit --target-cwd D:\CODE\github-toolkit --target-cwd D:\CODE\vps-ssh-launcher
```

Key result:

```text
status=pass
row_count=343
all six target repos visible in default page
```

API relay probe:

```text
GET http://35.213.82.91:8003/v1/models -> 200
WS  ws://35.213.82.91:8003/v1/responses -> 404 instead of 101
```

The remaining `35.213.82.91` App `Reconnecting` risk is the relay WebSocket capability. The local fix deliberately keeps history on `model_provider = "openai"` and does not reintroduce a custom no-WebSocket provider bucket because that would hide OAuth/API histories from each other.

Current no-switch trace baseline:

```powershell
python scripts\codex-cockpit-switch-trace.py --out docs\change-evidence\2026-05-10-codex-cockpit-switch-trace-current.json
```

Key result:

```text
changed_files=[]
cockpit_current_account_id=codex_00820d20868b374ba060cbdd05340e12
codex_launch_on_switch=false
codex_restart_specified_app_on_switch=false
codex_specified_app_path=""
default_instance.followLocalAccount=true
default_instance.bindAccountId=null
forced_login_method=chatgpt
auth_mode=chatgpt
threads.model_provider=openai:1638
```

When the recurrence needs to be captured live, run:

```powershell
python scripts\codex-cockpit-switch-trace.py --watch-seconds 45 --out docs\change-evidence\codex-cockpit-switch-trace-local.json
```

Then switch the account in Cockpit Tools during the 45-second window. The report identifies whether the overwrite came from Cockpit state files, Codex auth/config, history metadata, or only the relay/network layer.

For repeated manual checkpoints around a restart or API/OAuth switch incident:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Save-CodexCockpitSwitchRecord.ps1 -Label before-restart
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Save-CodexCockpitSwitchRecord.ps1 -Label api-reconnecting
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Save-CodexCockpitSwitchRecord.ps1 -Label oauth-restored
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Compare-CodexCockpitSwitchRecords.ps1
```

Records are stored under:

```text
docs/change-evidence/codex-cockpit-snapshots/<yyyyMMdd-HHmmss-label>/record.json
```

Current command smoke evidence:

```text
Save-CodexCockpitSwitchRecord.ps1 -Label current-baseline-parser-fixed
record_path=docs/change-evidence/codex-cockpit-snapshots/20260510-234437-current-baseline-parser-fixed/record.json
forced_login_method=chatgpt
auth_mode=chatgpt
model_provider=openai
openai_base_url=null
codex_launch_on_switch=false
bindAccountId=null

Save-CodexCockpitSwitchRecord.ps1 -Label current-baseline-repeat
record_path=docs/change-evidence/codex-cockpit-snapshots/20260510-234522-current-baseline-repeat/record.json

Compare-CodexCockpitSwitchRecords.ps1
current-baseline-parser-fixed -> current-baseline-repeat: no semantic or tracked-file changes
```

2026-05-11 recurrence captured after restart and switching to `35.213.82.91`:

```text
before-restart-final -> api-35-reconnecting
cockpit.current_account_id: codex_00820d20868b374ba060cbdd05340e12 -> codex_apikey_8b8853f15e823dc53bd156163035bc78
cockpit.default.bindAccountId: null -> codex_apikey_8b8853f15e823dc53bd156163035bc78
cockpit.default.followLocalAccount: true -> false
cockpit.default.lastPid: 26856 -> 44968
codex.config.model_provider: openai -> cmp_1778165666417_1
codex.auth.auth_mode: chatgpt -> apikey
codex.auth.has_openai_api_key: false -> true
codex.auth.has_tokens: true -> false
```

```text
api-35-reconnecting -> oauth-restored
cockpit.current_account_id: codex_apikey_8b8853f15e823dc53bd156163035bc78 -> codex_00820d20868b374ba060cbdd05340e12
cockpit.default.bindAccountId: codex_apikey_8b8853f15e823dc53bd156163035bc78 -> codex_00820d20868b374ba060cbdd05340e12
cockpit.default.lastPid: 44968 -> 5364
codex.config.model_provider: cmp_1778165666417_1 -> <missing>
codex.auth.auth_mode: apikey -> <missing>
codex.auth.has_openai_api_key: true -> false
codex.auth.has_tokens: false -> true
history_threads_by_provider: openai:1638 -> openai:1639
```

Cockpit logs also proved that the switch flow still raw-started Codex App even while `codex_launch_on_switch=false`:

```text
2026-05-11T00:03:57 [Codex切号] 开始切换账号: codex_apikey_8b8853f15e823dc53bd156163035bc78
2026-05-11T00:04:01 [Codex Start] 启动策略=system-store-entry ... pid=44968
```

The checker now includes `cockpit_codex_recent_start_after_switch_absent` so it no longer trusts config flags alone. A subsequent file-level repair restored:

```text
record_path=docs/change-evidence/codex-cockpit-snapshots/20260511-001618-after-interop-repair/record.json
cockpit_bind_account_id=null
cockpit_follow_local_account=true
codex_forced_login_method=chatgpt
codex_model_provider=openai
codex_auth_mode=chatgpt
```

Persistent switch guard added on 2026-05-11:

```text
repo scripts:
  scripts/codex-cockpit-switch-guard.py
  scripts/Start-CodexCockpitSwitchGuard.ps1

live synced scripts:
  C:\Users\sciman\.codex\scripts\codex-cockpit-switch-guard.py
  C:\Users\sciman\.codex\scripts\Start-CodexCockpitSwitchGuard.ps1
  C:\Users\sciman\.codex\scripts\codex-interop-check.py

scheduled task:
  name=codex-cockpit-switch-guard
  state=Running
  process_id=44388
  log=C:\Users\sciman\.codex\log\codex-cockpit-switch-guard.jsonl
```

The guard watches the Cockpit/Codex state files that were proven to drift during API/OAuth switching. When Cockpit rewrites those files, it debounces the change and runs the same deterministic repair:

```text
python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --apply --migrate-provider-bucket --quick-launch
```

Live guard log evidence:

```text
guard_started timestamp=2026-05-11T00:28:24
change_repaired timestamp=2026-05-11T00:29:01 stdout_status=pass
change_repaired timestamp=2026-05-11T00:30:01 stdout_status=pass
change_repaired timestamp=2026-05-11T00:32:11 stdout_status=pass
```

2026-05-11 follow-up hardening:

```text
Save-CodexCockpitSwitchRecord.ps1 -Label before-relay-generalization-check
record_path=docs/change-evidence/codex-cockpit-snapshots/20260511-003517-before-relay-generalization-check/record.json

run.ps1/operator.ps1/8770 UI now expose:
  codex_interop_check
  codex_interop_repair
  codex_switch_record
  codex_guard_status
  codex_guard_start

8770 live verification:
  url=http://127.0.0.1:8770/?lang=zh-CN
  Codex panel buttons present:
    检查共享历史互操作
    保存切换记录
    修复 Cockpit/Codex 互操作
    查看切换守护
    启动切换守护
  clicked 查看切换守护:
    exit_code=0
    task_state=4
    process_count=1

operator command evidence:
  CodexSwitchRecord saved docs/change-evidence/codex-cockpit-snapshots/20260511-004056-operator-ui-20260511-004056/record.json
  CodexInteropRepair exited 0 with status=pass
  CodexSwitchGuardStatus exited 0 with task_state=4 process_count=1
  codex-switch-guard-status.cmd exited 0 with task_state=4 process_count=1
  codex-switch-record.cmd -Label cmd-shortcut-smoke-repo saved docs/change-evidence/codex-cockpit-snapshots/20260511-004833-cmd-shortcut-smoke-repo/record.json

final pre-restart baseline:
  record_path=docs/change-evidence/codex-cockpit-snapshots/20260511-004613-before-restart-after-8770-integration/record.json
  auth_mode=chatgpt
  model_provider=openai
  cockpit launch_on_switch=False
  cockpit bindAccountId=null
```

2026-05-11 recurrence evidence and guard keepalive fix:

```text
comparison:
  before=docs/change-evidence/codex-cockpit-snapshots/20260511-004613-before-restart-after-8770-integration/record.json
  after=docs/change-evidence/codex-cockpit-snapshots/20260511-005733-after-restart-before-switch/record.json
  cockpit.current_account_id: codex_00820d20868b374ba060cbdd05340e12 -> codex_apikey_8b8853f15e823dc53bd156163035bc78
  codex.config.forced_login_method: chatgpt -> api
  codex.auth.auth_mode: chatgpt -> apikey
  codex.auth.base_url: null -> http://35.213.82.91:8003/v1

comparison:
  before=docs/change-evidence/codex-cockpit-snapshots/20260511-005733-after-restart-before-switch/record.json
  after=docs/change-evidence/codex-cockpit-snapshots/20260511-005845-after-switch-api-name/record.json
  field_changes=[]
  file_changes=[]

comparison:
  before=docs/change-evidence/codex-cockpit-snapshots/20260511-005845-after-switch-api-name/record.json
  after=docs/change-evidence/codex-cockpit-snapshots/20260511-010011-after-repair-api-name/record.json
  field_changes=[]
  file_changes=[]

root-cause refinement:
  The recurrence was not caused by a new semantic drift between the saved switch
  and repair snapshots. The missing control was guard liveness: after restart the
  scheduled task was Ready with process_count=0, so later Cockpit rewrites were
  not repaired. Cockpit logs still showed raw Codex App start within 4 seconds
  of API switching even with codex_launch_on_switch=false.

fix:
  scripts/Start-CodexCockpitSwitchGuard.ps1 now installs a keepalive task with
  StartWhenAvailable, indefinite ExecutionTimeLimit, RestartCount/RestartInterval
  where supported, startup-trigger attempt with logon-only fallback, and a
  fallback hidden worker when Start-ScheduledTask does not produce a Python guard.

live status after fix:
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexCockpitSwitchGuard.ps1 -Status
  task_state=4
  healthy=true
  process_count=1
  process_ids=[44112]

new snapshot with guard health:
  record_path=docs/change-evidence/codex-cockpit-snapshots/20260511-011130-after-guard-status-in-snapshot/record.json
  guard.healthy=true
  guard.process_count=1
  guard.task_state=Running
  auth_mode=chatgpt
  model_provider=openai
  cockpit bindAccountId=null
```

## Verification

```text
python -m unittest tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_repairs_cc_switch_shared_history_blockers tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_treats_cockpit_oauth_as_codex_chatgpt_auth
Ran 2 tests in 0.717s, OK

python -m unittest tests.runtime.test_codex_cockpit_switch_trace
Ran 2 tests in 0.398s, OK

python -m unittest tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_detects_recent_cockpit_raw_start_after_switch tests.runtime.test_codex_cockpit_switch_trace
Ran 3 tests in 0.506s, OK

python -m unittest tests.runtime.test_codex_cockpit_switch_guard tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_detects_recent_cockpit_raw_start_after_switch tests.runtime.test_codex_cockpit_switch_trace
Ran 5 tests in 0.897s, OK

python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_codex_interop_repair_and_switch_helpers_are_available_as_dry_run tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_server_helpers_are_bounded_to_repo_actions_and_files tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_accepts_common_cockpit_api_base_url_field_names tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_repairs_cc_switch_shared_history_blockers
Ran 11 selected tests, OK

python -m unittest tests.runtime.test_codex_local tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_codex_interop_repair_and_switch_helpers_are_available_as_dry_run tests.runtime.test_operator_ui tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_accepts_common_cockpit_api_base_url_field_names
Ran 38 tests in 6.134s, OK

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1
OK python-bytecode
OK python-import

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime
Completed 111 test files in 117.352s; failures=0
OK runtime-unittest
OK runtime-service-parity
OK runtime-service-wrapper-drift-guard

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract
OK schema-json-parse
OK dependency-baseline
OK agent-rule-sync
OK pre-change-review
OK functional-effectiveness

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1
OK hard checks; residual WARN codex-capability-degraded is the existing native attach/status-handshake warning.

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexCockpitSwitchGuard.ps1 -Status
task_name=codex-cockpit-switch-guard
task_state=4
process_count=1
process_ids=[44388]

python -m unittest tests.runtime.test_codex_cockpit_switch_trace tests.runtime.test_codex_cockpit_switch_guard
Ran 5 tests in 2.632s, OK

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexCockpitSwitchGuard.ps1 -InstallTask
Installed scheduled task: codex-cockpit-switch-guard (logon_only_fallback)

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexCockpitSwitchGuard.ps1 -Start
Started scheduled task: codex-cockpit-switch-guard

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexCockpitSwitchGuard.ps1 -Status
task_state=4
healthy=true
process_count=1
process_ids=[44112]
```

No `Codex`, `codex`, `Claude Code`, `Claude Desktop`, or `claude` process was stopped, killed, restarted, or launched by this repair. The only long-running process added is the dedicated hidden switch guard worker.

## Rollback

- Stop or remove the persistent switch guard:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File D:\CODE\governed-ai-coding-runtime\scripts\Start-CodexCockpitSwitchGuard.ps1 -Stop`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File D:\CODE\governed-ai-coding-runtime\scripts\Start-CodexCockpitSwitchGuard.ps1 -UninstallTask`
- Restore restart-guard backup with:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File D:\CODE\governed-ai-coding-runtime\scripts\Restore-CodexAppRestartState.ps1 -BackupDir "C:\Users\sciman\.codex\backups\codex-app-restart-guard\20260510-230651"`
- Or restore individual backups created by `codex-interop-check.py`:
  - `C:\Users\sciman\.antigravity_cockpit\backups\config.json.20260510_230701_cockpit_restart_wrapper.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260510_230701_cockpit_follow_current_account.bak`
  - `C:\Users\sciman\.codex\backups\config.toml.20260510_230701_cockpit_provider.bak`
  - `C:\Users\sciman\.codex\backups\auth.json.20260510_230701_cockpit_auth.bak`
