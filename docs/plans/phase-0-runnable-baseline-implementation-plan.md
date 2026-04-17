# Phase 0 Runnable Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap the minimum runnable repository baseline so `governed-ai-coding-runtime` can verify its contracts locally and in CI before runtime services are introduced.

**Architecture:** Phase 0 stays intentionally narrow. It creates the missing repository skeleton, adds a single local verification entrypoint, wires CI to that entrypoint, and converts the existing control-pack metadata into a runtime-consumable reference asset for repo admission planning. Runtime task execution, approval services, durable workflows, and UI remain Phase 1+ work.

**Tech Stack:** PowerShell 7+ for repository verification, JSON Schema draft 2020-12 files under `schemas/jsonschema/`, GitHub Actions for CI, Markdown/YAML/JSON as current repo-local contract formats.

---

## Source Inputs
- Latest review baseline: `docs/reviews/2026-04-17-pre-implementation-deep-audit-and-doc-refresh.md`
- Latest review evidence: `docs/change-evidence/20260417-pre-implementation-deep-audit-and-doc-refresh.md`
- Product scope: `docs/prd/governed-ai-coding-runtime-prd.md`
- Minimum loop: `docs/architecture/minimum-viable-governance-loop.md`
- Roadmap: `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- Backlog: `docs/backlog/issue-ready-backlog.md`
- Repo rules: `AGENTS.md`
- Control pack spec: `docs/specs/control-pack-spec.md`
- Schema catalog: `schemas/catalog/schema-catalog.yaml`

## Current Operator Starting Point
- Treat Task 0 as mandatory: freeze or explicitly carry forward the current dirty worktree before adding runtime-oriented files.
- Use `docs/plans/README.md`, `docs/backlog/README.md`, `docs/reviews/README.md`, and `docs/change-evidence/README.md` as the scoped navigation layer instead of re-running a whole-repo discovery pass each time.

## Phase 0 Boundaries

### Always do
- Keep the gate order `build -> test -> contract/invariant -> hotspot`.
- Preserve `docs-first / contracts-first` traceability until runtime code exists.
- Record every planning, schema, script, or CI change in `docs/change-evidence/`.
- Run local verification before claiming a task is complete.

### Ask first
- Adding non-PowerShell runtime dependencies.
- Choosing the first backend package manager.
- Adding Docker, database, Temporal, FastAPI, or Next.js scaffolding.
- Changing schema field semantics instead of making additive changes.

### Never do
- Do not implement the governed task runtime in Phase 0.
- Do not add broad platform services before local verification is reliable.
- Do not weaken schema validation to make examples pass.
- Do not redefine `control-pack` as executable policy code; it remains metadata plus references in Phase 0.

## Planned File Structure

### Create
- `apps/README.md`: declares future application boundaries without runtime code.
- `packages/README.md`: declares future package boundaries without runtime code.
- `infra/README.md`: declares future infrastructure boundary and CI position.
- `tests/README.md`: declares future test layout and current verification strategy.
- `scripts/verify-repo.ps1`: single local verification entrypoint for Phase 0.
- `.github/workflows/verify.yml`: CI entrypoint that runs `scripts/verify-repo.ps1`.
- `schemas/control-packs/minimum-governance-kernel.control-pack.json`: runtime-consumable copy of the minimum governance kernel control-pack metadata.
- `schemas/control-packs/README.md`: explains control-pack metadata vs runtime-consumable pack references.
- `docs/change-evidence/<date>-phase-0-runnable-baseline.md`: evidence for Phase 0 implementation.

### Modify
- `README.md`: add the local verification command once `scripts/verify-repo.ps1` exists.
- `docs/README.md`: add the Phase 0 plan and control-pack runtime asset links.
- `schemas/README.md`: add `schemas/control-packs/` to schema asset map.
- `AGENTS.md`: replace `build`/`test`/`hotspot` `gate_na` only after real commands exist. In Phase 0, `contract/invariant` should point to `scripts/verify-repo.ps1 -Check Contract`.
- `docs/backlog/issue-ready-backlog.md`: mark no checklist item complete unless the implementation actually lands.

## Task List

### Task 0: Freeze Current Planning Baseline Before Runtime Edits

**Files:**
- Inspect: all current modified files from `git status --short`
- No planned file edits in this task unless verification evidence is missing

**Purpose:** Ensure the docs/spec hardening baseline is reviewable before runtime bootstrap starts.

**Acceptance criteria:**
- Current diff is understood and either committed or explicitly carried forward.
- No runtime implementation starts on top of an unknown dirty state.
- Existing schema and docs checks pass before Phase 0 edits begin.

**Steps:**
- [ ] Run:
  ```powershell
  git status --short
  git diff --stat
  ```
  Expected: only known docs/spec/schema/script changes are present.

- [ ] Run:
  ```powershell
  Get-ChildItem schemas/jsonschema/*.json |
    ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }
  ```
  Expected: command exits `0`.

- [ ] Run:
  ```powershell
  $tokens = $null
  $errors = $null
  [void][System.Management.Automation.Language.Parser]::ParseFile(
    (Resolve-Path 'scripts/github/create-roadmap-issues.ps1'),
    [ref]$tokens,
    [ref]$errors
  )
  if ($errors.Count -gt 0) { $errors | Format-List *; exit 1 }
  ```
  Expected: command exits `0`.

- [ ] Commit the current planning baseline if requested by the maintainer:
  ```powershell
  git add README.md docs schemas scripts AGENTS.md
  git commit -m "docs: harden governance planning baseline"
  ```
  Expected: one docs/contracts commit. If not committing, record in the task evidence that the baseline remains intentionally uncommitted.

### Task 1: Create Skeleton Directories With Explicit Boundaries

**Files:**
- Create: `apps/README.md`
- Create: `packages/README.md`
- Create: `infra/README.md`
- Create: `tests/README.md`
- Modify: `README.md`
- Modify: `docs/README.md`
- Evidence: `docs/change-evidence/<date>-phase-0-runnable-baseline.md`

**Purpose:** Land the top-level directories promised by the roadmap without pretending runtime services exist.

**Acceptance criteria:**
- `apps/`, `packages/`, `infra/`, and `tests/` exist.
- Each directory states what belongs there and what remains out of scope.
- Root README no longer says those directories are absent.
- No application service code is created in this task.

**Steps:**
- [ ] Create `apps/README.md` with this content:
  ```markdown
  # Apps

  Future runtime application entrypoints live here.

  ## Planned Boundaries
  - `control-plane/`: task lifecycle, policy decisions, approvals, and registry APIs.
  - `tool-runner/`: governed tool request validation and execution adapters.
  - `workflow-worker/`: durable task orchestration once workflow runtime is selected.
  - `console-web/`: future approval and evidence inspection UI.

  ## Current Status
  No runtime services are implemented yet. Phase 0 only creates the repository boundary so later tasks have stable destinations.
  ```

- [ ] Create `packages/README.md` with this content:
  ```markdown
  # Packages

  Shared runtime packages will live here after Phase 0.

  ## Planned Boundaries
  - `contracts/`: generated or hand-maintained runtime types derived from `schemas/`.
  - `policy/`: deterministic risk and approval policy helpers.
  - `testkit/`: shared fixtures for task lifecycle, evidence, gates, and repo profiles.

  ## Current Status
  Phase 0 does not add language-specific package tooling. Add package managers only with explicit dependency and supply-chain evidence.
  ```

- [ ] Create `infra/README.md` with this content:
  ```markdown
  # Infra

  Infrastructure definitions and deployment notes will live here.

  ## Current Status
  Phase 0 only adds CI verification through `.github/workflows/verify.yml`.

  ## Boundaries
  - CI and local verification wiring are in scope.
  - Runtime deployment, databases, containers, and orchestration are out of scope until the first governed loop exists.
  ```

- [ ] Create `tests/README.md` with this content:
  ```markdown
  # Tests

  Runtime tests will live here once implementation packages exist.

  ## Phase 0 Verification
  Until runtime code exists, the authoritative checks are:
  - schema JSON parsing
  - schema example validation
  - schema catalog pairing
  - PowerShell script parsing
  - active markdown link checks
  - roadmap/backlog/script drift checks

  These checks are executed by `scripts/verify-repo.ps1`.
  ```

- [ ] Update `README.md` Current Baseline:
  - Move `apps/`, `packages/`, `infra/`, and `tests/` from "Not landed yet" to "Available now" only after their README files exist.
  - Keep runtime services, CI status, executable workers, and runtime-consumable control packs accurate based on actual implementation state.

- [ ] Update `docs/README.md`:
  - Add the Phase 0 plan under Roadmap And Execution.
  - Add links to the new directory README files if they exist.

- [ ] Run:
  ```powershell
  git status --short
  git diff --check
  ```
  Expected: no whitespace errors.

- [ ] Commit:
  ```powershell
  git add README.md docs/README.md apps/README.md packages/README.md infra/README.md tests/README.md docs/change-evidence/<date>-phase-0-runnable-baseline.md
  git commit -m "docs: add phase 0 repository skeleton"
  ```
  Expected: one docs-only skeleton commit.

### Task 2: Add Local Verification Entrypoint

**Files:**
- Create: `scripts/verify-repo.ps1`
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `docs/README.md`
- Evidence: `docs/change-evidence/<date>-phase-0-runnable-baseline.md`

**Purpose:** Replace scattered manual commands with one local entrypoint that can run in CI and by operators.

**Acceptance criteria:**
- `scripts/verify-repo.ps1` supports `-Check All`, `-Check Contract`, `-Check Docs`, and `-Check Scripts`.
- `-Check All` runs contract, docs, and script checks.
- The script exits non-zero on failed checks.
- README documents the exact command.
- `AGENTS.md` references the script as the current contract/invariant entrypoint.

**Steps:**
- [ ] Create `scripts/verify-repo.ps1` with these public parameters:
  ```powershell
  param(
    [ValidateSet("All", "Contract", "Docs", "Scripts")]
    [string]$Check = "All"
  )

  Set-StrictMode -Version Latest
  $ErrorActionPreference = "Stop"
  ```

- [ ] Implement these functions in `scripts/verify-repo.ps1`:
  ```powershell
  function Write-CheckOk {
    param([string]$Name)
    Write-Host "OK $Name"
  }

  function Invoke-SchemaJsonParse {
    Get-ChildItem schemas/jsonschema/*.json | Sort-Object Name | ForEach-Object {
      Get-Content -Raw $_.FullName | ConvertFrom-Json > $null
    }
    Write-CheckOk "schema-json-parse"
  }

  function Invoke-SchemaExampleValidation {
    $schemaMap = @{}
    Get-ChildItem schemas/jsonschema/*.json | ForEach-Object {
      $schemaMap[$_.BaseName -replace '\.schema$', ''] = $_.FullName
    }

    Get-ChildItem -Recurse -File schemas/examples -Filter *.json | Sort-Object FullName | ForEach-Object {
      $dir = Split-Path $_.DirectoryName -Leaf
      $schemaPath = $schemaMap[$dir]
      if (-not $schemaPath) {
        throw "No matching schema for example directory: $dir"
      }

      $ok = Test-Json -Json (Get-Content -Raw $_.FullName) -Schema (Get-Content -Raw $schemaPath)
      if (-not $ok) {
        throw "Example failed schema validation: $($_.FullName)"
      }
    }
    Write-CheckOk "schema-example-validation"
  }

  function Invoke-SchemaCatalogPairing {
    $catalog = Get-Content -Raw schemas/catalog/schema-catalog.yaml
    $paths = [regex]::Matches($catalog, '^\s+path:\s+(.+)$', 'Multiline') | ForEach-Object { $_.Groups[1].Value.Trim() }
    $specs = [regex]::Matches($catalog, '^\s+source_spec:\s+(.+)$', 'Multiline') | ForEach-Object { $_.Groups[1].Value.Trim() }

    foreach ($path in $paths + $specs) {
      if (-not (Test-Path $path)) {
        throw "Schema catalog references missing file: $path"
      }
    }

    $knownSchemas = $paths | ForEach-Object { Split-Path $_ -Leaf }
    $uncataloguedSchemas = Get-ChildItem schemas/jsonschema/*.json | Where-Object { $knownSchemas -notcontains $_.Name }
    if ($uncataloguedSchemas) {
      throw "Uncatalogued schema files: $($uncataloguedSchemas.Name -join ', ')"
    }

    $knownSpecs = $specs | ForEach-Object { Split-Path $_ -Leaf }
    $uncataloguedSpecs = Get-ChildItem docs/specs/*.md | Where-Object { $knownSpecs -notcontains $_.Name }
    if ($uncataloguedSpecs) {
      throw "Uncatalogued spec files: $($uncataloguedSpecs.Name -join ', ')"
    }

    Write-CheckOk "schema-catalog-pairing"
  }
  ```

- [ ] Implement script parsing:
  ```powershell
  function Invoke-PowerShellParse {
    Get-ChildItem scripts -Recurse -File -Filter *.ps1 | Sort-Object FullName | ForEach-Object {
      $tokens = $null
      $errors = $null
      [void][System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$errors)
      if ($errors.Count -gt 0) {
        $errors | Format-List *
        throw "PowerShell parser errors found in $($_.FullName)"
      }
    }
    Write-CheckOk "powershell-parse"
  }
  ```

- [ ] Implement active markdown link checks:
  ```powershell
  function Invoke-ActiveMarkdownLinkCheck {
    $files = Get-ChildItem -Recurse -File -Include *.md | Where-Object {
      $_.FullName -notmatch '\\docs\\change-evidence\\'
    }

    $broken = @()
    foreach ($file in $files) {
      $text = Get-Content -Raw $file.FullName
      $matches = [regex]::Matches($text, '\[[^\]]+\]\(([^)]+)\)')
      foreach ($match in $matches) {
        $target = $match.Groups[1].Value
        if ($target -match '^(https?:|mailto:|#)') { continue }
        $path = ($target -split '#')[0]
        if ([string]::IsNullOrWhiteSpace($path)) { continue }
        $resolved = Join-Path $file.DirectoryName $path
        if (-not (Test-Path $resolved)) {
          $broken += "$($file.FullName): $target"
        }
      }
    }

    if ($broken.Count -gt 0) {
      $broken | ForEach-Object { Write-Error $_ }
      throw "Broken active markdown links found"
    }

    Write-CheckOk "active-markdown-links"
  }
  ```

- [ ] Implement backlog ID sync and old-name scan:
  ```powershell
  function Invoke-BacklogYamlIdCheck {
    $idsBacklog = Select-String -Path docs/backlog/issue-ready-backlog.md -Pattern '^### (GAP-\d+) (.+)$' |
      ForEach-Object { $_.Matches[0].Groups[1].Value }
    $idsYaml = Select-String -Path docs/backlog/issue-seeds.yaml -Pattern '^\s+- id: (GAP-\d+)' |
      ForEach-Object { $_.Matches[0].Groups[1].Value }

    $missingInYaml = $idsBacklog | Where-Object { $idsYaml -notcontains $_ }
    $missingInBacklog = $idsYaml | Where-Object { $idsBacklog -notcontains $_ }

    if ($missingInYaml -or $missingInBacklog) {
      throw "Backlog/YAML ID drift found. Missing in YAML: $($missingInYaml -join ', '); missing in backlog: $($missingInBacklog -join ', ')"
    }

    Write-CheckOk "backlog-yaml-ids"
  }

  function Invoke-OldProjectNameScan {
    $oldSlug = @('governed', 'agent', 'platform') -join '-'
    $oldTitle = @('Governed', 'Agent', 'Platform') -join ' '
    $oldPlain = @('governed', 'agent', 'platform') -join ' '
    $pattern = "$([regex]::Escape($oldSlug))|$([regex]::Escape($oldTitle))|$([regex]::Escape($oldPlain))"
    $matches = Select-String -Path README.md,docs/**/*.md,schemas/**/*.json,scripts/**/*.ps1 -Pattern $pattern -ErrorAction SilentlyContinue
    $unexpected = $matches | Where-Object {
      $_.Path -notmatch 'docs\\change-evidence\\' -and
      $_.Path -notmatch 'docs\\adrs\\0004-' -and
      -not ($_.Path -match 'README.md$' -and $_.LineNumber -eq 33)
    }

    if ($unexpected) {
      $unexpected | ForEach-Object { Write-Error "$($_.Path):$($_.LineNumber):$($_.Line)" }
      throw "Unexpected old project name references found"
    }

    Write-CheckOk "old-project-name-historical-only"
  }
  ```

- [ ] Implement check dispatch:
  ```powershell
  function Invoke-ContractChecks {
    Invoke-SchemaJsonParse
    Invoke-SchemaExampleValidation
    Invoke-SchemaCatalogPairing
  }

  function Invoke-DocsChecks {
    Invoke-ActiveMarkdownLinkCheck
    Invoke-BacklogYamlIdCheck
    Invoke-OldProjectNameScan
  }

  function Invoke-ScriptChecks {
    Invoke-PowerShellParse
  }

  switch ($Check) {
    "Contract" { Invoke-ContractChecks }
    "Docs" { Invoke-DocsChecks }
    "Scripts" { Invoke-ScriptChecks }
    "All" {
      Invoke-ContractChecks
      Invoke-DocsChecks
      Invoke-ScriptChecks
    }
  }
  ```

- [ ] Run:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
  ```
  Expected output includes:
  ```text
  OK schema-json-parse
  OK schema-example-validation
  OK schema-catalog-pairing
  OK active-markdown-links
  OK backlog-yaml-ids
  OK old-project-name-historical-only
  OK powershell-parse
  ```

