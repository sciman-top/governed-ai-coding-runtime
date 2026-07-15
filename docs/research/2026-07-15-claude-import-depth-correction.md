# Claude import depth correction

## Scope

- checked on: `2026-07-15`
- affected surface: Claude Code memory imports in `CLAUDE.md`
- source: [Claude Code memory - import additional files](https://code.claude.com/docs/en/memory#import-additional-files)
- non-goals: no auth, provider, MCP, permission, account, process, or hosted UI change

## Finding

The current official Claude Code memory documentation states that imported files can recurse up to five hops. The managed Claude global source still said four hops, so the platform-delta statement was stale even though the project wrapper shape (`@AGENTS.md` as the first physical line) remained correct.

## Decision

- bump the content release from `9.56` to `9.57`; project contract `2.0` and coordination schema `2.3` remain unchanged
- change only the Claude import-depth fact from four to five hops
- bump the paired Codex source version without changing Codex semantics so the managed family remains one release
- update all nine target review markers and publish fresh per-repository evidence
- preserve historical `9.56` plans and release evidence as historical records

## Verification and rollback

- verify normalized common-section parity with `python scripts/verify-agent-rule-family.py`
- verify all target contracts with `python scripts/verify-target-project-rules.py --require-all`
- run protected dry-run/apply/zero-drift sync and fresh-process loading probes before fixed-order gates
- rollback only the `9.57` source, manifest, coordination, target markers, and their evidence; restore managed copies from the sync backup if apply has occurred
