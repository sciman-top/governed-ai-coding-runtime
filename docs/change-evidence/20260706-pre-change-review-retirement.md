pre_change_review

- scope: retire target-repo apply-all/governance surfaces, attachment/session-bridge write surfaces, and project-level rule distribution while keeping repo-local runtime gates, global-only rule sync, and historical evidence.
- changed surfaces: `rules/manifest.json`, deleted `rules/projects/**`, repo-local `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`, `scripts/sync-agent-rules.*`, `scripts/verify-repo.ps1`, `scripts/operator.ps1`, `run.ps1`, contract packages, control-plane routes, retired target-repo/session-bridge scripts, schema/spec/example cleanup, and operator/quickstart docs.

control_repo_manifest_and_rule_sources

- compared control-repo sources in `rules/manifest.json`, root rule files, and the remaining repo-local rule entrypoints against the new end-state: global-user copies stay managed; target-repo project entries are removed; this repository's own root rule files stay directly maintained.
- verified that deleted `rules/projects/**` files represent retired distribution sources rather than still-active repo-local runtime inputs.

user_level_deployed_rule_files

- confirmed the retained sync surface is only the user-level global rule copies under `~/.codex`, `~/.claude`, and `~/.gemini`; `scripts/sync-agent-rules.py --scope All --fail-on-change` is expected to operate only on those global entries after this slice.
- no target-repo deployed rule copy is treated as current required output after retirement.

repo_local_gate_scripts_and_ci

- reviewed repo-local gate ownership across `scripts/build-runtime.ps1`, `scripts/verify-repo.ps1`, `scripts/doctor-runtime.ps1`, and runtime/unit checks that remain in scope after retirement.
- removed current gate dependencies on target-repo rollout, session-bridge, speed-KPI, and all-history promotion artifact validation while preserving repo-local contract, host feedback, self-evolution, and continuity checks.

repo_local_repo_profile

- compared `.governed-ai/repo-profile.json` and repo-profile contract surfaces to the retired end-state; removed target-repo pre-change review inputs and kept repo-local policy, gate, and host/tool loading fields.
- confirmed repo-local profile remains the current typed policy surface; deleted target-repo profile examples are no longer part of the active contract set.

repo_local_readme_and_operator_docs

- reviewed current operator and user-facing docs for retired claims, including `README*.md`, `docs/README.md`, `docs/quickstart/**`, and `docs/product/**`.
- requirement for this retirement slice: no current document may present `runtime-flow-preset`, `ApplyAllFeatures`, attachments, session-bridge write flows, or target catalog rollout as live functionality.

current_official_tool_loading_docs

- aligned rule-sync and rule-file claims to current tool loading semantics already encoded in the root rule files and repo profile: Codex loads `AGENTS.md`, Claude uses imported `CLAUDE.md`, Gemini uses imported `GEMINI.md`, and deterministic enforcement stays in repo gates/scripts rather than prose alone.
- this slice keeps the global-user sync model but removes project-level target repo distribution claims.

drift-integration decision

- integrated drift by treating deleted target-repo/session-bridge/attachment surfaces as retired current capability, not as missing files to restore.
- historical `docs/change-evidence/**` JSON/MD artifacts remain preserved for traceability, but current gates and docs are being updated so those historical records are no longer interpreted as live capability proof.

reference_required_review

- this retirement slice touches guarded reference-sensitive surfaces including `.governed-ai/repo-profile.json`, `docs/product/codex-cli-app-integration-guide.md`, `docs/product/codex-cli-app-integration-guide.zh-CN.md`, `docs/product/codex-direct-adapter.md`, `docs/product/codex-direct-adapter.zh-CN.md`, `docs/product/host-feedback-loop.md`, `docs/product/host-feedback-loop.zh-CN.md`, `scripts/evaluate-runtime-evolution.py`, and `scripts/verify-repo.ps1`.

changed_surface_paths

