# Architecture Index

## Purpose
This directory holds the architectural views that explain product boundaries, target shape, MVP narrowing, and compatibility posture.

## Recommended Reading Order
1. [Minimum Viable Governance Loop](./minimum-viable-governance-loop.md)
2. [Governance Boundary Matrix](./governance-boundary-matrix.md)
3. [MVP Stack Vs Target Stack](./mvp-stack-vs-target-stack.md)
4. [Compatibility Matrix](./compatibility-matrix.md)
5. [Governed AI Coding Runtime Target Architecture](./governed-ai-coding-runtime-target-architecture.md)

## Document Roles
- [Minimum Viable Governance Loop](./minimum-viable-governance-loop.md)
  - smallest governed execution loop that the MVP must prove
- [Governance Boundary Matrix](./governance-boundary-matrix.md)
  - ownership split between kernel governance, repo inheritance, repo override, and out-of-scope concerns
- [MVP Stack Vs Target Stack](./mvp-stack-vs-target-stack.md)
  - tracer-bullet implementation posture versus long-term platform direction
- [Compatibility Matrix](./compatibility-matrix.md)
  - support levels for OS, shell, repo host, CI model, and agent product shapes
- [Governed AI Coding Runtime Target Architecture](./governed-ai-coding-runtime-target-architecture.md)
  - full target-state architecture and plane decomposition

## Usage Rule
- If implementation scope is under debate, start with the first three documents before reading the full target architecture.
- If adapter or environment questions arise, pair this index with [docs/specs/agent-adapter-contract-spec.md](../specs/agent-adapter-contract-spec.md) and [docs/specs/repo-profile-spec.md](../specs/repo-profile-spec.md).
