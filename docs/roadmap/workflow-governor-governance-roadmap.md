# Workflow Governor Governance Roadmap

## Status
- owner-directed conditional follow-on queue only
- does not replace the current `Continuous-Execution` active queue

## Goal
Build a governed workflow-mode layer on top of the existing target-repo baseline, gate orchestration, evidence, and KPI surfaces.

## Dependency Line
`GAP-172 -> GAP-173 -> GAP-174 -> GAP-175 -> GAP-176 -> GAP-177 -> GAP-178 -> GAP-179 -> GAP-180`

## Milestones
| milestone | closes | outcome |
| --- | --- | --- |
| `WFG-0` | claim drift around workflow value | value audit and product-boundary tightening are explicit |
| `WFG-1` | workflow reference ambiguity | guarded workflow-governance surface and local reference set are explicit |
| `WFG-2` | workflow contract gap | workflow-governance and workflow-effect-metrics contracts exist |
| `WFG-3` | projection gap | repo-profile, control-pack, adapter, runtime, target-run, KPI, and effect-report all speak the same workflow vocabulary |
| `WFG-4` | proof gap | two-repo workflow comparison evidence exists |

## Queue

### GAP-173 Workflow-Governor Value Audit And Product Boundary Rewrite
- tighten value claims
- separate proved governance value from unproved workflow-executor claims

### GAP-174 Reference Shelf Refresh And Workflow Reference-Basis Enforcement
- add workflow-governance shelf references
- guard workflow-governance surfaces with required local references

### GAP-175 Workflow Governance Contract Family
- define workflow modes
- define degrade rules
- define workflow effect metrics surface

### GAP-176 Repo Profile, Control Pack, And Adapter Workflow Expansion
- add workflow policy to repo profile
- add workflow refs to execution/materialization contracts
- add workflow capability declarations to adapters

### GAP-177 Runtime Selection And Workflow Projection
- deterministic workflow selection
- explicit degrade projection
- target-run output fields

### GAP-178 Workflow Effect Metrics And KPI Integration
- mode-aware KPI
- mode-aware effect-report

### GAP-179 Two-Repo Workflow Comparison Proof
- direct-fix low-risk proof
- spec-first/spec-plus-review medium-risk proof

### GAP-180 Claim Tightening And Conditional Package Completion
- closeout evidence
- renderable roadmap/backlog/issue seeds
- conditional completion without planning-truth mutation