- [ ] Update `README.md` Current Verification Entry Points to use:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
  ```

- [ ] Update `AGENTS.md` contract/invariant gate command to:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
  ```

- [ ] Commit:
  ```powershell
  git add scripts/verify-repo.ps1 README.md docs/README.md AGENTS.md docs/change-evidence/<date>-phase-0-runnable-baseline.md
  git commit -m "chore: add local repository verification entrypoint"
  ```

### Task 3: Add CI Verification

**Files:**
- Create: `.github/workflows/verify.yml`
- Modify: `README.md`
- Modify: `docs/README.md`
- Modify: `AGENTS.md`
- Evidence: `docs/change-evidence/<date>-phase-0-runnable-baseline.md`

**Purpose:** Make the local verification entrypoint run in CI without adding runtime dependencies.

**Acceptance criteria:**
- GitHub Actions runs the same `scripts/verify-repo.ps1 -Check All` command.
- CI does not introduce language package installation.
- README lists the CI workflow.
- `AGENTS.md` E5 remains `gate_na` unless dependency files are introduced.

**Steps:**
- [ ] Create `.github/workflows/verify.yml`:
  ```yaml
  name: Verify

  on:
    pull_request:
    push:
      branches:
        - main

  jobs:
    repo-integrity:
      name: Repository integrity
      runs-on: ubuntu-latest
      steps:
        - name: Checkout
          uses: actions/checkout@v4

        - name: Run repository verification
          shell: pwsh
          run: ./scripts/verify-repo.ps1 -Check All
  ```

