[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch] $Apply,
    [switch] $InstallAccountSwitcher = $true,
    [string] $CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),
    [string[]] $TrustedRepoRoot = @((Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path)
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Recommended = [ordered]@{
    approval_policy = '"never"'
    model = '"gpt-5.4"'
    model_reasoning_effort = '"medium"'
    model_verbosity = '"medium"'
    model_context_window = '128000'
    model_auto_compact_token_limit = '96000'
    personality = '"pragmatic"'
    sandbox_mode = '"workspace-write"'
    web_search = '"cached"'
}

function Set-TopLevelTomlValue {
    param(
        [string[]] $Lines,
        [string] $Key,
        [string] $Value
    )

    $result = New-Object System.Collections.Generic.List[string]
    $updated = $false
    $inserted = $false
    $inTopLevel = $true
    foreach ($line in $Lines) {
        if ($line -match '^\[') {
            if (-not $updated -and -not $inserted) {
                $result.Add("$Key = $Value")
                $inserted = $true
            }
            $inTopLevel = $false
        }
        if ($inTopLevel -and $line -match ("^\s*" + [regex]::Escape($Key) + "\s*=")) {
            $result.Add("$Key = $Value")
            $updated = $true
            continue
        }
        $result.Add($line)
    }
    if (-not $updated -and -not $inserted) {
        $result.Add("$Key = $Value")
    }
    return $result.ToArray()
}

function Set-HistorySection {
    param([string[]] $Lines)

    $result = New-Object System.Collections.Generic.List[string]
    $inHistory = $false
    $historySeen = $false
    $persistenceSeen = $false
    $maxBytesSeen = $false
    foreach ($line in $Lines) {
        if ($line -match '^\[history\]') {
            $historySeen = $true
            $inHistory = $true
            $result.Add($line)
            continue
        }
        if ($inHistory -and $line -match '^\[') {
            if (-not $persistenceSeen) { $result.Add('persistence = "save-all"') }
            if (-not $maxBytesSeen) { $result.Add('max_bytes = 104857600') }
            $inHistory = $false
        }
        if ($inHistory -and $line -match '^\s*persistence\s*=') {
            $result.Add('persistence = "save-all"')
            $persistenceSeen = $true
            continue
        }
        if ($inHistory -and $line -match '^\s*max_bytes\s*=') {
            $result.Add('max_bytes = 104857600')
            $maxBytesSeen = $true
            continue
        }
        $result.Add($line)
    }
    if ($inHistory) {
        if (-not $persistenceSeen) { $result.Add('persistence = "save-all"') }
        if (-not $maxBytesSeen) { $result.Add('max_bytes = 104857600') }
    }
    if (-not $historySeen) {
        $result.Add('')
        $result.Add('[history]')
        $result.Add('persistence = "save-all"')
        $result.Add('max_bytes = 104857600')
    }
    return $result.ToArray()
}

function Set-TrustedProject {
    param(
        [string[]] $Lines,
        [string] $Path
    )
    $header = "[projects.'$Path']"
    if ($Lines -contains $header) {
        return $Lines
    }
    $result = New-Object System.Collections.Generic.List[string]
    $result.AddRange([string[]]$Lines)
    $result.Add('')
    $result.Add($header)
    $result.Add('trust_level = "trusted"')
    return $result.ToArray()
}

function Update-ConfigToml {
    param([string] $Path)

    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        $lines = @(Get-Content -LiteralPath $Path)
    }
    else {
        $lines = @()
    }
    $lines = @($lines | Where-Object { $_ -notmatch '^ANTHROPIC_AUTH_TOKEN\s*=' })
    foreach ($entry in $Recommended.GetEnumerator()) {
        $lines = Set-TopLevelTomlValue -Lines $lines -Key $entry.Key -Value $entry.Value
    }
    $lines = Set-HistorySection -Lines $lines
    foreach ($repo in $TrustedRepoRoot) {
        $resolved = (Resolve-Path -LiteralPath $repo).Path
        $lines = Set-TrustedProject -Lines $lines -Path $resolved
    }
    return $lines
}

$resolvedHome = Resolve-Path -LiteralPath $CodexHome -ErrorAction SilentlyContinue
if ($resolvedHome) {
    $CodexHome = $resolvedHome.Path
}
else {
    $CodexHome = [System.IO.Path]::GetFullPath($CodexHome)
}
$configPath = Join-Path $CodexHome 'config.toml'
$plan = [ordered]@{
    codex_home = $CodexHome
    config_path = $configPath
    apply = [bool]$Apply
    install_account_switcher = [bool]$InstallAccountSwitcher
    trusted_repo_roots = $TrustedRepoRoot
}

if (-not $Apply) {
    $plan.status = 'dry_run'
    $plan.next = 'Re-run with -Apply to write config and install the account switcher.'
    $plan | ConvertTo-Json -Depth 5
    exit 0
}

New-Item -ItemType Directory -Force -Path $CodexHome | Out-Null
if (Test-Path -LiteralPath $configPath -PathType Leaf) {
    $backupDir = Join-Path $CodexHome 'config-backups'
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $backupPath = Join-Path $backupDir ("config-{0}.toml" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
    Copy-Item -LiteralPath $configPath -Destination $backupPath -Force
    $plan.config_backup = $backupPath
}

$updated = Update-ConfigToml -Path $configPath
Set-Content -LiteralPath $configPath -Value $updated -Encoding utf8
$plan.config_written = $true

if ($InstallAccountSwitcher) {
    $scriptsDir = Join-Path $CodexHome 'scripts'
    $binDir = Join-Path $HOME '.local\bin'
    New-Item -ItemType Directory -Force -Path $scriptsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $binDir | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'codex-account.ps1') -Destination (Join-Path $scriptsDir 'Switch-CodexAccount.ps1') -Force
    Set-Content -LiteralPath (Join-Path $binDir 'codex-account.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Switch-CodexAccount.ps1" %*' -Encoding ascii
    $plan.account_switcher_installed = $true
}

$plan.status = 'ok'
$plan | ConvertTo-Json -Depth 5
