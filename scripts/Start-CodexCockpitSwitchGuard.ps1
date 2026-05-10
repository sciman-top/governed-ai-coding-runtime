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

function New-GuardTaskSettings {
    try {
        return New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -StartWhenAvailable `
            -ExecutionTimeLimit ([timespan]::Zero) `
            -RestartCount 999 `
            -RestartInterval (New-TimeSpan -Minutes 1)
    }
    catch {
        return New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -StartWhenAvailable `
            -ExecutionTimeLimit ([timespan]::Zero)
    }
}

function Start-GuardProcessFallback {
    $pwshPath = (Get-Command pwsh).Source
    $argumentList = @(
        '-NoProfile',
        '-ExecutionPolicy',
        'Bypass',
        '-WindowStyle',
        'Hidden',
        '-File',
        $PSCommandPath,
        '-RunWorker',
        '-CodexHome',
        $CodexHome,
        '-CockpitHome',
        $CockpitHome,
        '-CcSwitchDb',
        $CcSwitchDb
    )
    Start-Process -FilePath $pwshPath -ArgumentList $argumentList -WindowStyle Hidden -PassThru
}

function Wait-GuardProcess {
    param([int] $TimeoutSeconds = 8)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        $processes = @(Get-GuardProcess)
        if ($processes.Count -gt 0) {
            return $processes
        }
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $deadline)
    return @()
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$guardScript = Join-Path $PSScriptRoot 'codex-cockpit-switch-guard.py'
$logPath = Join-Path (Join-Path $CodexHome 'log') 'codex-cockpit-switch-guard.jsonl'

if ($RunWorker) {
    & python $guardScript `
        --watch `
        --codex-home $CodexHome `
        --cockpit-home $CockpitHome `
        --cc-switch-db $CcSwitchDb `
        --log-path $logPath
    exit $LASTEXITCODE
}

if ($InstallTask) {
    $pwshPath = (Get-Command pwsh).Source
    $argument = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSCommandPath`" -RunWorker -CodexHome `"$CodexHome`" -CockpitHome `"$CockpitHome`" -CcSwitchDb `"$CcSwitchDb`""
    $action = New-ScheduledTaskAction -Execute $pwshPath -Argument $argument
    $logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
    $settings = New-GuardTaskSettings
    $settings.MultipleInstances = 'IgnoreNew'
    $settings.StopIfGoingOnBatteries = $false
    $settings.Hidden = $true
    try {
        $startupTrigger = New-ScheduledTaskTrigger -AtStartup
        $task = New-ScheduledTask -Action $action -Trigger @($logonTrigger, $startupTrigger) -Principal $principal -Settings $settings
        Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force | Out-Null
        Write-Host "Installed scheduled task: $TaskName (logon_and_startup)"
    }
    catch {
        $task = New-ScheduledTask -Action $action -Trigger $logonTrigger -Principal $principal -Settings $settings
        Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force | Out-Null
        Write-Host "Installed scheduled task: $TaskName (logon_only_fallback)"
    }
}
elseif ($UninstallTask) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue | Out-Null
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
    Write-Host "Uninstalled scheduled task: $TaskName"
}
elseif ($Start) {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($task) {
        Start-ScheduledTask -TaskName $TaskName
        $processes = @(Wait-GuardProcess)
        if ($processes.Count -gt 0) {
            Write-Host "Started scheduled task: $TaskName"
        }
        else {
            $process = Start-GuardProcessFallback
            Write-Host "Scheduled task did not produce a guard worker; started fallback process: $($process.Id)"
        }
    }
    else {
        $process = Start-GuardProcessFallback
        Write-Host "Started guard process: $($process.Id)"
    }
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
