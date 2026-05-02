function Get-OptionalStringProperty {
  param(
    [Parameter(Mandatory = $true)]
    [object]$Object,
    [Parameter(Mandatory = $true)]
    [string]$Name
  )

  if ($Object -and ($Object.PSObject.Properties.Name -contains $Name) -and $null -ne $Object.$Name) {
    return [string]$Object.$Name
  }
  return ""
}

function Get-OptionalIntProperty {
  param(
    [Parameter(Mandatory = $true)]
    [object]$Object,
    [Parameter(Mandatory = $true)]
    [string]$Name
  )

  if ($Object -and ($Object.PSObject.Properties.Name -contains $Name) -and $null -ne $Object.$Name) {
    return [int]$Object.$Name
  }
  return 0
}

function Load-TargetConfigMap {
  param(
    [Parameter(Mandatory = $true)]
    [string]$CatalogPath,
    [Parameter(Mandatory = $true)]
    [hashtable]$Variables
  )

  if (-not (Test-Path -LiteralPath $CatalogPath)) {
    throw "Target catalog not found: $CatalogPath"
  }

  $catalog = Get-Content -Raw -LiteralPath $CatalogPath | ConvertFrom-Json
  if (-not ($catalog -and $catalog.targets)) {
    throw "Target catalog is missing 'targets': $CatalogPath"
  }

  $map = @{}
  foreach ($entry in $catalog.targets.PSObject.Properties) {
    $name = [string]$entry.Name
    $rawConfig = $entry.Value
    $map[$name] = @{
      AttachmentRoot = Resolve-AbsolutePath -PathValue (Expand-TemplateString -Value ([string]$rawConfig.attachment_root) -Variables $Variables)
      AttachmentRuntimeStateRoot = Resolve-AbsolutePath -PathValue (Expand-TemplateString -Value ([string]$rawConfig.attachment_runtime_state_root) -Variables $Variables)
      RepoId = [string]$rawConfig.repo_id
      DisplayName = [string]$rawConfig.display_name
      PrimaryLanguage = [string]$rawConfig.primary_language
      BuildCommand = [string]$rawConfig.build_command
      TestCommand = [string]$rawConfig.test_command
      ContractCommand = Get-OptionalStringProperty -Object $rawConfig -Name "contract_command"
      ContractCommandsJson = $(if (($rawConfig.PSObject.Properties.Name -contains "contract_commands") -and $null -ne $rawConfig.contract_commands) { ConvertTo-Json -InputObject $rawConfig.contract_commands -Compress -Depth 20 } else { "" })
      QuickTestCommand = Get-OptionalStringProperty -Object $rawConfig -Name "quick_test_command"
      QuickTestReason = Get-OptionalStringProperty -Object $rawConfig -Name "quick_test_reason"
      QuickTestTimeoutSeconds = Get-OptionalIntProperty -Object $rawConfig -Name "quick_test_timeout_seconds"
      QuickTestSkipReason = Get-OptionalStringProperty -Object $rawConfig -Name "quick_test_skip_reason"
    }
  }

  return $map
}
