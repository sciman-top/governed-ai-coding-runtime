# 20260418 Codex Integration Documentation Clarification

## Goal
- clarify how this repository should be used with Codex CLI/App today
- remove wording that could be mistaken for "direct Codex coding execution is already implemented"
- add bilingual documentation for current state and future direct-adapter boundary

## Basis
- user request to explain practical Codex usage and assess documentation completeness
- current runtime implementation in `scripts/run-governed-task.py`
- current read-only trial boundary in `docs/product/first-readonly-trial.md`

## Changes
- added English guide:
  - `docs/product/codex-cli-app-integration-guide.md`
- added Chinese guide:
  - `docs/product/codex-cli-app-integration-guide.zh-CN.md`
- updated `README.md`, `README.zh-CN.md`, `README.en.md`, and `docs/README.md` to link the new guides
- tightened wording so `run-governed-task.py` is described as a runtime smoke path rather than a direct Codex adapter
- updated `docs/quickstart/single-machine-runtime-quickstart.md` and `docs/product/public-usable-release-criteria.md` with the same boundary note

## Commands
| cmd | exit_code | key_output |
|---|---:|---|
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` | 0 | docs, scripts, schemas, and runtime tests all pass after the wording updates |

## Risks
- the repository is now more explicit about current limitations, but some older historical planning docs still discuss future direct Codex integration as a target state
- this change clarifies the boundary; it does not implement a direct Codex adapter

## Rollback
- revert the new bilingual integration guides
- revert the wording changes in README, docs index, quickstart, and release criteria if the project later lands a true direct Codex adapter and wants to replace these docs
