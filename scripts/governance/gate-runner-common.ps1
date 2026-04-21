Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-ObjectProperty {
  param(
    [Parameter(Mandatory)]
    [object]$Object,
    [Parameter(Mandatory)]
    [string]$Name
  )

  return $Object.PSObject.Properties.Name -contains $Name
}

function Resolve-RepoProfilePath {
  param(
    [Parameter(Mandatory)]
    [string]$RepoProfilePath
  )

  if (-not (Test-Path -LiteralPath $RepoProfilePath)) {
    throw "Repo profile path not found: $RepoProfilePath"
  }
  return (Resolve-Path -LiteralPath $RepoProfilePath).Path
}

function Resolve-GateWorkingDirectory {
  param(
    [Parameter(Mandatory)]
    [string]$ResolvedRepoProfilePath,
    [string]$WorkingDirectory = ""
  )

  if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
    if (-not (Test-Path -LiteralPath $WorkingDirectory)) {
      throw "WorkingDirectory does not exist: $WorkingDirectory"
    }
    return (Resolve-Path -LiteralPath $WorkingDirectory).Path
  }

  $profileDir = Split-Path -Parent $ResolvedRepoProfilePath
  if ((Split-Path -Leaf $profileDir) -ieq ".governed-ai") {
    return (Resolve-Path -LiteralPath (Split-Path -Parent $profileDir)).Path
  }

  return (Get-Location).Path
}

function Get-RepoProfileObject {
  param(
    [Parameter(Mandatory)]
    [string]$ResolvedRepoProfilePath
  )

  try {
    $profile = Get-Content -Raw -LiteralPath $ResolvedRepoProfilePath | ConvertFrom-Json
  }
  catch {
    throw "Failed to parse repo profile JSON: $ResolvedRepoProfilePath`n$($_.Exception.Message)"
  }

  if ($null -eq $profile) {
    throw "Repo profile JSON is empty: $ResolvedRepoProfilePath"
  }
  return $profile
}

function Get-CommandGroup {
  param(
    [Parameter(Mandatory)]
    [object]$Profile,
    [Parameter(Mandatory)]
    [string]$GroupName
  )

  if (-not (Test-ObjectProperty -Object $Profile -Name $GroupName)) {
    return @()
  }

  $commands = $Profile.$GroupName
  if ($null -eq $commands) {
    return @()
  }
  return @($commands)
}

function Select-PreferredCommand {
  param(
    [object[]]$Commands
  )

  if ($null -eq $Commands -or $Commands.Count -eq 0) {
    return $null
  }

  $required = @(
    $Commands | Where-Object {
      -not (Test-ObjectProperty -Object $_ -Name "required") -or
      $_.required -eq $true
    }
  )
  if ($required.Count -gt 0) {
    return $required[0]
  }
  return $Commands[0]
}

function Assert-ValidCommandEntry {
  param(
    [Parameter(Mandatory)]
    [object]$Entry,
    [Parameter(Mandatory)]
    [string]$SourceGroup
  )

  if (-not (Test-ObjectProperty -Object $Entry -Name "command")) {
    throw "$SourceGroup entry is missing 'command'"
  }
  if ([string]::IsNullOrWhiteSpace([string]$Entry.command)) {
    throw "$SourceGroup entry has empty 'command'"
  }
}

function New-GateCommandRecord {
  param(
    [Parameter(Mandatory)]
    [object]$Entry,
    [Parameter(Mandatory)]
    [string]$DefaultGateId,
    [Parameter(Mandatory)]
    [string]$SourceGroup
  )

  Assert-ValidCommandEntry -Entry $Entry -SourceGroup $SourceGroup

  $gateId = $DefaultGateId
  if ((Test-ObjectProperty -Object $Entry -Name "id") -and -not [string]::IsNullOrWhiteSpace([string]$Entry.id)) {
    $gateId = [string]$Entry.id
  }

  $required = $true
  if (Test-ObjectProperty -Object $Entry -Name "required") {
    $required = [bool]$Entry.required
  }

  $description = ""
  if ((Test-ObjectProperty -Object $Entry -Name "description") -and $null -ne $Entry.description) {
    $description = [string]$Entry.description
  }

  return [pscustomobject]@{
    gate_id      = $gateId
    command      = ([string]$Entry.command).Trim()
    required     = $required
    source_group = $SourceGroup
    description  = $description
  }
}

