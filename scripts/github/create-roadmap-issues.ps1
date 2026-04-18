param(
  [string]$Repo,

  [string]$Milestone = "Governed AI Coding Runtime Full Lifecycle",

  [string]$Assignee = "@me",

  [switch]$SkipTasks,

  [switch]$ValidateOnly,

  [string]$IssueId,

  [string]$EpicId,

  [switch]$Initiative,

  [switch]$RenderAll
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Parse-InlineArray {
  param([string]$Value)

  $trimmed = $Value.Trim()
  if ($trimmed -eq '[]') {
    return @()
  }

  if ($trimmed -notmatch '^\[(.*)\]$') {
    throw "Unsupported inline array format: $Value"
  }

  $inner = $Matches[1].Trim()
  if ([string]::IsNullOrWhiteSpace($inner)) {
    return @()
  }

  return @(
    $inner.Split(',') |
      ForEach-Object { $_.Trim() } |
      Where-Object { $_ -ne '' } |
      ForEach-Object {
        if ($_ -match '^"(.*)"$') {
          $Matches[1]
        }
        elseif ($_ -match '^\d+$') {
          [int]$_
        }
        else {
          $_
        }
      }
  )
}

function Get-IssueSeeds {
  $path = Join-Path (Get-Location) "docs/backlog/issue-seeds.yaml"
  if (-not (Test-Path $path)) {
    throw "Issue seeds file not found: $path"
  }

  $content = Get-Content -Path $path
  $version = $null
  $issues = [System.Collections.Generic.List[object]]::new()
  $current = $null

  foreach ($line in $content) {
    if ($line -match '^issue_seed_version:\s+"([^"]+)"\s*$') {
      $version = $Matches[1]
      continue
    }

    if ($line -match '^\s*-\s+id:\s+(GAP-\d+)\s*$') {
      if ($null -ne $current) {
        $issues.Add([pscustomobject]$current)
      }

      $current = [ordered]@{
        id = $Matches[1]
        title = $null
        type = $null
        blocked_by = @()
        user_stories = @()
      }
      continue
    }

    if ($null -eq $current) {
      continue
    }

    if ($line -match '^\s+title:\s+(.+?)\s*$') {
      $current.title = $Matches[1]
      continue
    }

    if ($line -match '^\s+type:\s+(.+?)\s*$') {
      $current.type = $Matches[1]
      continue
    }

    if ($line -match '^\s+blocked_by:\s+(.+?)\s*$') {
      $current.blocked_by = @(Parse-InlineArray $Matches[1])
      continue
    }

    if ($line -match '^\s+user_stories:\s+(.+?)\s*$') {
      $current.user_stories = @(Parse-InlineArray $Matches[1])
      continue
    }
  }

  if ($null -ne $current) {
    $issues.Add([pscustomobject]$current)
  }

  if ([string]::IsNullOrWhiteSpace($version)) {
    throw "Issue seed version missing from docs/backlog/issue-seeds.yaml"
  }

  foreach ($issue in $issues) {
    if ([string]::IsNullOrWhiteSpace($issue.id) -or [string]::IsNullOrWhiteSpace($issue.title) -or [string]::IsNullOrWhiteSpace($issue.type)) {
      throw "Incomplete issue seed entry detected in docs/backlog/issue-seeds.yaml"
    }
  }

  return [pscustomobject]@{
    version = $version
    issues = @($issues)
  }
}

function Get-IssueSeedMap {
  param([object]$SeedData)

  $map = @{}
  foreach ($issue in $SeedData.issues) {
    $map[$issue.id] = $issue
  }
  return $map
}

function Get-BacklogTaskMap {
  $path = Join-Path (Get-Location) "docs/backlog/issue-ready-backlog.md"
  if (-not (Test-Path $path)) {
    throw "Issue-ready backlog not found: $path"
  }

  $content = Get-Content -Path $path
  $map = @{}
  $current = $null
  $currentSection = $null

  foreach ($line in $content) {
    if ($line -match '^### (GAP-\d+) (.+)$') {
      if ($null -ne $current) {
        $map[$current.id] = [pscustomobject]$current
      }

      $current = [ordered]@{
        id = $Matches[1]
        title = $Matches[2]
        what_to_build = [System.Collections.Generic.List[string]]::new()
        acceptance = [System.Collections.Generic.List[string]]::new()
      }
      $currentSection = $null
      continue
    }

    if ($null -eq $current) {
      continue
    }

    if ($line -match '^- What to build:\s*$') {
      $currentSection = "what_to_build"
      continue
    }

    if ($line -match '^- Acceptance criteria:\s*$') {
      $currentSection = "acceptance"
      continue
    }

    if ($line -match '^### ' -or $line -match '^## ') {
      $currentSection = $null
      continue
    }

    if ($line -match '^  - (.+?)\s*$') {
      if ($currentSection -eq "what_to_build") {
        $current.what_to_build.Add($Matches[1])
      }
      elseif ($currentSection -eq "acceptance") {
        $current.acceptance.Add($Matches[1])
      }
      continue
    }

    if ($line -notmatch '^\s*$' -and $line -notmatch '^- (Type|Blocked by|User stories|Status):') {
      $currentSection = $null
    }
  }

  if ($null -ne $current) {
    $map[$current.id] = [pscustomobject]$current
  }

  return $map
}

function Get-LifecyclePlanData {
  $path = Join-Path (Get-Location) "docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md"
  if (-not (Test-Path $path)) {
    throw "Lifecycle plan not found: $path"
  }

  $content = Get-Content -Path $path
  $goal = [System.Collections.Generic.List[string]]::new()
  $completion = [System.Collections.Generic.List[string]]::new()
  $nonGoals = [System.Collections.Generic.List[string]]::new()
  $stages = @{}
  $currentStage = $null
  $currentSection = $null

  foreach ($line in $content) {
    if ($line -match '^## Goal$') {
      $currentStage = $null
      $currentSection = "goal"
      continue
    }

    if ($line -match '^## Product Shape$') {
      $currentStage = $null
      $currentSection = $null
      continue
    }

    if ($line -match '^### Non-Goals$') {
      $currentStage = $null
      $currentSection = "non_goals"
      continue
    }

    if ($line -match '^## Lifecycle Stages$') {
      $currentStage = $null
      $currentSection = $null
      continue
    }

    if ($line -match '^### Stage \d+: (.+)$') {
      $stageName = $Matches[1]
      $currentStage = [ordered]@{
        name = $stageName
        status = [System.Collections.Generic.List[string]]::new()
        purpose = [System.Collections.Generic.List[string]]::new()
        required_outputs = [System.Collections.Generic.List[string]]::new()
        exit_check = [System.Collections.Generic.List[string]]::new()
      }
      $stages[$stageName] = [pscustomobject]$currentStage
      $currentSection = $null
      continue
    }

    if ($line -match '^\*\*Purpose\*\*$') {
      $currentSection = if ($null -ne $currentStage) { "purpose" } else { $null }
      continue
    }

    if ($line -match '^\*\*Status\*\*$') {
      $currentSection = if ($null -ne $currentStage) { "status" } else { $null }
      continue
    }

    if ($line -match '^\*\*Required outputs\*\*$') {
      $currentSection = if ($null -ne $currentStage) { "required_outputs" } else { $null }
      continue
    }

    if ($line -match '^\*\*Exit check\*\*$') {
      $currentSection = if ($null -ne $currentStage) { "exit_check" } else { $null }
      continue
    }

    if ($line -match '^## Lifecycle Completion Criteria$') {
      $currentStage = $null
      $currentSection = "completion"
      continue
    }

    if ($line -match '^## ' -or ($line -match '^### ' -and $line -notmatch '^### Stage \d+: ')) {
      $currentStage = $null
      $currentSection = $null
      continue
    }

    if ($line -match '^- (.+?)\s*$') {
      switch ($currentSection) {
        "goal" { $goal.Add($Matches[1]); continue }
        "non_goals" { $nonGoals.Add($Matches[1]); continue }
        "completion" { $completion.Add($Matches[1]); continue }
        "status" { $currentStage.status.Add($Matches[1]); continue }
        "purpose" { $currentStage.purpose.Add($Matches[1]); continue }
        "required_outputs" { $currentStage.required_outputs.Add($Matches[1]); continue }
        "exit_check" { $currentStage.exit_check.Add($Matches[1]); continue }
      }
    }
  }

  return [pscustomobject]@{
    goal = @($goal)
    completion = @($completion)
    non_goals = @($nonGoals)
    stages = $stages
  }
}

function Get-EpicDefinitions {
  return @(
    @{
      Id = "Vision"
      Title = "[Epic] Vision Alignment"
      StageName = "Vision"
      Labels = @("epic", "phase:vision", "product", "docs", "platform")
    }
    @{
      Id = "Foundation"
      Title = "[Epic] Foundation"
      StageName = "Foundation"
      Labels = @("epic", "phase:foundation", "platform", "contracts", "backend")
    }
    @{
      Id = "Full Runtime"
      Title = "[Epic] Full Runtime"
      StageName = "Full Runtime"
      Labels = @("epic", "phase:full-runtime", "platform", "backend", "frontend")
    }
    @{
      Id = "Public Usable Release"
      Title = "[Epic] Public Usable Release"
      StageName = "Public Usable Release"
      Labels = @("epic", "phase:public-release", "platform", "docs", "devops")
    }
    @{
      Id = "Maintenance Boundary"
      Title = "[Epic] Maintenance Boundary"
      StageName = "Maintenance Baseline"
      Labels = @("epic", "phase:maintenance", "platform", "docs", "product")
    }
    @{
      Id = "Interactive Session Productization"
      Title = "[Epic] Interactive Session Productization"
      StageName = "Interactive Session Productization"
      Labels = @("epic", "phase:interactive-session", "platform", "product", "docs", "frontend", "backend")
    }
  )
}

function Get-EpicDefinitionMap {
  param([object[]]$EpicDefinitions)

  $map = @{}
  foreach ($epic in $EpicDefinitions) {
    $map[$epic.Id] = $epic
    if ($epic.StageName -ne $epic.Id) {
      $map[$epic.StageName] = $epic
    }
  }
  return $map
}

function Format-SeedMetadataBlock {
  param([object]$Seed)

  $blockedBy = if ($Seed.blocked_by.Count -gt 0) {
    $Seed.blocked_by -join ", "
  }
  else {
    "None"
  }

  $userStories = if ($Seed.user_stories.Count -gt 0) {
    ($Seed.user_stories | ForEach-Object { "$_" }) -join ", "
  }
  else {
    "None"
  }

  return @"

## Seed Metadata
- Issue ID: $($Seed.id)
- Seed type: $($Seed.type)
- Blocked by: $blockedBy
- User stories: $userStories
"@
}

function Render-TaskIssueBody {
  param(
    [object]$Seed,
    [object]$BacklogTask
  )

  if ($null -eq $BacklogTask) {
    throw "Missing backlog section for $($Seed.id)"
  }

  if ($BacklogTask.what_to_build.Count -eq 0) {
    throw "Backlog section $($Seed.id) is missing 'What to build' bullets"
  }

  if ($BacklogTask.acceptance.Count -eq 0) {
    throw "Backlog section $($Seed.id) is missing acceptance criteria"
  }

  $goal = "Deliver $($Seed.title)."
  $dependencies = if ($Seed.blocked_by.Count -gt 0) {
    @($Seed.blocked_by | ForEach-Object { "- $_" }) -join "`n"
  }
  else {
    "- None"
  }

  $scope = @($BacklogTask.what_to_build | ForEach-Object { "- $_" }) -join "`n"
  $acceptance = @($BacklogTask.acceptance | ForEach-Object { "- $_" }) -join "`n"

  return @"
## Goal
$goal

## Scope
$scope

## Dependencies
$dependencies

## Acceptance Criteria
$acceptance
"@ + (Format-SeedMetadataBlock -Seed $Seed)
}

function Render-EpicIssueBody {
  param(
    [string]$EpicId,
    [object]$Stage
  )

  if ($null -eq $Stage) {
    throw "Missing lifecycle stage for epic '$EpicId'"
  }

  if ($Stage.purpose.Count -eq 0) {
    throw "Lifecycle stage '$EpicId' is missing purpose"
  }

  if ($Stage.required_outputs.Count -eq 0 -and $Stage.status.Count -eq 0) {
    throw "Lifecycle stage '$EpicId' is missing required outputs or status"
  }

  if ($Stage.exit_check.Count -eq 0 -and $Stage.status.Count -eq 0) {
    throw "Lifecycle stage '$EpicId' is missing exit check or status"
  }

  $goal = @($Stage.purpose | ForEach-Object { "- $_" }) -join "`n"
  $scopeItems = if ($Stage.required_outputs.Count -gt 0) { $Stage.required_outputs } else { $Stage.status }
  $acceptanceItems = if ($Stage.exit_check.Count -gt 0) { $Stage.exit_check } else { $Stage.status }
  $scope = @($scopeItems | ForEach-Object { "- $_" }) -join "`n"
  $acceptance = @($acceptanceItems | ForEach-Object { "- $_" }) -join "`n"

  return @"
## Goal
$goal

## Scope
$scope

## Acceptance Criteria
$acceptance
"@
}

function Render-InitiativeBody {
  param([object]$LifecyclePlan)

  if ($LifecyclePlan.goal.Count -eq 0 -or $LifecyclePlan.completion.Count -eq 0) {
    throw "Lifecycle plan is missing goal or completion criteria"
  }

  $goal = @($LifecyclePlan.goal | ForEach-Object { "- $_" }) -join "`n"
  $success = @($LifecyclePlan.completion | ForEach-Object { "- $_" }) -join "`n"
  $nonGoals = if ($LifecyclePlan.non_goals.Count -gt 0) {
    @($LifecyclePlan.non_goals | ForEach-Object { "- $_" }) -join "`n"
  }
  else {
    "- None"
  }

  return @"
## Goal
$goal

## Success Criteria
$success

## Out Of Scope
$nonGoals
"@
}

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

if (-not $ValidateOnly -and [string]::IsNullOrWhiteSpace($Repo)) {
  throw "Parameter Repo is required unless -ValidateOnly is used."
}

$seedData = Get-IssueSeeds
$seedMap = Get-IssueSeedMap -SeedData $seedData
$backlogTaskMap = Get-BacklogTaskMap
$lifecyclePlan = Get-LifecyclePlanData
$epicDefinitions = @(Get-EpicDefinitions)
$epicDefinitionMap = Get-EpicDefinitionMap -EpicDefinitions $epicDefinitions

if ($ValidateOnly) {
  if ($RenderAll) {
    $renderedTasks = 0
    foreach ($issue in $seedData.issues) {
      [void](Render-TaskIssueBody -Seed $issue -BacklogTask $backlogTaskMap[$issue.id])
      $renderedTasks += 1
    }

    $renderedEpics = 0
    foreach ($epicDefinition in $epicDefinitions) {
      [void](Render-EpicIssueBody -EpicId $epicDefinition.Id -Stage $lifecyclePlan.stages[$epicDefinition.StageName])
      $renderedEpics += 1
    }

    [void](Render-InitiativeBody -LifecyclePlan $lifecyclePlan)

    [pscustomobject]@{
      issue_seed_version = $seedData.version
      rendered_tasks = $renderedTasks
      rendered_epics = $renderedEpics
      rendered_initiative = $true
    } | ConvertTo-Json -Compress
    exit 0
  }

  if ($Initiative) {
    [pscustomobject]@{
      title = "[Initiative] Governed AI Coding Runtime Full Functional Lifecycle"
      body = (Render-InitiativeBody -LifecyclePlan $lifecyclePlan)
    } | ConvertTo-Json -Compress
    exit 0
  }

  if (-not [string]::IsNullOrWhiteSpace($EpicId)) {
    if (-not $epicDefinitionMap.ContainsKey($EpicId)) {
      throw "Epic definition not found for $EpicId"
    }

    $epicDefinition = $epicDefinitionMap[$EpicId]
    $body = Render-EpicIssueBody -EpicId $epicDefinition.Id -Stage $lifecyclePlan.stages[$epicDefinition.StageName]
    [pscustomobject]@{
      epic_id = $epicDefinition.Id
      title = $epicDefinition.Title
      body = $body
    } | ConvertTo-Json -Compress
    exit 0
  }

  if (-not [string]::IsNullOrWhiteSpace($IssueId)) {
    if (-not $seedMap.ContainsKey($IssueId)) {
      throw "Issue seed not found for $IssueId"
    }

    $seed = $seedMap[$IssueId]
    $title = if ($IssueId -match '^GAP-0(1[8-9]|2\d|3\d)$') { "[Task] $($seed.title)" } else { $seed.title }
    $body = Render-TaskIssueBody -Seed $seed -BacklogTask $backlogTaskMap[$IssueId]

    [pscustomobject]@{
      issue_id = $IssueId
      title = $title
      body = $body
    } | ConvertTo-Json -Compress
    exit 0
  }

  $gap027 = $seedMap["GAP-027"]
  [pscustomobject]@{
    issue_seed_version = $seedData.version
    issue_count = $seedData.issues.Count
    first_issue_id = $seedData.issues[0].id
    gap_027_title = $gap027.title
  } | ConvertTo-Json -Compress
  exit 0
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

$initiativeBody = Render-InitiativeBody -LifecyclePlan $lifecyclePlan

New-RoadmapIssue -Title "[Initiative] Governed AI Coding Runtime Full Functional Lifecycle" -Labels @("initiative", "platform") -Body $initiativeBody

foreach ($epicDefinition in $epicDefinitions) {
  $body = Render-EpicIssueBody -EpicId $epicDefinition.Id -Stage $lifecyclePlan.stages[$epicDefinition.StageName]
  New-RoadmapIssue -Title $epicDefinition.Title -Labels $epicDefinition.Labels -Body $body
}

if (-not $SkipTasks) {
  $tasks = @(
    @{
      IssueId = "GAP-018"
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
      IssueId = "GAP-019"
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
      IssueId = "GAP-020"
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
      IssueId = "GAP-021"
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
      IssueId = "GAP-022"
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
      IssueId = "GAP-023"
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
      IssueId = "GAP-024"
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
      IssueId = "GAP-025"
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
      IssueId = "GAP-027"
      Labels = @("task", "phase:full-runtime", "frontend", "platform", "backend")
      Body   = @"
## Goal
Give operators a control-plane surface for tasks, approvals, evidence, replay, and runtime status.

## Dependencies
- [Epic] Full Runtime

## Acceptance Criteria
- [ ] operators can inspect tasks, approvals, evidence, and replay without raw log digging
- [ ] runtime health and task query surfaces are stable
- [ ] the surface remains control-plane focused
- [ ] the first delivery may be CLI-first as long as it keeps a stable read model for a later UI
"@
    }
    @{
      IssueId = "GAP-029"
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
      IssueId = "GAP-033"
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
    if (-not $seedMap.ContainsKey($task.IssueId)) {
      throw "Task issue seed not found for $($task.IssueId)"
    }

    $seed = $seedMap[$task.IssueId]
    $title = "[Task] $($seed.title)"
    $body = Render-TaskIssueBody -Seed $seed -BacklogTask $backlogTaskMap[$task.IssueId]

    New-RoadmapIssue -Title $title -Labels $task.Labels -Body $body
  }
}