- `.governed-ai/repo-profile.json`
- `docs/product/codex-cli-app-integration-guide.md`
- `docs/product/codex-cli-app-integration-guide.zh-CN.md`
- `docs/product/codex-direct-adapter.md`
- `docs/product/codex-direct-adapter.zh-CN.md`
- `docs/product/host-feedback-loop.md`
- `docs/product/host-feedback-loop.zh-CN.md`
- `scripts/evaluate-runtime-evolution.py`
- `scripts/verify-repo.ps1`

official_sources_reviewed

- current tool-loading and rule-discovery semantics already captured in the active root rule files and repo-local loading policy were used as the official-source basis for removing stale target-repo distribution claims from README/operator surfaces and from `docs/product/host-feedback-loop.md` / `docs/product/host-feedback-loop.zh-CN.md`.
- no retired target-repo/session-bridge behavior was reintroduced to satisfy stale docs or stale schema expectations.

primary_references_reviewed

- reviewed the remaining repo-local contract and product references that still define live boundaries after retirement, especially `docs/product/codex-cli-app-integration-guide.md`, `docs/product/codex-cli-app-integration-guide.zh-CN.md`, `docs/product/codex-direct-adapter.md`, `docs/product/codex-direct-adapter.zh-CN.md`, `docs/product/host-feedback-loop.md`, `docs/product/host-feedback-loop.zh-CN.md`, and the repo-profile/rule-sync control surfaces they reference.
- treated deleted `rules/projects/**`, `docs/targets/**`, attachment/session-bridge specs, and retired examples as historical or removed surfaces rather than active primary references.

local_runtime_evidence_reviewed

- used fresh local gate outputs from `scripts/verify-repo.ps1 -Check Runtime` and repeated `scripts/verify-repo.ps1 -Check Contract` runs to drive the cleanup order.
- verified repo-local contract behavior through updated control-pack inheritance tests, pre-change review tests, current promotion artifact validation boundaries, and the host-only documentation surfaces in `docs/product/codex-cli-app-integration-guide.md`, `docs/product/codex-cli-app-integration-guide.zh-CN.md`, `docs/product/host-feedback-loop.md`, and `docs/product/host-feedback-loop.zh-CN.md`.

source_decision

- source decision: keep the repository as repo-local governance runtime plus global-user rule sync only; remove target-repo rollout, attachment bridge, and session-bridge write claims from current contracts, gates, and docs; preserve historical evidence as trace only.

reference_basis_review

- this retirement slice changes reference-governed surfaces in `.governed-ai/repo-profile.json`, `docs/architecture/capability-portfolio-classifier.json`, `docs/specs/README.md`, `docs/specs/control-pack-inheritance-matrix-spec.md`, `docs/specs/governance-hub-certification-spec.md`, `docs/specs/repo-admission-minimums-spec.md`, `docs/specs/repo-attachment-binding-spec.md`, `docs/specs/self-evolution-promotion-controller-spec.md`, `docs/specs/session-bridge-command-spec.md`, `docs/specs/target-repo-speed-kpi-spec.md`, `scripts/evaluate-runtime-evolution.py`, `scripts/governance/level-check.ps1`, and `scripts/verify-repo.ps1`.

reference_basis_surface_ids

- `community-execution-loop-and-context-shaping`
- `host-and-adapter-boundaries`
- `release-gate-and-ci-boundaries`
- `workflow-governance-and-spec-driven-delivery`

required_local_reference_ids_reviewed

- `1code`
- `aider`
- `anthropic-claude-code`
- `anthropic-claude-code-action`
- `cline`
- `github-copilot-cli`
- `github-spec-kit`
- `google-antigravity-cli`
- `goose`
- `hermes-agent`
- `langgraph`
- `microsoft-agent-framework`
- `mini-swe-agent`
- `obra-superpowers`
- `openai-agents-js`
- `openai-agents-python`
- `openai-codex`
- `openclaw-code-agent`
- `opencode`
- `openhands`
- `semantic-kernel`
- `swe-agent`

reference_adoption_decision

- adopted references that support repo-local governance, spec-driven delivery, host boundary verification, and release-style gate composition.
- rejected continued reliance on historical target-repo rollout, attachment light-pack, session-bridge write, or apply-all distribution surfaces even when those older files or historical evidence still exist in the repository.
