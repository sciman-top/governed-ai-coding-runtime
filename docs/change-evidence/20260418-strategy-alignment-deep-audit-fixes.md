# 20260418 Strategy Alignment Deep Audit Fixes Evidence

## Change Basis

- Request: deeply review recent strategic, final-state, roadmap, backlog, and plan changes; identify old/new plan errors and improve the documentation and automation.
- Landing point: roadmap, backlog, issue seeding, entry docs, and planning evidence.
- Target destination: keep `GAP-035` through `GAP-039` as the active productization queue while making `GAP-040` through `GAP-044` executable coordination gates.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=strategy-alignment-plan-audit`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Findings Fixed

1. The strategy alignment plan was listed under roadmap `Architecture` inputs even though it is a plan. It is now under `Plans`.
2. The roadmap said Strategy Alignment Gate A/B must constrain `GAP-035` through `GAP-039`, but `issue-seeds.yaml` did not encode those dependencies. The seed blockers and rendered backlog now match the roadmap:
   - `GAP-035` waits for `GAP-042`
   - `GAP-036` and `GAP-037` wait for `GAP-043`
   - `GAP-038` and `GAP-039` wait for `GAP-044`
3. `scripts/github/create-roadmap-issues.ps1` had a stale hand-maintained task list that did not create every seed-backed task and was not covered by `-ValidateOnly -RenderAll`. Task creation now derives from `issue-seeds.yaml`, and validation reports `rendered_issue_creation_tasks`.
4. The strategy plan treated backlog reconciliation as only after Tasks 1 through 6, but current work already seeded `GAP-040` through `GAP-044`. The plan now distinguishes initial gate seeding from final closeout reconciliation.
5. Root README, bilingual READMEs, docs index, backlog index, and plans index lagged behind the new coordination-gate posture. They now mention `GAP-040` through `GAP-044`.
6. The external reference list had a source gap for GAAI-style repo files. The plan now includes the primary repository and requires unsourced references to be re-verified or excluded.

## Files Changed

- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/plans/README.md`
- `docs/plans/governance-runtime-strategy-alignment-plan.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `scripts/github/create-roadmap-issues.ps1`
- `tests/runtime/test_issue_seeding.py`
- `docs/change-evidence/README.md`

## Platform Diagnostics

Executed from repository root on 2026-04-18:

```powershell
codex --version
```

- Exit code: `0`
- Key output: `codex-cli 0.121.0`

```powershell
codex --help
```

- Exit code: `0`
- Key output: `Codex CLI`, commands include `exec`, `review`, `mcp`, `app-server`, `features`

```powershell
codex status
```

- Exit code: `1`
- Classification: `platform_na`
- Reason: non-interactive shell returned `Error: stdin is not a terminal`
- Alternative verification: `codex --version`, `codex --help`, and local `AGENTS.md` read
- Evidence link: this file
- Expires at: `n/a`

## Verification

TDD red check:

```powershell
python -m unittest tests.runtime.test_issue_seeding.IssueSeedingScriptTests.test_validate_only_render_all_checks_all_issue_body_sources
```

- Exit code: `1`
- Key output: `KeyError: 'rendered_issue_creation_tasks'`

Dependency red check:

```powershell
python -m unittest tests.runtime.test_issue_seeding.IssueSeedingScriptTests.test_strategy_alignment_gates_are_rendered_as_productization_dependencies
```

- Exit code: `1`
- Key output: failures for missing `GAP-042`, `GAP-043`, and `GAP-044` dependencies

Targeted green checks:

```powershell
python -m unittest tests.runtime.test_issue_seeding
```

- Exit code: `0`
- Key output: `Ran 8 tests`, `OK`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll
```

- Exit code: `0`
- Key output: `{"issue_seed_version":"3.2","rendered_tasks":27,"rendered_issue_creation_tasks":27,"rendered_epics":7,"rendered_initiative":true}`

Local pre-gates:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts
```

- Exit code: `0`
- Key output: `OK powershell-parse`, `OK issue-seeding-render`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

- Exit code: `0`
- Key output: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK old-project-name-historical-only`

```powershell
git diff --check
```

- Exit code: `0`
- Key output: no whitespace errors; line-ending warnings only

Required gate order:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

- Exit code: `0`
- Key output: `OK python-bytecode`, `OK python-import`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

- Exit code: `0`
- Key output: `OK runtime-unittest`, `Ran 118 tests`, `OK`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

- Exit code: `0`
- Key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

- Exit code: `0`
- Key output: `OK runtime-policy-compatibility`, `OK runtime-policy-maintenance`, `OK runtime-status-surface`, `OK adapter-posture-visible`

Full check:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

- Exit code: `0`
- Key output: `OK runtime-build`, `OK runtime-unittest`, `OK schema-catalog-pairing`, `OK runtime-doctor`, `OK active-markdown-links`, `OK issue-seeding-render`, `Ran 118 tests`, `OK`

## Risks

- Strategy Alignment Gates are still planning and contract work, not the completed final product boundary.
- `GAP-035` through `GAP-039` remain active, but their harder design points now wait for explicit gate dependencies. This is intentional; it prevents light-pack, policy, adapter, and verification semantics from hardening too early.
- External mechanism references can drift. Task 1 must re-check primary sources before writing the final borrowing matrix.

## Rollback

- Revert this change set through git if the gate sequencing model is rejected.
- Manual rollback path:
  - remove `GAP-040` through `GAP-044` from `docs/backlog/issue-seeds.yaml`
  - remove the Strategy Alignment Gates sections from roadmap and backlog documents
  - restore the previous `GAP-035` through `GAP-039` blockers
  - revert `scripts/github/create-roadmap-issues.ps1` and `tests/runtime/test_issue_seeding.py`
  - remove strategy-gate references from README and docs index files
  - remove this evidence file and its index entry