- [ ] Run locally:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
  ```
  Expected: all checks print `OK`.

- [ ] Run:
  ```powershell
  git diff --check
  ```
  Expected: exit `0`.

- [ ] Update `README.md` to list CI under Current Verification Entry Points:
  ```markdown
  CI:
  - `.github/workflows/verify.yml`
  ```

- [ ] Update `AGENTS.md`:
  - Keep build as `gate_na` until runtime build exists.
  - Keep test as `gate_na` until a test harness exists.
  - Keep hotspot as `gate_na` until a runtime doctor exists.
  - Add CI workflow as alternative verification evidence for contract/script/doc integrity.

- [ ] Commit:
  ```powershell
  git add .github/workflows/verify.yml README.md docs/README.md AGENTS.md docs/change-evidence/<date>-phase-0-runnable-baseline.md
  git commit -m "ci: verify repository contracts and docs"
  ```

### Task 4: Promote Control-Pack Metadata Into A Runtime-Consumable Reference Asset

**Files:**
- Create: `schemas/control-packs/README.md`
- Create: `schemas/control-packs/minimum-governance-kernel.control-pack.json`
- Modify: `schemas/README.md`
- Modify: `docs/README.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Evidence: `docs/change-evidence/<date>-phase-0-runnable-baseline.md`

