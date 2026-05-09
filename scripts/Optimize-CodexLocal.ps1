[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch] $Apply,
    [switch] $InstallAccountSwitcher = $true,
    [switch] $RepairThirdPartyInterop = $true,
    [switch] $SkipInteropCheck,
    [string] $CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),
    [string[]] $TrustedRepoRoot = @((Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path),
    [string] $CcSwitchDbPath = $(Join-Path $HOME '.cc-switch\cc-switch.db'),
    [string] $CockpitHome = $(Join-Path $HOME '.antigravity_cockpit')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Recommended = [ordered]@{
    cli_auth_credentials_store = '"file"'
    approval_policy = '"never"'
    model = '"gpt-5.5"'
    model_reasoning_effort = '"medium"'
    model_verbosity = '"medium"'
    model_context_window = '272000'
    model_auto_compact_token_limit = '220000'
    personality = '"pragmatic"'
    sandbox_mode = '"workspace-write"'
    web_search = '"cached"'
}

function ConvertTo-TomlString {
    param([string] $Value)
    return '"' + ($Value -replace '\\', '\\' -replace '"', '\"') + '"'
}

function Get-TopLevelTomlStringValue {
    param(
        [string[]] $Lines,
        [string] $Key
    )

    foreach ($line in $Lines) {
        if ($line -match '^\[') {
            break
        }
        $pattern = '^\s*' + [regex]::Escape($Key) + '\s*=\s*"([^"]+)"'
        if ($line -match $pattern) {
            return $Matches[1]
        }
    }
    return $null
}

function Test-CustomModelProviderId {
    param([string] $Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $false
    }
    $reserved = @('amazon-bedrock', 'openai', 'ollama', 'lmstudio', 'oss', 'ollama-chat')
    return -not ($reserved -contains $Value.Trim().ToLowerInvariant())
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

function Set-TomlTableValues {
    param(
        [string[]] $Lines,
        [string] $Header,
        [hashtable] $Values
    )

    $result = New-Object System.Collections.Generic.List[string]
    $inTarget = $false
    $seenHeader = $false
    $seenKeys = New-Object 'System.Collections.Generic.HashSet[string]'

    foreach ($line in $Lines) {
        if ($line -eq $Header) {
            $seenHeader = $true
            $inTarget = $true
            $result.Add($line)
            continue
        }
        if ($inTarget -and $line -match '^\[') {
            foreach ($key in $Values.Keys) {
                if (-not $seenKeys.Contains($key)) {
                    $result.Add("$key = $($Values[$key])")
                }
            }
            $inTarget = $false
        }
        if ($inTarget) {
            $matched = $false
            foreach ($key in $Values.Keys) {
                if ($line -match ("^\s*" + [regex]::Escape($key) + "\s*=")) {
                    $result.Add("$key = $($Values[$key])")
                    [void]$seenKeys.Add($key)
                    $matched = $true
                    break
                }
            }
            if ($matched) {
                continue
            }
        }
        $result.Add($line)
    }
    if ($inTarget) {
        foreach ($key in $Values.Keys) {
            if (-not $seenKeys.Contains($key)) {
                $result.Add("$key = $($Values[$key])")
            }
        }
    }
    if (-not $seenHeader) {
        $result.Add('')
        $result.Add($Header)
        foreach ($key in $Values.Keys) {
            $result.Add("$key = $($Values[$key])")
        }
    }
    return $result.ToArray()
}

function Remove-TomlTable {
    param(
        [string[]] $Lines,
        [string] $Header
    )

    $result = New-Object System.Collections.Generic.List[string]
    $inTarget = $false
    foreach ($line in $Lines) {
        if ($line -eq $Header) {
            $inTarget = $true
            continue
        }
        if ($inTarget -and $line -match '^\[') {
            $inTarget = $false
        }
        if (-not $inTarget) {
            $result.Add($line)
        }
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
    param([string] $Path, [string] $HomePath)

    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        $lines = @(Get-Content -LiteralPath $Path)
    }
    else {
        $lines = @()
    }
    $activeModelProvider = Get-TopLevelTomlStringValue -Lines $lines -Key 'model_provider'
    $lines = @($lines | Where-Object {
        $_ -notmatch '^ANTHROPIC_AUTH_TOKEN\s*=' -and
        $_ -notmatch '^\s*disable_response_storage\s*='
    })
    foreach ($entry in $Recommended.GetEnumerator()) {
        $lines = Set-TopLevelTomlValue -Lines $lines -Key $entry.Key -Value $entry.Value
    }
    $lines = Set-TopLevelTomlValue -Lines $lines -Key 'sqlite_home' -Value (ConvertTo-TomlString $HomePath)
    $lines = Set-TopLevelTomlValue -Lines $lines -Key 'log_dir' -Value (ConvertTo-TomlString (Join-Path $HomePath 'log'))
    $lines = Set-HistorySection -Lines $lines
    $lines = Set-TomlTableValues -Lines $lines -Header '[profiles.shared-chatgpt]' -Values @{
        forced_login_method = '"chatgpt"'
    }
    $lines = Set-TomlTableValues -Lines $lines -Header '[profiles.shared-openai-api]' -Values @{
        forced_login_method = '"api"'
        model_provider = '"openai"'
    }
    if (Test-CustomModelProviderId -Value $activeModelProvider) {
        $lines = Set-TomlTableValues -Lines $lines -Header '[profiles.shared-current-provider]' -Values @{
            forced_login_method = '"chatgpt"'
            model_provider = (ConvertTo-TomlString $activeModelProvider)
        }
    }
    else {
        $lines = Remove-TomlTable -Lines $lines -Header '[profiles.shared-current-provider]'
    }
    foreach ($repo in $TrustedRepoRoot) {
        $resolved = (Resolve-Path -LiteralPath $repo).Path
        $lines = Set-TrustedProject -Lines $lines -Path $resolved
    }
    return $lines
}

function Invoke-CodexInteropCheck {
    param(
        [string] $HomePath,
        [string] $CcSwitchDb,
        [string] $CockpitStateHome,
        [switch] $ApplyRepair
    )

    if ($SkipInteropCheck) {
        return [ordered]@{
            status = 'skipped'
            reason = 'SkipInteropCheck was set.'
        }
    }

    $checker = Join-Path $PSScriptRoot 'codex-interop-check.py'
    if (-not (Test-Path -LiteralPath $checker -PathType Leaf)) {
        return [ordered]@{
            status = 'platform_na'
            reason = "Missing interop checker: $checker"
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        return [ordered]@{
            status = 'platform_na'
            reason = 'python command not found; cannot inspect CC Switch sqlite state.'
        }
    }

    $args = @(
        $checker,
        '--codex-home', $HomePath,
        '--cc-switch-db', $CcSwitchDb,
        '--cockpit-home', $CockpitStateHome
    )
    if ($ApplyRepair) {
        $args += '--apply'
    }

    $output = & $python.Source @args 2>&1
    $exitCode = $LASTEXITCODE
    $text = ($output | ForEach-Object { [string] $_ }) -join "`n"
    try {
        $payload = $text | ConvertFrom-Json
    }
    catch {
        return [ordered]@{
            status = 'fail'
            reason = 'Interop checker did not return valid JSON.'
            exit_code = $exitCode
            output = $text
        }
    }
    if ($exitCode -ne 0 -and $payload.status -ne 'fail') {
        $payload | Add-Member -NotePropertyName exit_code -NotePropertyValue $exitCode -Force
    }
    return $payload
}

$resolvedHome = Resolve-Path -LiteralPath $CodexHome -ErrorAction SilentlyContinue
if ($resolvedHome) {
    $CodexHome = $resolvedHome.Path
}
else {
    $CodexHome = [System.IO.Path]::GetFullPath($CodexHome)
}
$configPath = Join-Path $CodexHome 'config.toml'
$ccSwitchDbPath = [System.IO.Path]::GetFullPath($CcSwitchDbPath)
$cockpitHomePath = [System.IO.Path]::GetFullPath($CockpitHome)
$ccSwitchExePath = Join-Path $env:LOCALAPPDATA 'Programs\CC Switch\cc-switch.exe'
$cockpitToolsExePath = Join-Path $env:LOCALAPPDATA 'Cockpit Tools\cockpit-tools.exe'
$plan = [ordered]@{
    codex_home = $CodexHome
    config_path = $configPath
    apply = [bool]$Apply
    install_account_switcher = [bool]$InstallAccountSwitcher
    repair_third_party_interop = [bool]$RepairThirdPartyInterop
    skip_interop_check = [bool]$SkipInteropCheck
    trusted_repo_roots = $TrustedRepoRoot
    core_principle = '综合效率优先'
    principle_targets = @(
        '少打扰',
        '自动连续执行',
        '节省 token / 成本',
        '保留必要解释',
        '高效率'
    )
    current_implementation = [ordered]@{
        cli_auth_credentials_store = 'file'
        model = 'gpt-5.5'
        model_reasoning_effort = 'medium'
        approval_policy = 'never'
        model_context_window = 272000
        model_auto_compact_token_limit = 220000
        sqlite_home = $CodexHome
        history_persistence = 'save-all'
        shared_profiles = @('shared-chatgpt', 'shared-openai-api', 'shared-current-provider')
        launchers = @('codex-shared', 'codex-shared-exec', 'codex-shared-app', 'codex-interop-check', 'codex-interop-repair')
    }
    compatibility = [ordered]@{
        strategy = 'Use one shared CodexHome for coding history/state; switch auth/provider inside that home.'
        cockpit_tools = 'Compatible with default Cockpit Tools Codex home and Cockpit managed auth projection; Cockpit instances can still share state when their copied config keeps sqlite_home/log_dir pointing at this CodexHome.'
        cc_switch = 'Compatible with CC Switch default Codex config directory and stable model_provider behavior; provider switches should keep history/save-all plus sqlite_home/log_dir, and can use shared-current-provider for the currently active custom provider.'
        boundary = 'Use an isolated CODEX_HOME only for identities, relays, or privacy boundaries that must not share local coding sessions.'
    }
    local_tooling = [ordered]@{
        cc_switch = [ordered]@{
            installed = (Test-Path -LiteralPath $ccSwitchExePath -PathType Leaf)
            exe_path = $ccSwitchExePath
            db_present = (Test-Path -LiteralPath $ccSwitchDbPath -PathType Leaf)
            db_path = $ccSwitchDbPath
        }
        cockpit_tools = [ordered]@{
            installed = (Test-Path -LiteralPath $cockpitToolsExePath -PathType Leaf)
            exe_path = $cockpitToolsExePath
            state_home = $cockpitHomePath
            state_home_present = (Test-Path -LiteralPath $cockpitHomePath -PathType Container)
            managed_projection_present = (Test-Path -LiteralPath (Join-Path $CodexHome '.cockpit_codex_auth.json') -PathType Leaf)
        }
    }
}

if (-not $Apply) {
    $plan.interop = Invoke-CodexInteropCheck -HomePath $CodexHome -CcSwitchDb $ccSwitchDbPath -CockpitStateHome $cockpitHomePath
    $plan.status = 'dry_run'
    $plan.next = 'Re-run with -Apply to write the current implementation under the efficiency-first principle and install the account switcher.'
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

$updated = Update-ConfigToml -Path $configPath -HomePath $CodexHome
Set-Content -LiteralPath $configPath -Value $updated -Encoding utf8
$plan.config_written = $true

if ($InstallAccountSwitcher) {
    $scriptsDir = Join-Path $CodexHome 'scripts'
    $binDir = Join-Path $HOME '.local\bin'
    New-Item -ItemType Directory -Force -Path $scriptsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $binDir | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'codex-account.ps1') -Destination (Join-Path $scriptsDir 'Switch-CodexAccount.ps1') -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Start-CodexShared.ps1') -Destination (Join-Path $scriptsDir 'Start-CodexShared.ps1') -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'codex-interop-check.py') -Destination (Join-Path $scriptsDir 'codex-interop-check.py') -Force
    Set-Content -LiteralPath (Join-Path $binDir 'codex-account.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Switch-CodexAccount.ps1" %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-shared.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-shared-exec.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface exec %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-shared-app.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface app %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-interop-check.cmd') -Value '@echo off
python "%USERPROFILE%\.codex\scripts\codex-interop-check.py" --codex-home "%USERPROFILE%\.codex" --cc-switch-db "%USERPROFILE%\.cc-switch\cc-switch.db" --cockpit-home "%USERPROFILE%\.antigravity_cockpit" %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-interop-repair.cmd') -Value '@echo off
python "%USERPROFILE%\.codex\scripts\codex-interop-check.py" --codex-home "%USERPROFILE%\.codex" --cc-switch-db "%USERPROFILE%\.cc-switch\cc-switch.db" --cockpit-home "%USERPROFILE%\.antigravity_cockpit" --apply %*' -Encoding ascii
    $plan.account_switcher_installed = $true
    $plan.shared_launcher_installed = $true
    $plan.interop_shortcuts_installed = $true
}

$plan.interop = Invoke-CodexInteropCheck `
    -HomePath $CodexHome `
    -CcSwitchDb $ccSwitchDbPath `
    -CockpitStateHome $cockpitHomePath `
    -ApplyRepair:([bool]$RepairThirdPartyInterop)

if ($plan.interop.status -eq 'fail') {
    $plan.status = 'blocked'
    $plan.blocked_reason = 'Third-party Codex interop still has shared-history blockers after apply.'
    $plan | ConvertTo-Json -Depth 8
    exit 2
}

$plan.status = 'ok'
$plan | ConvertTo-Json -Depth 8
