param(
  [Parameter(Mandatory = $true)]
  [string]$Repo,

  [string]$Milestone = "Governed AI Coding Runtime Full Lifecycle",

  [string]$Assignee = "@me",

  [switch]$SkipTasks
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-Command {
  param([string]$Name)
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Required command not found: $Name"
  }
}

function Ensure-Label {
  param(
    [string]$Name,
    [string]$Color,
    [string]$Description
  )
  gh label create $Name -R $Repo -c $Color -d $Description -f | Out-Null
}

function Ensure-Milestone {
  $existing = gh api "repos/$Repo/milestones?state=all" --paginate --jq ".[] | select(.title == `"$Milestone`") | .title" 2>$null
  if (-not $existing) {
    gh api "repos/$Repo/milestones" -f title="$Milestone" | Out-Null
    Write-Host "Created milestone: $Milestone"
  }
  else {
    Write-Host "Milestone already exists: $Milestone"
  }
}

function Find-IssueNumberByTitle {
  param([string]$Title)

  gh api "repos/$Repo/issues?state=all&per_page=100" `
    --paginate `
    --jq ".[] | select(.pull_request | not) | select(.title == `"$Title`") | .number" 2>$null
}

function New-RoadmapIssue {
  param(
    [string]$Title,
    [string[]]$Labels,
    [string]$Body
  )

  $existing = Find-IssueNumberByTitle -Title $Title
  if ($existing) {
    Write-Host "Issue already exists: #$existing $Title"
    return
  }

  $tmp = New-TemporaryFile
  try {
    Set-Content -Path $tmp -Value $Body -Encoding utf8
    $args = @(
      "issue", "create",
      "-R", $Repo,
      "-t", $Title,
      "-F", $tmp,
      "-m", $Milestone,
      "-a", $Assignee
    )
    foreach ($label in $Labels) {
      $args += @("-l", $label)
    }
    gh @args | Out-Host
  }
  finally {
    Remove-Item $tmp -ErrorAction SilentlyContinue
  }
}

Ensure-Command -Name "gh"

$labels = @(
  @{ Name = "initiative"; Color = "5319E7"; Description = "Top-level initiative" }
  @{ Name = "epic"; Color = "1D76DB"; Description = "Epic issue" }
  @{ Name = "task"; Color = "0E8A16"; Description = "Task issue" }
  @{ Name = "phase:vision"; Color = "BFD4F2"; Description = "Vision alignment phase" }
  @{ Name = "phase:foundation"; Color = "BFDADC"; Description = "Foundation phase" }
  @{ Name = "phase:full-runtime"; Color = "FBCA04"; Description = "Full runtime phase" }
  @{ Name = "phase:public-release"; Color = "D93F0B"; Description = "Public usable release phase" }
  @{ Name = "phase:maintenance"; Color = "C5DEF5"; Description = "Maintenance phase" }
  @{ Name = "phase:interactive-session"; Color = "0B5FFF"; Description = "Interactive session productization phase" }
  @{ Name = "backend"; Color = "0052CC"; Description = "Backend work" }
  @{ Name = "platform"; Color = "6F42C1"; Description = "Platform work" }
  @{ Name = "security"; Color = "B60205"; Description = "Security and policy" }
  @{ Name = "devops"; Color = "0366D6"; Description = "Infra and operations" }
  @{ Name = "eval"; Color = "5319E7"; Description = "Eval and validation" }
  @{ Name = "contracts"; Color = "0E8A16"; Description = "Contracts and schemas" }
  @{ Name = "docs"; Color = "C2E0C6"; Description = "Documentation and planning" }
  @{ Name = "frontend"; Color = "FBCA04"; Description = "Operator surface work" }
  @{ Name = "product"; Color = "F9D0C4"; Description = "Product shape and lifecycle work" }
)

foreach ($label in $labels) {
  Ensure-Label -Name $label.Name -Color $label.Color -Description $label.Description
}

Ensure-Milestone

$initiativeBody = @"
## Goal
Turn the completed local runtime baseline into a generic, attach-first, interactive governed AI coding runtime that can be attached to real AI coding sessions across many repositories.

## Success Criteria
- [ ] Final product shape and capability boundary are frozen
- [ ] Real build and doctor or hotspot commands replace the remaining placeholders
- [ ] Durable task persistence and workflow skeleton are landed
- [ ] Execution workers, artifact storage, gate running, and replay exist as working runtime paths
- [ ] A repo-local light pack and machine-local runtime binding exist for arbitrary target repos
- [ ] An attach-first interactive session bridge exists
- [ ] At least one direct Codex path exists
- [ ] At least one non-Codex tool has an explicit capability-tiered posture
- [ ] Multi-repo trial evidence can drive onboarding and adapter evolution

