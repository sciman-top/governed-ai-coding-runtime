# Reference Basis Matrix

## Goal
- 给 `governed-ai-coding-runtime` 一个 repo 内可审计的“板块 -> 必查参考 -> 采用方式”矩阵。
- 回答两个持续出现的问题：
  1. `D:\CODE\external\ai-coding-runtime-references` 现在还要不要增补/删减？
  2. 本仓哪些代码或文档板块在改动时必须先看哪些参考？

## Add / Remove Decision
- `立即删减`: `none`
- `当前结论`: 现有本地参考 shelf 已覆盖本仓当前主线需要的宿主、协议、浏览器自动化、CLI host、plugin/action、agent-runtime 关键面，不需要为这轮治理升级再强制新增 clone。
- `允许的后续增补条件`:
  - 本仓真的开始实现 GitHub Actions 深层 runner/runtime 语义，而不是只写 workflow 级 preflight
  - 本仓真的开始实现 VS Code / JetBrains / desktop-only host surface，而不是维持 host-family compatibility 文档层
  - 本仓真的把 policy engine、memory runtime、computer-use host 作为主动实现面，而不只是 research/boundary
- `未来优先归档候选`: 仍沿用当前 external shelf 结论，不新增删除压力；先 keep，再按实际长期无洞见证据归档。

## Machine-Readable Source
- Policy: [Reference Basis Policy](../architecture/reference-basis-policy.json)
- Catalog: [Reference Basis Catalog](./reference-basis-catalog.json)
- Existing shelf entrypoints:
  - [External Reference Repo One-Page Overview](./external-reference-repo-one-page-overview.md)
  - [External Reference Repo Tiering](./external-reference-repo-tiering.md)
  - [External Reference Repo Index](./external-reference-repos-index.md)

## Surface Matrix
| Surface | Primary repo areas | Must-review local references | Reuse rule |
| --- | --- | --- | --- |
| Host family and adapter boundaries | `docs/architecture/*host*`, `docs/product/codex*`, `docs/product/host-feedback-loop*`, `scripts/verify-current-source-compatibility.py`, `scripts/evaluate-runtime-evolution.py` | `openai-codex`, `openai-agents-python`, `openai-agents-js`, `anthropic-claude-code`, `github-copilot-cli`, `google-antigravity-cli` | 借语义、边界、配置/approval/sandbox 规则；不复刻宿主 UI、模型 loop、原生 memory UX |
| Protocol, MCP, and A2A boundaries | `docs/architecture/current-source-compatibility-policy.json`, `docs/research/runtime-governance-borrowing-matrix.md`, future `mcp` / `a2a` verifiers | `mcp-specification`, `mcp-typescript-sdk`, `mcp-python-sdk`, `github-mcp-server`, `mcp-inspector`, `a2aproject-A2A` | 借协议 vocabulary、tool boundary、inspection workflow；不把协议本身当 governance kernel |
| Browser automation and plugin/skill composition | `scripts/governance/preflight.ps1`, future browser/operator verification surfaces, plugin/skill boundary docs | `microsoft-playwright-cli`, `microsoft-playwright-mcp`, `anthropic-claude-plugins-official` | 借 token-efficient browser CLI、persistent browser MCP、plugin packaging 边界；不把 browser host 变成本仓产品身份 |
| Release gate, preflight, and CI composition | `.github/workflows/*.yml`, `scripts/governance/*.ps1`, `.governed-ai/repo-profile.json`, `scripts/verify-repo.ps1` | `openai-codex`, `anthropic-claude-code-action`, `github-copilot-cli` | 借 release-style automation、host CI/action 边界、repo-profile/gate composition；保持“本地同契约、CI 兜底”，不造平行 gate 体系 |
| Community execution loop and context shaping | `docs/research/runtime-governance-borrowing-matrix.md`, `docs/architecture/capability-portfolio-classifier.json`, repo-map/context artifacts | `aider`, `swe-agent`, `continue`, `openhands`, `hermes-agent`, `langgraph`, `semantic-kernel`, `goose`, `opencode` | 借 repo grounding、trace/eval、memory lifecycle、orchestration vocabulary；不整体迁入 framework/runtime identity |

## Hard Rule
- 改动命中 [Reference Basis Policy](../architecture/reference-basis-policy.json) 里的 guarded surface 时，必须：
  - 在同一 diff 的 `docs/change-evidence/*.md` 中写出 `reference_basis_review`
  - 明确写出命中的 `reference_basis_surface_ids`
  - 明确写出这次实际查阅过的 `required_local_reference_ids_reviewed`
  - 给出 `reference_adoption_decision`
- 只写“参考了官方文档/社区项目”但不点名具体本地 reference id，不算过关。

## Practical Answer
- 当前不建议为这轮工作再删本地参考仓。
- 当前也不强制新增 clone；先把“哪些 surface 必查哪些现有 reference”收口成硬规则，比继续加仓更值钱。
- 未来真的要新增本地 reference repo 时，必须先回答：
  - 它补的是哪个当前 matrix 没覆盖的 surface？
  - 它解决的是哪个重复出现的设计/实现问题？
  - 现有 Tier 1 / Tier 2 为什么不够？
