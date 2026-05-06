# 2026-05-06 Codex local account persistence and dedupe follow-up

- current_landing: `127.0.0.1:8770` and `scripts/codex-account.py status` still had three operator-facing gaps after the first save-active slice:
  - newly logged-in CLI accounts were not auto-persisted unless the operator clicked a save button
  - duplicate logical accounts could surface as two rows (`auth` and a saved snapshot for the same `account_id`)
  - auth-claim plans and cached usage snapshots could disagree, and neither source alone was reliable enough for operator-facing plan display
- target_home:
  - the local Codex status pipeline auto-persists a new CLI `auth.json` into `auth-profiles/` when no named snapshot matches yet
  - logical account display is deduplicated by `account_id` / `account_hash`
  - account plan display uses explicit local account facts first, then account-scoped usage snapshots, then auth token claims
  - plan display keeps `plan_source` and `plan_conflicts` so conflicting local evidence remains visible
- verification_scope: `py_compile + manual fixed-workspace runtime probes + live CLI status`

## Changes

1. Added `save_active_auth_snapshot()` to `scripts/lib/codex_local.py`:
   - validate a user-provided snapshot name
   - refuse reserved / invalid names
   - write new named snapshots into `auth-profiles/`
   - fail closed on collisions with a different existing snapshot
2. Added `ensure_active_auth_snapshot()` and wired it into status loaders:
   - `codex_status(..., ensure_saved_snapshot=True)` auto-saves the active CLI account when no named snapshot matches
   - `scripts/codex-account.py status` now opts into that ensure path
   - `scripts/serve-operator-ui.py` now opts into that ensure path when loading Codex status
3. Tightened logical-account rendering:
   - display grouping now prefers `account_id`, then `account_hash`, instead of raw file hash
   - duplicate rows such as `auth` plus `auth2` collapse into one logical account row in the status payload
4. Corrected plan source precedence:
   - `C:\Users\sciman\.codex\account-facts.json` can hold non-secret local account facts such as email/name/file to plan mapping
   - `_resolve_account_plan_types()` now resolves display plan as `account_facts -> usage_snapshot -> auth_token`
   - the status payload includes `plan_source`, `auth_plan_type`, and `plan_conflicts`
   - the operator UI shows the plan source and conflict evidence on the account card
   - `prolite` / `go` is labeled as `Go` in the UI copy
5. Exposed the original save-active flow through:
   - `python scripts/codex-account.py save-active <name>`
   - `POST /api/codex/save-active`
   - Codex panel button shown only when `snapshot_status == missing_named_snapshot`
6. Kept existing safety boundaries:
   - no silent background write on page load
   - no deletion semantics change
   - no overwrite of another snapshot name

## Verification

```powershell
python -m py_compile scripts\lib\codex_local.py scripts\serve-operator-ui.py scripts\codex-account.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_script.py tests\runtime\test_codex_local.py tests\runtime\test_operator_entrypoint.py tests\runtime\test_operator_ui.py
```

Observed result:

- pass

```powershell
python -B scripts\codex-account.py status
```

Observed result:

- duplicate logical row `auth` + `auth2` no longer appears in CLI status output
- live `auth1` now reports `plan_type = plus` from `local_operator_asserted` account facts while its auth token still reports `prolite`
- live `auth5` now reports `plan_type = prolite` from `local_operator_asserted` account facts, so the UI renders it as `Go`, while its auth token and usage snapshot still report `plus`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -HostAddress 127.0.0.1 -Port 8770
Invoke-RestMethod http://127.0.0.1:8770/api/codex/status
```

Observed result:

- `8770` is now live and remains reachable after restart in the elevated host session
- live API returns one logical row for the active `ai.sciman.top@gmail.com` account instead of duplicated `auth` + `auth2`
- live API returns `auth1.plan_type = plus`, `auth1.plan_source = local_operator_asserted`, and a conflict for `auth_token = prolite`
- live API returns `auth5.plan_type = prolite`, `auth5.plan_source = local_operator_asserted`, and conflicts for `usage_snapshot = plus` and `auth_token = plus`
- live API returns `official_app_account.status = ambiguous` together with an explicit `limitation` field instead of silently implying safe auto-import

```text
Playwright browser verification on http://127.0.0.1:8770/?lang=zh-CN
```

Observed result:

- Codex overview card now shows the official-App ambiguity warning directly in the page summary
- `auth1` card renders `类型 = Plus` with source `本机账号事实`
- `auth5` card renders `类型 = Go` with source `本机账号事实`
- active `auth` card renders:
  - `快照 = auth2 仍是旧快照，建议用当前登录状态回写`
  - `官方 App = 官方 App 当前账号仍有歧义`
  - the explicit limitation string from the API

```powershell
python - <<'PY'
import json, shutil
from pathlib import Path
from scripts.lib import codex_local

