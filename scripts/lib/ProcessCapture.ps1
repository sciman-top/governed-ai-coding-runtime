function ConvertTo-ProcessArgumentString {
  param([string[]]$ArgumentList)

  $quoted = @()
  foreach ($argument in $ArgumentList) {
    $text = [string]$argument
    if ($text -notmatch '[\s"]') {
      $quoted += $text
      continue
    }
    $quoted += ('"' + ($text -replace '\\(?=\\*")', '$0$0' -replace '"', '\"') + '"')
  }
  return ($quoted -join " ")
}

function Stop-ProcessTree {
  param(
    [Parameter(Mandatory = $true)]
    [int]$ProcessId
  )

  if ($ProcessId -le 0) {
    return
  }

  $children = @()
  try {
    $children = @(Get-CimInstance Win32_Process -Filter ("ParentProcessId={0}" -f $ProcessId) -ErrorAction Stop)
  }
  catch {
    $children = @()
  }

  foreach ($child in $children) {
    Stop-ProcessTree -ProcessId ([int]$child.ProcessId)
  }

  try {
    Stop-Process -Id $ProcessId -Force -ErrorAction Stop
  }
  catch {
  }
}

function Get-ProcessCaptureOutput {
  param(
    [Parameter(Mandatory = $true)]
    [string]$StdoutPath,
    [Parameter(Mandatory = $true)]
    [string]$StderrPath,
    [string]$TimeoutMessage = ""
  )

  $stdoutText = Get-Content -LiteralPath $StdoutPath -Raw -ErrorAction SilentlyContinue
  $stderrText = Get-Content -LiteralPath $StderrPath -Raw -ErrorAction SilentlyContinue
  $segments = @()
  if (-not [string]::IsNullOrWhiteSpace($stdoutText)) {
    $segments += $stdoutText.TrimEnd()
  }
  if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
    $segments += $stderrText.TrimEnd()
  }
  if (-not [string]::IsNullOrWhiteSpace($TimeoutMessage)) {
    $segments += $TimeoutMessage.Trim()
  }
  return ($segments -join [Environment]::NewLine).TrimEnd()
}

function Invoke-ProcessCapture {
  param(
    [Parameter(Mandatory = $true)]
    [string]$FilePath,
    [string[]]$ArgumentList = @(),
    [int]$TimeoutSeconds = 0,
    [string]$WorkingDirectory = "",
    [string]$TimeoutMessage = "",
    [switch]$StringifyArguments
  )

  if ($TimeoutSeconds -lt 0) {
    throw "TimeoutSeconds must be >= 0."
  }

  $timedOut = $false
  $exitCode = 0
  $outputText = ""
  $startedAt = Get-Date

  if ($TimeoutSeconds -gt 0) {
    $stdoutPath = [System.IO.Path]::GetTempFileName()
    $stderrPath = [System.IO.Path]::GetTempFileName()
    try {
      $startArgs = @{
        FilePath               = $FilePath
        NoNewWindow            = $true
        PassThru               = $true
        RedirectStandardOutput = $stdoutPath
        RedirectStandardError  = $stderrPath
      }
      if ($StringifyArguments.IsPresent) {
        $startArgs["ArgumentList"] = (ConvertTo-ProcessArgumentString -ArgumentList $ArgumentList)
      }
      else {
        $startArgs["ArgumentList"] = $ArgumentList
      }
      if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
        $startArgs["WorkingDirectory"] = $WorkingDirectory
      }

      $process = Start-Process @startArgs
      $completed = $process.WaitForExit($TimeoutSeconds * 1000)
      if (-not $completed) {
        $timedOut = $true
        Stop-ProcessTree -ProcessId ([int]$process.Id)
        try {
          $null = $process.WaitForExit(5000)
        }
        catch {
        }
        $exitCode = 124
      }
      else {
        $exitCode = [int]$process.ExitCode
      }

      $message = ""
      if ($timedOut -and -not [string]::IsNullOrWhiteSpace($TimeoutMessage)) {
        $message = $TimeoutMessage
      }
      $outputText = Get-ProcessCaptureOutput -StdoutPath $stdoutPath -StderrPath $stderrPath -TimeoutMessage $message
    }
    finally {
      Remove-Item -LiteralPath $stdoutPath -ErrorAction SilentlyContinue
      Remove-Item -LiteralPath $stderrPath -ErrorAction SilentlyContinue
    }
  }
  else {
    if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
      Push-Location -LiteralPath $WorkingDirectory
    }
    try {
      $output = & $FilePath @ArgumentList 2>&1
      $exitCode = $LASTEXITCODE
      if ($null -eq $exitCode) {
        $exitCode = 0
      }
      $outputText = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).TrimEnd()
    }
    finally {
      if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
        Pop-Location
      }
    }
  }

  return [pscustomobject]@{
    exit_code       = [int]$exitCode
    output          = $outputText
    timed_out       = [bool]$timedOut
    timeout_seconds = [int]$TimeoutSeconds
    duration_ms     = [int][Math]::Round(((Get-Date) - $startedAt).TotalMilliseconds)
  }
}
