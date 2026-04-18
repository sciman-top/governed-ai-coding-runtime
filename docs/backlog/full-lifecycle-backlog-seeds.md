# Full Lifecycle Backlog Seeds

## Purpose
Seed the function-first full lifecycle of the project so it can evolve from a completed MVP governance kernel into a complete single-machine self-hosted governed AI coding runtime.

## Current Baseline
- `Phase 0` through `Phase 4` are complete through `GAP-017`.
- The repository already contains runtime contracts, verifier entrypoints, sample repo profiles, a runtime-consumable control pack, and MVP-era governance primitives.
- The repository still lacks the complete runtime substrate, public usable release path, and maintenance boundary required for final product completeness.
- The lifecycle definition and capability freeze work under `Vision / GAP-018` and `GAP-019` is complete.
- The Foundation stage under `GAP-020` through `GAP-023` is complete and now serves as implementation history.
- The active next-step queue begins at `Full Runtime / GAP-024`.

## Vision
1. Freeze the final product shape as a single-machine self-hosted complete governed runtime.
2. Freeze the final capability boundary and non-goal boundary.
3. Keep `Vision` as planning history rather than the active next-step queue.

## MVP
1. Keep the current MVP as historical baseline; do not re-open or re-scope it.

## Foundation
1. Keep Foundation as completed implementation history for `GAP-020` through `GAP-023`.
2. Use `docs/plans/foundation-runtime-substrate-implementation-plan.md` to understand what Foundation already delivered.

## Full Runtime
1. Add execution workers and managed runtime workspaces.
2. Add artifact storage, evidence persistence, and replay plumbing.
3. Add an operational quick/full gate runner.
4. Add a minimal operator surface with CLI-first delivery and stable read models.
5. Add runtime health, status, and query surfaces.
6. Treat `docs/plans/full-runtime-implementation-plan.md` as the current execution checklist for this stage.

## Public Usable Release
1. Add a single-machine deployment path and quickstart.
2. Add sample repo profiles and a demo governed task flow.
3. Add release packaging and public usable release criteria.
4. Define adapter baseline and degrade behavior.

## Maintenance
1. Add compatibility and upgrade policy.
2. Add maintenance, deprecation, and retirement rules.

## Explicit Non-Goals
- commercial packaging
- enterprise org model
- multi-tenant platform design
- marketplace or promotion lifecycle
- default multi-agent orchestration
- memory-first product identity
- deployment automation as the default completion path
