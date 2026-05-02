# repo-governance-hub Borrowing Review

## Purpose
Capture what `governed-agent-platform` should borrow from `repo-governance-hub`, what should be deferred, and what should remain outside the product boundary.

## Source Review Scope
Reviewed areas:
- `README.md`
- `config/governance-control-registry.json`
- `config/project-rule-policy.json`
- `config/agent-runtime-policy.json`
- `config/practice-stack-policy.json`
- `.governance/tracked-files-policy.json`
- `.governance/risk-tier-approval-policy.json`
- `.governance/trace-grading-policy.json`
- `.governance/failure-replay/policy.json`
- `scripts/lib/common.ps1`
- `scripts/governance/fast-check.ps1`
- `scripts/governance/check-tracked-files.ps1`
- `scripts/governance/check-risk-tier-approval.ps1`
- `scripts/governance/check-trace-grading-readiness.ps1`
- `scripts/governance/check-failure-replay-readiness.ps1`
- `scripts/governance/run-target-autopilot.ps1`
- `scripts/install.ps1`
- `docs/governance/evidence-and-rollback-runbook.md`
- `docs/governance/verification-entrypoints.md`
- `tests/repo-governance-hub.optimization.tests.ps1`

## Adopt Now
1. Control registry model
- Why: converts governance from prose into inventory.
- GAP use: catalog controls for task intake, approval, tool contracts, evidence, evals, rollback.

2. Default policy plus repo override model
- Why: lets the platform keep a stable kernel while allowing bounded repo variation.
- GAP use: repo profiles, budgets, risk posture, allowed commands, verification commands.

3. Agent runtime policy schema
- Why: required fields for prompts, tools, evals, observability, and memory constraints are directly relevant to AI coding.
- GAP use: prompt registry, tool contract registry, observability baseline, observe-to-enforce policy.

4. Fast check to full gate escalation
- Why: keeps local feedback fast without weakening hard-gate semantics.
- GAP use: quick verify, full verify, risk-based escalation by changed scope.

5. Risk-tier approval integrity checks
- Why: high-risk actions should fail structurally if no explicit approval path exists.
- GAP use: tool risks, write scopes, irreversible actions, evidence requirements by tier.

6. Evidence and rollback runbook discipline
- Why: the platform needs replayable, reviewable execution records.
- GAP use: evidence bundle schema, rollback reference, verification order, open questions.

7. Tracked files and artifact classification
- Why: AI coding produces many transient artifacts that should not leak into delivery.
- GAP use: commit packaging policy, artifact allowlist/denylist, generated output classification.

8. Shared deep-module helper layer
- Why: repeated governance logic should be hidden behind a small number of reusable interfaces.
- GAP use: config loading, path resolution, command capture, evidence writing, policy resolution.

## Adopt Later
1. Trace grading readiness
- Use after the platform has enough executions to audit evidence quality statistically.

2. Failure replay readiness
- Use after repeated failure signatures exist and replay cases become meaningful.

3. Practice-stack registry
- Keep as an architecture and operations checklist, not as a Phase 1 feature.

4. Controlled subagent decision policy
- Borrow the hard-guard and scoring concept only after single-agent execution is stable.

## Do Not Adopt Into MVP
1. Multi-repo source-of-truth distribution
2. Backflow and mirrored source trees
3. Skills promotion lifecycle
4. Cross-repo template sync
5. PowerShell-first runtime architecture
6. AGENTS/CLAUDE/GEMINI distribution machinery

## Boundary Decision
`governed-agent-platform` should inherit the governance kernel, not the governance-hub shape.

## Follow-on Documents
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/specs/control-registry-spec.md`
- `docs/specs/repo-profile-spec.md`
- `docs/specs/tool-contract-spec.md`
- `docs/specs/risk-tier-and-approval-spec.md`
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/verification-gates-spec.md`
- `docs/specs/eval-and-trace-grading-spec.md`
