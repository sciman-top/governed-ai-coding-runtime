# ADR-0004: Rename Project To Governed AI Coding Runtime

## Status
Accepted

## Date
2026-04-17

## Context
The previous project name, `governed-agent-platform`, was serviceable but too broad for the actual product thesis.

It suggested a general-purpose agent platform, which risks implying:
- generic enterprise automation
- default multi-agent orchestration
- broad agent hosting or agent platform ambitions

The current product definition is narrower and more precise:
- governed runtime
- AI coding focused
- repository-aware execution
- approval, verification, evidence, and replay centered

## Decision
Rename the project and active repository assets to `governed-ai-coding-runtime`.

This rename applies to:
- repository root directory
- active documentation
- active planning assets
- schema identifiers
- active automation scripts

Historical evidence and prior dated records remain unchanged unless a later audit explicitly requires annotation.

## Alternatives Considered

### Keep `governed-agent-platform`
- Pros: shorter and broader
- Cons: too vague; implies a wider product boundary than intended
- Rejected: not precise enough for the current thesis

### Rename to `governed-coding-runtime`
- Pros: shorter and still focused
- Cons: loses the explicit AI boundary and can read like a general developer tooling runtime
- Rejected: less explicit than desired

## Consequences
- The project identity now matches the PRD and architecture focus more closely.
- Active docs and scripts must be updated together so references do not drift.
- Historical evidence remains truthful rather than being rewritten to imply the old name never existed.
- External references to the old name may need a compatibility note during transition.
