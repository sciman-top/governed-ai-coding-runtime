# 20260417 Rename To Governed AI Coding Runtime

## Goal
- 新增三份澄清产品边界与实现边界的文档。
- 将项目当前有效命名从 `governed-agent-platform` 调整为 `governed-ai-coding-runtime`。
- 同步更新当前活跃文档、规划资产、schema 标识、脚本和根目录工作根。

## Basis
- `README.md`
- `AGENTS.md`
- `docs/README.md`
- `docs/product/interaction-model.md`
- `docs/architecture/mvp-stack-vs-target-stack.md`
- `docs/architecture/compatibility-matrix.md`
- `docs/adrs/0004-rename-project-to-governed-ai-coding-runtime.md`
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- `scripts/github/create-roadmap-issues.ps1`

## Commands
- `rg -n "governed-agent-platform|Governed Agent Platform|governed-agent-platform.local" README.md AGENTS.md docs schemas scripts`
- `Move-Item docs/prd/governed-agent-platform-ai-coding-prd.md docs/prd/governed-ai-coding-runtime-prd.md`
- `Move-Item docs/architecture/governed-agent-platform-target-architecture.md docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `Move-Item docs/roadmap/governed-agent-platform-90-day-plan.md docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- `Get-ChildItem schemas/jsonschema/*.json | ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }`
- `[System.Management.Automation.Language.Parser]::ParseFile(...)`
- custom PowerShell link checks for active docs
- `Rename-Item D:\OneDrive\CODE\governed-agent-platform -NewName governed-ai-coding-runtime`
- fallback content move from `D:\OneDrive\CODE\governed-agent-platform` to `D:\OneDrive\CODE\governed-ai-coding-runtime`
- background cleanup retry for the now-empty old directory

## Changes
- Added `docs/product/interaction-model.md`
- Added `docs/architecture/mvp-stack-vs-target-stack.md`
- Added `docs/architecture/compatibility-matrix.md`
- Added `docs/adrs/0004-rename-project-to-governed-ai-coding-runtime.md`
- Updated root `README.md`
- Updated root `AGENTS.md`
- Updated active docs, research notes, backlog/roadmap references, schema `$id`, and GitHub issue seeding script to the new project name
- Renamed active files:
  - `docs/prd/governed-agent-platform-ai-coding-prd.md` -> `docs/prd/governed-ai-coding-runtime-prd.md`
  - `docs/architecture/governed-agent-platform-target-architecture.md` -> `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
  - `docs/roadmap/governed-agent-platform-90-day-plan.md` -> `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- Moved the project contents into the new root directory:
  - `D:\OneDrive\CODE\governed-ai-coding-runtime`

## Verification

### File / Syntax
- new product and architecture docs exist
- rename ADR exists
- renamed PRD / architecture / roadmap files exist under the new names
- `Parser::ParseFile(scripts/github/create-roadmap-issues.ps1)` -> `PASS`

### Gate Results
- `build`: `gate_na`
  - reason: runtime build entrypoints still do not exist
  - alternative verification: active docs, renamed paths, and script references were reconciled
- `test`: `gate_na`
  - reason: no test harness yet
  - alternative verification: link checks + PowerShell parser validation
- `contract/invariant`:
  - `Get-ChildItem schemas/jsonschema/*.json | ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }` -> `PASS`
  - active doc links for renamed files -> `PASS`
  - active asset grep shows old name only in the historical note inside `README.md` and in ADR-0004 context -> `PASS`
- `hotspot`: `gate_na`
  - reason: no runtime health script yet
  - alternative verification: explicit rename ADR + compatibility / interaction / stack documents now define the product boundary more tightly

## Risks
- `D:\OneDrive\CODE\governed-agent-platform` may remain temporarily as an empty locked directory while the current session still holds a handle. The actual project contents already live under `D:\OneDrive\CODE\governed-ai-coding-runtime`.
- Historical evidence files intentionally keep the old project name to preserve audit fidelity.
- No git repository is present, so rollback relies on snapshot copies and file moves.

## Rollback
- Snapshot root:
  - `docs/change-evidence/snapshots/20260417-rename-to-governed-ai-coding-runtime/`
- Snapshot files include the pre-rename versions of all modified active files.
- To revert:
  - restore modified files from the snapshot copies
  - move renamed files back to their previous names
  - move project contents from `D:\OneDrive\CODE\governed-ai-coding-runtime` back into `D:\OneDrive\CODE\governed-agent-platform` if desired
- Added files can be removed directly:
  - `docs/product/interaction-model.md`
  - `docs/architecture/mvp-stack-vs-target-stack.md`
  - `docs/architecture/compatibility-matrix.md`
  - `docs/adrs/0004-rename-project-to-governed-ai-coding-runtime.md`
  - `docs/change-evidence/20260417-rename-to-governed-ai-coding-runtime.md`

## issue_id / clarification_mode
- `issue_id`: `rename-to-governed-ai-coding-runtime-20260417`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `plan`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`
