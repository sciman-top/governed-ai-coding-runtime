# Generic Target-Repo Attachment Blueprint

## Purpose
Define the preferred product shape for attaching `governed-ai-coding-runtime` to many real repositories and many AI coding tools without turning the kernel into a repo-specific script bundle or a replacement chat IDE.

## Product Direction
The runtime should be:

- generic and portable across repositories
- interactive AI-session first
- attach-first, launch-second
- Codex-first, but not Codex-only
- capability-based rather than vendor-bound
- optimized for rapid multi-repo trial feedback

The already-landed single-machine runtime remains the local kernel baseline. It is not the final product boundary by itself.

## Default Delivery Shape

```text
target repo
  |
  |  repo-local light pack
  v
+-------------------------------+
| .governed-ai/                 |
| repo-profile                  |
| gate commands                 |
| path/risk policy              |
| adapter preference            |
+---------------+---------------+
                |
                | attach / bind
                v
+---------------+---------------+
| machine-wide governed runtime |
| task state                    |
| approvals                     |
| evidence / replay             |
| verification runner           |
| operator read models          |
+---------------+---------------+
                |
                | session bridge
                v
+---------------+---------------+
| AI session frontend           |
| Codex / Claude Code / other tools |
| native attach or process      |
+-------------------------------+
```

## Three Layers

### 1. Repo-Local Light Pack
This layer lives inside the target repository and should stay declarative.

It should contain:

- repo profile
- gate command mapping
- path scope and risk defaults
- approval defaults
- optional adapter preference
- optional repo-local bootstrap hints

The current concrete attachment directory is `.governed-ai/`, with:
- `repo-profile.json`
- `light-pack.json`

`scripts/attach-target-repo.py` creates or validates this directory. Existing light packs are validated by default and are only regenerated when overwrite is requested.

It should not contain:

- a forked runtime implementation
- duplicated artifact or state logic
- heavyweight service code

### 2. Machine-Wide Runtime Sidecar
This layer is installed once per machine or workspace environment.

It owns:

- task lifecycle
- policy and approval decisions
- evidence, replay, and handoff storage
- verification orchestration
- operator-facing status and inspection surfaces
- adapter registry and compatibility posture

This keeps cross-repo behavior consistent and avoids copying the runtime into every target repository.

### 3. Session Bridge
This layer connects the current AI coding session to the runtime.

It should expose governed actions inside the active session, such as:

- start or bind a governed task
- show repo posture
- request approval
- run quick gate
- run full gate
- inspect evidence or status

The session bridge is part of the product core. Plain batch CLI is not enough as the primary user experience.

## Attach-First, Launch-Second

### Attach Mode
Default path.

The user keeps using an upstream AI tool such as Codex CLI/App. The runtime attaches to the active repository and current session posture, then exposes governed controls without forcing the user into a replacement shell.

Best when:

- the upstream tool supports tool bridges, MCP, app-server style hooks, or structured session integration
- fast experimentation across many repositories matters
- the user already has a preferred AI coding workflow

### Launch Mode
Fallback path.

The runtime becomes the session entrypoint and launches or bridges an upstream AI tool when attach is unavailable or too weak.

Best when:

- the upstream tool only exposes a process boundary
- session attach is unavailable
- automation or replay needs a stable launch contract

Attach mode should remain the preferred product posture. Launch mode exists for compatibility and recovery.

## Adapter Capability Tiers

### Tier 1: Native Attach
Strongest integration.

Expected capabilities:

- governed actions callable inside the live session
- structured tool or event visibility
- workspace binding
- resumable session identity
- evidence export richer than stdout

### Tier 2: Process Bridge
Medium integration.

Expected capabilities:

- runtime launches the tool
- stdout or stderr capture
- exit status capture
- changed file or diff recovery
- gate and evidence orchestration after execution

### Tier 3: Manual Handoff / Advisory
Weakest integration.

Expected capabilities:

- repo posture and approval rules still apply
- verification, evidence, and handoff still run
- unsupported guarantees degrade explicitly

Unknown AI tools should still fit one of these tiers. The kernel should never pretend a weak integration has strong governance guarantees.

## Target-Repo Onboarding Flow

1. Detect target repository root.
2. Generate or validate the repo-local light pack.
3. Bind the repo to the machine-wide runtime.
4. Detect compatible adapters and choose a preferred bridge mode.
5. Start or attach a governed task inside the active AI session.
6. Persist evidence and gate results outside the target repo's core source tree.
7. Feed onboarding and execution outcomes back into trial evidence.

## State Placement Rules

### Repo-local
Keep only what must travel with the repository:

- repo profile
- repo-specific policies
- repo-local attach metadata

### Machine-local
Keep mutable runtime state outside the target repository:

- task store
- approvals
- artifacts
- replay bundles
- operator snapshots

This split keeps repository onboarding lightweight and portable while preserving durable runtime behavior.

## Trial-Driven Evolution
The product should evolve through real usage across multiple repositories, not by guessing universal abstractions up front.

Therefore the runtime should first-class the ability to record:

- target repo identity
- adapter tier used
- unsupported capabilities
- approval friction points
- gate failures
- replay quality
- follow-up onboarding fixes

These become product evidence, not informal notes.

## Minimum Acceptance For This Blueprint
The blueprint is considered implemented only when all of the following are true together:

- a new target repo can be attached through a lightweight repo-local pack
- the runtime can bind that repo without copying the kernel into it
- an AI session can use governed actions interactively
- at least one direct Codex path exists
- at least one non-Codex adapter posture is modeled honestly
- multi-repo trial feedback is captured as structured evidence
