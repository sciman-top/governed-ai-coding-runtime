# 20260427 GAP-109 Data Plane And Provenance Release Batch

## Goal
- Close `GAP-109` by promoting local proof-shaped metadata into a service-shaped persistence boundary.
- Require provenance or explicit waiver evidence for release-adjacent artifacts.
- Keep event bus, semantic store, object store, and signing workflows deferred until measured pressure justifies them.

## Implementation
- `packages/agent-runtime/persistence.py`
  - records schema migration state for the SQLite metadata store
  - exports replay bundles across task/evidence/artifact/replay/provenance namespaces
  - prunes retained namespaces while returning rollback records
  - restores pruned records through the same upsert path
- `packages/contracts/src/governed_ai_coding_runtime_contracts/artifact_store.py`
  - adds release-adjacent JSON writes that require provenance or an explicit `waiver_ref`
  - returns provenance and waiver references on artifact refs
- `scripts/package-runtime.ps1`
  - emits `.runtime/dist/public-usable-release.provenance.json`
  - returns provenance summary in its JSON output

## Evidence
- Targeted tests:
  - `python -m unittest tests.runtime.test_artifact_store tests.service.test_persistence_data_plane tests.service.test_persistence_postgres`
  - Result: `Ran 10 tests ... OK (skipped=1)`
- Release package command:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1`
  - Result:
    - `distribution_root=D:/CODE/governed-ai-coding-runtime/.runtime/dist/public-usable-release`
    - `provenance_path=D:/CODE/governed-ai-coding-runtime/.runtime/dist/public-usable-release.provenance.json`
    - `provenance.verification_status=verified`
    - `provenance.attestation_id=public-usable-release-local`

## Trigger Decisions
- Event bus: deferred. Replay export and namespace query are sufficient for the current local/service-shaped boundary.
- Semantic store: deferred. No query pressure evidence exists beyond namespace/key lookups and replay bundle export.
- Object store: deferred. Filesystem artifact store plus provenance guard remains enough for current artifact size and local package scope.
- Signing workflow: deferred. The emitted provenance is local verified provenance, not external release signing.

## Planning Updates
- `GAP-109` is marked complete in backlog and implementation plan.
- Roadmap and indexes now state `GAP-104..109` complete and `GAP-110..111` remaining.

## Risks And Boundaries
- This does not certify a production database rollout or external release signing.
- Complete hybrid final-state closure is still not certified. `GAP-110` operations recovery and `GAP-111` final certification remain active.

## Rollback
- Revert the `GAP-109` change set.
- Remove generated local package outputs if needed:
  - `.runtime/dist/public-usable-release`
  - `.runtime/dist/public-usable-release.provenance.json`
