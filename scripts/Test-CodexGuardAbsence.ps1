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
$processes = @(
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.CommandLine -and
            (
                $_.CommandLine.Contains('codex-cockpit-switch-guard.py') -or
                $_.CommandLine.Contains('Start-CodexCockpitSwitchGuard.ps1')
            )
        } |
        Select-Object Name, ProcessId, ParentProcessId, CreationDate, CommandLine
)
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
