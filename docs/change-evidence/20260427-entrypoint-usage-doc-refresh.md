# Entrypoint Usage Documentation Refresh

## Context
- Date: 2026-04-27
- Change type: documentation / operator guidance
- Goal: make the current main entrypoints, one-command apply paths, usage flow, and concrete AI-coding assistance explicit in the README and quickstart docs.

## Updated Surfaces
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
- `docs/quickstart/ai-coding-usage-guide.md`
- `docs/quickstart/ai-coding-usage-guide.zh-CN.md`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`

## Entrypoint Contract
- Target-repo daily/batch entrypoint: `scripts/runtime-flow-preset.ps1`
- Agent-rule sync entrypoint: `scripts/sync-agent-rules.ps1`
- Self-repo verification entrypoint: `scripts/verify-repo.ps1 -Check All`

## Verification
- To run after this change:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -ListTargets`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Rollback
- Revert this evidence file and the listed documentation updates with git.
