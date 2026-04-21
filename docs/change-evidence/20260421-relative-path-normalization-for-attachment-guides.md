# 20260421 Relative Path Normalization For Attachment Guides

## Change Basis
- Repository root moved from `D:\OneDrive\CODE\...` to `D:\CODE\...`; hard-coded absolute examples in active docs required manual edits and created drift risk.
- Current product behavior already supports relative path inputs for attachment commands; docs can be normalized without runtime code changes.
- This change focuses on active docs/tests only. Historical evidence under `docs/change-evidence/` and runtime artifacts under `.runtime/` remain immutable as historical records.
- Active rule path: `governed-ai-coding-runtime 仓库根目录（repo root）/AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=relative-path-normalization-attachment-guides`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Updated `AGENTS.md`
- Updated `README.md`
- Updated `README.zh-CN.md`
- Updated `README.en.md`
- Updated `docs/quickstart/use-with-existing-repo.md`
- Updated `docs/quickstart/use-with-existing-repo.zh-CN.md`
- Updated `docs/product/target-repo-attachment-flow.md`
- Updated `docs/product/target-repo-attachment-flow.zh-CN.md`
- Updated `tests/runtime/test_workspace_allocation.py`
- Updated `docs/change-evidence/README.md`
- Added `docs/change-evidence/20260421-relative-path-normalization-for-attachment-guides.md`

## Summary
- Normalized active attachment examples from machine-specific absolute paths to repo-root-relative paths:
  - `D:\OneDrive\CODE\ClassroomToolkit` -> `..\ClassroomToolkit`
  - `D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit` -> `.runtime\attachments\classroomtoolkit`
  - `D:\OneDrive\CODE\governed-ai-runtime-state\self-runtime` -> `..\governed-ai-runtime-state\self-runtime`
- Updated project scope metadata in `AGENTS.md` to repository-root semantics to avoid future root-path churn.
- Kept one intentional absolute-path test input (`C:/live-repo`) to preserve rejection coverage for arbitrary absolute workspace roots.

## Verification
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```
- Exit code: `0`
- Key output: `OK python-bytecode`, `OK python-import`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```
- Exit code: `0`
- Key output: `OK runtime-unittest`, `Ran 256 tests`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```
- Exit code: `0`
- Key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```
- Exit code: `0`
- Key output: `OK gate-command-build`, `OK gate-command-test`, `OK gate-command-contract`, `OK gate-command-doctor`

```powershell
rg -n --hidden --no-ignore -S "D:\\OneDrive\\CODE|D:/OneDrive/CODE" . -g "!**/.git/**" -g "!**/.runtime/**" -g "!docs/change-evidence/**"
```
- Exit code: `1` (expected: no matches)
- Key output: empty result

## Risks
- Relative examples assume commands are run from runtime repository root; invoking from other working directories requires adjusting relative paths.
- Historical evidence still contains old absolute paths by design; operators must distinguish active guidance from historical records.

## Rollback
- Revert the listed files to restore previous absolute-path examples.
- Remove this evidence file and its index entry in `docs/change-evidence/README.md` if superseded.
