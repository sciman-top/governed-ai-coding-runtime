[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch] $Apply,
    [switch] $InstallAccountSwitcher = $true,
    [switch] $RepairThirdPartyInterop = $true,
    [bool] $MigrateProviderBucket = $false,
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
    model_provider = '"openai"'
    model_reasoning_effort = '"medium"'
    model_verbosity = '"medium"'
    model_context_window = '272000'
    model_auto_compact_token_limit = '220000'
    personality = '"pragmatic"'
    sandbox_mode = '"workspace-write"'
    web_search = '"cached"'
    check_for_update_on_startup = 'false'
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

function Set-TomlRawTable {
    param(
        [string[]] $Lines,
        [string] $Header,
        [string[]] $Body
    )

    $result = New-Object System.Collections.Generic.List[string]
    $result.AddRange([string[]](Remove-TomlTable -Lines $Lines -Header $Header))
    if ($result.Count -gt 0 -and $result[$result.Count - 1].Trim()) {
        $result.Add('')
    }
    $result.Add($Header)
    foreach ($line in $Body) {
        $result.Add($line)
    }
    return $result.ToArray()
}

function Set-PluginEnabled {
    param(
        [string[]] $Lines,
        [string] $PluginId,
        [bool] $Enabled
    )

    $value = if ($Enabled) { 'true' } else { 'false' }
    return Set-TomlTableValues -Lines $Lines -Header ('[plugins."{0}"]' -f $PluginId) -Values @{
        enabled = $value
    }
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

function Add-DuplicateSkillDisableOverrides {
    param(
        [string[]] $Lines,
        [string] $CanonicalSkillRoot = (Join-Path (Split-Path -Parent $PSScriptRoot) '..\skills-manager\agent'),
        [string] $DuplicateSkillRoot = (Join-Path $HOME '.agents\skills')
    )

    $canonicalRootResolved = $null
    if (Test-Path -LiteralPath $CanonicalSkillRoot -PathType Container) {
        $canonicalRootResolved = (Resolve-Path -LiteralPath $CanonicalSkillRoot).Path
    }
    elseif (Test-Path -LiteralPath 'D:\CODE\skills-manager\agent' -PathType Container) {
        $canonicalRootResolved = (Resolve-Path -LiteralPath 'D:\CODE\skills-manager\agent').Path
    }
    if (-not $canonicalRootResolved -or -not (Test-Path -LiteralPath $DuplicateSkillRoot -PathType Container)) {
        return $Lines
    }

    $canonicalNames = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($dir in Get-ChildItem -LiteralPath $canonicalRootResolved -Directory) {
        if (Test-Path -LiteralPath (Join-Path $dir.FullName 'SKILL.md') -PathType Leaf) {
            [void]$canonicalNames.Add($dir.Name)
        }
    }
    if ($canonicalNames.Count -eq 0) {
        return $Lines
    }

    $existingConfigText = [string]::Join("`n", $Lines)
    $result = New-Object System.Collections.Generic.List[string]
    $result.AddRange([string[]]$Lines)
    foreach ($dir in Get-ChildItem -LiteralPath $DuplicateSkillRoot -Directory | Sort-Object Name) {
        if (-not $canonicalNames.Contains($dir.Name)) {
            continue
        }
        if (-not (Test-Path -LiteralPath (Join-Path $dir.FullName 'SKILL.md') -PathType Leaf)) {
            continue
        }
        $skillPath = $dir.FullName
        $escapedPath = [regex]::Escape($skillPath)
        if ($existingConfigText -match $escapedPath) {
            continue
        }
        if ($result.Count -gt 0 -and $result[$result.Count - 1].Trim()) {
            $result.Add('')
        }
        $result.Add('[[skills.config]]')
        $result.Add(('path = {0}' -f (ConvertTo-TomlString $skillPath)))
        $result.Add('enabled = false')
        $existingConfigText += "`n$skillPath"
    }
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
    $lines = Remove-TomlTable -Lines $lines -Header '[model_providers.cockpit]'
    foreach ($entry in $Recommended.GetEnumerator()) {
        if ($entry.Key -eq 'model_provider' -and (Test-CustomModelProviderId -Value $activeModelProvider)) {
            $lines = Set-TopLevelTomlValue -Lines $lines -Key $entry.Key -Value (ConvertTo-TomlString $activeModelProvider)
            continue
        }
        $lines = Set-TopLevelTomlValue -Lines $lines -Key $entry.Key -Value $entry.Value
    }
    $lines = Set-TopLevelTomlValue -Lines $lines -Key 'sqlite_home' -Value (ConvertTo-TomlString $HomePath)
    $lines = Set-TopLevelTomlValue -Lines $lines -Key 'log_dir' -Value (ConvertTo-TomlString (Join-Path $HomePath 'log'))
    $lines = Set-HistorySection -Lines $lines
    $lines = Set-PluginEnabled -Lines $lines -PluginId 'chrome@openai-bundled' -Enabled:$false
    $postgresWrapperPath = Join-Path (Join-Path $HomePath 'scripts') 'mcp-postgres-env-wrapper.mjs'
    $lines = Set-TomlRawTable -Lines $lines -Header '[mcp_servers.postgres]' -Body @(
        'transport = "stdio"',
        'command = "node"',
        ('args = [{0}]' -f (ConvertTo-TomlString $postgresWrapperPath))
    )
    $lines = Set-TomlTableValues -Lines $lines -Header '[profiles.shared-chatgpt]' -Values @{
        forced_login_method = '"chatgpt"'
        model_provider = '"openai"'
    }
    $lines = Set-TomlTableValues -Lines $lines -Header '[profiles.shared-openai-api]' -Values @{
        forced_login_method = '"api"'
        model_provider = '"openai"'
    }
    if (Test-CustomModelProviderId -Value $activeModelProvider) {
        $lines = Set-TomlTableValues -Lines $lines -Header '[profiles.shared-cockpit-api]' -Values @{
            forced_login_method = '"api"'
            model_provider = (ConvertTo-TomlString $activeModelProvider)
        }
    }
    else {
        $lines = Set-TomlTableValues -Lines $lines -Header '[profiles.shared-cockpit-api]' -Values @{
            forced_login_method = '"api"'
            model_provider = '"openai"'
        }
    }
    $lines = Set-TomlTableValues -Lines $lines -Header '[profiles.shared-cockpit-auth]' -Values @{
        forced_login_method = '"chatgpt"'
        model_provider = '"openai"'
    }
    if (Test-CustomModelProviderId -Value $activeModelProvider) {
        $lines = Set-TomlTableValues -Lines $lines -Header '[profiles.shared-current-provider]' -Values @{
            forced_login_method = '"chatgpt"'
            model_provider = (ConvertTo-TomlString $activeModelProvider)
        }
    }
    else {
        $lines = Set-TomlTableValues -Lines $lines -Header '[profiles.shared-current-provider]' -Values @{
            forced_login_method = '"chatgpt"'
            model_provider = '"openai"'
        }
    }
    foreach ($repo in $TrustedRepoRoot) {
        $resolved = (Resolve-Path -LiteralPath $repo).Path
        $lines = Set-TrustedProject -Lines $lines -Path $resolved
    }
    $lines = Add-DuplicateSkillDisableOverrides -Lines $lines
    return $lines
}

function Install-PostgresMcpEnvWrapper {
    param([string] $HomePath)

    $scriptsDir = Join-Path $HomePath 'scripts'
    New-Item -ItemType Directory -Force -Path $scriptsDir | Out-Null
    $wrapperPath = Join-Path $scriptsDir 'mcp-postgres-env-wrapper.mjs'
    $content = @'
#!/usr/bin/env node
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const conn = process.env.POSTGRES_CONNECTION_STRING;
if (!conn || !conn.trim()) {
  console.error("POSTGRES_CONNECTION_STRING is required for postgres MCP.");
  process.exit(64);
}

const npmCache = process.env.npm_config_cache || join(process.env.LOCALAPPDATA || "", "npm-cache");
const npxRoot = join(npmCache, "_npx");
let entry = "";
if (existsSync(npxRoot)) {
  for (const item of readdirSync(npxRoot, { withFileTypes: true })) {
    if (!item.isDirectory()) continue;
    const candidate = join(
      npxRoot,
      item.name,
      "node_modules",
      "@modelcontextprotocol",
      "server-postgres",
      "dist",
      "index.js",
    );
    if (existsSync(candidate)) {
      entry = candidate;
      break;
    }
  }
}

if (!entry) {
  console.error("Cached @modelcontextprotocol/server-postgres package was not found. Run `npx -y @modelcontextprotocol/server-postgres --help` once to populate the npm cache.");
  process.exit(69);
}

process.argv = [process.argv[0], entry, conn];
await import(pathToFileURL(entry).href);
'@
    Set-Content -LiteralPath $wrapperPath -Value $content -Encoding utf8
    return $wrapperPath
}

function Invoke-CodexInteropCheck {
    param(
        [string] $HomePath,
        [string] $CcSwitchDb,
        [string] $CockpitStateHome,
        [switch] $ApplyRepair,
        [bool] $MigrateHistoryProviderBucket = $false
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
            reason = 'python command not found; cannot inspect Codex/Cockpit interop state.'
        }
    }

    $args = @(
        $checker,
        '--codex-home', $HomePath,
        '--cc-switch-db', $CcSwitchDb,
        '--cockpit-home', $CockpitStateHome
    )
    if ($ApplyRepair -or $MigrateHistoryProviderBucket) {
        return [ordered]@{
            status = 'blocked'
            reason = 'Codex/Cockpit write repair and provider bucket migration are deprecated. Cockpit Tools owns auth/API switching; project code may only run read-only interop diagnostics.'
        }
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
    migrate_provider_bucket = [bool]$MigrateProviderBucket
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
        shared_profiles = @('shared-chatgpt', 'shared-openai-api', 'shared-current-provider', 'shared-cockpit-api', 'shared-cockpit-auth')
        launchers = @('codex-shared', 'codex-shared-exec', 'codex-shared-resume', 'codex-shared-app', 'codex-cockpit', 'codex-cockpit-exec', 'codex-cockpit-resume', 'codex-cockpit-app', 'codex-cockpit-app-restart', 'codex-relay', 'codex-relay-exec', 'codex-relay-resume', 'codex-relay-app', 'codex-interop-check', 'codex-switch-record')
    }
    compatibility = [ordered]@{
        strategy = 'Use one shared CodexHome for local state, but keep API accounts on explicit custom model_provider buckets for connectivity; shared history is secondary for API relays.'
        cockpit_tools = 'Cockpit Tools owns Codex auth/API switching on this host; Codex launchers read the current Cockpit Codex account and project API providers as custom providers instead of normalizing them into openai.'
        cc_switch = 'CC Switch is treated as the Claude/third-party API switcher boundary and is not used as the Codex provider source.'
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
    $plan.next = 'Re-run with -Apply to write the current implementation. API provider connectivity is primary; history bucket migration is explicit only.'
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
$plan.postgres_mcp_env_wrapper = Install-PostgresMcpEnvWrapper -HomePath $CodexHome

if ($InstallAccountSwitcher) {
    $scriptsDir = Join-Path $CodexHome 'scripts'
    $binDir = Join-Path $HOME '.local\bin'
    New-Item -ItemType Directory -Force -Path $scriptsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $binDir | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'codex-account.ps1') -Destination (Join-Path $scriptsDir 'Switch-CodexAccount.ps1') -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Start-CodexShared.ps1') -Destination (Join-Path $scriptsDir 'Start-CodexShared.ps1') -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'codex-interop-check.py') -Destination (Join-Path $scriptsDir 'codex-interop-check.py') -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'codex-cockpit-switch-trace.py') -Destination (Join-Path $scriptsDir 'codex-cockpit-switch-trace.py') -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Save-CodexCockpitSwitchRecord.ps1') -Destination (Join-Path $scriptsDir 'Save-CodexCockpitSwitchRecord.ps1') -Force
    Set-Content -LiteralPath (Join-Path $binDir 'codex-account.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Switch-CodexAccount.ps1" %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-shared.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-shared-exec.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface exec %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-shared-resume.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface resume --all --include-non-interactive %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-shared-app.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface app %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-cockpit.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -UseCockpitCurrentAccount %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-cockpit-exec.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface exec -UseCockpitCurrentAccount %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-cockpit-resume.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface resume -UseCockpitCurrentAccount --all --include-non-interactive %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-cockpit-app.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface app -UseCockpitCurrentAccount %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-cockpit-app-restart.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface app -UseCockpitCurrentAccount -RestartExistingCodexApp %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-relay.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -UseCockpitCurrentAccount %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-relay-exec.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface exec -UseCockpitCurrentAccount %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-relay-resume.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface resume -UseCockpitCurrentAccount --all --include-non-interactive %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-relay-app.cmd') -Value '@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\scripts\Start-CodexShared.ps1" -Surface app -UseCockpitCurrentAccount %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $binDir 'codex-interop-check.cmd') -Value '@echo off
python "%USERPROFILE%\.codex\scripts\codex-interop-check.py" --codex-home "%USERPROFILE%\.codex" --cc-switch-db "%USERPROFILE%\.cc-switch\cc-switch.db" --cockpit-home "%USERPROFILE%\.antigravity_cockpit" %*' -Encoding ascii
    $saveRecordScriptForCmd = Join-Path $PSScriptRoot 'Save-CodexCockpitSwitchRecord.ps1'
    Set-Content -LiteralPath (Join-Path $binDir 'codex-switch-record.cmd') -Value ("@echo off`r`npwsh -NoProfile -ExecutionPolicy Bypass -File `"{0}`" %*" -f $saveRecordScriptForCmd) -Encoding ascii
    $plan.account_switcher_installed = $true
    $plan.shared_launcher_installed = $true
    $plan.interop_shortcuts_installed = 'read_only_check_only'
}

$plan.interop = Invoke-CodexInteropCheck `
    -HomePath $CodexHome `
    -CcSwitchDb $ccSwitchDbPath `
    -CockpitStateHome $cockpitHomePath `
    -ApplyRepair:$false `
    -MigrateHistoryProviderBucket:$false

if ($plan.interop.status -eq 'fail') {
    $plan.status = 'blocked'
    $plan.blocked_reason = 'Third-party Codex provider/auth interop still has blockers after apply.'
    $plan | ConvertTo-Json -Depth 8
    exit 2
}

$plan.status = 'ok'
$plan | ConvertTo-Json -Depth 8
