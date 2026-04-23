# Target Repo Speed KPI Spec

## Status
Draft

## Purpose
Define a versioned KPI snapshot for target-repo onboarding and daily loop speed metrics.

## Required Fields
- schema_version
- generated_at
- window_kind
- window_size
- record_count
- records[].target
- records[].total_daily_runs
- records[].deny_to_success_retries
- records[].fallback_rate

## Optional Fields
- records[].onboarding_latency_seconds
- records[].first_pass_latency_seconds
- records[].medium_risk_loop_success_ratio
- records[].problem_run_rate
- records[].problem_recovery_retries
- records[].latest_problem_signature
- records[].latest_problem_run_ref
- records[].window_start_utc
- records[].window_end_utc
- records[].latest_evidence_ref

## Enumerations
### window_kind
- latest
- rolling

## Invariants
- every speed claim must reference a concrete KPI snapshot file and window configuration
- `fallback_rate` must stay within `[0, 1]`
- `medium_risk_loop_success_ratio` must stay within `[0, 1]` when present
- `problem_run_rate` must stay within `[0, 1]`
- `problem_recovery_retries` counts fail-to-pass transitions inside the selected window
- snapshots are read-model exports and may not mutate target-repo truth contracts

## Non-Goals
- replacing detailed per-run evidence files
- forcing one universal latency definition across all adapters
