# 20260711 Agent Rule Cross-Repo CI

## Change Identity

- `status`: `control_pr_verified_merge_pending`
- 风险等级：中；变更 GitHub Actions、目标仓规则契约 Schema、审计脚本并发布 9 个目标仓规则 PR；不新增跨仓密钥、不修改 provider/auth，也不替代产品门禁。
- 当前落点：9 个目标 PR 已合并，目标仓 `main` 上的规则契约 workflow 全部通过；控制仓 PR 聚合认证已通过，尚待合并并复核 `main`。
- 目标归宿：`target-local proof + control aggregate certification`，让项目规则、Claude wrapper、CI 模板和控制清单形成确定性闭环。

## Pre-Change Review

### pre_change_review

- 先联合检查控制仓规则清单、Schema、verifier、现有 GitHub workflows、9 仓远端与现有 CI，再决定新增独立规则 workflow；未把规则检查塞入不同产品技术栈的既有 jobs。

### control_repo_manifest_and_rule_sources

- 审查 `rules/target-project-rule-coordination.json`、`rules/manifest.json`、全局规则源和 `AGENTS.md`；保留 `rule_release=9.55 / project_contract_version=2.0`，仅将 coordination schema 升为 `2.1` 并新增独立 `ci_contract=2.0`。

### user_level_deployed_rule_files

- `~/.codex/AGENTS.md` 与 `~/.claude/CLAUDE.md` 不在本切片变更面；最终仍以 global sync `changed=0 / blocked=0` 证明未产生全局副本漂移。

### repo_local_gate_scripts_and_ci

- 审查控制仓 `.github/workflows/verify.yml`、`runtime-evolution.yml` 和 9 仓现有 workflows；新增 `.github/workflows/agent-rule-coordination.yml`，不修改目标仓产品 CI。托管运行发现 `skills-manager` 存在无 `.gitmodules` 的 gitlink，CI contract `2.1` 在 runner 临时工作树补齐 cleanup 元数据，不修改目标仓真实子模块配置。
- 新增 `scripts/export-target-rule-ci-matrix.py`，并扩展 `scripts/verify-target-project-rules.py` 的 CI checkout override、GitHub repository、workflow hash和项目规则引用检查。

### repo_local_repo_profile

- `.governed-ai/repo-profile.json` 不变；新 workflow 只需 `contents: read`，不读取或新增 secret、provider、MCP、sandbox 或 credential profile。

### repo_local_readme_and_operator_docs

- 同步更新 `README.md`、`README.zh-CN.md`、`README.en.md`、`docs/README.md` 与 `docs/quickstart/use-with-existing-repo*.md`，保持双语接入、N/A、回滚和“不替代产品门禁”口径一致。

### current_official_tool_loading_docs

- Codex/Claude 规则加载仍沿用 2026-07-10 官方复核结论；本切片新增复核 GitHub Actions matrix、multiple repository checkout、workflow reuse 与 action pinning 官方文档，访问日期 2026-07-11。

### drift-integration decision

- 选择目标仓本地 workflow 加控制仓动态 matrix 两层；拒绝目标仓引用可变远程脚本、要求跨仓 PAT、把目标正文复制回控制仓或自动纳管非目标目录。

## Reference Review

### reference_required_review

- 本轮触及 release gate、workflow、Schema 与 source verifier，必须同时提供 GitHub 官方文档、`actions/checkout` 主项目、本机真实 9 仓和现有控制脚本证据。

### changed_surface_paths

- `.github/workflows/agent-rule-coordination.yml`
- `rules/target-project-rule-coordination.json`
- `rules/templates/github/agent-rule-contract.yml`
- `schemas/jsonschema/target-project-rule-coordination.schema.json`
- `schemas/catalog/schema-catalog.yaml`
- `scripts/export-target-rule-ci-matrix.py`
- `scripts/verify-target-project-rules.py`
- `tests/runtime/test_target_rule_ci.py`
- `tests/runtime/test_verify_target_project_rules.py`
- 9 仓各自的 `AGENTS.md`、`.github/workflows/agent-rule-contract.yml` 与 `20260711-agent-rule-ci.md`

### official_sources_reviewed

