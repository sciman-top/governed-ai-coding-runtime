# Checklist-first bug diagnosis

## Status
- Candidate only.
- `default_enabled=false`.
- Do not install or enable without human review and project gates.

## Description
Use checklist-first observation before root-cause reasoning when bug evidence is incomplete.

## Capabilities
- Restate the bug target before proposing a fix.
- Ask for request, log, repro, and last-known-good observations when missing.
- Keep the pattern advisory until project gates validate the fix.

## Required Contracts
- `interaction-evidence`
- `learning-efficiency-metrics`
- `controlled-improvement-proposal`

## Rollback
Delete this candidate directory. No runtime behavior is enabled by this file.
