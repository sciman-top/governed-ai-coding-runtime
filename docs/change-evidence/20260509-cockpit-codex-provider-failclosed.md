# Cockpit Codex Provider Fail-Closed Repair

## Goal

Prevent governed Codex interop helpers from rewriting Cockpit Tools API account/provider metadata to an OpenAI Official fallback when a Cockpit API account is missing provider fields.

## Risk

- Risk level: medium.
- Boundary: local Cockpit/Codex configuration only; no repository business code, auth login flow, or remote provider credentials are changed by the source patch.
- Secret handling: API keys are not recorded in this evidence file.

## Changes

- `scripts/Start-CodexShared.ps1` now refuses to launch from a Cockpit API account that has no `api_base_url` instead of falling back to `https://api.openai.com/v1`.
- `scripts/Start-CodexShared.ps1` now validates Cockpit API accounts against `GET /models` before launch, and fails closed on 401/invalid-token style responses instead of letting Codex App enter a generic reconnect loop.
- `scripts/codex-interop-check.py` now treats missing `api_base_url` on API accounts as non-projectable and no longer configures Cockpit Tools to run the governed restart wrapper on account switch.
- `tests/runtime/test_codex_shared_launcher.py` covers the fail-closed behavior and verifies the interop repair no longer writes Cockpit restart-wrapper settings.

## Live Repair

- Restored the rebuilt Cockpit API account `codex_apikey_ea3ce873947a6c4630b766ca2f9f3abc` provider fields from its `.bak` file:
  - `api_provider_id = cmp_1778165666417_1`
  - `api_provider_name = 35.213.82.91`
  - `api_base_url = http://35.213.82.91:8003/v1`
- Disabled Cockpit's managed Codex restart-wrapper setting:
  - `codex_restart_specified_app_on_switch = false`
  - `codex_specified_app_path = ""`
- Synced the patched scripts to `C:\Users\sciman\.codex\scripts` without restarting Codex App.
- Re-synced `Start-CodexShared.ps1` after adding API validation; live backup is under `C:\Users\sciman\.codex\script-backups\cockpit-api-validation-20260509-2110`.

## Follow-up Findings

- `C:\Users\sciman\.antigravity_cockpit\codex_accounts.json` currently points at an OAuth Codex account, not the rebuilt `35.213.82.91` API account.
- The rebuilt `35.213.82.91` API account still has its provider metadata, but its stored provider key returns HTTP 401 with `无效的令牌` from `http://35.213.82.91:8003/v1/models`.
- Latest Codex App desktop logs show slow startup RPCs: `thread/list` about 2167ms, `model/list` about 9690ms, `skills/list` about 12272ms.
- `C:\Users\sciman\.codex\state_5.sqlite` still contains one newly created `cmp_1778165666417_1` thread row, so provider-bucket split remains a risk when a custom provider bypasses the stable shared `openai` bucket.
- Follow-up repair found two saved keys under the `35.213.82.91` provider: the account-bound key returned 401, while the second provider key returned 200 from `/models`.
- Updated only `C:\Users\sciman\.antigravity_cockpit\codex_accounts\codex_apikey_ea3ce873947a6c4630b766ca2f9f3abc.json` to reference the verified provider key. The active Cockpit account remains `agi.phys@gmail.com`; no App restart was performed.
- Removed the stale 401 key from `C:\Users\sciman\.antigravity_cockpit\codex_model_providers.json`; the `35.213.82.91` provider now retains only the `/models = 200` key.

## Evidence

| Command | Key result |
| --- | --- |
| `python -m unittest tests.runtime.test_codex_shared_launcher` | `Ran 5 tests`, `OK` |
| `python scripts\codex-interop-check.py --codex-home "$env:USERPROFILE\.codex" --cc-switch-db "$env:USERPROFILE\.cc-switch\cc-switch.db" --cockpit-home "$env:USERPROFILE\.antigravity_cockpit"` | Cockpit restart wrapper disabled; API provider metadata remains under Cockpit ownership; only stale `lastPid` remains as `attention` |
| `GET http://35.213.82.91:8003/v1/models` with stored Cockpit provider key | HTTP 401, `无效的令牌`; no secret value logged |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexShared.ps1 -UseCockpitCurrentAccount -CockpitAccountId codex_apikey_ea3ce873947a6c4630b766ca2f9f3abc -Surface cli -Prompt 'noop'` | Fails before launch with `/models validation (status 401)`; no Codex App restart |
| `GET http://35.213.82.91:8003/v1/models` with the second saved provider key | HTTP 200; account key updated to that verified provider key; no secret value logged |
| Provider key inventory after deletion | one remaining `35.213.82.91` key; account key fingerprint matches it; `/models` returns HTTP 200 |

## Rollback

- Revert the source files listed above through git history.
- Live repair backups were written under:
  - `C:\Users\sciman\.antigravity_cockpit\backups\manual-repair-20260509-202128`
  - `C:\Users\sciman\.codex\script-backups\cockpit-failclosed-20260509-202311`
  - `C:\Users\sciman\.codex\script-backups\cockpit-api-validation-20260509-2110`
  - `C:\Users\sciman\.antigravity_cockpit\backups\switch-35api-valid-key-20260509-205822`
  - `C:\Users\sciman\.antigravity_cockpit\backups\remove-35api-401-key-20260509-210041`
- If needed, restore those backups manually while Cockpit Tools and Codex App are closed.
