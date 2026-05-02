param(
  [Parameter(Mandatory = $true)]
  [string]$Repo,

  [string]$Milestone = "90-Day Agent Platform MVP",

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
  @{ Name = "phase:1-foundation"; Color = "BFDADC"; Description = "Foundation phase" }
  @{ Name = "phase:2-execution"; Color = "FBCA04"; Description = "Execution phase" }
  @{ Name = "phase:3-hardening"; Color = "D93F0B"; Description = "Hardening phase" }
  @{ Name = "backend"; Color = "0052CC"; Description = "Backend work" }
  @{ Name = "frontend"; Color = "C5DEF5"; Description = "Frontend work" }
  @{ Name = "platform"; Color = "6F42C1"; Description = "Platform work" }
  @{ Name = "security"; Color = "B60205"; Description = "Security and policy" }
  @{ Name = "devops"; Color = "0366D6"; Description = "Infra and operations" }
  @{ Name = "eval"; Color = "5319E7"; Description = "Eval and validation" }
)

foreach ($label in $labels) {
  Ensure-Label -Name $label.Name -Color $label.Color -Description $label.Description
}

Ensure-Milestone

$initiativeBody = @"
## Goal
Deliver an MVP for a governed agent runtime in 90 days.

## Success Criteria
- [ ] Single-agent baseline is operational
- [ ] High-risk actions require approval
- [ ] Task execution supports pause, resume, timeout, retry, and rollback
- [ ] Key paths are auditable and traceable
- [ ] Minimal eval / regression / safety coverage exists
- [ ] Canary and rollback runbooks are complete

## In Scope
- Control Plane v1
- Policy / Risk / Approval v1
- Durable Workflow Runtime v1
- Single-Agent Baseline v1
- Tool Runner / Sandbox v1
- Validation / Evidence / Console v1
- Production Hardening v1

## Out of Scope
- Autonomous multi-agent negotiation
- Full A2A production rollout
- Automatic policy promotion
- Automatic rule modification
- Multi-region active-active deployment
- Standalone memory microservice
"@

New-RoadmapIssue -Title "[Initiative] 90-Day Agent Platform MVP" -Labels @("initiative", "platform") -Body $initiativeBody

