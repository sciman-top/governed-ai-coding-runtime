# Architecture Index

## Purpose
This directory holds the architectural views that explain product boundaries, target shape, MVP narrowing, and compatibility posture.

## Recommended Reading Order
1. [Minimum Viable Governance Loop](./minimum-viable-governance-loop.md)
2. [Governance Boundary Matrix](./governance-boundary-matrix.md)
3. [Generic Target-Repo Attachment Blueprint](./generic-target-repo-attachment-blueprint.md)
4. [Repo-Native Contract Bundle](./repo-native-contract-bundle.md)
5. [Local Baseline To Hybrid Final-State Migration Matrix](./local-baseline-to-hybrid-final-state-migration-matrix.md)
6. [MVP Stack Vs Target Stack](./mvp-stack-vs-target-stack.md)
7. [Compatibility Matrix](./compatibility-matrix.md)
8. [Governed AI Coding Runtime Target Architecture](./governed-ai-coding-runtime-target-architecture.md)
9. [Runtime Evolution Policy](./runtime-evolution-policy.json)
10. [Policy Tool Credential Audit Boundary](./policy-tool-credential-audit-boundary.json)
11. [Governance Hub Certification](./governance-hub-certification.json)

## Document Roles
- [Minimum Viable Governance Loop](./minimum-viable-governance-loop.md)
  - smallest governed execution loop that the MVP must prove
- [Governance Boundary Matrix](./governance-boundary-matrix.md)
  - ownership split between kernel governance, repo inheritance, repo override, and out-of-scope concerns
- [Generic Target-Repo Attachment Blueprint](./generic-target-repo-attachment-blueprint.md)
  - preferred attach-first product shape for repo-local packs, machine-wide runtime state, and session bridges
- [Repo-Native Contract Bundle](./repo-native-contract-bundle.md)
  - source-of-truth to runtime-bundle mapping for repo-local declarations versus machine-local state
- [Local Baseline To Hybrid Final-State Migration Matrix](./local-baseline-to-hybrid-final-state-migration-matrix.md)
  - decision bridge between completed local baseline slices, the landed hybrid boundary, and the active direct-to-hybrid closure queue
- [MVP Stack Vs Target Stack](./mvp-stack-vs-target-stack.md)
  - tracer-bullet implementation posture versus long-term platform direction
- [Compatibility Matrix](./compatibility-matrix.md)
  - support levels for OS, shell, repo host, CI model, and agent product shapes
- [Governed AI Coding Runtime Target Architecture](./governed-ai-coding-runtime-target-architecture.md)
  - full target-state architecture and plane decomposition
- [Runtime Evolution Policy](./runtime-evolution-policy.json)
  - enforced dry-run policy for 30-day source-grounded self-evolution review, candidate decisions, AI coding experience/skillization signals, risk boundaries, and verification floor
- [Policy Tool Credential Audit Boundary](./policy-tool-credential-audit-boundary.json)
  - enforced fail-closed audit boundary for tool identity, credential scope, policy basis, and target-repo override limits without becoming an IAM platform
- [Governance Hub Certification](./governance-hub-certification.json)
  - enforced certification contract that combines target-repo effect evidence, current-source compatibility, controlled evolution loops, and host-boundary assertions

## Usage Rule
- If implementation scope is under debate, start with the first three documents before reading the full target architecture.
- If the question is where repo-local declarations end and machine-local runtime state begins, read the repo-native contract bundle doc before changing attachment or packaging behavior.
- If historical completed plans or landed local runtime code are being compared against the hybrid final state, read the migration matrix before deciding that the current baseline is either "wrong" or "already final."
- If adapter or environment questions arise, pair this index with [docs/specs/agent-adapter-contract-spec.md](../specs/agent-adapter-contract-spec.md) and [docs/specs/repo-profile-spec.md](../specs/repo-profile-spec.md).
