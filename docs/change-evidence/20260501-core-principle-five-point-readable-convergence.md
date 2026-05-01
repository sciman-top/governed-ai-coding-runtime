# 2026-05-01 Core Principle Five-Point Readable Convergence Evidence

## Goal
Converge human-readable core-principle wording into five stable statements while keeping the existing machine-verifiable 14-principle policy as the enforcement source of truth.

## Root Cause And Changes
The previous human-facing wording split the same concept across README text, operator guidance, and agent-rule summaries. The active machine policy was already sufficiently granular, so the correct change is readability convergence, not another top-level principle expansion.

Changes made:

- Rewrote the human-readable principle summary in `README.md`, `README.en.md`, and `docs/README.md` into five statements.
- Rewrote the self-runtime project rule sources under `rules/projects/governed-ai-coding-runtime/*` with the same five-point summary.
- Synchronized the self-runtime deployed `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` from manifest-managed sources.
- Left `docs/architecture/core-principles-policy.json` and `docs/specs/core-principles-spec.md` unchanged so the 14 enforced machine principles remain the source of truth.

## Pre-Change Review
pre_change_review: required because this change modifies managed self-runtime rule sources and deployed project rule files.

control_repo_manifest_and_rule_sources: checked `rules/manifest.json` indirectly through `python scripts/sync-agent-rules.py --scope Targets --target self-runtime --fail-on-change`; the self-runtime sources were initially same-hash with deployed targets before editing.

user_level_deployed_rule_files: not changed by this task.

target_repo_deployed_rule_files: only the self-runtime project rule files were updated through the manifest-managed sync path.

target_repo_gate_scripts_and_ci: not changed.

target_repo_repo_profile: not changed.

target_repo_readme_and_operator_docs: `README.md`, `README.en.md`, and `docs/README.md` were updated to expose the five-point readable principle summary.

current_official_tool_loading_docs: reused the immediately preceding official/community best-practice review conclusion; this task only applied the accepted wording convergence and did not introduce a new loading-model claim.

drift-integration decision: integrate by editing manifest-managed source files first, then force-syncing only self-runtime targets after the sync script blocked same-version drift as expected.

## Verification
Completed verification:

```powershell
git status --short
```

Result before edits: clean working tree.

```powershell
python scripts/sync-agent-rules.py --scope Targets --target self-runtime --fail-on-change
```

Result before edits: pass. Key output: `status=pass`, `changed_count=0`, `blocked_count=0`.

```powershell
python scripts/sync-agent-rules.py --scope Targets --target self-runtime --apply
```

Result after source edits: blocked as expected on same-version drift for `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`.

```powershell
python scripts/sync-agent-rules.py --scope Targets --target self-runtime --apply --force
```

Result: pass. Key output: `status=applied`, `changed_count=3`, backups under `docs/change-evidence/rule-sync-backups/20260501-212006/`.

```powershell
python scripts/sync-agent-rules.py --scope Targets --target self-runtime --fail-on-change
```

Result after force sync: pass. Key output: `status=pass`, `changed_count=0`, `blocked_count=0`; all three self-runtime targets are same-hash with their manifest sources.

```powershell
python scripts/verify-core-principles.py
```

Result: pass. Key output: `status=pass`; no missing principles, doc refs, evidence refs, portfolio outcomes, or outer-AI controls.

```powershell
python -m unittest tests.runtime.test_core_principles
```

Result: pass. Key output: `Ran 5 tests`, `OK`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

Result: pass. Key output: `OK python-bytecode`, `OK python-import`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

Result: pass. Key output: `Completed 94 test files`, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK schema-json-parse`, `OK schema-example-validation`, `OK core-principle-change-proposal-artifacts`, `OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

Result: pass with existing host capability warning. Key output includes `OK runtime-status-surface`, `OK adapter-posture-visible`, and `WARN codex-capability-degraded`.

## Rollback
Revert this evidence file plus the matching `README.md`, `README.en.md`, `docs/README.md`, managed self-runtime rule-source edits, and synchronized `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` target copies. If needed, restore the three deployed rule files from `docs/change-evidence/rule-sync-backups/20260501-212006/`.
