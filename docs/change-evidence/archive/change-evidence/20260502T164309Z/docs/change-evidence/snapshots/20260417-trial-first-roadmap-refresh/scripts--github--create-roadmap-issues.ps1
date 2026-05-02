param(
  [Parameter(Mandatory = $true)]
  [string]$Repo,

  [string]$Milestone = "90-Day Governed AI Coding Runtime MVP",

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
  @{ Name = "phase:0-alignment"; Color = "BFD4F2"; Description = "Kernel alignment phase" }
  @{ Name = "phase:1-kernel"; Color = "BFDADC"; Description = "Kernel foundation phase" }
  @{ Name = "phase:2-execution"; Color = "FBCA04"; Description = "Governed execution phase" }
  @{ Name = "phase:3-assurance"; Color = "D93F0B"; Description = "Assurance and reuse phase" }
  @{ Name = "backend"; Color = "0052CC"; Description = "Backend work" }
  @{ Name = "platform"; Color = "6F42C1"; Description = "Platform work" }
  @{ Name = "security"; Color = "B60205"; Description = "Security and policy" }
  @{ Name = "devops"; Color = "0366D6"; Description = "Infra and operations" }
  @{ Name = "eval"; Color = "5319E7"; Description = "Eval and validation" }
  @{ Name = "contracts"; Color = "0E8A16"; Description = "Contracts and schemas" }
  @{ Name = "docs"; Color = "C2E0C6"; Description = "Documentation and planning" }
)

foreach ($label in $labels) {
  Ensure-Label -Name $label.Name -Color $label.Color -Description $label.Description
}

Ensure-Milestone

$initiativeBody = @"
## Goal
Deliver an MVP governance kernel for governed AI coding in 90 days.

## Success Criteria
- [ ] Kernel contracts and sample control packs validate locally
- [ ] One target repo can run a governed read-only task end-to-end
- [ ] High-risk writes require approval
- [ ] Evidence bundles and required trace fields are emitted
- [ ] Minimum eval / trace grading baseline exists
- [ ] Second-repo compatibility pilot passes without a kernel fork
- [ ] Rollback and waiver recovery notes are documented

## In Scope
- Governance kernel contracts
- Control packs
- Repo profile registry and compatibility validation
- Deterministic lifecycle
- Governed tool execution and approval
- Evidence, trace, and replay outputs
- Second-repo reuse pilot

## Out of Scope
- Multi-repo distribution hub behavior
- Default multi-agent orchestration
- Memory-first personalization platform
- Skill marketplace or promotion workflow
- Broad deployment automation as the platform identity
"@

New-RoadmapIssue -Title "[Initiative] 90-Day Governed AI Coding Runtime MVP" -Labels @("initiative", "platform") -Body $initiativeBody

