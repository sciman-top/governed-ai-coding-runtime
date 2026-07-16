# 2026-07-17 Agent Rule Governance v2 Current State

## Scope

- control repository: `D:\CODE\governed-ai-coding-runtime`
- branch: `codex/agent-rule-governance-v2`
- archive boundary: `archive/runtime-v1-20260716` at `876403f`
- product target: static Codex + Claude rule-governance control repository
- excluded: target writes, provider/auth/MCP/account/gateway state, process
  restart, native host acceptance, hosted acceptance, and remote repo rename

## Risk And Rollback

- risk: medium; the migration deletes obsolete active surfaces but preserves
  the exact pre-migration tree in an annotated tag and Git history
- control-repo rollback: revert only the v2 commits
- historical inspection: `git show archive/runtime-v1-20260716:<path>`
- target rollback: N/A because this migration does not modify target worktrees

## Implemented Slices

| Revision | Result |
| --- | --- |
| `c1ecbc6` | Separated target default-branch and workspace audit semantics. |
| `fb7a229` | Added structured multi-state status. |
| `9b00815` | Added the unified `rulesctl` gate entrypoint. |
| `4ed442d` | Added canonical global-rule assembly. |
| `2e4a9d5` | Reduced CI and hooks to rule-governance checks. |
| `b6f829a` | Made repo-local contract the default and target audit explicit. |

## Fresh Evidence Before Product-Truth Rewrite

| Command | Exit | Evidence |
| --- | ---: | --- |
| `python -m unittest tests.runtime.test_rulesctl_gates` | 0 | 5 tests passed. |
| `python scripts/rulesctl.py contract` | 0 | Global family, projection, and matrix passed; target audit was explicitly skipped as a separate mutable-state gate. |
| `python scripts/rulesctl.py contract --include-targets` | 1 | Expected strict failure: 8/9 target default branches passed. |

The failing target was `local-ai-dev-orchestrator` at local `origin/main`
revision `71eb1355ae96a8b7bf2ec0e855536d5190b6e94e` with:

- `na_contract_fields_missing:reason,alternative_verification,evidence_link,expires_at,recovery_condition`
- `project_contract_token_missing:.github/workflows/agent-rule-contract.yml`

This external result is intentionally not repaired from the control
repository and must remain visible through `rulesctl status` / `audit`.

## Current Completion Boundary

- repo-side implementation: product-truth docs, pruning, and multi-axis review
  are complete in the working tree; fresh final gates and commit remain
- target default branches: fresh `8/9`; only `local-ai-dev-orchestrator` fails
  at revision `71eb1355ae96a8b7bf2ec0e855536d5190b6e94e`
- target workspaces: fresh `2/9`; six targets still review global release 9.56,
  `local-ai-dev-orchestrator` has the two default-branch findings, and its
  worktree is also observed dirty
- `host_loaded`: `unknown`; no fresh native probe in this migration slice
- `hosted_accepted`: `unknown`; no hosted acceptance probe in scope
- remote repository rename: intentionally deferred as an external release
  action

## Multi-Axis Review

Reviewed retained tests before implementation, then correctness, readability,
architecture, security, and performance across the 49-file final tracked tree.

Resolved Required findings:

1. Replaced a retained test's structural dependency on deleted
   `verify-repo.ps1` with a behavior test of `rulesctl contract
   --include-targets` against an immutable temporary Git target.
2. Reclassified default target separation from false `platform_na` to the
   explicit `separate_mutable_state` boundary.
3. Made the PowerShell sync wrapper resolve its Python script and relative
   manifest from the repository when invoked from another current directory;
   added a regression test.
4. Clarified that local audits preserve existing target worktrees while
   aggregate CI uses isolated checkouts and never writes back.

No Critical finding remains. No dependency was added. The largest retained
implementation file is 835 lines, below the 1000-line review signal; its scope
is the single target-contract verifier. Target enumeration is bounded by the
explicit nine-entry allowlist and uses argument arrays rather than shell-built
commands.

## N/A Record

- kind: `platform_na`
- reason: native and hosted acceptance require separately authorized host
  execution and are not proven by repository files
- alternative_verification: canonical assembly, global projection dry-run,
  immutable Git-ref audit, repo-local fixed gates, and CI contracts
- evidence_link: this file and `docs/research/agent-rule-governance-v2-sources.md`
- expires_at: `2026-10-15`
- recovery_condition: an authorized release task provides fresh Codex, Claude,
  and hosted probes for the selected revision

## Final Repo-Local Evidence

- evidence time: `2026-07-17T01:35:39+08:00`
- final tracked tree: 49 files

| Command / check | Exit | Result |
| --- | ---: | --- |
| `python scripts/rulesctl.py verify` | 0 | Fixed order passed; 52 tests passed; canonical outputs current; global projection zero drift; hotspot `forbidden_count=0`. |
| PowerShell sync wrapper invoked from `D:\CODE` | 0 | Resolved repo paths outside repo CWD; `changed_count=0`, `blocked_count=0`. |
| `python scripts/rulesctl.py status` | 1 | Expected strict aggregate: source/global pass, default branch `8/9`, workspace `2/9`, host states unknown. |
| `python scripts/rulesctl.py audit --state default` | 1 | Expected strict external result: 9 selected, 1 failed, 0 unavailable; exact failing revision/findings recorded above. |
| `git diff --cached --check` | 0 | No whitespace errors. |
| tracked Markdown link check | 0 | 20 files, zero broken local links. |
| final-tree secret pattern scan | 0 | Zero private-key/password/API-key/bearer assignment patterns. |
| exact Claude wrapper check | 0 | 12 bytes, hex `404147454e54532e6d640d0a`, no BOM. |

## Acceptance Boundary

Repository-side governance v2 is verified. The external fleet is not globally
accepted: default branches remain `8/9`, workspaces remain `2/9`, and both
`host_loaded` and `hosted_accepted` remain `unknown`. No process restart,
provider/auth mutation, target write, remote rename, hosted probe, merge to
`main`, or release tag is included in this closeout.
