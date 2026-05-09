[CmdletBinding()]
param(
    [ValidateSet('cli', 'exec', 'app')]
    [string] $Surface = 'cli',

    [string] $Profile = 'shared-chatgpt',

    [string] $AuthProfile,

    [string] $ApiKeyEnv,

    [string] $BaseUrl = $env:OPENAI_BASE_URL,

    [string] $ModelProvider,

    [string] $CodexHome = (Join-Path $HOME '.codex'),

    [switch] $UseCockpitCurrentAccount,

    [string] $CockpitHome = (Join-Path $HOME '.antigravity_cockpit'),

    [string] $CockpitAccountId,

    [switch] $UseCcSwitchCurrentProvider,

    [string] $CcSwitchDbPath = (Join-Path $HOME '.cc-switch\cc-switch.db'),

    [switch] $RestartExistingCodexApp,

    [string] $Workdir,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Prompt
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function ConvertTo-TomlString {
    param([string] $Value)
    return '"' + ($Value -replace '\\', '\\' -replace '"', '\"') + '"'
}

function Get-JsonStringProperty {
    param(
        [object] $Object,
        [string] $Name
    )
    if ($null -eq $Object) {
        return ''
    }
    if ($Object.PSObject.Properties.Name -contains $Name) {
        return [string]$Object.$Name
    }
    return ''
}

function Write-CodexAuthProjection {
    param(
        [string] $HomePath,
        [object] $Account,
        [string] $Mode,
        [string] $ApiKey
    )

    $authPath = Join-Path $HomePath 'auth.json'
    if ($Mode -eq 'apikey') {
        $payload = [ordered]@{
            OPENAI_API_KEY = $ApiKey
            auth_mode = 'apikey'
        }
    }
    else {
        $tokens = if ($Account.PSObject.Properties.Name -contains 'tokens') { $Account.tokens } else { $null }
        if ($null -ne $tokens -and -not ($tokens.PSObject.Properties.Name -contains 'account_id')) {
            $accountId = Get-JsonStringProperty -Object $Account -Name 'account_id'
            if (-not [string]::IsNullOrWhiteSpace($accountId)) {
                $tokens | Add-Member -NotePropertyName account_id -NotePropertyValue $accountId -Force
            }
        }
        $payload = [ordered]@{
            auth_mode = 'chatgpt'
            OPENAI_API_KEY = $null
            tokens = $tokens
        }
        $updatedAt = Get-JsonStringProperty -Object $Account -Name 'token_updated_at'
        $updatedAtNumber = 0L
        if ([Int64]::TryParse($updatedAt, [ref]$updatedAtNumber) -and $updatedAtNumber -gt 0) {
            $payload['last_refresh'] = [DateTimeOffset]::FromUnixTimeSeconds($updatedAtNumber).UtcDateTime.ToString('o')
        }
    }

    $nextJson = ($payload | ConvertTo-Json -Depth 20)
    $currentJson = if (Test-Path -LiteralPath $authPath -PathType Leaf) {
        Get-Content -LiteralPath $authPath -Raw
    }
    else {
        ''
    }
    if ($currentJson.Trim() -eq $nextJson.Trim()) {
        return $false
    }
    if (Test-Path -LiteralPath $authPath -PathType Leaf) {
        $backupDir = Join-Path $HomePath 'auth-backups'
        New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
        $backupPath = Join-Path $backupDir ("auth-{0}-cockpit-projection.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
        Copy-Item -LiteralPath $authPath -Destination $backupPath -Force
    }
    Set-Content -LiteralPath $authPath -Value $nextJson -Encoding utf8
    return $true
}

$resolvedHome = (Resolve-Path -LiteralPath $CodexHome).Path
$env:CODEX_HOME = $resolvedHome
$forcedLoginMethod = $null
$requiresOpenAiAuth = $true
$cockpitAccount = $null

if ($UseCockpitCurrentAccount -and $UseCcSwitchCurrentProvider) {
    throw 'UseCockpitCurrentAccount and UseCcSwitchCurrentProvider are mutually exclusive.'
}

if (-not [string]::IsNullOrWhiteSpace($AuthProfile)) {
    $switcher = Join-Path $resolvedHome 'scripts\Switch-CodexAccount.ps1'
    if (-not (Test-Path -LiteralPath $switcher -PathType Leaf)) {
        throw "Missing Codex account switcher: $switcher"
    }
    & $switcher switch $AuthProfile -CodexHome $resolvedHome -NoLoginStatus
}

if (-not [string]::IsNullOrWhiteSpace($ApiKeyEnv)) {
    $apiKey = [Environment]::GetEnvironmentVariable($ApiKeyEnv, 'Process')
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        $apiKey = [Environment]::GetEnvironmentVariable($ApiKeyEnv, 'User')
    }
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        $apiKey = [Environment]::GetEnvironmentVariable($ApiKeyEnv, 'Machine')
    }
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        throw "API key environment variable is not set: $ApiKeyEnv"
    }
    $env:OPENAI_API_KEY = $apiKey
}

