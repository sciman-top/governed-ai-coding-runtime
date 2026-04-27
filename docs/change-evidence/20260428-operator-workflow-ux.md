# Operator Workflow UX And Local UI Refresh

## Context
- Date: 2026-04-28
- Change type: operator workflow / local UI / documentation
- Goal: reduce command memorization, make one-command daily paths easier to discover, and make the local operator HTML more scan-friendly.

## Updated Surfaces
- `scripts/operator.ps1`
- `scripts/serve-operator-ui.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- `tests/runtime/test_operator_entrypoint.py`
- `tests/runtime/test_operator_ui.py`
- `tests/runtime/test_runtime_doctor.py`
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
- `docs/quickstart/ai-coding-usage-guide.md`
- `docs/quickstart/ai-coding-usage-guide.zh-CN.md`

## Operator Contract
- `scripts/operator.ps1 -Action Help` is the low-risk discovery entrypoint.
- `scripts/operator.ps1 -Action Readiness` runs the local hard-gate order: `build -> test -> contract/invariant -> hotspot`, then renders the operator UI.
- Target-repo apply actions remain explicit: `GovernanceBaselineAll`, `DailyAll`, and `ApplyAllFeatures`; they default to all targets and accept `-Target <target-id>` for single-target operation.
- `scripts/operator.ps1 -Action OperatorUi -OpenUi` starts the localhost interactive console and opens the browser.
- `scripts/serve-operator-ui.py --serve --open` is the direct Python interactive server entrypoint.
- Without `-OpenUi` / `--serve`, the UI path remains a static snapshot generator.
- Operator UI defaults to `zh-CN`; English is explicit via `scripts/operator.ps1 -Action OperatorUi -OpenUi -UiLanguage en` or `python scripts/serve-operator-ui.py --serve --lang en --open`.

## UI Posture
- The operator HTML now has two modes: static snapshot and localhost interactive console.
- The interactive console runs allowlisted operator actions only: target list, readiness, rules dry-run/apply, governance baseline rollout, daily all, and all-features apply.
- Browser-side settings cover UI language, target selection, gate mode, target parallelism, fail-fast, dry-run, and milestone tag.
- Browser-local execution history records recent action, target, exit code, elapsed time, and output for quick comparison.
- Evidence/artifact/verification refs can be clicked for bounded repo-local file preview.
- The layout now prioritizes scan-friendly full-width operation, summary metrics, maintenance policy refs, attachment posture, and task output refs.
- The command output panel is placed directly below the action buttons and action completion scrolls it into view, so button clicks produce visible feedback without requiring manual search.
- The UI has Chinese and English label sets; raw runtime states, paths, refs, and protocol values remain unmodified.
- The UI does not allow arbitrary shell commands or arbitrary filesystem reads from the browser page.
- Local Playwright checks covered a 1366px desktop viewport and a 390px mobile viewport; the mobile layout uses field rows instead of clipped horizontal tables.

## Verification
- `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint -v` -> pass (`Ran 11 tests`, `OK`)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness` -> pass:
  - `OK python-bytecode`, `OK python-import`
  - runtime suite: `Completed 76 test files`, `failures=0`
  - `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
  - `OK dependency-baseline`, `OK transition-stack-convergence`, `OK target-repo-governance-consistency`
  - `OK python-command`, `OK windows-process-environment`, `OK gate-command-operator`, `OK codex-capability-ready`
  - generated `.runtime/artifacts/operator-ui/index.html`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> pass (`OK active-markdown-links`, `OK claim-drift-sentinel`, `OK claim-evidence-freshness`)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> pass (`OK powershell-parse`, `OK issue-seeding-render`)
- `python scripts/serve-operator-ui.py` -> pass; generated `.runtime/artifacts/operator-ui/index.html`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi` -> pass; generated default `zh-CN` static snapshot.
- `python scripts/serve-operator-ui.py --serve --lang zh-CN` -> pass; served default Chinese interactive console.
- UI action smoke via HTTP POST `/api/run` with `action=targets` -> pass; returned active targets: `classroomtoolkit`, `github-toolkit`, `self-runtime`, `skills-manager`, `vps-ssh-launcher`.
- UI dry-run smoke via `run_operator_action({"action":"daily_all","target":"classroomtoolkit","dry_run":true})` -> pass; command included `-Target classroomtoolkit` and `-DryRun`.
- `python scripts/serve-operator-ui.py --lang en --output .runtime/artifacts/operator-ui/index.en.html` -> pass; generated English UI.
- Playwright render checks:
  - `http://127.0.0.1:8770/?lang=zh-CN` at `1366x900` -> pass, title `Governed Runtime 操作者面板`, layout width `1307`, sidebar width `320`, dashboard width `969`, action buttons `7`, ref buttons `6`, approval ids not clickable.
  - clicked `列出目标仓` in the browser -> pass, output panel showed `exit_code: 0` and the target catalog list; after the feedback fix, output panel top was visible at `578px` in the `900px` viewport.
  - selected `classroomtoolkit`, checked `只预演`, and clicked `运行 Daily` in the browser -> pass; output included `-Target classroomtoolkit`, `-FlowMode daily`, `-Mode quick`, and `DRY-RUN daily-all-targets`; execution history recorded `daily_all · exit_code=0`.
  - `http://127.0.0.1:8770/?lang=zh-CN` at `390x800` -> pass, layout width `347`, target select width `317`, history width `317`, action buttons `7`, no horizontal overflow.
- `git diff --check` -> pass; only repo-normal LF/CRLF warnings were emitted.

## Rollback
- Revert this evidence file and the listed code/documentation updates with git.
