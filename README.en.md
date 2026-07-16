# Codex + Claude Agent Rule Governance

## Decision

The optimal end state for this product is a static, service-free control
repository for OpenAI Codex and Anthropic Claude Code rules. It is not a
general AI coding runtime.

Markdown, JSON/JSON Schema, Python, PowerShell, Git, and GitHub Actions cover
the proven requirements. A database, web UI, HTTP API, daemon, message broker,
model execution layer, or rewrite in another language would add operational
cost without improving native rule loading or repository ownership.

## Ownership

- This repository owns canonical global sources, host deltas, explicit target
  registration, deterministic validation, protected projection, aggregate CI,
  and release evidence.
- Each target owns its project `AGENTS.md`, thin `CLAUDE.md` wrapper, real
  product commands, gates, evidence, and rollback.
- Local audits do not move, reset, clean, overwrite, or blind-sync existing
  target worktrees. Aggregate CI uses isolated checkouts and never writes back.
- Provider, auth, account, session/history, MCP, gateway, and process control
  are outside the product boundary.

The runtime-era tree remains available at `archive/runtime-v1-20260716` as
history only.

## Use

```powershell
python scripts/rulesctl.py status
python scripts/rulesctl.py verify
```

`status` strictly reports source, global projection, target default branches,
and workspaces. `verify` is the reproducible control-repository gate and runs
`build -> test -> contract -> hotspot`. Add `--include-targets` only when the
mutable nine-target state should participate in the result.

```powershell
python scripts/rulesctl.py audit --state default
python scripts/rulesctl.py audit --state workspace
python scripts/rulesctl.py sync --check
python scripts/rulesctl.py matrix
```

`sync --apply` is a separate persistent operation. It writes only managed
user-level global rules and never distributes target project bodies.

## Evidence States

`workspace_effective`, `default_branch_effective`, `host_loaded`, and
`hosted_accepted` are independent. A healthy control repository does not erase
a target failure, and local file equality does not prove native or hosted
acceptance.

## Why This Architecture

- It follows native host behavior: Codex reads `AGENTS.md`; Claude Code reads
  `CLAUDE.md` and can import `@AGENTS.md`.
- Project facts remain with their owning repositories.
- Host loading, trust, settings, permissions, and hook differences stay
  explicit instead of being hidden behind a false common runtime.
- Immutable Git-revision audits, dry-run, atomic projection, backups,
  rollback, and CI drift checks cover the actual risks with a small footprint.

Continue with the [documentation index](docs/README.md),
[architecture](docs/architecture/agent-rule-governance-v2.md),
[release runbook](docs/runbooks/agent-rule-release.md), and
[source basis](docs/research/agent-rule-governance-v2-sources.md).
