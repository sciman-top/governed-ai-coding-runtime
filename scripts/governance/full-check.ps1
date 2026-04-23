param(
  [string]$RepoProfilePath = ".governed-ai/repo-profile.json",
  [string]$WorkingDirectory = "",
  [string]$MilestoneTag = "",
  [int]$GateTimeoutSeconds = 0,
  [switch]$ContinueOnError,
  [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptRoot "gate-runner-common.ps1")

# Skeleton entrypoint for release-preflight checks.
$result = Invoke-RepoProfileGateRun `
  -Mode "full" `
  -RepoProfilePath $RepoProfilePath `
  -WorkingDirectory $WorkingDirectory `
  -MilestoneTag $MilestoneTag `
  -GateTimeoutSeconds $GateTimeoutSeconds `
  -ContinueOnError:$ContinueOnError.IsPresent `
  -JsonOutput:$Json.IsPresent

exit ([int]$result.exit_code)
