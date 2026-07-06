# 20260706 Global Rule Governance And Project Audit

pre_change_review

- scope: narrow the managed global rule family to Codex/Claude, add target-project rule coordination audit, and keep settings/hooks/permissions/MCP in deterministic enforcement rather than blind text sync.

control_repo_manifest_and_rule_sources

- reviewed `rules/manifest.json`, `rules/global/codex/AGENTS.md`, `rules/global/claude/CLAUDE.md`, and `rules/target-project-rule-coordination.json` together before changing sync scope.
- verified the control repo now manages only `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md`; target-repo project rules stay outside the manifest and are audited separately.

user_level_deployed_rule_files

- compared the source changes against the deployed user-level rule-copy boundary: Codex and Claude global files may be synchronized; Gemini is no longer part of the current managed family.
- same-version drift remains fail-closed in `scripts/sync-agent-rules.py`; silent overwrite is still prohibited.

repo_local_gate_scripts_and_ci

- reviewed the repo-local gate ownership in `scripts/verify-repo.ps1`, `scripts/sync-agent-rules.py`, `scripts/verify-agent-rule-family.py`, and `scripts/verify-target-project-rules.py`.
- current rule-governance slice stays repo-local: no new CI workflow, no target-repo apply path, and no settings secret synchronization.

repo_local_repo_profile

- confirmed `.governed-ai/repo-profile.json` remains the repo-local typed governance surface; this slice does not repurpose it into target-repo rule distribution.
- target-project coordination is recorded in `rules/target-project-rule-coordination.json`, not in target blind-sync entries.
- aligned the local credential/config audit so Codex and Claude stay managed blocking hosts, while Gemini remains an observed compatibility surface and no longer blocks the current rule-governance slice.

repo_local_readme_and_operator_docs

- reviewed `README*.md`, `docs/README.md`, `docs/quickstart/use-with-existing-repo*.md`, `AGENTS.md`, and `CLAUDE.md` so the control repo vs target repo boundary, shared body vs wrapper boundary, and rule vs enforcement boundary are stated consistently.

current_official_tool_loading_docs

- aligned the source changes to the current loading model already encoded in the active rule family: Codex project truth comes from `AGENTS.md`; Claude can import `@AGENTS.md` and keeps settings/hooks as deterministic enforcement; project wrappers must remain thin.

drift-integration decision

- integrated drift by keeping `governed-ai-coding-runtime` as the global rule control repo while refusing to restore target-repo blind rule distribution.
- target differences are now resolved through `audit + integration + verification`, not by manifest-owned overwrite.

reference_required_review

- this slice changes guarded reference-sensitive surfaces in `rules/manifest.json`, `rules/target-project-rule-coordination.json`, `rules/global/codex/AGENTS.md`, `rules/global/claude/CLAUDE.md`, `scripts/sync-agent-rules.py`, `scripts/verify-agent-rule-family.py`, `scripts/verify-target-project-rules.py`, `scripts/verify-pre-change-review.py`, `scripts/verify-repo.ps1`, `README*.md`, `docs/README.md`, and `docs/quickstart/use-with-existing-repo*.md`.
- the closeout also changes guarded source-and-host verifier surfaces in `scripts/build-policy-tool-credential-audit.py` and the policy-boundary sources it now enforces for the Codex/Claude managed family.

changed_surface_paths

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
- `docs/change-evidence/20260706-global-rule-governance-and-project-audit.md`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `docs/architecture/policy-tool-credential-audit-boundary.json`
- `docs/specs/policy-tool-credential-audit-spec.md`
- `rules/global/codex/AGENTS.md`
- `rules/global/claude/CLAUDE.md`
- `rules/manifest.json`
- `rules/target-project-rule-coordination.json`
- `scripts/build-policy-tool-credential-audit.py`
- `scripts/host-feedback-summary.py`
- `scripts/sync-agent-rules.py`
- `scripts/verify-agent-rule-family.py`
- `scripts/verify-pre-change-review.py`
- `scripts/verify-repo.ps1`
- `scripts/verify-target-project-rules.py`
- `tests/runtime/test_agent_rule_sync.py`
- `tests/runtime/test_host_feedback_summary.py`
- `tests/runtime/test_verify_agent_rule_family.py`
- `tests/runtime/test_verify_target_project_rules.py`

official_sources_reviewed

- reviewed the currently encoded Codex project-rule loading semantics that rely on `AGENTS.md`, fallback ordering, and concise project-doc budgeting.
- reviewed the currently encoded Claude project-rule import and settings boundary semantics that rely on `CLAUDE.md`, `@AGENTS.md`, `/status`, `/memory`, and settings/hooks as deterministic enforcement.

primary_references_reviewed

- reviewed the control-repo rule sources and operator-facing docs that define the current supported boundary: `rules/manifest.json`, `rules/global/codex/AGENTS.md`, `rules/global/claude/CLAUDE.md`, `README*.md`, `docs/README.md`, and `docs/quickstart/use-with-existing-repo*.md`.
- reviewed the current target-project pilot boundary through `rules/target-project-rule-coordination.json` and the audited `local-ai-dev-orchestrator` project-rule model.

local_runtime_evidence_reviewed

