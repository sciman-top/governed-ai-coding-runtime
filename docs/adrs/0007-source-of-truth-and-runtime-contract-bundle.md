# ADR-0007: Keep Source-Of-Truth Authoring Separate From Runtime Contract Bundles

## Status
Accepted

## Date
2026-04-18

## Context
The repository is still `docs-first / contracts-first`, but the active final-state work now needs a repo-local attachment surface for governed target repositories.

That creates a real boundary risk:
- `docs/`, `schemas/`, and `packages/contracts/` already act as the authoring source of truth
- `GAP-035` needs a repo-native light pack or `.governed-ai/`-style attachment surface
- if the runtime bundle becomes a second handwritten source of truth too early, the project will carry duplicate contract copies and drift

Recent strategy work sharpened the desired final shape:
- the product is a governance/runtime layer, not a host replacement
- repo-native bundles are an attachment surface
- local and CI should consume the same declared contract inputs
- `PolicyDecision` should stay stable before deeper adapter work expands

This ADR must stop future work from treating the repo-local bundle shape as the new authoring center before duplication is proven and migration is justified.

Related decisions:
- [ADR-0005](./0005-governance-kernel-and-control-packs-before-platform-breadth.md)
- [ADR-0006](./0006-final-state-best-practice-agent-compatibility.md)

## Decision
1. `docs/`, `schemas/`, and `packages/contracts/` remain the repository source of truth.
2. A future `.governed-ai/` directory or equivalent repo-local light pack is a runtime-consumable output, attachment surface, or validated projection of the source-of-truth assets.
3. The project must not hand-maintain two competing contract copies.
4. The migration posture is:
   - author in source-of-truth assets
   - generate or validate the repo-local bundle shape
   - attach that bundle to target repositories
   - only consider deeper consolidation if long-term duplicated authoring becomes real and materially costly

## Alternatives Considered

### Alternative A: Make `.governed-ai/` the new handwritten source of truth now
- Pros:
  - would look closer to the eventual target-repo attachment shape
  - could simplify external onboarding demos in the short term
- Cons:
  - duplicates authoring with `docs/`, `schemas/`, and contract code
  - raises drift risk immediately
  - pushes wrapper or pack conventions ahead of actual validated runtime needs
- Rejected:
  - the project does not yet have evidence that authoring duplication is the dominant problem

### Alternative B: Keep the current source-of-truth assets and never materialize a repo-local bundle
- Pros:
  - avoids duplication
  - minimizes migration work
- Cons:
  - blocks the attach-first target-repo boundary
  - leaves `GAP-035` without a stable attachment surface
- Rejected:
  - the final product needs a bounded repo-local runtime-consumable pack

### Alternative C: Collapse all authoring and runtime concerns into one new monolithic bundle format
- Pros:
  - promises a single visible contract surface
- Cons:
  - would force a premature migration across docs, schemas, Python contracts, and verification
  - couples authoring, packaging, and runtime-consumption concerns too early
- Rejected:
  - the repository still benefits from explicit docs/spec/schema/contract separation

## Consequences
- `GAP-035` can proceed with a clear light-pack boundary.
- `GAP-042` stays an architecture and mapping exercise, not a repository-wide authoring migration.
- Verification should increasingly validate runtime-consumable bundle shapes against existing source-of-truth assets.
- Future consolidation remains possible, but only after the project observes real duplicated-authoring cost rather than assuming it.
