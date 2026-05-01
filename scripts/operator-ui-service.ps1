param(
  [ValidateSet("Start", "Stop", "Restart", "Status", "EnableAutoStart", "DisableAutoStart", "AutoStartStatus")]
  [string]$Action = "Start",

  [ValidateSet("zh-CN", "en")]
  [string]$UiLanguage = "zh-CN",

  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 8770,
  [switch]$OpenUi
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\Initialize-WindowsProcessEnvironment.ps1"
Initialize-WindowsProcessEnvironment

$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$RuntimeDir = Join-Path $RepoRoot ".runtime\operator-ui"
$PidPath = Join-Path $RuntimeDir "operator-ui.pid"
$LogPath = Join-Path $RuntimeDir "operator-ui.log"
$ErrorLogPath = Join-Path $RuntimeDir "operator-ui.err.log"
$Url = "http://$HostAddress`:$Port/?lang=$UiLanguage"
$AutoStartTaskName = "GovernedRuntimeOperatorUi-$Port"
$SourceFiles = @(
  (Join-Path $RepoRoot "scripts/serve-operator-ui.py"),
  (Join-Path $RepoRoot "scripts/operator-ui-service.ps1"),
  (Join-Path $RepoRoot "packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py"),
  (Join-Path $RepoRoot "packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py"),
  (Join-Path $RepoRoot "scripts/lib/codex_local.py"),
  (Join-Path $RepoRoot "scripts/lib/claude_local.py")
)

function Resolve-PythonCommand {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
  }
  if (-not $python) {
    throw "Required command not found: python or python3"
  }
  return $python.Source
}

function Get-RecordedProcess {
  if (-not (Test-Path -LiteralPath $PidPath)) {
    return $null
  }
  $raw = (Get-Content -LiteralPath $PidPath -Raw -ErrorAction SilentlyContinue).Trim()
  if ([string]::IsNullOrWhiteSpace($raw)) {
    return $null
  }
  $processId = 0
  if (-not [int]::TryParse($raw, [ref]$processId)) {
    return $null
  }
  return Get-Process -Id $processId -ErrorAction SilentlyContinue
}

function Get-PortOwner {
  $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.LocalAddress -in @($HostAddress, "0.0.0.0", "::") } |
    Select-Object -First 1
  if (-not $connection) {
    return $null
  }
  return Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
}

function Test-UiReady {
  try {
    $null = Invoke-RestMethod -Uri "http://$HostAddress`:$Port/api/status" -Method Get -TimeoutSec 2
    return $true
  }
  catch {
    return $false
  }
}

function Get-ServiceSourceLastWriteUtc {
  $latest = [datetime]::MinValue
  foreach ($sourceFile in $SourceFiles) {
    if (-not (Test-Path -LiteralPath $sourceFile)) {
      continue
    }
    $item = Get-Item -LiteralPath $sourceFile -ErrorAction SilentlyContinue
    if ($item -and $item.LastWriteTimeUtc -gt $latest) {
      $latest = $item.LastWriteTimeUtc
    }
  }
  return $latest
}

function Get-ProcessStartUtc {
  param([Parameter(Mandatory = $true)]$Process)

  try {
    return $Process.StartTime.ToUniversalTime()
  }
  catch {
    return $null
  }
}

function Test-ServiceProcessStale {
  param([Parameter(Mandatory = $true)]$Process)

  $processStartUtc = Get-ProcessStartUtc -Process $Process
  if ($null -eq $processStartUtc) {
    return $false
  }
  $sourceLastWriteUtc = Get-ServiceSourceLastWriteUtc
  if ($sourceLastWriteUtc -eq [datetime]::MinValue) {
    return $false
  }
  return $sourceLastWriteUtc -gt $processStartUtc
}

function Show-Status {
  $recorded = Get-RecordedProcess
  $owner = Get-PortOwner
  $ready = Test-UiReady
  $serviceProcess = if ($owner) { $owner } elseif ($recorded) { $recorded } else { $null }
  $sourceLastWriteUtc = Get-ServiceSourceLastWriteUtc
  $processStartUtc = if ($serviceProcess) { Get-ProcessStartUtc -Process $serviceProcess } else { $null }
  $stale = if ($serviceProcess) { Test-ServiceProcessStale -Process $serviceProcess } else { $false }
  [pscustomobject]@{
    status       = if ($ready) { "running" } else { "stopped" }
    url          = $Url
    pid          = if ($serviceProcess) { $serviceProcess.Id } else { $null }
    pid_path     = $PidPath
    log_path     = $LogPath
    error_log_path = $ErrorLogPath
    port         = $Port
    ready        = $ready
    stale        = $stale
    process_start_utc = if ($processStartUtc) { $processStartUtc.ToString("o") } else { $null }
    source_last_write_utc = if ($sourceLastWriteUtc -ne [datetime]::MinValue) { $sourceLastWriteUtc.ToString("o") } else { $null }
    autostart    = Get-AutoStartStatus
  } | ConvertTo-Json -Depth 3
}

function Get-AutoStartStatus {
  $task = Get-ScheduledTask -TaskName $AutoStartTaskName -ErrorAction SilentlyContinue
  if (-not $task) {
    return [pscustomobject]@{
      enabled = $false
      task_name = $AutoStartTaskName
      state = "missing"
    }
  }

  return [pscustomobject]@{
    enabled = [bool]$task.Settings.Enabled
    task_name = $AutoStartTaskName
    state = [string]$task.State
  }
}

