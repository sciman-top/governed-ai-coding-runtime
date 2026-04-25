function Initialize-WindowsProcessEnvironment {
  function Set-DefaultProcessEnvironmentVariable {
    param(
      [string]$Name,
      [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Name) -or [string]::IsNullOrWhiteSpace($Value)) {
      return
    }
    if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($Name, "Process"))) {
      [Environment]::SetEnvironmentVariable($Name, $Value, "Process")
    }
  }

  function Read-CodexShellEnvironmentPolicySet {
    $codexHome = [Environment]::GetEnvironmentVariable("CODEX_HOME", "Process")
    if ([string]::IsNullOrWhiteSpace($codexHome)) {
      $userProfile = [Environment]::GetEnvironmentVariable("USERPROFILE", "Process")
      if ([string]::IsNullOrWhiteSpace($userProfile)) {
        $userProfile = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
      }
      if ([string]::IsNullOrWhiteSpace($userProfile)) {
        return @{}
      }
      $codexHome = Join-Path $userProfile ".codex"
    }

    $configPath = Join-Path $codexHome "config.toml"
    if (-not (Test-Path -LiteralPath $configPath)) {
      return @{}
    }

    $values = @{}
    $insidePolicySet = $false
    foreach ($rawLine in Get-Content -LiteralPath $configPath -ErrorAction SilentlyContinue) {
      $line = [string]$rawLine
      $trimmed = $line.Trim()
      if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed.StartsWith("#")) {
        continue
      }
      if ($trimmed -match '^\[(.+)\]$') {
        $insidePolicySet = ($matches[1] -eq "shell_environment_policy.set")
        continue
      }
      if (-not $insidePolicySet) {
        continue
      }
      if ($trimmed -match '^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"(.*)"\s*$') {
        $name = $matches[1]
        $value = $matches[2].Replace('\"', '"').Replace('\\', '\')
        if (-not [string]::IsNullOrWhiteSpace($value)) {
          $values[$name] = $value
        }
      }
    }
    return $values
  }

  function Import-SafeCodexShellEnvironmentPolicy {
    $safeNames = @(
      "COMSPEC", "ComSpec",
      "WINDIR", "windir",
      "SYSTEMROOT", "SystemRoot",
      "APPDATA",
      "LOCALAPPDATA",
      "PROGRAMDATA",
      "ProgramFiles",
      "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
      "http_proxy", "https_proxy", "all_proxy", "no_proxy"
    )

    $policySet = Read-CodexShellEnvironmentPolicySet
    foreach ($name in $safeNames) {
      if ($policySet.ContainsKey($name)) {
        Set-DefaultProcessEnvironmentVariable -Name $name -Value ([string]$policySet[$name])
        continue
      }

      $userValue = [Environment]::GetEnvironmentVariable($name, "User")
      if (-not [string]::IsNullOrWhiteSpace($userValue)) {
        Set-DefaultProcessEnvironmentVariable -Name $name -Value $userValue
        continue
      }

      $machineValue = [Environment]::GetEnvironmentVariable($name, "Machine")
      if (-not [string]::IsNullOrWhiteSpace($machineValue)) {
        Set-DefaultProcessEnvironmentVariable -Name $name -Value $machineValue
      }
    }
  }

  function Add-WindowsProcessPathEntry {
    param([string]$PathEntry)

    if ([string]::IsNullOrWhiteSpace($PathEntry)) {
      return
    }
    if (-not (Test-Path -LiteralPath $PathEntry)) {
      return
    }

    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Process")
    $parts = @($currentPath -split [IO.Path]::PathSeparator | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $alreadyPresent = @($parts | Where-Object { $_.TrimEnd("\") -ieq $PathEntry.TrimEnd("\") }).Count -gt 0
    if (-not $alreadyPresent) {
      [Environment]::SetEnvironmentVariable("PATH", ($PathEntry + [IO.Path]::PathSeparator + $currentPath), "Process")
    }
  }

  $isWindowsPlatform = $true
  if ($PSVersionTable.PSVersion.Major -ge 6) {
    $isWindowsPlatform = $IsWindows
  }
  if (-not $isWindowsPlatform) {
    return
  }

  Import-SafeCodexShellEnvironmentPolicy

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
  if ([string]::IsNullOrWhiteSpace($env:ProgramFiles) -and (Test-Path -LiteralPath "C:\Program Files")) {
    $env:ProgramFiles = "C:\Program Files"
  }

  Add-WindowsProcessPathEntry (Join-Path $windowsRoot "System32")
  Add-WindowsProcessPathEntry $windowsRoot
  if (-not [string]::IsNullOrWhiteSpace($env:ProgramFiles)) {
    Add-WindowsProcessPathEntry (Join-Path $env:ProgramFiles "PowerShell\7")
    Add-WindowsProcessPathEntry (Join-Path $env:ProgramFiles "Git\cmd")
    Add-WindowsProcessPathEntry (Join-Path $env:ProgramFiles "GitHub CLI")
  }
  Add-WindowsProcessPathEntry (Join-Path $windowsRoot "System32\WindowsPowerShell\v1.0")
}
