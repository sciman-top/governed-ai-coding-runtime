param(
  [string]$AsOf,
  [switch]$WriteArtifacts
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

  $arguments = @("scripts/extract-ai-coding-experience.py")
  if (-not [string]::IsNullOrWhiteSpace($AsOf)) {
    $arguments += @("--as-of", $AsOf)
  }
  if ($WriteArtifacts) {
    $arguments += "--write-artifacts"
  }

  & $python.Source @arguments
  if ($LASTEXITCODE -ne 0) {
    throw "AI coding experience extraction failed with exit code $LASTEXITCODE"
  }
}
finally {
  Pop-Location
}