## In Scope
- final product alignment
- foundation maturity work
- full runtime implementation
- public usable release path
- local baseline maintenance
- target-repo attachment
- interactive session bridging
- adapter tiers and trial feedback

## Out Of Scope
- commercial packaging
- enterprise org model
- marketplace or promotion workflow
- default multi-agent orchestration
- memory-first product identity
- replacing upstream AI tools with a proprietary IDE shell
- deployment automation as the default completion path
"@

New-RoadmapIssue -Title "[Initiative] Governed AI Coding Runtime Full Functional Lifecycle" -Labels @("initiative", "platform") -Body $initiativeBody

$epics = @(
  @{
    Title  = "[Epic] Vision Alignment"
    Labels = @("epic", "phase:vision", "product", "docs", "platform")
    Body   = @"
## Goal
Freeze the final product shape, capability boundary, and lifecycle stages for the project.

## Scope
- full lifecycle alignment
- final capability boundary
- non-goal boundary

## Dependencies
- None

## Acceptance Criteria
- [ ] active planning docs describe the same lifecycle stages
- [ ] final capability boundary is explicit
- [ ] the project is described as a complete runtime target rather than only contracts or tooling
"@
  }
  @{
    Title  = "[Epic] Foundation"
    Labels = @("epic", "phase:foundation", "platform", "contracts", "backend")
    Body   = @"
## Goal
Make the completed MVP capable of supporting the full product runtime.

## Scope
- clarification, rollout, compatibility, and evidence maturity
- real build and doctor gates
- durable task store skeleton
- workflow skeleton
- control lifecycle metadata

## Dependencies
- [Epic] Vision Alignment

## Acceptance Criteria
- [ ] key runtime controls are no longer documentation-only
- [ ] build and doctor gates are live
- [ ] task state is durable enough for later runtime work
"@
  }
  @{
    Title  = "[Epic] Full Runtime"
    Labels = @("epic", "phase:full-runtime", "platform", "backend", "frontend")
    Body   = @"
## Goal
Land the complete runtime path for one governed AI coding task.

## Scope
- execution worker
- artifact store
- operational gate runner
- replay pipeline
- operator UI
- runtime health and status surface

## Dependencies
- [Epic] Foundation

## Acceptance Criteria
- [ ] a real governed task can run end-to-end
- [ ] approval, verification, evidence, and replay work on the runtime path
- [ ] operators can inspect runtime state from a control-plane UI
"@
  }
  @{
    Title  = "[Epic] Public Usable Release"
    Labels = @("epic", "phase:public-release", "platform", "docs", "devops")
    Body   = @"
## Goal
Make the full runtime understandable and runnable by a new user on one machine.

## Scope
- single-machine deployment
- quickstart
- sample repo profiles
- demo flow
- packaging and release criteria
- adapter baseline and degrade behavior

## Dependencies
- [Epic] Full Runtime

## Acceptance Criteria
- [ ] a new user can clone the repo and run the runtime from docs
- [ ] sample profiles and demo flow work end-to-end
- [ ] release and packaging expectations are explicit
"@
  }
  @{
    Title  = "[Epic] Maintenance Boundary"
    Labels = @("epic", "phase:maintenance", "platform", "docs", "product")
    Body   = @"
## Goal
Keep the landed local baseline maintainable without pretending the lifecycle is finished.

## Scope
- compatibility and upgrade policy
- maintenance and triage rules
- deprecation and retirement policy
- runtime maintenance visibility through status and doctor

## Dependencies
- [Epic] Public Usable Release

## Acceptance Criteria
- [ ] upgrade and compatibility expectations are explicit
- [ ] maintenance boundary is documented
- [ ] deprecated or retired capabilities remain traceable
- [ ] maintenance policy remains visible through runtime status and doctor output
"@
  }
  @{
    Title  = "[Epic] Interactive Session Productization"
    Labels = @("epic", "phase:interactive-session", "platform", "product", "docs", "frontend", "backend")
    Body   = @"
## Goal
Turn the landed local runtime baseline into a generic, interactive, attach-first product path for real AI coding sessions.

## Scope
- target-repo attachment pack and onboarding flow
- attach-first session bridge
- direct Codex adapter and evidence mapping
- capability-tiered non-Codex adapters
- multi-repo trial feedback and generic onboarding kit

## Dependencies
- [Epic] Maintenance Boundary

## Acceptance Criteria
- [ ] a new target repo can attach without copying the kernel into it
- [ ] governed actions are callable from an active AI coding session
- [ ] at least one Codex path is direct rather than manual-handoff only
- [ ] multi-repo trial evidence is captured as product feedback
"@
  }
)

