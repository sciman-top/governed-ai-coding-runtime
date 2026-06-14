# Continuous Execution Output Envelope

## Purpose
Define the bounded response shape for continuous autonomous execution so teaching remains short, actionable, and compatible with existing clarification and budget contracts.

## Required Envelope
- one-line task anchor
- `1..3` clarification questions at most
- `3..5` observation checklist items when observation gaps exist
- at most one term explanation per response

## Baseline Modes

### `teaching`
- Use when the task is still aligned but one compact explanation will likely prevent repeat mistakes.
- Keep the response anchored to the current task and evidence.
- Allowed structure:
  - one-line task anchor
  - one short explanation or one term explanation
  - optional `3..5` checklist items

### `guided`
- Use when the next best move is a short sequence of checks or actions rather than a concept-heavy explanation.
- Prefer checklist-first wording over long prose.
- Allowed structure:
  - one-line task anchor
  - `3..5` observation or action checklist items
  - optional one clarifying question

### `terse`
- Use when the task is already aligned, the next step is obvious, or budget pressure requires compression.
- Allowed structure:
  - one-line task anchor
  - one short status or next action line

## Budget-Driven Downgrade Rules

### `near_limit`
- downgrade order: `teaching -> guided -> terse`
- no more than one clarifying question
- prefer checklist-first over explanation-first
- term explanation remains optional but still limited to one item

### `exhausted`
- stop normal teaching expansion
- switch to one of:
  - `handoff_only`
  - `ref_only`
  - `stop_on_budget`
- preserve evidence refs, rollback refs, and the current task anchor

## Invariants
- `max_questions` may not exceed the clarification cap in `docs/specs/clarification-protocol-spec.md`
- explanation scope must remain bounded by `docs/specs/teaching-budget-spec.md`
- the envelope may compress wording, but it may not weaken approvals, canonical gate order, rollback requirements, or explicit degrade semantics
- checklist items and clarifying questions must remain task-scoped and evidence-backed rather than personality-driven filler

## Compatibility Notes
- This envelope complements `docs/specs/response-policy-spec.md`; it does not replace the machine-readable policy contract.
- This envelope is an operator-facing execution rule for response shape, not a transcript style guide for all contexts.
