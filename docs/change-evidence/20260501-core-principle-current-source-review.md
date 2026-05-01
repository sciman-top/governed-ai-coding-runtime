# 2026-05-01 Core Principle Current-Source Review

## Goal
Execute the follow-up decision from the 2026-05-01 core-principle review: do not add or delete core principles unless current official sources, target-run evidence, or verifier output proves a fresh gap.

## Decision
AI recommendation: keep the existing five human-readable principles and fourteen enforced machine principles.

This review updates the current-source compatibility guard so future source drift is checked by the existing Docs gate instead of expanding the root principle text.

## Source Review
Reviewed sources:

- OpenAI Codex AGENTS scope and precedence behavior.
- GitHub Copilot repository, path-specific, and agent instruction behavior.
- VS Code Copilot custom-instruction guidance for short self-contained rules with rationale.
- Claude Code memory, settings, hooks, and best-practice guidance for concise project instructions plus deterministic permissions, sandboxing, and hooks.
- OpenHands sandbox provider guidance and process-sandbox risk language.

Observed convergence:

- Instruction files should stay short, scoped, and self-contained.
- Natural-language instructions are advisory context; deterministic controls must carry permissions, hooks, sandboxing, verification, and evidence.
- Host-provided rules, guardrails, sandboxes, and instructions can strengthen runtime behavior but must not replace runtime-owned approval, containment, verification, rollback, evidence, or claim-drift checks.
- Completion claims should be tied to fresh executable evidence, not documentation presence alone.

## Changes
- Refreshed `docs/architecture/current-source-compatibility-policy.json` from the 2026-04-27 source set to the 2026-05-01 source set for core-principle review.
- Added official Copilot, VS Code Copilot, Claude Code best-practice, OpenHands sandbox, and OpenAI Codex AGENTS scope sources to the current-source policy.
- Added regression assertions so these source IDs remain covered by `tests/runtime/test_current_source_compatibility.py`.
- Regenerated `docs/change-evidence/governance-hub-certification-report.json` through the Contract gate so the certification snapshot carries the refreshed current-source review window and source IDs.

## Non-Changes
- No active core principle was added, removed, or renamed.
- No global or project agent rule file was synchronized.
- No target repository was changed.
- No automatic policy mutation, skill enablement, target-repo sync, push, merge, evidence deletion, or gate deletion was authorized.

## Verification
Completed verification:

```powershell
python scripts/verify-current-source-compatibility.py --as-of 2026-05-01
```

Result: pass. Key output: `status=pass`, `reviewed_on=2026-05-01`, `review_expires_at=2026-07-30`, source IDs include `github-copilot-repository-instructions`, `vscode-copilot-custom-instructions`, `anthropic-claude-code-best-practices`, and `openhands-sandbox-overview`.

```powershell
python scripts/verify-core-principles.py
```

Result: pass. Key output: `status=pass`; no missing principles, non-enforced principles, doc refs, evidence refs, outer-AI controls, portfolio outcomes, or forbidden active patterns.

```powershell
python -m unittest tests.runtime.test_current_source_compatibility tests.runtime.test_core_principles
```

Result: pass. Key output: `Ran 9 tests`, `OK`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

Result: pass. Key output includes `OK current-source-compatibility`, `OK core-principles`, `OK capability-portfolio`, `OK claim-drift-sentinel`, `OK claim-evidence-freshness`, and `OK post-closeout-queue-sync`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

Result: pass. Key output includes `OK python-bytecode` and `OK python-import`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

Result: pass. Key output: `Completed 94 test files`, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, and `OK runtime-service-wrapper-drift-guard`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK schema-json-parse`, `OK core-principle-change-proposal-artifacts`, `OK dependency-baseline`, `OK governance-hub-certification`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

Result: pass with existing host capability warning. Key output includes `OK runtime-status-surface`, `OK adapter-posture-visible`, and `WARN codex-capability-degraded`.

## Rollback
Revert this evidence file plus the matching `docs/architecture/current-source-compatibility-policy.json` and `tests/runtime/test_current_source_compatibility.py` changes. If only one reviewed external source later drifts, update that source entry and keep the existing 5/14 core-principle structure unless verifier evidence proves a new principle is required.
