# 20260606 Host Family Architecture Refresh

## Goal
- 把本仓对 AI coding 宿主的长期建模，从“并列的产品名/CLI 名称”升级为 `host family + capability surface`。
- 基于 2026-06-06 最新官方信息，明确 Google 侧长期主方向是 `Antigravity`，`Gemini CLI` 只保留为兼容/迁移桥。

## Official Sources
- Google Developers Blog:
  - <https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/>
  - 结论：Google 官方已明确 `Gemini CLI -> Antigravity CLI` 的长期转向。
- Google official repository:
  - <https://github.com/google-antigravity/antigravity-cli>
  - 结论：`Antigravity CLI` 与 `Antigravity 2.0` 共享 agent engine、shared settings、session export continuity。
- Anthropic official quickstart:
  - <https://code.claude.com/docs/en/quickstart>
  - 结论：`Claude Code` 已是多 surface 宿主家族，而不是单一 terminal CLI。
- Anthropic release notes:
  - <https://support.claude.com/en/articles/12138966-release-notes>
  - 结论：`Claude Cowork` 已在 `Claude Desktop` 面向 macOS / Windows 推广，并具备本地 VM 与本地文件/MCP 集成语义。
- OpenAI official docs:
  - <https://developers.openai.com/codex/guides/agents-md>
  - 结论：`AGENTS.md`、config layering、sandbox/approval 仍是 Codex 控制面核心语义。
- OpenAI official Codex App docs:
  - <https://developers.openai.com/codex/app/features>
  - <https://developers.openai.com/codex/app/computer-use>
  - <https://developers.openai.com/codex/remote-connections>
  - 结论：`Codex` 现在不能只按 CLI 理解；`Codex App` 已是正式 desktop host surface，并覆盖 worktrees、automations、in-app browser、Computer Use、remote/mobile continuation 与 SSH-host connected workflows。

## pre_change_review
- pre_change_review: required because this working tree includes sensitive governance surfaces under `docs/targets/target-repo-governance-baseline.json`, self-runtime `.governed-ai/repo-profile.json`, `scripts/verify-repo.ps1`, and an already-dirty managed rule source at `rules/projects/cockpit-tools-local/codex/AGENTS.md`.
- control_repo_manifest_and_rule_sources: reviewed `rules/manifest.json`, root `AGENTS.md`, `docs/targets/target-repo-governance-baseline.json`, `docs/targets/target-repo-rollout-contract.json`, and the host-family architecture source docs before changing runtime-evolution policy, governance baseline wording, and target sync revision.
- user_level_deployed_rule_files: no user-level global `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` deployment was edited in this slice; user-level rule distribution remains governed by `python scripts/sync-agent-rules.py --scope All --fail-on-change` plus later explicit sync.
- target_repo_deployed_rule_files: target repo rule files were not manually edited in this slice; after bumping the governance baseline `sync_revision`, the standard `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` path was used to refresh target `.governed-ai/repo-profile.json` governance projections across the seven managed targets.
- target_repo_gate_scripts_and_ci: reviewed the active gate contract through `scripts/verify-repo.ps1`, `scripts/verify-target-repo-governance-consistency.py`, `scripts/runtime-flow-preset.ps1`, and the documented hard-gate order so the Google host-family wording change would not weaken `build -> test -> contract/invariant -> hotspot`.
- target_repo_repo_profile: reviewed the baseline-owned `rule_file_coordination_policy` projection in target repo profiles and then synchronized the changed field through the governed baseline apply flow instead of hand-editing target repos.
- target_repo_readme_and_operator_docs: reviewed `README.md`, `README.zh-CN.md`, `README.en.md`, `docs/README.md`, `docs/architecture/README.md`, and `docs/plans/runtime-evolution-review-plan.md` so the host-family interpretation and official-source wording stay aligned across operator-facing entry documents.
- current_official_tool_loading_docs: refreshed against current OpenAI Codex `AGENTS.md` docs, Anthropic `Claude Code` quickstart/release notes, and Google official Antigravity announcement/repository/docs so the new wording reflects live official loading and product-surface semantics rather than older Gemini CLI assumptions.
- current_official_tool_loading_docs: refreshed against current OpenAI Codex `AGENTS.md` docs plus official `Codex App / Computer Use / Remote connections` docs, Anthropic `Claude Code` quickstart/release notes, and Google official Antigravity announcement/repository/docs so the new wording reflects live official loading and product-surface semantics rather than older CLI-only assumptions.
- drift-integration decision: integrate Google-host-direction drift by updating the control repo source-of-truth first, preserving existing `GEMINI.md` compatibility paths where they are still the real deployed bridge, then synchronizing target governance profile drift through the canonical baseline-apply entrypoint instead of overwriting unrelated dirty rule-source state.

## Changes
- 更新 `docs/architecture/runtime-evolution-policy.json`
  - 把 Google 官方最小必需 source catalog 从 `Gemini CLI` 文档切换为 `Antigravity` 公告、官方仓库、官方 docs 入口。
- 更新 `scripts/evaluate-runtime-evolution.py`
  - 把运行时演进评审的 Google 必需 source IDs 切换为 `Antigravity` 主方向。
- 更新 `tests/runtime/test_runtime_evolution.py`
  - 把 Google 侧 required host 断言从 `github.com/google-gemini` 改为 `developers.googleblog.com`、`github.com/google-antigravity`、`antigravity.google`。
- 更新 `docs/targets/target-repo-governance-baseline.json`
  - 明确当前 target-repo 兼容层仍使用 `~/.gemini/GEMINI.md` 与 `.geminiignore` 体系，但这是 Google host-family 的当前兼容路径，不再等同于长期主产品方向。
- 更新 `docs/targets/target-repo-governance-baseline.json` 与 `docs/targets/target-repo-rollout-contract.json`
  - 把 `sync_revision` 提升到 `2026-06-06.1`，为目标仓治理基线同步提供明确版本锚点。
- 新增 `docs/architecture/host-family-capability-surface-blueprint.md`
  - 正式固化“最佳工程终态”的宿主抽象、能力维度和 Google/Claude/Codex 的当前解释。
- 补强 `Codex family` 解释
  - 明确 `Codex` 不是单一 CLI 路径，而是包含 `Codex App`、`Remote connections`、`Computer Use` 的多 surface host family。
- 更新 `docs/architecture/README.md`
  - 把新蓝图纳入架构索引阅读顺序。
- 更新 `scripts/build-policy-tool-credential-audit.py`
  - 把 “main Gemini CLI settings” 改成更中性的 “current Google local settings baseline”，避免安全审计文案继续暗示旧产品名是主方向。

## Verification
- `python -m unittest tests.runtime.test_runtime_evolution -v`
- `python -m unittest tests.runtime.test_target_repo_governance_consistency -v`
- `python scripts/evaluate-runtime-evolution.py --as-of 2026-06-06 --write-artifacts`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Risks
- 当前规则同步与目标仓兼容层仍保留 `GEMINI.md` 相关路径，这属于真实运行兼容事实，不应被误读为长期产品方向未变。
- 若 Google 后续再次调整文档入口或 product naming，`runtime-evolution` source catalog 需要在下一轮 review 中继续刷新。

## Rollback
- 回滚本次相关文档、脚本、测试、生成产物和本证据文件。
- 若需要恢复旧 source catalog，可回退 `runtime-evolution-policy.json`、`evaluate-runtime-evolution.py`、`test_runtime_evolution.py` 到上一提交，但这会重新把 Google 长期方向描述为已过时的 `Gemini CLI` 主路径。
