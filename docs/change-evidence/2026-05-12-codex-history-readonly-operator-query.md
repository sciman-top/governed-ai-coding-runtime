# 2026-05-12 Codex history read-only operator query

- rules: R1/R3/R4/R6/R8, E4/E6
- risk: low, local operator UI/API addition that reads Codex history metadata without mutating live Codex state
- landing: `scripts/serve-operator-ui.py`, `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui*.py`, `tests/runtime/test_operator_codex_history_api.py`, `tests/runtime/test_operator_ui.py`
- destination: provide a complete paged history lookup in the 8770 operator surface while keeping native Codex App/CLI history behavior unchanged

## Change

- Added `GET /api/codex/history` to the operator server.
- The endpoint opens `state_5.sqlite` with SQLite URI `mode=ro`.
- Query parameters:
  - `source`: comma-separated or repeated source filter, default `vscode,cli`.
  - `cwd`: optional path substring filter, tolerant of the Windows `\\?\` extended prefix.
  - `search`: optional title, first user message, cwd, or thread id substring filter.
  - `limit`: default `50`, capped at `200`.
  - `offset`: default `0`, capped at `100000`.
- Added a compact Codex panel section for source/project/search/page-size controls, result list, and previous/next pagination.
- The UI intentionally does not auto-load history on page open; the operator must click the query button.

## Safety Boundary

- No writes to `C:\Users\sciman\.codex\state_5.sqlite`.
- No rollout JSONL content scan.
- No provider bucket migration.
- No timestamp rewriting.
- No edits to `config.toml`, `auth.json`, Cockpit state, or Codex provider/auth state.
- No Codex App, Codex CLI, Claude, or Cockpit process restart/kill/launch.

## Live Evidence

- Direct read-only helper probe against current host:
  - `status=ok`
  - `read_only=true`
  - `state_path=C:\Users\sciman\.codex\state_5.sqlite`
  - `sources=["vscode","cli"]`
  - `limit=3`
  - `returned=3`
  - `total=1326` for non-archived `vscode,cli` rows at probe time
  - latest returned row included current `governed-ai-coding-runtime` thread under provider `cmp_1778165666417_1`
- Managed operator UI service restart loaded the new source on port 8770:
  - `url=http://127.0.0.1:8770/?lang=zh-CN`
  - `ready=true`
  - `stale=false`
  - `autostart.current=true`
- Browser verification opened the live 8770 page, switched to the Codex tab, clicked `查询历史`, and rendered:
  - heading `完整历史查询`
  - safety hint `只读查询 state_5.sqlite 元数据；不扫描会话正文、不迁移 provider、不修复历史。`
  - status `只读 · 1-50 / 1326 · C:\Users\sciman\.codex\state_5.sqlite`

## Commands

- `python -m py_compile scripts\serve-operator-ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_script.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_style.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_text.py`
- `python -m unittest tests.runtime.test_operator_codex_history_api tests.runtime.test_operator_ui tests.runtime.test_codex_history_view_diagnose -v`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Start -UiLanguage zh-CN -Port 8770`
- Browser probe of `http://127.0.0.1:8770/?lang=zh-CN`, Codex tab, `查询历史`

## Results

- `py_compile`: pass.
- Focused unittest: 12 tests pass.
- `build-runtime.ps1`: `OK python-bytecode`, `OK python-import`.
- `verify-repo.ps1 -Check Runtime`: 112 test files pass, failures=0.
- `verify-repo.ps1 -Check Contract`: all checks pass, including schema, dependency baseline, target governance consistency, policy, and agent rule sync checks.
- `doctor-runtime.ps1`: pass with existing `WARN codex-capability-degraded`; this warning is host capability posture evidence and is unrelated to the read-only history query endpoint.
- 8770 browser probe: live UI rendered the new history query form and returned the first 50 read-only rows from the current SQLite state.

## Rollback

- Revert this evidence file and the history query changes in:
  - `scripts/serve-operator-ui.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui_script.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui_style.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui_text.py`
  - `tests/runtime/test_operator_codex_history_api.py`
  - `tests/runtime/test_operator_ui.py`
