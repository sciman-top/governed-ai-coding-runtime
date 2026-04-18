# Apps

Future runtime application entrypoints live here.

## Planned Boundaries
- `control-plane/`: task lifecycle, policy decisions, approvals, and registry APIs.
- `tool-runner/`: governed tool request validation and execution adapters.
- `workflow-worker/`: durable task orchestration once workflow runtime is selected.
- `console-web/`: future approval and evidence inspection UI.

## Current Status
No runtime services are implemented yet.

The current active stage remains `Full Runtime / GAP-024`, but it is still CLI-first and contract-layer heavy:
- `scripts/` and `packages/contracts/` are the live execution substrate today
- `apps/` stays reserved for later service-shaped boundaries once the runtime path and read models stabilize
