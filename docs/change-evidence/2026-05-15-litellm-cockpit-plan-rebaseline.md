# 2026-05-15 LiteLLM Cockpit Plan Rebaseline

- rule_id: LocalCodexCockpit / CCHS-005
- risk: low; planning, tests, and evidence only
- current_landing: `docs/plans/codex-cli-continuity-and-hot-switch-plan.md`, `docs/plans/README.md`, `tests/runtime/test_codex_cockpit_policy_contract.py`
- destination: replace the old single proxy feasibility step with an ordered `Codex -> LiteLLM -> Cockpit API service` implementation lane while preserving already-landed native-boundary work

## Decision

Do not delete the older CCHS work. `CCHS-002`, `CCHS-003`, and `CCHS-004` already provide read-only switch health, bounded CLI segment continuity, and operator visibility. They remain useful as fallback and diagnostic infrastructure.

The active next lane is now `CCHS-005A` through `CCHS-005F`:

1. LiteLLM local runtime baseline.
2. Cockpit API upstream listener and firewall hardening.
3. LiteLLM config with Cockpit API service as `cockpit-current`.
4. Reversible Codex profile pointing to LiteLLM without auto-restarting Codex App.
5. Manual Cockpit switch follow test through LiteLLM.
6. Runbook, rollback, evidence, and contract closeout.

## Compatibility

- No local Codex `auth.json`, `config.toml`, `state_5.sqlite`, Cockpit account file, LiteLLM runtime, or Cockpit API service state was changed by this rebaseline.
- The segmented CLI runner remains a fallback, not the primary implementation path.
- Cockpit-aware adapter remains deferred until single-upstream routing cannot satisfy account-label, group, quota, or routing requirements.
- The plan continues to forbid automatic Codex App restarts.

## Verification

- `python -m unittest tests.runtime.test_codex_cockpit_policy_contract`
  - result: pass, `Ran 4 tests`
- `git diff --check`
  - result: pass; only CRLF normalization warnings were reported
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass; key checks included `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`

The Contract gate refreshed `docs/change-evidence/governance-hub-certification-report.json` with stale target-run facts unrelated to this planning rebaseline. That generated diff was reverted before commit so the change remains scoped to CCHS/LiteLLM/Cockpit planning and contract tests.

## Rollback

Revert this evidence file plus the paired edits in:

- `docs/plans/codex-cli-continuity-and-hot-switch-plan.md`
- `docs/plans/README.md`
- `tests/runtime/test_codex_cockpit_policy_contract.py`
