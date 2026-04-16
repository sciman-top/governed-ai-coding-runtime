# Provenance And Attestation Spec

## Status
Draft

## Purpose
Define the minimum provenance and attestation record for build artifacts, control packs, schema bundles, and release outputs.

## Required Fields
- attestation_id
- subject_type
- subject_ref
- subject_digest
- predicate_type
- producer
- generated_at
- materials
- verification_status

## Optional Fields
- build_ref
- control_pack_ref
- repo_id
- statement_ref
- signature_refs
- notes

## Enumerations
### subject_type
- artifact
- control_pack
- schema_bundle
- release
- evidence_bundle

### verification_status
- unverified
- verified
- failed
- waived

## Invariants
- verified attestations must include either a statement reference or one or more signature references
- every material entry must identify a stable reference and digest or version
- attestation records may prove provenance but may not replace approval, evidence, or rollback records
- subject digest must be immutable for the lifetime of the attestation
