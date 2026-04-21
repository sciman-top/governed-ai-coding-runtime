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
        status = ""
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

    if ($line -match '^- Status:\s*(.+?)\s*$') {
      $current.status = $Matches[1]
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

function Test-BacklogTaskComplete {
  param([object]$BacklogTask)

  if ($null -eq $BacklogTask) {
    return $false
  }

  return $BacklogTask.status -match '^complete\b'
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

function Get-DirectRoadmapPhaseData {
  $path = Join-Path (Get-Location) "docs/roadmap/direct-to-hybrid-final-state-roadmap.md"
  if (-not (Test-Path $path)) {
    throw "Direct roadmap not found: $path"
  }

  $content = Get-Content -Path $path
  $phases = @{}
  $currentPhase = $null
  $currentSection = $null

  foreach ($line in $content) {
    if ($line -match '^## Phase (\d+): (.+)$') {
      $phaseName = "Phase $($Matches[1]): $($Matches[2])"
      $currentPhase = [ordered]@{
        name = $phaseName
        status = [System.Collections.Generic.List[string]]::new()
        goal = [System.Collections.Generic.List[string]]::new()
        scope = [System.Collections.Generic.List[string]]::new()
        exit_criteria = [System.Collections.Generic.List[string]]::new()
      }
      $phases[$phaseName] = [pscustomobject]$currentPhase
      $currentSection = $null
      continue
    }

    if ($null -eq $currentPhase) {
      continue
    }

    if ($line -match '^### Status$') {
      $currentSection = "status"
      continue
    }

    if ($line -match '^### Goal$') {
      $currentSection = "goal"
      continue
    }

    if ($line -match '^### Scope$') {
      $currentSection = "scope"
      continue
    }

    if ($line -match '^### Exit Criteria$') {
      $currentSection = "exit_criteria"
      continue
    }

    if ($line -match '^## ' -or $line -match '^### ') {
      $currentSection = $null
      continue
    }

    if ([string]::IsNullOrWhiteSpace($line) -or $null -eq $currentSection) {
      continue
    }

    if ($line -match '^- (.+?)\s*$') {
      $currentPhase[$currentSection].Add($Matches[1])
      continue
    }

    $trimmed = $line.Trim()
    if (-not [string]::IsNullOrWhiteSpace($trimmed)) {
      $currentPhase[$currentSection].Add($trimmed)
    }
  }

  return $phases
}

function Get-GovernanceRoadmapPhaseData {
  $path = Join-Path (Get-Location) "docs/roadmap/governance-optimization-lane-roadmap.md"
  if (-not (Test-Path $path)) {
    throw "Governance roadmap not found: $path"
  }

  $content = Get-Content -Path $path
  $phases = @{}
  $currentPhase = $null
  $currentSection = $null

  foreach ($line in $content) {
    if ($line -match '^## Phase (\d+): (.+)$') {
      $phaseName = "Phase $($Matches[1]): $($Matches[2])"
      $currentPhase = [ordered]@{
        name = $phaseName
        status = [System.Collections.Generic.List[string]]::new()
        goal = [System.Collections.Generic.List[string]]::new()
        scope = [System.Collections.Generic.List[string]]::new()
        exit_criteria = [System.Collections.Generic.List[string]]::new()
      }
      $phases[$phaseName] = [pscustomobject]$currentPhase
      $currentSection = $null
      continue
    }

    if ($null -eq $currentPhase) {
      continue
    }

    if ($line -match '^### Status$') {
      $currentSection = "status"
      continue
    }

    if ($line -match '^### Goal$') {
      $currentSection = "goal"
      continue
    }

    if ($line -match '^### Scope$') {
      $currentSection = "scope"
      continue
    }

    if ($line -match '^### Exit Criteria$') {
      $currentSection = "exit_criteria"
      continue
    }

    if ($line -match '^## ' -or $line -match '^### ') {
      $currentSection = $null
      continue
    }

    if ([string]::IsNullOrWhiteSpace($line) -or $null -eq $currentSection) {
      continue
    }

    if ($line -match '^- (.+?)\s*$') {
      $currentPhase[$currentSection].Add($Matches[1])
      continue
    }

    $trimmed = $line.Trim()
    if (-not [string]::IsNullOrWhiteSpace($trimmed)) {
      $currentPhase[$currentSection].Add($trimmed)
    }
  }

  return $phases
}

function Get-EpicDefinitions {
  return @(
    @{
      Id = "Vision"
      Title = "[Epic] Vision Alignment"
      StageName = "Vision"
      Source = "lifecycle"
      Labels = @("epic", "phase:vision", "product", "docs", "platform")
    }
    @{
      Id = "Foundation"
      Title = "[Epic] Foundation"
      StageName = "Foundation"
      Source = "lifecycle"
      Labels = @("epic", "phase:foundation", "platform", "contracts", "backend")
    }
    @{
      Id = "Full Runtime"
      Title = "[Epic] Full Runtime"
      StageName = "Full Runtime"
      Source = "lifecycle"
      Labels = @("epic", "phase:full-runtime", "platform", "backend", "frontend")
    }
    @{
      Id = "Public Usable Release"
      Title = "[Epic] Public Usable Release"
      StageName = "Public Usable Release"
      Source = "lifecycle"
      Labels = @("epic", "phase:public-release", "platform", "docs", "devops")
    }
    @{
      Id = "Maintenance Boundary"
      Title = "[Epic] Maintenance Boundary"
      StageName = "Maintenance Baseline"
      Source = "lifecycle"
      Labels = @("epic", "phase:maintenance", "platform", "docs", "product")
    }
    @{
      Id = "Interactive Session Productization"
      Title = "[Epic] Interactive Session Productization"
      StageName = "Interactive Session Productization"
      Source = "lifecycle"
      Labels = @("epic", "phase:interactive-session", "platform", "product", "docs", "frontend", "backend")
    }
    @{
      Id = "Strategy Alignment Gates"
      Title = "[Epic] Strategy Alignment Gates"
      StageName = "Strategy Alignment Gates"
      Source = "lifecycle"
      Labels = @("epic", "phase:strategy-alignment", "platform", "product", "docs", "contracts")
    }
    @{
      Id = "Phase 0"
      Title = "[Epic] Phase 0 Canonical Re-Baseline"
      RoadmapPhaseName = "Phase 0: Canonical Re-Baseline"
      Source = "roadmap"
      Labels = @("epic", "phase:rebaseline", "platform", "docs", "product")
    }
    @{
      Id = "Phase 1"
      Title = "[Epic] Phase 1 Governed Execution Surface"
      RoadmapPhaseName = "Phase 1: Close The Governed Execution Surface"
      Source = "roadmap"
      Labels = @("epic", "phase:governed-execution", "platform", "backend", "product")
    }
    @{
      Id = "Phase 2"
      Title = "[Epic] Phase 2 Live Host Adapter Reality"
      RoadmapPhaseName = "Phase 2: Close Live Host Adapter Reality"
      Source = "roadmap"
      Labels = @("epic", "phase:live-adapter", "platform", "backend", "product", "contracts")
    }
    @{
      Id = "Phase 3"
      Title = "[Epic] Phase 3 Multi-Repo And Machine-Local Sidecar Reality"
      RoadmapPhaseName = "Phase 3: Close Real Multi-Repo And Machine-Local Sidecar Reality"
      Source = "roadmap"
      Labels = @("epic", "phase:multi-repo-sidecar", "platform", "backend", "product", "docs")
    }
    @{
      Id = "Phase 4"
      Title = "[Epic] Phase 4 Service-Shaped Runtime Extraction"
      RoadmapPhaseName = "Phase 4: Extract Service-Shaped Runtime"
      Source = "roadmap"
      Labels = @("epic", "phase:service-extraction", "platform", "backend", "devops")
    }
    @{
      Id = "Phase 5"
      Title = "[Epic] Phase 5 Hardening And Closeout"
      RoadmapPhaseName = "Phase 5: Hardening And Operational Completion"
      Source = "roadmap"
      Labels = @("epic", "phase:hardening-closeout", "platform", "backend", "docs", "product")
    }
    @{
      Id = "Phase 6"
      Title = "[Epic] Phase 6 Governance Optimization Lane"
      RoadmapPhaseName = "Phase 6: Governance Optimization Lane"
      Source = "governance_roadmap"
      Labels = @("epic", "phase:governance-optimization", "platform", "docs", "product")
    }
  )
}

function Get-EpicDefinitionMap {
  param([object[]]$EpicDefinitions)

  $map = @{}
  foreach ($epic in $EpicDefinitions) {
    $map[$epic.Id] = $epic
    if ($epic.PSObject.Properties.Name -contains "StageName" -and $epic.StageName -ne $epic.Id) {
      $map[$epic.StageName] = $epic
    }
    if ($epic.PSObject.Properties.Name -contains "RoadmapPhaseName" -and $epic.RoadmapPhaseName -ne $epic.Id) {
      $map[$epic.RoadmapPhaseName] = $epic
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

function Render-RoadmapEpicIssueBody {
  param(
    [string]$EpicId,
    [object]$Phase
  )

  if ($null -eq $Phase) {
    throw "Missing roadmap phase for epic '$EpicId'"
  }

  if ($Phase.goal.Count -eq 0) {
    throw "Roadmap phase '$EpicId' is missing goal"
  }

  if ($Phase.scope.Count -eq 0) {
    throw "Roadmap phase '$EpicId' is missing scope"
  }

  if ($Phase.exit_criteria.Count -eq 0) {
    throw "Roadmap phase '$EpicId' is missing exit criteria"
  }

  $statusBlock = ""
  if ($Phase.status.Count -gt 0) {
    $statusBlock = @"
## Status
$( @($Phase.status | ForEach-Object { "- $_" }) -join "`n" )

"@
  }

  $goal = @($Phase.goal | ForEach-Object { "- $_" }) -join "`n"
  $scope = @($Phase.scope | ForEach-Object { "- $_" }) -join "`n"
  $acceptance = @($Phase.exit_criteria | ForEach-Object { "- $_" }) -join "`n"

  return @"
$statusBlock## Goal
$goal

## Scope
$scope

## Acceptance Criteria
$acceptance
"@
}

function Get-EpicBody {
  param(
    [object]$EpicDefinition,
    [object]$LifecyclePlan,
    [hashtable]$DirectRoadmapPhases,
    [hashtable]$GovernanceRoadmapPhases
  )

  if ($EpicDefinition.Source -eq "roadmap") {
    return Render-RoadmapEpicIssueBody -EpicId $EpicDefinition.Id -Phase $DirectRoadmapPhases[$EpicDefinition.RoadmapPhaseName]
  }

  if ($EpicDefinition.Source -eq "governance_roadmap") {
    return Render-RoadmapEpicIssueBody -EpicId $EpicDefinition.Id -Phase $GovernanceRoadmapPhases[$EpicDefinition.RoadmapPhaseName]
  }

  return Render-EpicIssueBody -EpicId $EpicDefinition.Id -Stage $LifecyclePlan.stages[$EpicDefinition.StageName]
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

function Get-TaskLabels {
  param([string]$IssueId)

  switch -Regex ($IssueId) {
    '^GAP-01[8-9]$' { return @("task", "phase:vision", "product", "docs", "platform") }
    '^GAP-02[0-3]$' { return @("task", "phase:foundation", "platform", "contracts", "backend") }
    '^GAP-02[4-8]$' { return @("task", "phase:full-runtime", "platform", "backend", "eval") }
    '^GAP-0(29|30|31|32)$' { return @("task", "phase:public-release", "platform", "docs", "devops") }
    '^GAP-0(33|34)$' { return @("task", "phase:maintenance", "platform", "docs", "product") }
    '^GAP-0(35|36|37|38|39)$' { return @("task", "phase:interactive-session", "platform", "product", "docs") }
    '^GAP-04[0-4]$' { return @("task", "phase:strategy-alignment", "platform", "docs", "contracts") }
    '^GAP-045$' { return @("task", "phase:rebaseline", "platform", "docs", "product") }
    '^GAP-0(46|47|48|49)$' { return @("task", "phase:governed-execution", "platform", "backend", "product") }
    '^GAP-0(50|51|52)$' { return @("task", "phase:live-adapter", "platform", "backend", "product", "contracts") }
    '^GAP-0(53|54)$' { return @("task", "phase:multi-repo-sidecar", "platform", "backend", "product", "docs") }
    '^GAP-0(55|56)$' { return @("task", "phase:service-extraction", "platform", "backend", "devops") }
    '^GAP-0(57|58|59|60)$' { return @("task", "phase:hardening-closeout", "platform", "backend", "docs", "product") }
    '^GAP-0(61|62|63|64|65|66|67|68|69|70|71|72|73|74)$' { return @("task", "phase:governance-optimization", "platform", "docs", "product") }
    '^GAP-08[0-4]$' { return @("task", "phase:near-term-gap-horizon", "platform", "backend", "product") }
    default { throw "No task label mapping defined for $IssueId" }
  }
}

function Get-TaskDefinitions {
  param(
    [object[]]$IssueSeeds,
    [hashtable]$BacklogTaskMap
  )

  return @(
    foreach ($issue in $IssueSeeds) {
      if (Test-BacklogTaskComplete -BacklogTask $BacklogTaskMap[$issue.id]) {
        continue
      }

      [pscustomobject]@{
        IssueId = $issue.id
        Labels = @(Get-TaskLabels -IssueId $issue.id)
      }
    }
  )
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
$directRoadmapPhases = Get-DirectRoadmapPhaseData
$governanceRoadmapPhases = Get-GovernanceRoadmapPhaseData
$epicDefinitions = @(Get-EpicDefinitions)
$epicDefinitionMap = Get-EpicDefinitionMap -EpicDefinitions $epicDefinitions

if ($ValidateOnly) {
  $completedTaskCount = @($seedData.issues | Where-Object { Test-BacklogTaskComplete -BacklogTask $backlogTaskMap[$_.id] }).Count
  $activeTaskCount = $seedData.issues.Count - $completedTaskCount
  if ($RenderAll) {
    $renderedTasks = 0
    foreach ($issue in $seedData.issues) {
      [void](Render-TaskIssueBody -Seed $issue -BacklogTask $backlogTaskMap[$issue.id])
      $renderedTasks += 1
    }

    $renderedIssueCreationTasks = 0
    $taskDefinitions = @(Get-TaskDefinitions -IssueSeeds $seedData.issues -BacklogTaskMap $backlogTaskMap)
    foreach ($task in $taskDefinitions) {
      if (-not $seedMap.ContainsKey($task.IssueId)) {
        throw "Task issue seed not found for $($task.IssueId)"
      }

      [void](Render-TaskIssueBody -Seed $seedMap[$task.IssueId] -BacklogTask $backlogTaskMap[$task.IssueId])
      $renderedIssueCreationTasks += 1
    }

    $renderedEpics = 0
    foreach ($epicDefinition in $epicDefinitions) {
      [void](Get-EpicBody -EpicDefinition $epicDefinition -LifecyclePlan $lifecyclePlan -DirectRoadmapPhases $directRoadmapPhases -GovernanceRoadmapPhases $governanceRoadmapPhases)
      $renderedEpics += 1
    }

    [void](Render-InitiativeBody -LifecyclePlan $lifecyclePlan)

    [pscustomobject]@{
      issue_seed_version = $seedData.version
      rendered_tasks = $renderedTasks
      rendered_issue_creation_tasks = $renderedIssueCreationTasks
      rendered_epics = $renderedEpics
      rendered_initiative = $true
      completed_task_count = $completedTaskCount
      active_task_count = $activeTaskCount
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
    $body = Get-EpicBody -EpicDefinition $epicDefinition -LifecyclePlan $lifecyclePlan -DirectRoadmapPhases $directRoadmapPhases -GovernanceRoadmapPhases $governanceRoadmapPhases
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
    $title = if ($IssueId -match '^GAP-\d+$') { "[Task] $($seed.title)" } else { $seed.title }
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
    completed_task_count = $completedTaskCount
    active_task_count = $activeTaskCount
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
  @{ Name = "phase:strategy-alignment"; Color = "8A63D2"; Description = "Strategy alignment gate phase" }
  @{ Name = "phase:rebaseline"; Color = "0052CC"; Description = "Canonical re-baseline phase" }
  @{ Name = "phase:governed-execution"; Color = "0E8A16"; Description = "Governed execution closure phase" }
  @{ Name = "phase:live-adapter"; Color = "FBCA04"; Description = "Live host adapter phase" }
  @{ Name = "phase:multi-repo-sidecar"; Color = "1D76DB"; Description = "Real multi-repo and machine-local sidecar phase" }
  @{ Name = "phase:service-extraction"; Color = "D93F0B"; Description = "Service-shaped runtime extraction phase" }
  @{ Name = "phase:hardening-closeout"; Color = "5319E7"; Description = "Hardening and closeout phase" }
  @{ Name = "phase:governance-optimization"; Color = "C2E0C6"; Description = "Governance optimization follow-on lane" }
  @{ Name = "phase:near-term-gap-horizon"; Color = "BFDADC"; Description = "Near-term optimized best-state execution horizon queue" }
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
  $body = Get-EpicBody -EpicDefinition $epicDefinition -LifecyclePlan $lifecyclePlan -DirectRoadmapPhases $directRoadmapPhases -GovernanceRoadmapPhases $governanceRoadmapPhases
  New-RoadmapIssue -Title $epicDefinition.Title -Labels $epicDefinition.Labels -Body $body
}

if (-not $SkipTasks) {
  $tasks = @(Get-TaskDefinitions -IssueSeeds $seedData.issues -BacklogTaskMap $backlogTaskMap)

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
