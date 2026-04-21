# 教学式协作与低 Token 治理总设计

## Status
- Proposed and approved in interactive design review on 2026-04-22.
- This document defines a top-level design slice that should later decompose into narrower specs and schemas.

## Goal
在不改变现有 governed task、approval、verification、evidence 主链的前提下，为外层 AI 增加一套可治理、可压缩、可留痕的交互行为设计，使其能够：
- 更早发现任务理解偏差、术语混淆、bug 观察缺口与重复返工信号
- 在任务进行过程中提供短而准的即时教学，而不是依赖长篇解释
- 在显式 token 预算内运行，并在预算压力下做可解释的压缩、降级或停止
- 将相关触发原因、策略选择、预算快照和结果写入 evidence 与 trace，供后续评估和改进

## Why This Change Is Needed
仓库已经具备多项与该方向直接相关的基础能力：
- `docs/specs/clarification-protocol-spec.md` 已把 repeated failure 后的澄清切换 formalize 为 runtime policy。
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py` 已要求 task 具备 `goal / scope / acceptance / budgets`。
- `docs/specs/repo-map-context-shaping-spec.md` 已要求 repo-aware context shaping 保持在显式 token budget 内。
- `docs/specs/evidence-bundle-spec.md` 与 `docs/specs/eval-and-trace-grading-spec.md` 已建立 evidence、trace grading 与 postmortem input 的统一闭环。

但当前仍缺三类正式 contract：
- 缺少针对教学式协作、认知摩擦识别与任务复述策略的正式行为模型。
- 缺少 explanation budget、clarification budget、session compaction 这类低 token 运行策略的统一对象。
- 缺少把这些交互行为接入 evidence、trace 与 metrics 的标准方式。

如果继续只靠 prompt 惯例：
- 跨仓迁移时容易漂移
- 不同 adapter tier 很难保持一致行为
- 很难衡量“解释太多”与“解释不够”的边界
- 也无法通过 postmortem inputs 产生可审查的改进提案

## Non-Goals
- 不做心理诊断，不声称 AI 真正知道用户的内在认知状态。
- 不把系统做成 memory-first personalization platform。
- 不把每轮响应都变成长篇教学内容。
- 不替代现有 task lifecycle、approval、verification gate order 或 delivery handoff 模型。
- 不把本设计变成脱离任务上下文的独立知识聊天产品。
- 不改变 canonical gate order: `build -> test -> contract/invariant -> hotspot`。

## Current State

### Landed Today
- 澄清协议已 formalize repeated failure 到 `clarify_required` 的切换与 evidence 字段要求。
- task intake 已有目标、范围、验收和预算骨架。
- repo map/context shaping 已有显式 `max_tokens` 约束。
- evidence bundle 已覆盖 `goal`、`acceptance_criteria`、`open_questions`、`verification_results`、`rollback_ref` 等交付事实。
- trace grading 已覆盖 evidence completeness、workflow correctness、replay readiness、outcome quality 四个维度。

### Gaps
- “教学式协作”仍是 prompt 风格，而不是 reviewable governance asset。
- 预算目前只存在于 task/repo map 级别，尚未细分为 explanation、clarification、compaction 等行为预算。
- 缺少 interaction-level evidence，无法解释为什么 AI 在某个时刻改为追问、教学、压缩或停机。
- 仓库研究已明确将 `Noise budget and session compaction thresholds` 标为 `defer`，因为还缺基于 governed sessions 的真实遥测。

## Options Considered

### Option A: 先只做教学式协作，不纳入低 token 治理
Pros:
- 概念最少
- 最容易快速落文档

Cons:
- “解释多寡”和“何时停”仍会散落在 prompt 习惯中
- 后续一定还要重做预算与压缩层

### Option B: 先只做低 token 预算与压缩，不定义教学行为
Pros:
- 成本控制目标清晰
- 容易转成遥测指标

Cons:
- 无法解释“应该保留哪些教学内容”
- 容易把压缩做成纯机械裁剪

### Option C: 先写一份统一总设计，内部拆成两个子系统，后续再分解成多份正式 spec
Pros:
- 先统一目标、术语、触发链和 evidence 口径
- 最适合当前 `docs-first / contracts-first` 阶段
- 便于后续拆成独立 spec/schema/example

Cons:
- 第一版文档更长
- 需要在设计阶段明确共享对象边界

## Chosen Approach
Choose Option C.

本次先落一份总设计，统一定义：
- `教学式协作与认知纠偏` 子系统
- `低 token 预算、压缩与高效教学` 子系统
- 二者共享的对象模型、触发链、evidence 接法与 metrics 口径

后续真正进入 contract implementation 时，再拆成多份更窄的 spec/schema/example。

## Design Overview
系统保持在现有 governed task 主链之上，不新增平行工作流。新增的是一层 interaction governance view：

`task intake -> interaction signals -> response policy -> user-visible guidance -> interaction evidence -> metrics / postmortem inputs`

这层 view 只决定：
- 何时对齐任务
- 何时提示用户补观察
- 何时短讲术语或原理
- 何时压缩、降级或停止

它不替代主执行链，不改变 approval 或 verification 的权威性。

## Subsystem A: 教学式协作与认知纠偏
该子系统只负责五类行为：

1. `意图对齐`
- 在关键节点短复述当前任务、非目标和当前判断，防止悄悄偏题。

2. `认知摩擦识别`
- 只识别外显信号，不对用户做心理判断。
- 重点信号包括：
  - 把现象当根因
  - 缺失 `expected vs actual`
  - 多次混淆术语、模块边界或验证门禁
  - 同一问题重复追问但没有信息增量
  - AI 连续修错方向

3. `即时教学`
- 只解释当前任务必须理解的术语、原理或设计取舍。
- 禁止百科式展开。

4. `bug 观察引导`
- 当现有信息不足以支撑根因推理时，优先给 observation checklist，而不是继续高成本猜测。

5. `误解显式化`
- 当 AI 判断用户前提与系统事实不一致时，要直接指出分歧点，而不是顺着错误前提继续生成。

该子系统的标准输出形态应保持简短：
- 一句话任务锚点
- 1 到 3 个澄清问题
- 3 到 5 条 observation checklist
- 1 个术语卡片
- 1 个显式误解提示

## Subsystem B: 低 Token 预算、压缩与高效教学
该子系统只负责五类行为：

1. `预算分配`
- 在 task budget 之下进一步拆分：
  - `execution budget`
  - `clarification budget`
  - `explanation budget`
  - `compaction budget`

2. `表达档位控制`
- 至少支持三档：
  - `terse`
  - `guided`
  - `teaching`

3. `触发式压缩`
- 压缩不按轮数触发，而按预算压力、历史重复度、阶段切换和单位收益下降触发。

4. `显式降级`
- 在预算或能力不足时显式降到更弱姿态，例如：
  - `teaching -> guided`
  - `guided -> terse`
  - 自由解释 -> checklist
  - 长文解释 -> `ref_only`

5. `停止条件`
- 当 token、时间、澄清轮次或返工次数超阈值时，要求用户补关键输入、确认目标、人工接管或结束当前轮。

## Shared Object Model
第一版统一定义五类共享对象，避免子系统之间各自发明字段：

### 1. `InteractionSignal`
Purpose:
- 记录为什么系统此刻要调整交互行为。

Suggested fields:
- `signal_id`
- `task_id`
- `signal_kind`
- `severity`
- `confidence`
- `source`
- `summary`
- `evidence_refs`
- `recorded_at`

Suggested `signal_kind` values:
- `intent_drift`
- `goal_scope_mismatch`
- `expected_actual_missing`
- `symptom_root_cause_confusion`
- `term_confusion`
- `repeated_question_no_progress`
- `repeated_failure`
- `observation_gap`
- `budget_pressure`
- `verbosity_overrun`
- `handoff_risk`

Invariants:
- signals 只记录可观察证据，不记录对用户心理状态的主观推断
- signals 必须能回链到 evidence 或 context refs

### 2. `ResponsePolicy`
Purpose:
- 记录当前一次响应应该如何表达，而不是持久人格设定。

Suggested fields:
- `policy_id`
- `task_id`
- `mode`
- `teaching_level`
- `clarification_mode`
- `compression_mode`
- `max_questions`
- `max_observation_items`
- `term_explain_limit`
- `restatement_required`
- `stop_or_escalate`
- `rationale_signal_ids`

Suggested enums:
- `mode`: `terse`, `guided`, `teaching`
- `clarification_mode`: `none`, `light`, `required`
- `compression_mode`: `none`, `stage_summary`, `aggressive_compaction`, `ref_only`
- `stop_or_escalate`: `continue`, `pause_for_user_input`, `switch_to_checklist`, `handoff_only`, `stop_on_budget`

### 3. `TeachingBudget`
Purpose:
- 记录 explanation、clarification 与 compaction 的可用预算和消耗状态。

Suggested fields:
- `task_id`
- `total_token_budget`
- `execution_budget`
- `clarification_budget`
- `explanation_budget`
- `compaction_budget`
- `used_execution_tokens`
- `used_clarification_tokens`
- `used_explanation_tokens`
- `used_compaction_tokens`
- `soft_thresholds`
- `hard_thresholds`
- `budget_status`

Suggested `budget_status` values:
- `healthy`
- `warning`
- `near_limit`
- `exhausted`

### 4. `InteractionEvidence`
Purpose:
- 记录本次教学、澄清、压缩或停机到底做了什么。

Suggested fields:
- `interaction_evidence_id`
- `task_id`
- `applied_policy_ref`
- `trigger_signal_refs`
- `task_restatement`
- `clarification_questions`
- `clarification_answers`
- `observation_checklist`
- `terms_explained`
- `compression_action`
- `before_after_summary`
- `budget_snapshot`
- `outcome_assessment`
- `created_at`

### 5. `LearningEfficiencyMetrics`
Purpose:
- 评估这套设计是否减少误解、返工与 token 浪费。

Suggested fields:
- `task_id`
- `restatement_count`
- `clarification_rounds`
- `term_explanation_count`
- `observation_prompt_count`
- `compression_count`
- `budget_downgrade_count`
- `token_spend_total`
- `token_spend_explanation`
- `token_spend_clarification`
- `repeated_misunderstanding_count`
- `rework_after_misalignment_count`
- `user_confirmed_alignment_count`
- `issue_resolution_without_repeated_question`
- `recorded_at`

## Interaction Posture And Trigger Rules
本设计不引入新的 task state machine，而是在现有 task 状态之外增加轻量 `interaction posture`：
- `aligned`
- `clarifying`
- `guiding`
- `teaching`
- `compressing`
- `handoff_only`
- `stopped_on_budget`

### Trigger Sources
第一版只保留六类关键触发点：

1. `task_created`
- 输出简短任务锚点
- 默认 `guided`

2. `scope_or_goal_changed`
- 强制任务复述
- 显式指出任务与原意是否已经漂移

3. `repeated_failure` 或阈值达到
- 从 `direct_fix` 切到 `clarifying`
- 继续复用现有 clarification protocol

4. `observation_gap_detected`
- 在缺失 `expected vs actual`、复现步骤、日志或 stack trace 时切到 `guiding`
- 优先给 checklist

5. `term_confusion_or_concept_confusion`
- 当术语或概念混淆正在影响决策时切到 `teaching`
- 一次最多解释一个关键术语或一个关键区别

6. `budget_pressure_detected`
- 当预算接近阈值或历史重复度过高时切到 `compressing`
- 允许进一步降到 `handoff_only` 或 `stopped_on_budget`

### Trigger Priority
同时出现多个信号时，采用固定优先级：
1. `high_risk_or_handoff_risk`
2. `scope_or_goal_changed`
3. `repeated_failure`
4. `observation_gap_detected`
5. `term_confusion_or_concept_confusion`
6. `budget_pressure_detected`

Budget optimization may not override correctness or safety.

### Posture Limits
为避免自由发挥，每种姿态有明确限制：

`aligned`
- 允许：一句任务锚点、一句判断、一句下一步
- 禁止：长篇教学

`clarifying`
- 允许：1 到 3 个关键问题
- 禁止：边问边铺陈长方案

`guiding`
- 允许：3 到 5 条 observation checklist
- 禁止：在观测不足时给高自信根因

`teaching`
- 允许：1 个关键术语或 1 个关键原理的微型解释
- 禁止：百科式扩展

`compressing`
- 允许：阶段摘要、删去重复解释、只保留 refs
- 禁止：新增大量教学内容

`handoff_only`
- 允许：状态、风险、refs、下一位操作者的动作
- 禁止：继续深推理

`stopped_on_budget`
- 允许：说明停止原因、当前摘要与所需补充信息
- 禁止：继续展开新推理

### Restatement Strategy
任务复述采用触发式，而非按轮次固定重复。

Must restate on:
- task created
- goal/scope changed
- large risky change before execution
- retry after repeated failure
- before delivery handoff

Do not restate on:
- 普通连续调试回合
- 仅补一条日志或单个命令结果
- checklist 模式下且目标未变化时

## Evidence, Trace, And Metrics Integration
该设计不另起一套证据仓，而是接入现有四个位置：

### 1. Task Intake / Runtime
复用现有 `goal / scope / acceptance / budgets`，仅增加附属输入：
- `interaction_defaults`
- `interaction_budget_overrides`

### 2. Evidence Bundle
在 evidence bundle 中新增可选扩展块 `interaction_trace`，建议包含：
- `signals`
- `applied_policies`
- `task_restatements`
- `clarification_rounds`
- `observation_checklists`
- `terms_explained`
- `compression_actions`
- `budget_snapshots`
- `alignment_outcome`
- `stop_or_degrade_reason`

### 3. Eval And Trace Grading
不新增第五个主 grading 维度，而是在 postmortem inputs 或扩展 follow-up signals 中引入：
- `misalignment_not_caught`
- `over_explained_under_budget_pressure`
- `under_explained_with_high_user_confusion`
- `repeated_question_without_signal_upgrade`
- `observation_gap_ignored`
- `compression_without_recoverable_summary`

### 4. Repo Profile / Operator Surface
repo profile 只允许设置默认交互偏好，例如：
- `interaction_profile.default_mode`
- `interaction_profile.term_explain_style`
- `interaction_profile.default_checklist_kind`
- `interaction_profile.compaction_preference`
- `interaction_profile.summary_template`
- `interaction_profile.handoff_teaching_notes`

这些配置不得覆盖：
- clarification question cap
- hard budget stop
- explicit degrade semantics
- risk/approval/gate order

operator surface 只投影最少必要字段，例如：
- current `interaction posture`
- latest `task restatement`
- current `budget status`
- whether clarification is active
- latest `compression action`
- count of outstanding observation items

## Minimal Metrics Set
第一版只追踪 8 个高价值指标：
- `alignment_confirm_rate`
- `misalignment_detect_rate`
- `repeated_failure_before_clarify`
- `observation_gap_prompt_rate`
- `term_explanation_trigger_rate`
- `compression_trigger_rate`
- `explanation_token_share`
- `handoff_recovery_success_rate`

这些指标足以回答：
- 是否更早发现误解
- 是否把 bug 观察前置
- 是否讲得过多
- 压缩后是否仍可恢复任务

## Follow-On Spec Decomposition
本总设计后续建议拆分为以下更窄资产：
- `intent-alignment-check-spec`
- `cognitive-friction-signal-spec`
- `bug-observation-checklist-spec`
- `teaching-response-policy-spec`
- `session-compaction-and-explanation-budget-spec`

第一阶段仍以 design 和 evidence 为主，不直接引入大规模 runtime mutation。

## Rollout Guidance
Recommended order:
1. land this top-level design
2. split the design into narrower specs and examples
3. extend evidence bundle with `interaction_trace`
4. extend postmortem inputs and metrics wiring
5. project the minimal read model into repo profile defaults and operator surface

## Risks
- `signal false positive`: 过度触发教学或澄清会伤害流畅度。
- `budget overfitting`: 如果只追求压缩，可能在高认知摩擦场景下解释不足。
- `adapter inconsistency`: 不同 host/adapter tier 的上下文可见性差异可能影响 signal quality。
- `metric distortion`: 仅看 token 降低而不看误解率，可能导致“省 token 但更难用”的假优化。

## Design Acceptance Criteria
This design is acceptable when:
- 可以明确说明何时复述任务、何时教学、何时给 checklist、何时压缩或停机
- 教学行为与 budget 行为共享同一套 signal/policy/evidence 语言
- 新行为可以挂接到现有 evidence、trace 与 postmortem 流程，而不是平行系统
- 后续可以自然拆成更窄的 spec/schema/example，而无需推翻总设计

