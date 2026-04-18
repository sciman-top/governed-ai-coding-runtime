# 20260418 Bilingual Usage Guides And Path Semantics

## Purpose
Make usage / guide / quickstart docs available in both Chinese and English, and document path-change semantics plus self-attachment behavior clearly.

## Basis
- `docs/quickstart/*`
- `docs/product/target-repo-attachment-flow*.md`
- `docs/product/session-bridge-commands*.md`
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`

## Changes
- recorded the bilingual coverage rule in:
  - `AGENTS.md`
  - `docs/README.md`
- added Chinese versions:
  - `docs/quickstart/single-machine-runtime-quickstart.zh-CN.md`
  - `docs/quickstart/multi-repo-trial-quickstart.zh-CN.md`
  - `docs/quickstart/use-with-existing-repo.zh-CN.md`
  - `docs/product/target-repo-attachment-flow.zh-CN.md`
  - `docs/product/session-bridge-commands.zh-CN.md`
  - `docs/product/first-readonly-trial.zh-CN.md`
  - `docs/product/multi-repo-trial-loop.zh-CN.md`
  - `docs/product/codex-direct-adapter.zh-CN.md`
  - `docs/product/minimal-approval-evidence-console.zh-CN.md`
  - `docs/product/verification-runner.zh-CN.md`
  - `docs/product/adapter-capability-tiers.zh-CN.md`
  - `docs/product/adapter-degrade-policy.zh-CN.md`
  - `docs/product/approval-flow.zh-CN.md`
  - `docs/product/public-usable-release-criteria.zh-CN.md`
  - `docs/product/delivery-handoff.zh-CN.md`
  - `docs/product/write-side-tool-governance.zh-CN.md`
  - `docs/product/write-policy-defaults.zh-CN.md`
  - `docs/product/second-repo-reuse-pilot.zh-CN.md`
- documented path-change behavior:
  - target repo path changes require the new `attachment_root`
  - runtime state path changes require the new `attachment_runtime_state_root` or a fresh attach
  - runtime repo path changes do not change semantics, but operator commands must point at the new script location
- documented self-attachment behavior:
  - the runtime repo itself can be attached as a target repo
  - `runtime_state_root` must remain outside the repo root

## Verification
1. `python scripts/attach-target-repo.py --target-repo "D:\OneDrive\CODE\governed-ai-coding-runtime" --runtime-state-root "D:\OneDrive\CODE\governed-ai-runtime-state\self-runtime" --repo-id "governed-ai-coding-runtime" --display-name "Governed AI Coding Runtime" --primary-language "python" --build-command "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1" --test-command "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime" --contract-command "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract" --adapter-preference process_bridge --overwrite`
   - exit `0`
2. `python scripts/run-governed-task.py status --json --attachment-root "D:\OneDrive\CODE\governed-ai-coding-runtime" --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-runtime-state\self-runtime"`
   - exit `0`
   - `binding_state = healthy`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - exit `0`

## Rollback
- remove the new Chinese guide variants
- revert README / docs index bilingual link updates
- revert the path/self-attachment explanation blocks
