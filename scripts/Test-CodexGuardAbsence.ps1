[CmdletBinding()]
param(
    [string] $TaskName = 'codex-cockpit-switch-guard',
    [string] $CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$startupLauncherPath = Join-Path ([Environment]::GetFolderPath('Startup')) "$TaskName.vbs"
$installedScriptsRoot = Join-Path $CodexHome 'scripts'
$retiredInstalledFiles = @(
    'codex-cockpit-switch-guard.py',
    'Start-CodexCockpitSwitchGuard.ps1',
    'Install-CodexCockpitNoopLauncher.ps1',
    'Start-CodexShared.ps1',
    'Switch-CodexAccount.ps1'
)

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
$guardPythonPattern = '(^|[\s"''])\S*codex-cockpit-switch-guard\.py([\s"'']|$)'
$guardPowerShellPattern = '(^|[\s"''])\S*Start-CodexCockpitSwitchGuard\.ps1([\s"'']|$)'
$processes = @()
if ($TaskName -eq 'codex-cockpit-switch-guard') {
    $processFilter = {
        $_.CommandLine -and
        $_.ProcessId -ne $PID -and
        -not $_.CommandLine.Contains('Test-CodexGuardAbsence.ps1') -and
        (
            $_.CommandLine -match $guardPythonPattern -or
            $_.CommandLine -match $guardPowerShellPattern
        )
    }
    try {
        $processes = @(
            Get-CimInstance Win32_Process -Filter "CommandLine LIKE '%codex-cockpit-switch-guard.py%' OR CommandLine LIKE '%Start-CodexCockpitSwitchGuard.ps1%'" |
                Where-Object $processFilter |
                Select-Object Name, ProcessId, ParentProcessId, CreationDate, CommandLine
        )
    }
    catch {
        $processes = @(
            Get-CimInstance Win32_Process |
                Where-Object $processFilter |
                Select-Object Name, ProcessId, ParentProcessId, CreationDate, CommandLine
        )
    }
}
$presentInstalledFiles = @(
    foreach ($name in $retiredInstalledFiles) {
        $path = Join-Path $installedScriptsRoot $name
        if (Test-Path -LiteralPath $path) {
            $path
        }
    }
)

$findings = @()
if ($task) {
    $findings += "scheduled_task_present"
}
if (Test-Path -LiteralPath $startupLauncherPath) {
    $findings += "startup_launcher_present"
}
if ($processes.Count -gt 0) {
    $findings += "guard_process_present"
}
if ($presentInstalledFiles.Count -gt 0) {
    $findings += "retired_installed_script_present"
}

[pscustomobject]@{
    status = if ($findings.Count -eq 0) { 'pass' } else { 'fail' }
    task_name = $TaskName
    scheduled_task_present = [bool]$task
    startup_launcher_path = $startupLauncherPath
    startup_launcher_present = Test-Path -LiteralPath $startupLauncherPath
    process_count = $processes.Count
    process_ids = @($processes | ForEach-Object { $_.ProcessId })
    installed_scripts_root = $installedScriptsRoot
    retired_installed_files_present = $presentInstalledFiles
    findings = $findings
    expected = 'No Codex/Cockpit background guard task, startup fallback, worker process, or retired installed wrapper should exist.'
} | ConvertTo-Json -Depth 5

if ($findings.Count -gt 0) {
    exit 2
}
