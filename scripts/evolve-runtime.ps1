param(
  [ValidateSet("dry-run")]
  [string]$Mode = "dry-run",

  [string]$AsOf = "",
  [switch]$WriteArtifacts,
  [switch]$OnlineSourceCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\Initialize-WindowsProcessEnvironment.ps1"
Initialize-WindowsProcessEnvironment

$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
  throw "Required command not found: python or python3"
}

$arguments = @("scripts/evaluate-runtime-evolution.py")
if (-not [string]::IsNullOrWhiteSpace($AsOf)) {
  $arguments += @("--as-of", $AsOf)
}
if ($WriteArtifacts) {
  $arguments += "--write-artifacts"
}
if ($OnlineSourceCheck) {
  $arguments += "--online-source-check"
}

Push-Location -LiteralPath $RepoRoot
try {
  & $python.Source @arguments
  $exitCode = $LASTEXITCODE
  if ($null -eq $exitCode) {
    $exitCode = 0
  }
  if ($exitCode -ne 0) {
    throw "Runtime evolution dry-run failed (exit_code=$exitCode)"
  }
}
finally {
  Pop-Location
}
