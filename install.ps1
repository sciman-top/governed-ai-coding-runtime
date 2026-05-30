param(
  [ValidateSet("Portable", "User")]
  [string]$Mode = "Portable",

  [string]$RuntimeRoot = "",

  [switch]$SyncRules,

  [switch]$InstallHooks,

  [switch]$OpenUi,

  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvironmentScript = Join-Path $RepoRoot "scripts/Initialize-WindowsProcessEnvironment.ps1"
if (Test-Path -LiteralPath $EnvironmentScript) {
  . $EnvironmentScript
  Initialize-WindowsProcessEnvironment | Out-Null
}

function Get-CommandPath {
  param([string]$Name)

  $command = Get-Command $Name -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }
  return $null
}

function Resolve-InstallRuntimeRoot {
  param(
    [string]$RequestedRoot,
    [string]$InstallMode
  )

  if (-not [string]::IsNullOrWhiteSpace($RequestedRoot)) {
    $resolved = Resolve-Path -Path $RequestedRoot -ErrorAction SilentlyContinue
    if ($resolved) {
      return $resolved.Path
    }
    if ([System.IO.Path]::IsPathRooted($RequestedRoot)) {
      return [System.IO.Path]::GetFullPath($RequestedRoot)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $RequestedRoot))
  }
  if ($InstallMode -eq "Portable") {
    return (Join-Path $RepoRoot ".runtime")
  }
  $localAppData = $env:LOCALAPPDATA
  if ([string]::IsNullOrWhiteSpace($localAppData)) {
    $localAppData = Join-Path $HOME "AppData\Local"
  }
  return (Join-Path $localAppData "governed-ai-coding-runtime\governed-ai-coding-runtime")
}

function New-InstallState {
  param(
    [string]$InstallMode,
    [string]$ResolvedRuntimeRoot,
    [bool]$IsDryRun,
    [object]$RuntimeStatus,
    [string]$RuleSyncStatus,
    [string]$HookStatus
  )

  return @{
    schema_version = "1.0"
    mode = $InstallMode
    dry_run = $IsDryRun
    repo_root = $RepoRoot
    runtime_root = $ResolvedRuntimeRoot
    required_commands = @("pwsh", "python")
    optional_commands = @("git")
    command_paths = @{
      pwsh = Get-CommandPath -Name "pwsh"
      python = Get-CommandPath -Name "python"
      git = Get-CommandPath -Name "git"
    }
    created_paths = @(
      $ResolvedRuntimeRoot,
      (Join-Path $ResolvedRuntimeRoot "tasks"),
      (Join-Path $ResolvedRuntimeRoot "artifacts"),
      (Join-Path $ResolvedRuntimeRoot "replay"),
      (Join-Path $ResolvedRuntimeRoot "workspaces"),
      (Join-Path $ResolvedRuntimeRoot "attachments")
    )
    runtime_status = $RuntimeStatus
    rule_sync = $RuleSyncStatus
    hooks = $HookStatus
    migration_boundary = "This installer initializes runtime directories only. It does not migrate credentials, provider settings, target-repo working trees, or historical runtime evidence."
    next_commands = @(
      ".\run.ps1 readiness -OpenUi",
      ".\run.ps1 targets",
      ".\install.ps1 -Mode User"
    )
  }
}

$missingRequired = @()
foreach ($commandName in @("pwsh", "python")) {
  if (-not (Get-CommandPath -Name $commandName)) {
    $missingRequired += $commandName
  }
}
if ($missingRequired.Count -gt 0) {
  throw "Missing required commands: $($missingRequired -join ', ')"
}

$resolvedRuntimeRoot = Resolve-InstallRuntimeRoot -RequestedRoot $RuntimeRoot -InstallMode $Mode
$runtimeStatus = $null
$ruleSyncStatus = if ($SyncRules) { "pending" } else { "skipped" }
$hookStatus = if ($InstallHooks) { "pending" } else { "skipped" }

if (-not $DryRun) {
  foreach ($path in @(
      $resolvedRuntimeRoot,
      (Join-Path $resolvedRuntimeRoot "tasks"),
      (Join-Path $resolvedRuntimeRoot "artifacts"),
      (Join-Path $resolvedRuntimeRoot "replay"),
      (Join-Path $resolvedRuntimeRoot "workspaces"),
      (Join-Path $resolvedRuntimeRoot "attachments")
    )) {
    New-Item -ItemType Directory -Force -Path $path | Out-Null
  }

  Push-Location $RepoRoot
  try {
    $statusJson = & python "scripts/run-governed-task.py" --runtime-root $resolvedRuntimeRoot status --json
    if ($LASTEXITCODE -ne 0) {
      throw "Runtime status command failed during install"
    }
    $runtimeStatus = $statusJson | ConvertFrom-Json

    if ($SyncRules) {
      & pwsh -NoProfile -ExecutionPolicy Bypass -File "scripts/sync-agent-rules.ps1" -Scope All -Apply | Out-Null
      if ($LASTEXITCODE -ne 0) {
        throw "Rule sync failed during install"
      }
      $ruleSyncStatus = "applied"
    }

    if ($InstallHooks) {
      if (Test-Path -LiteralPath (Join-Path $RepoRoot ".git")) {
        & pwsh -NoProfile -ExecutionPolicy Bypass -File "scripts/install-repo-hooks.ps1" | Out-Null
        if ($LASTEXITCODE -ne 0) {
          throw "Git hook installation failed"
        }
        $hookStatus = "installed"
      } else {
        $hookStatus = "skipped_no_git_metadata"
      }
    }
  }
  finally {
    Pop-Location
  }
}

$payload = New-InstallState `
  -InstallMode $Mode `
  -ResolvedRuntimeRoot $resolvedRuntimeRoot `
  -IsDryRun ([bool]$DryRun) `
  -RuntimeStatus $runtimeStatus `
  -RuleSyncStatus $ruleSyncStatus `
  -HookStatus $hookStatus

if (-not $DryRun) {
  $statePath = Join-Path $resolvedRuntimeRoot "install-state.json"
  $payload | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -Path $statePath
  $payload.install_state_path = $statePath
}

if ($OpenUi -and -not $DryRun) {
  Push-Location $RepoRoot
  try {
    & pwsh -NoProfile -ExecutionPolicy Bypass -File "run.ps1" "ui" "-OpenUi" | Out-Null
    if ($LASTEXITCODE -ne 0) {
      throw "Operator UI startup failed"
    }
  }
  finally {
    Pop-Location
  }
}

$payload | ConvertTo-Json -Depth 8
