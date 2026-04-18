# 20260418 Existing Repo Usage Guide

## Purpose
Clarify whether the current runtime can already be used against an external repository such as `D:\OneDrive\CODE\ClassroomToolkit`, and document the exact supported boundary and command flow.

## Basis
- `scripts/attach-target-repo.py`
- `scripts/session-bridge.py`
- `scripts/run-governed-task.py`
- `docs/product/target-repo-attachment-flow.md`
- `D:\OneDrive\CODE\ClassroomToolkit\README.md`
- `D:\OneDrive\CODE\ClassroomToolkit\README.en.md`
- `D:\OneDrive\CODE\ClassroomToolkit\scripts\validation\run-compatibility-preflight.ps1`

## Findings
- `D:\OneDrive\CODE\ClassroomToolkit` exists and is a .NET solution repository.
- The repo already exposes stable build and test commands:
  - `dotnet build ClassroomToolkit.sln -c Debug`
  - `dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug`
- The repo also exposes a contract-style filtered test command through its current documentation and validation scripts.

## Documentation Changes
- added [Use With An Existing Repo](../quickstart/use-with-existing-repo.md)
- updated [Target Repo Attachment Flow](../product/target-repo-attachment-flow.md) with a concrete `ClassroomToolkit` example
- updated [Session Bridge Commands](../product/session-bridge-commands.md) with attached repo gate-plan resolution
- updated [Single-Machine Runtime Quickstart](../quickstart/single-machine-runtime-quickstart.md)
- updated [Multi-Repo Trial Quickstart](../quickstart/multi-repo-trial-quickstart.md)
- updated [docs/README.md](../README.md)
- updated [README.md](../../README.md)
- updated [README.zh-CN.md](../../README.zh-CN.md)
- updated [README.en.md](../../README.en.md)

## Supported Boundary
The current branch baseline already supports:
- repo-local light-pack generation or validation in an external repo
- machine-local runtime-state binding
- attachment posture inspection through `status` and `doctor`
- local session-bridge posture and gate-plan requests that resolve to target repo declared commands
- attached repo declared gate execution through `run-governed-task.py verify-attachment`
- Codex smoke-trial and multi-repo trial surfaces against the attached posture

The current branch baseline does not yet support:
- full runtime-owned real-write Codex execution inside the external target repo
- claiming that the upstream Codex CLI/App UI has been fully replaced or absorbed by this runtime

## Verification
1. `python scripts/attach-target-repo.py --help`
   - exit `0`
2. `python scripts/session-bridge.py --help`
   - exit `0`
3. `python scripts/run-governed-task.py status --help`
   - exit `0`
4. `python scripts/session-bridge.py request-gate --help`
   - exit `0`
5. `python scripts/run-governed-task.py verify-attachment --help`
   - exit `0`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - exit `0`

## Rollback
- revert the new quickstart page and the README/doc index links
- revert the `ClassroomToolkit` example block in the target-repo attachment flow doc
