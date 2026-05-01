# 2026-05-01 - evolution trigger hardening

## Scope
- Harden `scripts/operator.ps1` so `select-next-work.py` becomes a real preflight for high-impact operator actions.
- Expose the same selector result through `scripts/serve-operator-ui.py` and inject a visible next-work panel into generated operator HTML.

## Changes
- Added operator preflight helpers in `scripts/operator.ps1`:
  - `Get-OperatorPreflightDecision`
  - `Show-OperatorPreflight`
  - `Assert-OperatorPreflight`
- Enforced preflight on:
  - `Readiness` as visible advisory
  - `DailyAll` as blocking gate for `repair_gate_first` / `refresh_evidence_first`
  - `ApplyAllFeatures` as blocking gate for `repair_gate_first` / `refresh_evidence_first` / `owner_directed_scope_required`
  - `EvolutionMaterialize` as blocking gate for `repair_gate_first` / `refresh_evidence_first` / `owner_directed_scope_required`
- Added localhost UI support in `scripts/serve-operator-ui.py`:
  - new actions: `evolution_review`, `experience_review`, `evolution_materialize`
  - new helper: `load_next_work_summary()`
  - new API: `/api/next-work`
  - injected visible selector summary panel into generated HTML
  - cached next-work payloads for short-lived UI refreshes
- Added interactive UI guard wiring in `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`:
  - refresh next-work summary on load and after actions
  - disable blocked high-impact action buttons when selector says they must not run
  - show the blocking reason inside the command output panel instead of silently ignoring clicks
- Added regression coverage in:
  - `tests/runtime/test_operator_entrypoint.py`

## Why
- Previous evolution trigger logic could produce correct recommendations but still be bypassed by the main operator entrypoint.
- The selector output also lacked a stable first-class UI surface, so an operator could miss the current `next_action` unless they opened artifacts manually.

## Commands
```powershell
python -m unittest tests.runtime.test_operator_entrypoint
python -m unittest tests.runtime.test_operator_ui
python scripts/select-next-work.py --as-of 2026-05-01
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness -DryRun
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -UiLanguage zh-CN
python scripts/serve-operator-ui.py --lang zh-CN
```

## Key evidence
- `test_operator_entrypoint` passed with new preflight-block and readiness-advisory coverage.
- `test_operator_ui` remained green, confirming the package renderer contract stayed compatible.
- `select-next-work.py --as-of 2026-05-01` returned:
  - `gate_state=pass`
  - `source_state=fresh`
  - `evidence_state=fresh`
  - `next_action=defer_ltp_and_refresh_evidence`
- `operator.ps1 -Action Readiness -DryRun` now prints:
  - `operator-preflight: action=Readiness next_action=defer_ltp_and_refresh_evidence`
  - `operator-preflight-state: gate=pass source=fresh evidence=fresh`
- Generated operator HTML now contains a visible next-work panel and selector JSON details.
- Generated operator HTML now includes:
  - `id='next-work-action'`
  - `data-next-work-refresh='1'`
  - front-end hooks for `fetch('/api/next-work')`, `syncNextWorkActionGuards()`, and `data-blocked-reason`
- `load_next_work_summary()` now returns `status=pass`, `ui_status=healthy`, `blocked_actions=[]`, and a `cached_at` timestamp for UI cache coordination.

## Compatibility
- Existing operator actions remain unchanged when preflight is healthy.
- Read-only actions and evidence-refresh actions are not newly blocked.
- High-impact actions now fail closed when selector state requires gate repair, evidence refresh, or owner-directed scope.

## Rollback
- Revert:
  - `scripts/operator.ps1`
  - `scripts/serve-operator-ui.py`
  - `tests/runtime/test_operator_entrypoint.py`
  - this evidence file
