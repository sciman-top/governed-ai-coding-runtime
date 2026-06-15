# Workflow Governor Governance Plan

## Status
- owner-directed conditional follow-on package only
- do not treat this plan as the current active queue while `docs/architecture/planning-status.json` remains `Continuous-Execution`

## Goal
Turn the product boundary from vague “best AI coding workflow” claims into a governed, evidence-backed `workflow governor` package with explicit contracts, workflow modes, degrade rules, and measurable effect outputs.

## Fixed Boundaries
- do not change `planning-status.json`
- do not claim replacement-host status
- do not claim default built-in multi-agent orchestration is already complete
- do not add a Matt Pocock local reference repo
- do not delete existing reference repos

## Task List

### Task 1: value audit and claim tightening
**Maps to:** `GAP-173`

**Acceptance criteria:**
- a repo-owned value audit exists
- README/docs/interaction/quickstart wording converges on workflow/gate/evidence governance
- docs stop implying replacement-host or built-in best-workflow completion

### Task 2: workflow-governance reference basis
**Maps to:** `GAP-174`

**Acceptance criteria:**
- external shelf includes `github-spec-kit` and `obra-superpowers`
- `workflow-governance-and-spec-driven-delivery` is a guarded surface
- required local references are explicit and machine-readable

### Task 3: workflow governance contract family
**Maps to:** `GAP-175`

**Acceptance criteria:**
- workflow-governance spec/schema/example exist
- workflow-effect-metrics spec/schema/example exist
- workflow modes and degrade rules are explicit

### Task 4: repo profile, control pack, and adapter expansion
**Maps to:** `GAP-176`

**Acceptance criteria:**
- repo-profile supports `workflow_governance_policy`
- control-pack execution/materialization can prove workflow policy distribution
- agent-adapter contract declares workflow-related capabilities

### Task 5: runtime selection and projection
**Maps to:** `GAP-177`

**Acceptance criteria:**
- runtime selection is deterministic
- unsupported advanced modes degrade explicitly
- target-run/effect outputs expose selected workflow mode and reason

### Task 6: workflow effect metrics
**Maps to:** `GAP-178`

**Acceptance criteria:**
- workflow metrics join KPI/effect-report outputs
- evidence is mode-aware, not just pass/fail aware

### Task 7: two-repo proof
**Maps to:** `GAP-179`

**Acceptance criteria:**
- proof targets stay `classroomtoolkit` and `github-toolkit`
- at least one low-risk and one medium-risk workflow comparison exists
- advanced mode claims require explicit host capability proof

### Task 8: closeout and conditional completion
**Maps to:** `GAP-180`

**Acceptance criteria:**
- claim-tightening docs, change evidence, backlog, seeds, roadmap, and scripts agree on `GAP-173..180`
- package remains conditional unless planning truth is promoted later