**Purpose:** Turn the validated example into a stable runtime input location while preserving the distinction between metadata and executable policy.

**Acceptance criteria:**
- `schemas/control-packs/minimum-governance-kernel.control-pack.json` validates against `schemas/jsonschema/control-pack.schema.json`.
- README documents that this is a runtime-consumable metadata reference, not executable hook code.
- GAP-003 wording remains accurate after the asset exists.

**Steps:**
- [ ] Create `schemas/control-packs/README.md`:
  ```markdown
  # Control Packs

  Runtime-consumable control-pack metadata lives here.

  ## Current Assets
  - `minimum-governance-kernel.control-pack.json`: reference metadata pack for the first governed AI coding trial loop.

  ## Boundaries
  - Control packs reference controls, hooks, skills, gates, evals, and knowledge sources.
  - Control packs do not embed executable policy code.
  - A pack can tighten governance but must not weaken kernel guarantees.

  ## Validation
  ```powershell
  Get-Content -Raw 'schemas/control-packs/minimum-governance-kernel.control-pack.json' |
    Test-Json -SchemaFile 'schemas/jsonschema/control-pack.schema.json'
  ```
  ```

- [ ] Copy the exact JSON content from `schemas/examples/control-pack/minimum-governance-kernel.example.json` to `schemas/control-packs/minimum-governance-kernel.control-pack.json`.