function Resolve-FastGateCommands {
  param(
    [Parameter(Mandatory)]
    [object]$Profile
  )

  $quick = Get-CommandGroup -Profile $Profile -GroupName "quick_gate_commands"
  if ($quick.Count -gt 0) {
    $commands = @()
    $index = 0
    foreach ($entry in $quick) {
      $index += 1
      $commands += New-GateCommandRecord -Entry $entry -DefaultGateId ("quick-{0}" -f $index) -SourceGroup "quick_gate_commands"
    }
    return [pscustomobject]@{
      source   = "quick_gate_commands"
      commands = $commands
    }
  }

  $testEntry = Select-PreferredCommand -Commands (Get-CommandGroup -Profile $Profile -GroupName "test_commands")
  $contractEntry = Select-PreferredCommand -Commands (Get-CommandGroup -Profile $Profile -GroupName "contract_commands")
  $contractSource = "contract_commands"
  if ($null -eq $contractEntry) {
    $contractEntry = Select-PreferredCommand -Commands (Get-CommandGroup -Profile $Profile -GroupName "invariant_commands")
    $contractSource = "invariant_commands"
  }

  if ($null -eq $testEntry -or $null -eq $contractEntry) {
    throw "fast gate fallback requires test_commands plus contract_commands (or invariant_commands)"
  }

  return [pscustomobject]@{
    source   = "fallback:test+contract"
    commands = @(
      (New-GateCommandRecord -Entry $testEntry -DefaultGateId "test" -SourceGroup "test_commands"),
      (New-GateCommandRecord -Entry $contractEntry -DefaultGateId "contract" -SourceGroup $contractSource)
    )
  }
}

function Resolve-FullGateCommands {
  param(
    [Parameter(Mandatory)]
    [object]$Profile
  )

  $full = Get-CommandGroup -Profile $Profile -GroupName "full_gate_commands"
  if ($full.Count -gt 0) {
    $commands = @()
    $index = 0
    foreach ($entry in $full) {
      $index += 1
      $commands += New-GateCommandRecord -Entry $entry -DefaultGateId ("full-{0}" -f $index) -SourceGroup "full_gate_commands"
    }
    return [pscustomobject]@{
      source   = "full_gate_commands"
      commands = $commands
    }
  }

  $buildEntry = Select-PreferredCommand -Commands (Get-CommandGroup -Profile $Profile -GroupName "build_commands")
  $testEntry = Select-PreferredCommand -Commands (Get-CommandGroup -Profile $Profile -GroupName "test_commands")
  $contractEntry = Select-PreferredCommand -Commands (Get-CommandGroup -Profile $Profile -GroupName "contract_commands")
  $contractSource = "contract_commands"
  if ($null -eq $contractEntry) {
    $contractEntry = Select-PreferredCommand -Commands (Get-CommandGroup -Profile $Profile -GroupName "invariant_commands")
    $contractSource = "invariant_commands"
  }

  if ($null -eq $buildEntry -or $null -eq $testEntry -or $null -eq $contractEntry) {
    throw "full gate fallback requires build_commands + test_commands + contract_commands (or invariant_commands)"
  }

  return [pscustomobject]@{
    source   = "fallback:build+test+contract"
    commands = @(
      (New-GateCommandRecord -Entry $buildEntry -DefaultGateId "build" -SourceGroup "build_commands"),
      (New-GateCommandRecord -Entry $testEntry -DefaultGateId "test" -SourceGroup "test_commands"),
      (New-GateCommandRecord -Entry $contractEntry -DefaultGateId "contract" -SourceGroup $contractSource)
    )
  }
}

function Resolve-GateCommands {
  param(
    [Parameter(Mandatory)]
    [ValidateSet("fast", "full")]
    [string]$Mode,
    [Parameter(Mandatory)]
    [object]$Profile
  )

  if ($Mode -eq "fast") {
    return Resolve-FastGateCommands -Profile $Profile
  }
  return Resolve-FullGateCommands -Profile $Profile
}