if ($UseCockpitCurrentAccount) {
    $accountsIndexPath = Join-Path $CockpitHome 'codex_accounts.json'
    if (-not (Test-Path -LiteralPath $accountsIndexPath -PathType Leaf)) {
        throw "Cockpit Tools Codex account index not found: $accountsIndexPath"
    }
    $accountsIndex = Get-Content -LiteralPath $accountsIndexPath -Raw | ConvertFrom-Json
    $accountId = if ([string]::IsNullOrWhiteSpace($CockpitAccountId)) { Get-JsonStringProperty -Object $accountsIndex -Name 'current_account_id' } else { $CockpitAccountId }
    if ([string]::IsNullOrWhiteSpace($accountId)) {
        throw "Cockpit Tools has no current Codex account in: $accountsIndexPath"
    }
    $accountPath = Join-Path (Join-Path $CockpitHome 'codex_accounts') ($accountId + '.json')
    if (-not (Test-Path -LiteralPath $accountPath -PathType Leaf)) {
        throw "Cockpit Tools current Codex account file not found: $accountPath"
    }
    $cockpitAccount = Get-Content -LiteralPath $accountPath -Raw | ConvertFrom-Json
    $authMode = Get-JsonStringProperty -Object $cockpitAccount -Name 'auth_mode'
    if ([string]::IsNullOrWhiteSpace($authMode)) {
        throw "Cockpit Tools current Codex account has no auth_mode: $accountPath"
    }
    if (-not $PSBoundParameters.ContainsKey('ModelProvider') -or [string]::IsNullOrWhiteSpace($ModelProvider)) {
        $ModelProvider = 'cockpit'
    }
    $accountBaseUrl = Get-JsonStringProperty -Object $cockpitAccount -Name 'api_base_url'
    if ([string]::IsNullOrWhiteSpace($accountBaseUrl)) {
        $accountBaseUrl = 'https://api.openai.com/v1'
    }
    $accountBaseUrl = $accountBaseUrl.TrimEnd('/')
    if (-not $PSBoundParameters.ContainsKey('BaseUrl') -or [string]::IsNullOrWhiteSpace($BaseUrl)) {
        $BaseUrl = $accountBaseUrl
    }
    if ($authMode -eq 'apikey') {
        $apiKey = Get-JsonStringProperty -Object $cockpitAccount -Name 'openai_api_key'
        if ([string]::IsNullOrWhiteSpace($apiKey)) {
            throw "Cockpit Tools current Codex API account has no openai_api_key: $accountPath"
        }
        $env:OPENAI_API_KEY = $apiKey
        $forcedLoginMethod = 'api'
        $requiresOpenAiAuth = $false
        if (-not $PSBoundParameters.ContainsKey('Profile')) {
            $Profile = 'shared-cockpit-api'
        }
        [void](Write-CodexAuthProjection -HomePath $resolvedHome -Account $cockpitAccount -Mode 'apikey' -ApiKey $apiKey)
    }
    else {
        $forcedLoginMethod = 'chatgpt'
        $requiresOpenAiAuth = $true
        if (-not $PSBoundParameters.ContainsKey('Profile')) {
            $Profile = 'shared-cockpit-auth'
        }
        [void](Write-CodexAuthProjection -HomePath $resolvedHome -Account $cockpitAccount -Mode 'chatgpt' -ApiKey '')
    }
}

if ($UseCcSwitchCurrentProvider) {
    if (-not (Test-Path -LiteralPath $CcSwitchDbPath -PathType Leaf)) {
        throw "CC Switch database not found: $CcSwitchDbPath"
    }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw 'python command not found; cannot read CC Switch provider state.'
    }
    $providerJson = & $python.Source -c @'
import json, sqlite3, sys
db = sys.argv[1]
con = sqlite3.connect(db)
con.row_factory = sqlite3.Row
row = con.execute("select name, settings_config from providers where app_type='codex' and is_current=1 limit 1").fetchone()
con.close()
if not row:
    print("{}")
    raise SystemExit(0)
payload = json.loads(row["settings_config"] or "{}")
auth = payload.get("auth") if isinstance(payload, dict) else {}
print(json.dumps({"name": row["name"], "openai_api_key": auth.get("OPENAI_API_KEY") if isinstance(auth, dict) else None}))
'@ $CcSwitchDbPath
    $provider = $providerJson | ConvertFrom-Json
    if (-not [string]::IsNullOrWhiteSpace([string]$provider.openai_api_key)) {
        $env:OPENAI_API_KEY = [string]$provider.openai_api_key
    }
    if ([string]::IsNullOrWhiteSpace($Profile)) {
        $Profile = 'shared-current-provider'
    }
}

