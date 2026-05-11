[CmdletBinding(DefaultParameterSetName = 'Status')]
param(
    [Parameter(ParameterSetName = 'Install')]
    [switch] $InstallTask,

    [Parameter(ParameterSetName = 'Uninstall')]
    [switch] $UninstallTask,

    [Parameter(ParameterSetName = 'Start')]
    [switch] $Start,

    [Parameter(ParameterSetName = 'Stop')]
    [switch] $Stop,

    [Parameter(ParameterSetName = 'RunWorker')]
    [switch] $RunWorker,

    [Parameter(ParameterSetName = 'Status')]
    [switch] $Status,

    [string] $TaskName = 'codex-cockpit-switch-guard',

    [string] $CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),

    [string] $CockpitHome = $(Join-Path $HOME '.antigravity_cockpit'),

    [string] $CcSwitchDb = $(Join-Path (Join-Path $HOME '.cc-switch') 'cc-switch.db')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-GuardProcess {
    $pattern = 'codex-cockpit-switch-guard.py'
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.CommandLine -and
            $_.CommandLine.Contains($pattern) -and
            $_.Name -match '^(python|python3)(\.exe)?$'
        } |
        Select-Object Name, ProcessId, ParentProcessId, CreationDate, CommandLine
}

$logPath = Join-Path (Join-Path $CodexHome 'log') 'codex-cockpit-switch-guard.jsonl'

$deprecatedReason = 'codex-cockpit-switch-guard is deprecated. Cockpit Tools owns Codex auth/API switching and launch-on-switch; this project must not install or start a background repair guard.'

if ($RunWorker) {
    Write-Error $deprecatedReason
    exit 2
}

if ($InstallTask) {
    Write-Error $deprecatedReason
    exit 2
}
elseif ($UninstallTask) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue | Out-Null
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
    Write-Host "Uninstalled scheduled task: $TaskName"
}
elseif ($Start) {
    Write-Error $deprecatedReason
    exit 2
}
elseif ($Stop) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue | Out-Null
    Get-GuardProcess | ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force
        Write-Host "Stopped guard process: $($_.ProcessId)"
    }
}
else {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    $processes = @(Get-GuardProcess)
    [pscustomobject]@{
        task_name = $TaskName
        task_state = if ($task) { $task.State } else { 'not_installed' }
        healthy = $processes.Count -gt 0
        process_count = $processes.Count
        process_ids = @($processes | ForEach-Object { $_.ProcessId })
        log_path = $logPath
        issue = if ($processes.Count -eq 0) { 'guard_worker_not_running' } else { $null }
    } | ConvertTo-Json -Depth 4
}