$epics = @(
  @{
    Title  = "[Epic] Governance Kernel Alignment"
    Labels = @("epic", "phase:0-alignment", "platform", "docs", "contracts")
    Body   = @"
## Goal
Lock the kernel-first boundary and complete the missing governance contract family.

## Scope
- ADR and planning alignment
- Hook, skill manifest, knowledge source, waiver, provenance, and repo-map contracts
- Control maturity and rollback semantics

## Dependencies
- None

## Acceptance Criteria
- [ ] Kernel-first ADR is accepted
- [ ] Missing contract families are named and linked to active planning docs
- [ ] Control maturity and waiver expectations are explicit
"@
  }
  @{
    Title  = "[Epic] Repo Compatibility And Control Packs"
    Labels = @("epic", "phase:1-kernel", "platform", "contracts")
    Body   = @"
## Goal
Make repo reuse explicit and testable before runtime breadth increases.

## Scope
- Sample repo profiles
- Sample control packs
- Compatibility validator and repo admission checks

## Dependencies
- [Epic] Governance Kernel Alignment

## Acceptance Criteria
- [ ] At least two sample repo profiles exist
- [ ] At least one control pack exists with owner and version
- [ ] Invalid profiles or packs fail admission
"@
  }
  @{
    Title  = "[Epic] Repo Bootstrap And Verification Foundation"
    Labels = @("epic", "phase:1-kernel", "platform", "devops")
    Body   = @"
## Goal
Bootstrap implementation skeleton and verification entrypoints around the kernel.

## Scope
- apps / packages / infra / tests skeleton
- Local verification commands
- CI baseline for schema, docs, and script integrity

## Dependencies
- [Epic] Repo Compatibility And Control Packs

## Acceptance Criteria
- [ ] Missing implementation skeleton exists
- [ ] Local verification entrypoint is documented
- [ ] CI runs minimum integrity checks
"@
  }
  @{
    Title  = "[Epic] Control Plane And Deterministic Lifecycle"
    Labels = @("epic", "phase:2-execution", "backend", "platform")
    Body   = @"
## Goal
Establish deterministic task state, gate order, and evidence references.

## Scope
- Task store skeleton
- Deterministic lifecycle validation
- Quick/full gate runner
- Control registry maturity handling

## Dependencies
- [Epic] Repo Bootstrap And Verification Foundation

## Acceptance Criteria
- [ ] Illegal transitions fail closed
- [ ] Gate order is canonical and recorded
- [ ] Control status can express advisory, observe, and enforce
"@
  }
  @{
    Title  = "[Epic] Tool Governance And Approval"
    Labels = @("epic", "phase:2-execution", "backend", "security")
    Body   = @"
## Goal
Make governed tool execution and approvals executable.

## Scope
- Tool contract enforcement
- Approval defaults and interruption path
- Risk classifier and approval service

## Dependencies
- [Epic] Control Plane And Deterministic Lifecycle

## Acceptance Criteria
- [ ] Tool requests validate against contract
- [ ] Approval-required tools pause before execution
- [ ] High-risk writes require explicit approval
"@
  }
  @{
    Title  = "[Epic] Governed Session, Evidence And Eval"
    Labels = @("epic", "phase:3-assurance", "backend", "eval")
    Body   = @"
## Goal
Run a governed session with evidence, trace, and minimum eval coverage.

## Scope
- Repo map and context shaping
- Isolated workspace bootstrap
- Evidence bundle writer
- Trace fields and minimum eval suites
- Delivery handoff bundle

## Dependencies
- [Epic] Tool Governance And Approval

## Acceptance Criteria
- [ ] One repo runs the minimum governed loop end-to-end
- [ ] Evidence and trace outputs are emitted
- [ ] Delivery bundle distinguishes full vs partial validation
"@
  }
  @{
    Title  = "[Epic] Second-Repo Reuse And Hardening"
    Labels = @("epic", "phase:3-assurance", "platform", "eval", "devops")
    Body   = @"
## Goal
Prove bounded multi-repo reuse and document minimum operating controls.

## Scope
- Second target repo profile
- Compatibility pilot
- Minimum approval/evidence operator surface
- Rollout, waiver recovery, and rollback notes

## Dependencies
- [Epic] Governed Session, Evidence And Eval

## Acceptance Criteria
- [ ] Second repo passes compatibility validation
- [ ] Second repo uses the same kernel semantics
- [ ] Minimum runbooks exist for failed rollout and expired waiver handling
"@
  }
)

foreach ($epic in $epics) {
  New-RoadmapIssue -Title $epic.Title -Labels $epic.Labels -Body $epic.Body
}

