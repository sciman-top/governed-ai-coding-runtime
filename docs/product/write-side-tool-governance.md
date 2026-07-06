# Write-Side Tool Governance

## Current Boundary
This repository no longer owns attachment-based or session-bridge-based write execution.

Current write-side governance is repo-local:
1. stay within repo-local path policies
2. keep risky changes bounded by approval defaults and rollback references
3. run the canonical hard-gate chain before claiming completion
4. record evidence and handoff artifacts in the local runtime/task surfaces

## Fail-Closed Rules
- blocked paths remain blocked before any effective write
- medium/high-risk work still requires rollback-ready reasoning
- retired attachment/write commands fail closed instead of silently forwarding
- release packaging and other guarded operations still remain governed by repo-local policy and evidence

## Not A Current Capability
- session-bridge write request/approve/execute flows
- attached target-repo write brokerage
- light-pack-driven external repo mutation

## Related
- [Write Policy Defaults](./write-policy-defaults.md)
- [Approval Flow](./approval-flow.md)
