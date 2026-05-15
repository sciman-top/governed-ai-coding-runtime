param(
  [string]$ModeFile = "$HOME\.antigravity_cockpit\codex_runtime_mode.json",
  [switch]$DryRun,
  [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))

function Write-Result {
  param([Parameter(Mandatory = $true)][hashtable]$Data)
  if ($Json) {
    $Data | ConvertTo-Json -Depth 8 -Compress | Write-Host
    return
  }
  Write-Host ("codex-mode-sync: status={0} mode={1} account_kind={2} action={3}" -f $Data.status, $Data.mode, $Data.account_kind, $Data.materialized_action)
}

function Invoke-Step {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$ScriptPath,
    [Parameter(Mandatory = $true)][string[]]$Arguments
  )

  $pwsh = Get-Command pwsh -ErrorAction Stop
  $display = "pwsh -NoProfile -ExecutionPolicy Bypass -File $ScriptPath $($Arguments -join ' ')"
  if ($DryRun) {
    Write-Host ("DRY-RUN {0}: {1}" -f $Name, $display)
    return
  }
  Write-Host ("codex-mode-sync-step: {0}" -f $Name)
  & $pwsh.Source -NoProfile -ExecutionPolicy Bypass -File $ScriptPath @Arguments
  $exitCode = $LASTEXITCODE
  if ($null -eq $exitCode) {
    $exitCode = 0
  }
  if ($exitCode -ne 0) {
    throw "Codex mode sync step failed: $Name (exit_code=$exitCode)"
  }
}

function Invoke-PythonRepair {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string[]]$RepairArguments
  )

  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    $python = Get-Command python3 -ErrorAction Stop
  }
  $arguments = @(
    "scripts/codex-interop-check.py",
    "--codex-home",
    (Join-Path $HOME ".codex"),
    "--cc-switch-db",
    (Join-Path $HOME ".cc-switch\cc-switch.db"),
    "--cockpit-home",
    (Join-Path $HOME ".antigravity_cockpit"),
    "--quick-launch"
  ) + $RepairArguments
  $display = "$($python.Source) $($arguments -join ' ')"
  if ($DryRun) {
    Write-Host ("DRY-RUN {0}: {1}" -f $Name, $display)
    return
  }
  Write-Host ("codex-mode-sync-step: {0}" -f $Name)
  & $python.Source @arguments
  $exitCode = $LASTEXITCODE
  if ($null -eq $exitCode) {
    $exitCode = 0
  }
  if ($exitCode -ne 0) {
    throw "Codex mode sync step failed: $Name (exit_code=$exitCode)"
  }
}

if (-not (Test-Path -LiteralPath $ModeFile)) {
  throw "Cockpit Codex runtime mode file not found: $ModeFile"
}

$modeState = Get-Content -LiteralPath $ModeFile -Raw | ConvertFrom-Json
$mode = [string]$modeState.mode
$accountKind = [string]$modeState.accountKind
$currentAccountId = [string]$modeState.currentAccountId

Push-Location -LiteralPath $RepoRoot
try {
  switch ($mode) {
    "gateway_litellm" {
      Invoke-Step -Name "codex-gateway-start" -ScriptPath "scripts/Manage-LiteLLMGateway.ps1" -Arguments @("-Action", "Start")
      Invoke-Step -Name "codex-gateway-smoke" -ScriptPath "scripts/Manage-LiteLLMGateway.ps1" -Arguments @("-Action", "Smoke")
      Invoke-Step -Name "codex-gateway-prepare-cockpit-upstream" -ScriptPath "scripts/Manage-LiteLLMGateway.ps1" -Arguments @("-Action", "PrepareCockpitUpstream")
      Invoke-Step -Name "codex-gateway-status" -ScriptPath "scripts/Manage-LiteLLMGateway.ps1" -Arguments @("-Action", "CockpitStatus")
      Invoke-Step -Name "codex-gateway-write-profile" -ScriptPath "scripts/Manage-LiteLLMGateway.ps1" -Arguments @("-Action", "WriteCodexProfile")
      Write-Result @{ status = "ok"; mode = $mode; account_kind = $accountKind; current_account_id = $currentAccountId; materialized_action = "gateway_litellm"; mode_file = $ModeFile }
    }
    "direct_projection" {
      Invoke-Step -Name "codex-gateway-rollback" -ScriptPath "scripts/Manage-LiteLLMGateway.ps1" -Arguments @("-Action", "Rollback")
      if ($accountKind -eq "api") {
        Invoke-PythonRepair -Name "codex-direct-api-projection" -RepairArguments @("--repair-current-cockpit-api-projection", "--prefer-cockpit-api-account")
        Write-Result @{ status = "ok"; mode = $mode; account_kind = $accountKind; current_account_id = $currentAccountId; materialized_action = "direct_projection_api"; mode_file = $ModeFile }
      }
      elseif ($accountKind -eq "oauth") {
        Invoke-PythonRepair -Name "codex-direct-oauth-projection" -RepairArguments @("--repair-current-cockpit-oauth-projection")
        Write-Result @{ status = "ok"; mode = $mode; account_kind = $accountKind; current_account_id = $currentAccountId; materialized_action = "direct_projection_oauth"; mode_file = $ModeFile }
      }
      else {
        throw "Cannot materialize direct_projection with accountKind=$accountKind"
      }
    }
    default {
      throw "Unsupported Cockpit Codex runtime mode: $mode"
    }
  }
}
finally {
  Pop-Location
}