- [ ] Update the copied file only if needed:
  - Keep `pack_id` as `kernel.minimum-governance`.
  - Keep `version` as `0.1.0`.
  - Keep `lifecycle_status` as `draft`.
  - Keep canonical gate names `build`, `test`, `contract_or_invariant`, `hotspot_or_health_check`.

- [ ] Run:
  ```powershell
  Get-Content -Raw 'schemas/control-packs/minimum-governance-kernel.control-pack.json' |
    Test-Json -SchemaFile 'schemas/jsonschema/control-pack.schema.json'
  ```
  Expected: `True`.

- [ ] Run:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
  ```
  Expected: all checks print `OK`.

- [ ] Update `schemas/README.md`:
  - Add `control-packs/README.md`.
  - Add `control-packs/minimum-governance-kernel.control-pack.json`.

- [ ] Update `docs/README.md`:
  - Link to `schemas/control-packs/minimum-governance-kernel.control-pack.json`.

- [ ] Update `docs/backlog/issue-ready-backlog.md` GAP-003 acceptance criteria only if the runtime-consumable metadata asset is landed:
  ```markdown
  - [x] control pack metadata validates against `schemas/jsonschema/control-pack.schema.json`
  - [x] sample control pack has version, owner, and scope metadata
  - [ ] runtime-consumable pack references are checked by repo admission
  - [ ] admission minimums cover commands, tools, and path policy
  - [ ] invalid repos fail before session startup
  ```

- [ ] Commit:
  ```powershell
  git add schemas/control-packs schemas/README.md docs/README.md docs/backlog/issue-ready-backlog.md docs/change-evidence/<date>-phase-0-runnable-baseline.md
  git commit -m "docs: add runtime-consumable control pack metadata"
  ```

### Task 5: Add Repo Admission Planning Contract

**Files:**
- Create: `docs/specs/repo-admission-minimums-spec.md`
- Modify: `docs/README.md`
- Modify: `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Evidence: `docs/change-evidence/<date>-phase-0-runnable-baseline.md`

