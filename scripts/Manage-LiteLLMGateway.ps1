param(
  [ValidateSet("Install", "RenderConfig", "Start", "Stop", "Status", "Smoke", "CockpitStatus", "PrepareCockpitUpstream", "WriteCodexProfile", "Rollback", "All")]
  [string]$Action = "Status",

  [string]$HostName = "127.0.0.1",
  [int]$Port = 4000,
  [int]$CockpitPort = 2876,
  [string]$ModelAlias = "cockpit-current",
  [string]$UpstreamModel = "gpt-5.5",
  # Backward-compatible no-op: the custom Cockpit local build allows free accounts by default.
  [switch]$AllowFreeAccount,
  [switch]$EnableVerboseLogs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$RuntimeRoot = Join-Path $RepoRoot ".runtime\litellm"
$VenvRoot = Join-Path $RuntimeRoot "venv"
$PythonExe = Join-Path $VenvRoot "Scripts\python.exe"
$LiteLlmExe = Join-Path $VenvRoot "Scripts\litellm.exe"
$ConfigPath = Join-Path $RuntimeRoot "config.yaml"
$SecretsPath = Join-Path $RuntimeRoot "secrets.env"
$RunnerPath = Join-Path $RuntimeRoot "run-litellm.ps1"
$PidPath = Join-Path $RuntimeRoot "litellm.pid"
$LogPath = Join-Path $RuntimeRoot "litellm.log"
$CockpitLocalAccessPath = Join-Path $HOME ".antigravity_cockpit\codex_local_access.json"
$CockpitAccountsPath = Join-Path $HOME ".antigravity_cockpit\codex_accounts.json"
$CockpitInstancesPath = Join-Path $HOME ".antigravity_cockpit\codex_instances.json"
$CodexConfigPath = Join-Path $HOME ".codex\config.toml"
$CodexAuthPath = Join-Path $HOME ".codex\auth.json"
$FirewallRuleName = "governed-cockpit-api-$CockpitPort-block-inbound"
$ManagedStart = "# BEGIN governed-litellm-gateway"
$ManagedEnd = "# END governed-litellm-gateway"

function Write-JsonLine {
  param([Parameter(Mandatory = $true)][hashtable]$Data)
  $Data | ConvertTo-Json -Depth 8 -Compress | Write-Host
}

function Ensure-RuntimeRoot {
  New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
}

function New-SecretValue {
  $bytes = New-Object byte[] 32
  [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
  return "sk-litellm-" + ([Convert]::ToBase64String($bytes).TrimEnd("=") -replace "[+/]", "")
}

function Read-EnvFile {
  $values = @{}
  if (-not (Test-Path -LiteralPath $SecretsPath)) {
    return $values
  }
  foreach ($line in Get-Content -LiteralPath $SecretsPath) {
    if ($line -match "^\s*#" -or [string]::IsNullOrWhiteSpace($line)) {
      continue
    }
    $idx = $line.IndexOf("=")
    if ($idx -lt 1) {
      continue
    }
    $name = $line.Substring(0, $idx).Trim()
    $value = $line.Substring($idx + 1).Trim()
    $values[$name] = $value
  }
  return $values
}

function Write-EnvFile {
  param([hashtable]$Values)
  Ensure-RuntimeRoot
  $lines = @(
    "# Local-only LiteLLM gateway secrets. Do not commit.",
    "LITELLM_MASTER_KEY=$($Values["LITELLM_MASTER_KEY"])",
    "LITELLM_COCKPIT_API_KEY=$($Values["LITELLM_COCKPIT_API_KEY"])"
  )
  Set-Content -LiteralPath $SecretsPath -Value $lines -Encoding utf8
}

function ConvertTo-YamlSingleQuoted {
  param([string]$Value)
  return "'" + ($Value -replace "'", "''") + "'"
}

function Get-CockpitLocalAccessState {
  if (-not (Test-Path -LiteralPath $CockpitLocalAccessPath)) {
    return [pscustomobject]@{
      present = $false
      enabled = $false
      port = $CockpitPort
      account_count = 0
      restrict_free_accounts = $false
      follow_current_account = $false
      has_api_key = $false
      api_key = ""
    }
  }
  $raw = Get-Content -LiteralPath $CockpitLocalAccessPath -Raw
  $json = $raw | ConvertFrom-Json
  $apiKey = [string]$json.apiKey
  return [pscustomobject]@{
    present = $true
    enabled = [bool]$json.enabled
    port = [int]$json.port
    account_count = @($json.accountIds).Count
    restrict_free_accounts = [bool]$json.restrictFreeAccounts
    follow_current_account = if ($json.PSObject.Properties.Name -contains "followCurrentAccount") { [bool]$json.followCurrentAccount } else { $false }
    has_api_key = -not [string]::IsNullOrWhiteSpace($apiKey)
    api_key = $apiKey
  }
}

function Get-CockpitCurrentAccountForUpstream {
  if (-not (Test-Path -LiteralPath $CockpitAccountsPath)) {
    return $null
  }
  $accountsJson = Get-Content -LiteralPath $CockpitAccountsPath -Raw | ConvertFrom-Json
  $accounts = @($accountsJson.accounts)
  $current = [string]$accountsJson.current_account_id
  if ([string]::IsNullOrWhiteSpace($current)) {
    return $null
  }
  $account = $accounts | Where-Object { [string]$_.id -eq $current } | Select-Object -First 1
  if (-not $account) {
    return $null
  }
  $isFree = ([string]$account.plan_type) -match "(?i)free"
  return [pscustomobject]@{
    id = [string]$account.id
    plan_type = [string]$account.plan_type
    is_free = $isFree
  }
}

function Get-CockpitFirewallState {
  $rules = @(Get-NetFirewallRule -DisplayName $FirewallRuleName -ErrorAction SilentlyContinue | Where-Object {
    $_.Enabled -eq "True" -and $_.Direction -eq "Inbound" -and $_.Action -eq "Block"
  })
  $matching = @()
  foreach ($rule in $rules) {
    $filters = @(Get-NetFirewallPortFilter -AssociatedNetFirewallRule $rule -ErrorAction SilentlyContinue | Where-Object {
      $_.Protocol -eq "TCP" -and ($_.LocalPort -eq "$CockpitPort" -or $_.LocalPort -eq "Any")
    })
    if ($filters.Count -gt 0) {
      $matching += $rule
    }
  }
  return [pscustomobject]@{
    rule_name = $FirewallRuleName
    block_present = ($matching.Count -gt 0)
    rule_count = $matching.Count
  }
}

function Get-WindowsFirewallDefaultInboundBlock {
  $output = (& netsh advfirewall show allprofiles firewallpolicy 2>$null) -join "`n"
  if ([string]::IsNullOrWhiteSpace($output)) {
    return $false
  }
  return ($output -match "Firewall Policy\s+BlockInbound,AllowOutbound")
}

function Get-CockpitNetworkConstraintState {
  $firewall = Get-CockpitFirewallState
  $profileDefaultBlock = Get-WindowsFirewallDefaultInboundBlock
  return [pscustomobject]@{
    rule_name = $firewall.rule_name
    block_present = $firewall.block_present
    rule_count = $firewall.rule_count
    profile_default_block = $profileDefaultBlock
    constrained = ($firewall.block_present -or $profileDefaultBlock)
  }
}

function Ensure-CockpitFirewall {
  $state = Get-CockpitNetworkConstraintState
  if ($state.constrained) {
    return $state
  }
  New-NetFirewallRule -DisplayName $FirewallRuleName -Direction Inbound -Action Block -Protocol TCP -LocalPort $CockpitPort -Profile Any | Out-Null
  return Get-CockpitNetworkConstraintState
}

function Ensure-Secrets {
  Ensure-RuntimeRoot
  $values = Read-EnvFile
  if (-not $values.ContainsKey("LITELLM_MASTER_KEY") -or [string]::IsNullOrWhiteSpace([string]$values["LITELLM_MASTER_KEY"])) {
    $values["LITELLM_MASTER_KEY"] = New-SecretValue
  }
  $cockpit = Get-CockpitLocalAccessState
  if ($cockpit.has_api_key) {
    $values["LITELLM_COCKPIT_API_KEY"] = $cockpit.api_key
    $values["LITELLM_MASTER_KEY"] = $cockpit.api_key
  }
  elseif (-not $values.ContainsKey("LITELLM_COCKPIT_API_KEY")) {
    $values["LITELLM_COCKPIT_API_KEY"] = ""
  }
  Write-EnvFile -Values $values
  [Environment]::SetEnvironmentVariable("LITELLM_MASTER_KEY", [string]$values["LITELLM_MASTER_KEY"], "User")
  $env:LITELLM_MASTER_KEY = [string]$values["LITELLM_MASTER_KEY"]
  return $values
}

function Invoke-Install {
  Ensure-RuntimeRoot
  if (-not (Test-Path -LiteralPath $PythonExe)) {
    & python -m venv $VenvRoot
  }
  & $PythonExe -m pip install --upgrade pip setuptools wheel
  & $PythonExe -m pip install "litellm[proxy]"
  $version = (& $LiteLlmExe --version 2>&1) -join "`n"
  Write-JsonLine @{ status = "ok"; action = "install"; litellm = $version.Trim(); runtime_root = $RuntimeRoot }
}

function Invoke-RenderConfig {
  $values = Ensure-Secrets
  $verboseValue = if ($EnableVerboseLogs) { "true" } else { "false" }
  $cockpitApiKey = ConvertTo-YamlSingleQuoted -Value ([string]$values["LITELLM_COCKPIT_API_KEY"])
  $masterKey = ConvertTo-YamlSingleQuoted -Value ([string]$values["LITELLM_MASTER_KEY"])
  $config = @"
model_list:
  - model_name: $ModelAlias
    litellm_params:
      model: openai/$UpstreamModel
      api_base: http://127.0.0.1:$CockpitPort/v1
      api_key: $cockpitApiKey
  - model_name: $UpstreamModel
    litellm_params:
      model: openai/$UpstreamModel
      api_base: http://127.0.0.1:$CockpitPort/v1
      api_key: $cockpitApiKey

general_settings:
  master_key: $masterKey

litellm_settings:
  drop_params: true
  set_verbose: $verboseValue
"@
  Set-Content -LiteralPath $ConfigPath -Value $config -Encoding utf8
  $runner = @"
Set-StrictMode -Version Latest
`$ErrorActionPreference = "Stop"
`$envFile = "$($SecretsPath -replace "\\", "\\")"
foreach (`$line in Get-Content -LiteralPath `$envFile) {
  if (`$line -match "^\s*#" -or [string]::IsNullOrWhiteSpace(`$line)) { continue }
  `$idx = `$line.IndexOf("=")
  if (`$idx -lt 1) { continue }
  `$name = `$line.Substring(0, `$idx).Trim()
  if (`$name -eq "LITELLM_MASTER_KEY") { continue }
  `$value = `$line.Substring(`$idx + 1).Trim()
  [Environment]::SetEnvironmentVariable(`$name, `$value, "Process")
}
[Environment]::SetEnvironmentVariable("LITELLM_MASTER_KEY", `$null, "Process")
& "$($LiteLlmExe -replace "\\", "\\")" --host $HostName --port $Port --config "$($ConfigPath -replace "\\", "\\")" --telemetry False *> "$($LogPath -replace "\\", "\\")"
"@
  Set-Content -LiteralPath $RunnerPath -Value $runner -Encoding utf8
  Write-JsonLine @{ status = "ok"; action = "render_config"; config = $ConfigPath; secrets = $SecretsPath; host = $HostName; port = $Port; upstream = "http://127.0.0.1:$CockpitPort/v1"; model_alias = $ModelAlias }
}

function Get-ChildProcessIds {
  param([int]$ParentProcessId)
  $children = @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$ParentProcessId" -ErrorAction SilentlyContinue)
  $ids = @()
  foreach ($child in $children) {
    $ids += [int]$child.ProcessId
    $ids += @(Get-ChildProcessIds -ParentProcessId ([int]$child.ProcessId))
  }
  return $ids
}

function Get-LiteLlmPortOwnerIds {
  $owners = @(Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object {
    $_.State -eq "Listen" -or $_.State -eq "Established"
  } | Select-Object -ExpandProperty OwningProcess -Unique)
  $owned = @()
  foreach ($owner in $owners) {
    $proc = Get-Process -Id ([int]$owner) -ErrorAction SilentlyContinue
    $cim = Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$owner)" -ErrorAction SilentlyContinue
    $cmd = if ($cim) { [string]$cim.CommandLine } else { "" }
    if ($proc -and (($proc.Path -and $proc.Path.StartsWith($RuntimeRoot, [System.StringComparison]::OrdinalIgnoreCase)) -or $cmd.Contains($RuntimeRoot))) {
      $owned += [int]$owner
    }
  }
  return $owned
}

function Get-ManagedProcess {
  if (-not (Test-Path -LiteralPath $PidPath)) {
    return $null
  }
  $pidText = (Get-Content -LiteralPath $PidPath -Raw).Trim()
  if (-not ($pidText -match "^\d+$")) {
    return $null
  }
  return Get-Process -Id ([int]$pidText) -ErrorAction SilentlyContinue
}

function Invoke-Start {
  if (-not (Test-Path -LiteralPath $LiteLlmExe)) {
    Invoke-Install
  }
  Invoke-RenderConfig
  $existing = Get-ManagedProcess
  if ($existing) {
    Write-JsonLine @{ status = "ok"; action = "start"; already_running = $true; pid = $existing.Id; port = $Port }
    return
  }
  $proc = Start-Process -FilePath "pwsh" -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $RunnerPath) -PassThru -WindowStyle Hidden -WorkingDirectory $RepoRoot
  Set-Content -LiteralPath $PidPath -Value ([string]$proc.Id) -Encoding ascii
  $deadline = (Get-Date).AddSeconds(45)
  do {
    Start-Sleep -Milliseconds 700
    $tcp = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" -or $_.State -eq "Established" }
    if ($tcp) {
      Write-JsonLine @{ status = "ok"; action = "start"; pid = $proc.Id; port = $Port; listener = "present" }
      return
    }
  } while ((Get-Date) -lt $deadline)
  Write-JsonLine @{ status = "fail"; action = "start"; pid = $proc.Id; port = $Port; log = $LogPath; reason = "listener_not_ready" }
  exit 2
}

function Invoke-Stop {
  $proc = Get-ManagedProcess
  $stopped = @()
  if (-not $proc) {
    foreach ($ownerId in Get-LiteLlmPortOwnerIds) {
      Stop-Process -Id $ownerId -Force
      $stopped += $ownerId
    }
    if (Test-Path -LiteralPath $PidPath) {
      [System.IO.File]::Delete($PidPath)
    }
    Write-JsonLine @{ status = "ok"; action = "stop"; already_stopped = ($stopped.Count -eq 0); stopped_pids = $stopped }
    return
  }
  $processIds = @([int]$proc.Id) + @(Get-ChildProcessIds -ParentProcessId ([int]$proc.Id)) + @(Get-LiteLlmPortOwnerIds)
  $processIds = @($processIds | Sort-Object -Unique)
  foreach ($processId in $processIds) {
    $target = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($target) {
      Stop-Process -Id $processId -Force
      $stopped += $processId
    }
  }
  if (Test-Path -LiteralPath $PidPath) {
    [System.IO.File]::Delete($PidPath)
  }
  Write-JsonLine @{ status = "ok"; action = "stop"; pid = $proc.Id; stopped_pids = $stopped }
}

function Invoke-Status {
  $proc = Get-ManagedProcess
  $tcp = @(Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object LocalAddress, LocalPort, State, OwningProcess)
  $cockpitTcp = @(Get-NetTCPConnection -LocalPort $CockpitPort -ErrorAction SilentlyContinue | Select-Object LocalAddress, LocalPort, State, OwningProcess)
  $cockpit = Get-CockpitLocalAccessState
  Write-JsonLine @{
    status = "ok"
    action = "status"
    litellm_installed = (Test-Path -LiteralPath $LiteLlmExe)
    litellm_running = ($null -ne $proc)
    litellm_pid = $(if ($proc) { $proc.Id } else { $null })
    litellm_listener_count = $tcp.Count
    cockpit_local_access_enabled = $cockpit.enabled
    cockpit_local_access_has_api_key = $cockpit.has_api_key
    cockpit_listener_count = $cockpitTcp.Count
    config = $ConfigPath
    log = $LogPath
  }
}

function Invoke-Smoke {
  $values = Ensure-Secrets
  $headers = @{ Authorization = "Bearer $($values["LITELLM_MASTER_KEY"])" }
  try {
    $models = Invoke-RestMethod -Method Get -Uri "http://$HostName`:$Port/v1/models" -Headers $headers -TimeoutSec 20
    $ids = @()
    if ($models.data) {
      $ids = @($models.data | ForEach-Object { [string]$_.id })
    }
    Write-JsonLine @{ status = "ok"; action = "smoke"; endpoint = "/v1/models"; model_ids = $ids; secret_redacted = $true }
  }
  catch {
    Write-JsonLine @{ status = "fail"; action = "smoke"; endpoint = "/v1/models"; reason = $_.Exception.Message; secret_redacted = $true }
    exit 2
  }
}

function Invoke-CockpitStatus {
  $state = Get-CockpitLocalAccessState
  $networkConstraint = Get-CockpitNetworkConstraintState
  $tcp = @(Get-NetTCPConnection -LocalPort $CockpitPort -ErrorAction SilentlyContinue | Select-Object LocalAddress, LocalPort, State, OwningProcess)
  $nonLoopback = @($tcp | Where-Object { $_.LocalAddress -notin @("127.0.0.1", "::1") })
  $safeListener = ($tcp.Count -gt 0 -and ($nonLoopback.Count -eq 0 -or $networkConstraint.constrained))
  Write-JsonLine @{
    status = "ok"
    action = "cockpit_status"
    enabled = $state.enabled
    port = $state.port
    account_count = $state.account_count
    restrict_free_accounts = $state.restrict_free_accounts
    follow_current_account = $state.follow_current_account
    has_api_key = $state.has_api_key
    listener_count = $tcp.Count
    listener_addresses = @($tcp | ForEach-Object { $_.LocalAddress } | Sort-Object -Unique)
    non_loopback_listener_count = $nonLoopback.Count
    firewall_block_present = $networkConstraint.block_present
    firewall_profile_default_block = $networkConstraint.profile_default_block
    firewall_rule_name = $networkConstraint.rule_name
    safe_for_upstream = ($state.enabled -and $state.has_api_key -and $state.account_count -gt 0 -and $safeListener)
    secret_redacted = $true
  }
}

function Backup-File {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$BackupRoot,
    [Parameter(Mandatory = $true)][string]$Suffix
  )
  New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $leaf = Split-Path -Leaf $Path
  $backupPath = Join-Path $BackupRoot "$leaf.$stamp.$Suffix.bak"
  Copy-Item -LiteralPath $Path -Destination $backupPath -Force
  return $backupPath
}

