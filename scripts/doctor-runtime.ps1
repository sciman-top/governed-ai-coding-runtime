Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-WindowsPlatform {
  if ($PSVersionTable.PSVersion.Major -lt 6) {
    return $true
  }
  return $IsWindows
}

function Get-MissingWindowsProcessEnvironmentVariables {
  if (-not (Test-WindowsPlatform)) {
    return @()
  }

  $required = @("ComSpec", "SystemRoot", "WINDIR", "APPDATA", "LOCALAPPDATA", "PROGRAMDATA", "ProgramFiles")
  $missing = @()
  foreach ($name in $required) {
    if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name, "Process"))) {
      $missing += $name
    }
  }
  return $missing
}

$missingWindowsProcessEnvBeforeInit = @(Get-MissingWindowsProcessEnvironmentVariables)

. "$PSScriptRoot\Initialize-WindowsProcessEnvironment.ps1"
Initialize-WindowsProcessEnvironment

function Write-CheckOk {
  param([string]$Name)
  Write-Host "OK $Name"
}

function Write-CheckWarn {
  param([string]$Name)
  Write-Host "WARN $Name"
}

function Assert-WindowsProcessEnvironmentHealth {
  param(
    [Parameter(Mandatory = $true)]
    [string]$PythonCommand,
    [string[]]$MissingBeforeInit
  )

  if (-not (Test-WindowsPlatform)) {
    return
  }

  $missingAfterInit = @(Get-MissingWindowsProcessEnvironmentVariables)
  if ($missingAfterInit.Count -gt 0) {
    throw ("Windows process environment is incomplete after initialization: " + ($missingAfterInit -join ", "))
  }

  Write-CheckOk "windows-process-environment"
  if ($MissingBeforeInit.Count -gt 0) {
    Write-CheckOk ("windows-process-environment-normalized:" + ($MissingBeforeInit -join ","))
  }

  $asyncioOutput = & $PythonCommand -c "import asyncio; print('asyncio ok')" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $hint = if ($MissingBeforeInit.Count -gt 0) {
      "Process env was incomplete and has been normalized, but asyncio still fails. Re-check Windows Winsock/network provider health in a fresh elevated PowerShell."
    }
    else {
      "Process env was complete before doctor started. This points to Windows Winsock/network provider health rather than repo code."
    }
    throw ("Python asyncio unavailable after Windows process environment normalization. $hint Output: " + (($asyncioOutput | Out-String).Trim()))
  }
  Write-CheckOk "python-asyncio"

  $node = Get-Command node -ErrorAction SilentlyContinue
  if ($node) {
    $nodeOutput = & $node.Source -e "console.log('node ok')" 2>&1
    if ($LASTEXITCODE -eq 0) {
      Write-CheckOk "windows-node-csprng"
    }
    else {
      Write-CheckWarn "windows-node-csprng-unavailable"
      Write-Host ("HINT Node exists but cannot initialize crypto/CSPRNG. Run the same node probe in a fresh elevated PowerShell; if it also fails, repair Winsock/IP and reboot.")
      Write-Host ("DETAIL " + (($nodeOutput | Out-String).Trim()))
    }
  }
  else {
    Write-CheckWarn "windows-node-not-found"
  }
}

function Assert-PathExists {
  param(
    [string]$Path,
    [string]$CheckName
  )

  if (-not (Test-Path $Path)) {
    throw "Required path missing: $Path"
  }

  Write-CheckOk $CheckName
}

function Assert-RepoHookEnforcement {
  Assert-PathExists -Path ".githooks/pre-commit" -CheckName "repo-hook-pre-commit"
  Assert-PathExists -Path ".githooks/commit-msg" -CheckName "repo-hook-commit-msg"
  Assert-PathExists -Path "scripts/hooks/pre-commit.ps1" -CheckName "repo-hook-script"
  Assert-PathExists -Path "scripts/hooks/commit-msg.ps1" -CheckName "repo-hook-commit-msg-script"
  Assert-PathExists -Path "scripts/install-repo-hooks.ps1" -CheckName "repo-hook-installer"

  $git = Get-Command git -ErrorAction SilentlyContinue
  if (-not $git) {
    Write-CheckWarn "repo-hooks-path-git-unavailable"
    return
  }
  if (-not (Test-Path -LiteralPath ".git")) {
    Write-CheckWarn "repo-hooks-path-no-git-metadata"
    return
  }

  $configuredHooksPath = (& $git.Source -C (Get-Location).Path config --get core.hooksPath 2>$null) -join ""
  if ($LASTEXITCODE -ne 0 -or $configuredHooksPath -ne ".githooks") {
    throw "Git core.hooksPath must be .githooks for repo-local one-click rollout enforcement. Run: pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1"
  }

  Write-CheckOk "repo-hooks-path"
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
  throw "Required command not found: python or python3"
}
Write-CheckOk "python-command"
Assert-WindowsProcessEnvironmentHealth -PythonCommand $python.Source -MissingBeforeInit $missingWindowsProcessEnvBeforeInit

