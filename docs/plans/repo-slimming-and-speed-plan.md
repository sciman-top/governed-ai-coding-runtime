# Repo Slimming And Coding Speed Plan

> **For agentic workers:** Treat this as a bounded optimization lane. Do not delete, move, or archive evidence until the relevant task has a fresh inventory, rollback path, focused tests, and a change-evidence entry.

**Goal:** Reduce coding latency, repository navigation noise, and default context/token cost without weakening the governed runtime evidence model, rule distribution chain, rollback posture, or hard-gate semantics.

**Architecture:** Keep the active runtime and governance surfaces small, and move historical material behind explicit indexes. Active work should default to root entrypoints, current evidence summaries, relevant scripts, relevant tests, and the governed repo-map artifact. Historical evidence, screenshots, rule-sync backups, old target-run payloads, and completed GAP records remain traceable but should not be part of the default agent work surface.

**Tech Stack:** Markdown plans and evidence under `docs/`, repo-map strategy under `.governed-ai/`, PowerShell operator/gate entrypoints under `run.ps1` and `scripts/`, Python inventory and verifier scripts under `scripts/`, and existing runtime tests under `tests/runtime/`.

---

## Status

- Status: completed bounded optimization lane on `2026-05-03`.
- Created from the 2026-05-02 repository slimming review.
- This plan does not authorize deletion or evidence movement by itself.
- First implementation slice must be inventory-only or archive-index-only unless a task explicitly adds fresh rollback and gate evidence.

## Current Baseline

Observed on 2026-05-02 with the generated inventory artifact `docs/change-evidence/repo-slimming-surface-audit.json`:

