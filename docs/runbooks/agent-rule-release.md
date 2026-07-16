# Agent Rule Release Runbook

## Scope

Use this runbook to release global Codex/Claude rules or coordination-contract
changes. It does not authorize target-repository writes, provider/auth changes,
managed enterprise policy, process restart, or hosted acceptance.

## 1. Establish The Release Boundary

Record:

- selected control-repository revision and branch
- rule release, project contract, and coordination schema versions
- selected target state: `origin/main` default branches or local workspaces
- intended global projection target profile
- rollback commit/tag and evidence file

For the v2 migration, the runtime-era rollback boundary is
`archive/runtime-v1-20260716`.

## 2. Change Canonical Sources

Edit shared/platform fragments under `rules/global/sources/` and the source
manifest. Do not edit generated global outputs as the source of truth.

```powershell
python scripts/build-global-rules.py
python scripts/build-global-rules.py --check
```

If the generated diff contains an unrelated host section or target-specific
fact, stop and repair the source boundary.

## 3. Run Repo-Local Gates

```powershell
python scripts/rulesctl.py verify
```

The fixed order is `build -> test -> contract -> hotspot`. Failure blocks the
release. This command intentionally does not make mutable target state part of
control-repository health.

## 4. Audit Targets Separately

```powershell
python scripts/rulesctl.py audit --state default
python scripts/rulesctl.py audit --state workspace
```

- Default-branch audit is the publishable Git-state view.
- Workspace audit is an operator observation and may differ because of local
  changes or stale refs.
- Do not checkout, reset, clean, stash, or edit target repositories to make an
  aggregate report green.
- Record every target failure; do not reduce `8/9` to a generic success.

## 5. Preview Global Projection

```powershell
python scripts/rulesctl.py sync --check
```

Inspect source/target versions, hashes, planned changes, blocked same-version
drift, and backup destination. Unexpected drift blocks apply.

## 6. Apply Only With Release Authorization

```powershell
python scripts/rulesctl.py sync --apply
python scripts/rulesctl.py sync --check
```

Apply writes only the two user-level global files from `rules/manifest.json`.
It does not write target projects. Preserve the reported backup until native
loading verification is accepted.

## 7. Native And Hosted Verification

Run a fresh native Codex loading probe and a fresh Claude Code loading probe
only when the current task authorizes the host action. Record installed
version, working directory, resolved instruction chain, exit code, and time.

Hosted acceptance is a separate probe. Do not infer it from local files,
local CLI output, or a GitHub Actions result.

## 8. Closeout Evidence

Evidence must include:

- revision and exact commands
- exit codes and meaningful result counts
- control-repository result
- each failing/unavailable target
- `workspace_effective`, `default_branch_effective`, `host_loaded`, and
  `hosted_accepted` as separate fields
- N/A reason, alternative evidence, evidence link, expiry, and recovery
  condition where applicable
- rollback command and backup reference

## Rollback

- Control-repository change: revert only the release commits.
- Global projection: restore the sync backup, align canonical sources to the
  restored version, then rerun `sync --check` and repo-local `verify`.
- Target project: hand off the finding to that repository; its owner reverts
  only its rule/evidence slice.
- Runtime-era recovery: inspect the archive tag; do not silently restore old
  services or entrypoints into the active tree.
