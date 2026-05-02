param(
  [ValidateSet("All", "Build", "Contract", "Dependency", "Doctor", "Docs", "Runtime", "RuntimeQuick", "Scripts")]
  [string]$Check = "All"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\Initialize-WindowsProcessEnvironment.ps1"
Initialize-WindowsProcessEnvironment

function Write-CheckOk {
  param([string]$Name)
  Write-Host "OK $Name"
}

function Resolve-PythonCommand {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
  }
  if (-not $python) {
    throw "Required command not found: python or python3"
  }

  return $python
}

function Invoke-SchemaJsonParse {
  Get-ChildItem schemas/jsonschema/*.json | Sort-Object Name | ForEach-Object {
    Get-Content -Raw $_.FullName | ConvertFrom-Json > $null
  }

  Write-CheckOk "schema-json-parse"
}

function Invoke-SchemaExampleValidation {
  $schemaMap = @{}
  Get-ChildItem schemas/jsonschema/*.json | ForEach-Object {
    $schemaMap[$_.BaseName -replace '\.schema$', ''] = $_.FullName
  }

  Get-ChildItem -Recurse -File schemas/examples -Filter *.json | Sort-Object FullName | ForEach-Object {
    $dir = Split-Path $_.DirectoryName -Leaf
    $schemaPath = $schemaMap[$dir]
    if (-not $schemaPath) {
      throw "No matching schema for example directory: $dir"
    }

    $ok = Test-Json -Json (Get-Content -Raw $_.FullName) -SchemaFile $schemaPath
    if (-not $ok) {
      throw "Example failed schema validation: $($_.FullName)"
    }
  }

  Write-CheckOk "schema-example-validation"
}

function Invoke-SchemaCatalogPairing {
  $catalog = Get-Content -Raw schemas/catalog/schema-catalog.yaml
  $paths = [regex]::Matches($catalog, '^\s+path:\s+(.+)$', 'Multiline') | ForEach-Object { $_.Groups[1].Value.Trim() }
  $specs = [regex]::Matches($catalog, '^\s+source_spec:\s+(.+)$', 'Multiline') | ForEach-Object { $_.Groups[1].Value.Trim() }

  foreach ($path in ($paths + $specs)) {
    if (-not (Test-Path $path)) {
      throw "Schema catalog references missing file: $path"
    }
  }

  $knownSchemas = $paths | ForEach-Object { Split-Path $_ -Leaf }
  $uncataloguedSchemas = Get-ChildItem schemas/jsonschema/*.json | Where-Object { $knownSchemas -notcontains $_.Name }
  if ($uncataloguedSchemas) {
    throw "Uncatalogued schema files: $($uncataloguedSchemas.Name -join ', ')"
  }

  $knownSpecs = $specs | ForEach-Object { Split-Path $_ -Leaf }
  $uncataloguedSpecs = Get-ChildItem docs/specs/*.md | Where-Object {
    $_.Name -ne 'README.md' -and $knownSpecs -notcontains $_.Name
  }
  if ($uncataloguedSpecs) {
    throw "Uncatalogued spec files: $($uncataloguedSpecs.Name -join ', ')"
  }

  Write-CheckOk "schema-catalog-pairing"
}

function Invoke-CorePrincipleChangeArtifactSchemaCheck {
  $checks = @(
    @{
      Name = "core-principle-change-proposal-artifacts"
      Directory = "docs/change-evidence/core-principle-change-proposals"
      Schema = "schemas/jsonschema/core-principle-change-proposal.schema.json"
    },
    @{
      Name = "core-principle-change-manifest-artifacts"
      Directory = "docs/change-evidence/core-principle-change-patches"
      Schema = "schemas/jsonschema/core-principle-change-manifest.schema.json"
    },
    @{
      Name = "core-principle-change-report-artifacts"
      Directory = "docs/change-evidence/core-principle-change-reports"
      Schema = "schemas/jsonschema/core-principle-change-report.schema.json"
    }
  )

  foreach ($check in $checks) {
    if (-not (Test-Path $check.Directory)) {
      continue
    }

    Get-ChildItem -Path $check.Directory -File -Filter *.json | Sort-Object FullName | ForEach-Object {
      $ok = Test-Json -Json (Get-Content -Raw $_.FullName) -SchemaFile $check.Schema
      if (-not $ok) {
        throw "Core principle change artifact failed schema validation: $($_.FullName)"
      }
    }

    Write-CheckOk $check.Name
  }
}

function Invoke-PowerShellParse {
  Get-ChildItem scripts -Recurse -File -Filter *.ps1 | Sort-Object FullName | ForEach-Object {
    $tokens = $null
    $errors = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$errors)
    if ($errors.Count -gt 0) {
      $errors | Format-List *
      throw "PowerShell parser errors found in $($_.FullName)"
    }
  }

  Write-CheckOk "powershell-parse"
}

function Invoke-IssueSeedingRenderCheck {
  $output = & pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll
  if ($LASTEXITCODE -ne 0) {
    throw "Issue seeding render check failed"
  }

  $summary = $output | ConvertFrom-Json
  if ($summary.rendered_tasks -lt 1 -or $summary.rendered_epics -lt 1 -or -not $summary.rendered_initiative) {
    throw "Issue seeding render check returned incomplete summary"
  }

  Write-CheckOk "issue-seeding-render"
}

function Invoke-ActiveMarkdownLinkCheck {
  $files = @()
  $git = Get-Command git -ErrorAction SilentlyContinue
  if ($git -and (Test-Path ".git")) {
    $markdownPaths = & $git.Source -c core.quotepath=false ls-files --cached --others --exclude-standard -- "*.md"
    if ($LASTEXITCODE -ne 0) {
      throw "git ls-files failed while collecting active markdown files"
    }

    $files = @(
      $markdownPaths |
        Where-Object { $_ } |
        ForEach-Object { Get-Item -LiteralPath (Join-Path (Get-Location) $_) } |
        Where-Object { $_.FullName -notmatch '[\\/]+docs[\\/]+change-evidence[\\/]' }
    )
  }
  else {
    $files = @(
      Get-ChildItem -Recurse -File -Filter *.md | Where-Object {
        $_.FullName -notmatch '[\\/]+docs[\\/]+change-evidence[\\/]' -and
        $_.FullName -notmatch '[\\/]+\.git[\\/]' -and
        $_.FullName -notmatch '[\\/]+\.worktrees[\\/]' -and
        $_.FullName -notmatch '[\\/]+\.runtime[\\/]'
      }
    )
  }

  $broken = [System.Collections.Generic.List[string]]::new()
  foreach ($file in $files) {
    $text = Get-Content -Raw $file.FullName
    $matches = [regex]::Matches($text, '\[[^\]]+\]\(([^)]+)\)')
    foreach ($match in $matches) {
      $target = $match.Groups[1].Value.Trim()
      if ($target -match '^(https?:|mailto:|#)') { continue }
      if ($target -match '^<.*>$') {
        $target = $target.Trim('<', '>')
      }

      $path = ($target -split '#')[0]
      if ([string]::IsNullOrWhiteSpace($path)) { continue }

      $resolved = Join-Path $file.DirectoryName $path
      if (-not (Test-Path $resolved)) {
        $broken.Add("$($file.FullName): $target")
      }
    }
  }

  if ($broken.Count -gt 0) {
    $broken | ForEach-Object { Write-Error $_ }
    throw "Broken active markdown links found"
  }

  Write-CheckOk "active-markdown-links"
}

function Invoke-BacklogYamlIdCheck {
  $idsBacklog = Select-String -Path docs/backlog/issue-ready-backlog.md -Pattern '^### (GAP-\d+) (.+)$' |
    ForEach-Object { $_.Matches[0].Groups[1].Value }
  $idsYaml = Select-String -Path docs/backlog/issue-seeds.yaml -Pattern '^\s+- id: (GAP-\d+)' |
    ForEach-Object { $_.Matches[0].Groups[1].Value }

  $missingInYaml = $idsBacklog | Where-Object { $idsYaml -notcontains $_ }
  $missingInBacklog = $idsYaml | Where-Object { $idsBacklog -notcontains $_ }

  if ($missingInYaml -or $missingInBacklog) {
    throw "Backlog/YAML ID drift found. Missing in YAML: $($missingInYaml -join ', '); missing in backlog: $($missingInBacklog -join ', ')"
  }

  Write-CheckOk "backlog-yaml-ids"
}

function Invoke-OldProjectNameScan {
  $oldSlug = @('governed', 'agent', 'platform') -join '-'
  $oldTitle = @('Governed', 'Agent', 'Platform') -join ' '
  $oldPlain = @('governed', 'agent', 'platform') -join ' '
  $pattern = "$([regex]::Escape($oldSlug))|$([regex]::Escape($oldTitle))|$([regex]::Escape($oldPlain))"

  $searchFiles = @(
    (Get-Item README.md),
    (Get-ChildItem docs, schemas, scripts -Recurse -File | Where-Object {
      $_.Extension -in @('.md', '.json', '.ps1') -and $_.FullName -notmatch '[\\/]+\.runtime[\\/]'
    })
  )

  $matches = Select-String -Path ($searchFiles | ForEach-Object { $_.FullName }) -Pattern $pattern
  $unexpected = $matches | Where-Object {
    $_.Path -notmatch '[\\/]+docs[\\/]+change-evidence[\\/]' -and
    $_.Path -notmatch '[\\/]+docs[\\/]+adrs[\\/]0004-' -and
    -not ($_.Path -match 'README\.md$' -and $_.Line -match 'Historical evidence may still mention')
  }

  if ($unexpected) {
    $unexpected | ForEach-Object { Write-Error "$($_.Path):$($_.LineNumber):$($_.Line)" }
    throw "Unexpected old project name references found"
  }

  Write-CheckOk "old-project-name-historical-only"
}

function Invoke-HostReplacementClaimBoundaryScan {
  $targetFiles = @(
    "README.md",
    "README.en.md",
    "README.zh-CN.md",
    "docs/quickstart/ai-coding-usage-guide.md",
    "docs/quickstart/ai-coding-usage-guide.zh-CN.md",
    "docs/product/codex-cli-app-integration-guide.md",
    "docs/product/codex-cli-app-integration-guide.zh-CN.md"
  ) | ForEach-Object { Join-Path (Get-Location) $_ } | Where-Object { Test-Path $_ }

  $riskPatterns = @(
    '(?i)\bfully\s+replaces?\b.*\bhost\b',
    '(?i)\breplaces?\b.*\bupstream\b.*\bcoding\b.*\bproducts?\b',
    '(?i)\bhost\s+replacement\s+shell\b',
    '完全替代.{0,20}宿主',
    '替代上游.{0,30}宿主'
  )

  $negationPatterns = @(
    '(?i)\b(not|does not|should not|is not|isn''t|not implemented|not yet|without)\b',
    '不应|不是|并非|未实现|尚未|还没有|不替代|不取代'
  )

  $violations = [System.Collections.Generic.List[string]]::new()
  foreach ($file in $targetFiles) {
    $lineNo = 0
    foreach ($line in (Get-Content $file)) {
      $lineNo += 1
      $hasRisk = $false
      foreach ($pattern in $riskPatterns) {
        if ($line -match $pattern) {
          $hasRisk = $true
          break
        }
      }

      if (-not $hasRisk) {
        continue
      }

      $hasNegation = $false
      foreach ($pattern in $negationPatterns) {
        if ($line -match $pattern) {
          $hasNegation = $true
          break
        }
      }

      if (-not $hasNegation) {
        $violations.Add(("{0}:{1}:{2}" -f $file, $lineNo, $line))
      }
    }
  }

  if ($violations.Count -gt 0) {
    $violations | ForEach-Object { Write-Error $_ }
    throw "Host-replacement over-claim lines found in operator-facing docs"
  }

  Write-CheckOk "host-replacement-claim-boundary"
}

function Invoke-GapEvidenceSloCheck {
  $backlogPath = Join-Path (Get-Location) "docs/backlog/issue-ready-backlog.md"
  $seedPath = Join-Path (Get-Location) "docs/backlog/issue-seeds.yaml"
  $evidenceRoot = Join-Path (Get-Location) "docs/change-evidence"
  if (-not (Test-Path $backlogPath)) {
    throw "Issue-ready backlog not found: $backlogPath"
  }
  if (-not (Test-Path $seedPath)) {
    throw "Issue seeds file not found: $seedPath"
  }
  if (-not (Test-Path $evidenceRoot)) {
    throw "Change evidence directory not found: $evidenceRoot"
  }

  $seedIds = @(
    Select-String -Path $seedPath -Pattern '^\s+- id: (GAP-\d+)' |
      ForEach-Object { $_.Matches[0].Groups[1].Value } |
      Where-Object { $_ -match '^GAP-0(6[9]|7\d)$' }
  )
  if ($seedIds.Count -lt 1) {
    throw "No post-closeout GAP ids found in issue seeds"
  }

  $targetGaps = New-Object System.Collections.Generic.HashSet[string]
  $inPostCloseout = $false
  foreach ($line in (Get-Content $backlogPath)) {
    if ($line -match '^## Post-Closeout Optimization Queue') {
      $inPostCloseout = $true
      continue
    }
    if ($inPostCloseout -and $line -match '^## ') {
      break
    }
    if ($inPostCloseout -and $line -match '^### (GAP-\d+) ') {
      $gapId = $Matches[1]
      if ($seedIds -contains $gapId) {
        [void]$targetGaps.Add($gapId)
      }
    }
  }
  if ($targetGaps.Count -lt 1) {
    throw "No post-closeout GAP sections found in backlog"
  }

  $completedGaps = New-Object System.Collections.Generic.HashSet[string]
  $currentGap = $null
  foreach ($line in (Get-Content $backlogPath)) {
    if ($line -match '^### (GAP-\d+) ') {
      $currentGap = $Matches[1]
      continue
    }
    if ($line -match '^### ') {
      $currentGap = $null
      continue
    }
    if ($null -ne $currentGap -and $line -match '^- Status:\s*(.+?)\s*$') {
      if ($Matches[1] -match '^complete\b') {
        [void]$completedGaps.Add($currentGap)
      }
    }
  }

  foreach ($gapId in @($targetGaps)) {
    if (-not $completedGaps.Contains($gapId)) {
      continue
    }

    $gapSlug = $gapId.ToLower()
    $matches = @(
      Get-ChildItem -Path $evidenceRoot -File | Where-Object {
      $_.Name.ToLower().Contains($gapSlug) -and $_.Name.ToLower().Contains("closeout")
      }
    )
    if (-not $matches -or $matches.Count -lt 1) {
      throw "Missing closeout evidence file for completed $gapId"
    }

    $content = Get-Content -Raw $matches[0].FullName
    foreach ($requiredHeader in @("## Verification", "## Rollback")) {
      if ($content -notmatch [regex]::Escape($requiredHeader)) {
        throw "$($matches[0].Name) missing required section: $requiredHeader"
      }
    }

    foreach ($requiredToken in @(
      "scripts/build-runtime.ps1",
      "verify-repo.ps1 -Check Runtime",
      "verify-repo.ps1 -Check Contract",
      "scripts/doctor-runtime.ps1"
    )) {
      if ($content -notmatch [regex]::Escape($requiredToken)) {
        throw "$($matches[0].Name) missing required verification token: $requiredToken"
      }
    }
  }

  Write-CheckOk "gap-evidence-slo"
}

function Invoke-PostCloseoutQueueSyncCheck {
  $seedPath = Join-Path (Get-Location) "docs/backlog/issue-seeds.yaml"
  if (-not (Test-Path $seedPath)) {
    throw "Issue seeds file not found: $seedPath"
  }

  $postCloseoutIds = @(
    Select-String -Path $seedPath -Pattern '^\s+- id: (GAP-\d+)' |
      ForEach-Object { $_.Matches[0].Groups[1].Value } |
      Where-Object { $_ -match '^GAP-0(6[9]|7\d)$' }
  )
  if ($postCloseoutIds.Count -lt 1) {
    throw "No post-closeout GAP ids found in issue seeds"
  }

  $sorted = @($postCloseoutIds | Sort-Object)
  $minGap = $sorted[0]
  $maxGap = $sorted[$sorted.Count - 1]

  $syncTargets = @(
    "docs/backlog/README.md",
    "docs/backlog/full-lifecycle-backlog-seeds.md",
    "docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md"
  ) | ForEach-Object { Join-Path (Get-Location) $_ }

  foreach ($target in $syncTargets) {
    if (-not (Test-Path $target)) {
      throw "Post-closeout sync target missing: $target"
    }
    $matches = @(
      Select-String -Path $target -Pattern ([regex]::Escape($minGap) + '.*' + [regex]::Escape($maxGap) + '.*complete') -CaseSensitive:$false
    )
    if ($matches.Count -lt 1) {
      throw "Post-closeout queue posture drift in $target; expected '$minGap through $maxGap' complete line"
    }
  }

  Write-CheckOk "post-closeout-queue-sync"
}

function Invoke-ClaimDriftSentinelCheck {
  $catalogPath = Join-Path (Get-Location) "docs/product/claim-catalog.json"
  if (-not (Test-Path $catalogPath)) {
    throw "Claim catalog not found: $catalogPath"
  }

  $catalog = Get-Content -Raw $catalogPath | ConvertFrom-Json
  if ($null -eq $catalog.claims -or @($catalog.claims).Count -lt 1) {
    throw "Claim catalog must contain at least one claim entry"
  }

  $maxEvidenceAgeDays = 30
  $now = Get-Date
  foreach ($claim in @($catalog.claims)) {
    foreach ($requiredField in @("claim_id", "claim_text", "proof_command", "evidence_link")) {
      if (-not $claim.PSObject.Properties.Name.Contains($requiredField)) {
        throw "Claim catalog entry missing required field: $requiredField"
      }
      $value = [string]$claim.$requiredField
      if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Claim catalog field '$requiredField' must be non-empty"
      }
    }

    $evidencePath = Join-Path (Get-Location) ([string]$claim.evidence_link)
    if (-not (Test-Path $evidencePath)) {
      throw "Claim $($claim.claim_id) references missing evidence file: $($claim.evidence_link)"
    }
    $evidenceName = [System.IO.Path]::GetFileName($evidencePath)
    $evidenceDate = $null
    if ($evidenceName -match '^(\d{8})-') {
      $rawDate = $Matches[1]
      $parsed = [datetime]::MinValue
      if ([datetime]::TryParseExact($rawDate, "yyyyMMdd", [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::AssumeLocal, [ref]$parsed)) {
        $evidenceDate = $parsed
      }
    }
    if ($null -eq $evidenceDate) {
      $evidenceDate = (Get-Item $evidencePath).LastWriteTime
    }
    if ($evidenceDate -lt $now.AddDays(-$maxEvidenceAgeDays)) {
      throw "Claim $($claim.claim_id) references stale evidence older than $maxEvidenceAgeDays days: $($claim.evidence_link)"
    }

    if (-not $claim.PSObject.Properties.Name.Contains("source_refs") -or $null -eq $claim.source_refs -or @($claim.source_refs).Count -lt 1) {
      throw "Claim $($claim.claim_id) must include source_refs"
    }

    foreach ($sourceRef in @($claim.source_refs)) {
      if (-not $sourceRef.PSObject.Properties.Name.Contains("path") -or -not $sourceRef.PSObject.Properties.Name.Contains("contains")) {
        throw "Claim $($claim.claim_id) source_ref must include path and contains"
      }

      $sourcePath = Join-Path (Get-Location) ([string]$sourceRef.path)
      if (-not (Test-Path $sourcePath)) {
        throw "Claim $($claim.claim_id) source file missing: $($sourceRef.path)"
      }

      $needle = [string]$sourceRef.contains
      if ([string]::IsNullOrWhiteSpace($needle)) {
        throw "Claim $($claim.claim_id) source_ref contains must be non-empty"
      }

      $sourceContent = Get-Content -Raw $sourcePath
      if ($sourceContent -notmatch [regex]::Escape($needle)) {
        throw "Claim $($claim.claim_id) drift detected: source text not found in $($sourceRef.path)"
      }
    }
  }

  Write-CheckOk "claim-drift-sentinel"
  Write-CheckOk "claim-evidence-freshness"
}

function Invoke-ClaimExceptionPathCheck {
  $exceptionsPath = Join-Path (Get-Location) "docs/product/claim-exceptions.json"
  if (-not (Test-Path $exceptionsPath)) {
    throw "Claim exceptions file not found: $exceptionsPath"
  }

  $data = Get-Content -Raw $exceptionsPath | ConvertFrom-Json
  if ($null -eq $data.exceptions) {
    throw "Claim exceptions file must define exceptions array"
  }
  if (-not ($data.exceptions -is [System.Array])) {
    throw "Claim exceptions 'exceptions' field must be an array"
  }

  $now = Get-Date
  foreach ($exception in @($data.exceptions)) {
    foreach ($requiredField in @("claim_id", "owner", "reason", "recovery_plan", "rollback_ref", "evidence_link", "expires_at", "status", "review_ref")) {
      if (-not $exception.PSObject.Properties.Name.Contains($requiredField)) {
        throw "Claim exception missing required field: $requiredField"
      }
      $value = [string]$exception.$requiredField
      if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Claim exception field '$requiredField' must be non-empty"
      }
    }

    $rollbackPath = Join-Path (Get-Location) ([string]$exception.rollback_ref)
    if (-not (Test-Path $rollbackPath)) {
      throw "Claim exception rollback_ref missing: $($exception.rollback_ref)"
    }
    $evidencePath = Join-Path (Get-Location) ([string]$exception.evidence_link)
    if (-not (Test-Path $evidencePath)) {
      throw "Claim exception evidence_link missing: $($exception.evidence_link)"
    }

    $status = ([string]$exception.status).ToLowerInvariant()
    if ($status -notin @("active", "resolved", "expired", "revoked")) {
      throw "Claim exception status must be one of active/resolved/expired/revoked"
    }

    $expiresAt = [datetime]::MinValue
    if (-not [datetime]::TryParse([string]$exception.expires_at, [ref]$expiresAt)) {
      throw "Claim exception expires_at is invalid: $($exception.expires_at)"
    }
    if ($status -eq "active" -and $expiresAt -lt $now) {
      throw "Claim exception is active but expired: $($exception.claim_id)"
    }
  }

  Write-CheckOk "claim-exception-paths"
}

function Invoke-CurrentSourceCompatibilityChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-current-source-compatibility.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Current source compatibility checks failed"
    }
    throw "Current source compatibility checks failed`n$detail"
  }

  Write-CheckOk "current-source-compatibility"
}

function Invoke-CorePrinciplesChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-core-principles.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      $detail = "verify-core-principles.py exited with code $LASTEXITCODE"
    }
    throw "Core principles checks failed`n$detail"
  }

  Write-CheckOk "core-principles"
}

function Invoke-CapabilityPortfolioChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-capability-portfolio.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Capability portfolio checks failed"
    }
    throw "Capability portfolio checks failed`n$detail"
  }

  Write-CheckOk "capability-portfolio"
}

function Invoke-LtpAutonomousPromotionChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/evaluate-ltp-promotion.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "LTP autonomous promotion checks failed"
    }
    throw "LTP autonomous promotion checks failed`n$detail"
  }

  Write-CheckOk "ltp-autonomous-promotion"
}

function Invoke-AutonomousNextWorkSelectionChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/select-next-work.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Autonomous next-work selection checks failed"
    }
    throw "Autonomous next-work selection checks failed`n$detail"
  }

  Write-CheckOk "autonomous-next-work-selection"
}

function Invoke-RuntimeEvolutionReviewChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/evaluate-runtime-evolution.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Runtime evolution review checks failed"
    }
    throw "Runtime evolution review checks failed`n$detail"
  }

  Write-CheckOk "runtime-evolution-review"
}

function Invoke-AiCodingExperienceReviewChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/extract-ai-coding-experience.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "AI coding experience review checks failed"
    }
    throw "AI coding experience review checks failed`n$detail"
  }

  Write-CheckOk "ai-coding-experience-review"
}

function Invoke-RuntimeEvolutionMaterializationChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/materialize-runtime-evolution.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Runtime evolution materialization checks failed"
    }
    throw "Runtime evolution materialization checks failed`n$detail"
  }

  Write-CheckOk "runtime-evolution-materialization"
}

function Invoke-CorePrincipleChangeMaterializationChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/materialize-core-principle-change.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Core principle change materialization checks failed"
    }
    throw "Core principle change materialization checks failed`n$detail"
  }

  Write-CheckOk "core-principle-change-materialization"
}

function Invoke-RuntimeEvolutionPrPreparationChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/prepare-runtime-evolution-pr.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    throw "Runtime evolution PR preparation checks failed`n$detail"
  }

  Write-CheckOk "runtime-evolution-pr-preparation"
}

function Invoke-RuntimeEvolutionRetirementChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/review-runtime-evolution-retirements.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    throw "Runtime evolution retirement checks failed`n$detail"
  }

  Write-CheckOk "runtime-evolution-retirement"
}

function Invoke-ContractChecks {
  Invoke-SchemaJsonParse
  Invoke-SchemaExampleValidation
  Invoke-SchemaCatalogPairing
  Invoke-ControlPackInheritanceChecks
  Invoke-ControlPackExecutionChecks
  Invoke-CorePrincipleChangeArtifactSchemaCheck
  Invoke-DependencyBaselineChecks
  Invoke-TransitionStackConvergenceChecks
  Invoke-TargetRepoRolloutContractChecks
  Invoke-TargetRepoGovernanceConsistencyChecks
  Invoke-TargetRepoReuseEffectFeedbackChecks
  Invoke-KnowledgeMemoryLifecycleChecks
  Invoke-PromotionLifecycleChecks
  Invoke-RepoMapContextArtifactChecks
  Invoke-PolicyToolCredentialAuditChecks
  Invoke-GovernanceHubCertificationChecks
  Invoke-TargetRepoPowerShellPolicyChecks
  Invoke-AgentRuleSyncChecks
  Invoke-PreChangeReviewChecks
  Invoke-FunctionalEffectivenessChecks
}

function Invoke-DependencyBaselineChecks {
  $python = Resolve-PythonCommand
  & $python.Source "scripts/verify-dependency-baseline.py"
  if ($LASTEXITCODE -ne 0) {
    throw "Dependency baseline checks failed"
  }

  Write-CheckOk "dependency-baseline"
}

function Invoke-TransitionStackConvergenceChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-transition-stack-convergence.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Transition stack convergence checks failed"
    }
    throw "Transition stack convergence checks failed`n$detail"
  }

  Write-CheckOk "transition-stack-convergence"
}

function Invoke-TargetRepoGovernanceConsistencyChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-target-repo-governance-consistency.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Target repo governance consistency checks failed"
    }
    throw "Target repo governance consistency checks failed`n$detail"
  }

  Write-CheckOk "target-repo-governance-consistency"
}

function Invoke-TargetRepoRolloutContractChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-target-repo-rollout-contract.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Target repo rollout contract checks failed"
    }
    throw "Target repo rollout contract checks failed`n$detail"
  }

  Write-CheckOk "target-repo-rollout-contract"
}

function Invoke-TargetRepoPowerShellPolicyChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-target-repo-powershell-policy.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Target repo PowerShell policy checks failed"
    }
    throw "Target repo PowerShell policy checks failed`n$detail"
  }

  Write-CheckOk "target-repo-powershell-policy"
}

function Invoke-TargetRepoReuseEffectFeedbackChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-target-repo-reuse-effect-report.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Target repo reuse effect feedback checks failed"
    }
    throw "Target repo reuse effect feedback checks failed`n$detail"
  }

  Write-CheckOk "target-repo-reuse-effect-feedback"
}

function Invoke-KnowledgeMemoryLifecycleChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-knowledge-memory-lifecycle.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Knowledge memory lifecycle checks failed"
    }
    throw "Knowledge memory lifecycle checks failed`n$detail"
  }

  Write-CheckOk "knowledge-memory-lifecycle"
}

function Invoke-PromotionLifecycleChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-promotion-lifecycle.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Promotion lifecycle checks failed"
    }
    throw "Promotion lifecycle checks failed`n$detail"
  }

  Write-CheckOk "promotion-lifecycle"
}

function Invoke-RepoMapContextArtifactChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-repo-map-context-artifact.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Repo-map context artifact checks failed"
    }
    throw "Repo-map context artifact checks failed`n$detail"
  }

  Write-CheckOk "repo-map-context-artifact"
}

function Invoke-PolicyToolCredentialAuditChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-policy-tool-credential-audit.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Policy tool credential audit checks failed"
    }
    throw "Policy tool credential audit checks failed`n$detail"
  }

  Write-CheckOk "policy-tool-credential-audit"
}

function Invoke-GovernanceHubCertificationChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-governance-hub-certification.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Governance hub certification checks failed"
    }
    throw "Governance hub certification checks failed`n$detail"
  }

  Write-CheckOk "governance-hub-certification"
}

function Invoke-ControlPackExecutionChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-control-pack-execution.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Control pack execution checks failed"
    }
    throw "Control pack execution checks failed`n$detail"
  }

  Write-CheckOk "control-pack-execution"
}

function Invoke-ControlPackInheritanceChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-control-pack-inheritance.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Control pack inheritance checks failed"
    }
    throw "Control pack inheritance checks failed`n$detail"
  }

  Write-CheckOk "control-pack-inheritance"
}

function Invoke-AgentRuleSyncChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/sync-agent-rules.py" --scope All --fail-on-change 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = ($output | Out-String).Trim()
    if (-not $detail) {
      throw "Agent rule sync checks failed"
    }
    throw "Agent rule sync checks failed`n$detail"
  }

  Write-CheckOk "agent-rule-sync"
}

function Invoke-PreChangeReviewChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-pre-change-review.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Pre-change review checks failed"
    }
    throw "Pre-change review checks failed`n$detail"
  }

  Write-CheckOk "pre-change-review"
}

function Invoke-FunctionalEffectivenessChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-functional-effectiveness.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Functional effectiveness evidence checks failed"
    }
    throw "Functional effectiveness evidence checks failed`n$detail"
  }

  Write-CheckOk "functional-effectiveness"
}

function Invoke-HostFeedbackSurfaceChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/host-feedback-summary.py" --assert-minimum 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Host feedback surface checks failed"
    }
    throw "Host feedback surface checks failed`n$detail"
  }

  Write-CheckOk "host-feedback-surface"
}

function Invoke-EvidenceRecoveryPostureChecks {
  $python = Resolve-PythonCommand
  $output = & $python.Source "scripts/verify-evidence-recovery-posture.py" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $detail = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($detail)) {
      throw "Evidence recovery posture checks failed"
    }
    throw "Evidence recovery posture checks failed`n$detail"
  }

  Write-CheckOk "evidence-recovery-posture"
}

function Invoke-BuildChecks {
  & pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
  if ($LASTEXITCODE -ne 0) {
    throw "Runtime build checks failed"
  }

  Write-CheckOk "runtime-build"
}

function Invoke-DocsChecks {
  Invoke-ActiveMarkdownLinkCheck
  Invoke-BacklogYamlIdCheck
  Invoke-OldProjectNameScan
  Invoke-HostReplacementClaimBoundaryScan
  Invoke-HostFeedbackSurfaceChecks
  Invoke-EvidenceRecoveryPostureChecks
  Invoke-CurrentSourceCompatibilityChecks
  Invoke-CorePrinciplesChecks
  Invoke-CapabilityPortfolioChecks
  Invoke-LtpAutonomousPromotionChecks
  Invoke-AutonomousNextWorkSelectionChecks
  Invoke-RuntimeEvolutionReviewChecks
  Invoke-AiCodingExperienceReviewChecks
  Invoke-RuntimeEvolutionMaterializationChecks
  Invoke-CorePrincipleChangeMaterializationChecks
  Invoke-RuntimeEvolutionPrPreparationChecks
  Invoke-RuntimeEvolutionRetirementChecks
  Invoke-GapEvidenceSloCheck
  Invoke-ClaimDriftSentinelCheck
  Invoke-ClaimExceptionPathCheck
  Invoke-PostCloseoutQueueSyncCheck
}

function Invoke-ScriptChecks {
  Invoke-PowerShellParse
  Invoke-IssueSeedingRenderCheck
}

function Invoke-RuntimeChecks {
  $python = Resolve-PythonCommand

  & $python.Source "scripts/run-runtime-tests.py" --suite "runtime=tests/runtime" --suite "service=tests/service"
  if ($LASTEXITCODE -ne 0) {
    throw "Runtime/service unit tests failed"
  }

  Write-CheckOk "runtime-unittest"
  Write-CheckOk "runtime-service-parity"

  $wrapperPath = "scripts/run-governed-task.py"
  $forbiddenTokens = @(
    "build_session_bridge_command(",
    "handle_session_bridge_command("
  )
  foreach ($token in $forbiddenTokens) {
    if (Select-String -Path $wrapperPath -SimpleMatch $token) {
      throw "Service wrapper drift detected in ${wrapperPath}: found forbidden token '$token'"
    }
  }

  Write-CheckOk "runtime-service-wrapper-drift-guard"
}

function Invoke-RuntimeQuickChecks {
  $python = Resolve-PythonCommand

  & $python.Source -m unittest `
    tests.runtime.test_governance_gate_runner `
    tests.runtime.test_target_repo_governance_consistency `
    tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_governance_baseline_only_bootstraps_blank_target `
    tests.runtime.test_target_repo_rollout_contract `
    tests.runtime.test_target_repo_speed_kpi
  if ($LASTEXITCODE -ne 0) {
    throw "Runtime quick slice failed"
  }

  Write-CheckOk "runtime-quick-slice"
}

function Invoke-DoctorChecks {
  & pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
  if ($LASTEXITCODE -ne 0) {
    throw "Runtime doctor checks failed"
  }

  Write-CheckOk "runtime-doctor"
}

switch ($Check) {
  "Build" { Invoke-BuildChecks }
  "Contract" { Invoke-ContractChecks }
  "Dependency" { Invoke-DependencyBaselineChecks }
  "Doctor" { Invoke-DoctorChecks }
  "Docs" { Invoke-DocsChecks }
  "Runtime" { Invoke-RuntimeChecks }
  "RuntimeQuick" { Invoke-RuntimeQuickChecks }
  "Scripts" { Invoke-ScriptChecks }
  "All" {
    Invoke-BuildChecks
    Invoke-RuntimeChecks
    Invoke-ContractChecks
    Invoke-DoctorChecks
    Invoke-DocsChecks
    Invoke-ScriptChecks
  }
}