- GitHub Docs：[matrix jobs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations)、[reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)、[security hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)，访问日期 2026-07-11。
- `actions/checkout` 官方仓：[multiple repositories](https://github.com/actions/checkout#checkout-multiple-repos-side-by-side)；本机 `git ls-remote` 将 `v4` 解析到完整提交 `34e114876b0b11c390a56381ad16ebd13914f8d5`。
- OpenAI Codex [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference#configtoml) 将 `model_auto_compact_token_limit` 定义为自动压缩触发阈值，未设置时使用模型默认值；官方未规定固定比例。控制仓因此保留显式的提前压缩偏好，仅把非正值、达到/超过上下文和晚于 90% 的阈值作为硬失败。

### primary_references_reviewed

- 继续参考 `openai-codex`、`anthropic-claude-code`、`anthropic-claude-code-action` 与 `github-copilot-cli` 的宿主/CI 边界；它们不取得本仓规则正文所有权。

### local_runtime_evidence_reviewed

- 9 个目标仓都有可访问 GitHub origin；其中 7 个公开、`github-toolkit` 与 `qq-astrbot-stack` 为私有。`local-ai-dev-orchestrator -> sciman-top/local-ai-runtime`、`qq-codex-bot -> sciman-top/qq-astrbot-stack` 必须显式映射，不能从目录名猜测。
- RED 先证明 Schema、workspace override、workflow hash、matrix exporter、aggregate workflow、错误契约拒绝和 action SHA pinning 缺失；GREEN 后由实际脚本执行与 9 仓审计收口。

### source_decision

- 采纳目标本地门禁、显式 matrix、7 个公开仓的 multi-repo checkout、2 个私有仓的 target-local enforcement、完整 action SHA 和 workflow hash；不引入跨仓 PAT，也不采用可变远程脚本或跨仓 reusable workflow 引用。

### reference_basis_review

- changed surface 属于 release-gate-and-ci-boundaries、workflow-governance-and-spec-driven-delivery、host-and-adapter-boundaries；所有外部做法只经机器契约和本机测试采纳。

### reference_basis_surface_ids

- `release-gate-and-ci-boundaries`
- `workflow-governance-and-spec-driven-delivery`
- `host-and-adapter-boundaries`

### required_local_reference_ids_reviewed

- `openai-codex`
- `anthropic-claude-code`
- `anthropic-claude-code-action`
- `github-copilot-cli`

### reference_adoption_decision

- 采用：显式 9 仓 allowlist、matrix fan-out、目标本地规则门禁、只读权限、完整 action SHA、模板 SHA-256 漂移阻断。
- 不采用：自动发现目录、目标正文同步、跨仓 secret/PAT、可变远程脚本、用规则 CI 替代产品门禁。

## Changes

- coordination schema `2.0 -> 2.2`；`rule_release=9.55` 与 `project_contract_version=2.0` 不变。`2.2` 显式记录 `github_visibility / aggregate_mode`。
- CI contract `2.0 -> 2.1`；保留固定 SHA 的 checkout，并兼容无完整 `.gitmodules` 的 gitlink cleanup。
- canonical CI workflow 由 `rules/templates/github/agent-rule-contract.yml` 管理，manifest 固定其 SHA-256。
- 9 仓 workflow 仅在 `AGENTS.md`、`CLAUDE.md` 或自身变化时运行；验证 UTF-8/BOM、预算、结构、契约版本、门禁/证据/回滚、宿主中立和 exact Claude wrapper。
- 控制仓 workflow 从 manifest 动态导出 matrix，逐仓 checkout 并以 `--workspace-root ... --targets ... --require-all` 审计。

## Verification

- TDD RED：新增用例因缺少 `2.1` Schema、workspace override、workflow hash、matrix exporter/aggregate workflow、错误版本拒绝和完整 action SHA 而失败。
- focused GREEN：`python -m unittest tests.runtime.test_verify_target_project_rules tests.runtime.test_target_rule_ci tests.runtime.test_verify_agent_rule_family tests.runtime.test_agent_rule_sync`，`Ran 29 tests`、`OK`。
- target audit：当前 `selected=9 / failed=0 / unavailable=0 / blocking=[]`，9 仓 workflow SHA-256 均为 `634eb76978774b8eaad39fe61172c9f65f5558fcd32ce7f13e98ecfae7214190`。
- workflow static/behavior：canonical embedded Python 的 `2.0 pass / 1.9 fail` 测试通过；PyYAML 解析通过；`actionlint v1.7.12` 对 canonical 与 aggregate workflow 返回 `exit_code=0`。
- target publication：9 个目标 PR 均已合并；各仓 `main` 的 Agent Rule Contract 均成功：
  - `ai-content-delivery-studio`: https://github.com/sciman-top/ai-content-delivery-studio/actions/runs/29110660199
  - `classroom-answer-toolkit`: https://github.com/sciman-top/classroom-answer-toolkit/actions/runs/29110663412
  - `ClassroomToolkit`: https://github.com/sciman-top/ClassroomToolkit/actions/runs/29110666876
  - `github-toolkit`: https://github.com/sciman-top/github-toolkit/actions/runs/29110670585
  - `k12-question-graph`: https://github.com/sciman-top/k12-question-graph/actions/runs/29110674051
  - `local-ai-dev-orchestrator`: https://github.com/sciman-top/local-ai-runtime/actions/runs/29110677700
  - `qq-codex-bot`: https://github.com/sciman-top/qq-astrbot-stack/actions/runs/29110682060
  - `skills-manager`: https://github.com/sciman-top/skills-manager/actions/runs/29110685073
  - `vps-ssh-launcher`: https://github.com/sciman-top/vps-ssh-launcher/actions/runs/29110688699
- product gate split：`vps-ssh-launcher` 的规则字面契约修复后 Windows/Linux 产品 gates 全部通过；`ai-content-delivery-studio`、`ClassroomToolkit`、`skills-manager` 的产品 CI 失败已由其 `main` 历史运行证明为既有基线，并在 PR 评论记录 `reason / alternative_verification / evidence_link / expires_at / recovery_plan`。
- global family/sync：A/C/D common hash 不变；Codex/Claude 用户级副本 `changed=0 / blocked=0`。
- build：`scripts/build-runtime.ps1` 返回 `exit_code=0`，包含新增 exporter/verifier 的 bytecode/import 检查。
- test：`verify-repo.ps1 -Check Runtime` 返回 `exit_code=0`，`101` 个测试文件、`failures=0`、`268.490s`，service parity 与 wrapper drift guard 均通过。
- contract/invariant：`verify-repo.ps1 -Check Contract` 返回 `exit_code=0`，Schema/catalog、9 仓 target audit、同步/family、引用依据与功能实效全部 `OK`。
- hotspot：`doctor-runtime.ps1` 返回 `exit_code=0`，`29` 项检查全部 `OK`。

### Repair Trace

- `issue_id=codex-context-catalog-growth`：本机 Codex `0.144.1` 的 `gpt-5.6-sol` bundled catalog 将有效窗口报告为 `372000`，而用户显式 `model_auto_compact_token_limit=220000`。旧审计把 `220000 / 372000 = 0.5914` 低于建议区间误判为必须改到 `301000`，连带阻断 policy audit 和 governance certification。
- RED：新增 `test_context_window_probe_preserves_explicit_early_compaction_after_catalog_growth`，修复前得到 `status=attention`。
- GREEN：安全门禁改为“正值、早于上下文且不晚于 90%”；低于 75% 记录为 `configured_early_threshold`，不自动改写用户偏好。新增回归、`test_codex_local` 29 项、policy audit 8 项、governance certification 3 项与完整固定门禁全部通过。
- 未修改 `~/.codex/config.toml`，未重启、停止或拉起 Codex/Claude 进程。
- `issue_id=aggregate-skills-manager-checkout-cleanup`：控制仓首次 PR 聚合运行 [29148837996](https://github.com/sciman-top/governed-ai-coding-runtime/actions/runs/29148837996) 中 8 个目标 job 通过，`skills-manager` 在 checkout 的即时 credential cleanup 阶段因 `imports/agent-browser` 缺少 `.gitmodules` URL 失败。新增 RED 断言后，将目标 checkout 改为 `persist-credentials: true`，并在审计后、Post Checkout 前只在 runner 临时副本补齐 gitlink 元数据；`test_target_rule_ci` 6 项和 `actionlint v1.7.12` 通过。
- hosted aggregate：[29148963827](https://github.com/sciman-top/governed-ai-coding-runtime/actions/runs/29148963827) 返回 `success`；matrix 构建成功，7 个公开目标完成 checkout + strict audit，`github-toolkit` 与 `qq-codex-bot` 两个私有目标完成显式边界记录，所有 checkout Post Cleanup 成功。

## N/A Boundary

- `platform_na`：控制仓默认 `GITHUB_TOKEN` 不能跨仓读取两个私有目标。`reason=private repositories and no cross-repository credential by design`；`alternative_verification=repository-local Agent Rule Contract on each private main branch`；`evidence_link=the github-toolkit and qq-codex-bot hosted run URLs above`；`expires_at=2026-08-09`。
- `gate_na`：控制仓既有 `.github/workflows/verify.yml` 在本 PR 运行 [29148837977](https://github.com/sciman-top/governed-ai-coding-runtime/actions/runs/29148837977) 中失败；`reason=the workflow depends on uncommitted host-local .runtime artifacts and host feedback, and the latest five main-branch runs already fail on the same repository-integrity/release-preflight surface`；`alternative_verification=the fresh local fixed-order build/runtime/contract/doctor results recorded above plus the independent agent-rule aggregate workflow`；`evidence_link=https://github.com/sciman-top/governed-ai-coding-runtime/actions/runs/28768144311`；`expires_at=2026-08-09`；`recovery_plan=repair CI fixture isolation and host-evidence platform_na semantics in a separate runtime-governance slice`。
- 目标产品 build/test/contract/hotspot 对纯规则 Markdown/workflow 切片为 `gate_na`；3 个既有失败仓的 PR 评论补齐四字段与 recovery plan，其余可执行产品门禁以实际托管结果收口。

## Rollback

- 控制仓只回滚本证据列出的 Schema、manifest、template、exporter、verifier、tests、docs 与 aggregate workflow。
- 每个目标仓只回滚新增 workflow、本轮 `AGENTS.md` 单行引用和 `20260711-agent-rule-ci.md`；保留 20260710 规则契约以及所有其他用户改动。
- 不回滚或覆盖 `skills-manager/imports/**`、其 audit/MCP/源码测试改动，也不回滚 `vps-ssh-launcher` 的 README、主机脚本、`ssh_tool.py`、测试或 live evidence。
