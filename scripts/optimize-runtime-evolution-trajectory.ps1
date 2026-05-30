param(
  [string]$AsOf = "",
  [switch]$WriteArtifacts,
  [string]$ArtifactRoot = ""
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

  $arguments = @("scripts/optimize-runtime-evolution-trajectory.py")
  if (-not [string]::IsNullOrWhiteSpace($AsOf)) {
    $arguments += @("--as-of", $AsOf)
  }
  if ($WriteArtifacts) {
    $arguments += "--write-artifacts"
  }
  if (-not [string]::IsNullOrWhiteSpace($ArtifactRoot)) {
    $arguments += @("--artifact-root", $ArtifactRoot)
  }

  & $python.Source @arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Runtime evolution trajectory optimization failed with exit code $LASTEXITCODE"
  }
}
finally {
  Pop-Location
}
