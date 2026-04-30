# 2026-04-30 Codex Efficiency-First Defaults

## Goal
- Strengthen this repository's documented and rendered Codex posture so the long-lived rule is `efficiency first`, not any single temporary model combo.
- Keep the principle explicit across docs, local status payloads, and Operator UI: low interruption, continuous execution, lower token/cost burn, and high throughput.
- Treat `gpt-5.4 + medium + never` only as the current implementation choice under that principle.
- Keep `cli_auth_credentials_store = "file"` in the recommended local Codex setup.
- Mark `model_auto_compact_token_limit = 220000` as the paired recommendation for the current `272000` context window instead of introducing multiple default profiles.

## Scope
- `AGENTS.md`
- `docs/README.md`
- `docs/quickstart/ai-coding-usage-guide.md`
- `docs/quickstart/ai-coding-usage-guide.zh-CN.md`
- `docs/product/host-feedback-loop.md`
- `docs/product/host-feedback-loop.zh-CN.md`
- `scripts/operator.ps1`
- `scripts/lib/codex_local.py`
- `scripts/Optimize-CodexLocal.ps1`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `tests/runtime/test_codex_local.py`
- `rules/projects/governed-ai-coding-runtime/codex/AGENTS.md`
- `rules/projects/governed-ai-coding-runtime/claude/CLAUDE.md`
- `rules/projects/governed-ai-coding-runtime/gemini/GEMINI.md`
- `scripts/host-feedback-summary.py`

## Changes
- Added `cli_auth_credentials_store = "file"` to the Codex recommended default set used by local config-health checks and the one-click optimizer.
- Expanded the explicit `recommended_defaults` payload in Codex local status so the Operator UI can render:
  - the long-lived `efficiency first` principle
  - the four principle bullets
  - the current temporary choice `gpt-5.4 + medium + never`
  - the compact policy and manual escalation note
- Updated the Operator UI Codex tab text to clearly present:
  - core principle: `efficiency first`
  - current temporary choice: `gpt-5.4 + medium + never`
  - compact policy: `model_auto_compact_token_limit = 220000`
-  - manual escalation: switch to a stronger model or reasoning level only when a task truly needs deeper reasoning
- Updated the repo README surfaces so the local Codex optimization entrypoint and UI description use the same defaults wording.
- Elevated the same principle into the project-level `AGENTS.md`, docs index, AI coding quickstart, and host feedback loop docs so it becomes a repository-level operating rule instead of only a UI/config note.
- Added the same principle to operator-facing script entrypoints so `operator.ps1 -Action Help` and `Optimize-CodexLocal.ps1` expose the rule directly during normal local usage.
- Added unit coverage for the new Codex recommended-defaults payload.
- Synced the same concise rule text back into the manifest-managed Codex/Claude/Gemini project rule sources so `agent rule sync` no longer sees same-version drift between the control-repo source and the deployed root copies.
- Made `scripts/host-feedback-summary.py` emit ASCII-safe JSON on stdout so Windows locale-dependent subprocess readers do not fail with `gbk` decode errors during runtime tests.

## pre_change_review
- `control_repo_manifest_and_rule_sources`: checked `rules/manifest.json`, the root deployed `AGENTS.md`, and the managed rule source files under `rules/projects/governed-ai-coding-runtime/{codex,claude,gemini}` before editing; the source-of-truth drift was real and had to be integrated back into the control repo instead of overwritten from the deployed copy.
- `user_level_deployed_rule_files`: reviewed the current rule-distribution model through `python scripts/sync-agent-rules.py --scope All --fail-on-change`; this change does not alter user-level rule semantics, but the dry-run remains the authoritative proof path that user-level deployed files still align through the manifest.
- `target_repo_deployed_rule_files`: reviewed the same manifest-managed distribution path and kept the project-rule family synchronized at the source level so downstream deployed project files can be regenerated without accepting same-version drift.
- `target_repo_gate_scripts_and_ci`: checked `scripts/verify-repo.ps1`, `scripts/verify-pre-change-review.py`, and the current contract gate order before changing evidence/rule files; no gate order or CI semantics were changed by this patch, only the evidence and managed source alignment needed by the existing contract checks.
- `target_repo_repo_profile`: checked the current repo-profile-driven quick/runtime path through `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json` and `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`; no repo-profile semantics changed here.
- `target_repo_readme_and_operator_docs`: checked the already-updated operator-facing docs (`README*`, `docs/README.md`, quickstart, host-feedback-loop) and verified this patch only brings manifest-managed rule sources and verification evidence into line with those repo-facing documents.
- `current_official_tool_loading_docs`: checked the existing repository understanding of Codex/Claude/Gemini rule-loading behavior that already governs this rule family; this patch does not change loading semantics, only preserves the concise efficiency-first rule across the managed source files that feed those deployments.
- `drift-integration decision`: no uncontrolled same-version drift was accepted; the concise principle text was integrated into the manifest-managed source files, and the evidence file was expanded so the existing `pre-change review` gate can validate the change set without weakening gate semantics.

## Recommendation Basis
- OpenAI's configuration reference documents `model_auto_compact_token_limit` as the explicit compaction trigger threshold, but does not publish one universal recommended number.
- OpenAI's GPT-5.4 model page shows that long-context pricing changes after `272K` input tokens, so keeping the working threshold below that boundary fits the repository's efficiency-first posture.
- Community Codex usage examples often raise context far higher for frontier usage, but issue traffic also shows compaction and near-limit instability when sessions stay too close to the model ceiling.
- For this repository's stated goal of lower interruption, lower token burn, automatic continuous execution, and one stable default, `220000` remains the recommended compromise. It leaves roughly `52000` tokens of headroom on a `272000` window, which is about `19%` slack.

## Verification
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_operator_entrypoint`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Rollback
- Revert the files listed in Scope and remove this evidence file.
