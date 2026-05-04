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

# Skeleton entrypoint for low-latency local checks.
$result = Invoke-RepoProfileGateRun `
  -Mode "fast" `
  -RepoProfilePath $RepoProfilePath `
  -WorkingDirectory $WorkingDirectory `
  -MilestoneTag $MilestoneTag `
  -GateTimeoutSeconds $GateTimeoutSeconds `
  -MaxGateCount $MaxGateCount `
  -ContinueOnError:$ContinueOnError.IsPresent `
  -DisableAutoCommit:$DisableAutoCommit.IsPresent `
  -JsonOutput:$Json.IsPresent

exit ([int]$result.exit_code)