function Enable-AutoStart {
  $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
  if (-not $pwsh) {
    throw "pwsh is not available; cannot enable autostart task."
  }

  $scriptPath = Join-Path $RepoRoot "scripts/operator-ui-service.ps1"
  $taskCommand = '"{0}" -NoProfile -ExecutionPolicy Bypass -File "{1}" -Action Start -UiLanguage {2} -HostAddress {3} -Port {4}' -f $pwsh.Source, $scriptPath, $UiLanguage, $HostAddress, $Port
  $taskAction = New-ScheduledTaskAction -Execute $pwsh.Source -Argument ("-NoProfile -ExecutionPolicy Bypass -File `"{0}`" -Action Start -UiLanguage {1} -HostAddress {2} -Port {3}" -f $scriptPath, $UiLanguage, $HostAddress, $Port)
  $logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
  $startupTrigger = New-ScheduledTaskTrigger -AtStartup
  $taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -StartWhenAvailable
  $registerMode = "logon_and_startup"
  try {
    $taskPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited
    $task = New-ScheduledTask -Action $taskAction -Trigger @($logonTrigger, $startupTrigger) -Principal $taskPrincipal -Settings $taskSettings
    Register-ScheduledTask -TaskName $AutoStartTaskName -InputObject $task -Force | Out-Null
  }
  catch {
    $registerMode = "logon_only_fallback"
    $taskPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
    $task = New-ScheduledTask -Action $taskAction -Trigger $logonTrigger -Principal $taskPrincipal -Settings $taskSettings
    Register-ScheduledTask -TaskName $AutoStartTaskName -InputObject $task -Force | Out-Null
  }

  [pscustomobject]@{
    action = "EnableAutoStart"
    task_name = $AutoStartTaskName
    register_mode = $registerMode
    command = $taskCommand
    autostart = Get-AutoStartStatus
  } | ConvertTo-Json -Depth 4
}

function Disable-AutoStart {
  Unregister-ScheduledTask -TaskName $AutoStartTaskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
  [pscustomobject]@{
    action = "DisableAutoStart"
    task_name = $AutoStartTaskName
    autostart = Get-AutoStartStatus
  } | ConvertTo-Json -Depth 4
}

function Show-AutoStartStatus {
  [pscustomobject]@{
    action = "AutoStartStatus"
    task_name = $AutoStartTaskName
    autostart = Get-AutoStartStatus
    url = $Url
  } | ConvertTo-Json -Depth 4
}

function Stop-ServiceProcess {
  $processes = @()
  $recorded = Get-RecordedProcess
  if ($recorded) {
    $processes += $recorded
  }
  $owner = Get-PortOwner
  if ($owner -and -not ($processes | Where-Object { $_.Id -eq $owner.Id })) {
    $processes += $owner
  }
  foreach ($process in $processes) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
  }
  Remove-Item -LiteralPath $PidPath -ErrorAction SilentlyContinue
}

function Start-ServiceProcess {
  New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null

  if (Test-UiReady) {
    $owner = Get-PortOwner
    if ($owner -and (Test-ServiceProcessStale -Process $owner)) {
      Stop-ServiceProcess
    }
    else {
      Show-Status
      if ($OpenUi) {
        Start-Process $Url | Out-Null
      }
      return
    }
  }

  if (Test-UiReady) {
    Show-Status
    if ($OpenUi) {
      Start-Process $Url | Out-Null
    }
    return
  }

  $owner = Get-PortOwner
  if ($owner) {
    throw "Port $Port is already owned by process $($owner.Id). Use -Action Stop or choose another -Port."
  }

  $python = Resolve-PythonCommand
  $arguments = @(
    "scripts/serve-operator-ui.py",
    "--serve",
    "--lang",
    $UiLanguage,
    "--host",
    $HostAddress,
    "--port",
    [string]$Port
  )
  $process = Start-Process `
    -FilePath $python `
    -ArgumentList $arguments `
    -WorkingDirectory $RepoRoot `
    -RedirectStandardOutput $LogPath `
    -RedirectStandardError $ErrorLogPath `
    -WindowStyle Hidden `
    -PassThru

  Set-Content -LiteralPath $PidPath -Value ([string]$process.Id) -Encoding UTF8

  $deadline = (Get-Date).AddSeconds(8)
  while ((Get-Date) -lt $deadline) {
    if (Test-UiReady) {
      if ($OpenUi) {
        Start-Process $Url | Out-Null
      }
      Show-Status
      return
    }
    Start-Sleep -Milliseconds 250
  }

  Show-Status
  throw "Operator UI service did not become ready within 8 seconds. See log: $LogPath"
}

Push-Location -LiteralPath $RepoRoot
try {
  switch ($Action) {
    "Start" { Start-ServiceProcess }
    "Stop" {
      Stop-ServiceProcess
      Show-Status
    }
    "Restart" {
      Stop-ServiceProcess
      Start-ServiceProcess
    }
    "Status" { Show-Status }
    "EnableAutoStart" { Enable-AutoStart }
    "DisableAutoStart" { Disable-AutoStart }
    "AutoStartStatus" { Show-AutoStartStatus }
  }
}
finally {
  Pop-Location
}
