# 2026-04-19 混合终态可执行缺口深度审查

## 审查对象
- 审查对象是当前工作区基线，而不是某个历史提交点。
- 审查目标不是重新否定 `GAP-035` 到 `GAP-044` 的已落地成果，而是明确“还差什么才可以声称达到完整混合终态”。
- 终态基线主要来自：
  - `README.md`
  - `docs/architecture/hybrid-final-state-master-outline.md`
  - `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
  - `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
  - `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
  - `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
  - `docs/reviews/2026-04-18-hybrid-final-state-and-plan-reconciliation.md`

## 审查方法
- 静态对照：`docs/`、`schemas/`、`packages/contracts/`、`scripts/`、`tests/`
- 动态验证：
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - `python scripts/run-codex-adapter-trial.py --repo-id python-service --task-id task-codex-trial --binding-id binding-python-service`
  - `python scripts/run-multi-repo-trial.py`
  - `python scripts/session-bridge.py --help`

## 结论
- 仓库方向正确，且“混合终态第一版产品化边界”已经成立。
- 当前基线已经具备：repo attachment、attachment-aware verification、first attached write loop、session bridge 的 write/evidence/handoff 命令面、PolicyDecision contract、adapter posture contract、profile-based multi-repo trial model。
- 但当前仍不能宣称项目达到“完整混合终态”。
- 阻断原因不是基础内核失效，而是关键能力仍停留在 contract、smoke、projection、profile-based summary 或 fallback 层。
- 结论口径：还存在 `7` 个阻断级缺口和 `3` 个硬化级缺口。

## 阻断级缺口

### HFG-001 外部目标仓真实高风险写入还不是 live-host-backed runtime-owned 宿主执行链
- 当前证据：
  - `README.md` 明确写明“外部目标仓中的真实高风险写入仍未接成完整 runtime-owned Codex 执行链”。
  - `docs/quickstart/use-with-existing-repo.md` 明确写明当前还没有“fully runtime-owned direct Codex coding path for real high-risk writes”。
  - `docs/change-evidence/20260418-interactive-session-productization-closeout.md` 明确写明当前 Codex smoke trial 仍是 safe-mode wiring proof。
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py` 与 `scripts/session-bridge.py` 已经提供 `write_request` / `write_approve` / `write_execute` / `write_status`。
- 现状判断：
  - 当前已经存在通过 session bridge 暴露的 runtime-owned attached write flow，所以缺口不是“完全没有 runtime-owned write chain”。
  - 当前真正未闭环的是：这条写链还没有和真实宿主会话的 live adapter/session/continuation identity 绑定，也还没有在真实 attached external repo 中证明 medium/high-risk write 的完整宿主内闭环。
- 可执行补齐动作：
  1. 把现有 bridge write flow 绑定真实 adapter/session/continuation identity，而不是只保留 local runtime refs。
  2. 让真实 attached write execution 产出可追到同一 task 的 approval ref、artifact ref、handoff ref、replay ref。
  3. 增加 attached external repo 端到端测试：`attach -> request medium write -> approve -> execute -> verify -> handoff -> replay`。
  4. 保持 deny/escalate/allow fail-closed 语义，不因 live path 接入而退回到 smoke-only 证明。
- 完成标准：
  - 在真实 attached repo 中，一次 medium/high-risk write 能够从受治理的宿主会话面发起、暂停、审批、恢复、执行，并产出同一 task 下的 evidence/handoff/replay。
- 主要依据：
  - `README.md`
  - `docs/quickstart/use-with-existing-repo.md`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - `scripts/session-bridge.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py`

### HFG-002 Session bridge 已越过查询面，但 gate execution 与 live-host continuation 仍未闭环
- 当前证据：
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py` 已实现 `inspect_evidence`、`inspect_handoff`、`write_request`、`write_approve`、`write_execute`、`write_status`，并返回 stable execution ids。
  - `scripts/session-bridge.py` 已暴露 `inspect-evidence`、`inspect-handoff`、`write-request`、`write-approve`、`write-execute`、`write-status` 等本地入口。
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py` 对 `run_quick_gate` / `run_full_gate` 仍只返回 verification plan，而不是 runtime-managed gate execution lifecycle。
- 现状判断：
  - 当前 bridge 已经不是纯 posture/probe 面，而是有一条真实的 local runtime-owned write/evidence/handoff surface。
  - 当前真正未闭环的是：gate path 仍是 plan-only，且 bridge 结果还没有绑定真实 live host continuation identity，所以它还不是“完整宿主内治理操作总线”。
- 可执行补齐动作：
  1. 将 `run_quick_gate` / `run_full_gate` 从 plan request 提升为 runtime-managed execution lifecycle。
  2. 把 gate、write、approval、evidence、handoff 的 execution/continuation identity 统一到同一 bridge result model。
  3. 把 live host 的 session identity / continuation identity 接入 bridge 结果，而不是停留在 local-only command ids。
  4. 继续保留已有的 evidence/handoff 查询能力，并将其挂到统一 read model 上而不是散落在局部 CLI 行为上。
- 完成标准：
  - bridge 可在同一命令面中完成 posture、runtime-managed gate execution、write governance、approval continuation、evidence query、handoff query，并保留稳定的 execution/continuation identity。
- 主要依据：
  - `docs/product/session-bridge-commands.md`
  - `scripts/session-bridge.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - `docs/change-evidence/20260418-local-session-bridge-entrypoint.md`