$epics = @(
  @{
    Title  = "[Epic] Repo Bootstrap & Dev Foundation"
    Labels = @("epic", "phase:1-foundation", "platform")
    Body   = @"
## Goal
Establish the monorepo, shared tooling, CI baseline, and ADR skeleton.

## Scope
- Initialize apps / packages / infra / schemas / tests / docs
- Initialize Python and frontend workspaces
- Add lint / unit test / schema check CI
- Add ADR template and dev scripts

## Dependencies
- None

## Acceptance Criteria
- [ ] New contributor can start local environment within 30 minutes
- [ ] CI runs baseline checks
- [ ] Monorepo structure is documented
- [ ] ADR template is usable
"@
  }
  @{
    Title  = "[Epic] Contracts & Domain Model v1"
    Labels = @("epic", "phase:1-foundation", "backend")
    Body   = @"
## Goal
Define the first version of core object models, schemas, and audit fields.

## Scope
- Goal / Task / Plan / ApprovalRequest / RiskEvent
- ToolCall / Evidence / ValidationResult / RollbackPoint
- JSON Schema / OpenAPI / Protobuf v1
- Object states and immutable fields

## Dependencies
- [Epic] Repo Bootstrap & Dev Foundation

## Acceptance Criteria
- [ ] Core domain model v1 is complete
- [ ] API and event schema validation is available
- [ ] Audit fields are standardized
- [ ] State enums for key objects are fixed
"@
  }
  @{
    Title  = "[Epic] Infra Foundation"
    Labels = @("epic", "phase:1-foundation", "devops", "platform")
    Body   = @"
## Goal
Provision PostgreSQL, Redis, Temporal, OTel, and local object storage for development.

## Scope
- Local dev stack
- Config and secret loading
- Migration flow
- Tracing / metrics / logging bootstrap

## Dependencies
- [Epic] Repo Bootstrap & Dev Foundation

## Acceptance Criteria
- [ ] PostgreSQL / Redis / Temporal / OTel run locally
- [ ] Services emit traces and logs
- [ ] Migrations are repeatable and reversible
- [ ] Config and secret loading are documented
"@
  }
  @{
    Title  = "[Epic] Control Plane v1"
    Labels = @("epic", "phase:1-foundation", "backend", "platform")
    Body   = @"
## Goal
Create the initial gateway, control plane, registry, and audit write path.

## Scope
- API gateway
- Control plane service
- Auth and tenant context
- Initial registry
- Audit / evidence write API

## Dependencies
- [Epic] Contracts & Domain Model v1
- [Epic] Infra Foundation

## Acceptance Criteria
- [ ] Goal / Task CRUD works
- [ ] API calls write audit records
- [ ] Gateway and control plane are separated
- [ ] Registry can record tool / policy / prompt metadata
"@
  }
  @{
    Title  = "[Epic] Policy, Risk & Approval v1"
    Labels = @("epic", "phase:1-foundation", "security", "backend")
    Body   = @"
## Goal
Establish deterministic permission, risk, approval, and blocking flows.

## Scope
- OPA integration
- Permission levels
- Risk levels
- Tool side-effect catalog
- Approval state machine
- Approval notifications and audit

## Dependencies
- [Epic] Control Plane v1

## Acceptance Criteria
- [ ] Permission and risk checks run before tool execution
- [ ] High-risk operations are blocked by default
- [ ] Approval supports create / approve / reject / revoke / timeout
- [ ] Approval results drive task state transitions
"@
  }
  @{
    Title  = "[Epic] Durable Workflow Runtime v1"
    Labels = @("epic", "phase:2-execution", "backend", "platform")
    Body   = @"
## Goal
Implement durable task orchestration with pause, resume, timeout, retry, and compensation hooks.

## Scope
- Workflow worker
- Main task state machine
- Pause / resume / timeout / retry
- Approval checkpoints
- Compensation hooks

## Dependencies
- [Epic] Policy, Risk & Approval v1

## Acceptance Criteria
- [ ] Main workflow runs end-to-end
- [ ] Approval pauses and resumes workflows
- [ ] Failures enter compensation or human handoff
- [ ] Workflow integration tests run
"@
  }
  @{
    Title  = "[Epic] Single-Agent Baseline v1"
    Labels = @("epic", "phase:2-execution", "backend")
    Body   = @"
## Goal
Run a governed single-agent baseline inside the workflow shell.

## Scope
- Agent worker
- Model invocation and context assembly
- Limited reasoning capabilities
- Token / cost / time budgets
- Typed input / output schema

## Dependencies
- [Epic] Durable Workflow Runtime v1

## Acceptance Criteria
- [ ] Agent runs inside workflows
- [ ] Agent cannot bypass policy to call high-risk tools
- [ ] Budget overflow stops execution and records evidence
- [ ] Input and output satisfy schema validation
"@
  }
  @{
    Title  = "[Epic] Tool Runner & Sandbox v1"
    Labels = @("epic", "phase:2-execution", "backend", "security")
    Body   = @"
## Goal
Provide a unified tool execution layer and restricted sandbox execution.

## Scope
- Tool SDK
- First 3-5 tool adapters
- Schema validation
- Idempotency / timeout / retry budget
- Sandbox runner
- Rollback point registration

## Dependencies
- [Epic] Single-Agent Baseline v1

## Acceptance Criteria
- [ ] At least 3 high-value tools are integrated
- [ ] All tool calls go through the Tool Runner
- [ ] At least 2 write actions support approval before execution
- [ ] High-risk writes register rollback points
- [ ] Sandbox failures do not contaminate the control plane
"@
  }
  @{
    Title  = "[Epic] Validation, Evidence & Console v1"
    Labels = @("epic", "phase:3-hardening", "frontend", "eval")
    Body   = @"
## Goal
Establish the initial eval, evidence, and console feedback loop.

## Scope
- Eval worker
- Final outcome / trajectory / regression / safety eval
- Console Web v1
- Approval, task detail, evidence, and replay pages
- Prompt / policy / tool version visibility

## Dependencies
- [Epic] Tool Runner & Sandbox v1

## Acceptance Criteria
- [ ] Minimal eval suite runs on key changes
- [ ] Each task exposes trace, evidence, and audit
- [ ] Admin completes approvals in the web console
- [ ] Failed tasks can be replayed and handed off
"@
  }
  @{
    Title  = "[Epic] Production Hardening v1"
    Labels = @("epic", "phase:3-hardening", "devops", "security")
    Body   = @"
## Goal
Complete async wiring, worker pools, canary rollout, drills, and runbooks.

## Scope
- NATS JetStream for non-critical async events
- Worker pools and rate limiting
- Canary rollout
- Chaos drill
- Backup / restore drill
- Minimal red-team scenarios
- Production and rollback runbooks

## Dependencies
- [Epic] Validation, Evidence & Console v1

## Acceptance Criteria
- [ ] At least one restore drill completes
- [ ] At least one canary rollout drill completes
- [ ] Runbooks cover key failure modes
- [ ] The system meets the minimum canary gate
"@
  }
)

