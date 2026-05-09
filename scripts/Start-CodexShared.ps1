[CmdletBinding(PositionalBinding = $false)]
param(
    [ValidateSet('cli', 'exec', 'app', 'resume')]
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

    [switch] $SkipCockpitApiValidation,

    [switch] $UseCcSwitchCurrentProvider,

    [string] $CcSwitchDbPath = (Join-Path $HOME '.cc-switch\cc-switch.db'),

    [switch] $RestartExistingCodexApp,

    [string] $Workdir,

    [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
    [string[]] $Prompt
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($Surface -eq 'app' -and [string]::IsNullOrWhiteSpace($Workdir) -and $Prompt -and $Prompt.Count -gt 0) {
    $Workdir = $Prompt[0]
    if ($Prompt.Count -gt 1) {
        $Prompt = @($Prompt[1..($Prompt.Count - 1)])
    }
    else {
        $Prompt = @()
    }
}

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

function Assert-CockpitApiAccountUsable {
    param(
        [string] $BaseUrl,
        [string] $ApiKey
    )
    if ([string]::IsNullOrWhiteSpace($BaseUrl) -or [string]::IsNullOrWhiteSpace($ApiKey)) {
        throw 'Cockpit Tools current Codex API account is missing base URL or API key.'
    }
    $modelsUrl = $BaseUrl.TrimEnd('/') + '/models'
    try {
        $response = Invoke-WebRequest `
            -Uri $modelsUrl `
            -Method Get `
            -Headers @{ Authorization = ('Bearer ' + $ApiKey) } `
            -TimeoutSec 10 `
            -ErrorAction Stop
        if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 300) {
            throw ("status {0}" -f $response.StatusCode)
        }
    }
    catch {
        $status = ''
        if ($_.Exception.PSObject.Properties.Name -contains 'Response' -and $null -ne $_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode
            if ($statusCode) {
                $status = " (status $([int]$statusCode))"
            }
        }
        throw "Cockpit Tools current Codex API account failed /models validation$status; refusing to launch Codex with a broken API account: $modelsUrl"
    }
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
        $accountBaseUrl = Get-JsonStringProperty -Object $Account -Name 'api_base_url'
        $providerId = Get-JsonStringProperty -Object $Account -Name 'api_provider_id'
        $providerName = Get-JsonStringProperty -Object $Account -Name 'api_provider_name'
        $payload = [ordered]@{
            OPENAI_API_KEY = $ApiKey
            auth_mode = 'apikey'
        }
        if (-not [string]::IsNullOrWhiteSpace($accountBaseUrl)) {
            $payload['base_url'] = $accountBaseUrl
            $payload['api_base_url'] = $accountBaseUrl
            $payload['api_provider_mode'] = 'custom'
            if (-not [string]::IsNullOrWhiteSpace($providerId)) {
                $payload['api_provider_id'] = $providerId
            }
            if (-not [string]::IsNullOrWhiteSpace($providerName)) {
                $payload['api_provider_name'] = $providerName
            }
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

function Stop-CodexAppProcesses {
    $processes = Get-Process -Name 'Codex', 'codex' -ErrorAction SilentlyContinue |
        Where-Object { $_.Id -ne $PID }
    if ($processes) {
        foreach ($process in $processes) {
            $liveProcess = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
            if ($liveProcess) {
                try {
                    Stop-Process -Id $liveProcess.Id -Force -ErrorAction SilentlyContinue
                }
                catch {
                }
            }
        }
        Start-Sleep -Seconds 1
    }
}

function Wait-CockpitCodexStateStable {
    param([string] $CockpitStateHome)

    $paths = @(
        (Join-Path $CockpitStateHome 'codex_accounts.json'),
        (Join-Path $CockpitStateHome 'codex_instances.json'),
        (Join-Path $CockpitStateHome 'config.json')
    )
    $previous = $null
    foreach ($attempt in 1..10) {
        $current = @($paths | ForEach-Object {
            if (Test-Path -LiteralPath $_ -PathType Leaf) {
                $item = Get-Item -LiteralPath $_
                '{0}|{1}|{2}' -f $_, $item.Length, $item.LastWriteTimeUtc.Ticks
            }
            else {
                '{0}|missing' -f $_
            }
        })
        if ($previous -and (($current -join "`n") -eq ($previous -join "`n"))) {
            return
        }
        $previous = $current
        Start-Sleep -Milliseconds 250
    }
}

function Invoke-CodexInteropRepair {
    param(
        [string] $HomePath,
        [string] $CockpitStateHome,
        [string] $CcSwitchDb
    )

    $checker = Join-Path $PSScriptRoot 'codex-interop-check.py'
    if (-not (Test-Path -LiteralPath $checker -PathType Leaf)) {
        Write-Warning "Codex interop checker not found; skipping pre-launch repair: $checker"
        return $false
    }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Warning 'python command not found; skipping Codex pre-launch interop repair.'
        return $false
    }
    $repairArgs = @(
        $checker,
        '--codex-home', $HomePath,
        '--cc-switch-db', $CcSwitchDb,
        '--cockpit-home', $CockpitStateHome,
        '--apply',
        '--migrate-provider-bucket'
    )
    $output = & $python.Source @repairArgs 2>&1
    $exitCode = $LASTEXITCODE
    $text = ($output | ForEach-Object { [string] $_ }) -join "`n"
    if ($exitCode -ne 0) {
        throw "Codex pre-launch interop repair failed with exit code ${exitCode}: $text"
    }
    try {
        $payload = $text | ConvertFrom-Json
        Write-Host ("interop_repair_status={0}" -f $payload.status)
        $changedActions = @($payload.actions | Where-Object { $_.status -eq 'changed' })
        if ($changedActions.Count -gt 0) {
            Write-Host ("interop_repair_actions={0}" -f (($changedActions | ForEach-Object { $_.id }) -join ','))
        }
    }
    catch {
        Write-Host 'interop_repair_status=unknown'
    }
    return $true
}

$resolvedHome = (Resolve-Path -LiteralPath $CodexHome).Path
$env:CODEX_HOME = $resolvedHome
$forcedLoginMethod = $null
$requiresOpenAiAuth = $true
$cockpitAccount = $null
$pendingCockpitAuthProjection = $null

if ($UseCockpitCurrentAccount -and $UseCcSwitchCurrentProvider) {
    throw 'UseCockpitCurrentAccount and UseCcSwitchCurrentProvider are mutually exclusive.'
}

if ($UseCockpitCurrentAccount) {
    Wait-CockpitCodexStateStable -CockpitStateHome $CockpitHome
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
        $ModelProvider = 'openai'
    }
    $accountBaseUrl = Get-JsonStringProperty -Object $cockpitAccount -Name 'api_base_url'
    if ([string]::IsNullOrWhiteSpace($accountBaseUrl) -and $authMode -eq 'apikey') {
        throw "Cockpit Tools current Codex API account has no api_base_url; refusing to fall back to OpenAI Official: $accountPath"
    }
    elseif ([string]::IsNullOrWhiteSpace($accountBaseUrl)) {
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
        if (-not $SkipCockpitApiValidation) {
            Assert-CockpitApiAccountUsable -BaseUrl $accountBaseUrl -ApiKey $apiKey
        }
        $env:OPENAI_API_KEY = $apiKey
        $forcedLoginMethod = 'api'
        $requiresOpenAiAuth = $false
        if (-not $PSBoundParameters.ContainsKey('Profile')) {
            $Profile = 'shared-cockpit-api'
        }
        $pendingCockpitAuthProjection = [ordered]@{ Mode = 'apikey'; ApiKey = $apiKey }
    }
    else {
        [Environment]::SetEnvironmentVariable('OPENAI_API_KEY', $null, 'Process')
        $forcedLoginMethod = 'chatgpt'
        $requiresOpenAiAuth = $true
        if (-not $PSBoundParameters.ContainsKey('Profile')) {
            $Profile = 'shared-cockpit-auth'
        }
        $pendingCockpitAuthProjection = [ordered]@{ Mode = 'chatgpt'; ApiKey = '' }
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

if ($Surface -eq 'app' -and $RestartExistingCodexApp -and -not $UseCockpitCurrentAccount) {
    Stop-CodexAppProcesses
}
if ($UseCockpitCurrentAccount) {
    $repairApplied = Invoke-CodexInteropRepair -HomePath $resolvedHome -CockpitStateHome $CockpitHome -CcSwitchDb $CcSwitchDbPath
    if (-not $repairApplied -and $pendingCockpitAuthProjection) {
        [void](Write-CodexAuthProjection `
            -HomePath $resolvedHome `
            -Account $cockpitAccount `
            -Mode ([string]$pendingCockpitAuthProjection.Mode) `
            -ApiKey ([string]$pendingCockpitAuthProjection.ApiKey))
    }
    if ($Surface -eq 'app' -and $RestartExistingCodexApp) {
        Stop-CodexAppProcesses
    }
}

$codexArgs = @()
if (-not [string]::IsNullOrWhiteSpace($Profile)) {
    $codexArgs += @('--profile', $Profile)
}
$shouldPassOpenAiBaseUrl = -not [string]::IsNullOrWhiteSpace($BaseUrl) -and (
    -not $UseCockpitCurrentAccount -or
    $forcedLoginMethod -eq 'api' -or
    $BaseUrl.TrimEnd('/') -ne 'https://api.openai.com/v1'
)
if ($shouldPassOpenAiBaseUrl) {
    $codexArgs += @('-c', ('openai_base_url={0}' -f (ConvertTo-TomlString $BaseUrl)))
}
if (-not [string]::IsNullOrWhiteSpace($ModelProvider)) {
    $codexArgs += @('-c', ('model_provider={0}' -f (ConvertTo-TomlString $ModelProvider)))
}
if (-not [string]::IsNullOrWhiteSpace($forcedLoginMethod)) {
    $codexArgs += @('-c', ('forced_login_method={0}' -f (ConvertTo-TomlString $forcedLoginMethod)))
}
if ($UseCockpitCurrentAccount -and -not [string]::IsNullOrWhiteSpace($ModelProvider) -and $ModelProvider -ne 'openai') {
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
elseif ($Surface -eq 'resume') {
    $codexArgs += 'resume'
}
elseif ($Surface -eq 'app') {
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
