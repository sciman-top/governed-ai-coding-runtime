# 2026-04-30 Codex operator UI account + usage fix

- rule_id: `R6`,`R8`
- risk: `low`
- current_landing: `operator UI Codex tab showed account hash instead of email and usage as unknown`
- target_home: `operator UI Codex tab shows email-based account label and local quota windows sourced from Codex local auth/log data`
- verification_scope: `build -> test -> contract/invariant -> hotspot`, live `/api/codex/status`, browser rendering at `http://127.0.0.1:8770/?lang=zh-CN`

## Changes

1. `scripts/lib/codex_local.py`
   - decode non-sensitive claims from `~/.codex/auth*.json` `tokens.id_token`
   - expose `email`, `display_name`, `account_label`, `plan_type`, `active_account`
   - read recent `codex.rate_limits` events from `~/.codex/logs_2.sqlite`
   - normalize `used_percent <= 1` to `remaining_percent = 100` to match Codex App remaining display
   - add conservative online refresh path: run a minimal `codex exec --json "Reply only ok."`, then parse the newest session `token_count.rate_limits`; if that fails, fall back to the local sqlite snapshot
   - update global Codex recommended defaults to `model_context_window = 272000` and `model_auto_compact_token_limit = 220000`
2. `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
   - render account selector/list using `account_label`
   - render quota windows as localized text in zh-CN: `5 小时`, `1 周`, Chinese month/day
   - use document language helper instead of runtime `state` to avoid `ReferenceError`
   - add `强制在线刷新` button and show whether the current panel is using online refresh or local fallback
3. `scripts/operator-ui-service.ps1`
   - use `Stop-Process -Force` so restart reliably replaces the old local UI process
4. `scripts/Optimize-CodexLocal.ps1`
   - align the user-level `~/.codex/config.toml` optimizer with the current `gpt-5.4 medium` recommended context and compact thresholds

## Commands

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN
python -B -m unittest tests.runtime.test_codex_local tests.runtime.test_operator_ui
python -B -c "import json, urllib.request; data=json.load(urllib.request.urlopen('http://127.0.0.1:8770/api/codex/status')); print(json.dumps({'active_account': data.get('active_account'), 'usage': data.get('usage')}, ensure_ascii=False, indent=2))"
python -B -c "import json, urllib.request; req=urllib.request.Request('http://127.0.0.1:8770/api/codex/refresh', data=b'{}', headers={'content-type':'application/json'}, method='POST'); data=json.load(urllib.request.urlopen(req)); print(json.dumps({'usage': data.get('usage'), 'usage_refresh': data.get('usage_refresh')}, ensure_ascii=False, indent=2))"
```

## Key evidence

- `build`: `OK python-bytecode`, `OK python-import`
- `runtime`: `Completed 78 test files ... failures=0`
- `contract`: `OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK functional-effectiveness`
- `hotspot`: `OK python-asyncio`, `OK codex-capability-ready`
- live API:
  - `active_account.email = sciman.top@gmail.com`
  - `usage.source = codex_logs_2_sqlite`
  - `usage.windows = [("5h", 100), ("7d", 97)]`
  - `POST /api/codex/refresh` returns `usage_refresh.status = ok|fallback` and preserves a local snapshot fallback path
- browser verification on `?lang=zh-CN`:
  - account option rendered as `* sciman.top@gmail.com`
  - quota rendered as `5 小时 100% 23:22 · 1 周 97% 5月5日`
  - toolbar renders both `刷新 Codex 状态` and `强制在线刷新`

## Compatibility

- no token values are returned or rendered; only non-sensitive claims are surfaced
- existing payload fields remain available; new fields are additive
- online refresh uses the official local `codex exec` path rather than an undocumented HTTP endpoint; it may consume a very small amount of quota
- restart behavior remains scoped to the local operator UI process on port `8770`

## Rollback

```powershell
git checkout -- packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py
git checkout -- scripts/lib/codex_local.py
git checkout -- scripts/operator-ui-service.ps1
git checkout -- tests/runtime/test_codex_local.py
git checkout -- tests/runtime/test_operator_ui.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN
```
