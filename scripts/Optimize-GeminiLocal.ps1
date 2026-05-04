[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch] $Apply,
    [string] $GeminiHome = $(Join-Path $HOME '.gemini')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RequiredSecretEnvVars = @(
    'ANTHROPIC_AUTH_TOKEN',
    'ANTHROPIC_API_KEY',
    'ANTHROPIC_CUSTOM_HEADERS',
    'GITHUB_PERSONAL_ACCESS_TOKEN',
    'GITHUB_TOKEN',
    'GH_TOKEN',
    'OPENAI_API_KEY',
    'GEMINI_API_KEY',
    'GOOGLE_API_KEY',
    'NPM_TOKEN'
)

function Read-JsonMap {
    param([string] $Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return @{}
    }
    $raw = Get-Content -LiteralPath $Path -Raw
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return @{}
    }
    return ConvertFrom-Json -InputObject $raw -AsHashtable
}

function Ensure-Map {
    param(
        [hashtable] $Map,
        [string[]] $Path
    )
    $current = $Map
    foreach ($part in $Path) {
        if (-not $current.ContainsKey($part) -or -not ($current[$part] -is [hashtable])) {
            $current[$part] = @{}
        }
        $current = $current[$part]
    }
    return $current
}

function Get-StringArray {
    param([object] $Value)
    if ($null -eq $Value) {
        return @()
    }
    if ($Value -is [array]) {
        return @($Value | ForEach-Object { [string]$_ } | Where-Object { $_ })
    }
    return @([string]$Value)
}

function Merge-Strings {
    param([object[]] $Values)
    $set = [ordered]@{}
    foreach ($value in $Values) {
        foreach ($item in (Get-StringArray -Value $value)) {
            $text = [string]$item
            if (-not [string]::IsNullOrWhiteSpace($text) -and -not $set.Contains($text)) {
                $set[$text] = $true
            }
        }
    }
    return @($set.Keys)
}

function Set-IfChanged {
    param(
        [hashtable] $Map,
        [string] $Key,
        [object] $Value,
        [string] $ChangeId,
        [System.Collections.Generic.List[string]] $Changes
    )
    $before = $null
    $hadKey = $Map.ContainsKey($Key)
    if ($hadKey) {
        $before = $Map[$Key]
    }
    $beforeJson = ConvertTo-Json $before -Depth 20 -Compress
    $afterJson = ConvertTo-Json $Value -Depth 20 -Compress
    if (-not $hadKey -or $beforeJson -ne $afterJson) {
        $Map[$Key] = $Value
        $Changes.Add($ChangeId)
    }
}

$resolvedHome = Resolve-Path -LiteralPath $GeminiHome -ErrorAction SilentlyContinue
if ($resolvedHome) {
    $GeminiHome = $resolvedHome.Path
}
else {
    $GeminiHome = [System.IO.Path]::GetFullPath($GeminiHome)
}

$mainPath = Join-Path $GeminiHome 'settings.json'
$antigravityDir = Join-Path $GeminiHome 'antigravity'
$antigravityPath = Join-Path $antigravityDir 'settings.json'
$ignorePath = Join-Path $GeminiHome '.geminiignore'

$main = Read-JsonMap -Path $mainPath
$target = Read-JsonMap -Path $antigravityPath
$changes = [System.Collections.Generic.List[string]]::new()

if (-not $target.ContainsKey('$schema') -and $main.ContainsKey('$schema')) {
    $target['$schema'] = $main['$schema']
    $changes.Add('schema_from_main')
}

$admin = Ensure-Map -Map $target -Path @('admin')
Set-IfChanged -Map $admin -Key 'secureModeEnabled' -Value $true -ChangeId 'admin.secureModeEnabled=true' -Changes $changes

