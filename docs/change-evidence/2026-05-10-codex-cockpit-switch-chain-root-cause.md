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

## Verification

```text
python -m unittest tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_repairs_cc_switch_shared_history_blockers tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_treats_cockpit_oauth_as_codex_chatgpt_auth
Ran 2 tests in 0.717s, OK

python -m unittest tests.runtime.test_codex_cockpit_switch_trace
Ran 2 tests in 0.398s, OK

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1
OK python-bytecode
OK python-import

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime
Completed 110 test files in 119.960s; failures=0
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
```

No `Codex`, `codex`, `Claude Code`, `Claude Desktop`, or `claude` process was stopped, killed, restarted, or launched by this repair.

## Rollback

- Restore restart-guard backup with:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File D:\CODE\governed-ai-coding-runtime\scripts\Restore-CodexAppRestartState.ps1 -BackupDir "C:\Users\sciman\.codex\backups\codex-app-restart-guard\20260510-230651"`
- Or restore individual backups created by `codex-interop-check.py`:
  - `C:\Users\sciman\.antigravity_cockpit\backups\config.json.20260510_230701_cockpit_restart_wrapper.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260510_230701_cockpit_follow_current_account.bak`
  - `C:\Users\sciman\.codex\backups\config.toml.20260510_230701_cockpit_provider.bak`
  - `C:\Users\sciman\.codex\backups\auth.json.20260510_230701_cockpit_auth.bak`
