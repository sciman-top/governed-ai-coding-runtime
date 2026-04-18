# 20260418 ClassroomToolkit Preset Flow

## Purpose
Provide a near zero-parameter operator entrypoint for the common `ClassroomToolkit` target-repo flow.

## Basis
- `scripts/runtime-flow-classroomtoolkit.ps1`
- `scripts/runtime-flow.ps1`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `README.md`
- `README.en.md`
- `README.zh-CN.md`

## Change
- Added `scripts/runtime-flow-classroomtoolkit.ps1` preset wrapper with:
  - default `AttachmentRoot = D:\OneDrive\CODE\ClassroomToolkit`
  - default runtime state root for `classroomtoolkit`
  - `daily` and `onboard` modes
  - onboarding defaults for repo id, language, adapter preference, and dotnet gate commands
- Added bilingual usage examples in quickstart and README documents.

## Verification
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode daily -Json`
   - exit `1` in this run
   - cause: underlying `verify-attachment` returned `test=fail` / `contract=fail` from target-repo gate execution
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode onboard -Json`
   - exit `1` in this run for the same reason as above
   - attach stage still succeeded (`binding-classroomtoolkit` validated)
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode daily -SkipVerifyAttachment -Json`
   - exit `0`
   - payload reports `overall_status = pass`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode onboard -SkipVerifyAttachment -Json`
   - exit `0`
   - attach and runtime-check chain pass
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - exit `0`

## Note
- This preset wrapper intentionally preserves strict behavior from `runtime-flow.ps1` and `runtime-check.ps1`.
- If target-repo verification gates fail, preset flow should fail and report that state instead of masking it.

## Rollback
- Remove `scripts/runtime-flow-classroomtoolkit.ps1`
- Remove preset usage references from quickstart and README files
