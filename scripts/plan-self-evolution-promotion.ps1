param(
  [string]$AsOf = "",
  [string]$Recommendation = "",
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

  $arguments = @("scripts/plan-self-evolution-promotion.py")
  if (-not [string]::IsNullOrWhiteSpace($AsOf)) {
    $arguments += @("--as-of", $AsOf)
  }
  if (-not [string]::IsNullOrWhiteSpace($Recommendation)) {
    $arguments += @("--recommendation", $Recommendation)
  }
  if ($WriteArtifacts) {
    $arguments += "--write-artifacts"
  }
  if (-not [string]::IsNullOrWhiteSpace($ArtifactRoot)) {
    $arguments += @("--artifact-root", $ArtifactRoot)
  }

  & $python.Source @arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Self-evolution promotion planning failed with exit code $LASTEXITCODE"
  }
}
finally {
  Pop-Location
}
