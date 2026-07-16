# Codex + Claude Agent Rule Governance

Static, service-free governance for OpenAI Codex and Anthropic Claude Code
rules. 中文详见 [README.zh-CN.md](README.zh-CN.md); English details are in
[README.en.md](README.en.md).

## Product Boundary / 产品边界

This repository owns global rule sources, host-specific deltas, explicit
target registration, deterministic validation, protected global projection,
cross-repository CI coordination, and release evidence.

本仓不再是 AI coding runtime。它不提供数据库、API、UI、daemon、模型调用、
provider/auth/session/gateway 管理或多代理编排。目标仓始终拥有自己的项目规则、
真实命令、产品门禁、证据与回滚。

The pre-migration runtime tree is preserved at
`archive/runtime-v1-20260716`; it is history, not an active compatibility
surface.

## Quick Start / 快速入口

```powershell
python scripts/rulesctl.py status
python scripts/rulesctl.py verify
```

- `status` reports source, global projection, target default branches, and
  target workspaces separately. It can fail when an external target drifts.
- `verify` is the reproducible control-repository gate and runs
  `build -> test -> contract -> hotspot`.
- `verify --include-targets` explicitly adds the mutable nine-target audit.

## Architecture / 架构

```text
canonical global sources -> deterministic Codex/Claude outputs
                         -> protected user-profile projection

explicit target registry -> immutable default-branch audit
                         -> workspace observation
                         -> per-target CI contract
```

The design deliberately separates four evidence states:

| State | Meaning |
| --- | --- |
| `workspace_effective` | Current local target worktree satisfies the contract. |
| `default_branch_effective` | Configured immutable/default Git revision satisfies the contract. |
| `host_loaded` | A fresh native Codex or Claude probe loaded the intended rule chain. |
| `hosted_accepted` | A hosted surface separately accepted the intended rule chain. |

No state implies another. Control-repo health does not erase target failures,
and local file equality does not prove hosted acceptance.

## Main Commands / 主要命令

```powershell
python scripts/rulesctl.py build
python scripts/rulesctl.py test
python scripts/rulesctl.py contract
python scripts/rulesctl.py hotspot
python scripts/rulesctl.py verify
python scripts/rulesctl.py audit --state default
python scripts/rulesctl.py audit --state workspace
python scripts/rulesctl.py sync --check
python scripts/rulesctl.py matrix
```

`sync --apply` writes managed user-level global files and is intentionally
separate from verification. It never distributes target-repository rule
bodies.

## Why This End State / 为什么采用此终态

- It matches native ownership: Codex loads `AGENTS.md`; Claude Code loads
  `CLAUDE.md` and can import `@AGENTS.md`.
- It keeps target facts in target repositories instead of creating a second
  central source of truth.
- Markdown, JSON/JSON Schema, Python, PowerShell, Git, and GitHub Actions cover
  every proven requirement without an always-on service.
- Host-specific loading, trust, settings, permissions, and hooks remain
  explicit adapters rather than a false common abstraction.
- Dry-run, immutable Git-revision audit, atomic projection, backups, and CI
  drift checks provide traceability and rollback with low operational cost.

## Read Next / 继续阅读

- [Documentation index](docs/README.md)
- [Architecture](docs/architecture/agent-rule-governance-v2.md)
- [Rule release runbook](docs/runbooks/agent-rule-release.md)
- [Source basis](docs/research/agent-rule-governance-v2-sources.md)
- [Current migration evidence](docs/change-evidence/20260717-agent-rule-governance-v2-current-state.md)
