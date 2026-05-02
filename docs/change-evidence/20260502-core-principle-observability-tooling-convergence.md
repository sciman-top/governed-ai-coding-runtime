# Core Principle Observability And Tooling Convergence

Current landing: `D:\CODE\governed-ai-coding-runtime`.
Target home: core-principles policy, spec, operator docs, and managed project rule sources.
Verification path: core-principles verifier -> focused unit test -> rule-sync drift dry-run.

## Decision

Keep the existing five human-readable principles and fifteen machine-enforced principles. Do not add, delete, merge, or retire principle ids in this pass.

External official and community practice review showed the current structure is already aligned with agent best practices, but three existing principles benefit from sharper enforcement wording:

- `context_budget_and_instruction_minimalism`: tool outputs should be bounded, high-signal, trim-friendly, and reusable so tool use does not consume task context with low-value text.
- `least_privilege_tool_credential_boundary`: MCP/tool identity and allowlist-style controls belong in the same least-privilege boundary as permissions, sandbox, mounted paths, network, and provider secrets.
- `measured_effect_feedback_over_claims`: trace/replay/trajectory references should be preserved where available alongside target-run evidence, eval traces, effect feedback, verification commands, and rollback paths.

## Sources Reviewed

- OpenAI Agents SDK and agentic governance/evals guidance: modular agents, tool schemas, guardrails, tracing, eval loops, and continuous comparison.
- OpenAI Codex configuration and managed requirements guidance: configuration precedence, rules/hooks, security-sensitive settings, and MCP identity allowlist boundaries.
- Anthropic tool-use guidance: precise tool definitions and token-efficient tool use.
- Gemini CLI, OpenHands, SWE-agent, Cline, and Aider documentation: host-compatible status surfaces, state ownership, trajectory/replay evidence, plan/act separation, and concise edit/tool formats.

## Changes

- Updated `docs/architecture/core-principles-policy.json` summaries for the three existing principles above and added doc/evidence refs so `verify-core-principles.py` checks the stronger wording.
- Updated `docs/specs/core-principles-spec.md` invariants with bounded tool-output, MCP/tool identity, and trace/replay/trajectory fields.
- Updated root and bilingual README operator wording.
- Updated `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and their managed project-rule sources under `rules/projects/governed-ai-coding-runtime/`.

## Risk

Risk level: low. This is policy/spec/docs wording convergence only. It does not enable automatic policy mutation, skill enablement, target-repo sync, push, merge, reviewed-evidence deletion, or active-gate deletion.

## Pre-Change Review

pre_change_review: required because this change modifies core-principles policy/spec docs, deployed self-runtime `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`, and managed self-runtime rule sources.

control_repo_manifest_and_rule_sources: checked `rules/manifest.json` and the governed-ai-coding-runtime project rule sources under `rules/projects/governed-ai-coding-runtime/{codex,claude,gemini}` before editing.

user_level_deployed_rule_files: checked by `python scripts/sync-agent-rules.py --scope All --fail-on-change`; no global user-level Codex/Claude/Gemini rule drift was present and no user-level rule file was changed.

target_repo_deployed_rule_files: checked by `python scripts/sync-agent-rules.py --scope All --fail-on-change`; self-runtime deployed rule files are same-hash with managed sources, and no external target repository rule file was changed.

target_repo_gate_scripts_and_ci: not changed; the existing `scripts/verify-core-principles.py`, tests, and `scripts/verify-repo.ps1` wiring remain the verification path.

target_repo_repo_profile: not changed; no target repo profile or catalog entry was modified.

target_repo_readme_and_operator_docs: root README files and `docs/README.md` were updated only to expose the stronger wording for existing principles.

current_official_tool_loading_docs: checked current OpenAI Agents/Evals/Codex docs, Anthropic tool-use docs, Gemini CLI docs, OpenHands docs, SWE-agent trajectory docs, Cline Plan/Act docs, and Aider edit-format docs before changing the wording.

drift-integration decision: integrate the best-practice delta into existing `context_budget_and_instruction_minimalism`, `least_privilege_tool_credential_boundary`, and `measured_effect_feedback_over_claims`; do not add, delete, merge, or retire principle ids.

## Verification

- `python scripts\verify-core-principles.py`: pass. Key output: `status=pass`, no missing principles, doc refs, evidence refs, outer-AI controls, portfolio outcomes, non-enforced principles, or forbidden active patterns.
- `python -m unittest tests.runtime.test_core_principles`: pass, 5 tests.
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`: pass, dry-run, `changed_count=0`, `blocked_count=0`, 18 entries checked.

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`: pass (`OK python-bytecode`, `OK python-import`).
- First full `Runtime` replay: failed closed before this section was added because `pre_change_review` evidence tokens were missing from this evidence file. The evidence gap is now closed in this file and must be rerun.
- `python scripts\verify-pre-change-review.py`: pass; matched this evidence file.
- Second full `Runtime` replay after evidence repair: failed with 5 files outside this core-principle wording change scope: `test_attached_write_execution.py`, `test_repo_attachment.py`, `test_target_repo_governance_consistency.py`, `test_runtime_flow_preset.py`, and `test_target_repo_rollout_contract.py`. Key failures expect unrelated implementation that is not part of this pass, including `expected_sha256` support, `generated_managed_files`, and initialized `blocked_catalog_fields`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass. Key output includes `OK core-principle-change-proposal-artifacts`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`: pass with existing `WARN codex-capability-degraded`; all hard checks returned `OK`.

## Rollback

Revert this evidence file plus the matching edits to `docs/architecture/core-principles-policy.json`, `docs/specs/core-principles-spec.md`, README files, root rule files, and `rules/projects/governed-ai-coding-runtime/` managed rule sources.
