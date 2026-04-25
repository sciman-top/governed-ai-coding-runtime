Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$GitDir = Join-Path $RepoRoot ".git"
$HooksDir = Join-Path $RepoRoot ".githooks"
$PreCommit = Join-Path $HooksDir "pre-commit"

if (-not (Test-Path -LiteralPath $GitDir)) {
  throw "Git repository metadata was not found: $GitDir"
}
if (-not (Test-Path -LiteralPath $PreCommit)) {
  throw "Repository pre-commit hook was not found: $PreCommit"
}

& git -C $RepoRoot config core.hooksPath .githooks
if ($LASTEXITCODE -ne 0) {
  throw "Failed to set git core.hooksPath"
}

$configured = (& git -C $RepoRoot config --get core.hooksPath) -join ""
if ($configured -ne ".githooks") {
  throw "Expected core.hooksPath=.githooks, got: $configured"
}

Write-Host "OK git core.hooksPath=.githooks"