$codexArgs = @()
if (-not [string]::IsNullOrWhiteSpace($Profile)) {
    $codexArgs += @('--profile', $Profile)
}
if (-not $UseCockpitCurrentAccount -and -not [string]::IsNullOrWhiteSpace($BaseUrl)) {
    $codexArgs += @('-c', ('openai_base_url={0}' -f (ConvertTo-TomlString $BaseUrl)))
}
if (-not [string]::IsNullOrWhiteSpace($ModelProvider)) {
    $codexArgs += @('-c', ('model_provider={0}' -f (ConvertTo-TomlString $ModelProvider)))
}
if (-not [string]::IsNullOrWhiteSpace($forcedLoginMethod)) {
    $codexArgs += @('-c', ('forced_login_method={0}' -f (ConvertTo-TomlString $forcedLoginMethod)))
}
if ($UseCockpitCurrentAccount -and -not [string]::IsNullOrWhiteSpace($ModelProvider)) {
    $providerName = 'Cockpit Tools Current'
    $cockpitProviderName = Get-JsonStringProperty -Object $cockpitAccount -Name 'api_provider_name'
    $cockpitEmail = Get-JsonStringProperty -Object $cockpitAccount -Name 'email'
    if ($cockpitAccount -and -not [string]::IsNullOrWhiteSpace($cockpitProviderName)) {
        $providerName = $cockpitProviderName
    }
    elseif ($cockpitAccount -and -not [string]::IsNullOrWhiteSpace($cockpitEmail)) {
        $providerName = $cockpitEmail
    }
    $codexArgs += @('-c', ('model_providers.{0}.name={1}' -f $ModelProvider, (ConvertTo-TomlString $providerName)))
    $codexArgs += @('-c', ('model_providers.{0}.base_url={1}' -f $ModelProvider, (ConvertTo-TomlString $BaseUrl)))
    $codexArgs += @('-c', ('model_providers.{0}.wire_api="responses"' -f $ModelProvider))
    $codexArgs += @('-c', ('model_providers.{0}.requires_openai_auth={1}' -f $ModelProvider, ($requiresOpenAiAuth.ToString().ToLowerInvariant())))
}
if ($Surface -ne 'app' -and -not [string]::IsNullOrWhiteSpace($Workdir)) {
    $codexArgs += @('--cd', $Workdir)
}
if ($Surface -eq 'exec') {
    $codexArgs += 'exec'
}
elseif ($Surface -eq 'app') {
    if ($RestartExistingCodexApp) {
        Get-Process -Name 'Codex' -ErrorAction SilentlyContinue | Stop-Process -Force
        Start-Sleep -Seconds 1
    }
    $codexArgs += 'app'
    if (-not [string]::IsNullOrWhiteSpace($Workdir)) {
        $codexArgs += $Workdir
    }
}
if ($Surface -ne 'app' -and $Prompt) {
    $codexArgs += $Prompt
}

Write-Host ("CODEX_HOME={0}" -f $env:CODEX_HOME)
Write-Host ("profile={0}" -f $Profile)
if (-not [string]::IsNullOrWhiteSpace($ApiKeyEnv)) {
    Write-Host ("OPENAI_API_KEY sourced from {0}" -f $ApiKeyEnv)
}
if ($UseCcSwitchCurrentProvider) {
    Write-Host ("OPENAI_API_KEY sourced from current CC Switch provider")
}
if ($UseCockpitCurrentAccount) {
    $accountLabel = if ($cockpitAccount) { Get-JsonStringProperty -Object $cockpitAccount -Name 'email' } else { '' }
    Write-Host ("Cockpit Tools Codex account={0}" -f $accountLabel)
    Write-Host ("forced_login_method={0}" -f $forcedLoginMethod)
    if ($forcedLoginMethod -eq 'api') {
        Write-Host ("OPENAI_API_KEY sourced from current Cockpit Tools account")
    }
}
if (-not [string]::IsNullOrWhiteSpace($BaseUrl)) {
    if ($UseCockpitCurrentAccount) {
        Write-Host ("provider_base_url={0}" -f $BaseUrl)
    }
    else {
        Write-Host ("openai_base_url={0}" -f $BaseUrl)
    }
}
if (-not [string]::IsNullOrWhiteSpace($ModelProvider)) {
    Write-Host ("model_provider={0}" -f $ModelProvider)
}
if ($Surface -eq 'app' -and $Prompt) {
    Write-Warning 'Codex app accepts a workspace path, not an initial prompt; trailing prompt arguments were ignored.'
}

& codex @codexArgs
