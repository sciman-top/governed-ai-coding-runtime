# Agent Continuity Record Spec

## Purpose
Define the portable record shape used to share AI coding continuity across host tools without merging private host history stores.

## Scope
The record describes continuity metadata for Codex App, Codex CLI, Claude Code, Claude Desktop, and future compatible hosts. It can reference native session artifacts, but it must not copy secrets, cookies, auth snapshots, or large raw transcripts.

## Record Classes
- `native_shared`: same host family can safely reuse native state under a shared root.
- `portable_shared`: cross-host data can be stored as a governed artifact.
- `referenced_only`: source material is referenced by path or id but not copied.
- `isolated_secret`: secret-like material is not stored; only redacted presence or env-var reference is allowed.

## Required Fields
Each record must include:

- `record_id`: stable id for this continuity record.
- `created_at`: ISO 8601 timestamp.
- `updated_at`: ISO 8601 timestamp.
- `tool_family`: host family that produced or owns the native state.
- `surface`: concrete host surface.
- `repo_ref`: repository or workspace path/id.
- `continuity_class`: one of the record classes.
- `account_alias`: non-secret account label.
- `provider_alias`: non-secret provider label.
- `task_summary`: concise portable task summary.
- `evidence_refs`: evidence paths or urls.
- `handoff_refs`: handoff package paths or ids.
- `sensitivity`: retrieval and injection boundary.
- `retention`: expiry and retirement metadata.
- `rollback_ref`: how to remove or ignore the record.

## Optional Auditor Fields
- `config_summary`: non-secret read-only host posture details, such as history persistence, profile names, state file presence, transcript counts, launcher presence, and provider switch policy. It must not include raw credentials, tokens, cookies, or full transcript bodies.

## Security Rules
- Records must not contain raw API keys, refresh tokens, cookies, session cookies, private auth snapshots, or unredacted credential-bearing logs.
- Transcript references are allowed only as `referenced_only` unless a separate redacted excerpt is created as `portable_shared`.
- Cross-account injection must be opt-in or filtered by `account_alias`.
- `isolated_secret` records may contain only redacted presence, secret type, owner surface, and recovery instructions.

## Verification
- JSON records validate against `schemas/jsonschema/agent-continuity-record.schema.json`.
- Schema and spec remain paired through `schemas/catalog/schema-catalog.yaml`.
- Future runtime writers must add secret redaction tests before producing records automatically.
