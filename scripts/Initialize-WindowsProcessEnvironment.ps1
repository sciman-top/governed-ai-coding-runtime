function Initialize-WindowsProcessEnvironment {
  $isWindowsPlatform = $true
  if ($PSVersionTable.PSVersion.Major -ge 6) {
    $isWindowsPlatform = $IsWindows
  }
  if (-not $isWindowsPlatform) {
    return
  }

  $windowsRoot = $env:SystemRoot
  if ([string]::IsNullOrWhiteSpace($windowsRoot)) {
    $windowsRoot = $env:WINDIR
  }
  if ([string]::IsNullOrWhiteSpace($windowsRoot)) {
    $windowsRoot = "C:\Windows"
  }

  if ([string]::IsNullOrWhiteSpace($env:SystemRoot)) {
    $env:SystemRoot = $windowsRoot
  }
  if ([string]::IsNullOrWhiteSpace($env:WINDIR)) {
    $env:WINDIR = $windowsRoot
  }
  if ([string]::IsNullOrWhiteSpace($env:ComSpec)) {
    $cmdPath = Join-Path $windowsRoot "System32\cmd.exe"
    if (Test-Path -LiteralPath $cmdPath) {
      $env:ComSpec = $cmdPath
    }
  }
  if ([string]::IsNullOrWhiteSpace($env:SystemDrive)) {
    $env:SystemDrive = ([System.IO.Path]::GetPathRoot($windowsRoot)).TrimEnd("\")
  }
  if (-not [string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
    $profileRoot = $env:USERPROFILE
    if ([string]::IsNullOrWhiteSpace($env:HOMEDRIVE)) {
      $env:HOMEDRIVE = ([System.IO.Path]::GetPathRoot($profileRoot)).TrimEnd("\")
    }
    if ([string]::IsNullOrWhiteSpace($env:HOMEPATH)) {
      $env:HOMEPATH = $profileRoot.Substring(([System.IO.Path]::GetPathRoot($profileRoot)).Length - 1)
    }
    if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
      $env:LOCALAPPDATA = Join-Path $profileRoot "AppData\Local"
    }
    if ([string]::IsNullOrWhiteSpace($env:APPDATA)) {
      $env:APPDATA = Join-Path $profileRoot "AppData\Roaming"
    }
  }
  if ([string]::IsNullOrWhiteSpace($env:PROGRAMDATA) -and (Test-Path -LiteralPath "C:\ProgramData")) {
    $env:PROGRAMDATA = "C:\ProgramData"
  }
}
