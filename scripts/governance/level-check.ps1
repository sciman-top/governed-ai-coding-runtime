param(
  [string]$RepoProfilePath = ".governed-ai/repo-profile.json",
  [string]$WorkingDirectory = "",
  [ValidateSet("l1", "l2", "l3", "quick", "fast", "full")]
  [string]$Level = "l1",
  [string]$MilestoneTag = "",
  [int]$GateTimeoutSeconds = 0,
  [int]$MaxGateCount = 50,
  [switch]$ContinueOnError,
  [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptRoot "gate-runner-common.ps1")

# Layered entrypoint for explicit l1/l2/l3 target-repo gate runs.
$result = Invoke-RepoProfileGateRun `
  -Mode $Level `
  -RepoProfilePath $RepoProfilePath `
  -WorkingDirectory $WorkingDirectory `
  -MilestoneTag $MilestoneTag `
  -GateTimeoutSeconds $GateTimeoutSeconds `
  -MaxGateCount $MaxGateCount `
  -ContinueOnError:$ContinueOnError.IsPresent `
  -JsonOutput:$Json.IsPresent

exit ([int]$result.exit_code)