root = Path(r"D:\CODE\governed-ai-coding-runtime\.runtime\manual-codex-verify-2")
if root.exists():
    shutil.rmtree(root)
root.mkdir(parents=True)

def write_auth(path, account_id, email, plan_type, last_refresh):
    payload = {
        "auth_mode": "chatgpt",
        "last_refresh": last_refresh,
        "tokens": {"account_id": account_id, "email": email},
        "email": email,
        "plan_type": plan_type,
        "name": email,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")

home = root / "dup"
home.mkdir()
write_auth(home / "auth.json", "acct-1", "same@example.com", "plus", "2026-05-06T00:00:00Z")
write_auth(home / "auth2.json", "acct-1", "same@example.com", "plus", "2026-05-05T00:00:00Z")
print(codex_local.codex_status(home)["accounts"])

home2 = root / "autosave"
home2.mkdir()
write_auth(home2 / "auth.json", "acct-2", "new@example.com", "team", "2026-05-06T00:00:00Z")
print(codex_local.codex_status(home2, ensure_saved_snapshot=True)["auto_snapshot"])
PY
```

Observed result:

- fixed-workspace probe collapses same-account `auth` + `auth2` to one logical account row
- fixed-workspace probe auto-creates `auth-profiles/auto-*.json` and promotes the saved snapshot name into the active-account display

```powershell
python -m unittest tests.runtime.test_codex_local tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui
```

Observed result:

- `Ran 63 tests in 26.745s`
- `OK`

```powershell
python scripts\codex-account.py status
Invoke-RestMethod http://127.0.0.1:8770/api/codex/status
```

Observed result:

- `auth1` / `sciman.top@gmail.com`: `plan_type = plus`, `plan_source = local_operator_asserted`, conflict evidence includes `auth_token = prolite`
- `auth5` / `agi.phys@gmail.com`: `plan_type = prolite`, `plan_source = local_operator_asserted`, conflict evidence includes `usage_snapshot = plus` and `auth_token = plus`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1
```

Observed result:

- `OK python-bytecode`
- `OK python-import`
- Runtime gate completed `105 test files`; `failures=0`; `OK runtime-unittest`; `OK runtime-service-parity`; `OK runtime-service-wrapper-drift-guard`
- Contract gate passed through `OK functional-effectiveness`
- Doctor passed with existing `WARN codex-capability-degraded` / native attach capability hint only

## Compatibility

- Existing `switch`, `sync-active`, and `delete` semantics remain unchanged.
- New snapshots are stored under `auth-profiles/`, which is already part of the supported local scan surface.
- `account-facts.json` stores non-secret local facts only and is intentionally outside the repo; deleting it reverts display resolution to usage/auth evidence.
- CLI and operator status loads now auto-persist only when the active CLI account has no matching named snapshot.
- Official Codex App storage discovery is still best-effort and may remain `ambiguous`; this follow-up does not yet auto-import a brand-new App-only account that has not propagated into `auth.json`.
- Official App storage inspection in this session found:
  - `Preferences` only contains lightweight UI settings
  - `Local State` exposes Chromium `os_crypt.encrypted_key`
  - storage scans can find multiple known `account_id` values in LevelDB, but no stable full auth payload that is safe to convert into a new local snapshot automatically

## Rollback

- Revert the touched files from git history:
  - `scripts/lib/codex_local.py`
  - `scripts/codex-account.py`
  - `scripts/serve-operator-ui.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui_script.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui_text.py`
  - `tests/runtime/test_codex_local.py`
  - `tests/runtime/test_operator_entrypoint.py`
  - `tests/runtime/test_operator_ui.py`
- Delete `C:\Users\sciman\.codex\account-facts.json` to remove the local fact override and return to usage/auth-derived plan display.