**Purpose:** Define what must be true before a repository can enter the first governed trial slice.

**Acceptance criteria:**
- Admission minimums cover commands, tools, path policy, control pack, and verification.
- The spec is explicit enough for Phase 1 repo profile resolution.
- No runtime admission code is implemented in this task.

**Steps:**
- [ ] Create `docs/specs/repo-admission-minimums-spec.md`:
  ```markdown
  # Repo Admission Minimums Spec

  ## Status
  Draft

  ## Purpose
  Define the minimum checks a target repository must satisfy before it can enter the first governed AI coding trial slice.

  ## Required Inputs
  - repository identifier
  - repo profile reference
  - working directory or checkout locator
  - control pack reference
  - allowed read-only tools
  - path scope policy
  - verification gate commands or explicit gate_na records

  ## Admission Checks
  1. Repo profile validates against `schemas/jsonschema/repo-profile.schema.json`.
  2. Control pack validates against `schemas/jsonschema/control-pack.schema.json`.
  3. Path policy defines at least one allowed read scope.
  4. Read-only tool references are declared in the repo profile or inherited control pack.
  5. Build, test, contract_or_invariant, and hotspot_or_health_check are either command-backed or have explicit gate_na records.
  6. Repo overrides only tighten or extend kernel governance.

  ## Failure Behavior
  - Missing repo profile: block startup.
  - Invalid control pack: block startup.
  - Missing path policy: block startup.
  - Weakened gate semantics: block startup.
  - Missing optional handoff hints: warn only.

  ## Non-Goals
  - running the governed task
  - mutating the target repository
  - approving write-side tools
  - creating runtime UI
  ```

