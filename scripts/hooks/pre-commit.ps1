Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Push-Location $RepoRoot

try {
  $initializer = Join-Path $RepoRoot "scripts\Initialize-WindowsProcessEnvironment.ps1"
  if (Test-Path -LiteralPath $initializer) {
    . $initializer
    if (Get-Command Initialize-WindowsProcessEnvironment -ErrorAction SilentlyContinue) {
      Initialize-WindowsProcessEnvironment | Out-Null
    }
  }

  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    throw "Python command not found on PATH"
  }

  Write-Host "pre-commit: Contract gate"
  & (Join-Path $RepoRoot "scripts\verify-repo.ps1") -Check Contract
  if ($LASTEXITCODE -ne 0) {
    throw "Contract gate failed"
  }

  Write-Host "pre-commit: Codex executable reference guard"
  & $python.Source -m unittest tests.runtime.test_codex_executable_reference_guard
  if ($LASTEXITCODE -ne 0) {
    throw "Codex executable reference guard failed"
  }

  Write-Host "pre-commit: target repo rollout hook checks passed"
}
finally {
  Pop-Location
}
