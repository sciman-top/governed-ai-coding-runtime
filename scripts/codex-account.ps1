[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Position = 0)]
    [ValidateSet('list', 'status', 'switch', 'backup')]
    [string] $Action = 'list',

    [Parameter(Position = 1)]
    [string] $Name,

    [string] $CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),

    [switch] $NoLoginStatus
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-CodexHome {
    param([string] $Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        throw "Codex home does not exist: $Path"
    }
    return (Resolve-Path -LiteralPath $Path).Path
}

function Get-ShortHash {
    param([string] $Path)
    $hash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    return $hash.Substring(0, 12)
}

function Get-StringHash {
    param([AllowNull()][string] $Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ''
    }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
        $hashBytes = $sha.ComputeHash($bytes)
        return ([BitConverter]::ToString($hashBytes).Replace('-', '').ToLowerInvariant()).Substring(0, 12)
    }
    finally {
        $sha.Dispose()
    }
}

function Read-AuthJson {
    param([string] $Path)
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        throw "Invalid auth JSON: $Path"
    }
}

function Get-AuthMetadata {
    param([string] $Path, [string] $ActiveHash)
    $item = Get-Item -LiteralPath $Path
    $json = Read-AuthJson -Path $Path
    $hash = Get-ShortHash -Path $Path
    $accountId = ''
    if ($json.PSObject.Properties.Name -contains 'tokens' -and $json.tokens) {
        if ($json.tokens.PSObject.Properties.Name -contains 'account_id') {
            $accountId = [string] $json.tokens.account_id
        }
    }
    [pscustomobject]@{
        Name        = [System.IO.Path]::GetFileNameWithoutExtension($item.Name)
        File        = $item.Name
        Active      = ($hash -eq $ActiveHash)
        AuthMode    = if ($json.PSObject.Properties.Name -contains 'auth_mode') { [string] $json.auth_mode } else { '' }
        LastRefresh = if ($json.PSObject.Properties.Name -contains 'last_refresh') { [string] $json.last_refresh } else { '' }
        AccountHash = Get-StringHash -Value $accountId
        Sha256      = $hash
        FullName    = $item.FullName
    }
}

function Get-AuthCandidates {
    param([string] $HomePath, [string] $ActiveHash)
    $files = @()
    $files += Get-ChildItem -LiteralPath $HomePath -File -Filter 'auth*.json' -ErrorAction SilentlyContinue
    $profilesPath = Join-Path $HomePath 'auth-profiles'
    if (Test-Path -LiteralPath $profilesPath -PathType Container) {
        $files += Get-ChildItem -LiteralPath $profilesPath -File -Filter '*.json' -ErrorAction SilentlyContinue
    }
    $files | Sort-Object FullName -Unique | ForEach-Object { Get-AuthMetadata -Path $_.FullName -ActiveHash $ActiveHash }
}

function Backup-ActiveAuth {
    param([string] $AuthPath, [string] $HomePath)
    if (-not (Test-Path -LiteralPath $AuthPath -PathType Leaf)) {
        throw "Active auth file does not exist: $AuthPath"
    }
    $backupDir = Join-Path $HomePath 'auth-backups'
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $backupPath = Join-Path $backupDir ("auth-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
    Copy-Item -LiteralPath $AuthPath -Destination $backupPath -Force
    return $backupPath
}

function Resolve-AuthCandidate {
    param([object[]] $Candidates, [string] $Name)
    if ([string]::IsNullOrWhiteSpace($Name)) {
        throw 'Missing account name. Example: codex-account switch auth1'
    }
    $matches = $Candidates | Where-Object { $_.Name -eq $Name -or $_.File -eq $Name -or $_.FullName -eq $Name }
    if (-not $matches) {
        throw "No auth profile matched '$Name'. Run: codex-account list"
    }
    if (@($matches).Count -gt 1) {
        throw "Auth profile name '$Name' is ambiguous. Use the exact file name."
    }
    return $matches
}

$homePath = Resolve-CodexHome -Path $CodexHome
$authPath = Join-Path $homePath 'auth.json'
$activeHash = if (Test-Path -LiteralPath $authPath -PathType Leaf) { Get-ShortHash -Path $authPath } else { '' }
$candidates = @(Get-AuthCandidates -HomePath $homePath -ActiveHash $activeHash)

switch ($Action) {
    'list' {
        $candidates | Select-Object Name, Active, AuthMode, LastRefresh, AccountHash, Sha256, File | Format-Table -AutoSize
    }
    'status' {
        if (-not (Test-Path -LiteralPath $authPath -PathType Leaf)) {
            throw "Active auth file does not exist: $authPath"
        }
        Get-AuthMetadata -Path $authPath -ActiveHash $activeHash | Select-Object Name, Active, AuthMode, LastRefresh, AccountHash, Sha256, File | Format-List
        if (-not $NoLoginStatus) {
            codex login status
        }
    }
    'backup' {
        $backupPath = Backup-ActiveAuth -AuthPath $authPath -HomePath $homePath
        Write-Host "Backed up active auth to: $backupPath"
    }
    'switch' {
        $candidate = Resolve-AuthCandidate -Candidates $candidates -Name $Name
        Read-AuthJson -Path $candidate.FullName | Out-Null
        if ($candidate.Sha256 -eq $activeHash) {
            Write-Host "Active auth already matches '$($candidate.Name)' ($($candidate.Sha256))."
        }
        elseif ($PSCmdlet.ShouldProcess($authPath, "Switch active Codex auth to '$($candidate.Name)'")) {
            $backupPath = Backup-ActiveAuth -AuthPath $authPath -HomePath $homePath
            Copy-Item -LiteralPath $candidate.FullName -Destination $authPath -Force
            Write-Host "Switched active auth to '$($candidate.Name)' ($($candidate.Sha256))."
            Write-Host "Previous active auth backup: $backupPath"
        }
        if (-not $NoLoginStatus) {
            codex login status
        }
    }
}
