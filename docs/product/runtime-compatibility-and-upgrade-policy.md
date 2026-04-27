# Runtime Compatibility And Upgrade Policy

## Purpose
- define how adapters, repo profiles, and persisted runtime state may evolve without silently breaking the governed runtime
- keep compatibility expectations explicit after the public usable release baseline

## Compatibility Classes
- `compatible`: no schema, operator-surface, or workflow migration required; quickstart and package bundle continue to work without operator intervention
- `compatible_with_note`: behavior remains usable but requires an explicit note in release or evidence docs, such as a new optional field, richer operator output, or a stricter doctor warning
- `migration_required`: a compatibility-breaking change that needs a documented migration path, rollback note, and evidence entry before it can be treated as released
- `blocked`: the requested adapter or rollout posture cannot safely execute and must fail closed until a supported migration or degrade path exists

## Upgrade Scope

### Adapters
- Codex and Claude Code are the current dual first-class baseline adapters.
- adapters must declare partial support or unsupported capability signals rather than pretending feature parity after host capability drift.
- unsupported capabilities must either declare an explicit `degrade_to` posture or fail closed to `blocked`.

### Repo Profiles
- repo profile additions may be backward-compatible when they only add optional metadata.
- repo profile changes become `migration_required` when they rename required fields, change gate command meaning, or alter path-scope semantics.
- every sample profile shipped in `schemas/examples/repo-profile/` must keep the documented quickstart runnable.

### Persisted Runtime State
- new optional fields in `.runtime/tasks/*.json`, evidence bundles, or runtime status examples are allowed when older readers can ignore them safely.
- removing or renaming persisted fields requires:
  - migration notes
  - rollback guidance
  - evidence that old artifacts remain interpretable or are explicitly retired

## Upgrade Rules
- every compatibility-impacting change must be classified as `compatible`, `compatible_with_note`, `migration_required`, or `blocked`
- `migration_required` changes must update both product policy docs and execution evidence before the queue is treated as complete
- release-adjacent docs, schemas, examples, and doctor checks must stay aligned; drift is a maintenance failure, not a documentation nicety
- operator-visible surfaces should prefer additive changes and preserve stable identifiers such as `task_id`, `run_id`, and persisted artifact refs

## Migration Minimums
- explain what changes
- explain who is affected
- explain how to upgrade or recover
- explain how to roll back if the migration fails

## Evidence Requirement
- compatibility-impacting changes must leave a trace in `docs/change-evidence/*.md`
- the evidence entry should record:
  - compatibility class
  - affected surface
  - migration or rollback note
  - verification commands that proved the upgraded path still works

## Non-Goals
- promise binary stability across every future storage layout
- guarantee feature parity across all adapters
- support silent breaking changes in repo profiles or runtime snapshots