- [ ] Update `docs/README.md` Specs list with `Repo Admission Minimums Spec`.

- [ ] Update roadmap Phase 0 wording to reference repo admission minimums spec once created.

- [ ] Update GAP-003 acceptance criteria:
  ```markdown
  - [x] admission minimums cover commands, tools, and path policy
  - [ ] invalid repos fail before session startup
  ```

- [ ] Run:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
  ```
  Expected: all checks print `OK`.

- [ ] Commit:
  ```powershell
  git add docs/specs/repo-admission-minimums-spec.md docs/README.md docs/roadmap/governed-ai-coding-runtime-90-day-plan.md docs/backlog/issue-ready-backlog.md docs/change-evidence/<date>-phase-0-runnable-baseline.md
  git commit -m "docs: define repo admission minimums"
  ```

### Task 6: Update Project Gates After Verification Entrypoint Exists

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/change-evidence/<date>-phase-0-runnable-baseline.md`

**Purpose:** Move the repo from scattered manual contract checks to one documented verification command while keeping non-existent runtime gates honest.

**Acceptance criteria:**
- `contract/invariant` gate uses `scripts/verify-repo.ps1 -Check Contract`.
- `test` alternative verification uses `scripts/verify-repo.ps1 -Check Scripts` and docs checks.
- `hotspot` alternative verification uses `scripts/verify-repo.ps1 -Check Docs`.
- `build` remains `gate_na` until runtime build exists.
- `E5` remains `gate_na` because no dependencies are introduced.