function Invoke-GateCommand {
  param(
    [Parameter(Mandatory)]
    [object]$Gate,
    [Parameter(Mandatory)]
    [string]$WorkingDirectory
  )

  $startedAt = Get-Date
  Write-Host ("==> [{0}] {1}" -f $Gate.gate_id, $Gate.command)

  Push-Location -LiteralPath $WorkingDirectory
  try {
    $outputLines = & pwsh -NoProfile -ExecutionPolicy Bypass -Command $Gate.command 2>&1
    $exitCode = $LASTEXITCODE
    if ($null -eq $exitCode) {
      $exitCode = 0
    }
  }
  finally {
    Pop-Location
  }

  $outputText = (($outputLines | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).TrimEnd()
  if (-not [string]::IsNullOrWhiteSpace($outputText)) {
    Write-Host $outputText
  }

  $finishedAt = Get-Date
  $status = if ([int]$exitCode -eq 0) { "pass" } else { "fail" }

  return [pscustomobject]@{
    gate_id      = $Gate.gate_id
    required     = [bool]$Gate.required
    source_group = $Gate.source_group
    command      = $Gate.command
    status       = $status
    exit_code    = [int]$exitCode
    duration_ms  = [int][Math]::Round(($finishedAt - $startedAt).TotalMilliseconds)
    started_at   = $startedAt.ToString("o")
    finished_at  = $finishedAt.ToString("o")
  }
}

function Write-GateRunSummary {
  param(
    [Parameter(Mandatory)]
    [hashtable]$Summary,
    [Parameter(Mandatory)]
    [int]$ExitCode
  )

  Write-Host ("mode={0} source={1} exit_code={2}" -f $Summary.mode, $Summary.command_source, $ExitCode)
  foreach ($result in $Summary.detailed) {
    Write-Host ("- {0}: {1} (required={2}, exit={3}, {4}ms)" -f $result.gate_id, $result.status, $result.required, $result.exit_code, $result.duration_ms)
  }
}

function Invoke-RepoProfileGateRun {
  param(
    [Parameter(Mandatory)]
    [ValidateSet("fast", "full")]
    [string]$Mode,
    [string]$RepoProfilePath = ".governed-ai/repo-profile.json",
    [string]$WorkingDirectory = "",
    [switch]$ContinueOnError,
    [switch]$JsonOutput
  )

  $resolvedProfilePath = Resolve-RepoProfilePath -RepoProfilePath $RepoProfilePath
  $resolvedWorkingDirectory = Resolve-GateWorkingDirectory -ResolvedRepoProfilePath $resolvedProfilePath -WorkingDirectory $WorkingDirectory
  $profile = Get-RepoProfileObject -ResolvedRepoProfilePath $resolvedProfilePath
  $resolved = Resolve-GateCommands -Mode $Mode -Profile $profile

  $startedAt = Get-Date
  $results = @()

  foreach ($gate in $resolved.commands) {
    $result = Invoke-GateCommand -Gate $gate -WorkingDirectory $resolvedWorkingDirectory
    $results += $result
    if ($result.status -eq "fail" -and $result.required -and -not $ContinueOnError.IsPresent) {
      break
    }
  }

  $requiredFailures = @($results | Where-Object { $_.required -and $_.status -eq "fail" })
  $exitCode = if ($requiredFailures.Count -gt 0) { 1 } else { 0 }

  $resultMap = [ordered]@{}
  foreach ($result in $results) {
    $resultMap[$result.gate_id] = $result.status
  }

  $summary = [ordered]@{
    mode              = $Mode
    command_source    = $resolved.source
    repo_profile_path = $resolvedProfilePath
    working_directory = $resolvedWorkingDirectory
    gate_order        = @($results | ForEach-Object { $_.gate_id })
    results           = $resultMap
    detailed          = $results
    started_at        = $startedAt.ToString("o")
    finished_at       = (Get-Date).ToString("o")
  }

  if ($JsonOutput.IsPresent) {
    $payload = [ordered]@{
      exit_code = $exitCode
      summary   = $summary
    }
    Write-Host ($payload | ConvertTo-Json -Depth 10)
  }
  else {
    Write-GateRunSummary -Summary $summary -ExitCode $exitCode
  }

  return [pscustomobject]@{
    exit_code = $exitCode
    summary   = $summary
  }
}
