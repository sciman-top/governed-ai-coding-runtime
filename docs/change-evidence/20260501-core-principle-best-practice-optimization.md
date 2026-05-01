# 2026-05-01 Core Principle Best-Practice Optimization Evidence

## Goal
Promote the external best-practice review findings into the active core-principles kernel without weakening the existing proposal-first and gate-controlled evolution boundaries.

## Root Cause And Changes
External official and community practice checks converged on three gaps that were already partially implemented in this repository but not elevated as explicit core principles:

- context budget and instruction minimalism
- least-privilege tool and credential boundaries
- measured effect feedback over documentation-only claims

Changes made:

- Added `context_budget_and_instruction_minimalism`, `least_privilege_tool_credential_boundary`, and `measured_effect_feedback_over_claims` to `docs/architecture/core-principles-policy.json`.
- Tightened `efficiency_first` so efficiency includes bounded context, measured throughput, and safe automation.
- Tightened `evidence_and_rollback_required` so evidence includes freshness, effect metrics, verification commands, N/A expiry where applicable, and rollback records.
- Updated `docs/specs/core-principles-spec.md`, `scripts/verify-core-principles.py`, `tests/runtime/test_core_principles.py`, `schemas/jsonschema/core-principles.schema.json`, `docs/README.md`, and managed self-runtime agent-rule sources.
- Reviewed and updated planning/backlog crosswalks so the new principles map to completed `GAP-130..143` work instead of spawning duplicate roadmap items.

## Pre-Change Review
pre_change_review: required because this change modifies core-principles policy/spec/verifier/tests, managed self-runtime rule sources, and deployed self-runtime `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` files.

control_repo_manifest_and_rule_sources: checked `rules/manifest.json` before editing; the governed-ai-coding-runtime project rule sources are `rules/projects/governed-ai-coding-runtime/codex/AGENTS.md`, `rules/projects/governed-ai-coding-runtime/claude/CLAUDE.md`, and `rules/projects/governed-ai-coding-runtime/gemini/GEMINI.md`.

user_level_deployed_rule_files: not changed by this task; the update is project-scoped to `self-runtime`, not global user-level Codex/Claude/Gemini rules.

target_repo_deployed_rule_files: only the `self-runtime` target was synchronized; no external target repository was changed.

target_repo_gate_scripts_and_ci: not changed; the existing `scripts/verify-core-principles.py` and `scripts/verify-repo.ps1` wiring were extended through required-principle checks only.

target_repo_repo_profile: not changed; no target repo profile or catalog entry was modified.

target_repo_readme_and_operator_docs: root `README.md` and `docs/README.md` were updated to expose the added core-principle boundaries.

current_official_tool_loading_docs: checked current official Codex `AGENTS.md`, Claude settings/memory/hooks, GitHub/VS Code Copilot instructions, OpenHands sandbox, and Letta memory guidance before changing the core principle set.

drift-integration decision: integrate by promoting already-supported best-practice boundaries into core-principles policy/spec/verifier/tests and synchronizing only the self-runtime managed rule copies.

roadmap_backlog_review: existing implementation plans and task lists already cover the new principles through `GAP-134`, `GAP-137`, `GAP-138`, `GAP-139`, `GAP-142`, and `GAP-143`; only the plan/backlog indexes and crosswalk text needed updates.

## Verification
Completed verification:

```powershell
python scripts/sync-agent-rules.py --scope Targets --target self-runtime --apply
```

Result: blocked as expected on same-version drift for `CLAUDE.md` and `GEMINI.md`.

```powershell
python scripts/sync-agent-rules.py --scope Targets --target self-runtime --apply --force
```

Result: pass. Key output: `status=applied`, `changed_count=2`, updated self-runtime `CLAUDE.md` and `GEMINI.md` with backups under `docs/change-evidence/rule-sync-backups/20260501-192342/`.

```powershell
python scripts/sync-agent-rules.py --scope Targets --target self-runtime --fail-on-change
```

Result: pass. Key output: `status=pass`, `changed_count=0`, `blocked_count=0`.

```powershell
python scripts/verify-core-principles.py
```

Result: pass. Key output: `status=pass`; `principle_ids` includes `context_budget_and_instruction_minimalism`, `least_privilege_tool_credential_boundary`, and `measured_effect_feedback_over_claims`; no missing doc refs, evidence refs, or forbidden active patterns.

```powershell
python -m unittest tests.runtime.test_core_principles
```

Result: pass. Key output: `Ran 5 tests`, `OK`.

```powershell
python scripts/verify-capability-portfolio.py
```

Result: pass. Key output: `status=pass`, `entry_count=26`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

Result: pass. Key output includes `OK core-principles`, `OK capability-portfolio`, `OK core-principle-change-materialization`, and `OK post-closeout-queue-sync`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll
```

Result after roadmap/backlog crosswalk update: pass. Key output: `rendered_tasks=121`, `rendered_epics=14`, `rendered_initiative=true`, `active_task_count=0`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

Result after roadmap/backlog crosswalk update: pass. Key output includes `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK core-principles`, `OK core-principle-change-materialization`, and `OK post-closeout-queue-sync`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

Result: pass. Key output: `OK python-bytecode`, `OK python-import`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

First result: fail-closed because this evidence file did not yet include the required `pre_change_review` drift-review fields for sensitive rule-source changes.

Final result after evidence completion: pass. Key output: `Completed 94 test files`, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK schema-json-parse`, `OK schema-example-validation`, `OK core-principle-change-proposal-artifacts`, `OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK repo-map-context-artifact`, `OK policy-tool-credential-audit`, `OK governance-hub-certification`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

Result: pass with existing host capability warning. Key output includes `OK runtime-status-surface`, `OK adapter-posture-visible`, and `WARN codex-capability-degraded`.

## Rollback
Revert this evidence file plus the linked core-principles policy, spec, schema, verifier, tests, docs, and managed self-runtime rule-source updates.
