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
  @{ Name = "phase:0-baseline"; Color = "BFD4F2"; Description = "Runnable baseline phase" }
  @{ Name = "phase:1-trial"; Color = "BFDADC"; Description = "First trial slice phase" }
  @{ Name = "phase:2-write"; Color = "FBCA04"; Description = "Controlled write phase" }
  @{ Name = "phase:3-assurance"; Color = "D93F0B"; Description = "Delivery assurance phase" }
  @{ Name = "phase:4-hardening"; Color = "C5DEF5"; Description = "Reuse and hardening phase" }
  @{ Name = "backend"; Color = "0052CC"; Description = "Backend work" }
  @{ Name = "platform"; Color = "6F42C1"; Description = "Platform work" }
  @{ Name = "security"; Color = "B60205"; Description = "Security and policy" }
  @{ Name = "devops"; Color = "0366D6"; Description = "Infra and operations" }
  @{ Name = "eval"; Color = "5319E7"; Description = "Eval and validation" }
  @{ Name = "contracts"; Color = "0E8A16"; Description = "Contracts and schemas" }
  @{ Name = "docs"; Color = "C2E0C6"; Description = "Documentation and planning" }
  @{ Name = "frontend"; Color = "FBCA04"; Description = "Operator surface work" }
)

foreach ($label in $labels) {
  Ensure-Label -Name $label.Name -Color $label.Color -Description $label.Description
}

Ensure-Milestone

$initiativeBody = @"
## Goal
Deliver an MVP governance kernel for governed AI coding in 90 days while producing a first trialable governed loop within 2-3 weeks.

## Success Criteria
- [ ] One target repo can run a governed read-only task end-to-end within the first 2-3 weeks
- [ ] High-risk writes require approval and carry rollback references
- [ ] Quick and full verification states are emitted in canonical order
- [ ] Evidence bundles and required trace fields are emitted
- [ ] Completed tasks produce a delivery handoff bundle
- [ ] Second-repo compatibility pilot passes without a kernel fork
- [ ] Rollback and waiver recovery notes are documented

## In Scope
- Governance kernel contracts already landed in the repo
- Runnable baseline, repo admission, and local verification
- Deterministic task intake and repo resolution
- Governed tool execution, approval, verification, and evidence
- CLI/scripted early trial flow
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
    Title  = "[Epic] Runnable Baseline And Trial Bootstrap"
    Labels = @("epic", "phase:0-baseline", "platform", "docs", "devops")
    Body   = @"
## Goal
Create the minimum runnable repository baseline for the first governed trial.

## Scope
- Planning alignment
- apps / packages / infra / tests bootstrap
- Local verification entrypoints and CI minimums
- Sample control pack and repo admission minimums

## Dependencies
- None

## Acceptance Criteria
- [ ] Planning artifacts describe the same trial-first order
- [ ] Missing implementation skeleton exists
- [ ] Local verification entrypoint and minimum CI are documented
- [ ] Repo admission minimums are explicit
"@
  }
  @{
    Title  = "[Epic] First Read-Only Governed Trial Slice"
    Labels = @("epic", "phase:1-trial", "backend", "platform")
    Body   = @"
## Goal
Run the first operator-visible governed session through a CLI or scripted path.

## Scope
- Deterministic task intake
- Repo profile resolution
- Read-only governed tool path
- Evidence timeline and task output
- CLI or scripted trial entrypoint

## Dependencies
- [Epic] Runnable Baseline And Trial Bootstrap

## Acceptance Criteria
- [ ] One repo can run a read-only governed task end-to-end
- [ ] Evidence captures task, decisions, commands, and outputs
- [ ] Operator can inspect output without reconstructing raw logs
"@
  }
  @{
    Title  = "[Epic] Controlled Write And Approval"
    Labels = @("epic", "phase:2-write", "backend", "security")
    Body   = @"
## Goal
Extend the read-only trial into a controlled write path with workspace isolation and approvals.

## Scope
- Isolated workspace or worktree allocation
- Write policy defaults
- Approval service and interruption flow
- Write-side governed tool path
- Rollback references
- Quick verification

## Dependencies
- [Epic] First Read-Only Governed Trial Slice

## Acceptance Criteria
- [ ] High-risk writes require explicit approval
- [ ] Write-side tools carry rollback references
- [ ] Quick verification runs before delivery claims
"@
  }
  @{
    Title  = "[Epic] Delivery Assurance And Replay"
    Labels = @("epic", "phase:3-assurance", "backend", "eval")
    Body   = @"
## Goal
Turn governed execution into validated delivery with evidence, replay, and trace quality.

## Scope
- Full verification and escalation rules
- Delivery handoff bundle
- Replay references
- Required trace fields and minimum eval baseline

## Dependencies
- [Epic] Controlled Write And Approval

## Acceptance Criteria
- [ ] Quick and full verification states are distinct and recorded
- [ ] Completed tasks produce a handoff bundle
- [ ] Trace and eval baseline can run on trial tasks
"@
  }
  @{
    Title  = "[Epic] Second-Repo Reuse And Operator Hardening"
    Labels = @("epic", "phase:4-hardening", "platform", "eval", "frontend", "devops")
    Body   = @"
## Goal
Prove bounded multi-repo reuse and add only the operator surfaces needed for repeated use.

## Scope
- Second target repo profile
- Compatibility pilot
- Minimum approval/evidence console
- Waiver recovery and control rollback runbooks

## Dependencies
- [Epic] Delivery Assurance And Replay

## Acceptance Criteria
- [ ] Second repo uses the same kernel semantics
- [ ] Console scope stays control-plane focused
- [ ] Runbooks exist for failed rollout and expired waiver handling
"@
  }
)

