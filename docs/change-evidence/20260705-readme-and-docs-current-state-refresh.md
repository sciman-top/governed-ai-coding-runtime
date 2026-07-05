# 20260705 Readme And Docs Current-State Refresh

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/README.md`
  - `apps/README.md`
  - `infra/README.md`
  - `docs/architecture/README.md`
  - `docs/backlog/README.md`
  - `docs/plans/README.md`
  - `docs/prd/governed-ai-coding-runtime-prd.md`
  - `docs/product/interaction-model.md`
  - `docs/strategy/current-best-end-state-blueprint.md`
  - `docs/strategy/positioning-and-competitive-layering.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/evidence-index.json`
  - `docs/change-evidence/20260705-readme-and-docs-current-state-refresh.md`
- verification path: refresh operator-facing entry docs so they reflect the final `2026-07-05` selector and live-posture truth after the fresh target-run/KPI/effect refresh, the refreshed functional-effectiveness evidence, the still-current `2026-06-24` governance/self-evolution machine-readable refresh, and the checked-in app/infra/package surfaces without promoting a new queue

## Why This Refresh Was Needed
- The entry docs first had to be downgraded away from the older `2026-06-23` recovered posture when the selector temporarily fell back to `repair_gate_first`.
- After the `2026-07-05` target-run refresh and the new `2026-07-05` functional-effectiveness evidence refresh, the selector returned to `defer_ltp_and_refresh_evidence`; the repo therefore needed a second same-day docs sync so the entry surfaces no longer overstated the intermediate stale/repair posture.
- Several entry docs also needed to distinguish two different machine-readable timelines:
  - fresh `2026-07-05` target-run / KPI / effect evidence
  - still-current `2026-06-24` governance / self-evolution evidence artifacts
- `apps/README.md`, `infra/README.md`, and `docs/architecture/README.md` had already been refreshed to checked-in repo truth and remained part of the same operator-facing entry surface.

## Current Truth Captured
- `planning-status.json` is refreshed again as the single source of current queue and live-posture truth:
  - `updated_on=2026-07-05`
  - `current_active_queue=Continuous-Execution`
  - `current_decision_gate=defer_ltp_and_refresh_evidence`
  - target-run freshness is `fresh`
  - Codex target runs are `native_attach / ready`
  - the Claude workload probe remains `native_attach / ready`
- The latest machine-readable target-run upkeep on this branch is the `2026-07-05` daily target-run/KPI/effect refresh under `docs/change-evidence/target-repo-runs/`.
- The latest governance / self-evolution machine-readable refresh still remains the `2026-06-24` evidence set; it stays current without promoting a new queue.

## Change Summary
1. Refreshed root and docs entrypoints
- updated `README.md`, `README.en.md`, `README.zh-CN.md`, and `docs/README.md`
- restored the truthful recovered posture after the fresh `2026-07-05` target-run and functional-effectiveness evidence refresh
- separated the `2026-07-05` target-run/KPI/effect refresh from the still-current `2026-06-24` governance/self-evolution machine-readable refresh so the timelines are not conflated

2. Refreshed repository sub-surface docs
- kept the checked-in `apps/` / `infra/` / `docs/architecture/` entry surfaces aligned with actual repo truth
- updated `docs/backlog/README.md`, `docs/plans/README.md`, `docs/product/interaction-model.md`, `docs/strategy/*`, and the PRD so they again match `defer_ltp_and_refresh_evidence` plus the fresh `native_attach / ready` posture
- preserved historical `2026-06-17` planning-proof references as archived milestones instead of letting them override the current evidence window

3. Refreshed evidence routing
- added the fresh `20260705` functional-effectiveness and claim-catalog evidence notes to the operator-facing evidence index
- updated `docs/change-evidence/README.md` to expose the current `20260705` posture proof chain
- regenerated `docs/change-evidence/evidence-index.json` so the newest markdown entrypoints remain machine-readable

## Reference Required Review
- `reference_required_review`: required because this slice updates operator-facing truth surfaces, the claim catalog, fresh 2026-07-05 evidence notes, and guarded strategy wording that falls under the repo's `reference-shelf-and-borrowing-docs` surface.
- `changed_surface_paths`:
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/README.md`
  - `docs/architecture/planning-status.json`
  - `docs/backlog/README.md`
  - `docs/plans/README.md`
  - `docs/prd/governed-ai-coding-runtime-prd.md`
  - `docs/product/claim-catalog.json`
  - `docs/product/interaction-model.md`
  - `docs/strategy/current-best-end-state-blueprint.md`
  - `docs/strategy/positioning-and-competitive-layering.md`
  - `docs/change-evidence/20260705-readme-and-docs-current-state-refresh.md`
  - `docs/change-evidence/20260705-runtime-evolution-functional-verification.md`
  - `docs/change-evidence/20260705-claim-catalog-freshness-refresh.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/evidence-index.json`
- `official_sources_reviewed`: no new vendor behavior or external workflow claim was adopted in this slice; the repo keeps the existing official-tool-loading and host-boundary posture, and this refresh only reprojects fresh local evidence into the operator-facing docs.
- `primary_references_reviewed`:
  - `docs/architecture/planning-status.json`
  - `docs/product/claim-catalog.json`
  - `scripts/select-next-work.py`
  - `scripts/host-feedback-summary.py`
  - `scripts/verify-evidence-recovery-posture.py`
  - `scripts/verify-functional-effectiveness.py`
  - guarded paths:
    - `docs/strategy/current-best-end-state-blueprint.md`
    - `docs/strategy/positioning-and-competitive-layering.md`
- `local_runtime_evidence_reviewed`:
  - `docs/change-evidence/target-repo-runs/classroomtoolkit-daily-20260705225034.json`
  - `docs/change-evidence/target-repo-runs/cockpit-tools-local-daily-20260705225034.json`
  - `docs/change-evidence/target-repo-runs/github-toolkit-daily-20260705225034.json`
  - `docs/change-evidence/target-repo-runs/k12-question-graph-daily-20260705225034.json`
  - `docs/change-evidence/target-repo-runs/self-runtime-daily-20260705225034.json`
  - `docs/change-evidence/target-repo-runs/skills-manager-daily-20260705225034.json`
  - `docs/change-evidence/target-repo-runs/vps-ssh-launcher-daily-20260705225034.json`
  - `docs/change-evidence/target-repo-runs/kpi-latest.json`
  - `docs/change-evidence/target-repo-runs/kpi-rolling.json`
  - `docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json`
  - gate outputs from `scripts/build-runtime.ps1`, `scripts/verify-repo.ps1 -Check Runtime`, `scripts/verify-repo.ps1 -Check Docs`, and `scripts/verify-repo.ps1 -Check All`
- `source_decision`: restore the recovered `defer_ltp_and_refresh_evidence` wording only because fresh 2026-07-05 target-run evidence, fresh 2026-07-05 functional-effectiveness evidence, and the recovered host-feedback/effect posture all agree again; keep the 2026-06-17 planning-proof chain and the 2026-06-09 live-posture recovery strictly as historical milestones, not as substitutes for the current evidence window.

## Verification
- `python scripts/select-next-work.py --as-of 2026-07-05`
  - result: pass
  - result: `next_action=defer_ltp_and_refresh_evidence`, `gate_state=pass`, `evidence_state=fresh`
- `python scripts/host-feedback-summary.py --assert-minimum`
  - result: pass
  - result: `status=pass`; target-run freshness is `fresh` and the latest evidence is summarized for 7 repos
- `python scripts/verify-evidence-recovery-posture.py --as-of 2026-07-05`
  - result: pass
  - result: selector, host-feedback, and effect-report recovery posture agree on fresh `ready/native_attach/live_attach` evidence
- `python scripts/verify-planning-status.py`
  - result: pass
  - result: `planning-status.json` and dependent README/strategy/PRD/doc entrypoints are aligned on `Continuous-Execution`, `defer_ltp_and_refresh_evidence`, and `ready`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass
  - result: Docs gate passed through `claim-evidence-freshness` and `post-closeout-queue-sync`
- `python scripts/archive-change-evidence.py --write-index`
  - result: pass
  - result: `docs/change-evidence/evidence-index.json` regenerated with the latest markdown entry list
- `docker compose -f infra/local-runtime/docker-compose.yml config`
  - result: pass
  - result: local compose scaffold renders the checked-in `postgres`, `control-plane`, `workflow-worker`, `agent-worker`, and `tool-runner` services; Docker also warns that the Compose `version` key is obsolete

## Risk
- risk_level: `low`
- reason:
  - documentation and evidence-routing refresh only
  - fresh functional-effectiveness and claim-catalog evidence refresh only
  - no queue promotion
  - no policy broadening
  - no host/provider/runtime-state mutation
  - repo truth is tightened by restoring only evidence-backed recovered posture claims instead of masking drift

## Rollback
- revert:
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/README.md`
  - `apps/README.md`
  - `infra/README.md`
  - `docs/architecture/README.md`
  - `docs/backlog/README.md`
  - `docs/plans/README.md`
  - `docs/prd/governed-ai-coding-runtime-prd.md`
  - `docs/product/interaction-model.md`
  - `docs/strategy/current-best-end-state-blueprint.md`
  - `docs/strategy/positioning-and-competitive-layering.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/evidence-index.json`
  - `docs/change-evidence/20260705-readme-and-docs-current-state-refresh.md`
- re-run:
  - `python scripts/select-next-work.py --as-of 2026-07-05`
  - `python scripts/host-feedback-summary.py --assert-minimum`
  - `python scripts/verify-evidence-recovery-posture.py --as-of 2026-07-05`
  - `python scripts/verify-planning-status.py`
  - `python scripts/archive-change-evidence.py --write-index`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
