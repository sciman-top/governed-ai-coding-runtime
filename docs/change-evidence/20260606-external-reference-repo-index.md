# 20260606 External Reference Repo Index

## Goal
- Add a project-owned pointer surface for the local external reference repos so future operators and agents can find the curated official and community sources without relying on prior chat context.

## Changes
- Added [External Reference Repo Index](../research/external-reference-repos-index.md) with:
  - local external reference root and clone-results pointer
  - official/primary reference set
  - community mechanism-source set
  - recommended reading order
  - explicit boundary that external repos are mechanism inputs, not source of truth
- Linked the new index from:
  - [Root README](../../README.md)
  - [中文 README](../../README.zh-CN.md)
  - [English README](../../README.en.md)
  - [Docs Index](../README.md)
  - [Change Evidence Index](./README.md)

## Verification
- `rg -n "External Reference Repo Index|外部参考索引|external reference index" README.md README.zh-CN.md README.en.md docs/README.md docs/change-evidence/README.md docs/research/external-reference-repos-index.md`
- `Test-Path D:\CODE\external\ai-coding-runtime-references\README.md`
- `Test-Path D:\CODE\external\ai-coding-runtime-references\clone-results.json`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Gate Status
| Gate | Status | Reason | Alternative Verification | Evidence Link | Expires At |
| --- | --- | --- | --- | --- | --- |
| `build` | `gate_na` | docs-only index and link changes; no buildable artifact changed | docs link grep plus external index path presence | this file | `2026-07-06` |
| `test` | `gate_na` | no runtime code, contract code, or test target changed | docs link grep plus docs verifier | this file | `2026-07-06` |
| `contract/invariant` | `gate_na` | no spec/schema/catalog or runtime contract surface changed | docs link grep plus docs verifier | this file | `2026-07-06` |
| `hotspot` | `gate_na` | no runtime health or doctor surface changed | docs link grep plus docs verifier | this file | `2026-07-06` |

## Risks
- The local external reference root is machine-local (`D:\CODE\external\ai-coding-runtime-references`), so another machine needs its own local clone set even though the project-owned index now explains the expected shape.
- The reference set can drift if future external additions update the out-of-repo README but not this project-owned index.

## Rollback
- Revert the README/docs index links and delete `docs/research/external-reference-repos-index.md`.
- Preferred rollback: restore this change from git history.
