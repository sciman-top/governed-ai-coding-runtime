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
$startupLauncherPath = Join-Path ([Environment]::GetFolderPath('Startup')) "$TaskName.vbs"

function Resolve-PwshPath {
    $command = Get-Command pwsh -ErrorAction Stop | Select-Object -First 1
    return [string]$command.Source
}

function Write-StartupLauncher {
    param(
        [Parameter(Mandatory = $true)][string] $LauncherPath,
        [Parameter(Mandatory = $true)][string] $PwshPath
    )

    [string] $pwshExecutable = @($PwshPath -split '\r?\n' | Where-Object { $_.Trim() } | Select-Object -First 1)[0].Trim()
    $arguments = @(
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
    [string] $command = '"' + $pwshExecutable + '" ' + (($arguments | ForEach-Object { '"' + ($_ -replace '"', '""') + '"' }) -join ' ')
    [string] $escapedCommand = ($command -replace '"', '""') -replace '[\r\n]+', ''
    $vbs = @(
        'Set shell = CreateObject("WScript.Shell")',
        ('shell.Run "{0}", 0, False' -f $escapedCommand)
    ) -join "`r`n"
    Set-Content -LiteralPath $LauncherPath -Value $vbs -Encoding ASCII
}

if ($RunWorker) {
    $python = (Get-Command python -ErrorAction Stop).Source
    $guardScript = Join-Path $PSScriptRoot 'codex-cockpit-switch-guard.py'
    $repairScript = Join-Path $PSScriptRoot 'codex-interop-check.py'
    & $python $guardScript `
        --codex-home $CodexHome `
        --cockpit-home $CockpitHome `
        --cc-switch-db $CcSwitchDb `
        --repair-script $repairScript `
        --watch `
        --log-path $logPath
    exit $LASTEXITCODE
}

if ($InstallTask) {
    $pwsh = Resolve-PwshPath
    $action = New-ScheduledTaskAction -Execute $pwsh -Argument (
        '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}" -RunWorker -CodexHome "{1}" -CockpitHome "{2}" -CcSwitchDb "{3}"' -f
        $PSCommandPath,
        $CodexHome,
        $CockpitHome,
        $CcSwitchDb
    )
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 7)
    try {
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description 'Projects Cockpit Tools current Codex account into Codex live config/auth/history without launching or killing Codex.' -Force | Out-Null
        if (Test-Path -LiteralPath $startupLauncherPath) {
            Remove-Item -LiteralPath $startupLauncherPath -Force
        }
        Write-Host "Installed scheduled task: $TaskName"
    }
    catch {
        Write-StartupLauncher -LauncherPath $startupLauncherPath -PwshPath $pwsh
        Write-Host "Scheduled task install failed; installed startup launcher fallback: $startupLauncherPath"
    }
}
elseif ($UninstallTask) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue | Out-Null
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
    if (Test-Path -LiteralPath $startupLauncherPath) {
        Remove-Item -LiteralPath $startupLauncherPath -Force
        Write-Host "Removed startup launcher fallback: $startupLauncherPath"
    }
    Write-Host "Uninstalled scheduled task: $TaskName"
}
elseif ($Start) {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($task) {
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "Started scheduled task: $TaskName"
    }
    else {
        $pwsh = Resolve-PwshPath
        Start-Process -FilePath $pwsh -ArgumentList @(
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
        ) -WindowStyle Hidden | Out-Null
        Write-Host "Started guard process fallback: $TaskName"
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
        startup_launcher_path = $startupLauncherPath
        startup_launcher_exists = Test-Path -LiteralPath $startupLauncherPath
        issue = if ($processes.Count -eq 0) { 'guard_worker_not_running' } else { $null }
    } | ConvertTo-Json -Depth 4
}