- reviewed fresh local rule-sync evidence from `python .\scripts\sync-agent-rules.py --scope All --fail-on-change` and `pwsh .\scripts\sync-agent-rules.ps1 -Scope All -Apply`.
- reviewed fresh local verifier evidence from `python .\scripts\verify-agent-rule-family.py`, `python .\scripts\verify-target-project-rules.py --targets local-ai-dev-orchestrator`, and the targeted runtime/unit test slice covering sync, host-feedback, family verifier, target-project audit, and pre-change review.
- reviewed the policy-tool-credential audit boundary and governance-hub certification closeout so local Gemini preference drift is reported as observation, not misclassified as a blocker for the current Codex/Claude-only managed family.

source_decision

- source decision: keep `governed-ai-coding-runtime` as the global rule control repo for Codex/Claude only, preserve project-level rule differences in each target repo, and use audit + integration + verification rather than target-repo blind distribution.

reference_basis_review

- this slice changes reference-governed rule and release-gate surfaces in `rules/manifest.json`, `rules/target-project-rule-coordination.json`, `rules/global/codex/AGENTS.md`, `rules/global/claude/CLAUDE.md`, `scripts/sync-agent-rules.py`, `scripts/verify-agent-rule-family.py`, `scripts/verify-target-project-rules.py`, and `scripts/verify-repo.ps1`.
- this slice also changes the repo-owned policy-boundary builder `scripts/build-policy-tool-credential-audit.py`, so the reference-required review must mention that verifier surface explicitly rather than only the downstream aggregated gate.
- `docs/specs/policy-tool-credential-audit-spec.md` now codifies the managed-family vs observed-compatibility split, so its workflow-governance reference basis must be reviewed alongside the release-gate basis used by `scripts/verify-repo.ps1`.
- `scripts/verify-repo.ps1` remains the repo-owned release/contract aggregation entrypoint, so the new verifier/audit surfaces must stay reference-backed rather than prose-only.

reference_basis_surface_ids

- `release-gate-and-ci-boundaries`
- `workflow-governance-and-spec-driven-delivery`

required_local_reference_ids_reviewed

- `1code`
- `aider`
- `anthropic-claude-code`
- `anthropic-claude-code-action`
- `github-spec-kit`
- `github-copilot-cli`
- `obra-superpowers`
- `openclaw-code-agent`
- `openai-codex`
- `swe-agent`

reference_adoption_decision

- adopted only the reference-backed parts that improve rule-family consistency, target-project wrapper audits, and release-style gate composition for this repo.
- adopted the workflow/spec-driven reference signals only far enough to justify explicit managed-family boundary documentation in `docs/specs/policy-tool-credential-audit-spec.md`; no blind expansion back to Gemini/global multi-tool sync was reintroduced.
- rejected restoration of target-repo blind rule distribution, settings-value sync, or prose-only enforcement even when older historical materials still mention broader rollout surfaces.

## Summary

本次切片把规则治理面正式收口到新的边界：

- `governed-ai-coding-runtime` 继续作为规则控制仓
- 只管理 `Codex + Claude` 的全局用户级规则源与同步
- 不恢复 target-repo blind apply / blind sync
- 目标仓项目规则只做 `AGENTS.md + CLAUDE.md thin wrapper` 协同审计

## Why This Scope

- global-only sync 仍然有价值，因为它能把跨仓稳定语义统一到 `~/.codex/AGENTS.md` 与 `~/.claude/CLAUDE.md`
- blind target-repo distribution 已经被证明会放大 drift，尤其会把控制仓文本和目标仓真实 gate/evidence/rollback 事实混在一起
- 项目级差异必须以目标仓自己的 `AGENTS.md` 为真源，再由 `CLAUDE.md` thin wrapper 补平台差异，才能形成 `global WHAT + project WHERE/HOW + wrapper DELTA + enforcement` 的协同

## Adopted Practices

- 吸收的官方工具加载语义：
  - Codex：`AGENTS.md` 分层加载、fallback、override、size budget
  - Claude：`CLAUDE.md` / `@AGENTS.md` import、`CLAUDE.local.md`、settings/hooks 边界
- 吸收的社区实践：
  - 共同项目规则主体保持短而硬
  - wrapper 不复制共同正文
  - settings / hooks / permissions / MCP 归 deterministic enforcement，不靠 prose 代替

## Landed Surfaces

- `rules/manifest.json`
- `rules/target-project-rule-coordination.json`
- `rules/global/codex/AGENTS.md`
- `rules/global/claude/CLAUDE.md`
- `scripts/verify-agent-rule-family.py`
- `scripts/verify-target-project-rules.py`
- `scripts/verify-repo.ps1`
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `AGENTS.md`
- `CLAUDE.md`

## Commands And Verification

- `python .\scripts\sync-agent-rules.py --scope All --fail-on-change`
- `python .\scripts\verify-agent-rule-family.py`
- `python .\scripts\verify-target-project-rules.py --targets local-ai-dev-orchestrator`
- `pwsh .\scripts\verify-repo.ps1 -Check Contract`

## Rollback

- `git revert` 本次控制仓规则/文档/verifier 变更
- 如已下发全局规则副本，再运行回滚后的 `pwsh .\scripts\sync-agent-rules.ps1 -Scope All -Apply`
- 不对目标仓执行 blind rollback；目标仓项目规则只回滚其自身的集成 diff