if (-not $SkipTasks) {
  $tasks = @(
    @{
      Title  = "[Task] Define missing governance contracts"
      Labels = @("task", "phase:0-alignment", "contracts", "docs")
      Body   = @"
## Goal
Define hook, skill manifest, knowledge source, waiver, provenance, and repo-map contracts.

## Dependencies
- [Epic] Governance Kernel Alignment

## Acceptance Criteria
- [ ] Each contract family has a named spec target
- [ ] Kernel-owned vs repo-owned fields are explicit
- [ ] Active planning docs link to the new contract family
"@
    }
    @{
      Title  = "[Task] Add sample repo profiles and control packs"
      Labels = @("task", "phase:1-kernel", "contracts", "platform")
      Body   = @"
## Goal
Add sample reuse artifacts that make compatibility concrete.

## Dependencies
- [Epic] Repo Compatibility And Control Packs

## Acceptance Criteria
- [ ] At least two sample repo profiles exist
- [ ] At least one control pack exists
- [ ] Samples demonstrate inheritance and stricter overrides
"@
    }
    @{
      Title  = "[Task] Build compatibility validator and repo admission checks"
      Labels = @("task", "phase:1-kernel", "platform", "contracts")
      Body   = @"
## Goal
Fail invalid repos and control packs before execution starts.

## Dependencies
- [Epic] Repo Compatibility And Control Packs

## Acceptance Criteria
- [ ] Invalid profiles fail closed
- [ ] Invalid control packs fail closed
- [ ] Admission output explains failure reasons
"@
    }
    @{
      Title  = "[Task] Initialize monorepo structure and shared verification tooling"
      Labels = @("task", "phase:1-kernel", "platform", "devops")
      Body   = @"
## Goal
Bootstrap the missing implementation skeleton and shared verification entrypoints.

## Dependencies
- [Epic] Repo Bootstrap And Verification Foundation

## Acceptance Criteria
- [ ] apps / packages / infra / tests directories exist
- [ ] Local verification entrypoint is documented
- [ ] CI runs schema, docs, and script integrity checks
"@
    }
    @{
      Title  = "[Task] Implement task store and control registry maturity model"
      Labels = @("task", "phase:2-execution", "backend", "platform")
      Body   = @"
## Goal
Create deterministic task state and control maturity handling.

## Dependencies
- [Epic] Control Plane And Deterministic Lifecycle

## Acceptance Criteria
- [ ] Task lifecycle supports required states
- [ ] Illegal transitions fail
- [ ] Control status supports advisory, observe, and enforce
"@
    }
    @{
      Title  = "[Task] Implement quick/full gate runner and repo map context shaper"
      Labels = @("task", "phase:2-execution", "platform", "backend")
      Body   = @"
## Goal
Make verification and bounded repo context executable.

## Dependencies
- [Epic] Control Plane And Deterministic Lifecycle

## Acceptance Criteria
- [ ] Canonical gate order is enforced
- [ ] Repo map stays within explicit token budget
- [ ] Invalid admission blocks governed session startup
"@
    }
    @{
      Title  = "[Task] Implement policy decision log and evidence bundle writer"
      Labels = @("task", "phase:3-assurance", "backend", "eval")
      Body   = @"
## Goal
Record all critical decisions and produce replay-oriented evidence.

## Dependencies
- [Epic] Governed Session, Evidence And Eval

## Acceptance Criteria
- [ ] Allow, block, and approve decisions are logged structurally
- [ ] Evidence bundle includes rollback or replay references where applicable
- [ ] Evidence is queryable by task id
"@
    }
    @{
      Title  = "[Task] Implement governed tool runner and approval defaults"
      Labels = @("task", "phase:2-execution", "backend", "security")
      Body   = @"
## Goal
Route tool execution through policy and approval defaults.

## Dependencies
- [Epic] Tool Governance And Approval

## Acceptance Criteria
- [ ] Tool requests validate against contract
- [ ] Approval-required tools pause before execution
- [ ] High-risk writes require explicit approval
"@
    }
    @{
      Title  = "[Task] Implement governed session bootstrap and isolated workspace"
      Labels = @("task", "phase:3-assurance", "backend", "platform")
      Body   = @"
## Goal
Start governed sessions with repo-aware context and isolated execution.

## Dependencies
- [Epic] Governed Session, Evidence And Eval

## Acceptance Criteria
- [ ] Task can start in isolated workspace
- [ ] Repo-aware context and budgets are injected
- [ ] One repo can run the minimum governed loop end-to-end
"@
    }
    @{
      Title  = "[Task] Add eval baseline and second-repo compatibility pilot"
      Labels = @("task", "phase:3-assurance", "eval", "platform")
      Body   = @"
## Goal
Prove the kernel is both measurable and reusable.

## Dependencies
- [Epic] Second-Repo Reuse And Hardening

## Acceptance Criteria
- [ ] Minimum eval suites and required trace fields exist
- [ ] Second repo passes compatibility validation
- [ ] No kernel fork is needed for the second-repo pilot
"@
    }
  )

  foreach ($task in $tasks) {
    New-RoadmapIssue -Title $task.Title -Labels $task.Labels -Body $task.Body
  }
}
