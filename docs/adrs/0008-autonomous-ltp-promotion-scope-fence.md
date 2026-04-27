# ADR-0008: Autonomous LTP Promotion Scope Fence

## Status
Accepted

## Date
2026-04-27

## Context
After `GAP-111`, the repository can truthfully claim complete hybrid final-state closure for the current branch baseline. After `GAP-112`, external host, protocol, sandbox, guardrail, and provenance assumptions are machine-checked before they can strengthen those claims.

The remaining question is how to answer repeated pressure to "directly push to the north-star heavy stack" without violating the repository's evidence-first architecture. The final-state candidate stack includes Temporal-class orchestration, OPA/Rego, event streams, object stores, semantic indexes, A2A gateway, full observability, and external signing. Those are valid candidates, but adopting them all at once would change operations, testing, failure modes, and user cost before the current runtime has evidence that it needs them.

## Decision
Do not directly force the full heavy stack as the default route.

Adopt this promotion model instead:
- `evidence-triggered`: the runtime may autonomously select exactly one `LTP-01..06` package when the promotion policy has fresh trigger evidence, a scope fence, a full gate reference, rollback, and one vertical slice.
- `owner-directed`: the user may explicitly direct a heavy-stack package, but the implementation must be labeled as owner-directed, not evidence-triggered, and still needs a scope fence, verification floor, rollback, and claim discipline.
- `defer/watch`: when evidence is absent or only watch-level, the correct action is to preserve the certified hybrid final state and keep running gates.

## Why
- The project is a governed AI coding runtime, not an infrastructure demo.
- The certified final state is a capability closure, not a checklist requiring every attractive technology.
- Heavy packages are useful only when they remove real complexity, reduce real risk, or satisfy real consumption pressure.
- Autonomous promotion must be safe enough to run without asking the user every time, so it must be deterministic, one-package-at-a-time, and fail-closed.

## Alternatives Considered

### Force the whole north-star stack now
- Pros: superficially looks closer to a large platform.
- Cons: introduces infrastructure without evidence, makes verification harder, raises maintenance cost, and weakens the current local-first runtime.
- Rejected because it optimizes for stack appearance instead of runtime proof.

### Never adopt heavy packages
- Pros: keeps the runtime small.
- Cons: would block valid growth when orchestration, policy, data, operations, protocol, or supply-chain pressure becomes real.
- Rejected because the final-state architecture must remain capable of growing.

### Ask the user every time
- Pros: simple governance.
- Cons: does not satisfy autonomous continuous execution.
- Rejected as the default because the repo can encode safe conditions mechanically.

## Consequences
- `scripts/evaluate-ltp-promotion.py` becomes the mechanical answer to whether an LTP package should advance now.
- `verify-repo.ps1 -Check Docs` fails if promotion policy, ADR, evidence, or claim boundaries drift.
- The current decision is `defer_all`, not because the north-star stack is invalid, but because no package currently satisfies autonomous trigger conditions.
- Future promotion is possible without new debate when exactly one package becomes `auto_selected` with fresh evidence, scope fence, full gate, and rollback.
