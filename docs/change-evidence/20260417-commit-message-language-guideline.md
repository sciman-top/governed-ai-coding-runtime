# 2026-04-17 Commit Message Language Guideline

## Summary
Added a project-level commit message guideline to `AGENTS.md`: commit messages should be Chinese-first, but not strictly Chinese-only. The intent is to keep history readable and searchable across tools without turning language choice into a needless hard constraint.

## Basis
- User requested the rule be formalized in the project.
- The project already uses mixed Chinese/English documentation and technical terms.
- Strict Chinese-only commit messages would reduce searchability and interoperability without adding governance value.

## Files Changed
- Updated `AGENTS.md`

## Commands

### Rule presence check
```powershell
Select-String -Path AGENTS.md -Pattern '提交信息规范','提交信息以中文为主','不强制全中文','subject' | ForEach-Object { "{0}:{1}:{2}" -f $_.Path, $_.LineNumber, $_.Line.Trim() }
```
Result: the new section is present in `AGENTS.md`.

### Diff whitespace check
```powershell
git diff --check
```
Result: clean diff; only CRLF conversion warnings for tracked files in the working tree.

## Gate Status
| gate | status | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|
| build | `gate_na` | no build artifacts or runtime services are involved | rule presence check | `docs/change-evidence/20260417-commit-message-language-guideline.md` | `2026-05-31` |
| test | `gate_na` | no test harness exists for this docs-only rule change | rule presence check and diff whitespace check | `docs/change-evidence/20260417-commit-message-language-guideline.md` | `2026-05-31` |
| contract/invariant | `active` | repository contract lives in `AGENTS.md` and was updated directly | direct content verification | `docs/change-evidence/20260417-commit-message-language-guideline.md` | `n/a` |
| hotspot | `gate_na` | no runtime doctor/health path exists for a docs-only rule | direct content verification | `docs/change-evidence/20260417-commit-message-language-guideline.md` | `2026-05-31` |

## Rollback
Remove the new `## E. 提交信息规范` section from [AGENTS.md](/D:/OneDrive/CODE/governed-ai-coding-runtime/AGENTS.md) and delete this evidence file.

## Outcome
The repository now encodes the commit-message policy explicitly: Chinese-first for readability and consistency, but not Chinese-only.