foreach ($epic in $epics) {
  New-RoadmapIssue -Title $epic.Title -Labels $epic.Labels -Body $epic.Body
}

if (-not $SkipTasks) {
  $tasks = @(
    @{
      Title  = "[Task] Align the full functional lifecycle and freeze the final product shape"
      Labels = @("task", "phase:vision", "product", "docs", "platform")
      Body   = @"
## Goal
Align active planning docs around the full functional lifecycle and final product shape.

## Dependencies
- [Epic] Vision Alignment

## Acceptance Criteria
- [ ] active planning docs use the same lifecycle stages
- [ ] the project is described as a governed runtime target rather than only a local single-machine script bundle
- [ ] MVP remains historical baseline rather than active next-step queue
"@
    }
    @{
      Title  = "[Task] Freeze the final capability boundary and non-goal boundary"
      Labels = @("task", "phase:vision", "product", "docs", "platform")
      Body   = @"
## Goal
Make final product completeness and non-goals explicit.

## Dependencies
- [Epic] Vision Alignment

## Acceptance Criteria
- [ ] final capability groups are explicit
- [ ] non-goals remain outside the active queue
- [ ] final product completeness can be judged without ad hoc interpretation
"@
    }
    @{
      Title  = "[Task] Formalize clarification, rollout, compatibility, and evidence maturity"
      Labels = @("task", "phase:foundation", "contracts", "platform", "security")
      Body   = @"
## Goal
Turn the remaining governance semantics into formal runtime policy.

## Dependencies
- [Epic] Foundation

## Acceptance Criteria
- [ ] clarification is formal runtime policy
- [ ] rollout state supports observe, advisory, and enforced modes
- [ ] compatibility is machine-checkable
- [ ] evidence maturity distinguishes missing evidence from weak outcomes
"@
    }
    @{
      Title  = "[Task] Add real build and doctor gates"
      Labels = @("task", "phase:foundation", "backend", "devops", "platform")
      Body   = @"
## Goal
Replace the remaining build and hotspot placeholders with live commands.

## Dependencies
- [Epic] Foundation

## Acceptance Criteria
- [ ] build no longer depends on gate_na
- [ ] doctor or hotspot no longer depends on gate_na
- [ ] canonical gate order can run with live commands
"@
    }
    @{
      Title  = "[Task] Add the durable task store and workflow skeleton"
      Labels = @("task", "phase:foundation", "backend", "platform")
      Body   = @"
## Goal
Make task state durable enough to support the full runtime.

## Dependencies
- [Epic] Foundation

## Acceptance Criteria
- [ ] task state survives process boundaries
- [ ] workflow transitions stay deterministic
- [ ] lifecycle data is no longer trapped in in-memory primitives
"@
    }
    @{
      Title  = "[Task] Add control lifecycle metadata and evidence completeness checks"
      Labels = @("task", "phase:foundation", "contracts", "platform", "eval")
      Body   = @"
## Goal
Track control lifecycle state and validate evidence completeness.

## Dependencies
- [Epic] Foundation

## Acceptance Criteria
- [ ] controls track lifecycle and review state
- [ ] evidence completeness can fail missing required fields
- [ ] rollback and observability links are explicit per control
"@
    }
    @{
      Title  = "[Task] Add the execution worker and managed workspace runtime"
      Labels = @("task", "phase:full-runtime", "backend", "platform")
      Body   = @"
## Goal
Run real governed tasks through a worker and managed workspace.

## Dependencies
- [Epic] Full Runtime

## Acceptance Criteria
- [ ] governed tasks execute through a worker
- [ ] workspaces are lifecycle-bound and policy-aware
- [ ] worker execution preserves approval and rollback semantics
"@
    }
    @{
      Title  = "[Task] Add artifact storage, replay plumbing, and the operational gate runner"
      Labels = @("task", "phase:full-runtime", "backend", "platform", "eval")
      Body   = @"
## Goal
Persist artifacts and make verification and replay operational.

## Dependencies
- [Epic] Full Runtime

## Acceptance Criteria
- [ ] artifacts persist outside stdout or transcript-only output
- [ ] quick and full gates run against real task executions
- [ ] failed tasks leave enough data for replay-oriented diagnosis
"@
    }
    @{
      Title  = "[Task] Add the operator UI and runtime health or status surfaces"
      Labels = @("task", "phase:full-runtime", "frontend", "platform", "backend")
      Body   = @"
## Goal
Give operators a control-plane surface for tasks, approvals, evidence, replay, and runtime status.

## Dependencies
- [Epic] Full Runtime

## Acceptance Criteria
- [ ] operators can inspect tasks, approvals, evidence, and replay without raw log digging
- [ ] runtime health and task query surfaces are stable
- [ ] the UI remains control-plane focused
"@
    }
    @{
      Title  = "[Task] Add single-machine deployment, quickstart, sample profiles, and release criteria"
      Labels = @("task", "phase:public-release", "docs", "devops", "platform")
      Body   = @"
## Goal
Make the full runtime publicly usable on one machine.

## Dependencies
- [Epic] Public Usable Release

## Acceptance Criteria
- [ ] the runtime can be started on one machine with a documented path
- [ ] sample repo profiles and a demo flow work end-to-end
- [ ] release and packaging expectations are explicit
"@
    }
    @{
      Title  = "[Task] Add adapter baseline, compatibility policy, and maintenance boundary"
      Labels = @("task", "phase:maintenance", "product", "docs", "platform")
      Body   = @"
## Goal
Keep the project maintainable after the first usable release.

## Dependencies
- [Epic] Maintenance Boundary

## Acceptance Criteria
- [ ] adapter compatibility and degrade behavior are explicit
- [ ] upgrade expectations are explicit
- [ ] maintenance, deprecation, and retirement remain traceable
- [ ] maintenance policy remains visible in runtime status and doctor checks
"@
    }
    @{
      Title  = "[Task] Add generic target-repo attachment and onboarding flow"
      Labels = @("task", "phase:interactive-session", "product", "docs", "platform", "backend")
      Body   = @"
## Goal
Make arbitrary target repositories attachable through a lightweight repo-local pack and machine-local runtime binding.

## Dependencies
- [Epic] Interactive Session Productization

## Acceptance Criteria
- [ ] a new repo can attach without copying the runtime into it
- [ ] repo-local pack contents stay declarative and portable
- [ ] onboarding posture is visible to the runtime and doctor surfaces
"@
    }
    @{
      Title  = "[Task] Add the attach-first session bridge and governed interaction surface"
      Labels = @("task", "phase:interactive-session", "frontend", "platform", "product")
      Body   = @"
## Goal
Expose governed actions from inside active AI coding sessions, with launch mode as fallback.

## Dependencies
- [Epic] Interactive Session Productization

## Acceptance Criteria
- [ ] the preferred operator flow runs inside an active AI coding session
- [ ] the runtime can fall back to launch mode when attach is unavailable
- [ ] governed actions do not require replacing the upstream tool UI
"@
    }
    @{
      Title  = "[Task] Add the direct Codex adapter and evidence mapping path"
      Labels = @("task", "phase:interactive-session", "platform", "backend", "product")
      Body   = @"
## Goal
Make at least one real Codex path direct rather than manual-handoff only.

## Dependencies
- [Epic] Interactive Session Productization

## Acceptance Criteria
- [ ] the runtime can bind a governed task to a direct Codex execution path
- [ ] Codex-driven changes and verification outputs map into task evidence
- [ ] unsupported capabilities degrade explicitly
"@
    }
    @{
      Title  = "[Task] Add capability tiers for non-Codex AI tools"
      Labels = @("task", "phase:interactive-session", "platform", "product", "docs")
      Body   = @"
## Goal
Generalize adapters beyond Codex through explicit capability tiers.

## Dependencies
- [Epic] Interactive Session Productization

## Acceptance Criteria
- [ ] native attach, process bridge, and manual handoff tiers are explicit
- [ ] non-Codex tools have honest compatibility posture
- [ ] fail-closed and degrade rules remain visible
"@
    }
    @{
      Title  = "[Task] Add the multi-repo trial loop and generic onboarding kit"
      Labels = @("task", "phase:interactive-session", "product", "docs", "eval", "platform")
      Body   = @"
## Goal
Evolve onboarding and adapters from real usage across multiple repositories.

## Dependencies
- [Epic] Interactive Session Productization

## Acceptance Criteria
- [ ] multiple repos can run through the attach flow without kernel rewrites
- [ ] onboarding and adapter gaps are captured as structured evidence
- [ ] the runtime ships with a reusable onboarding kit for new repos
"@
    }
  )

  foreach ($task in $tasks) {
    New-RoadmapIssue -Title $task.Title -Labels $task.Labels -Body $task.Body
  }
}