function Set-TomlTopLevelString {
  param(
    [Parameter(Mandatory = $true)][string]$Text,
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$Value
  )
  $replacement = "$Name = `"$Value`""
  $sectionMatch = [regex]::Match($Text, "(?m)^\s*\[")
  if ($sectionMatch.Success) {
    $head = $Text.Substring(0, $sectionMatch.Index)
    $tail = $Text.Substring($sectionMatch.Index)
  }
  else {
    $head = $Text
    $tail = ""
  }

  $pattern = "(?m)^\s*$([regex]::Escape($Name))\s*=.*$"
  if ([regex]::IsMatch($head, $pattern)) {
    $head = [regex]::Replace($head, $pattern, $replacement, 1)
  }
  else {
    $head = $head.TrimEnd() + "`r`n" + $replacement + "`r`n"
  }
  return ($head.TrimEnd() + "`r`n" + $tail.TrimStart())
}

function Ensure-CockpitLaunchBindingForGateway {
  if (-not (Test-Path -LiteralPath $CockpitInstancesPath)) {
    return @{ changed = $false; backup = $null; reason = "codex_instances_missing" }
  }

  $json = Get-Content -LiteralPath $CockpitInstancesPath -Raw | ConvertFrom-Json
  if (-not ($json.PSObject.Properties.Name -contains "defaultSettings") -or -not $json.defaultSettings) {
    $json | Add-Member -NotePropertyName "defaultSettings" -NotePropertyValue ([pscustomobject]@{})
  }
  $settings = $json.defaultSettings
  $changed = $false

  if (-not ($settings.PSObject.Properties.Name -contains "followLocalAccount")) {
    $settings | Add-Member -NotePropertyName "followLocalAccount" -NotePropertyValue $true
    $changed = $true
  }
  elseif ($settings.followLocalAccount -ne $true) {
    $settings.followLocalAccount = $true
    $changed = $true
  }

  if (-not ($settings.PSObject.Properties.Name -contains "bindAccountId")) {
    $settings | Add-Member -NotePropertyName "bindAccountId" -NotePropertyValue $null
    $changed = $true
  }
  elseif ($null -ne $settings.bindAccountId) {
    $settings.bindAccountId = $null
    $changed = $true
  }

  if (($settings.PSObject.Properties.Name -contains "lastPid") -and $null -ne $settings.lastPid) {
    $settings.lastPid = $null
    $changed = $true
  }

  if (-not $changed) {
    return @{ changed = $false; backup = $null; reason = "already_gateway_safe" }
  }

  $backupPath = Backup-File -Path $CockpitInstancesPath -BackupRoot (Join-Path $HOME ".antigravity_cockpit\backups") -Suffix "litellm-gateway-follow-current"
  $json | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $CockpitInstancesPath -Encoding utf8
  return @{ changed = $true; backup = $backupPath; reason = "cleared_fixed_codex_instance_binding" }
}

function Invoke-PrepareCockpitUpstream {
  $current = Get-CockpitCurrentAccountForUpstream
  if (-not $current) {
    Write-JsonLine @{ status = "fail"; action = "prepare_cockpit_upstream"; reason = "current_codex_account_not_found"; secret_redacted = $true }
    exit 2
  }
  $networkConstraint = Get-CockpitNetworkConstraintState
  if (-not (Test-Path -LiteralPath $CockpitLocalAccessPath)) {
    Write-JsonLine @{ status = "fail"; action = "prepare_cockpit_upstream"; reason = "cockpit_local_access_config_missing"; path = $CockpitLocalAccessPath; secret_redacted = $true }
    exit 2
  }
  $backupRoot = Join-Path $HOME ".antigravity_cockpit\backups"
  New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $backupPath = Join-Path $backupRoot "codex_local_access.json.$stamp.enable-litellm-upstream.bak"
  Copy-Item -LiteralPath $CockpitLocalAccessPath -Destination $backupPath -Force

  $json = Get-Content -LiteralPath $CockpitLocalAccessPath -Raw | ConvertFrom-Json
  $json.enabled = $true
  $json.port = $CockpitPort
  $json.restrictFreeAccounts = $false
  if ($json.PSObject.Properties.Name -contains "followCurrentAccount") {
    $json.followCurrentAccount = $true
  }
  else {
    $json | Add-Member -NotePropertyName "followCurrentAccount" -NotePropertyValue $true
  }
  $json.accountIds = @($current.id)
  $json.updatedAt = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
  $json | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $CockpitLocalAccessPath -Encoding utf8
  $launchBinding = Ensure-CockpitLaunchBindingForGateway
  $null = Ensure-Secrets
  Write-JsonLine @{
    status = "ok"
    action = "prepare_cockpit_upstream"
    enabled = $true
    port = $CockpitPort
    account_count = 1
    account_id = $current.id
    follow_current_account = $true
    restrict_free_accounts = $false
    firewall_block_present = $networkConstraint.block_present
    firewall_profile_default_block = $networkConstraint.profile_default_block
    firewall_rule_name = $networkConstraint.rule_name
    backup = $backupPath
    launch_binding_changed = $launchBinding.changed
    launch_binding_backup = $launchBinding.backup
    launch_binding_reason = $launchBinding.reason
    restart_required = $true
    secret_redacted = $true
  }
}

function Invoke-WriteCodexProfile {
  $values = Ensure-Secrets
  if (-not (Test-Path -LiteralPath $CodexConfigPath)) {
    throw "Codex config not found: $CodexConfigPath"
  }
  $backupPath = Backup-File -Path $CodexConfigPath -BackupRoot (Join-Path $HOME ".codex\config-backups") -Suffix "litellm-gateway"
  $authBackupPath = $null
  if (Test-Path -LiteralPath $CodexAuthPath) {
    $authBackupPath = Backup-File -Path $CodexAuthPath -BackupRoot (Join-Path $HOME ".codex\backups") -Suffix "litellm-gateway"
  }

  $text = Get-Content -LiteralPath $CodexConfigPath -Raw
  $pattern = "(?ms)^# BEGIN governed-litellm-gateway\r?\n.*?^# END governed[^\r\n]*\r?\n?"
  $text = [regex]::Replace($text, $pattern, "")
  $text = Set-TomlTopLevelString -Text $text -Name "model" -Value $ModelAlias
  $text = Set-TomlTopLevelString -Text $text -Name "forced_login_method" -Value "api"
  $text = Set-TomlTopLevelString -Text $text -Name "model_provider" -Value "litellm_gateway"
  $block = @"

$ManagedStart
[profiles.litellm-gateway]
forced_login_method = "api"
model_provider = "litellm_gateway"

[model_providers.litellm_gateway]
name = "LiteLLM Gateway (local)"
base_url = "http://127.0.0.1:$Port/v1"
wire_api = "responses"
env_key = "LITELLM_MASTER_KEY"
requires_openai_auth = false
supports_websockets = false
$ManagedEnd
"@
  Set-Content -LiteralPath $CodexConfigPath -Value ($text.TrimEnd() + $block) -Encoding utf8
  $auth = [ordered]@{
    OPENAI_API_KEY = [string]$values["LITELLM_MASTER_KEY"]
    auth_mode = "apikey"
    base_url = "http://127.0.0.1:$Port/v1"
    api_base_url = "http://127.0.0.1:$Port/v1"
    api_provider_id = "litellm_gateway"
    api_provider_name = "LiteLLM Gateway (local)"
    source = "governed-litellm-gateway"
    source_account_id = "litellm_gateway"
    email = "local-litellm-gateway"
  }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $CodexAuthPath) | Out-Null
  $auth | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $CodexAuthPath -Encoding utf8
  [Environment]::SetEnvironmentVariable("LITELLM_MASTER_KEY", [string]$values["LITELLM_MASTER_KEY"], "User")
  Write-JsonLine @{ status = "ok"; action = "write_codex_profile"; profile = "litellm-gateway"; config = $CodexConfigPath; auth = $CodexAuthPath; backup = $backupPath; auth_backup = $authBackupPath; default_provider_changed = $true; auth_written = $true; secret_redacted = $true }
}

function Invoke-Rollback {
  Invoke-Stop
  if (Test-Path -LiteralPath $CodexConfigPath) {
    $backupRoot = Join-Path $HOME ".codex\config-backups"
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    Copy-Item -LiteralPath $CodexConfigPath -Destination (Join-Path $backupRoot "config.toml.before-litellm-rollback-$stamp.bak") -Force
    $text = Get-Content -LiteralPath $CodexConfigPath -Raw
    $pattern = "(?ms)^# BEGIN governed-litellm-gateway\r?\n.*?^# END governed[^\r\n]*\r?\n?"
    $text = [regex]::Replace($text, $pattern, "")
    Set-Content -LiteralPath $CodexConfigPath -Value $text.TrimEnd() -Encoding utf8
  }
  Write-JsonLine @{ status = "ok"; action = "rollback"; codex_profile_removed = $true; runtime_root = $RuntimeRoot }
}

switch ($Action) {
  "Install" { Invoke-Install }
  "RenderConfig" { Invoke-RenderConfig }
  "Start" { Invoke-Start }
  "Stop" { Invoke-Stop }
  "Status" { Invoke-Status }
  "Smoke" { Invoke-Smoke }
  "CockpitStatus" { Invoke-CockpitStatus }
  "PrepareCockpitUpstream" { Invoke-PrepareCockpitUpstream }
  "WriteCodexProfile" { Invoke-WriteCodexProfile }
  "Rollback" { Invoke-Rollback }
  "All" {
    Invoke-Install
    Invoke-Start
    Invoke-Smoke
    Invoke-PrepareCockpitUpstream
    Invoke-CockpitStatus
    Invoke-WriteCodexProfile
  }
}