foreach ($pathCheck in @(
  @{ Path = "packages/contracts/src"; Check = "runtime-path-contracts" },
  @{ Path = "schemas/catalog/schema-catalog.yaml"; Check = "runtime-path-schema-catalog" },
  @{ Path = "docs/specs"; Check = "runtime-path-specs" },
  @{ Path = "tests/runtime"; Check = "runtime-path-tests" },
  @{ Path = "docs/dependency-baseline.md"; Check = "dependency-baseline-doc" },
  @{ Path = "docs/dependency-baseline.json"; Check = "dependency-baseline-manifest" },
  @{ Path = "scripts/verify-dependency-baseline.py"; Check = "dependency-baseline-script" },
  @{ Path = "docs/product/runtime-compatibility-and-upgrade-policy.md"; Check = "runtime-policy-compatibility" },
  @{ Path = "docs/product/maintenance-deprecation-and-retirement-policy.md"; Check = "runtime-policy-maintenance" }
)) {
  Assert-PathExists -Path $pathCheck.Path -CheckName $pathCheck.Check
}

$catalog = Get-Content -Raw "schemas/catalog/schema-catalog.yaml"
if ($catalog -notmatch "repo-profile" -or $catalog -notmatch "clarification-protocol") {
  throw "Schema catalog is missing expected schema families"
}
Write-CheckOk "schema-catalog-visible"

$gateCommands = @(
  @{ Path = "scripts/build-runtime.ps1"; Check = "gate-command-build" },
  @{ Path = "scripts/verify-repo.ps1"; Check = "gate-command-test" },
  @{ Path = "scripts/verify-repo.ps1"; Check = "gate-command-contract" },
  @{ Path = "scripts/doctor-runtime.ps1"; Check = "gate-command-doctor" }
)

foreach ($gateCommand in $gateCommands) {
  Assert-PathExists -Path $gateCommand.Path -CheckName $gateCommand.Check
}

Assert-PathExists -Path "scripts/run-governed-task.py" -CheckName "gate-command-operator"
Assert-RepoHookEnforcement

$statusJson = & $python.Source "scripts/run-governed-task.py" status --json
if ($LASTEXITCODE -ne 0) {
  throw "Runtime status command failed"
}

$status = $statusJson | ConvertFrom-Json
if ($null -eq $status.total_tasks) {
  throw "Runtime status output missing total_tasks"
}
if ($null -eq $status.maintenance -or [string]::IsNullOrWhiteSpace($status.maintenance.stage)) {
  throw "Runtime status output missing maintenance stage"
}
Write-CheckOk "runtime-status-surface"
Write-CheckOk "maintenance-policy-visible"

$codexCapability = $status.codex_capability
if ($null -ne $codexCapability) {
  $codexStatus = [string]$codexCapability.status
  if ($codexStatus -eq "ready") {
    Write-CheckOk "codex-capability-ready"
  }
  elseif ($codexStatus -eq "degraded") {
    Write-CheckWarn "codex-capability-degraded"
    if ($codexCapability.remediation_hint) {
      Write-Host ("HINT " + [string]$codexCapability.remediation_hint)
    }
  }
  elseif ($codexStatus -eq "blocked") {
    Write-CheckWarn "codex-capability-blocked"
    if ($codexCapability.remediation_hint) {
      Write-Host ("HINT " + [string]$codexCapability.remediation_hint)
    }
  }
}

$adapterCheck = @'
from pathlib import Path
import sys

root = Path.cwd()
contracts_src = root / "packages" / "contracts" / "src"
sys.path.insert(0, str(contracts_src))

from governed_ai_coding_runtime_contracts.compatibility import resolve_runtime_posture
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile

profile = load_repo_profile(root / "schemas" / "examples" / "repo-profile" / "governed-ai-coding-runtime.example.json")
result = resolve_runtime_posture(
    requested_posture="enforced",
    repo_supported_postures=["observe", "advisory", "enforced"],
    compatibility_signals=profile.compatibility_signals,
)
if result.support_level not in ("partial_support", "full_support", "unsupported"):
    raise SystemExit(1)
print(result.effective_posture)
'@

$adapterResult = $adapterCheck | & $python.Source -
if ($LASTEXITCODE -ne 0) {
  throw "Adapter posture visibility check failed"
}
if ([string]::IsNullOrWhiteSpace($adapterResult)) {
  throw "Adapter posture visibility output missing"
}
Write-CheckOk "adapter-posture-visible"