$security = Ensure-Map -Map $target -Path @('security')
$redaction = Ensure-Map -Map $target -Path @('security', 'environmentVariableRedaction')
$mainBlocked = @()
if ($main.ContainsKey('security') -and $main['security'].ContainsKey('environmentVariableRedaction')) {
    $mainBlocked = @(Get-StringArray -Value $main['security']['environmentVariableRedaction']['blocked'])
}
Set-IfChanged -Map $redaction -Key 'enabled' -Value $true -ChangeId 'security.environmentVariableRedaction.enabled=true' -Changes $changes
Set-IfChanged -Map $redaction -Key 'blocked' -Value @(Merge-Strings -Values @($mainBlocked, $RequiredSecretEnvVars)) -ChangeId 'security.environmentVariableRedaction.blocked' -Changes $changes

$advanced = Ensure-Map -Map $target -Path @('advanced')
$mainExcludedEnv = @()
if ($main.ContainsKey('advanced') -and $main['advanced'].ContainsKey('excludedEnvVars')) {
    $mainExcludedEnv = @(Get-StringArray -Value $main['advanced']['excludedEnvVars'])
}
Set-IfChanged -Map $advanced -Key 'excludedEnvVars' -Value @(Merge-Strings -Values @($mainExcludedEnv, $RequiredSecretEnvVars)) -ChangeId 'advanced.excludedEnvVars' -Changes $changes

$fileFiltering = Ensure-Map -Map $target -Path @('context', 'fileFiltering')
$mainIgnorePaths = @()
if ($main.ContainsKey('context') -and $main['context'].ContainsKey('fileFiltering')) {
    $mainIgnorePaths = @(Get-StringArray -Value $main['context']['fileFiltering']['customIgnoreFilePaths'])
}
$targetIgnorePaths = if ($mainIgnorePaths.Count -gt 0) { $mainIgnorePaths } else { @($ignorePath.Replace('\', '/')) }
Set-IfChanged -Map $fileFiltering -Key 'respectGeminiIgnore' -Value $true -ChangeId 'context.fileFiltering.respectGeminiIgnore=true' -Changes $changes
Set-IfChanged -Map $fileFiltering -Key 'customIgnoreFilePaths' -Value @(Merge-Strings -Values @($targetIgnorePaths)) -ChangeId 'context.fileFiltering.customIgnoreFilePaths' -Changes $changes

$mcp = Ensure-Map -Map $target -Path @('mcp')
$mainMcpExcluded = @()
if ($main.ContainsKey('mcp') -and $main['mcp'].ContainsKey('excluded')) {
    $mainMcpExcluded = @(Get-StringArray -Value $main['mcp']['excluded'])
}
if ($mainMcpExcluded -contains 'github') {
    Set-IfChanged -Map $mcp -Key 'excluded' -Value @(Merge-Strings -Values @($mcp['excluded'], @('github'))) -ChangeId 'mcp.excluded=github' -Changes $changes
}

$plan = [ordered]@{
    status = if ($Apply) { 'pending_apply' } else { 'dry_run' }
    gemini_home = $GeminiHome
    main_settings_path = $mainPath
    antigravity_settings_path = $antigravityPath
    apply = [bool]$Apply
    changes = @($changes)
}

if (-not $Apply) {
    $plan.next = 'Re-run with -Apply to back up and write the Antigravity Gemini settings.'
    $plan | ConvertTo-Json -Depth 20
    exit 0
}

New-Item -ItemType Directory -Force -Path $antigravityDir | Out-Null
if (Test-Path -LiteralPath $antigravityPath -PathType Leaf) {
    $backupDir = Join-Path $GeminiHome 'settings-backups'
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $backupPath = Join-Path $backupDir ("antigravity-settings-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
    Copy-Item -LiteralPath $antigravityPath -Destination $backupPath -Force
    $plan.backup_path = $backupPath
}

$json = $target | ConvertTo-Json -Depth 50
Set-Content -LiteralPath $antigravityPath -Value $json -Encoding utf8
$plan.status = 'ok'
$plan.written = $true
$plan | ConvertTo-Json -Depth 20
