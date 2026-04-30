param(
  [string]$AsOf,
  [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\Initialize-WindowsProcessEnvironment.ps1"
Initialize-WindowsProcessEnvironment

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $repoRoot
try {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
  }
  if (-not $python) {
    throw "Required command not found: python or python3"
  }

  $arguments = @("scripts/materialize-runtime-evolution.py")
  if (-not [string]::IsNullOrWhiteSpace($AsOf)) {
    $arguments += @("--as-of", $AsOf)
  }
  if ($Apply) {
    $arguments += "--apply"
  }

  & $python.Source @arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Runtime evolution materialization failed with exit code $LASTEXITCODE"
  }
}
finally {
  Pop-Location
}
