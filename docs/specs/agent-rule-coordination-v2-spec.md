# Agent Rule Coordination v2 Spec

## Status
Active design baseline for the 2026-07-10 Codex and Claude rule-family rollout.

## Purpose
Define a concise, auditable collaboration contract between user-level rules and repository-level rules for OpenAI Codex and Anthropic Claude Code.

The contract must produce a practical `global WHAT + project WHERE/HOW + host DELTA + deterministic enforcement` model without copying target-repository truth into the control repository.

## Scope

- Managed user-level hosts: `codex`, `claude`.
- Managed global copies: `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`.
- Explicit target repositories:
  - `ai-content-delivery-studio`
  - `classroom-answer-toolkit`
  - `ClassroomToolkit`
  - `github-toolkit`
  - `k12-question-graph`
  - `local-ai-dev-orchestrator`
  - `qq-codex-bot`
  - `skills-manager`
  - `vps-ssh-launcher`
- Non-target sibling directories remain affected by user-level rules but receive no project-rule edits from this rollout.
- Gemini is outside the managed family. Historical Gemini files are not deleted or synchronized by this contract.

## Version Model

- `rule_release` identifies the deployed global rule content release. This rollout uses `9.55`.
- `project_contract_version` identifies the machine-audited project integration interface. This rollout uses `2.0`.
- A target declares both its compatible project contract and the global release last reviewed.
- Contract incompatibility blocks. A later compatible global content release may be reported as review drift without treating wording-only changes as a broken project contract.

## Instruction Architecture

### User Level

- Codex and Claude global files carry the same normalized common sections.
- Only the platform section may differ.
- Platform instruction priority is distinct from factual drift resolution.
- Machine/provider/profile facts that can change independently belong in configuration or evidence, not stable global prose.

### Project Level

- Root `AGENTS.md` is the host-neutral repository contract and is directly read by Codex.
- Root `CLAUDE.md` starts with a raw, standalone `@AGENTS.md` import.
- The preferred Claude wrapper is exactly one import line. Extra content is allowed only for a verified repository-specific Claude difference and must not duplicate common project rules.
- Project `AGENTS.md` keeps the `1 / A / B / C / D` structure, but every section remains meaningful to both hosts. It must not contain a Codex-only platform section.
- Project rules contain repository truth, canonical gates, risk/invariant boundaries, evidence, and rollback. They do not repeat global language preferences, generic N/A definitions, generic clarification rules, or host loading tutorials.

## Progressive Disclosure

- Root files retain only facts required in nearly every session.
- Directory-specific rules live next to the relevant code when they are stable and high value.
- Low-frequency, multi-step procedures live in skills or runbooks with an explicit trigger and verification entrypoint.
- An import organizes Claude context but does not reduce context size.
- Critical safety rules must not rely solely on a path rule that may require a prior `Read` trigger.

## Enforcement Boundary

- Natural-language rules guide model decisions.
- Codex sandbox, approval policy, exec policy, hooks, and CI provide deterministic controls.
- Claude permissions, hooks, sandbox, managed/project settings, and CI provide deterministic controls.
- The verifier reports an enforcement gap when prose claims deterministic prevention but no corresponding machine control is referenced. It does not claim general semantic understanding.

## Coordination Manifest

`rules/target-project-rule-coordination.json` is an explicit allowlist, not a discovery-and-auto-enroll mechanism.

Each target records:

- repository identity and path relative to the workspace root
- GitHub repository identity and the project-owned rule-contract workflow path
- project contract version and reviewed global release
- common rule and Claude wrapper paths
- repository-specific required anchors
- evidence path
- size budgets
- local-only availability semantics

The top-level CI contract records the project workflow contract version and canonical workflow SHA-256. `schema_version=2.2` adds explicit GitHub visibility and aggregate execution mode without changing `project_contract_version=2.0` or `rule_release=9.55`. Public targets use aggregate checkout; private targets use repository-local enforcement because the control repository deliberately holds no cross-repository credential.

The manifest stores audit contracts, not target rule bodies.

## Deterministic Audit

The standalone target verifier rejects missing workspace/date/CI metadata. The control-repository contract gate validates the coordination manifest against its JSON Schema and audits every target available on the current machine; release verification adds `--require-all` so any missing allowlisted target blocks rollout. `--workspace-root` provides an explicit CI checkout override without changing the local manifest path.

Hard failures include:

- missing target, project rule, or Claude wrapper when `--require-all` is used
- missing/drifted target rule-contract workflow or an invalid GitHub repository locator
- missing/invalid coordination metadata or a schema-invalid coordination manifest
- incompatible project contract
- missing repository-specific anchors
- a project rule containing Codex-only platform guidance
- a wrapper whose first physical line is not `@AGENTS.md`
- BOM-prefixed wrapper or unapproved additional imports
- duplicated common headings/body in the wrapper
- Gemini managed-family residue
- project rule exceeding its configured byte/line budget
- missing gate order, evidence path, or rollback contract
- project rule that does not reference its deterministic rule-contract workflow

## Cross-Repository CI Parity

- Each target owns `.github/workflows/agent-rule-contract.yml`; it runs only for rule/workflow changes, uses read-only contents permission, requires no secret, and validates the project rule plus exact Claude wrapper.
- All nine project workflows must match `rules/templates/github/agent-rule-contract.yml` byte-for-byte. The manifest SHA-256 and target verifier make drift blocking.
- `.github/workflows/agent-rule-coordination.yml` builds its matrix from the explicit manifest, checks out each public target into an isolated workspace, and runs a strict one-target audit with `--require-all`.
- The aggregate workflow is scheduled and manually runnable, and also reacts to control-contract changes. Target workflows cover target pull requests independently.
- Rule-contract CI never substitutes for a target's build, test, contract/invariant, or hotspot gates.

Observations include:

- reviewed global release lag within the same project contract
- effective Claude context growth
- nested third-party instruction files
- prose-only enforcement claims
- dirty target worktrees

## Gate Integrity

- Gate order remains `build -> test -> contract/invariant -> hotspot`.
- Commands must reflect repository-owned runnable entrypoints.
- Setup/install commands are not routine gates.
- Repeating the same command under two gate labels must be declared as a temporary gap, not represented as independent evidence.
- `gate_na` is valid only with `reason`, `alternative_verification`, `evidence_link`, and a machine-readable `expires_at` value (`task_end`, `next_executable_change`, or ISO-8601 timestamp).
- The control-repository contract gate includes global-family verification, coordination-schema validation, and audit of locally available targets; the release command remains the stricter all-target check.

## Rollout And Rollback

1. Capture source, deployed-copy, target-rule, and dirty-worktree baselines.
2. Update tests and deterministic verifiers.
3. Update global sources and target rules in place.
4. Run static audits before deployment.
5. Back up and synchronize user-level global copies.
6. Run fresh Codex/Claude loading probes.
7. Run control-repository gates and target-appropriate rule-change verification.

Rollback is scoped:

- global deployment uses the sync backup plus the reverted source release
- control-repository code uses its Git diff/history
- each target reverts only its own rule/evidence slice
- unrelated dirty-worktree changes are never restored or rewritten

## Non-Goals

- synchronizing target project rules as manifest-owned copies
- modifying provider, auth, MCP, sandbox, or permission settings
- deleting historical Gemini files
- auto-enrolling new sibling directories
- rewriting third-party instruction files under generated/vendor/import directories
- claiming product runtime gates passed when only rule-structure verification ran
