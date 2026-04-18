# 20260418 One-Command Runtime Check

## Purpose
Improve day-to-day operator ergonomics by adding a one-command attachment check path that chains the most common runtime governance commands.

## Basis
- `scripts/runtime-check.ps1`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `README.md`
- `README.en.md`
- `README.zh-CN.md`

## Change
- Added `scripts/runtime-check.ps1` to run:
  - attachment-aware `status`
  - attachment-aware `doctor`
  - `session-bridge request-gate`
  - `verify-attachment` (default on)
  - optional `govern-attachment-write` when `-WriteTargetPath` is given
- Added explicit exit semantics:
  - exit `0` only when the chain succeeds and verification results are all `pass`
  - exit `1` when any step fails or any gate result is `fail`
- Added Chinese and English usage entrypoints in quickstart and README docs.

## Verification
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1 -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" -Mode "quick" -WriteTargetPath "src/ClassroomToolkit.App/MainWindow.ZOrder.cs" -WriteTier "medium" -Json`
   - script runs full chain and returns structured payload
   - when target repo gate commands fail, script returns exit `1` and preserves failure visibility
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - docs links and usage references remain valid

## Risks
- The one-command path intentionally inherits target-repo gate outcomes. If the target repo has an active process lock or failing tests, this script should fail fast and report that state.

## Rollback
- Remove `scripts/runtime-check.ps1`
- Remove references from quickstart and README docs