**Steps:**
- [ ] In `AGENTS.md`, update the gate table:
  ```markdown
  | contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | 当前仓库最硬的机器约束是 schema 与示例完整性 | 同步检查 catalog/spec/schema/example 配对完整性 | `docs/change-evidence/*.md` | `n/a` |
  ```

- [ ] In `AGENTS.md`, update `test` alternative verification to mention:
  ```markdown
  `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
  ```

- [ ] In `AGENTS.md`, update `hotspot` alternative verification to mention:
  ```markdown
  `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  ```

- [ ] In `README.md`, replace manual verification snippets with:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
  ```

- [ ] Run gate order manually:
  ```powershell
  # build gate_na: record reason in evidence
  # test gate_na alternative
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts

  # contract/invariant active
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract

  # hotspot gate_na alternative
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
  ```
  Expected: all executable commands print `OK`.

- [ ] Commit:
  ```powershell
  git add AGENTS.md README.md docs/change-evidence/<date>-phase-0-runnable-baseline.md
  git commit -m "docs: route project gates through local verifier"
  ```

### Task 7: Final Phase 0 Verification And Handoff

**Files:**
- Modify: `docs/change-evidence/<date>-phase-0-runnable-baseline.md`
- Optional modify: `docs/reviews/<date>-phase-0-runnable-baseline-review.md`

**Purpose:** Close Phase 0 with evidence that the repository is ready for Phase 1 implementation planning.

**Acceptance criteria:**
- `scripts/verify-repo.ps1 -Check All` passes.
- `git diff --check` passes.
- `git status --short` is clean after commits.
- Evidence records `gate_na` fields with reason, alternative verification, evidence link, and expiry.
- Residual risks are explicit.

**Steps:**
- [ ] Run:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
  git diff --check
  git status --short
  ```
  Expected:
  - verifier prints all `OK` lines
  - `git diff --check` exits `0`
  - `git status --short` prints no output

- [ ] Ensure evidence contains this gate table:
  ```markdown
  | gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
  |---|---|---|---|---|---|---|---|
  | build | `gate_na` | `n/a` | not run | runtime services and build entrypoints still do not exist | repo skeleton and verification entrypoint checks | `docs/change-evidence/<date>-phase-0-runnable-baseline.md` | `2026-05-31` |
  | test | `gate_na` | `n/a` | not run | no runtime test harness exists yet | `scripts/verify-repo.ps1 -Check Scripts` plus docs checks | `docs/change-evidence/<date>-phase-0-runnable-baseline.md` | `2026-05-31` |
  | contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass | schema, examples, and catalog are the active contract baseline | full repo verification also passed | `docs/change-evidence/<date>-phase-0-runnable-baseline.md` | `n/a` |
  | hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | `scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/<date>-phase-0-runnable-baseline.md` | `2026-05-31` |
  ```

- [ ] Add final residual risks:
  ```markdown
  ## Residual Risks
  - Runtime task execution is still absent.
  - Repo admission is specified but not enforced by runtime code.
  - Build/test gates remain gate_na until the first runtime package exists.
  - CI validates repository integrity, not governed task behavior.
  ```

- [ ] Commit:
  ```powershell
  git add docs/change-evidence/<date>-phase-0-runnable-baseline.md
  git commit -m "docs: record phase 0 verification evidence"
  ```

## Checkpoints

### Checkpoint A: After Tasks 1-3
- `apps/`, `packages/`, `infra/`, and `tests/` exist.
- `scripts/verify-repo.ps1 -Check All` passes locally.
- `.github/workflows/verify.yml` uses the same verification command.
- No runtime service code exists yet.

### Checkpoint B: After Tasks 4-6
- Runtime-consumable control-pack metadata exists.
- Repo admission minimums are specified.
- `AGENTS.md` gate table points at the local verifier for contract/invariant checks.
- Build/test/hotspot remain honestly classified as `gate_na`.

### Checkpoint C: After Task 7
- Working tree is clean.
- Evidence captures all gate results and N/A fields.
- The repository is ready for Phase 1 implementation planning.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Verification script grows into a runtime framework | Medium | Keep it limited to repository integrity checks; runtime work starts in Phase 1. |
| CI creates false confidence | Medium | Label CI as repo integrity only, not governed task validation. |
| Control pack metadata is mistaken for executable policy | High | README and schemas docs must state it references controls and does not execute hooks. |
| `AGENTS.md` gate updates overclaim readiness | High | Keep build/test/hotspot as `gate_na` until real runtime commands exist. |
| PowerShell `Test-Json` behavior differs by host version | Medium | Run CI on `ubuntu-latest` with `pwsh`; record version if failure occurs. |

## Open Questions
- Should Phase 1 introduce Python package tooling immediately, or should the first governed trial stay script-first until task intake semantics are proven?
- Should GitHub Actions be the only CI target in Phase 0, or should a local-only verifier remain the sole hard requirement until the first runtime package exists?

## Completion Definition
Phase 0 is complete when:
- the repository has explicit top-level skeleton directories
- a single local verifier runs contract, docs, and script checks
- CI runs the same verifier
- control-pack metadata has a runtime-consumable reference location
- repo admission minimums are documented
- project gates are updated without overclaiming runtime readiness
- evidence records verification and rollback paths
