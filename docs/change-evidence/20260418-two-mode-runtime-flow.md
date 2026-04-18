# 20260418 Two-Mode Runtime Flow

## Purpose
Further reduce operator friction by adding a two-mode one-command flow that covers both first-time onboarding and daily checks.

## Basis
- `scripts/runtime-flow.ps1`
- `scripts/runtime-check.ps1`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `README.md`
- `README.en.md`
- `README.zh-CN.md`

## Change
- Added `scripts/runtime-flow.ps1` with:
  - `-FlowMode onboard`: run `attach-target-repo.py` first, then run `runtime-check.ps1`
  - `-FlowMode daily`: skip attach and run `runtime-check.ps1` directly
- Added pass-through support for:
  - check settings (`Mode`, `PolicyStatus`, `TaskId`, `RunId`, `CommandId`, `RepoBindingId`)
  - optional write-governance probe (`WriteTargetPath`, `WriteTier`, `WriteToolName`, `RollbackReference`)
  - onboarding inputs (`RepoId`, `DisplayName`, `PrimaryLanguage`, `BuildCommand`, `TestCommand`, `ContractCommand`, `AdapterPreference`, `GateProfile`, `Overwrite`)
- Added bilingual usage entries in quickstart and README files.

## Verification
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 -FlowMode daily -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" -Mode quick -Json`
   - exit `0`
   - `runtime_check.payload.summary.overall_status = pass`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 -FlowMode onboard -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" -RepoId "classroomtoolkit" -DisplayName "ClassroomToolkit" -PrimaryLanguage "csharp" -BuildCommand "dotnet build ClassroomToolkit.sln -c Debug" -TestCommand "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug" -ContractCommand "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug" -Mode quick -Json`
   - exit `0`
   - `onboard_attach.payload.binding.binding_id = binding-classroomtoolkit`
   - `runtime_check.payload.summary.overall_status = pass`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - exit `0`

## Rollback
- Remove `scripts/runtime-flow.ps1`
- Remove quickstart and README references to the two-mode flow