- Visible work surface, excluding transient runtime/cache directories: `1154` files, `16097152` bytes, `15.35 MB`.
- Text surface: `1123` files and `184362` lines.
- `docs/`: `764` files, `10879267` bytes, `10.38 MB`, and `96022` text lines.
- `docs/change-evidence/`: `572` files, `9455870` bytes, `9.02 MB`, and `66505` text lines.
- PNG evidence and root screenshots: `26` files and `6.44 MB`.
- Hotspot entrypoints:
  - `scripts/runtime-flow-preset.ps1`: about `2594` lines.
  - `scripts/verify-repo.ps1`: about `950` lines in text inventory.
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`: about `3224` lines.
- Existing context budget control:
  - `.governed-ai/repo-map-context-shaping.json` excludes `docs/change-evidence/**`.
  - `docs/change-evidence/repo-map-context-artifact.json` reported `selected_file_count=31`, `estimated_token_cost=5988`, `max_tokens=6000`, and `decision=keep`.

## Problem Statement

The repository is not too heavy because governance exists. It is too heavy because active operating surfaces, completed planning history, raw evidence archives, UI screenshots, target-run payloads, rule-sync backups, and large orchestration scripts live close enough together that agents and maintainers repeatedly rediscover historical material while trying to make current code changes.

The optimization target is therefore separation and routing, not blanket deletion.

## Non Goals

- Do not delete governance rules, hard-gate semantics, rollback requirements, or evidence requirements.
- Do not remove Codex, Claude, or Gemini rule-source families from `rules/manifest.json`.
- Do not rewrite the runtime architecture while doing repository slimming.
- Do not make `fast` checks replace delivery readiness or full gates.
- Do not move target-repo evidence without an index, compatibility note, and rollback path.
- Do not touch current uncommitted managed-asset cleanup work unless the current slice explicitly owns that file set.

## Source Inputs

- `AGENTS.md`
- `README.md`
- `run.ps1`
- `scripts/operator.ps1`
- `scripts/runtime-flow-preset.ps1`
- `scripts/verify-repo.ps1`
- `.governed-ai/repo-map-context-shaping.json`
- `docs/change-evidence/repo-map-context-artifact.json`
- `docs/change-evidence/runtime-test-speed-latest.json`
- `docs/change-evidence/target-repo-runs/kpi-latest.json`
- `docs/plans/README.md`

## Dependency Graph

```text
Task 1 baseline inventory and policy fence
  -> Task 2 evidence archive layout and index
       -> Task 3 context routing and repo-map defaults
            -> Task 4 root README and plan index slimming
                 -> Task 5 runtime-flow-preset.ps1 responsibility split
                      -> Task 6 verify-repo and gate timing split
                           -> Task 7 operator UI and screenshot retention
                                -> Task 8 closeout metrics and guardrails
```

## Task List

**Cross-task evidence rule:**
- Any task that moves files, changes default context routing, changes gate routing, or changes operator behavior must add one `docs/change-evidence/<date>-repo-slimming-<slug>.md` entry with basis, commands, key output, compatibility, and rollback.

### Task 1: Baseline Inventory And Safety Fence

**Purpose:** Turn the current size and token-cost concern into a machine-readable baseline before any cleanup work starts.

**Files:**
- Create: `docs/change-evidence/20260502-repo-slimming-inventory.md`
- Create: `docs/change-evidence/repo-slimming-surface-audit.json`
- Create: `scripts/audit-repo-slimming-surface.py`
- Create: `tests/runtime/test_repo_slimming_surface.py`

**Acceptance criteria:**
- [x] Inventory reports file count, bytes, text lines, top directories, top files, and large binary evidence.
- [x] Inventory separates active runtime, docs, evidence, rules, tests, schemas, and generated/transient directories.
- [x] Inventory emits JSON suitable for future comparison.
- [x] Safety fence says current plan is no-delete until Task 2 or later explicitly authorizes archive moves.
- [x] Existing dirty worktree changes are listed as out of scope unless explicitly adopted.

**Verification:**
- [x] `python -m unittest tests.runtime.test_repo_slimming_surface`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

**Result summary:**
- Visible work surface: `1154` files, `15.35 MB`.
- Text surface: `1123` files, `184362` lines.
- `docs/change-evidence/`: `572` files, `9.02 MB`.
- Transient surfaces remain excluded from the visible baseline, with `.runtime` at `20.81 MB` and `dist` at `13.54 MB`.

### Task 2: Evidence Archive Layout And Index

**Purpose:** Keep evidence traceable while removing historical raw artifacts from the default work surface.

**Planned files:**
- Modify: `docs/change-evidence/README.md`
- Create: `docs/change-evidence/current/README.md`
- Create: `docs/change-evidence/archive/README.md`
- Create: `docs/change-evidence/evidence-index.json`
- Create: `docs/change-evidence/20260502-change-evidence-archive-index.md`
- Create: `scripts/archive-change-evidence.py`
- Create: `tests/runtime/test_archive_change_evidence.py`

**Acceptance criteria:**
- [x] Defines `current`, `latest`, and `archive` semantics.
- [x] Keeps latest summaries and active rollback references easy to find.
- [x] Moves no files until the archive script can dry-run and produce a rollback manifest.
- [x] Archive dry-run identifies old screenshots, old target-run JSON, old rule-sync backups, and old snapshots separately.
- [x] No active evidence referenced by current plans, README, or rule manifests is moved without an updated reference.

**Verification:**
- [x] `python scripts/archive-change-evidence.py --dry-run --json`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

**Result summary:**
- Dry-run candidate groups: `5`
- Dry-run candidate files: `237`
- Dry-run candidate size: `8.75 MB`
- Largest candidate group is operator UI screenshots at `4.56 MB`, followed by root operator UI screenshots at `1.55 MB` and target-run payloads at `1.43 MB`.

### Task 3: Context Routing And Repo-Map Defaults

**Purpose:** Make low-token context routing the default instead of relying on agent discipline.

**Planned files:**
- Modify: `.governed-ai/repo-map-context-shaping.json`
- Modify: `scripts/build-repo-map-context-artifact.py`
- Modify: `tests/runtime/test_repo_map_context_artifact.py`
- Create: `docs/change-evidence/20260502-repo-map-archive-routing.md`

**Acceptance criteria:**
- [x] Default repo-map excludes evidence archives, generated run payloads, raw screenshots, rule-sync backups, and snapshots.
- [x] Required governance files remain included even when broad excludes are tightened.
- [x] Artifact reports estimated token cost, selected file count, excluded archive count, and required-file override count.
- [x] Target budget remains at or below the current `6000` token budget unless a task records a justified exception.

**Verification:**
- [x] `python scripts/build-repo-map-context-artifact.py`
- [x] `python -m unittest tests.runtime.test_repo_map_context_artifact`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

**Result summary:**
- `decision=keep`
- `estimated_token_cost=5985`
- `selected_file_count=31`
- `excluded_archive_candidate_count=231`
- `required_file_override_count=0`

### Task 4: Root README And Plan Index Slimming

**Purpose:** Keep human entrypoints useful without making root docs carry long completion history.

**Planned files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `README.en.md`
- Modify: `docs/plans/README.md`
- Create: `docs/archive/completed-gap-history.md`
- Create: `docs/archive/completed-gap-history.zh-CN.md`
- Create: `docs/change-evidence/20260502-root-readme-history-slimming.md`

**Acceptance criteria:**
- [x] Root README files keep project purpose, canonical entrypoints, daily commands, readiness commands, current posture, and links.
- [x] Completed GAP history moves behind a stable archive/history link.
- [x] Chinese and English operator-facing usage remains available.
- [x] No gate, rollback, rule-sync, or safety semantics are removed.

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

**Result summary:**
- Root README entrypoints now keep current posture and commands while routing long completion history to `docs/archive/completed-gap-history*.md`.
- `docs/plans/README.md` now links to the same archive for detailed `GAP-104..111` and `GAP-130..143` history instead of repeating long status blocks inline.

### Task 5: Runtime Flow Preset Responsibility Split

**Purpose:** Reduce the maintenance cost of the largest PowerShell orchestration script without changing behavior.

**Planned files:**
- Modify: `scripts/runtime-flow-preset.ps1`
- Consider create: `scripts/lib/RuntimeFlow.Targets.ps1`
- Consider create: `scripts/lib/RuntimeFlow.Batch.ps1`
- Consider create: `scripts/lib/RuntimeFlow.Evidence.ps1`
- Modify: `tests/runtime/test_runtime_flow_preset.py`

**Acceptance criteria:**
- [x] Extract one responsibility at a time.
- [x] Public CLI parameters and JSON output remain backward compatible.
- [x] Focused tests cover the extracted responsibility before the next extraction begins.
- [x] The root script remains the canonical entrypoint.

**Verification:**
- [x] `python -m unittest tests.runtime.test_runtime_flow_preset`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`

**Current slice status:**
- First extraction complete: target catalog parsing moved into `scripts/lib/RuntimeFlow.Targets.ps1`.
- Canonical entrypoint remains `scripts/runtime-flow-preset.ps1`.
- Fresh evidence: `docs/change-evidence/20260502-runtime-flow-target-catalog-split.md`
- Focused verification already passed:
  - `python -m unittest tests.runtime.test_runtime_flow_preset`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`

**Result summary:**
- One stable responsibility is now split out: target catalog parsing lives in `scripts/lib/RuntimeFlow.Targets.ps1`.
- `-ListTargets -Json` and the existing target selection flow remain backward compatible under the canonical `scripts/runtime-flow-preset.ps1` entrypoint.
- Focused runtime-flow tests and the repo-level Runtime gate both passed after the extraction.

### Task 6: Verify Repo And Gate Timing Split

**Purpose:** Keep hard-gate semantics while improving daily feedback time and failure locality.

**Planned files:**
- Modify: `scripts/verify-repo.ps1`
- Modify: `scripts/run-runtime-tests.py`
- Modify: `run.ps1`
- Modify: `scripts/operator.ps1`
- Modify or create: runtime speed evidence under `docs/change-evidence/`

**Acceptance criteria:**
- [x] `.\run.ps1 fast` remains the daily coding default.
- [x] `readiness` remains the delivery path for `build -> test -> contract/invariant -> hotspot`.
- [x] Slow and timeout-prone test files are visible in a timing report.
- [x] Any new quick profile is explicitly marked as not replacing readiness.

**Verification:**
- [x] `.\run.ps1 fast`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`

**Current slice status:**
- `FastFeedback` now routes through the shared `verify-repo.ps1 -Check RuntimeQuick` surface instead of owning a second inline unittest list.
- `Readiness` still owns the delivery path for `build -> test -> contract/invariant -> hotspot`.
- Fresh timing evidence now lands in `docs/change-evidence/runtime-test-speed-latest.json` on every passing Runtime gate.
- Fresh evidence: `docs/change-evidence/20260503-runtime-gate-timing-split.md`

**Result summary:**
- `.\run.ps1 fast` remains the default daily path and completed successfully with the shared quick gate.
- The full Runtime gate completed `101` test files in `188.408s` with `0` failures and refreshed the latest timing artifact.
- The current runtime hotspot list is now visible in one stable machine-readable report instead of a stale failed benchmark snapshot.

### Task 7: Operator UI And Screenshot Retention

**Purpose:** Keep visual regression evidence useful without letting screenshots dominate the repository surface.

**Planned files:**
- Modify or create: `docs/change-evidence/README.md`
- Consider create: `scripts/prune-operator-ui-screenshots.py`
- Modify or create: `tests/runtime/test_operator_ui_evidence_retention.py`

**Acceptance criteria:**
- [x] Defines which screenshots are latest, milestone, or archive candidates.
- [x] Dry-run reports screenshot count and total size.
- [x] Apply mode requires explicit flag, backup or manifest, and rollback instructions.
- [x] Current README/operator UI docs reference latest screenshots only when needed.

**Verification:**
- [x] `python scripts/prune-operator-ui-screenshots.py --dry-run --json`
- [x] `python -m unittest tests.runtime.test_operator_ui_evidence_retention`

**Current slice status:**
- Operator UI screenshots now have an explicit `latest / milestone / archive_candidate` contract.
- Dry-run classification and apply-mode manifest behavior are covered by focused tests.
- This slice adds a real archive path but does not move any existing screenshots yet.
- Fresh evidence: `docs/change-evidence/20260503-operator-ui-screenshot-retention.md`

**Result summary:**
- Dry-run classified `26` screenshots: `5 latest`, `5 milestone`, `16 archive candidates`.
- Archive candidates total `4226988` bytes, which keeps the screenshot-heavy active surface measurable without forcing a move in the same slice.
- Apply mode is now explicit and rollback-aware through a generated archive manifest.

### Task 8: Closeout Metrics And Guardrails

**Purpose:** Prove the slimming work improved the work surface without weakening governance.

**Planned files:**
- Create: `docs/change-evidence/<date>-repo-slimming-closeout.md`
- Update: `docs/plans/repo-slimming-and-speed-plan.md`
- Consider update: `docs/plans/README.md`

**Acceptance criteria:**
- [x] Reports before/after file counts, bytes, text lines, context artifact token estimate, and fast/readiness timing.
- [x] Reports which evidence moved, which stayed current, and how rollback works.
- [x] Confirms hard-gate semantics and rule-sync contracts remain intact.
- [x] Leaves future retention policy visible enough that history does not accumulate in the active surface again.

**Verification:**
- [x] `.\run.ps1 fast`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

**Current slice status:**
- Closeout evidence now reports both the honest physical-surface outcome and the improved default context/retention/gate posture.
- No archive candidate was moved silently; the lane ends with dry-run-first controls and explicit future apply paths.
- Fresh evidence: `docs/change-evidence/20260503-repo-slimming-closeout.md`

**Result summary:**
- Physical repo size is slightly larger than the initial baseline because this lane added executable guardrails, tests, and fresh evidence instead of applying archive moves.
- The default active work posture is still improved: token routing stays within budget, archive-heavy surfaces are explicitly classified, fast/readiness ownership is clearer, and screenshot retention is now executable rather than implicit.
- This bounded optimization lane is complete without weakening governance.

## Risk Controls

- **Evidence loss risk:** all file movement must be dry-run-first and manifest-backed.
- **Rule drift risk:** any rule-source or distributed-rule path change must run the existing rule drift checks.
- **Gate weakening risk:** quick profiles must remain explicitly non-authoritative for delivery.
- **Token regression risk:** repo-map artifact must report estimated token cost after each routing change.
- **Dirty worktree risk:** do not mix this lane with unrelated managed-asset cleanup changes unless the user explicitly asks to merge scopes.

## Initial Recommendation

AI recommended first implementation slice:

1. Add an inventory script and test.
2. Produce machine-readable inventory evidence.
3. Update this plan with the exact inventory output.
4. Stop before moving or deleting evidence.

Reason: it creates a safe measurement baseline and avoids mixing repository slimming with the current uncommitted managed-asset cleanup work.