foreach ($epic in $epics) {
  New-RoadmapIssue -Title $epic.Title -Labels $epic.Labels -Body $epic.Body
}

if (-not $SkipTasks) {
  $tasks = @(
    @{
      Title  = "[Task] Initialize monorepo structure and shared tooling"
      Labels = @("task", "phase:1-foundation", "platform")
      Body   = @"
## Goal
Initialize the monorepo structure and shared tooling.

## Dependencies
- [Epic] Repo Bootstrap & Dev Foundation

## Acceptance Criteria
- [ ] apps / packages / infra / schemas / tests / docs directories exist
- [ ] Python and frontend workspaces run locally
- [ ] Shared lint / test commands are available
- [ ] README includes local startup steps
"@
    }
    @{
      Title  = "[Task] Add CI for lint, unit test, and schema validation"
      Labels = @("task", "phase:1-foundation", "platform")
      Body   = @"
## Goal
Establish the minimum CI quality gate.

## Dependencies
- [Epic] Repo Bootstrap & Dev Foundation

## Acceptance Criteria
- [ ] Lint job runs
- [ ] Unit test job runs
- [ ] Schema validation job runs
- [ ] Pull requests trigger baseline checks
"@
    }
    @{
      Title  = "[Task] Define Goal, Task, Plan, ApprovalRequest schemas"
      Labels = @("task", "phase:1-foundation", "backend")
      Body   = @"
## Goal
Define the first version of the core business schemas.

## Dependencies
- [Epic] Contracts & Domain Model v1

## Acceptance Criteria
- [ ] Goal / Task / Plan / ApprovalRequest schemas are defined
- [ ] State, version, and owner fields are present
- [ ] Schema validation passes
- [ ] Field semantics are documented
"@
    }
    @{
      Title  = "[Task] Provision local PostgreSQL, Redis, Temporal, and OTel stack"
      Labels = @("task", "phase:1-foundation", "devops", "platform")
      Body   = @"
## Goal
Provide the complete local development infrastructure stack.

## Dependencies
- [Epic] Infra Foundation

## Acceptance Criteria
- [ ] PostgreSQL / Redis / Temporal / OTel run locally
- [ ] One test request appears in tracing
- [ ] Startup scripts are repeatable
- [ ] Environment setup is documented
"@
    }
    @{
      Title  = "[Task] Create api-gateway skeleton with auth and tenant context"
      Labels = @("task", "phase:1-foundation", "backend", "platform")
      Body   = @"
## Goal
Create the unified entry point with auth and tenant context.

## Dependencies
- [Epic] Control Plane v1

## Acceptance Criteria
- [ ] API gateway skeleton exists
- [ ] Auth middleware runs
- [ ] Tenant context is injected
- [ ] Request logs include correlation IDs
"@
    }
    @{
      Title  = "[Task] Integrate OPA for permission and risk checks"
      Labels = @("task", "phase:1-foundation", "security", "backend")
      Body   = @"
## Goal
Move permission and risk checks into the policy engine.

## Dependencies
- [Epic] Policy, Risk & Approval v1

## Acceptance Criteria
- [ ] OPA integration works
- [ ] At least one permission policy and one risk policy are active
- [ ] Unauthorized writes are blocked
- [ ] Policy decisions are audited
"@
    }
    @{
      Title  = "[Task] Implement approval state machine and notification flow"
      Labels = @("task", "phase:1-foundation", "backend", "security")
      Body   = @"
## Goal
Implement the approval loop and connect it to task state updates.

## Dependencies
- [Epic] Policy, Risk & Approval v1

## Acceptance Criteria
- [ ] Create / approve / reject / revoke / timeout are supported
- [ ] Notification flow works
- [ ] Approval results update control-plane state
- [ ] Approval lifecycle is auditable
"@
    }
    @{
      Title  = "[Task] Implement Temporal workflow for task lifecycle"
      Labels = @("task", "phase:2-execution", "backend", "platform")
      Body   = @"
## Goal
Implement the main workflow for task lifecycle management.

## Dependencies
- [Epic] Durable Workflow Runtime v1

## Acceptance Criteria
- [ ] Main workflow runs
- [ ] Pause / resume / timeout / retry are supported
- [ ] Approval nodes interrupt and resume the workflow
- [ ] Failures can enter compensation or human handoff
"@
    }
  )

  foreach ($task in $tasks) {
    New-RoadmapIssue -Title $task.Title -Labels $task.Labels -Body $task.Body
  }
}
