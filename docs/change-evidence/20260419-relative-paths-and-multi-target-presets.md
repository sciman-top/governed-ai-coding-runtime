# 20260419 Relative Paths And Multi-Target Presets

## Purpose
Improve operator ergonomics by removing hard dependence on absolute paths and adding reusable target presets, including self-runtime and skills-manager.

## Basis
- `scripts/runtime-check.ps1`
- `scripts/runtime-flow.ps1`
- `scripts/runtime-flow-preset.ps1`
- `scripts/runtime-flow-classroomtoolkit.ps1`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `README.md`
- `README.en.md`
- `README.zh-CN.md`

## Change
- Added relative-path normalization in:
  - `runtime-check.ps1`
  - `runtime-flow.ps1`
- Added `runtime-flow-preset.ps1` with target presets:
  - `classroomtoolkit`
  - `self-runtime`
  - `skills-manager`
- Reworked `runtime-flow-classroomtoolkit.ps1` into a compatibility wrapper over preset flow.
- Updated bilingual quickstart/readme docs with preset usage examples.

## Verification
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target self-runtime -FlowMode onboard -TaskId "task-self-onboard-001" -RunId "run-self-onboard-001" -CommandId "cmd-self-onboard-001" -Json`
   - exit `0`
   - attach + quick verification gates pass
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target self-runtime -FlowMode daily -Json`
   - exit `0`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target skills-manager -FlowMode onboard -Json`
   - exit `0`
   - generated `.governed-ai` light pack for `skills-manager`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target skills-manager -FlowMode daily -Json`
   - exit `0`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 -FlowMode daily -AttachmentRoot "." -AttachmentRuntimeStateRoot "..\governed-ai-runtime-state\self-runtime" -TaskId "task-relative-001" -RunId "run-relative-001" -CommandId "cmd-relative-001" -Json`
   - exit `0`
   - relative paths normalized to absolute and full quick chain passes
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
   - exit `0`

## Rollback
- Remove `runtime-flow-preset.ps1`
- Revert relative-path normalization in runtime check and flow scripts
- Revert preset references in quickstart/readme docs
