# Full Lifecycle Backlog Seeds

## Purpose
Seed the function-first full lifecycle of the project so it can evolve from a completed MVP governance kernel into a generic, interactive, attach-first governed AI coding runtime.

## Current Baseline
- `Phase 0` through `Phase 4` are complete through `GAP-017`.
- The repository already contains runtime contracts, verifier entrypoints, sample repo profiles, a runtime-consumable control pack, and MVP-era governance primitives.
- The repository now contains the local single-machine runtime baseline through `Maintenance Baseline / GAP-034`.
- `Interactive Session Productization / GAP-035` through `GAP-039` are complete on the current branch baseline.
- `Strategy Alignment Gates / GAP-040` through `GAP-044` are complete on the current branch baseline and remain encoded as satisfied dependencies around the completed productization queue.
- `Direct-To-Hybrid-Final-State Mainline / GAP-045` through `GAP-060` are complete on the current branch baseline.
- `Governance Optimization Lane / GAP-061` through `GAP-068` are complete on the current branch baseline.
- `Post-Closeout Optimization Queue / GAP-069` through `GAP-074` is complete on the current branch baseline (verified on 2026-04-20).
- `Near-Term Gap Horizon Queue / GAP-080` through `GAP-089` are complete on the current branch baseline (`GAP-080` through `GAP-084` verified on 2026-04-21; `GAP-085` through `GAP-089` verified on 2026-04-22).
- `Long-Term Gap Trigger Audit Queue / GAP-090` through `GAP-092` is complete; all `LTP-01..05` packages remain deferred pending future trigger evidence.
- `GAP-018` through `GAP-068` remain completion history and dependency context for the active queue.

## Vision
1. Freeze the initial product shape and capability boundary.
2. Keep `Vision` as planning history rather than the active next-step queue.

## MVP
1. Keep the current MVP as historical baseline; do not re-open or re-scope it.

## Foundation
1. Preserve clarification, rollout, compatibility, and evidence maturity as landed baseline.
2. Preserve live `build` and `hotspot` gates.
3. Preserve durable task persistence and workflow skeletons.
4. Preserve control lifecycle metadata and evidence completeness checks.

## Full Runtime
1. Preserve execution workers and managed runtime workspaces.
2. Preserve artifact storage, evidence persistence, and replay plumbing.
3. Preserve the operational quick/full gate runner.
4. Preserve the local operator surface.
5. Preserve runtime health, status, and query surfaces.

## Public Usable Release
1. Preserve the single-machine deployment path and quickstart.
2. Preserve sample repo profiles and the demo governed task flow.
3. Preserve release packaging and public usable release criteria.
4. Preserve the adapter baseline and degrade behavior.

## Maintenance Baseline
1. Preserve compatibility and upgrade policy.
2. Preserve maintenance, deprecation, and retirement rules.
3. Treat this stage as the local baseline hardening layer, not the final lifecycle endpoint.

## Interactive Session Productization
1. Preserve the generic target-repo attachment pack and onboarding flow.
2. Preserve the attach-first session bridge and governed interaction surface.
3. Preserve the direct Codex adapter and evidence mapping path.
4. Preserve capability-tiered adapters for non-Codex AI tools.
5. Preserve multi-repo trial feedback capture and the reusable onboarding kit.

## Strategy Alignment Gates
1. `Strategy Alignment Gate A` is complete on the current branch baseline:
   - runtime governance borrowing matrix
   - source-of-truth versus runtime contract bundle ADR
   - repo-native contract bundle architecture
2. `Strategy Alignment Gate B` is complete on the current branch baseline:
   - PolicyDecision contract with `allow`, `escalate`, and `deny`
3. Verification and reconciliation are complete on the current branch baseline before broad `GAP-038` and `GAP-039` expansion:
   - local/CI same-contract verification
   - backlog and issue-seed reconciliation
4. These gates remain encoded in `issue-seeds.yaml` so rendered GitHub task dependencies match the roadmap:
   - `GAP-035` waits for `GAP-042`
   - `GAP-036` and `GAP-037` wait for `GAP-043`
   - `GAP-038` and `GAP-039` wait for `GAP-044`

## Next Queue Policy
1. Do not reopen `GAP-018` through `GAP-044` unless a verified regression requires it.
2. Keep `GAP-045` through `GAP-068` as completed closure and optimization history unless verified regressions require reopening.
3. Keep `GAP-069` through `GAP-074` as completed post-closeout optimization history unless verified regressions require reopening.
4. Treat `GAP-080` through `GAP-084` as completed near-term queue history unless verified regressions require reopening older ranges.
5. Treat `GAP-085` through `GAP-089` as completed near-term queue history unless verified regressions require reopening.
6. Use `GAP-090` through `GAP-092` for trigger-audit planning and evidence before any LTP implementation starts.
7. Introduce any LTP implementation queue only as new IDs beyond `GAP-092`.
8. Add new IDs only after acceptance criteria and dependency wiring are explicit in both markdown and seed YAML.

## Explicit Non-Goals
- commercial packaging
- enterprise org model
- multi-tenant platform design
- marketplace or promotion lifecycle
- default multi-agent orchestration
- memory-first product identity
- replacing upstream AI coding products with a proprietary IDE shell
- deployment automation as the default completion path
