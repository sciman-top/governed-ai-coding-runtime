# 2026-04-22 Milestone-Only Auto Commit Profile Preset

## Goal
- Provide a ready-to-use target-repo profile preset that auto-commits only at milestone checkpoints.

## Changes
- Added new repo-profile example preset:
  - `schemas/examples/repo-profile/target-repo-milestone-autocommit.example.json`
- Updated examples index and validation snippet:
  - `schemas/examples/README.md`

## Preset Behavior
- `auto_commit_policy.enabled = true`
- `auto_commit_policy.on = ["milestone"]`
- Requires caller to pass milestone marker (for example via `-MilestoneTag milestone`).
- Commit message template defaults to Chinese.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

## Rollback
- `git checkout -- schemas/examples/repo-profile/target-repo-milestone-autocommit.example.json schemas/examples/README.md`
- or `git revert <this-commit>`
