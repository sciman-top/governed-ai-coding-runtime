param(
  [string]$RepoProfilePath = ".governed-ai/repo-profile.json",
  [string]$WorkingDirectory = "",
  [string]$MilestoneTag = "",
  [int]$GateTimeoutSeconds = 0,
  [int]$MaxGateCount = 50,
  [switch]$ContinueOnError,
  [switch]$DisableAutoCommit,
  [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptRoot "gate-runner-common.ps1")

$resolvedProfilePath = Resolve-RepoProfilePath -RepoProfilePath $RepoProfilePath
$resolvedWorkingDirectory = Resolve-GateWorkingDirectory -ResolvedRepoProfilePath $resolvedProfilePath -WorkingDirectory $WorkingDirectory

$result = Invoke-RepoProfileGateRun `
  -Mode "full" `
  -RepoProfilePath $RepoProfilePath `
  -WorkingDirectory $resolvedWorkingDirectory `
  -MilestoneTag $MilestoneTag `
  -GateTimeoutSeconds $GateTimeoutSeconds `
  -MaxGateCount $MaxGateCount `
  -ContinueOnError:$ContinueOnError.IsPresent `
  -DisableAutoCommit:$DisableAutoCommit.IsPresent `
  -JsonOutput:$false

if ($result.exit_code -ne 0) {
  exit ([int]$result.exit_code)
}

$docsCheck = & pwsh -NoProfile -ExecutionPolicy Bypass -File "scripts/verify-repo.ps1" -Check Docs 2>&1
if ($LASTEXITCODE -ne 0) {
  $detail = (($docsCheck | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
  throw "Release-preflight Docs checks failed`n$detail"
}
Write-Host ($docsCheck | Out-String).TrimEnd()

$scriptsCheck = & pwsh -NoProfile -ExecutionPolicy Bypass -File "scripts/verify-repo.ps1" -Check Scripts 2>&1
if ($LASTEXITCODE -ne 0) {
  $detail = (($scriptsCheck | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
  throw "Release-preflight Scripts checks failed`n$detail"
}
Write-Host ($scriptsCheck | Out-String).TrimEnd()

$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
  throw "git is required for release preflight"
}

$diffCheck = & $git.Source diff --check 2>&1
if ($LASTEXITCODE -ne 0) {
  $detail = (($diffCheck | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
  throw "Release-preflight git diff check failed`n$detail"
}
if ($diffCheck) {
  Write-Host ($diffCheck | Out-String).TrimEnd()
}

if ($Json.IsPresent) {
  $payload = [ordered]@{
    exit_code = 0
    summary = [ordered]@{
      entrypoint = "scripts/governance/preflight.ps1"
      release_ready = $true
      extra_checks = @(
        "scripts/verify-repo.ps1 -Check Docs",
        "scripts/verify-repo.ps1 -Check Scripts",
        "git diff --check"
      )
      base_gate_summary = $result.summary
    }
  }
  Write-Host ($payload | ConvertTo-Json -Depth 10)
}

exit 0
