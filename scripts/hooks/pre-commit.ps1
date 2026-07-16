Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Push-Location $RepoRoot

try {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    throw "Python command not found on PATH"
  }

  foreach ($gate in @("build", "test")) {
    Write-Host "pre-commit: rulesctl $gate"
    & $python.Source (Join-Path $RepoRoot "scripts\rulesctl.py") $gate
    if ($LASTEXITCODE -ne 0) {
      throw "rulesctl $gate failed"
    }
  }

  Write-Host "pre-commit: rulesctl contract (repo-local quick feedback)"
  & $python.Source (Join-Path $RepoRoot "scripts\rulesctl.py") contract --skip-targets
  if ($LASTEXITCODE -ne 0) {
    throw "rulesctl contract failed"
  }

  Write-Host "pre-commit: quick feedback passed; full delivery still requires rulesctl verify"
}
finally {
  Pop-Location
}