foreach ($epic in $epics) {
  New-RoadmapIssue -Title $epic.Title -Labels $epic.Labels -Body $epic.Body
}

if (-not $SkipTasks) {
  $tasks = @(
    @{
      Title  = "[Task] Align planning artifacts around the first trial slice"
      Labels = @("task", "phase:0-baseline", "docs", "platform")
      Body   = @"
## Goal
Keep roadmap, backlog, issue seeds, and the seeding script synchronized around the same first trial slice.

## Dependencies
- [Epic] Runnable Baseline And Trial Bootstrap

## Acceptance Criteria
- [ ] Planning artifacts describe the same order and success criteria
- [ ] First runnable slice is explicit
- [ ] 90-day MVP criteria still preserve approval, evidence, verification, and reuse goals
"@
    }
    @{
      Title  = "[Task] Initialize implementation skeleton and verification entrypoints"
      Labels = @("task", "phase:0-baseline", "platform", "devops")
      Body   = @"
## Goal
Bootstrap the missing implementation skeleton and minimum verification foundation.

## Dependencies
- [Epic] Runnable Baseline And Trial Bootstrap

## Acceptance Criteria
- [ ] apps / packages / infra / tests directories exist
- [ ] Local verification entrypoint is documented
- [ ] CI runs schema, docs, and script integrity checks
"@
    }
    @{
      Title  = "[Task] Add sample control pack and repo admission minimums"
      Labels = @("task", "phase:0-baseline", "contracts", "platform")
      Body   = @"
## Goal
Make the first trial slice enforceable through minimum repo admission rules.

## Dependencies
- [Epic] Runnable Baseline And Trial Bootstrap

## Acceptance Criteria
- [ ] At least one control pack exists with owner and version
- [ ] Admission minimums cover commands, tools, and path policy
- [ ] Invalid repos fail before startup
"@
    }
    @{
      Title  = "[Task] Implement deterministic task intake and repo profile resolution"
      Labels = @("task", "phase:1-trial", "backend", "platform")
      Body   = @"
## Goal
Create the durable task and startup inputs for the first trial slice.

## Dependencies
- [Epic] First Read-Only Governed Trial Slice

## Acceptance Criteria
- [ ] Task intake requires goal, scope, acceptance, repo, and budgets
- [ ] Illegal startup transitions fail closed
- [ ] Repo profile resolution attaches the correct runtime inputs
"@
    }
    @{
      Title  = "[Task] Implement read-only governed tool path and evidence timeline"
      Labels = @("task", "phase:1-trial", "backend", "platform")
      Body   = @"
## Goal
Run bounded read-only execution and persist what happened.

## Dependencies
- [Epic] First Read-Only Governed Trial Slice

## Acceptance Criteria
- [ ] Read-only tools validate against contract
- [ ] Evidence captures task, decisions, commands, and outputs
- [ ] One repo can execute a bounded read-only session
"@
    }
    @{
      Title  = "[Task] Add CLI or scripted entrypoint for the first governed trial"
      Labels = @("task", "phase:1-trial", "platform", "docs")
      Body   = @"
## Goal
Give an operator one documented path to run the first trial slice.

## Dependencies
- [Epic] First Read-Only Governed Trial Slice

## Acceptance Criteria
- [ ] Operator can start the first trial through one documented entrypoint
- [ ] Entry path attaches repo profile and budgets
- [ ] One read-only governed task runs end-to-end
"@
    }
    @{
      Title  = "[Task] Implement isolated workspace allocation and write policy defaults"
      Labels = @("task", "phase:2-write", "backend", "platform")
      Body   = @"
## Goal
Prepare the runtime for safe write-side execution.

## Dependencies
- [Epic] Controlled Write And Approval

## Acceptance Criteria
- [ ] Write-side execution does not target arbitrary live directories
- [ ] Workspace allocation is tied to task lifecycle
- [ ] Medium/high write policy defaults are explicit
"@
    }
    @{
      Title  = "[Task] Implement approval service and write-side tool governance"
      Labels = @("task", "phase:2-write", "backend", "security")
      Body   = @"
## Goal
Require approval and rollback-aware policy before risky writes execute.

## Dependencies
- [Epic] Controlled Write And Approval

## Acceptance Criteria
- [ ] Approval supports create / approve / reject / revoke / timeout
- [ ] Approval-required writes pause before execution
- [ ] Risky writes carry rollback references
"@
    }
    @{
      Title  = "[Task] Implement quick/full verification and delivery handoff"
      Labels = @("task", "phase:3-assurance", "backend", "eval")
      Body   = @"
## Goal
Make governed execution produce validated delivery artifacts.

## Dependencies
- [Epic] Delivery Assurance And Replay

## Acceptance Criteria
- [ ] Canonical quick/full verification order is enforced
- [ ] Completed tasks produce a handoff bundle
- [ ] Replay references are present for failed or interrupted paths
"@
    }
    @{
      Title  = "[Task] Add eval baseline, second-repo pilot, and minimum operator hardening"
      Labels = @("task", "phase:4-hardening", "eval", "platform", "frontend", "devops")
      Body   = @"
## Goal
Prove the kernel is measurable, reusable, and operable after the first trial loop succeeds.

## Dependencies
- [Epic] Second-Repo Reuse And Operator Hardening

## Acceptance Criteria
- [ ] Minimum eval suites and required trace fields exist
- [ ] Second repo passes compatibility validation without a kernel fork
- [ ] Minimum approval/evidence console and runbooks exist for repeated use
"@
    }
  )

  foreach ($task in $tasks) {
    New-RoadmapIssue -Title $task.Title -Labels $task.Labels -Body $task.Body
  }
}
