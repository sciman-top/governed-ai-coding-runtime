# 2026-05-01 Core Principle Current Review README zh-CN Sync

## Goal
Re-check the active core-principles kernel against current official agent-tool documentation and local policy evidence, then fix any documentation drift found during the review.

## Finding
The active machine policy already includes the best-practice additions from the earlier external review:

- `context_budget_and_instruction_minimalism`
- `least_privilege_tool_credential_boundary`
- `measured_effect_feedback_over_claims`

No active principle was added or removed in this pass.

The only drift found was `README.zh-CN.md`: it still described the older single human-readable core principle and an outdated Codex temporary default model. The root `README.md`, `README.en.md`, `AGENTS.md`, and `docs/architecture/core-principles-policy.json` already reflected the current five human-readable principles and 14 enforced machine principles.

## External Reference Basis
The review used official/current agent-tool guidance rather than community instructions as authority:

- OpenAI Codex guidance: use persistent `AGENTS.md`, structured context, scoped tasks, and environment iteration.
- Claude Code guidance: keep `CLAUDE.md` concise, verify work with tests/outputs, manage context aggressively, use permissions/hooks for deterministic controls, and use skills/subagents for scoped context.
- Gemini CLI guidance: hierarchical `GEMINI.md` context, `/memory show|refresh`, imports, and concise saved memory facts.

These sources support the current policy shape: concise root instructions, least-privilege tool/credential boundaries, deterministic gates, and measured effect evidence.

## Change
Updated `README.zh-CN.md` so the Chinese operator guide now matches the current five human-readable core principles and the current Codex temporary implementation wording from the root README.

## Verification Commands
```powershell
python scripts/verify-core-principles.py
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

## Rollback
Revert this evidence file and the matching `README.zh-CN.md` edit.