### HFG-003 Codex direct adapter 仍是能力声明与 safe smoke，不是 live attach/runtime ingestion
- 当前证据：
  - `README.md` 已明确说明 direct Codex adapter 目前只是 honest smoke-trial / posture / evidence wiring。
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py` 主要做 capability classification、normalized evidence event recording、trial result assembly。
  - `scripts/run-codex-adapter-trial.py` 只输出 deterministic JSON，不与真实 Codex 会话建立绑定。
  - `docs/product/codex-direct-adapter.md` 明确写明 trial 默认 safe-mode，不要求真实高风险写入。
- 现状判断：
  - 现在的“direct adapter”更准确地说是“direct-adapter-shaped contract surface”。
  - 缺的不是文档，而是 live attach、resume、structured event ingestion、structured evidence export reader。
- 可执行补齐动作：
  1. 与真实 Codex CLI/App capability surface 做握手或探测，而不是用 CLI flags 人工声明。
  2. 接入真实 session id / resume id / continuation model。
  3. 从真实事件源读取 tool call、diff、gate run、approval interruption，而不是构造 deterministic refs。
  4. 增加 live Codex adapter E2E fixture，验证 evidence timeline 与 delivery handoff 能从真实会话中生成。
- 完成标准：
  - 至少一个真实 Codex path 可从 live session 中生成 runtime-owned task/session/evidence linkage，而不是 safe-mode static refs。
- 主要依据：
  - `README.md`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `scripts/run-codex-adapter-trial.py`
  - `docs/product/codex-direct-adapter.md`
  - `docs/change-evidence/20260418-codex-session-evidence-mapping.md`

### HFG-004 Multi-repo trial 仍是 profile-based summary，不是 attached external repos 的真实试运行闭环
- 当前证据：
  - `scripts/run-multi-repo-trial.py` 的描述就是 “profile-based multi-repo trial summary”。
  - 默认输入直接来自 `schemas/examples/repo-profile/*.json`。
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py` 生成的 `attachment_posture` 固定是 `profile_validated`，artifact refs 也是推导出来的 deterministic refs。
  - `docs/change-evidence/20260418-interactive-session-productization-closeout.md` 明确写明 current multi-repo runner 仍是 profile-based，不会 attach external repositories。
- 现状判断：
  - 当前 multi-repo loop 更像“trial record schema + sample runner”，不是“真实多仓接入与反馈循环”。
  - 因此它还不能承担终态里的 onboarding feedback engine。
- 可执行补齐动作：
  1. 让 multi-repo runner 接受 attachment roots，而不是 repo-profile paths。
  2. 每个 repo 实际执行 `attach -> doctor/status -> request gate -> verify-attachment -> optional write probe -> evidence aggregation`。
  3. trial record 的 `gate_failures`、`approval_friction`、`replay_quality` 必须来自真实运行结果，而不是默认值。
  4. 至少验证两个真实外部仓，不允许靠 sample profile 自证完成。
- 完成标准：
  - 两个以上真实 attached repos 可以在不改 kernel 的前提下跑完整 onboarding/trial loop，并产出差异化 follow-ups。
- 主要依据：
  - `scripts/run-multi-repo-trial.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py`
  - `docs/quickstart/multi-repo-trial-quickstart.md`
  - `docs/change-evidence/20260418-interactive-session-productization-closeout.md`

### HFG-005 Adapter framework 仍是 posture/classification helper，不是可执行 registry
- 当前证据：
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py` 文件头直接写明是 “Minimal adapter capability helpers for launch-second fallback.”
  - 当前能力主要是 `resolve_launch_fallback(...)`、`build_adapter_contract(...)`、`project_codex_profile_to_adapter_contract(...)`。
  - `docs/change-evidence/20260418-launch-second-fallback.md` 明确写明这是 minimal launch-second helper，不是 full adapter registry。
- 现状判断：
  - 当前 registry 更像 type/contract projector，不是 runtime adapter manager。
  - 它还没有 provider discovery、capability probing、adapter selection state、execution delegation、session continuation binding。
- 可执行补齐动作：
  1. 引入 adapter registration/discovery 机制。
  2. 把 capability probe 变成运行时行为，而不是手工参数。
  3. 为 native_attach / process_bridge / manual_handoff 提供统一执行接口，而不是只提供 posture 分类。
  4. 把 Codex 和至少一个非 Codex adapter 接到同一执行接口上。
- 完成标准：
  - runtime 能按 attached repo + host capability 自动决定 adapter，并通过统一接口驱动命令、事件采集和 degrade。
- 主要依据：
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
  - `docs/change-evidence/20260418-launch-second-fallback.md`

### HFG-006 Governed execution 覆盖面仍过窄，只覆盖 first file-write loop
- 当前证据：
  - 终态 capability boundary 明确要求 governed shell、file、git、package-manager、helper-tool execution。
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py` 当前只支持 `write_file` 与 `append_file`。
  - 当前没有 attached repo 下的 governed shell/git/package-manager/tool execution 统一路径。
- 现状判断：
  - 当前有“第一条受控写回路”，但还没有“终态治理执行面”。
  - 这会导致实际 AI coding 高频动作仍游离在 runtime-owned execution 之外。
- 可执行补齐动作：
  1. 把 tool contract 与 risk tier 映射扩展到 shell / git / package-manager / helper tools。
  2. 统一 approval、rollback、artifact、evidence、handoff 记录模型。
  3. 为每类执行引入最小 one happy path + one denied path + one escalated path 测试。
  4. 先从 `git status` / `git diff` / dependency install dry-run / shell command allowlist 开始，不要一次做全。
- 完成标准：
  - session/adapter 进入 runtime 后，至少 shell、git、file 三类动作都能走相同治理与证据闭环。
- 主要依据：
  - `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py`
  - `scripts/run-governed-task.py`

### HFG-007 Machine-local sidecar placement 还没有变成 end-to-end 一等公民
- 当前证据：
  - `scripts/run-governed-task.py` 仍把 `RUNTIME_ROOT`、`TASK_ROOT`、`ARTIFACT_ROOT`、`REPLAY_ROOT` 固定在 repo-root `.runtime/` 下。
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/workspace.py` 默认 workspace 前缀仍是相对路径 `.governed-workspaces/`。
  - 迁移矩阵中对 workspace/binding root 的最终要求是 machine-local，而不是隐式 repo-root。
- 现状判断：
  - attachment path 已经允许传 machine-local runtime state root，但核心自运行入口仍大量默认 repo-root state。
  - 这说明终态中的 machine-local sidecar 还不是 end-to-end substrate，只是 attached flow 的局部能力。
- 可执行补齐动作：
  1. 引入统一 runtime root config，对 tasks/artifacts/replay/workspaces 一并生效。
  2. 让 self-runtime 与 attached-runtime 共享同一 machine-local state placement model。
  3. 为 state root migration 提供向后兼容与回滚脚本。
  4. 增加测试覆盖：repo-root default、machine-local configured、migration rollback。
- 完成标准：
  - 无论是 self-runtime 还是 attached repo，durable state 与 workspace root 都不再依赖 repo-root 隐式相对路径。
- 主要依据：
  - `scripts/run-governed-task.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/workspace.py`
  - `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`

## 硬化级缺口

### HFG-H1 Operator / control-plane 还缺 attachment-scoped evidence、approval、handoff、replay 查询面
- 当前证据：
  - `inspect_evidence` 与 `inspect_handoff` 已在 session bridge 中落地，但它们还是 task-local read surface，不是 attachment-scoped aggregated operator query surface。
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py` 目前仍是 local HTML renderer，核心内容主要是 maintenance + tasks。
- 可执行补齐动作：
  1. 在现有 bridge read commands 之上增加 attachment 维度的 approvals、evidence、handoff、replay 聚合查询。
  2. 给 operator surface 增加 attachment 维度的 approvals、evidence、handoff、replay 视图。
  3. 让 attached write loop 的审批记录和 evidence refs 可从统一 control-plane read model 查询，而不是只依赖单 task 逐个查看。

### HFG-H2 Local/CI same-contract parity 目前只证明到 verifier boundary，没有证明到 session/adapter runtime readers
- 当前证据：
  - `docs/change-evidence/20260418-local-ci-same-contract-verification.md` 已明确写明：当前只对齐到了 verifier boundary，还没有证明每个 future adapter/session bridge 都消费了新 shape。
- 可执行补齐动作：
  1. 把 execution context 相关字段接入真实 runtime readers。
  2. 在 CI 中增加 session bridge / adapter / attachment verification 路径的 contract tests。
  3. 防止出现“spec/schema 已更新，但 runtime 入口没读到”的隐性漂移。

### HFG-H3 Attachment doctor/status 仍是 posture-only，还没有 remediation enforcement
- 当前证据：
  - `docs/change-evidence/20260418-attachment-posture-status-doctor.md` 已明确写明 doctor 目前只报告 posture，不执行 remediation policy。
- 可执行补齐动作：
  1. 对 missing/invalid/stale binding 定义 remediation policy。
  2. 在 doctor 或 session bridge 中执行 fail-closed 或 guided remediation。
  3. 给 remediation 增加 evidence 与 rollback 记录。

## 建议收敛顺序

### Phase A 先闭环真实治理执行链
- 处理：`HFG-001`、`HFG-002`、`HFG-006`
- 原因：
  - 这三项决定项目能不能从“合同+探针”升级为“真实 runtime-owned execution surface”。

### Phase B 再补 live host adapter
- 处理：`HFG-003`、`HFG-005`
- 原因：
  - 只有先把执行面补齐，真实 Codex/native/process bridge attach 才不会接到一个只有 posture 的空壳。

### Phase C 再做真实多仓与 sidecar 收口
- 处理：`HFG-004`、`HFG-007`
- 原因：
  - 多仓与 machine-local sidecar 是终态完整性问题，但必须建立在真实宿主执行链已经跑通之上。

### Phase D 最后做控制面与 CI 硬化
- 处理：`HFG-H1`、`HFG-H2`、`HFG-H3`
- 原因：
  - 这些问题不否定方向，但会影响终态长期稳定性与可运维性。

## 不应误判为缺口的部分
- durable task/evidence/verification/handoff/replay kernel 本身没有被本次审查否定。
- build/test/contract/doctor 门禁当前是可执行、可通过的。
- attachment-aware verification 与 first attached write loop 已经形成真实起点，不应回退成“只有 docs/spec”。

## 审查口径
- 正确口径应是：
  - “当前仓库已经完成混合终态第一版产品化边界”
  - “当前仓库距离完整混合终态，还差外部仓真实写入、完整 session bridge、live adapter ingestion、真实 multi-repo loop、end-to-end machine-local sidecar 等阻断项”
- 不正确口径应是：
  - “已经完整完成混合终态”
  - “Codex 已被 runtime 在外部仓完整接管用于真实高风险写入”
  - “multi-repo onboarding 已经通过真实 attached repos 闭环验证”
