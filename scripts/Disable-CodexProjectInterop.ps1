[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),
    [string] $CockpitHome = $(Join-Path $HOME '.antigravity_cockpit'),
    [string] $BinDir = $(Join-Path $HOME '.local\bin'),
    [string] $TaskName = 'codex-cockpit-switch-guard',
    [string] $EvidenceDir = $(Join-Path (Get-Location) 'docs\change-evidence'),
    [switch] $Apply,
    [switch] $DisableProjectShortcuts
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupRoot = Join-Path $CodexHome "backups\disable-project-interop-$timestamp"
$actions = New-Object System.Collections.Generic.List[object]

function Add-Action {
    param(
        [string] $Id,
        [string] $Status,
        [hashtable] $Data = @{}
    )
    $entry = [ordered]@{
        id = $Id
        status = $Status
    }
    foreach ($key in $Data.Keys) {
        $entry[$key] = $Data[$key]
    }
    $actions.Add([pscustomobject]$entry) | Out-Null
}

function Backup-File {
    param([string] $Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    if ($Apply) {
        New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
        $name = Split-Path -Leaf $Path
        $safeParent = (Split-Path -Parent $Path).Replace(':', '').Replace('\', '_').Replace('/', '_')
        $destination = Join-Path $backupRoot "$safeParent--$name"
        Copy-Item -LiteralPath $Path -Destination $destination -Force
        return $destination
    }
    return "dry-run:$Path"
}

function Set-JsonProperty {
    param(
        [Parameter(Mandatory)] $Object,
        [Parameter(Mandatory)] [string] $Name,
        [AllowNull()] $Value
    )
    $property = $Object.PSObject.Properties[$Name]
    if ($property) {
        $property.Value = $Value
    }
    else {
        $Object | Add-Member -NotePropertyName $Name -NotePropertyValue $Value
    }
}

function Rename-IfExists {
    param([string] $Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Add-Action -Id 'shortcut_absent' -Status 'ok' -Data @{ path = $Path }
        return
    }
    $target = "$Path.disabled-$timestamp"
    $binRootFullPath = [System.IO.Path]::GetFullPath($BinDir).TrimEnd('\') + '\'
    $pathFullPath = [System.IO.Path]::GetFullPath($Path)
    $targetFullPath = [System.IO.Path]::GetFullPath($target)
    if (-not $pathFullPath.StartsWith($binRootFullPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to disable shortcut outside bin dir: $Path"
    }
    if (-not $targetFullPath.StartsWith($binRootFullPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to move shortcut outside bin dir: $target"
    }
    if ($Apply) {
        Move-Item -LiteralPath $Path -Destination $target -Force
    }
    Add-Action -Id 'shortcut_disabled' -Status $(if ($Apply) { 'changed' } else { 'would_change' }) -Data @{
        path = $Path
        disabled_path = $target
    }
}

function Get-CockpitProcesses {
    @(Get-CimInstance Win32_Process | Where-Object {
        ($_.Name -match '^(cockpit-tools|Cockpit Tools)(\.exe)?$') -or
        ($_.CommandLine -and $_.CommandLine -match 'Cockpit Tools\\cockpit-tools\.exe')
    })
}

function Get-LatestCockpitLogPath {
    $logDir = Join-Path $CockpitHome 'logs'
    if (-not (Test-Path -LiteralPath $logDir -PathType Container)) {
        return $null
    }
    $latest = Get-ChildItem -LiteralPath $logDir -Filter 'app.log*' -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($latest) {
        return $latest.FullName
    }
    return $null
}

function Get-CockpitRecentCodexLaunchLines {
    $logPath = Get-LatestCockpitLogPath
    if (-not $logPath) {
        return @()
    }
    @(Select-String -LiteralPath $logPath -Pattern '已关闭切换 Codex 时自动启动 Codex App|Codex Start|Codex 启动|启动 Codex' -ErrorAction SilentlyContinue |
        Select-Object -Last 20 |
        ForEach-Object { $_.Line })
}

function Get-LogLineTimestamp {
    param([AllowNull()] [string] $Line)
    if (-not $Line) {
        return $null
    }
    if ($Line -notmatch '^(\d{4}-\d{2}-\d{2}T\S+)') {
        return $null
    }
    try {
        return [datetimeoffset]::Parse($Matches[1])
    }
    catch {
        return $null
    }
}

$cockpitConfigPath = Join-Path $CockpitHome 'config.json'
$cockpitInstancesPath = Join-Path $CockpitHome 'codex_instances.json'
$codexConfigPath = Join-Path $CodexHome 'config.toml'
$codexAuthPath = Join-Path $CodexHome 'auth.json'
$stateDbPath = Join-Path $CodexHome 'state_5.sqlite'

foreach ($path in @($cockpitConfigPath, $cockpitInstancesPath, $codexConfigPath, $codexAuthPath, $stateDbPath)) {
    $backup = Backup-File -Path $path
    if ($backup) {
        Add-Action -Id 'backup_file' -Status $(if ($Apply) { 'ok' } else { 'would_backup' }) -Data @{
            path = $path
            backup = $backup
        }
    }
}

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($task) {
    Add-Action -Id 'guard_task_found' -Status 'attention' -Data @{
        task_name = $TaskName
        state = $task.State.ToString()
    }
    if ($Apply) {
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue | Out-Null
        Disable-ScheduledTask -TaskName $TaskName | Out-Null
    }
    Add-Action -Id 'guard_task_disabled' -Status $(if ($Apply) { 'changed' } else { 'would_change' }) -Data @{ task_name = $TaskName }
}
else {
    Add-Action -Id 'guard_task_absent' -Status 'ok' -Data @{ task_name = $TaskName }
}

$guardProcesses = @(Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -and
    $_.CommandLine.Contains('codex-cockpit-switch-guard.py') -and
    $_.Name -match '^(python|python3)(\.exe)?$'
})
foreach ($process in $guardProcesses) {
    if ($Apply) {
        Stop-Process -Id $process.ProcessId -Force
    }
    Add-Action -Id 'guard_process_stopped' -Status $(if ($Apply) { 'changed' } else { 'would_change' }) -Data @{
        process_id = $process.ProcessId
    }
}

if (Test-Path -LiteralPath $cockpitConfigPath -PathType Leaf) {
    $config = Get-Content -LiteralPath $cockpitConfigPath -Raw | ConvertFrom-Json
    $before = [ordered]@{
        codex_app_path = $config.codex_app_path
        codex_launch_on_switch = $config.codex_launch_on_switch
        codex_restart_specified_app_on_switch = $config.codex_restart_specified_app_on_switch
        codex_specified_app_path = $config.codex_specified_app_path
        antigravity_dual_switch_no_restart_enabled = $config.antigravity_dual_switch_no_restart_enabled
    }
    Set-JsonProperty -Object $config -Name 'codex_app_path' -Value ''
    Set-JsonProperty -Object $config -Name 'codex_restart_specified_app_on_switch' -Value $false
    Set-JsonProperty -Object $config -Name 'codex_specified_app_path' -Value ''
    Set-JsonProperty -Object $config -Name 'antigravity_dual_switch_no_restart_enabled' -Value $false
    if ($Apply) {
        $config | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $cockpitConfigPath -Encoding utf8
    }
    Add-Action -Id 'cockpit_project_launch_interception_removed' -Status $(if ($Apply) { 'changed' } else { 'would_change' }) -Data @{
        path = $cockpitConfigPath
        before = $before
        preserved_codex_launch_on_switch = $config.codex_launch_on_switch
    }
}
else {
    Add-Action -Id 'cockpit_config_missing' -Status 'attention' -Data @{ path = $cockpitConfigPath }
}

if (Test-Path -LiteralPath $cockpitInstancesPath -PathType Leaf) {
    $instances = Get-Content -LiteralPath $cockpitInstancesPath -Raw | ConvertFrom-Json
    if ($instances.defaultSettings) {
        Set-JsonProperty -Object $instances.defaultSettings -Name 'followLocalAccount' -Value $true
        Set-JsonProperty -Object $instances.defaultSettings -Name 'bindAccountId' -Value $null
        Set-JsonProperty -Object $instances.defaultSettings -Name 'launchMode' -Value 'app'
    }
    foreach ($propertyName in @('lastPid', 'last_pid')) {
        if ($instances.PSObject.Properties[$propertyName]) {
            $instances.PSObject.Properties[$propertyName].Value = $null
        }
    }
    if ($Apply) {
        $instances | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $cockpitInstancesPath -Encoding utf8
    }
    Add-Action -Id 'cockpit_instances_follow_current_account' -Status $(if ($Apply) { 'changed' } else { 'would_change' }) -Data @{ path = $cockpitInstancesPath }
}

if (Test-Path -LiteralPath $stateDbPath -PathType Leaf) {
    $python = (Get-Command python -ErrorAction Stop).Source
    $code = @'
import json
import sqlite3
import sys

path = sys.argv[1]
apply = sys.argv[2] == "1"
trigger_names = [
    "trg_threads_shared_provider_after_insert",
    "trg_threads_shared_provider_after_update",
]
conn = sqlite3.connect(path)
try:
    existing = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger' AND name IN ({})".format(
                ",".join("?" for _ in trigger_names)
            ),
            trigger_names,
        )
    ]
    if apply:
        for name in trigger_names:
            conn.execute(f"DROP TRIGGER IF EXISTS {name}")
        conn.commit()
    print(json.dumps({"existing": existing, "dropped": existing if apply else []}, ensure_ascii=False))
finally:
    conn.close()
'@
    $sqliteResult = & $python -c $code $stateDbPath $(if ($Apply) { '1' } else { '0' })
    Add-Action -Id 'codex_provider_bucket_triggers_removed' -Status $(if ($Apply) { 'changed' } else { 'would_change' }) -Data @{
        path = $stateDbPath
        result = ($sqliteResult | ConvertFrom-Json)
    }
}

Rename-IfExists -Path (Join-Path $BinDir 'codex-cockpit-noop-launcher.exe')
Rename-IfExists -Path (Join-Path $BinDir 'codex-cockpit-install-noop-launcher.cmd')

$disabledProjectShortcuts = [bool]$DisableProjectShortcuts

if ($DisableProjectShortcuts) {
    $shortcutNames = @(
        'codex.cmd',
        'codex.ps1',
        'codex-account.cmd',
        'codex-account.ps1',
        'codex-cockpit.cmd',
        'codex-cockpit-exec.cmd',
        'codex-cockpit-resume.cmd',
        'codex-cockpit-app.cmd',
        'codex-cockpit-app-restart.cmd',
        'codex-shared.cmd',
        'codex-shared-exec.cmd',
        'codex-shared-resume.cmd',
        'codex-shared-app.cmd',
        'codex-relay.cmd',
        'codex-relay-exec.cmd',
        'codex-relay-resume.cmd',
        'codex-relay-app.cmd',
        'codex-interop-check.cmd',
        'codex-interop-repair.cmd',
        'codex-switch-guard.cmd',
        'codex-switch-guard-status.cmd',
        'codex-switch-guard-start.cmd'
    )
    foreach ($name in $shortcutNames) {
        Rename-IfExists -Path (Join-Path $BinDir $name)
    }
}

$cockpitProcesses = @(Get-CockpitProcesses)
$recentCodexLaunchLines = @(Get-CockpitRecentCodexLaunchLines)
$latestDisabledLaunchLine = $recentCodexLaunchLines |
    Where-Object { $_ -match '已关闭切换 Codex 时自动启动 Codex App' } |
    Select-Object -Last 1
if ($cockpitProcesses.Count -gt 0) {
    $latestProcessStart = $cockpitProcesses |
        Sort-Object CreationDate -Descending |
        Select-Object -First 1 -ExpandProperty CreationDate
    $latestDisabledLaunchAt = Get-LogLineTimestamp -Line $latestDisabledLaunchLine
    $disabledAfterCurrentStart = $false
    if ($latestProcessStart -and $latestDisabledLaunchAt) {
        $disabledAfterCurrentStart = $latestDisabledLaunchAt -gt ([datetimeoffset]$latestProcessStart)
    }
    if ($disabledAfterCurrentStart) {
        Add-Action -Id 'cockpit_runtime_reload_required' -Status 'attention' -Data @{
            process_ids = @($cockpitProcesses | ForEach-Object { $_.ProcessId })
            latest_process_start = $latestProcessStart.ToString('o')
            reason = 'Cockpit Tools caches config.json in process memory; external disk repair is not hot-loaded by the running process.'
            remediation = 'Reload Cockpit Tools or toggle/save the Cockpit UI setting for Codex launch-on-switch before expecting native Codex App launch.'
            latest_disabled_launch_log = $latestDisabledLaunchLine
        }
    }
    else {
        Add-Action -Id 'cockpit_runtime_config_reload_not_currently_indicated' -Status 'ok' -Data @{
            process_ids = @($cockpitProcesses | ForEach-Object { $_.ProcessId })
            latest_process_start = $(if ($latestProcessStart) { $latestProcessStart.ToString('o') } else { $null })
            latest_disabled_launch_log = $latestDisabledLaunchLine
            reason = 'No disabled Codex native-launch log was observed after the latest running Cockpit Tools process start.'
        }
    }
}
else {
    Add-Action -Id 'cockpit_not_running' -Status 'ok' -Data @{
        reason = 'No running Cockpit Tools process holds stale in-memory launch settings.'
    }
}

$backupRootForReport = ''
if ($Apply) {
    $backupRootForReport = $backupRoot
}
$applyForReport = [bool]$Apply

$report = [ordered]@{}
$report['timestamp'] = $timestamp
$report['apply'] = $applyForReport
$report['codex_home'] = $CodexHome
$report['cockpit_home'] = $CockpitHome
$report['bin_dir'] = $BinDir
$report['backup_root'] = $backupRootForReport
$report['disabled_project_shortcuts'] = $disabledProjectShortcuts
$report['actions'] = @($actions.ToArray())

New-Item -ItemType Directory -Path $EvidenceDir -Force | Out-Null
$evidencePath = Join-Path $EvidenceDir "disable-codex-project-interop-$timestamp.json"
$report | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $evidencePath -Encoding utf8
$report['evidence_path'] = $evidencePath
$report | ConvertTo-Json -Depth 30
