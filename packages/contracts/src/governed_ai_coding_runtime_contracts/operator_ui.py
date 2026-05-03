"""Local HTML renderer for the runtime operator surface."""

from html import escape
from pathlib import Path

from governed_ai_coding_runtime_contracts.file_guard import atomic_write_text
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeSnapshot


_TRANSLATIONS = {
    "zh-CN": {
        "html_lang": "zh-CN",
        "title": "Governed Runtime 控制台",
        "runtime_root": "Runtime 根目录",
        "persistence": "持久化",
        "summary_aria": "Runtime 摘要",
        "tasks": "任务",
        "tasks_caption": "最近任务",
        "approvals": "审批",
        "approvals_caption": "待确认",
        "verification": "验证结果",
        "verification_caption": "验证记录",
        "attachments": "已接入仓库",
        "fail_closed_caption": "风险自动阻断",
        "workspace_overview": "控制台总览",
        "workspace_overview_caption": "所有日常入口集中在左侧操作台；这里只保留当前状态、账号配置和反馈证据的决策摘要。",
        "shortcut_entry": "推荐入口",
        "shortcut_entry_caption": "优先用这些入口完成日常闭环；页面按钮会通过同一个根目录入口执行。",
        "shortcut_fast": "日常快速反馈",
        "shortcut_fast_command": ".\\run.ps1 fast",
        "shortcut_fast_caption": "编码中先跑 build + quick feedback tests；不替代交付前 readiness。",
        "shortcut_daily": "交付 readiness",
        "shortcut_daily_command": ".\\run.ps1 readiness -OpenUi",
        "shortcut_daily_caption": "按 build -> test -> contract/invariant -> hotspot 收口并打开中文控制台。",
        "shortcut_targets": "目标仓巡检",
        "shortcut_targets_command": ".\\run.ps1 daily -Mode quick",
        "shortcut_targets_caption": "对 active targets 执行快速 daily flow。",
        "shortcut_rules": "规则漂移检查",
        "shortcut_rules_command": ".\\run.ps1 rules-check",
        "shortcut_rules_caption": "只检查 Codex/Claude/Gemini 规则漂移。",
        "shortcut_feedback": "功能反馈汇总",
        "shortcut_feedback_command": ".\\run.ps1 feedback",
        "shortcut_feedback_caption": "汇总 Codex/Claude 与 target-run 证据。",
        "run_now": "执行",
        "command_label": "命令",
        "open_surface": "打开面板",
        "surface_current": "当前面板",
        "runtime_surface_caption": "任务、执行输出、下一步建议和目标仓状态。",
        "codex_surface_caption": "当前账号、配置健康和额度快照。",
        "claude_surface_caption": "当前 Provider、凭据状态和本机配置入口。",
        "feedback_surface_caption": "闭环状态、证据新鲜度和处理建议。",
        "surface_loading": "正在加载摘要…",
        "surface_runtime_summary": "任务 {tasks} · 审批 {approvals} · 验证 {verification}",
        "surface_runtime_detail": "接入仓库 {attachments} · 风险阻断 {fail_closed}",
        "surface_runtime_action": "在此查看执行输出、历史和下一步建议。",
        "surface_codex_action": "去 Codex 面板查看账号详情和在线刷新。",
        "surface_claude_action": "去 Claude 面板查看 Provider 和推荐配置。",
        "surface_feedback_action": "去反馈面板查看证据、建议和详细报告。",
        "maintenance": "维护与升级",
        "stage": "阶段",
        "compatibility": "兼容性",
        "upgrade": "升级",
        "triage": "分流",
        "deprecation": "弃用",
        "retirement": "退役",
        "no_tasks": "暂无运行记录。",
        "no_attachments": "暂无已接入目标仓记录。",
        "task": "任务",
        "state": "状态",
        "goal": "目标",
        "outputs": "结果与记录",
        "run": "运行",
        "workspace": "工作区",
        "interaction": "交互",
        "rollback": "回滚",
        "repo": "仓库",
        "adapter": "接入方式",
        "diagnostics": "问题说明",
        "binding": "接入标识",
        "light_pack": "轻量上下文包",
        "fail_closed": "风险自动阻断",
        "preference": "默认方式",
        "gate_profile": "验证档位",
        "reason": "原因",
        "remediation": "修复建议",
        "missing": "缺失",
        "none": "无",
        "not_recorded": "未记录",
        "unknown_repo": "未知仓库",
        "actions": "统一操作台",
        "settings": "执行参数",
        "recommended_next": "AI 推荐下一步",
        "quick_actions": "本仓验证",
        "target_actions": "目标仓治理",
        "rule_actions": "规则与演进",
        "advanced_settings": "高级参数",
        "page_actions": "页面",
        "language": "语言",
        "target": "目标仓",
        "all_targets": "全部目标仓",
        "target_selection": "目标仓选择",
        "target_selection_hint": "默认全部；取消全部后可勾选多个目标仓。批量卸载只处理勾选目标。",
        "mode": "验证模式",
        "parallelism": "目标并发",
        "fail_fast": "失败即停",
        "dry_run": "只预演",
        "apply_removal": "真实执行清理/卸载",
        "apply_removal_hint": "全部功能应用默认删除已证明安全的退役托管文件；清理/卸载按钮需勾选才真实执行。只预演会禁用真实删除。",
        "milestone": "里程碑标签",
        "refresh": "刷新状态",
        "run": "执行",
        "command_output": "执行输出",
        "codex_console": "Codex 账号与配置",
        "codex_account": "账号",
        "codex_active": "当前",
        "codex_usage": "额度",
        "codex_usage_note": "额度说明",
        "codex_switch": "切换",
        "codex_sync_active": "同步快照",
        "codex_snapshot": "快照",
        "codex_snapshot_synced": "已与 {name} 同步",
        "codex_snapshot_drifted": "{name} 仍是旧快照，建议用当前登录状态回写",
        "codex_snapshot_missing": "当前活动账号还没有命名快照",
        "codex_sync_confirm": "将把当前 auth.json 覆盖回对应命名快照。继续执行？",
        "codex_sync_ok": "已同步当前账号快照。",
        "codex_open_usage": "打开官方 Usage",
        "codex_refresh": "刷新 Codex 状态",
        "codex_refresh_online": "强制在线刷新",
        "codex_refresh_online_hint": "会发起一次最小 Codex 在线请求，可能消耗极少量额度",
        "codex_refresh_idle": "当前显示本机最新快照。",
        "codex_refresh_ok": "在线刷新成功；当前显示最新在线快照。",
        "codex_refresh_fallback": "在线刷新失败；已回退到本机最新快照。",
        "codex_refresh_if_stale": "检测到额度快照过期时，会自动尝试在线刷新。",
        "codex_unknown_usage": "暂时无法读取额度信息",
        "codex_usage_freshness_stale": "额度快照已过期",
        "codex_usage_freshness_fresh": "额度快照较新",
        "codex_usage_freshness_unknown": "未记录刷新时间",
        "codex_config": "配置健康",
        "codex_recommended": "核心原则",
        "codex_current_choice": "当前实现",
        "codex_compact_policy": "压缩策略",
        "codex_manual_upgrade": "手动升档",
        "codex_recommended_note": "本项目长期优先遵循“综合效率优先”：少打扰、自动连续执行、节省 token / 成本、高效率。`gpt-5.5 + medium + never` 只是当前暂行实现；以后若模型、参数或技术栈更迭，应优先保持这个原则，而不是固化当前组合本身。",
        "codex_login": "登录状态",
        "codex_token_validity": "本地令牌",
        "codex_token_expiry": "登录令牌到期",
        "codex_token_note": "登录令牌到期只表示本地 Codex 登录凭据的 token 截止时间。",
        "codex_token_unknown": "未读取到本地 token 有效期",
        "codex_subscription_expiry": "套餐到期日",
        "codex_subscription_note": "套餐日期来自本地 token 声明，不是实时 billing API 查询。",
        "codex_subscription_unknown": "未读取到套餐有效期",
        "panel_cache_state": "数据状态",
        "panel_cache_cold": "首次加载中",
        "panel_cache_cached": "缓存快照",
        "panel_cache_refreshing": "后台刷新中",
        "panel_cache_ready": "已刷新",
        "panel_cache_error": "刷新失败",
        "codex_account_usage_unknown": "切换后可获取额度",
        "codex_usage_remaining": "余量",
        "codex_usage_reset": "重置",
        "claude_console": "Claude Provider 与配置",
        "claude_provider": "Provider",
        "claude_active": "当前",
        "claude_switch": "切换",
        "claude_refresh": "刷新 Claude 状态",
        "claude_optimize_preview": "预演推荐配置",
        "claude_optimize_apply": "应用推荐配置",
        "claude_view_settings": "查看 settings.json",
        "claude_view_profiles": "查看 provider-profiles.json",
        "claude_view_switcher": "查看切换脚本",
        "claude_service": "服务地址",
        "claude_models": "模型",
        "claude_extensions": "扩展能力",
        "claude_usage_note": "额度说明",
        "claude_settings_summary": "本机设置",
        "claude_config": "配置健康",
        "claude_command": "CLI 状态",
        "claude_mcp": "MCP 状态",
        "claude_settings": "本机设置",
        "claude_credential": "凭据",
        "claude_usage": "额度",
        "claude_unknown_usage": "暂时无法读取额度信息",
        "claude_active_provider": "当前 Provider",
        "claude_active_summary": "当前映射",
        "claude_context_strategy": "上下文策略",
        "claude_timeout": "超时",
        "claude_subagent": "子代理",
        "claude_note": "建议",
        "claude_local_files": "本机入口",
        "claude_file_hint": "只开放本机 Claude 配置相关文件预览，不开放任意系统路径读取。",
        "claude_provider_profiles": "Provider 配置",
        "claude_missing_credential": "缺少凭据",
        "claude_credential_ready": "凭据已就绪",
        "claude_apply_recommended_confirm": "将按当前激活 provider 备份并写入 Claude Code 推荐配置。继续执行？",
        "claude_no_active_provider": "当前未识别到激活 provider",
        "history": "执行历史",
        "no_history": "暂无执行历史。",
        "clear_history": "清空历史",
        "runtime_view": "Runtime",
        "feedback_view": "反馈",
        "codex_view": "Codex",
        "claude_view": "Claude",
        "feedback_console": "功能反馈闭环",
        "feedback_refresh": "刷新反馈摘要",
        "feedback_status": "反馈状态",
        "feedback_generated_at": "生成时间",
        "feedback_summary_caption": "简版摘要",
        "feedback_dimensions": "维度状态",
        "feedback_recommendations": "优化建议",
        "feedback_latest_runs": "最新目标仓证据",
        "feedback_latest_runs_hint": "看这 3 项就够了：接入方式是否正常、闭环状态是否 ready、写入状态是否真的执行过。",
        "feedback_repo_attach": "接入方式",
        "feedback_repo_flow": "运行流",
        "feedback_repo_closure": "闭环状态",
        "feedback_repo_write": "写入状态",
        "feedback_repo_attach_native": "原生直连",
        "feedback_repo_attach_bridge": "桥接接入",
        "feedback_repo_attach_manual": "人工接力",
        "feedback_repo_flow_live": "宿主内直接运行",
        "feedback_repo_flow_bridge": "通过桥接运行",
        "feedback_repo_closure_ready": "已具备闭环",
        "feedback_repo_closure_partial": "闭环未完成",
        "feedback_repo_write_unknown": "未记录写入执行",
        "feedback_repo_write_done": "已执行写入",
        "feedback_links": "文档与报告",
        "feedback_open_report": "查看详细报告",
        "feedback_open_guide": "查看反馈指南",
        "feedback_open_guide_en": "查看英文指南",
        "feedback_report_missing": "尚未生成详细报告，可先执行“功能反馈汇总”。",
        "feedback_loading": "正在加载反馈摘要…",
        "feedback_empty": "暂未获取到反馈摘要。",
        "feedback_preview": "文档预览",
        "feedback_preview_idle": "点击“查看详细报告”或“查看反馈指南”后，会在这里展开内容。",
        "ready": "就绪",
        "running": "执行中",
        "static_snapshot": "只读快照",
        "targets_action": "目标仓列表",
        "fast_feedback_action": "快速反馈",
        "readiness_action": "本仓 readiness",
        "rules_dry_run_action": "只查规则漂移",
        "rules_apply_action": "同步规则文件",
        "governance_baseline_action": "下发治理基线",
        "daily_all_action": "运行 Daily 巡检",
        "apply_all_action": "应用全部治理能力",
        "cleanup_targets_action": "一键清理退役文件",
        "uninstall_governance_action": "一键卸载治理",
        "feedback_report_action": "功能反馈汇总",
        "evolution_review_action": "演进候选预演",
        "experience_review_action": "经验沉淀预演",
        "evolution_materialize_action": "物化演进候选",
        "core_principle_action": "核心原则候选",
        "view_ref": "查看",
        "confirm_mutating": "该操作会应用目标仓治理能力，并默认删除已证明安全的退役托管文件；不安全候选会阻断。继续执行？",
        "confirm_evolution_materialize": "将把低风险演进候选物化为 proposal 或禁用态 skill candidate，不启用技能。继续执行？",
        "confirm_managed_cleanup": "将对选中的目标仓执行退役治理文件清理；未勾选“实际删除”时只预演。继续执行？",
        "confirm_governance_uninstall": "将对选中的目标仓执行治理卸载；勾选“实际删除”会删除或修补受管文件并写备份。继续执行？",
        "no_target_selected": "至少选择一个目标仓。",
        "interactive_required": "当前是静态快照；启动本地服务后可执行操作。",
    },
    "en": {
        "html_lang": "en",
        "title": "Governed Runtime Console",
        "runtime_root": "Runtime root",
        "persistence": "Persistence",
        "summary_aria": "Runtime Summary",
        "tasks": "Tasks",
        "tasks_caption": "recent tasks",
        "approvals": "Approvals",
        "approvals_caption": "waiting",
        "verification": "Verification",
        "verification_caption": "verification records",
        "attachments": "Attachments",
        "fail_closed_caption": "risk auto-block",
        "workspace_overview": "Workbench Overview",
        "workspace_overview_caption": "All daily entrypoints live in the left operator bench; this overview keeps only decision-grade status, account config, and feedback evidence.",
        "shortcut_entry": "Recommended Entrypoints",
        "shortcut_entry_caption": "Use these entrypoints for routine closure; page buttons delegate through the same repository-root command.",
        "shortcut_fast": "Daily fast feedback",
        "shortcut_fast_command": ".\\run.ps1 fast",
        "shortcut_fast_caption": "Run build plus quick feedback tests while coding; delivery still needs readiness.",
        "shortcut_daily": "Delivery readiness",
        "shortcut_daily_command": ".\\run.ps1 readiness -OpenUi",
        "shortcut_daily_caption": "Close with build -> test -> contract/invariant -> hotspot and open the console.",
        "shortcut_targets": "Target sweep",
        "shortcut_targets_command": ".\\run.ps1 daily -Mode quick",
        "shortcut_targets_caption": "Run quick daily flow for active targets.",
        "shortcut_rules": "Rule drift check",
        "shortcut_rules_command": ".\\run.ps1 rules-check",
        "shortcut_rules_caption": "Check Codex/Claude/Gemini rule drift only.",
        "shortcut_feedback": "Feedback summary",
        "shortcut_feedback_command": ".\\run.ps1 feedback",
        "shortcut_feedback_caption": "Summarize Codex/Claude and target-run evidence.",
        "run_now": "Run",
        "command_label": "Command",
        "open_surface": "Open panel",
        "surface_current": "Current panel",
        "runtime_surface_caption": "Tasks, execution output, next-work recommendation, and target state.",
        "codex_surface_caption": "Active account, config health, and usage snapshot.",
        "claude_surface_caption": "Active provider, credential status, and local config entrypoints.",
        "feedback_surface_caption": "Closure status, evidence freshness, and recommendations.",
        "surface_loading": "Loading summary...",
        "surface_runtime_summary": "Tasks {tasks} · Approvals {approvals} · Verification {verification}",
        "surface_runtime_detail": "Attachments {attachments} · Fail-closed {fail_closed}",
        "surface_runtime_action": "Use Runtime for output, history, and next-work decisions.",
        "surface_codex_action": "Open Codex for account detail and online refresh.",
        "surface_claude_action": "Open Claude for provider status and recommended config.",
        "surface_feedback_action": "Open Feedback for evidence, recommendations, and reports.",
        "maintenance": "Maintenance and Upgrade",
        "stage": "Stage",
        "compatibility": "Compatibility",
        "upgrade": "Upgrade",
        "triage": "Triage",
        "deprecation": "Deprecation",
        "retirement": "Retirement",
        "no_tasks": "No runtime activity has been recorded.",
        "no_attachments": "No attached target repos recorded.",
        "task": "Task",
        "state": "State",
        "goal": "Goal",
        "outputs": "Results",
        "run": "Run",
        "workspace": "Workspace",
        "interaction": "Interaction",
        "rollback": "Rollback",
        "repo": "Repo",
        "adapter": "Connection",
        "diagnostics": "Issue details",
        "binding": "Connection ID",
        "light_pack": "Light context pack",
        "fail_closed": "Fail closed",
        "preference": "Preference",
        "gate_profile": "Gate profile",
        "reason": "Reason",
        "remediation": "Remediation",
        "missing": "missing",
        "none": "none",
        "not_recorded": "not recorded",
        "unknown_repo": "unknown repo",
        "actions": "Unified Operator Bench",
        "settings": "Run Parameters",
        "recommended_next": "AI Recommended Next Step",
        "quick_actions": "Repo Verification",
        "target_actions": "Target Governance",
        "rule_actions": "Rules and Evolution",
        "advanced_settings": "Advanced Parameters",
        "page_actions": "Page",
        "language": "Language",
        "target": "Target repo",
        "all_targets": "All targets",
        "target_selection": "Target selection",
        "target_selection_hint": "All targets are selected by default. Clear all to choose multiple specific target repos.",
        "mode": "Mode",
        "parallelism": "Target parallelism",
        "fail_fast": "Fail fast",
        "dry_run": "Dry run",
        "apply_removal": "Apply cleanup/uninstall deletes",
        "apply_removal_hint": "Apply-all deletes proven-safe retired managed files by default; cleanup/uninstall buttons require this checkbox. Dry run disables deletes.",
        "milestone": "Milestone tag",
        "refresh": "Refresh status",
        "run": "Run",
        "command_output": "Execution output",
        "codex_console": "Codex Account and Config",
        "codex_account": "Account",
        "codex_active": "Active",
        "codex_usage": "Usage",
        "codex_usage_note": "Usage details",
        "codex_switch": "Switch",
        "codex_sync_active": "Sync snapshot",
        "codex_snapshot": "Snapshot",
        "codex_snapshot_synced": "Synced with {name}",
        "codex_snapshot_drifted": "{name} is stale; save the current login back into it",
        "codex_snapshot_missing": "The current active account has no named snapshot yet",
        "codex_sync_confirm": "This will overwrite the named auth snapshot with the current auth.json. Continue?",
        "codex_sync_ok": "Saved the current account snapshot.",
        "codex_open_usage": "Open Usage",
        "codex_refresh": "Refresh Codex",
        "codex_refresh_online": "Force online refresh",
        "codex_refresh_online_hint": "Runs a minimal Codex online request and may consume a small amount of quota",
        "codex_refresh_idle": "Showing the latest local snapshot.",
        "codex_refresh_ok": "Online refresh succeeded; showing the latest online snapshot.",
        "codex_refresh_fallback": "Online refresh failed; fell back to the latest local snapshot.",
        "codex_refresh_if_stale": "Automatically tries an online refresh when the usage snapshot is stale.",
        "codex_unknown_usage": "Usage information is not available yet",
        "codex_usage_freshness_stale": "Usage snapshot is stale",
        "codex_usage_freshness_fresh": "Usage snapshot is fresh",
        "codex_usage_freshness_unknown": "Refresh time not recorded",
        "codex_config": "Config health",
        "codex_recommended": "Core principle",
        "codex_current_choice": "Current implementation",
        "codex_compact_policy": "Compact policy",
        "codex_manual_upgrade": "Manual upgrade",
        "codex_recommended_note": "This project keeps the long-lived principle of efficiency first: low interruption, continuous execution, lower token and cost burn, and high throughput. `gpt-5.5 + medium + never` is only the current implementation. When future models, parameters, or tooling change, preserve that principle first rather than freezing the current combo itself.",
        "codex_login": "Login status",
        "codex_token_validity": "Local token",
        "codex_token_expiry": "Sign-in token expiry",
        "codex_token_note": "Sign-in token expiry only reflects the local Codex credential token lifetime.",
        "codex_token_unknown": "Local token expiry is not available",
        "codex_subscription_expiry": "Plan renewal date",
        "codex_subscription_note": "Plan dates come from local token claims, not a live billing API query.",
        "codex_subscription_unknown": "Plan validity is not available",
        "panel_cache_state": "Data status",
        "panel_cache_cold": "Loading for the first time",
        "panel_cache_cached": "Cached snapshot",
        "panel_cache_refreshing": "Refreshing in background",
        "panel_cache_ready": "Refreshed",
        "panel_cache_error": "Refresh failed",
        "codex_account_usage_unknown": "Switch to this account to fetch usage",
        "codex_usage_remaining": "left",
        "codex_usage_reset": "reset",
        "claude_console": "Claude Provider and Config",
        "claude_provider": "Provider",
        "claude_active": "Active",
        "claude_switch": "Switch",
        "claude_refresh": "Refresh Claude",
        "claude_optimize_preview": "Preview recommended config",
        "claude_optimize_apply": "Apply recommended config",
        "claude_view_settings": "View settings.json",
        "claude_view_profiles": "View provider-profiles.json",
        "claude_view_switcher": "View switcher script",
        "claude_service": "Service",
        "claude_models": "Models",
        "claude_extensions": "Extensions",
        "claude_usage_note": "Usage",
        "claude_settings_summary": "Settings",
        "claude_config": "Config health",
        "claude_command": "CLI status",
        "claude_mcp": "MCP status",
        "claude_settings": "Local settings",
        "claude_credential": "Credential",
        "claude_usage": "Usage",
        "claude_unknown_usage": "Usage information is not available yet",
        "claude_active_provider": "Active provider",
        "claude_active_summary": "Current mapping",
        "claude_context_strategy": "Context strategy",
        "claude_timeout": "Timeout",
        "claude_subagent": "Subagent",
        "claude_note": "Recommendation",
        "claude_local_files": "Local entrypoints",
        "claude_file_hint": "Only Claude-related local config files are previewable here; arbitrary system files stay blocked.",
        "claude_provider_profiles": "Provider profiles",
        "claude_missing_credential": "missing credential",
        "claude_credential_ready": "credential ready",
        "claude_apply_recommended_confirm": "This will back up and write the recommended Claude Code config for the active provider. Continue?",
        "claude_no_active_provider": "no active provider detected",
        "history": "Run history",
        "no_history": "No run history.",
        "clear_history": "Clear history",
        "runtime_view": "Runtime",
        "feedback_view": "Feedback",
        "codex_view": "Codex",
        "claude_view": "Claude",
        "feedback_console": "Host Feedback Loop",
        "feedback_refresh": "Refresh feedback summary",
        "feedback_status": "Feedback status",
        "feedback_generated_at": "Generated at",
        "feedback_summary_caption": "Snapshot summary",
        "feedback_dimensions": "Dimension status",
        "feedback_recommendations": "Recommendations",
        "feedback_latest_runs": "Latest target evidence",
        "feedback_latest_runs_hint": "Focus on the adapter, closure state, and whether a write step actually ran.",
        "feedback_repo_attach": "Adapter",
        "feedback_repo_flow": "Flow",
        "feedback_repo_closure": "Closure",
        "feedback_repo_write": "Write",
        "feedback_repo_attach_native": "native attach",
        "feedback_repo_attach_bridge": "bridge attach",
        "feedback_repo_attach_manual": "manual handoff",
        "feedback_repo_flow_live": "live host run",
        "feedback_repo_flow_bridge": "bridge run",
        "feedback_repo_closure_ready": "closure ready",
        "feedback_repo_closure_partial": "closure incomplete",
        "feedback_repo_write_unknown": "write not recorded",
        "feedback_repo_write_done": "write executed",
        "feedback_links": "Docs and reports",
        "feedback_open_report": "Open detailed report",
        "feedback_open_guide": "Open zh-CN guide",
        "feedback_open_guide_en": "Open English guide",
        "feedback_report_missing": "No detailed report yet. Run the feedback summary action first.",
        "feedback_loading": "Loading feedback summary...",
        "feedback_empty": "Feedback summary is not available yet.",
        "feedback_preview": "Preview",
        "feedback_preview_idle": "Open the detailed report or guide to preview the content here.",
        "ready": "Ready",
        "running": "Running",
        "static_snapshot": "Read-only snapshot",
        "targets_action": "View targets",
        "fast_feedback_action": "Fast feedback",
        "readiness_action": "Check repo status",
        "rules_dry_run_action": "Rule drift check",
        "rules_apply_action": "Sync rules",
        "governance_baseline_action": "Apply governance baseline",
        "daily_all_action": "Run Daily sweep",
        "apply_all_action": "Apply all governance",
        "cleanup_targets_action": "Clean retired files",
        "uninstall_governance_action": "Uninstall governance",
        "feedback_report_action": "Feedback summary",
        "evolution_review_action": "Evolution dry run",
        "experience_review_action": "Experience dry run",
        "evolution_materialize_action": "Materialize evolution candidates",
        "core_principle_action": "Core-principle candidates",
        "view_ref": "View",
        "confirm_mutating": "This applies target governance and deletes proven-safe retired managed files by default; unsafe candidates are blocked. Continue?",
        "confirm_evolution_materialize": "This materializes low-risk evolution candidates as proposals or disabled skill candidates. It does not enable skills. Continue?",
        "confirm_managed_cleanup": "Run retired governance file cleanup for the selected targets. It only dry-runs unless apply removal is enabled. Continue?",
        "confirm_governance_uninstall": "Run governance uninstall for the selected targets. Apply removal deletes or patches managed files and writes backups. Continue?",
        "no_target_selected": "Select at least one target repo.",
        "interactive_required": "This is a static snapshot; start the local service to run actions.",
    },
}


def render_runtime_snapshot_html(
    snapshot: RuntimeSnapshot,
    language: str = "zh-CN",
    interactive: bool = False,
    target_options: list[str] | None = None,
) -> str:
    text = _ui_text(language)
    approval_count = sum(len(task.approval_ids) for task in snapshot.tasks)
    verification_count = sum(len(task.verification_refs) for task in snapshot.tasks)
    fail_closed_count = sum(1 for attachment in snapshot.attachments if attachment.fail_closed)
    summary = "\n".join(
        [
            f"<section class='summary-grid' aria-label='{escape(text['summary_aria'])}'>",
            _render_metric(text["tasks"], str(snapshot.total_tasks), text["tasks_caption"]),
            _render_metric(text["approvals"], str(approval_count), text["approvals_caption"]),
            _render_metric(text["verification"], str(verification_count), text["verification_caption"]),
            _render_metric(text["attachments"], str(len(snapshot.attachments)), f"{fail_closed_count} {text['fail_closed_caption']}"),
            "</section>",
        ]
    )
    maintenance = _render_maintenance(snapshot, text)
    tasks = _render_tasks(snapshot, text, interactive=interactive)
    attachments = _render_attachments(snapshot, text, interactive=interactive)
    actions = _render_actions(text, language=language, interactive=interactive, target_options=target_options or [])
    feedback = _render_feedback(text, interactive=interactive)
    codex_panel = _render_codex_panel(text, interactive=interactive)
    claude_panel = _render_claude_panel(text, interactive=interactive)
    feedback_panel = _render_host_feedback_panel(text, interactive=interactive)
    script = _render_interactive_script(
        text,
        language=language,
        total_tasks=snapshot.total_tasks,
        approval_count=approval_count,
        verification_count=verification_count,
        attachment_count=len(snapshot.attachments),
        fail_closed_count=fail_closed_count,
    ) if interactive else ""
    runtime_root = snapshot.runtime_root or text["missing"]
    tabs = _render_view_tabs(text)
    workspace_overview = _render_workspace_overview(text, interactive=interactive)
    return f"""<!doctype html>
<html lang="{escape(text['html_lang'])}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>{escape(text['title'])}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #eef3f3;
      --bg-deep: #0e1c20;
      --surface: #ffffff;
      --surface-raised: rgba(255, 255, 255, 0.94);
      --surface-muted: #eef4f3;
      --ink: #152125;
      --ink-strong: #091316;
      --muted: #5d6b70;
      --line: #d4dfe0;
      --line-strong: #aebfc2;
      --accent: #0b766e;
      --accent-strong: #064f49;
      --accent-soft: #e7f5f2;
      --gold: #b8872d;
      --gold-soft: #fff5df;
      --warning: #9a5b08;
      --danger: #b42318;
      --danger-soft: #fff0ee;
      --shadow-soft: 0 22px 54px rgba(8, 22, 26, 0.13);
      --shadow-card: 0 10px 28px rgba(12, 31, 36, 0.08);
      --shadow-tight: 0 2px 0 rgba(255, 255, 255, 0.84) inset, 0 1px 2px rgba(12, 31, 36, 0.04);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI Variable", "Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei", sans-serif;
      background:
        linear-gradient(90deg, rgba(15, 35, 39, 0.035) 1px, transparent 1px),
        linear-gradient(180deg, rgba(15, 35, 39, 0.035) 1px, transparent 1px),
        linear-gradient(145deg, rgba(11, 118, 110, 0.16), transparent 360px),
        linear-gradient(180deg, #fbfcfb 0, var(--bg) 460px);
      background-size: 42px 42px, 42px 42px, auto, auto;
      color: var(--ink);
      font-size: 14px;
      letter-spacing: 0;
    }}
    main {{ width: 100%; max-width: 1600px; margin: 0 auto; padding: 20px 20px 36px; }}
    header {{
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(236, 245, 243, 0.1);
      border-radius: 8px;
      padding: 20px 22px;
      margin-bottom: 16px;
      background:
        linear-gradient(120deg, rgba(255, 255, 255, 0.08), transparent 34%),
        repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.045) 0 1px, transparent 1px 14px),
        linear-gradient(135deg, #0c171b 0, #173136 54%, #075e58 150%);
      color: #f6fbfb;
      box-shadow: var(--shadow-soft);
    }}
    header::after {{
      content: "";
      position: absolute;
      inset: auto 18px 0;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(239, 209, 142, 0.72), transparent);
    }}
    h1 {{ font-size: 1.58rem; line-height: 1.18; margin: 0 0 10px; font-weight: 760; }}
    h2 {{ display: flex; align-items: center; gap: 8px; font-size: 0.98rem; line-height: 1.3; margin: 0 0 12px; color: var(--ink-strong); }}
    h2::before {{ content: ""; width: 4px; height: 1.05em; border-radius: 99px; background: linear-gradient(180deg, var(--gold), var(--accent)); }}
    h3 {{ margin: 0 0 10px; font-size: 0.95rem; line-height: 1.35; color: var(--ink-strong); }}
    .meta-row {{ display: flex; flex-wrap: wrap; gap: 10px 18px; color: var(--muted); font-size: 0.92rem; }}
    header .meta-row {{ color: #cfe1e2; }}
    header code {{ color: #ffffff; }}
    .console-layout {{ display: grid; grid-template-columns: minmax(300px, 352px) minmax(0, 1fr); gap: 16px; align-items: start; }}
    .sidebar {{ position: sticky; top: 14px; display: grid; gap: 12px; align-self: start; }}
    .dashboard {{ min-width: 0; display: grid; gap: 15px; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(165px, 1fr)); gap: 12px; margin-bottom: 2px; }}
    .feedback-grid {{ display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.65fr); gap: 14px; align-items: start; }}
    .runtime-shell {{ display: grid; grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.9fr); gap: 14px; align-items: start; }}
    .runtime-main, .runtime-side {{ display: grid; gap: 14px; min-width: 0; }}
    .runtime-main > *, .runtime-side > * {{ min-width: 0; }}
    .details-grid {{ display: grid; gap: 14px; align-items: start; }}
    .feedback-summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; margin-bottom: 12px; }}
    .feedback-shell {{ display: grid; grid-template-columns: minmax(320px, 0.9fr) minmax(420px, 1.1fr); gap: 14px; align-items: start; }}
    .feedback-column {{ display: grid; gap: 12px; min-width: 0; }}
    .feedback-list, .feedback-links, .feedback-latest-runs {{ display: grid; gap: 8px; }}
    .feedback-run {{ border: 1px solid var(--line); border-radius: 8px; padding: 11px 12px; background: linear-gradient(180deg, #ffffff, #f9fcfc); box-shadow: var(--shadow-tight); }}
    .feedback-run strong {{ display: block; margin-bottom: 6px; }}
    .status-pill-list {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-start; }}
    .status-pill {{ display: inline-flex; flex: 0 0 auto; align-items: center; gap: 6px; padding: 5px 9px; border-radius: 999px; border: 1px solid var(--line); background: var(--surface-muted); font-size: 0.82rem; white-space: nowrap; max-width: 100%; box-shadow: var(--shadow-tight); }}
    .status-pill.ok {{ border-color: #b2ddd6; background: #edf9f6; color: var(--accent-strong); }}
    .status-pill.attention {{ border-color: #edd39b; background: #fff6e5; color: var(--warning); }}
    .status-pill.fail {{ border-color: #efc2bc; background: #fff0ee; color: var(--danger); }}
    .feedback-preview-card {{ display: grid; gap: 10px; }}
    .feedback-preview {{ height: 420px; overflow: auto; white-space: pre-wrap; background: linear-gradient(180deg, #ffffff, #fbfdfc); color: var(--ink); border: 1px solid var(--line); border-radius: 8px; padding: 14px; box-shadow: var(--shadow-tight); }}
    .feedback-runs-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }}
    .metric {{
      position: relative;
      overflow: hidden;
      background: linear-gradient(180deg, #ffffff, #f8fbfa);
      border: 1px solid var(--line);
      border-top: 3px solid var(--gold);
      border-radius: 8px;
      padding: 13px 14px 12px;
      min-width: 0;
      box-shadow: var(--shadow-card);
    }}
    .metric::after {{ content: ""; position: absolute; inset: 0 0 auto; height: 1px; background: rgba(255,255,255,0.92); }}
    .metric span {{ display: block; color: var(--muted); font-size: 0.75rem; font-weight: 760; text-transform: uppercase; }}
    .metric strong {{ display: block; font-size: 1.52rem; line-height: 1.05; margin: 5px 0 4px; color: var(--ink-strong); }}
    .metric small {{ display: block; color: var(--muted); overflow-wrap: anywhere; }}
    .section {{ min-width: 0; }}
    .table-wrap {{ background: var(--surface-raised); border: 1px solid var(--line); border-radius: 8px; overflow-x: auto; box-shadow: var(--shadow-card); backdrop-filter: blur(6px); }}
    table {{ width: 100%; border-collapse: collapse; min-width: 720px; }}
    th, td {{ padding: 11px 13px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: linear-gradient(180deg, #f2f6f6, #e7eeee); color: #314253; font-size: 0.76rem; text-transform: uppercase; }}
    tr:last-child td {{ border-bottom: 0; }}
    tbody tr:hover {{ background: #fbfdfd; }}
    .task-id {{ font-weight: 700; }}
    .state {{ display: inline-flex; align-items: center; gap: 6px; font-weight: 700; color: var(--accent); }}
    .state::before {{ content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; box-shadow: 0 0 0 3px rgba(11, 118, 110, 0.12); }}
    .state.warn {{ color: var(--warning); }}
    .state.danger {{ color: var(--danger); }}
    .meta {{ color: var(--muted); font-size: 0.86rem; margin-top: 4px; overflow-wrap: anywhere; }}
    .info-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 8px 12px; margin-top: 7px; min-width: 0; align-items: start; }}
    .info-line {{ min-width: 0; display: grid; grid-template-columns: minmax(0, 1fr); gap: 2px; color: var(--muted); font-size: 0.86rem; line-height: 1.35; }}
    .info-label {{ color: #53646a; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }}
    .info-value {{ min-width: 0; color: #263940; overflow-wrap: anywhere; white-space: pre-line; }}
    .info-value-stack {{ min-width: 0; display: grid; gap: 2px; }}
    .info-value-line {{ min-width: 0; overflow-wrap: anywhere; white-space: pre-wrap; }}
    .info-value-line.secondary {{ color: var(--muted); }}
    .usage-meter-list {{ display: grid; gap: 7px; min-width: 0; }}
    .usage-meter-row {{ display: grid; gap: 4px; min-width: 0; }}
    .usage-meter-head {{ display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 4px 8px; color: #263940; font-size: 0.82rem; }}
    .usage-meter-head small {{ color: var(--muted); font-size: 0.76rem; white-space: normal; overflow-wrap: anywhere; }}
    .usage-bar {{ position: relative; height: 7px; overflow: hidden; border-radius: 999px; background: #dce7e8; box-shadow: inset 0 1px 2px rgba(12, 31, 36, 0.13); }}
    .usage-fill {{ position: absolute; inset: 0 auto 0 0; width: 0%; border-radius: inherit; background: linear-gradient(90deg, var(--accent), #55b8a9); }}
    .usage-fill.warn {{ background: linear-gradient(90deg, #c78317, #e2b051); }}
    .usage-fill.danger {{ background: linear-gradient(90deg, var(--danger), #df6b5f); }}
    .empty-state {{ background: rgba(255, 255, 255, 0.8); border: 1px dashed var(--line-strong); border-radius: 8px; padding: 18px; color: var(--muted); box-shadow: var(--shadow-tight); }}
    .refs {{ display: grid; gap: 8px; }}
    .ref-title {{ display: block; color: var(--muted); font-size: 0.78rem; text-transform: uppercase; margin-bottom: 4px; }}
    ul {{ margin: 0; padding-left: 18px; }}
    li + li {{ margin-top: 4px; }}
    code {{ font-family: Consolas, "Cascadia Mono", "Liberation Mono", monospace; font-size: 0.9rem; overflow-wrap: anywhere; }}
    .policy-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }}
    .policy-item {{ background: linear-gradient(180deg, #ffffff, #f9fcfb); border: 1px solid var(--line); border-radius: 8px; padding: 12px; min-width: 0; box-shadow: var(--shadow-tight); }}
    .policy-label {{ display: block; color: var(--muted); font-size: 0.76rem; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }}
    .panel {{ background: var(--surface-raised); border: 1px solid var(--line); border-top: 3px solid #c5d5d8; border-radius: 8px; padding: 14px; min-width: 0; box-shadow: var(--shadow-card); backdrop-filter: blur(6px); }}
    .output-panel {{ border-top-color: var(--gold); }}
    .surface-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 10px; }}
    .surface-card {{ display: grid; grid-template-rows: auto minmax(86px, 1fr) auto; gap: 10px; align-content: start; background: linear-gradient(180deg, #ffffff, #f9fcfb); border: 1px solid var(--line); border-radius: 8px; padding: 12px; min-width: 0; box-shadow: var(--shadow-tight); }}
    .surface-card.active {{ border-color: #bde0da; background: linear-gradient(180deg, #f2fbf8, #ffffff); }}
    .surface-card-head {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
    .surface-card-title {{ font-weight: 760; color: var(--ink-strong); }}
    .surface-summary {{ display: grid; align-content: start; gap: 4px; min-width: 0; }}
    .surface-summary p {{ margin: 0; color: var(--muted); line-height: 1.45; overflow-wrap: anywhere; }}
    .surface-summary p:first-child {{ color: var(--ink); font-weight: 650; }}
    .surface-card button {{ min-height: 36px; align-self: end; width: 100%; }}
    .surface-badge {{ display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; padding: 4px 8px; font-size: 0.76rem; font-weight: 760; border: 1px solid var(--line); background: var(--surface-muted); color: var(--muted); }}
    .surface-card.active .surface-badge {{ border-color: #bde0da; color: var(--accent-strong); background: var(--accent-soft); }}
    .view-tabs {{ display: inline-flex; gap: 4px; background: rgba(234, 241, 241, 0.92); border: 1px solid var(--line); border-radius: 8px; padding: 4px; width: fit-content; max-width: 100%; box-shadow: 0 9px 22px rgba(12, 31, 36, 0.07); }}
    .view-tab {{ border: 0; background: transparent; border-radius: 6px; padding: 8px 13px; }}
    .view-tab[aria-selected="true"] {{ background: var(--surface); color: var(--accent-strong); box-shadow: 0 0 0 1px var(--line), 0 6px 14px rgba(12, 31, 36, 0.09); font-weight: 760; }}
    .action-list {{ display: grid; gap: 8px; }}
    .action-group {{ display: grid; gap: 8px; }}
    .action-group + .action-group {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--line); }}
    .action-group-title {{ margin: 0; color: var(--muted); font-size: 0.76rem; font-weight: 700; text-transform: uppercase; }}
    .foldout {{ border-top: 1px solid var(--line); margin-top: 12px; padding-top: 10px; }}
    .foldout > summary {{ cursor: pointer; color: var(--ink-strong); font-weight: 760; line-height: 1.4; list-style-position: inside; }}
    .foldout[open] > summary {{ margin-bottom: 9px; }}
    .shortcut-list {{ display: grid; gap: 9px; margin-top: 10px; }}
    .shortcut-item {{ display: grid; gap: 8px; min-width: 0; padding: 11px; border: 1px solid var(--line); border-radius: 8px; background: linear-gradient(180deg, #ffffff, #f9fcfb); box-shadow: var(--shadow-tight); }}
    .shortcut-item.recommended {{ border-color: #bde0da; background: linear-gradient(180deg, #f2fbf8, #ffffff); }}
    .shortcut-head {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; min-width: 0; }}
    .shortcut-title {{ font-weight: 760; color: var(--ink-strong); line-height: 1.35; }}
    .shortcut-command {{ display: block; min-width: 0; width: 100%; padding: 7px 8px; border: 1px solid #dfe9ea; border-radius: 6px; background: #f7fbfa; color: #20333a; overflow-wrap: anywhere; white-space: normal; }}
    .shortcut-item .meta {{ margin: 0; }}
    .shortcut-blocked {{ color: var(--warning); font-weight: 650; }}
    .shortcut-item button {{ text-align: center; min-height: 34px; }}
    button, select, input {{ font: inherit; }}
    button {{ border: 1px solid var(--line); background: linear-gradient(180deg, #ffffff, #f8fbfb); color: var(--ink); border-radius: 7px; padding: 9px 11px; cursor: pointer; text-align: left; transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease, background 140ms ease; }}
    button:hover {{ border-color: var(--accent); box-shadow: 0 7px 16px rgba(11, 118, 110, 0.10); transform: translateY(-1px); }}
    button.primary {{ background: linear-gradient(135deg, var(--accent), var(--accent-strong)); border-color: var(--accent-strong); color: #fff; font-weight: 760; }}
    button.danger {{ border-color: #efb8b2; color: var(--danger); background: linear-gradient(180deg, #fff, var(--danger-soft)); }}
    button:disabled {{ cursor: not-allowed; opacity: 0.55; }}
    .setting-grid {{ display: grid; gap: 10px; }}
    label {{ display: grid; gap: 4px; color: var(--muted); font-size: 0.82rem; min-width: 0; }}
    select, input[type="number"], input[type="text"] {{ width: 100%; min-width: 0; max-width: 100%; border: 1px solid var(--line); border-radius: 7px; padding: 8px 9px; color: var(--ink); background: #fff; box-shadow: var(--shadow-tight); }}
    select:focus, input:focus, button:focus-visible {{ outline: 2px solid rgba(11, 118, 110, 0.24); outline-offset: 2px; }}
    .checkbox-row {{ display: flex; align-items: center; gap: 8px; color: var(--ink); }}
    .target-picker {{ display: grid; gap: 8px; border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: linear-gradient(180deg, #ffffff, #f9fcfb); box-shadow: var(--shadow-tight); }}
    .target-picker-head {{ display: grid; gap: 2px; }}
    .target-picker-title {{ color: var(--ink-strong); font-weight: 760; }}
    .target-checkbox-list {{ display: grid; gap: 7px; max-height: 180px; overflow: auto; padding-top: 6px; border-top: 1px solid var(--line); }}
    .target-checkbox-list input:disabled + span {{ color: var(--muted); }}
    .danger-row {{ padding: 8px 9px; border: 1px solid #efc2bc; border-radius: 8px; background: var(--danger-soft); }}
    .status-line {{ color: var(--muted); font-size: 0.86rem; min-height: 1.2rem; }}
    .output {{
      min-height: 260px;
      max-height: 460px;
      overflow: auto;
      white-space: pre-wrap;
      background:
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(180deg, rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(180deg, #111d23, #071015);
      background-size: 18px 18px, 18px 18px, auto;
      color: #dce8ea;
      border: 1px solid #1e2f36;
      border-radius: 8px;
      padding: 14px;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }}
    .history-list {{ display: grid; gap: 8px; }}
    .history-item {{ width: 100%; min-width: 0; display: grid; gap: 2px; }}
    .history-item small {{ color: var(--muted); overflow-wrap: anywhere; }}
    .codex-toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 10px; }}
    .codex-toolbar select {{ width: min(100%, 260px); }}
    .codex-grid {{ display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; align-items: start; }}
    .codex-list {{ display: grid; gap: 8px; }}
    .codex-account {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px; align-items: start; border: 1px solid var(--line); border-radius: 8px; padding: 13px; background: linear-gradient(180deg, #ffffff, #f9fcfb); box-shadow: var(--shadow-tight); }}
    .codex-account-body {{ min-width: 0; display: grid; gap: 3px; }}
    .codex-account-actions {{ display: flex; align-items: flex-start; justify-content: flex-end; }}
    .codex-account strong, .codex-account small {{ display: block; overflow-wrap: anywhere; }}
    .codex-badge {{ display: inline-flex; align-items: center; align-self: start; border: 1px solid #bde0da; border-radius: 999px; padding: 4px 10px; color: var(--accent-strong); background: var(--accent-soft); font-size: 0.78rem; font-weight: 760; white-space: nowrap; }}
    .codex-account-switch {{ display: inline-flex; align-items: center; justify-content: center; min-width: 68px; min-height: 34px; padding: 8px 14px; border-radius: 7px; text-align: center; font-weight: 700; }}
    .codex-account-switch.is-current {{ border-color: #bde0da; color: var(--accent-strong); background: var(--accent-soft); }}
    .codex-account-switch[disabled] {{ opacity: 1; cursor: default; box-shadow: none; transform: none; }}
    .claude-toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 12px; }}
    .claude-console-grid {{ display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(290px, 0.65fr); gap: 12px; align-items: start; }}
    .claude-summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }}
    .claude-summary-card {{ background: linear-gradient(180deg, #ffffff, #f9fcfb); border: 1px solid var(--line); border-radius: 8px; padding: 12px; min-width: 0; box-shadow: var(--shadow-tight); }}
    .claude-summary-card .meta {{ margin: 0; }}
    .claude-side-panel {{ display: grid; gap: 12px; min-width: 0; }}
    .claude-file-actions {{ display: grid; gap: 8px; }}
    .claude-provider-list {{ display: grid; gap: 10px; }}
    .provider-status-pill {{ display: inline-flex; align-items: center; gap: 6px; width: fit-content; padding: 4px 10px; border-radius: 999px; font-size: 0.76rem; font-weight: 760; border: 1px solid var(--line); background: #fff; color: var(--muted); }}
    .provider-status-pill.ready {{ border-color: #bde0da; color: var(--accent-strong); background: var(--accent-soft); }}
    .provider-status-pill.missing {{ border-color: #f2d2a4; color: #8b5d10; background: #fff7e8; }}
    .provider-card-actions {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-start; justify-content: flex-end; }}
    .ref-button {{ display: inline; padding: 0; border: 0; background: transparent; color: #0b5cad; text-align: left; font-family: inherit; font-size: 0.92rem; font-weight: 600; overflow-wrap: anywhere; box-shadow: none; transform: none; }}
    .ref-button:hover {{ text-decoration: underline; border-color: transparent; box-shadow: none; transform: none; }}
    @media (max-width: 820px) {{
      body {{ font-size: 13px; }}
      main {{ padding: 12px 10px 28px; }}
      header {{ padding: 14px; margin-bottom: 12px; }}
      h1 {{ font-size: 1.2rem; }}
      .console-layout, .summary-grid, .policy-grid, .feedback-grid, .runtime-shell, .details-grid, .codex-grid, .codex-account, .claude-console-grid, .feedback-shell, .feedback-runs-grid, .surface-grid {{ grid-template-columns: 1fr; }}
      .view-tabs {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); width: 100%; }}
      .view-tab {{ text-align: center; padding: 8px 7px; }}
      .feedback-preview {{ height: 300px; }}
      .info-list {{ grid-template-columns: 1fr; }}
      .sidebar {{ position: static; }}
      .output {{ min-height: 220px; }}
      .panel, .metric, .policy-item, .table-wrap {{ box-shadow: 0 4px 16px rgba(12, 31, 36, 0.06); }}
      .table-wrap {{ overflow-x: visible; }}
      table, thead, tbody, tr, th, td {{ display: block; min-width: 0; width: 100%; }}
      thead {{ position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); }}
      tr {{ border-bottom: 1px solid var(--line); }}
      tr:last-child {{ border-bottom: 0; }}
      td {{ display: grid; grid-template-columns: 82px minmax(0, 1fr); gap: 9px; border-bottom: 1px solid var(--line); }}
      td:last-child {{ border-bottom: 0; }}
      td::before {{ content: attr(data-label); color: var(--muted); font-size: 0.76rem; text-transform: uppercase; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{escape(text['title'])}</h1>
      <div class="meta-row">
        <span>{escape(text['runtime_root'])}: <code>{escape(runtime_root)}</code></span>
        <span>{escape(text['persistence'])}: <code>{escape(snapshot.persistence_backend)}</code></span>
      </div>
    </header>
    <div class="console-layout">
      {actions}
      <div class="dashboard">
        {tabs}
        {workspace_overview}
        <div data-view-panel="runtime">
          {summary}
          <div class="runtime-shell">
            <div class="runtime-main">
              {feedback}
              <!-- NEXT_WORK_PANEL -->
            </div>
            <div class="runtime-side">
              <div class="details-grid">
                {maintenance}
                {attachments}
              </div>
            </div>
          </div>
          {tasks}
        </div>
        <div data-view-panel="codex" hidden>
          {codex_panel}
        </div>
        <div data-view-panel="claude" hidden>
          {claude_panel}
        </div>
        <div data-view-panel="feedback" hidden>
          {feedback_panel}
        </div>
      </div>
    </div>
  </main>
  {script}
</body>
</html>"""


def write_runtime_snapshot_html(
    snapshot: RuntimeSnapshot,
    output_path: Path,
    language: str = "zh-CN",
    interactive: bool = False,
    target_options: list[str] | None = None,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(
        output_path,
        render_runtime_snapshot_html(snapshot, language=language, interactive=interactive, target_options=target_options),
        encoding="utf-8",
    )
    return output_path


def _render_metric(title: str, value: str, caption: str) -> str:
    return "\n".join(
        [
            "<div class='metric'>",
            f"<span>{escape(title)}</span>",
            f"<strong>{escape(value)}</strong>",
            f"<small>{escape(caption)}</small>",
            "</div>",
        ]
    )


def _render_view_tabs(text: dict[str, str]) -> str:
    return "\n".join(
        [
            "<div class='view-tabs' role='tablist' aria-label='Operator view'>",
            f"<button type='button' class='view-tab' role='tab' aria-selected='true' data-view-tab='runtime'>{escape(text['runtime_view'])}</button>",
            f"<button type='button' class='view-tab' role='tab' aria-selected='false' data-view-tab='codex'>{escape(text['codex_view'])}</button>",
            f"<button type='button' class='view-tab' role='tab' aria-selected='false' data-view-tab='claude'>{escape(text['claude_view'])}</button>",
            f"<button type='button' class='view-tab' role='tab' aria-selected='false' data-view-tab='feedback'>{escape(text['feedback_view'])}</button>",
            "</div>",
        ]
    )


def _render_workspace_overview(text: dict[str, str], *, interactive: bool) -> str:
    surfaces = [
        ("runtime", text["runtime_view"], text["runtime_surface_caption"], True),
        ("codex", text["codex_view"], text["codex_surface_caption"], False),
        ("claude", text["claude_view"], text["claude_surface_caption"], False),
        ("feedback", text["feedback_view"], text["feedback_surface_caption"], False),
    ]
    cards: list[str] = []
    for surface_id, title, caption, active in surfaces:
        badge = text["surface_current"] if active else text["open_surface"]
        button_label = text["surface_current"] if active else text["open_surface"]
        button_attrs = " disabled" if active or not interactive else ""
        button_class = " class='primary'" if not active and interactive else ""
        summary_lines = [
            text["surface_loading"],
            caption,
            _runtime_surface_default_summary(text) if surface_id == "runtime" else _surface_action_text(surface_id, text),
        ]
        cards.append(
            "\n".join(
                [
                    f"<article class='surface-card{' active' if active else ''}' data-surface-card='{escape(surface_id)}'>",
                    "<div class='surface-card-head'>",
                    f"<span class='surface-card-title'>{escape(title)}</span>",
                    f"<span class='surface-badge' data-surface-badge='{escape(surface_id)}'>{escape(badge)}</span>",
                    "</div>",
                    f"<div class='surface-summary' data-surface-summary='{escape(surface_id)}'>{''.join(f'<p>{escape(line)}</p>' for line in summary_lines if line)}</div>",
                    f"<button type='button'{button_class} data-open-view='{escape(surface_id)}'{button_attrs}>{escape(button_label)}</button>",
                    "</article>",
                ]
            )
        )

    return "\n".join(
        [
            "<section class='panel'>",
            f"<h2>{escape(text['workspace_overview'])}</h2>",
            f"<p class='meta'>{escape(text['workspace_overview_caption'])}</p>",
            "<div class='surface-grid'>",
            *cards,
            "</div>",
            "</section>",
        ]
    )


def _runtime_surface_default_summary(text: dict[str, str]) -> str:
    return text["surface_runtime_action"]


def _surface_action_text(surface_id: str, text: dict[str, str]) -> str:
    mapping = {
        "runtime": text["surface_runtime_action"],
        "codex": text["surface_codex_action"],
        "claude": text["surface_claude_action"],
        "feedback": text["surface_feedback_action"],
    }
    return mapping.get(surface_id, "")


def _render_maintenance(snapshot: RuntimeSnapshot, text: dict[str, str]) -> str:
    return "\n".join(
        [
            "<section class='section'>",
            f"<h2>{escape(text['maintenance'])}</h2>",
            "<div class='policy-grid'>",
            _render_policy_item(text["stage"], snapshot.maintenance.stage, text),
            _render_policy_item(text["compatibility"], snapshot.maintenance.compatibility_policy_ref, text),
            _render_policy_item(text["upgrade"], snapshot.maintenance.upgrade_policy_ref, text),
            _render_policy_item(text["triage"], snapshot.maintenance.triage_policy_ref, text),
            _render_policy_item(text["deprecation"], snapshot.maintenance.deprecation_policy_ref, text),
            _render_policy_item(text["retirement"], snapshot.maintenance.retirement_policy_ref, text),
            "</div>",
            "</section>",
        ]
    )


def _render_tasks(snapshot: RuntimeSnapshot, text: dict[str, str], *, interactive: bool) -> str:
    if not snapshot.tasks:
        return "\n".join(
            [
                "<section class='section'>",
                f"<h2>{escape(text['tasks'])}</h2>",
                f"<div class='empty-state'>{escape(text['no_tasks'])}</div>",
                "</section>",
            ]
        )

    rows = "\n".join(_render_task_row(task, text, interactive=interactive) for task in snapshot.tasks)
    return "\n".join(
        [
            "<section class='section'>",
            f"<h2>{escape(text['tasks'])}</h2>",
            "<div class='table-wrap'>",
            "<table>",
            (
                "<thead><tr>"
                f"<th>{escape(text['task'])}</th>"
                f"<th>{escape(text['state'])}</th>"
                f"<th>{escape(text['goal'])}</th>"
                f"<th>{escape(text['outputs'])}</th>"
                "</tr></thead>"
            ),
            f"<tbody>{rows}</tbody>",
            "</table>",
            "</div>",
            "</section>",
        ]
    )


def _render_task_row(task, text: dict[str, str], *, interactive: bool) -> str:
    interaction = _humanize_runtime_value(task.interaction_posture or text["not_recorded"], language=text["html_lang"])
    state_class = _state_class(task.current_state)
    state_label = _humanize_runtime_value(task.current_state, language=text["html_lang"])
    return "\n".join(
        [
            "<tr>",
            f"<td data-label='{escape(text['task'])}'>",
            f"<div class='task-id'>{escape(task.task_id)}</div>",
            f"<div class='meta'>{escape(text['run'])}: <code>{escape(task.active_run_id or text['missing'])}</code></div>",
            f"<div class='meta'>{escape(text['workspace'])}: <code>{escape(task.workspace_root or text['missing'])}</code></div>",
            "</td>",
            f"<td data-label='{escape(text['state'])}'>",
            f"<div class='state {state_class}'>{escape(state_label)}</div>",
            f"<div class='meta'>{escape(text['interaction'])}: {escape(interaction)}</div>",
            f"<div class='meta'>{escape(text['rollback'])}: <code>{escape(task.rollback_ref or text['missing'])}</code></div>",
            "</td>",
            f"<td data-label='{escape(text['goal'])}'>{escape(task.goal)}</td>",
            f"<td data-label='{escape(text['outputs'])}'><div class='refs'>",
            _render_list(text["approvals"], task.approval_ids, text, interactive=interactive),
            _render_list("执行输出" if text["html_lang"] == "zh-CN" else "Execution outputs", task.artifact_refs, text, interactive=interactive),
            _render_list("运行证据" if text["html_lang"] == "zh-CN" else "Evidence", task.evidence_refs, text, interactive=interactive),
            _render_list(text["verification"], task.verification_refs, text, interactive=interactive),
            "</div></td>",
            "</tr>",
        ]
    )


def _render_attachments(snapshot: RuntimeSnapshot, text: dict[str, str], *, interactive: bool) -> str:
    if not snapshot.attachments:
        return "\n".join(
            [
                "<section class='section'>",
                f"<h2>{escape(text['attachments'])}</h2>",
                f"<div class='empty-state'>{escape(text['no_attachments'])}</div>",
                "</section>",
            ]
        )

    rows = "\n".join(_render_attachment_row(attachment, text, interactive=interactive) for attachment in snapshot.attachments)
    return "\n".join(
        [
            "<section class='section'>",
            f"<h2>{escape(text['attachments'])}</h2>",
            "<div class='table-wrap'>",
            "<table>",
            (
                "<thead><tr>"
                f"<th>{escape(text['repo'])}</th>"
                f"<th>{escape(text['state'])}</th>"
                f"<th>{escape(text['adapter'])}</th>"
                f"<th>{escape(text['diagnostics'])}</th>"
                "</tr></thead>"
            ),
            f"<tbody>{rows}</tbody>",
            "</table>",
            "</div>",
            "</section>",
        ]
    )


def _render_attachment_row(attachment, text: dict[str, str], *, interactive: bool) -> str:
    state_class = "danger" if attachment.fail_closed else _state_class(attachment.binding_state)
    state_label = _humanize_runtime_value(attachment.binding_state, language=text["html_lang"])
    adapter_label = _humanize_runtime_value(attachment.adapter_preference or text["missing"], language=text["html_lang"])
    gate_profile_label = _humanize_runtime_value(attachment.gate_profile or text["missing"], language=text["html_lang"])
    return "\n".join(
        [
            "<tr>",
            f"<td data-label='{escape(text['repo'])}'>",
            f"<div class='task-id'>{escape(attachment.repo_id or text['unknown_repo'])}</div>",
            f"<div class='meta'>{escape(text['binding'])}: <code>{escape(attachment.binding_id or text['missing'])}</code></div>",
            f"<div class='meta'>{escape(text['light_pack'])}: {_render_ref_value(attachment.light_pack_path, interactive=interactive)}</div>",
            "</td>",
            f"<td data-label='{escape(text['state'])}'>",
            f"<div class='state {state_class}'>{escape(state_label)}</div>",
            f"<div class='meta'>{escape(text['fail_closed'])}: {escape(_humanize_bool(attachment.fail_closed, language=text['html_lang']))}</div>",
            "</td>",
            f"<td data-label='{escape(text['adapter'])}'>",
            f"<div>{escape(text['preference'])}: <code>{escape(adapter_label)}</code></div>",
            f"<div class='meta'>{escape(text['gate_profile'])}: <code>{escape(gate_profile_label)}</code></div>",
            "</td>",
            f"<td data-label='{escape(text['diagnostics'])}'>",
            f"<div>{escape(text['reason'])}: {escape(attachment.reason or text['none'])}</div>",
            f"<div class='meta'>{escape(text['remediation'])}: {escape(attachment.remediation or text['none'])}</div>",
            "</td>",
            "</tr>",
        ]
    )


def _render_list(title: str, values: list[str], text: dict[str, str], *, interactive: bool) -> str:
    if not values:
        return f"<div><span class='ref-title'>{escape(title)}</span><span class='meta'>{escape(text['none'])}</span></div>"
    items = "".join(f"<li>{_render_ref_value(value, interactive=interactive)}</li>" for value in values)
    return f"<div><span class='ref-title'>{escape(title)}</span><ul>{items}</ul></div>"


def _render_ref_value(value: str, *, interactive: bool) -> str:
    if not interactive or not _is_viewable_ref(value):
        return f"<code>{escape(value)}</code>"
    return (
        "<button type='button' class='ref-button' data-ref='"
        + escape(value, quote=True)
        + "'>"
        + escape(value)
        + "</button>"
    )


def _is_viewable_ref(value: str) -> bool:
    return "/" in value or "\\" in value


def _render_policy_item(title: str, value: str | None, text: dict[str, str]) -> str:
    rendered_value = _humanize_runtime_value(value or text["missing"], language=text["html_lang"])
    return "\n".join(
        [
            "<div class='policy-item'>",
            f"<span class='policy-label'>{escape(title)}</span>",
            f"<code>{escape(rendered_value)}</code>",
            "</div>",
        ]
    )


def _humanize_bool(value: bool, *, language: str) -> str:
    if language == "zh-CN":
        return "是" if value else "否"
    return "yes" if value else "no"


def _humanize_runtime_value(value: str, *, language: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        return normalized
    lower = normalized.lower()
    zh_map = {
        "missing": "未配置",
        "not recorded": "未记录",
        "completed": "已完成",
        "delivered": "已完成",
        "running": "执行中",
        "queued": "排队中",
        "failed": "失败",
        "attached": "已接入",
        "detached": "未接入",
        "native_attach": "原生接入",
        "manual_handoff": "人工接力",
        "process_bridge": "进程桥接",
        "quick": "快速",
        "full": "完整",
        "l1": "L1 基础",
        "l2": "L2 标准",
        "l3": "L3 深度",
    }
    en_map = {
        "native_attach": "native attach",
        "manual_handoff": "manual handoff",
        "process_bridge": "process bridge",
    }
    if language == "zh-CN":
        return zh_map.get(lower, normalized)
    return en_map.get(lower, normalized)


def _render_actions(text: dict[str, str], *, language: str, interactive: bool, target_options: list[str]) -> str:
    if not interactive:
        return "\n".join(
            [
                "<aside class='sidebar'>",
                "<section class='panel'>",
                f"<h2>{escape(text['static_snapshot'])}</h2>",
                f"<p class='meta'>{escape(text['interactive_required'])}</p>",
                "</section>",
                "</aside>",
            ]
        )

    action_groups = [
        (
            text["quick_actions"],
            True,
            [
                ("fast_feedback", text["fast_feedback_action"], "primary", ""),
                ("readiness", text["readiness_action"], "primary", ""),
                ("feedback_report", text["feedback_report_action"], "", ""),
            ],
        ),
        (
            text["target_actions"],
            False,
            [
                ("targets", text["targets_action"], "", ""),
                ("daily_all", text["daily_all_action"], "", ""),
                ("governance_baseline_all", text["governance_baseline_action"], "danger", text["confirm_mutating"]),
                ("apply_all_features", text["apply_all_action"], "danger", text["confirm_mutating"]),
                ("cleanup_targets", text["cleanup_targets_action"], "danger", text["confirm_managed_cleanup"]),
                ("uninstall_governance", text["uninstall_governance_action"], "danger", text["confirm_governance_uninstall"]),
            ],
        ),
        (
            text["rule_actions"],
            False,
            [
                ("rules_dry_run", text["rules_dry_run_action"], "", ""),
                ("rules_apply", text["rules_apply_action"], "danger", text["confirm_mutating"]),
                ("evolution_review", text["evolution_review_action"], "", ""),
                ("experience_review", text["experience_review_action"], "", ""),
                ("evolution_materialize", text["evolution_materialize_action"], "danger", text["confirm_evolution_materialize"]),
                ("core_principle_materialize", text["core_principle_action"], "", ""),
            ],
        ),
    ]

    rendered_groups: list[str] = []
    for group_title, expanded, action_items in action_groups:
        buttons = []
        for action_id, label, class_name, confirm in action_items:
            class_attr = f" class='{class_name}'" if class_name else ""
            confirm_attr = f" data-confirm='{escape(confirm, quote=True)}'" if confirm else ""
            buttons.append(
                f"<button type='button'{class_attr} data-action='{escape(action_id)}'{confirm_attr}>{escape(label)}</button>"
            )
            buttons.append(f"<p class='meta shortcut-blocked' data-action-blocked='{escape(action_id)}'></p>")
        if expanded:
            rendered_groups.extend(
                [
                    "<div class='action-group'>",
                    f"<p class='action-group-title'>{escape(group_title)}</p>",
                    "<div class='action-list'>",
                    *buttons,
                    "</div>",
                    "</div>",
                ]
            )
        else:
            rendered_groups.extend(
                [
                    "<details class='foldout'>",
                    f"<summary>{escape(group_title)}</summary>",
                    "<div class='action-list'>",
                    *buttons,
                    "</div>",
                    "</details>",
                ]
            )
    target_choices = [("__all__", text["all_targets"])] + [(target, target) for target in target_options]
    target_select_options = "".join(
        f"<option value='{escape(value, quote=True)}'>{escape(label)}</option>"
        for value, label in target_choices
    )
    target_checkboxes = [
        (
            "<label class='checkbox-row target-option'>"
            f"<input type='checkbox' data-ui-target-option='{escape(target, quote=True)}'> "
            f"<span>{escape(target)}</span>"
            "</label>"
        )
        for target in target_options
    ]

    return "\n".join(
        [
            "<aside class='sidebar'>",
            "<section class='panel'>",
            f"<h2>{escape(text['actions'])}</h2>",
            _render_shortcut_entrypoints(text),
            "<div class='action-group'>",
            f"<p class='action-group-title'>{escape(text['page_actions'])}</p>",
            f"<button type='button' data-refresh='1'>{escape(text['refresh'])}</button>",
            "</div>",
            *rendered_groups,
            "</section>",
            "<section class='panel'>",
            f"<h2>{escape(text['settings'])}</h2>",
            "<div class='setting-grid'>",
            f"<label>{escape(text['language'])}<select id='ui-language'><option value='zh-CN' {'selected' if language == 'zh-CN' else ''}>中文</option><option value='en' {'selected' if language == 'en' else ''}>English</option></select></label>",
            f"<label hidden>{escape(text['target'])}<select id='ui-target'>{target_select_options}</select></label>",
            "<div class='target-picker' role='group' aria-labelledby='ui-target-picker-title'>",
            "<div class='target-picker-head'>",
            f"<span class='target-picker-title' id='ui-target-picker-title'>{escape(text['target_selection'])}</span>",
            f"<span class='meta'>{escape(text['target_selection_hint'])}</span>",
            "</div>",
            f"<label class='checkbox-row'><input id='ui-target-all' type='checkbox' checked> {escape(text['all_targets'])}</label>",
            "<div id='ui-target-list' class='target-checkbox-list'>",
            *target_checkboxes,
            "</div>",
            "</div>",
            f"<label>{escape(text['mode'])}<select id='ui-mode'><option value='quick'>quick</option><option value='full'>full</option><option value='l1'>l1</option><option value='l2'>l2</option><option value='l3'>l3</option></select></label>",
            f"<label class='checkbox-row'><input id='ui-dry-run' type='checkbox'> {escape(text['dry_run'])}</label>",
            "<details class='foldout'>",
            f"<summary>{escape(text['advanced_settings'])}</summary>",
            f"<label>{escape(text['parallelism'])}<input id='ui-parallelism' type='number' min='1' max='16' value='1'></label>",
            f"<label>{escape(text['milestone'])}<input id='ui-milestone' type='text' value='milestone'></label>",
            f"<label class='checkbox-row'><input id='ui-fail-fast' type='checkbox'> {escape(text['fail_fast'])}</label>",
            f"<label class='checkbox-row danger-row'><input id='ui-apply-removal' type='checkbox'> {escape(text['apply_removal'])}</label>",
            f"<p class='meta'>{escape(text['apply_removal_hint'])}</p>",
            "</details>",
            "</div>",
            "</section>",
            "</aside>",
        ]
    )


def _render_shortcut_entrypoints(text: dict[str, str]) -> str:
    items = [
        ("fast_feedback", text["shortcut_fast"], text["shortcut_fast_command"], text["shortcut_fast_caption"], True),
        ("readiness", text["shortcut_daily"], text["shortcut_daily_command"], text["shortcut_daily_caption"], False),
    ]
    rendered: list[str] = []
    for action_id, title, command, caption, recommended in items:
        class_name = "shortcut-item recommended" if recommended else "shortcut-item"
        rendered.append(
            "\n".join(
                [
                    f"<article class='{class_name}'>",
                    "<div class='shortcut-head'>",
                    f"<span class='shortcut-title'>{escape(title)}</span>",
                    f"<button type='button' class='primary' data-action='{escape(action_id)}'>{escape(text['run_now'])}</button>",
                    "</div>",
                    f"<code class='shortcut-command' aria-label='{escape(text['command_label'])}'>{escape(command)}</code>",
                    f"<p class='meta'>{escape(caption)}</p>",
                    f"<p class='meta shortcut-blocked' data-action-blocked='{escape(action_id)}'></p>",
                    "</article>",
                ]
            )
        )
    return "\n".join(
        [
            "<div class='action-group'>",
            f"<p class='action-group-title'>{escape(text['recommended_next'])}</p>",
            f"<p class='meta'>{escape(text['shortcut_entry_caption'])}</p>",
            "<div class='shortcut-list'>",
            *rendered,
            "</div>",
            "</div>",
        ]
    )


def _render_feedback(text: dict[str, str], *, interactive: bool) -> str:
    if not interactive:
        return ""
    return "\n".join(
        [
            "<section class='feedback-grid'>",
            "<div class='panel output-panel'>",
            f"<h2>{escape(text['command_output'])}</h2>",
            f"<div id='ui-status' class='status-line'>{escape(text['ready'])}</div>",
            "<pre id='ui-output' class='output'></pre>",
            "</div>",
            "<div class='panel'>",
            f"<h2>{escape(text['history'])}</h2>",
            f"<div id='ui-history' class='history-list'><p class='meta'>{escape(text['no_history'])}</p></div>",
            f"<button type='button' data-clear-history='1'>{escape(text['clear_history'])}</button>",
            "</div>",
            "</section>",
        ]
    )


def _render_codex_panel(text: dict[str, str], *, interactive: bool) -> str:
    if not interactive:
        return "\n".join(
            [
                "<section class='panel'>",
                f"<h2>{escape(text['codex_console'])}</h2>",
                f"<p class='meta'>{escape(text['interactive_required'])}</p>",
                "</section>",
            ]
        )
    return "\n".join(
        [
            "<section class='panel'>",
            f"<h2>{escape(text['codex_console'])}</h2>",
            "<div class='codex-toolbar'>",
            f"<button type='button' data-codex-refresh='1' title='{escape(text['codex_refresh_if_stale'])}'>{escape(text['codex_refresh'])}</button>",
            f"<button type='button' data-codex-refresh-online='1' title='{escape(text['codex_refresh_online_hint'])}'>{escape(text['codex_refresh_online'])}</button>",
            f"<button type='button' data-codex-usage='1'>{escape(text['codex_open_usage'])}</button>",
            "</div>",
            "<div class='codex-grid'>",
            "<div>",
            f"<div class='status-line' id='codex-cache-state'>{escape(text['panel_cache_state'])}: {escape(text['panel_cache_cold'])}</div>",
            "<div id='codex-accounts' class='codex-list'></div>",
            "</div>",
            "</div>",
            "</section>",
        ]
    )


def _render_claude_panel(text: dict[str, str], *, interactive: bool) -> str:
    if not interactive:
        return "\n".join(
            [
                "<section class='panel'>",
                f"<h2>{escape(text['claude_console'])}</h2>",
                f"<p class='meta'>{escape(text['interactive_required'])}</p>",
                "</section>",
            ]
        )
    return "\n".join(
        [
            "<section class='panel'>",
            f"<h2>{escape(text['claude_console'])}</h2>",
            "<div class='claude-toolbar'>",
            f"<button type='button' data-claude-refresh='1'>{escape(text['claude_refresh'])}</button>",
            f"<button type='button' data-claude-optimize-preview='1'>{escape(text['claude_optimize_preview'])}</button>",
            f"<button type='button' class='primary' data-claude-optimize-apply='1' data-confirm='{escape(text['claude_apply_recommended_confirm'])}'>{escape(text['claude_optimize_apply'])}</button>",
            "</div>",
            "<div class='claude-console-grid'>",
            "<div class='claude-side-panel'>",
            "<div id='claude-providers' class='claude-provider-list'></div>",
            "</div>",
            "<div class='claude-side-panel'>",
            "<section class='panel'>",
            f"<h3>{escape(text['claude_local_files'])}</h3>",
            f"<p class='meta'>{escape(text['claude_file_hint'])}</p>",
            "<div class='claude-file-actions'>",
            f"<button type='button' data-claude-file='settings'>{escape(text['claude_view_settings'])}</button>",
            f"<button type='button' data-claude-file='profiles'>{escape(text['claude_view_profiles'])}</button>",
            f"<button type='button' data-claude-file='switcher'>{escape(text['claude_view_switcher'])}</button>",
            "</div>",
            "</section>",
            "</div>",
            "</div>",
            "</section>",
        ]
    )


def _render_host_feedback_panel(text: dict[str, str], *, interactive: bool) -> str:
    if not interactive:
        return "\n".join(
            [
                "<section class='panel'>",
                f"<h2>{escape(text['feedback_console'])}</h2>",
                f"<p class='meta'>{escape(text['interactive_required'])}</p>",
                "</section>",
            ]
        )
    return "\n".join(
        [
            "<section class='panel'>",
            f"<h2>{escape(text['feedback_console'])}</h2>",
            "<div class='claude-toolbar'>",
            f"<button type='button' data-feedback-refresh='1'>{escape(text['feedback_refresh'])}</button>",
            "</div>",
            f"<div class='status-line' id='feedback-status'>{escape(text['feedback_status'])}: {escape(text['feedback_loading'])}</div>",
            f"<div class='status-line' id='feedback-cache-state'>{escape(text['panel_cache_state'])}: {escape(text['panel_cache_cold'])}</div>",
            f"<div class='status-line' id='feedback-generated-at'>{escape(text['feedback_generated_at'])}: {escape(text['not_recorded'])}</div>",
            "<div id='feedback-summary' class='feedback-summary-grid'></div>",
            "<div class='feedback-shell'>",
            "<div class='feedback-column'>",
            "<section class='panel'>",
            f"<h2>{escape(text['feedback_dimensions'])}</h2>",
            "<div id='feedback-dimensions' class='status-pill-list'></div>",
            "</section>",
            "<section class='panel'>",
            f"<h2>{escape(text['feedback_recommendations'])}</h2>",
            "<div id='feedback-recommendations' class='refs'></div>",
            "</section>",
            "<section class='panel'>",
            f"<h2>{escape(text['feedback_links'])}</h2>",
            "<div class='feedback-links'>",
            "<div id='feedback-report-link'></div>",
            "<div id='feedback-guide-link'></div>",
            "<div id='feedback-guide-link-en'></div>",
            "</div>",
            "</section>",
            "</div>",
            "<div class='feedback-column'>",
            "<section class='panel feedback-preview-card'>",
            f"<h2>{escape(text['feedback_preview'])}</h2>",
            f"<pre id='feedback-preview' class='feedback-preview'>{escape(text['feedback_preview_idle'])}</pre>",
            "</section>",
            "</div>",
            "</div>",
            "<section class='panel'>",
            f"<h2>{escape(text['feedback_latest_runs'])}</h2>",
            f"<p class='meta'>{escape(text['feedback_latest_runs_hint'])}</p>",
            "<div id='feedback-latest-runs' class='feedback-runs-grid'></div>",
            "</section>",
            "</section>",
        ]
    )


def _render_interactive_script(
    text: dict[str, str],
    *,
    language: str,
    total_tasks: int,
    approval_count: int,
    verification_count: int,
    attachment_count: int,
    fail_closed_count: int,
) -> str:
    return f"""
<script>
(() => {{
  const output = document.getElementById('ui-output');
  const status = document.getElementById('ui-status');
  const outputPanel = output.closest('.panel');
  const languageSelect = document.getElementById('ui-language');
  const target = document.getElementById('ui-target');
  const targetAll = document.getElementById('ui-target-all');
  const targetOptions = Array.from(document.querySelectorAll('input[data-ui-target-option]'));
  const mode = document.getElementById('ui-mode');
  const parallelism = document.getElementById('ui-parallelism');
  const milestone = document.getElementById('ui-milestone');
  const failFast = document.getElementById('ui-fail-fast');
  const dryRun = document.getElementById('ui-dry-run');
  const applyRemoval = document.getElementById('ui-apply-removal');
  const historyList = document.getElementById('ui-history');
  const codexAccounts = document.getElementById('codex-accounts');
  const codexCacheState = document.getElementById('codex-cache-state');
  const claudeProviders = document.getElementById('claude-providers');
  const feedbackStatus = document.getElementById('feedback-status');
  const feedbackCacheState = document.getElementById('feedback-cache-state');
  const feedbackGeneratedAt = document.getElementById('feedback-generated-at');
  const feedbackSummary = document.getElementById('feedback-summary');
  const feedbackDimensions = document.getElementById('feedback-dimensions');
  const feedbackRecommendations = document.getElementById('feedback-recommendations');
  const feedbackLatestRuns = document.getElementById('feedback-latest-runs');
  const feedbackReportLink = document.getElementById('feedback-report-link');
  const feedbackGuideLink = document.getElementById('feedback-guide-link');
  const feedbackGuideLinkEn = document.getElementById('feedback-guide-link-en');
  const feedbackPreview = document.getElementById('feedback-preview');
  const nextWorkAction = document.getElementById('next-work-action');
  const nextWorkRecommendation = document.getElementById('next-work-recommendation');
  const nextWorkState = document.getElementById('next-work-state');
  const nextWorkWhy = document.getElementById('next-work-why');
  const nextWorkJson = document.getElementById('next-work-json');
  const nextWorkCacheState = document.getElementById('next-work-cache-state');
  const historyKey = 'governed-runtime-operator-history';
  const codexCacheKey = 'governed-runtime-operator-codex-status';
  const claudeCacheKey = 'governed-runtime-operator-claude-status';
  const feedbackCacheKey = 'governed-runtime-operator-feedback-summary';
  const nextWorkCacheKey = 'governed-runtime-operator-next-work';
  const surfaceOpenLabel = {text['open_surface']!r};
  const surfaceCurrentLabel = {text['surface_current']!r};
  const runtimeSurfaceSummaryTemplate = {text['surface_runtime_summary']!r};
  const runtimeSurfaceDetailTemplate = {text['surface_runtime_detail']!r};
  const runtimeSurfaceActionText = {text['surface_runtime_action']!r};
  const codexSurfaceActionText = {text['surface_codex_action']!r};
  const claudeSurfaceActionText = {text['surface_claude_action']!r};
  const feedbackSurfaceActionText = {text['surface_feedback_action']!r};
  const managedRemovalActions = new Set(['cleanup_targets', 'uninstall_governance']);
  const defaultManagedRemovalActions = new Set(['apply_all_features']);
  const codexAutoRefreshAgeSeconds = 90;
  const codexRefreshCooldownMs = 15000;
  let codexLoaded = false;
  let claudeLoaded = false;
  let feedbackLoaded = false;
  let nextWorkLoaded = false;
  let lastClaudePayload = null;
  let lastCodexPayload = null;
  let lastCodexRefreshEpoch = 0;
  let lastNextWorkPayload = null;

  function readHistory() {{
    try {{
      const value = JSON.parse(window.localStorage.getItem(historyKey) || '[]');
      return Array.isArray(value) ? value : [];
    }} catch (error) {{
      return [];
    }}
  }}

  function writeHistory(items) {{
    window.localStorage.setItem(historyKey, JSON.stringify(items.slice(0, 12)));
  }}

  function readPanelCache(key) {{
    try {{
      const value = JSON.parse(window.localStorage.getItem(key) || 'null');
      return value && typeof value === 'object' ? value : null;
    }} catch (error) {{
      return null;
    }}
  }}

  function writePanelCache(key, payload) {{
    try {{
      window.localStorage.setItem(key, JSON.stringify(payload));
    }} catch (error) {{
      return;
    }}
  }}

  function formatCachedAtLabel(value) {{
    const raw = String(value || '').trim();
    if (!raw) {{
      return '';
    }}
    const parsed = new Date(raw);
    if (Number.isNaN(parsed.getTime())) {{
      return raw;
    }}
    return parsed.toLocaleTimeString([], {{ hour: '2-digit', minute: '2-digit', second: '2-digit' }});
  }}

  function setPanelCacheState(kind, state, cachedAt) {{
    const target = kind === 'codex'
      ? codexCacheState
      : (kind === 'feedback' ? feedbackCacheState : (kind === 'next-work' ? nextWorkCacheState : null));
    if (!target) {{
      return;
    }}
    const label = kind === 'codex'
      ? (currentUiLanguage() === 'zh-CN' ? 'Codex 状态' : 'Codex state')
      : (kind === 'feedback'
        ? {text['feedback_status']!r}
        : (currentUiLanguage() === 'zh-CN' ? 'next-work 状态' : 'next-work state'));
    const stateLabels = {{
      cold: {text['panel_cache_cold']!r},
      cached: {text['panel_cache_cached']!r},
      refreshing: {text['panel_cache_refreshing']!r},
      ready: {text['panel_cache_ready']!r},
      error: {text['panel_cache_error']!r},
    }};
    const suffix = formatCachedAtLabel(cachedAt);
    target.textContent = suffix
      ? `${{label}}: ${{stateLabels[state] || state}} · ${{suffix}}`
      : `${{label}}: ${{stateLabels[state] || state}}`;
  }}

  function isUsageSnapshotStale(snapshot) {{
    const freshness = snapshot && snapshot.freshness ? snapshot.freshness : null;
    if (!freshness) {{
      return true;
    }}
    if (freshness.is_stale) {{
      return true;
    }}
    const ageSeconds = Number(freshness.age_seconds);
    if (!Number.isFinite(ageSeconds)) {{
      return true;
    }}
    return ageSeconds > codexAutoRefreshAgeSeconds;
  }}

  function shouldHydrateCodexCache(payload) {{
    if (!payload || typeof payload !== 'object') {{
      return false;
    }}
    const active = payload.active_account && typeof payload.active_account === 'object'
      ? payload.active_account
      : ((Array.isArray(payload.accounts) ? payload.accounts.find((item) => item && item.active) : null) || null);
    const snapshot = active && active.usage_snapshot && typeof active.usage_snapshot === 'object'
      ? active.usage_snapshot
      : null;
    return !!snapshot && !isUsageSnapshotStale(snapshot);
  }}

  function hydratePanelCache(kind, key) {{
    const cached = readPanelCache(key);
    if (!cached) {{
      setPanelCacheState(kind, 'cold');
      return false;
    }}
    if (kind === 'codex') {{
      if (!shouldHydrateCodexCache(cached)) {{
        setPanelCacheState(kind, 'cold');
        return false;
      }}
      renderCodexStatus(cached);
      codexLoaded = true;
    }} else if (kind === 'claude') {{
      renderClaudeStatus(cached);
      claudeLoaded = true;
    }} else if (kind === 'feedback') {{
      renderFeedbackSummary(cached);
      feedbackLoaded = true;
    }} else {{
      renderNextWorkSummary(cached);
      nextWorkLoaded = true;
    }}
    setPanelCacheState(kind, 'cached', cached.cached_at);
    return true;
  }}

  function escapeHtml(value) {{
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }}

  function setSurfaceSummary(surface, lines) {{
    const target = document.querySelector(`[data-surface-summary="${{surface}}"]`);
    if (!target) {{
      return;
    }}
    const items = Array.isArray(lines)
      ? lines.map((item) => String(item || '').trim()).filter(Boolean)
      : [];
    target.innerHTML = items.map((item) => `<p>${{escapeHtml(item)}}</p>`).join('');
  }}

  function updateRuntimeSurfaceSummary() {{
    const summary = runtimeSurfaceSummaryTemplate
      .replace('{{tasks}}', String({total_tasks}))
      .replace('{{approvals}}', String({approval_count}))
      .replace('{{verification}}', String({verification_count}));
    const detail = runtimeSurfaceDetailTemplate
      .replace('{{attachments}}', String({attachment_count}))
      .replace('{{fail_closed}}', String({fail_closed_count}));
    setSurfaceSummary('runtime', [summary, detail, runtimeSurfaceActionText]);
  }}

  function updateCodexSurfaceSummary(payload) {{
    const accounts = Array.isArray(payload && payload.accounts) ? payload.accounts : [];
    const active = accounts.find((item) => item && item.active) || accounts[0] || null;
    const usage = payload && payload.usage ? payload.usage : {{}};
    const config = payload && payload.config ? payload.config : {{}};
    const snapshot = active && active.snapshot_status ? active.snapshot_status : (payload && payload.snapshot_status ? payload.snapshot_status : null);
    setSurfaceSummary('codex', [
      active ? codexAccountLabel(active) : (currentUiLanguage() === 'zh-CN' ? '未识别当前账号' : 'No active account'),
      formatConfigHealth(config),
      formatCodexSnapshotStatus(snapshot),
      usage && usage.source
        ? [formatUsageSourceLabel(usage.source), formatUsageFreshnessLabel(usage)].filter(Boolean).join(' · ')
        : codexSurfaceActionText,
    ]);
  }}

  function updateClaudeSurfaceSummary(payload) {{
    const provider = payload && payload.active_provider ? payload.active_provider : null;
    const config = payload && payload.config ? payload.config : {{}};
    setSurfaceSummary('claude', [
      provider && (provider.label || provider.name)
        ? (provider.label || provider.name)
        : (currentUiLanguage() === 'zh-CN' ? '未识别当前 Provider' : 'No active provider'),
      provider ? (provider.credential_present ? {text['claude_credential_ready']!r} : {text['claude_missing_credential']!r})
        : (currentUiLanguage() === 'zh-CN' ? '凭据状态未知' : 'Credential status unknown'),
      formatConfigHealth(config) || claudeSurfaceActionText,
    ]);
  }}

  function updateFeedbackSurfaceSummary(payload) {{
    const summary = payload && payload.summary ? payload.summary : {{}};
    const firstRecommendation = payload && Array.isArray(payload.recommendations) && payload.recommendations.length
      ? String(payload.recommendations[0] || '').trim()
      : '';
    setSurfaceSummary('feedback', [
      currentUiLanguage() === 'zh-CN'
        ? `总状态 ${{formatFeedbackStatusLabel(payload && payload.status)}}`
        : `Overall ${{formatFeedbackStatusLabel(payload && payload.status)}}`,
      `Codex ${{formatFeedbackStatusLabel(summary.codex_host_status)}} · Claude ${{formatFeedbackStatusLabel(summary.claude_host_status)}}`,
      firstRecommendation || feedbackSurfaceActionText,
    ]);
  }}

  function activateView(selected) {{
    document.querySelectorAll('[data-view-tab]').forEach((tab) => {{
      const isSelected = tab.getAttribute('data-view-tab') === selected;
      tab.setAttribute('aria-selected', String(isSelected));
    }});
    document.querySelectorAll('[data-view-panel]').forEach((panel) => {{
      panel.hidden = panel.getAttribute('data-view-panel') !== selected;
    }});
    document.querySelectorAll('[data-surface-card]').forEach((card) => {{
      const isSelected = card.getAttribute('data-surface-card') === selected;
      card.classList.toggle('active', isSelected);
      const badge = card.querySelector('[data-surface-badge]');
      if (badge) {{
        badge.textContent = isSelected ? surfaceCurrentLabel : surfaceOpenLabel;
      }}
      const button = card.querySelector('button[data-open-view]');
      if (button) {{
        button.disabled = isSelected;
        button.classList.toggle('primary', !isSelected);
        button.textContent = isSelected ? surfaceCurrentLabel : surfaceOpenLabel;
      }}
    }});
    if (selected === 'codex' && !codexLoaded) {{
      hydratePanelCache('codex', codexCacheKey);
      refreshCodexStatus();
    }}
    if (selected === 'claude' && !claudeLoaded) {{
      hydratePanelCache('claude', claudeCacheKey);
      refreshClaudeStatus();
    }}
    if (selected === 'feedback' && !feedbackLoaded) {{
      hydratePanelCache('feedback', feedbackCacheKey);
      refreshFeedbackSummary();
    }}
  }}

  function renderHistory() {{
    const items = readHistory();
    if (!items.length) {{
      historyList.innerHTML = `<p class="meta">{text['no_history']}</p>`;
      return;
    }}
    historyList.innerHTML = '';
    items.forEach((item, index) => {{
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'history-item';
      button.dataset.historyIndex = String(index);
      const title = document.createElement('span');
      title.textContent = `${{item.action}} · exit_code=${{item.exit_code}}`;
      const detail = document.createElement('small');
      detail.textContent = `${{item.target}} · ${{item.elapsed_seconds}}s · ${{item.at}}`;
      button.append(title, detail);
      historyList.appendChild(button);
    }});
  }}

  function addHistory(item) {{
    writeHistory([item, ...readHistory()]);
    renderHistory();
  }}

  function setOutput(text) {{
    output.textContent = text || '';
    outputPanel.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
  }}

  function setFeedbackPreview(text) {{
    if (!feedbackPreview) {{
      setOutput(text);
      return;
    }}
    feedbackPreview.textContent = text || '';
    feedbackPreview.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
  }}

  function setBusy(isBusy) {{
    document.body.dataset.busy = isBusy ? '1' : '';
    status.textContent = isBusy ? {text['running']!r} : {text['ready']!r};
    document.querySelectorAll('button[data-action]').forEach((button) => button.disabled = isBusy);
    if (!isBusy) {{
      syncNextWorkActionGuards();
    }}
  }}

  function selectedTargetValues() {{
    if (!targetAll || targetAll.checked) {{
      return ['__all__'];
    }}
    return targetOptions
      .filter((item) => item.checked)
      .map((item) => item.getAttribute('data-ui-target-option') || '')
      .filter(Boolean);
  }}

  function syncTargetControls() {{
    const allSelected = !targetAll || targetAll.checked;
    targetOptions.forEach((item) => {{
      item.disabled = allSelected;
    }});
    const selected = selectedTargetValues();
    if (target) {{
      target.value = selected[0] || '';
    }}
  }}

  function selectedTargetLabel(values) {{
    const selected = Array.isArray(values) ? values : selectedTargetValues();
    if (!selected.length) {{
      return '';
    }}
    if (selected.includes('__all__')) {{
      return {text['all_targets']!r};
    }}
    return selected.join(', ');
  }}

  function setNextWorkStatusLine(text) {{
    if (nextWorkCacheState) {{
      nextWorkCacheState.textContent = text || '';
    }}
  }}

  function nextWorkStateLabel(value) {{
    const normalized = String(value || '').trim() || 'unknown';
    if (currentUiLanguage() === 'zh-CN') {{
      if (normalized === 'healthy') return 'healthy';
      if (normalized === 'attention') return 'attention';
      if (normalized === 'action_required') return 'action_required';
      return normalized;
    }}
    return normalized;
  }}

  function actionDisplayLabel(action) {{
    const labels = {{
      fast_feedback: {text['fast_feedback_action']!r},
      readiness: {text['readiness_action']!r},
      rules_dry_run: {text['rules_dry_run_action']!r},
      rules_apply: {text['rules_apply_action']!r},
      governance_baseline_all: {text['governance_baseline_action']!r},
      daily_all: {text['daily_all_action']!r},
      apply_all_features: {text['apply_all_action']!r},
      cleanup_targets: {text['cleanup_targets_action']!r},
      uninstall_governance: {text['uninstall_governance_action']!r},
      feedback_report: {text['feedback_report_action']!r},
      evolution_review: {text['evolution_review_action']!r},
      experience_review: {text['experience_review_action']!r},
      evolution_materialize: {text['evolution_materialize_action']!r},
      core_principle_materialize: {text['core_principle_action']!r},
      targets: {text['targets_action']!r},
    }};
    return labels[action] || action || 'unknown';
  }}

  function nextWorkActionLabel(action) {{
    const value = String(action || '').trim();
    const labels = currentUiLanguage() === 'zh-CN'
      ? {{
          refresh_evidence_first: '先刷新证据',
          wait_for_host_capability_recovery: '等待宿主能力恢复',
          repair_gate_first: '先修门禁',
          owner_directed_scope_required: '需要人工定范围',
          promote_ltp: '进入 LTP 提升评审',
          defer_ltp_and_refresh_evidence: '暂缓 LTP，先补新证据',
          defer_all: '暂缓自动推进',
        }}
      : {{
          refresh_evidence_first: 'Refresh evidence first',
          wait_for_host_capability_recovery: 'Wait for host recovery',
          repair_gate_first: 'Repair gates first',
          owner_directed_scope_required: 'Owner scope required',
          promote_ltp: 'Promote LTP',
          defer_ltp_and_refresh_evidence: 'Defer LTP and refresh evidence',
          defer_all: 'Defer automatic progression',
        }};
    return labels[value] || value || 'unknown';
  }}

  function nextWorkWhyLabel(action, why) {{
    const raw = String(why || '').trim();
    const value = String(action || '').trim();
    const labels = currentUiLanguage() === 'zh-CN'
      ? {{
          refresh_evidence_first: '当前证据或来源已过期，先刷新 target-run 证据和来源状态，再决定后续实现动作。',
          wait_for_host_capability_recovery: '最新 target-run 证据仍证明宿主能力退化且已有有界暂缓，等待新的 Codex/宿主姿态证明 native_attach 恢复。',
          repair_gate_first: '当前仓库门禁未通过，先修复 gate，再继续执行高影响动作。',
          owner_directed_scope_required: '当前范围需要人工明确，暂不自动推进实现动作。',
          promote_ltp: '已满足进入 LTP 提升评审的条件，可继续处理选中的 LTP 包。',
          defer_ltp_and_refresh_evidence: '暂不推进新的实现范围，优先补齐更新证据。',
          defer_all: '当前不建议自动推进新的实现动作。',
        }}
      : {{
          refresh_evidence_first: 'Evidence or source posture is stale. Refresh target-run evidence and source posture before new implementation work.',
          wait_for_host_capability_recovery: 'Fresh target-run evidence still proves bounded host degradation. Wait for a new Codex or host posture that proves native_attach recovery.',
          repair_gate_first: 'Repository gates are not healthy. Repair gates before higher-impact actions.',
          owner_directed_scope_required: 'Scope needs explicit owner direction before automatic implementation work can continue.',
          promote_ltp: 'The selected LTP package is ready for promotion review.',
          defer_ltp_and_refresh_evidence: 'Do not expand implementation scope yet; refresh evidence first.',
          defer_all: 'Automatic implementation progression is currently deferred.',
        }};
    return labels[value] || raw || (currentUiLanguage() === 'zh-CN' ? '当前被 next-work 阻断。' : 'Blocked by next-work.');
  }}

  function sanitizeNextWorkPayload(payload) {{
    const normalized = payload && typeof payload === 'object' ? {{ ...payload }} : {{}};
    const safeAction = String(normalized.safe_next_action || normalized.next_action || '').trim();
    const blocked = Array.isArray(normalized.blocked_actions) ? [...normalized.blocked_actions] : [];
    if (safeAction === 'refresh_evidence_first') {{
      normalized.blocked_actions = blocked.filter((action) => action !== 'daily_all');
    }} else {{
      normalized.blocked_actions = blocked;
    }}
    return normalized;
  }}

  function syncNextWorkActionGuards() {{
    const safePayload = sanitizeNextWorkPayload(lastNextWorkPayload || {{}});
    lastNextWorkPayload = safePayload;
    const blocked = new Set(Array.isArray(safePayload.blocked_actions) ? safePayload.blocked_actions : []);
    const why = String(safePayload.why || '').trim();
    const nextAction = String(safePayload.safe_next_action || safePayload.next_action || '').trim();
    const localizedWhy = nextWorkWhyLabel(nextAction, why);
    document.querySelectorAll('button[data-action]').forEach((button) => {{
      const action = button.getAttribute('data-action') || '';
      const isBlocked = blocked.has(action);
      const blockedNote = document.querySelector(`[data-action-blocked="${{action}}"]`);
      if (isBlocked) {{
        button.disabled = true;
        button.dataset.blockedReason = localizedWhy || 'blocked by next-work selector';
        button.title = `${{actionDisplayLabel(action)}}: ${{button.dataset.blockedReason}}`;
        if (blockedNote) {{
          blockedNote.textContent = currentUiLanguage() === 'zh-CN'
            ? `当前被 next-work 阻断: ${{button.dataset.blockedReason}}`
            : `Currently blocked by next-work: ${{button.dataset.blockedReason}}`;
        }}
      }} else {{
        if (!document.body.dataset.busy) {{
          button.disabled = false;
        }}
        delete button.dataset.blockedReason;
        button.title = '';
        if (blockedNote) {{
          blockedNote.textContent = '';
        }}
      }}
    }});
  }}

  function renderNextWorkSummary(payload) {{
    const safePayload = sanitizeNextWorkPayload(payload);
    lastNextWorkPayload = safePayload;
    const safeAction = String(safePayload.safe_next_action || safePayload.next_action || 'unknown');
    if (nextWorkAction) {{
      nextWorkAction.textContent = nextWorkActionLabel(safeAction);
    }}
    if (nextWorkRecommendation) {{
      nextWorkRecommendation.textContent = currentUiLanguage() === 'zh-CN'
        ? `AI 推荐: ${{nextWorkActionLabel(safeAction)}}`
        : `AI recommended: ${{nextWorkActionLabel(safeAction)}}`;
    }}
    if (nextWorkState) {{
      nextWorkState.textContent = currentUiLanguage() === 'zh-CN'
        ? `状态: ${{nextWorkStateLabel(safePayload.ui_status)}}`
        : `Status: ${{nextWorkStateLabel(safePayload.ui_status)}}`;
    }}
    if (nextWorkWhy) {{
      nextWorkWhy.textContent = nextWorkWhyLabel(safeAction, safePayload.why || '');
    }}
    if (nextWorkJson) {{
      nextWorkJson.textContent = JSON.stringify(safePayload, null, 2);
    }}
    syncNextWorkActionGuards();
  }}

  async function refreshNextWorkSummary() {{
    return refreshNextWorkSummaryWithMode(false);
  }}

  async function refreshNextWorkSummaryWithMode(forceRefresh) {{
    if (!nextWorkAction) {{
      return;
    }}
    setPanelCacheState('next-work', nextWorkLoaded ? 'refreshing' : 'cold');
    try {{
      const response = forceRefresh
        ? await fetch('/api/next-work?refresh=1')
        : await fetch('/api/next-work');
      const payload = await response.json();
      if (!response.ok) {{
        setNextWorkStatusLine(payload.error || response.statusText);
        return;
      }}
      renderNextWorkSummary(payload);
      writePanelCache(nextWorkCacheKey, payload);
      nextWorkLoaded = true;
      setPanelCacheState('next-work', 'ready', payload.cached_at);
    }} catch (error) {{
      setNextWorkStatusLine(String(error));
      setPanelCacheState('next-work', 'error');
    }}
  }}

  async function runAction(action, button) {{
    const blockedReason = button.getAttribute('data-blocked-reason');
    if (blockedReason) {{
      setOutput(`${{actionDisplayLabel(action)}}\n\n${{blockedReason}}`);
      return;
    }}
    const targets = selectedTargetValues();
    if (!targets.length) {{
      setOutput({text['no_target_selected']!r});
      return;
    }}
    const confirmMessage = button.getAttribute('data-confirm');
    if (confirmMessage && !window.confirm(confirmMessage)) {{
      return;
    }}
    const applyManagedAssetRemoval = !dryRun.checked && (
      defaultManagedRemovalActions.has(action)
      || (managedRemovalActions.has(action) && applyRemoval && applyRemoval.checked)
    );
    document.body.dataset.busy = 'true';
    setBusy(true);
    setOutput('');
    try {{
      const response = await fetch('/api/run', {{
        method: 'POST',
        headers: {{ 'content-type': 'application/json' }},
        body: JSON.stringify({{
          action,
          language: languageSelect.value,
          target: targets[0] || '__all__',
          targets,
          mode: mode.value,
          target_parallelism: Number(parallelism.value || 1),
          milestone_tag: milestone.value || 'milestone',
          fail_fast: failFast.checked,
          dry_run: dryRun.checked,
          apply_managed_asset_removal: applyManagedAssetRemoval
        }})
      }});
      const payload = await response.json();
      const rendered = [
        `action: ${{payload.action || action}}`,
        `exit_code: ${{payload.exit_code}}`,
        `elapsed_seconds: ${{payload.elapsed_seconds}}`,
        '',
        payload.output || ''
      ].join('\\n');
      setOutput(rendered);
      addHistory({{
        action: payload.action || action,
        target: selectedTargetLabel(targets),
        exit_code: payload.exit_code,
        elapsed_seconds: payload.elapsed_seconds,
        at: new Date().toLocaleString(),
        output: rendered
      }});
      if (nextWorkAction) {{
        await refreshNextWorkSummary();
      }}
    }} catch (error) {{
      setOutput(String(error));
    }} finally {{
      delete document.body.dataset.busy;
      setBusy(false);
    }}
  }}

  async function viewRef(path, options = {{}}) {{
    const previewTarget = options && options.previewTarget === 'feedback' ? 'feedback' : 'runtime';
    setBusy(true);
    try {{
      const response = await fetch('/api/file?path=' + encodeURIComponent(path));
      const payload = await response.json();
      if (!response.ok) {{
        if (previewTarget === 'feedback') {{
          setFeedbackPreview(payload.error || response.statusText);
        }} else {{
          setOutput(payload.error || response.statusText);
        }}
      }} else {{
        const rendered = `path: ${{payload.path}}\\n\\n${{payload.content}}`;
        if (previewTarget === 'feedback') {{
          setFeedbackPreview(rendered);
        }} else {{
          setOutput(rendered);
        }}
      }}
    }} catch (error) {{
      if (previewTarget === 'feedback') {{
        setFeedbackPreview(String(error));
      }} else {{
        setOutput(String(error));
      }}
    }} finally {{
      setBusy(false);
    }}
  }}

  function codexAccountLabel(account) {{
    return account.account_label || account.email || account.display_name || account.account_hash || account.name || 'unknown';
  }}

  function formatCodexSnapshotStatus(snapshot) {{
    if (!snapshot || typeof snapshot !== 'object') {{
      return '';
    }}
    const name = snapshot.profile_name || snapshot.profile_file || 'auth';
    const status = String(snapshot.status || '').trim();
    if (status === 'synced') {{
      return {text['codex_snapshot_synced']!r}.replace('{{name}}', name);
    }}
    if (status === 'drifted') {{
      return {text['codex_snapshot_drifted']!r}.replace('{{name}}', name);
    }}
    if (status === 'missing_named_snapshot') {{
      return {text['codex_snapshot_missing']!r};
    }}
    return '';
  }}

  function formatPlanLabel(planType) {{
    const value = String(planType || '').trim().toLowerCase();
    if (!value) {{
      return '';
    }}
    if (currentUiLanguage() === 'zh-CN') {{
      const labels = {{
        team: '团队版',
        plus: 'Plus',
        prolite: 'Pro',
        pro: 'Pro',
        free: '免费版',
      }};
      return labels[value] || planType;
    }}
    return planType;
  }}

  function formatAuthModeLabel(authMode) {{
    const value = String(authMode || '').trim().toLowerCase();
    if (!value) {{
      return currentUiLanguage() === 'zh-CN' ? '登录方式未知' : 'unknown sign-in';
    }}
    if (value === 'chatgpt') {{
      return currentUiLanguage() === 'zh-CN' ? 'ChatGPT 登录' : 'ChatGPT sign-in';
    }}
    return authMode;
  }}

  function formatTimestampLabel(timestamp) {{
    const raw = String(timestamp || '').trim();
    if (!raw) {{
      return currentUiLanguage() === 'zh-CN' ? '最近刷新时间未知' : 'last refresh unknown';
    }}
    const date = new Date(raw);
    if (Number.isNaN(date.getTime())) {{
      return raw;
    }}
    const locale = currentUiLanguage() === 'zh-CN' ? 'zh-CN' : 'en-US';
    return new Intl.DateTimeFormat(locale, {{
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }}).format(date);
  }}

  function formatCompactTimestamp(timestamp) {{
    const raw = String(timestamp || '').trim();
    if (!raw) {{
      return '';
    }}
    const date = new Date(raw);
    if (Number.isNaN(date.getTime())) {{
      return raw;
    }}
    const locale = currentUiLanguage() === 'zh-CN' ? 'zh-CN' : 'en-US';
    return new Intl.DateTimeFormat(locale, {{
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }}).format(date);
  }}

  function daysRemainingLabel(timestamp) {{
    const raw = String(timestamp || '').trim();
    if (!raw) {{
      return '';
    }}
    const date = new Date(raw);
    if (Number.isNaN(date.getTime())) {{
      return '';
    }}
    const dayMs = 24 * 60 * 60 * 1000;
    const days = Math.max(0, Math.ceil((date.getTime() - Date.now()) / dayMs));
    return currentUiLanguage() === 'zh-CN' ? `剩余${{days}}日` : `${{days}}d left`;
  }}

  function formatCompactTimestampWithDays(timestamp) {{
    const compact = formatCompactTimestamp(timestamp);
    const days = daysRemainingLabel(timestamp);
    return [compact, days].filter(Boolean).join(currentUiLanguage() === 'zh-CN' ? ' ' : ', ');
  }}

  function currentUiLanguage() {{
    const lang = document.documentElement.lang || '';
    return lang.toLowerCase().startsWith('zh') ? 'zh-CN' : 'en-US';
  }}

  function formatUsageReset(resetAt) {{
    const seconds = Number(resetAt);
    if (!Number.isFinite(seconds) || seconds <= 0) {{
      return '';
    }}
    const date = new Date(seconds * 1000);
    if (Number.isNaN(date.getTime())) {{
      return '';
    }}
    const now = new Date();
    const sameDay = date.getFullYear() === now.getFullYear()
      && date.getMonth() === now.getMonth()
      && date.getDate() === now.getDate();
    const locale = currentUiLanguage();
    const options = sameDay
      ? {{ hour: '2-digit', minute: '2-digit', hour12: false }}
      : (locale === 'zh-CN' ? {{ month: 'long', day: 'numeric' }} : {{ month: 'numeric', day: 'numeric' }});
    return new Intl.DateTimeFormat(locale, options).format(date);
  }}

  function formatUsageWindowLabel(item) {{
    const minutes = Number(item.window_minutes);
    if (currentUiLanguage() === 'zh-CN') {{
      if (minutes === 300) {{
        return '5 小时';
      }}
      if (minutes === 10080) {{
        return '1 周';
      }}
    }}
    return item.window || 'unknown';
  }}

  function formatUsageWindow(item) {{
    const windowLabel = formatUsageWindowLabel(item);
    const remaining = item.remaining_percent !== null && item.remaining_percent !== undefined
      ? `${{item.remaining_percent}}%`
      : (item.remaining || 'unknown');
    const reset = formatUsageReset(item.reset_at);
    const resetLabel = reset ? `${{ {text['codex_usage_reset']!r} }} ${{reset}}` : '';
    return [windowLabel, remaining, resetLabel].filter(Boolean).join(' ');
  }}

  function formatAccountUsageSummary(account) {{
    const snapshot = account && account.usage_snapshot;
    const windows = snapshot && Array.isArray(snapshot.windows) ? snapshot.windows : [];
    if (!windows.length) {{
      return {text['codex_account_usage_unknown']!r};
    }}
    return windows.map(formatUsageWindow).join('\\n');
  }}

  function clampUsagePercent(value) {{
    const percent = Number(value);
    if (!Number.isFinite(percent)) {{
      return null;
    }}
    return Math.max(0, Math.min(100, percent));
  }}

  function createUsageMeter(account) {{
    const snapshot = account && account.usage_snapshot;
    const windows = snapshot && Array.isArray(snapshot.windows) ? snapshot.windows : [];
    if (!windows.length) {{
      const fallback = document.createElement('span');
      fallback.textContent = {text['codex_account_usage_unknown']!r};
      return fallback;
    }}
    const list = document.createElement('div');
    list.className = 'usage-meter-list';
    windows.forEach((item) => {{
      const percent = clampUsagePercent(item.remaining_percent);
      const row = document.createElement('div');
      row.className = 'usage-meter-row';
      const head = document.createElement('div');
      head.className = 'usage-meter-head';
      const label = document.createElement('span');
      label.textContent = formatUsageWindowLabel(item);
      const detail = document.createElement('small');
      const reset = formatUsageReset(item.reset_at);
      const remaining = percent === null ? (item.remaining || 'unknown') : `${{percent}}%`;
      detail.textContent = [
        `${{ {text['codex_usage_remaining']!r} }} ${{remaining}}`,
        reset ? `${{ {text['codex_usage_reset']!r} }} ${{reset}}` : '',
      ].filter(Boolean).join(' · ');
      head.append(label, detail);
      const bar = document.createElement('div');
      bar.className = 'usage-bar';
      const fill = document.createElement('span');
      fill.className = 'usage-fill';
      if (percent !== null && percent <= 15) {{
        fill.classList.add('danger');
      }} else if (percent !== null && percent <= 35) {{
        fill.classList.add('warn');
      }}
      fill.style.width = `${{percent === null ? 0 : percent}}%`;
      bar.appendChild(fill);
      row.append(head, bar);
      list.appendChild(row);
    }});
    return list;
  }}

  function formatUsageSourceLabel(source) {{
    const value = String(source || '').trim();
    if (!value) {{
      return currentUiLanguage() === 'zh-CN' ? '来源未知' : 'unknown source';
    }}
    const labels = currentUiLanguage() === 'zh-CN'
      ? {{
          codex_logs_2_sqlite: '本机日志快照',
          codex_sessions_jsonl: '在线刷新后的最新会话',
          codex_exec_stdout: '在线响应结果',
          unknown: '来源未知',
        }}
      : {{
          codex_logs_2_sqlite: 'local log snapshot',
          codex_sessions_jsonl: 'latest refreshed session',
          codex_exec_stdout: 'online response',
          unknown: 'unknown source',
    }};
    return labels[value] || value;
  }}

  function formatRelativeAgeLabel(ageSeconds) {{
    const seconds = Number(ageSeconds);
    if (!Number.isFinite(seconds) || seconds < 0) {{
      return '';
    }}
    if (seconds < 60) {{
      return currentUiLanguage() === 'zh-CN' ? '刚刚' : 'just now';
    }}
    if (seconds < 3600) {{
      const minutes = Math.max(1, Math.round(seconds / 60));
      return currentUiLanguage() === 'zh-CN' ? `${{minutes}} 分钟前` : `${{minutes}} min ago`;
    }}
    const hours = Math.max(1, Math.round(seconds / 3600));
    return currentUiLanguage() === 'zh-CN' ? `${{hours}} 小时前` : `${{hours}} h ago`;
  }}

  function formatUsageFreshnessLabel(usage) {{
    const freshness = usage && usage.freshness ? usage.freshness : null;
    if (!freshness) {{
      return {text['codex_usage_freshness_unknown']!r};
    }}
    const age = formatRelativeAgeLabel(freshness.age_seconds);
    const captured = formatCompactTimestamp(freshness.captured_at);
    const prefix = freshness.is_stale
      ? {text['codex_usage_freshness_stale']!r}
      : {text['codex_usage_freshness_fresh']!r};
    return [prefix, age || captured].filter(Boolean).join(currentUiLanguage() === 'zh-CN' ? ' · ' : ' - ');
  }}

  function formatTokenExpirySummary(account) {{
    const idExpiry = formatCompactTimestampWithDays(account && account.id_token_expires_at);
    const accessExpiry = formatCompactTimestampWithDays(account && account.access_token_expires_at);
    const parts = [];
    if (idExpiry) {{
      parts.push(`ID token ${{idExpiry}}`);
    }}
    if (accessExpiry) {{
      parts.push(`Access token ${{accessExpiry}}`);
    }}
    if (!parts.length) {{
      return {text['codex_token_unknown']!r};
    }}
    return parts.join('\\n');
  }}

  function formatSubscriptionExpirySummary(account) {{
    const expiry = formatCompactTimestampWithDays(account && account.subscription_active_until);
    if (!expiry) {{
      return {text['codex_subscription_unknown']!r};
    }}
    const checked = formatCompactTimestamp(account && account.subscription_last_checked);
    if (!checked) {{
      return expiry;
    }}
    return currentUiLanguage() === 'zh-CN'
      ? `${{expiry}}\n核验 ${{checked}}`
      : `${{expiry}}\nchecked ${{checked}}`;
  }}

  function summarizeClaudeMcp(summary) {{
    const text = String(summary || '').trim();
    if (!text) {{
      return currentUiLanguage() === 'zh-CN' ? '状态未知' : 'status unknown';
    }}
    const normalized = text.replace(/\\s+/g, ' ').trim();
    const connected = (normalized.match(/Connected/gi) || []).length;
    const checking = (normalized.match(/Checking MCP server health/gi) || []).length;
    const names = Array.from(normalized.matchAll(/\\b([a-z0-9-]+):\\s/gi))
      .map((match) => match[1])
      .filter((name, index, items) => items.indexOf(name) === index);
    const prefix = [];
    if (connected) {{
      prefix.push(currentUiLanguage() === 'zh-CN' ? `已连接 ${{connected}} 个` : `${{connected}} connected`);
    }}
    if (checking) {{
      prefix.push(currentUiLanguage() === 'zh-CN' ? `检查中 ${{checking}} 个` : `${{checking}} checking`);
    }}
    const visibleNames = names.slice(0, 4).join(currentUiLanguage() === 'zh-CN' ? '、' : ', ');
    const hiddenCount = Math.max(names.length - 4, 0);
    if (visibleNames) {{
      prefix.push(
        currentUiLanguage() === 'zh-CN'
          ? hiddenCount
            ? `${{visibleNames}} 等 ${{names.length}} 个`
            : visibleNames
          : hiddenCount
            ? `${{visibleNames}} and ${{hiddenCount}} more`
            : visibleNames
      );
    }}
    return prefix.join('\\n') || (currentUiLanguage() === 'zh-CN' ? '状态未知' : 'status unknown');
  }}

  function createInfoLine(label, value) {{
    const line = document.createElement('div');
    line.className = 'info-line';
    const labelEl = document.createElement('span');
    labelEl.className = 'info-label';
    labelEl.textContent = label;
    const valueEl = document.createElement('span');
    valueEl.className = 'info-value';
    if (value && typeof value === 'object' && value.nodeType) {{
      valueEl.appendChild(value);
    }} else if (String(value || '').includes('\\n')) {{
      valueEl.appendChild(createMultilineInfoValue(value));
    }} else {{
      valueEl.textContent = value;
    }}
    line.append(labelEl, valueEl);
    return line;
  }}

  function createInfoValueStack(lines) {{
    const stack = document.createElement('div');
    stack.className = 'info-value-stack';
    lines.filter(Boolean).forEach((text, index) => {{
      const line = document.createElement('span');
      line.className = index === 0 ? 'info-value-line' : 'info-value-line secondary';
      line.textContent = text;
      stack.appendChild(line);
    }});
    return stack;
  }}

  function createMultilineInfoValue(value) {{
    const lines = String(value || '')
      .split('\\n')
      .map((line) => line.trim())
      .filter(Boolean);
    if (lines.length <= 1) {{
      return lines[0] || '';
    }}
    return createInfoValueStack(lines);
  }}

  function formatFeedbackStatusLabel(value) {{
    const normalized = String(value || '').trim().toLowerCase();
    if (currentUiLanguage() === 'zh-CN') {{
      const labels = {{
        pass: '通过',
        ok: '正常',
        attention: '需关注',
        fail: '失败',
        error: '错误',
      }};
      return labels[normalized] || (value || '未知');
    }}
    return value || 'unknown';
  }}

  function summarizeFeedbackAdapter(value) {{
    const normalized = String(value || '').trim().toLowerCase();
    if (normalized === 'native_attach') {{
      return {text['feedback_repo_attach_native']!r};
    }}
    if (normalized === 'process_bridge') {{
      return {text['feedback_repo_attach_bridge']!r};
    }}
    if (normalized === 'manual_handoff') {{
      return {text['feedback_repo_attach_manual']!r};
    }}
    return value || 'unknown';
  }}

  function summarizeFeedbackFlow(value) {{
    const normalized = String(value || '').trim().toLowerCase();
    if (normalized === 'live_attach') {{
      return {text['feedback_repo_flow_live']!r};
    }}
    if (normalized === 'bridge_attach') {{
      return {text['feedback_repo_flow_bridge']!r};
    }}
    return value || 'unknown';
  }}

  function summarizeFeedbackClosure(value) {{
    const normalized = String(value || '').trim().toLowerCase();
    if (normalized === 'live_closure_ready') {{
      return {text['feedback_repo_closure_ready']!r};
    }}
    if (!normalized || normalized === 'unknown') {{
      return currentUiLanguage() === 'zh-CN' ? '未记录' : 'not recorded';
    }}
    return {text['feedback_repo_closure_partial']!r};
  }}

  function summarizeFeedbackWrite(value) {{
    const normalized = String(value || '').trim().toLowerCase();
    if (!normalized || normalized === 'unknown') {{
      return {text['feedback_repo_write_unknown']!r};
    }}
    return {text['feedback_repo_write_done']!r};
  }}

  function createRefButton(path, label, previewTarget = 'runtime') {{
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'ref-button';
    button.dataset.ref = path;
    button.textContent = label || path;
    button.addEventListener('click', () => viewRef(path, {{ previewTarget }}));
    return button;
  }}

  function renderFeedbackSummary(payload) {{
    if (!feedbackSummary || !feedbackDimensions || !feedbackRecommendations || !feedbackLatestRuns) {{
      return;
    }}
    const summary = payload && payload.summary ? payload.summary : {{}};
    const dimensions = Array.isArray(payload && payload.dimensions) ? payload.dimensions : [];
    const recommendations = Array.isArray(payload && payload.recommendations) ? payload.recommendations : [];
    const generatedAt = payload && payload.generated_at ? formatTimestampLabel(payload.generated_at) : {text['not_recorded']!r};

    feedbackGeneratedAt.textContent = `{text['feedback_generated_at']}: ${{generatedAt}}`;
    feedbackStatus.textContent = `{text['feedback_status']}: ${{formatFeedbackStatusLabel(payload && payload.status)}}`;

    feedbackSummary.innerHTML = '';
    [
      {{
        label: {text['feedback_status']!r},
        value: formatFeedbackStatusLabel(payload && payload.status),
        detail: summary.rule_manifest_revision ? `manifest=${{summary.rule_manifest_revision}}` : ''
      }},
      {{
        label: {text['feedback_summary_caption']!r},
        value: currentUiLanguage() === 'zh-CN'
          ? `正常 ${{summary.dimensions_ok || 0}} / 关注 ${{summary.dimensions_attention || 0}} / 失败 ${{summary.dimensions_fail || 0}}`
          : `ok ${{summary.dimensions_ok || 0}} / attention ${{summary.dimensions_attention || 0}} / fail ${{summary.dimensions_fail || 0}}`,
        detail: ''
      }},
      {{
        label: 'Codex',
        value: formatFeedbackStatusLabel(summary.codex_host_status),
        detail: ''
      }},
      {{
        label: 'Claude',
        value: formatFeedbackStatusLabel(summary.claude_host_status),
        detail: ''
      }},
    ].forEach((card) => {{
      const section = document.createElement('section');
      section.className = 'claude-summary-card';
      section.appendChild(createInfoLine(card.label, card.value));
      if (card.detail) {{
        const meta = document.createElement('p');
        meta.className = 'meta';
        meta.textContent = card.detail;
        section.appendChild(meta);
      }}
      feedbackSummary.appendChild(section);
    }});
    updateFeedbackSurfaceSummary(payload);

    feedbackDimensions.innerHTML = '';
    dimensions.forEach((item) => {{
      const pill = document.createElement('span');
      pill.className = `status-pill ${{String(item.status || '').toLowerCase()}}`;
      pill.textContent = `${{item.dimension_id}}: ${{formatFeedbackStatusLabel(item.status)}}`;
      pill.title = item.summary || '';
      feedbackDimensions.appendChild(pill);
    }});
    if (!dimensions.length) {{
      const empty = document.createElement('p');
      empty.className = 'meta';
      empty.textContent = {text['feedback_empty']!r};
      feedbackDimensions.appendChild(empty);
    }}

    feedbackRecommendations.innerHTML = '';
    if (recommendations.length) {{
      const list = document.createElement('ul');
      recommendations.forEach((item) => {{
        const li = document.createElement('li');
        li.textContent = String(item);
        list.appendChild(li);
      }});
      feedbackRecommendations.appendChild(list);
    }} else {{
      feedbackRecommendations.innerHTML = `<p class="meta">{text['none']}</p>`;
    }}

    feedbackLatestRuns.innerHTML = '';
    const targetRuns = dimensions.find((item) => item.dimension_id === 'target_runs');
    const runs = targetRuns && targetRuns.details && Array.isArray(targetRuns.details.latest_runs)
      ? targetRuns.details.latest_runs
      : [];
    runs.forEach((item) => {{
      const card = document.createElement('div');
      card.className = 'feedback-run';
      const title = document.createElement('strong');
      title.textContent = String(item.repo_id || 'repo');
      const meta = document.createElement('div');
      meta.className = 'info-list';
      meta.append(
        createInfoLine({text['feedback_repo_attach']!r}, summarizeFeedbackAdapter(item.adapter_tier)),
        createInfoLine({text['feedback_repo_flow']!r}, summarizeFeedbackFlow(item.flow_kind || item.flow_mode)),
        createInfoLine({text['feedback_repo_closure']!r}, summarizeFeedbackClosure(item.closure_state)),
        createInfoLine({text['feedback_repo_write']!r}, summarizeFeedbackWrite(item.write_status))
      );
      card.append(title, meta);
      feedbackLatestRuns.appendChild(card);
    }});
    if (!runs.length) {{
      feedbackLatestRuns.innerHTML = `<p class="meta">{text['feedback_empty']}</p>`;
    }}

    feedbackReportLink.innerHTML = '';
    if (payload && payload.report_path) {{
      feedbackReportLink.appendChild(createRefButton(payload.report_path, {text['feedback_open_report']!r}, 'feedback'));
    }} else {{
      feedbackReportLink.innerHTML = `<p class="meta">{text['feedback_report_missing']}</p>`;
    }}
    feedbackGuideLink.innerHTML = '';
    if (payload && payload.guide_path) {{
      feedbackGuideLink.appendChild(createRefButton(payload.guide_path, {text['feedback_open_guide']!r}, 'feedback'));
    }}
    feedbackGuideLinkEn.innerHTML = '';
    if ((document.documentElement.lang || '').toLowerCase().startsWith('en') && payload && payload.guide_path_en) {{
      feedbackGuideLinkEn.appendChild(createRefButton(payload.guide_path_en, {text['feedback_open_guide_en']!r}, 'feedback'));
    }}
  }}

  async function refreshFeedbackSummary() {{
    return refreshFeedbackSummaryWithMode(false);
  }}

  async function refreshFeedbackSummaryWithMode(forceRefresh) {{
    if (!feedbackSummary) {{
      return;
    }}
    setPanelCacheState('feedback', feedbackLoaded ? 'refreshing' : 'cold');
    try {{
      const response = forceRefresh
        ? await fetch('/api/feedback/summary?refresh=1')
        : await fetch('/api/feedback/summary');
      const payload = await response.json();
      if (!response.ok) {{
        feedbackStatus.textContent = `{text['feedback_status']}: ${{payload.error || response.statusText}}`;
        setPanelCacheState('feedback', 'error');
        return;
      }}
      payload.cached_at = payload.generated_at || payload.cached_at;
      renderFeedbackSummary(payload);
      writePanelCache(feedbackCacheKey, payload);
      feedbackLoaded = true;
      setPanelCacheState('feedback', 'ready', payload.cached_at);
    }} catch (error) {{
      feedbackStatus.textContent = `{text['feedback_status']}: ${{String(error)}}`;
      setPanelCacheState('feedback', 'error');
    }}
  }}

  function summarizeClaudeContext(provider) {{
    const env = provider && provider.env ? provider.env : {{}};
    const compactWindow = String(env.CLAUDE_CODE_AUTO_COMPACT_WINDOW || '').trim();
    const compactPct = String(env.CLAUDE_AUTOCOMPACT_PCT_OVERRIDE || '').trim();
    const parts = [];
    if (compactWindow) {{
      parts.push(currentUiLanguage() === 'zh-CN' ? `窗口 ${{compactWindow}}` : `window ${{compactWindow}}`);
    }}
    if (compactPct) {{
      parts.push(currentUiLanguage() === 'zh-CN' ? `触发 ${{compactPct}}%` : `trigger ${{compactPct}}%`);
    }}
    return parts.join(' · ') || (currentUiLanguage() === 'zh-CN' ? '未记录' : 'not recorded');
  }}

  function summarizeClaudeTimeout(provider) {{
    const env = provider && provider.env ? provider.env : {{}};
    const timeout = Number(env.API_TIMEOUT_MS || 0);
    if (!Number.isFinite(timeout) || timeout <= 0) {{
      return currentUiLanguage() === 'zh-CN' ? '未记录' : 'not recorded';
    }}
    const minutes = Math.round(timeout / 60000);
    return currentUiLanguage() === 'zh-CN' ? `${{minutes}} 分钟` : `${{minutes}} min`;
  }}

  function summarizeClaudeModels(provider) {{
    const models = provider && provider.models ? provider.models : {{}};
    return [
      models.opus ? `Opus ${{models.opus}}` : '',
      models.sonnet ? `Sonnet ${{models.sonnet}}` : '',
      models.haiku ? `Haiku ${{models.haiku}}` : '',
    ].filter(Boolean).join(' · ');
  }}

  function configCheckLabel(key) {{
    const labels = currentUiLanguage() === 'zh-CN'
      ? {{
          model: '默认模型',
          model_reasoning_effort: '推理强度',
          model_verbosity: '回答详细度',
          model_context_window: '上下文窗口',
          model_auto_compact_token_limit: '自动压缩阈值',
          sandbox_mode: '沙箱模式',
          approval_policy: '审批策略',
          web_search: '联网搜索',
          cli_path: 'CLI 路径',
          command_status: 'CLI 状态',
          provider_name: 'Provider',
          base_url: '服务地址',
          credential_present: '凭据',
        }}
      : {{
          model: 'default model',
          model_reasoning_effort: 'reasoning effort',
          model_verbosity: 'verbosity',
          model_context_window: 'context window',
          model_auto_compact_token_limit: 'auto compact threshold',
          sandbox_mode: 'sandbox mode',
          approval_policy: 'approval policy',
          web_search: 'web search',
          cli_path: 'CLI path',
          command_status: 'CLI status',
          provider_name: 'provider',
          base_url: 'service URL',
          credential_present: 'credential',
        }};
    return labels[key] || key || 'unknown';
  }}

  function formatConfigHealth(config) {{
    if (!config || config.status === 'missing') {{
      return currentUiLanguage() === 'zh-CN' ? '未检测到本机配置文件' : 'Local config file not found';
    }}
    const failedChecks = Array.isArray(config.checks) ? config.checks.filter((check) => !check.ok) : [];
    const secretMarkers = Array.isArray(config.secret_like_markers) ? config.secret_like_markers : [];
    if (!failedChecks.length && !secretMarkers.length) {{
      return currentUiLanguage() === 'zh-CN' ? '已符合推荐值' : 'Matches recommended defaults';
    }}
    const issues = failedChecks.map((check) => configCheckLabel(check.key));
    if (secretMarkers.length) {{
      issues.push(currentUiLanguage() === 'zh-CN' ? '疑似敏感字段' : 'possible secret markers');
    }}
    const prefix = currentUiLanguage() === 'zh-CN' ? '建议调整：' : 'Needs attention: ';
    return prefix + issues.join('、');
  }}

  function renderCodexStatus(payload) {{
    lastCodexPayload = payload;
    const accounts = Array.isArray(payload.accounts) ? payload.accounts : [];
    codexAccounts.innerHTML = '';
    accounts.forEach((account) => {{
      const label = codexAccountLabel(account);
      const row = document.createElement('div');
      row.className = 'codex-account';
      const body = document.createElement('div');
      body.className = 'codex-account-body';
      const name = document.createElement('strong');
      name.textContent = label;
      const infoList = document.createElement('div');
      infoList.className = 'info-list';
      infoList.append(
        createInfoLine(
          currentUiLanguage() === 'zh-CN' ? '配置' : 'profile',
          account.name || account.file || 'auth'
        ),
        createInfoLine(
          currentUiLanguage() === 'zh-CN' ? '登录' : 'sign-in',
          formatAuthModeLabel(account.auth_mode)
        ),
        createInfoLine(
          currentUiLanguage() === 'zh-CN' ? '套餐' : 'plan',
          createMultilineInfoValue(formatSubscriptionExpirySummary(account))
        ),
        createInfoLine(
          currentUiLanguage() === 'zh-CN' ? '令牌' : 'token',
          createMultilineInfoValue(formatTokenExpirySummary(account))
        )
      );
      const planLabel = formatPlanLabel(account.plan_type);
      if (planLabel) {{
        infoList.appendChild(
          createInfoLine(
            currentUiLanguage() === 'zh-CN' ? '类型' : 'type',
            planLabel
          )
        );
      }}
      infoList.appendChild(
        createInfoLine(
          currentUiLanguage() === 'zh-CN' ? '额度' : 'usage',
          createUsageMeter(account)
        )
      );
      row.title = [
        account.file ? `file=${{account.file}}` : '',
        account.account_hash ? `hash=${{account.account_hash}}` : '',
        account.last_refresh || '',
      ].filter(Boolean).join(' · ');
      body.append(name, infoList);
      row.appendChild(body);
      const actions = document.createElement('div');
      actions.className = 'codex-account-actions';
      const switchButton = document.createElement('button');
      switchButton.type = 'button';
      switchButton.className = account.active ? 'codex-account-switch is-current' : 'codex-account-switch';
      switchButton.textContent = account.active ? {text['codex_active']!r} : {text['codex_switch']!r};
      if (account.active) {{
        switchButton.disabled = true;
      }} else {{
        switchButton.dataset.codexSwitchName = account.name || '';
      }}
      actions.appendChild(switchButton);
      row.appendChild(actions);
      if (account.active) {{
        const snapshot = account.snapshot_status || payload.snapshot_status || null;
        infoList.append(
          createInfoLine(
            currentUiLanguage() === 'zh-CN' ? '配置' : 'config',
            formatConfigHealth(payload.config || {{}})
          ),
          createInfoLine(
            {text['codex_snapshot']!r},
            formatCodexSnapshotStatus(snapshot)
          ),
          createInfoLine(
            currentUiLanguage() === 'zh-CN' ? '来源' : 'source',
            createMultilineInfoValue([
              [
                formatPlanLabel((payload.usage || {{}}).plan_type)
                  ? (currentUiLanguage() === 'zh-CN'
                      ? `${{formatPlanLabel((payload.usage || {{}}).plan_type)}} 账号`
                      : `${{formatPlanLabel((payload.usage || {{}}).plan_type)}} account`)
                  : '',
                formatUsageSourceLabel((payload.usage || {{}}).source || 'unknown'),
              ].filter(Boolean).join(' · '),
              formatUsageFreshnessLabel(payload.usage || {{}}),
            ].filter(Boolean).join('\\n'))
          )
        );
        if (snapshot && snapshot.status === 'drifted' && snapshot.profile_name) {{
          const syncButton = document.createElement('button');
          syncButton.type = 'button';
          syncButton.className = 'codex-account-switch';
          syncButton.textContent = {text['codex_sync_active']!r};
          syncButton.dataset.codexSyncName = snapshot.profile_name;
          syncButton.dataset.confirm = {text['codex_sync_confirm']!r};
          actions.appendChild(syncButton);
        }}
      }}
      codexAccounts.appendChild(row);
    }});
    if (!accounts.length) {{
      codexAccounts.innerHTML = `<p class="meta">{text['not_recorded']}</p>`;
    }}
    updateCodexSurfaceSummary(payload);

  }}

  async function refreshCodexStatus() {{
    if (!codexAccounts) {{
      return;
    }}
    lastCodexRefreshEpoch = Date.now();
    setPanelCacheState('codex', codexLoaded ? 'refreshing' : 'cold');
    try {{
      const response = await fetch('/api/codex/status?refresh_if_stale=1', {{ cache: 'no-store' }});
      const payload = await response.json();
      if (!response.ok) {{
        codexAccounts.innerHTML = `<p class="meta">${{payload.error || response.statusText}}</p>`;
        setPanelCacheState('codex', 'error');
        return;
      }}
      renderCodexStatus(payload);
      writePanelCache(codexCacheKey, payload);
      codexLoaded = true;
      setPanelCacheState('codex', 'ready', payload.cached_at);
    }} catch (error) {{
      codexAccounts.innerHTML = `<p class="meta">${{String(error)}}</p>`;
      setPanelCacheState('codex', 'error');
    }}
  }}

  async function refreshCodexStatusOnline() {{
    if (!codexAccounts) {{
      return;
    }}
    setBusy(true);
    lastCodexRefreshEpoch = Date.now();
    setPanelCacheState('codex', codexLoaded ? 'refreshing' : 'cold');
    try {{
      const response = await fetch('/api/codex/refresh', {{
        method: 'POST',
        cache: 'no-store',
        headers: {{ 'content-type': 'application/json' }},
        body: JSON.stringify({{}})
      }});
      const payload = await response.json();
      if (!response.ok) {{
        codexAccounts.innerHTML = `<p class="meta">${{payload.error || response.statusText}}</p>`;
        setPanelCacheState('codex', 'error');
        return;
      }}
      renderCodexStatus(payload);
      writePanelCache(codexCacheKey, payload);
      codexLoaded = true;
      setPanelCacheState('codex', 'ready', payload.cached_at);
    }} catch (error) {{
      codexAccounts.innerHTML = `<p class="meta">${{String(error)}}</p>`;
      setPanelCacheState('codex', 'error');
    }} finally {{
      setBusy(false);
    }}
  }}

  function shouldRefreshCodexOnResume() {{
    if (document.hidden || document.body.dataset.busy === '1') {{
      return false;
    }}
    if (!lastCodexPayload) {{
      return true;
    }}
    const age = Date.now() - lastCodexRefreshEpoch;
    if (age < codexRefreshCooldownMs) {{
      return false;
    }}
    const active = lastCodexPayload.active_account && typeof lastCodexPayload.active_account === 'object'
      ? lastCodexPayload.active_account
      : null;
    const snapshot = active && active.usage_snapshot && typeof active.usage_snapshot === 'object'
      ? active.usage_snapshot
      : null;
    return isUsageSnapshotStale(snapshot);
  }}

  function maybeRefreshCodexStatusOnResume() {{
    if (!shouldRefreshCodexOnResume()) {{
      return;
    }}
    refreshCodexStatus();
  }}

  async function switchCodexAccount(name) {{
    if (!name) {{
      return;
    }}
    setBusy(true);
    try {{
      const response = await fetch('/api/codex/switch', {{
        method: 'POST',
        headers: {{ 'content-type': 'application/json' }},
        body: JSON.stringify({{ name }})
      }});
      const payload = await response.json();
      setOutput(JSON.stringify(payload, null, 2));
      await refreshCodexStatus();
    }} catch (error) {{
      setOutput(String(error));
    }} finally {{
      setBusy(false);
    }}
  }}

  async function syncCodexActiveSnapshot(name, confirmMessage) {{
    if (confirmMessage && !window.confirm(confirmMessage)) {{
      return;
    }}
    setBusy(true);
    try {{
      const response = await fetch('/api/codex/sync-active', {{
        method: 'POST',
        headers: {{ 'content-type': 'application/json' }},
        body: JSON.stringify({{ name }})
      }});
      const payload = await response.json();
      setOutput(JSON.stringify(payload, null, 2));
      await refreshCodexStatus();
    }} catch (error) {{
      setOutput(String(error));
    }} finally {{
      setBusy(false);
    }}
  }}

  function renderClaudeStatus(payload) {{
    lastClaudePayload = payload;
    const providers = Array.isArray(payload.providers) ? payload.providers : [];
    claudeProviders.innerHTML = '';
    const settings = payload.settings || {{}};
    const permissions = settings.permissions || {{}};
    const config = payload.config || {{}};
    const mcp = payload.mcp || {{}};
    const usage = payload.usage || {{}};
    providers.forEach((provider) => {{
      const row = document.createElement('div');
      row.className = 'codex-account';
      const body = document.createElement('div');
      body.className = 'codex-account-body';
      const name = document.createElement('strong');
      name.textContent = provider.label || provider.name;
      const models = provider.models || {{}};
      const credential = provider.credential_present
        ? {text['claude_credential_ready']!r}
        : `${{currentUiLanguage() === 'zh-CN' ? {text['claude_missing_credential']!r} : {text['claude_missing_credential']!r}}} ${{provider.auth_env || ''}}`;
      const badge = document.createElement('span');
      badge.className = provider.credential_present ? 'provider-status-pill ready' : 'provider-status-pill missing';
      badge.textContent = credential;
      const infoList = document.createElement('div');
      infoList.className = 'info-list';
      if (provider.base_url) {{
        infoList.appendChild(
          createInfoLine(
            {text['claude_service']!r},
            provider.base_url
          )
        );
      }}
      const modelSummary = [
        models.opus ? `Opus ${{models.opus}}` : '',
        models.sonnet ? `Sonnet ${{models.sonnet}}` : '',
      ].filter(Boolean).join(' · ');
      if (modelSummary) {{
        infoList.appendChild(
          createInfoLine(
            {text['claude_models']!r},
            modelSummary
          )
        );
      }}
      infoList.appendChild(
        createInfoLine(
          {text['claude_credential']!r},
          credential
        )
      );
      body.append(name, badge, infoList);
      row.appendChild(body);
      const actions = document.createElement('div');
      actions.className = 'provider-card-actions';
      const switchButton = document.createElement('button');
      switchButton.type = 'button';
      switchButton.className = provider.active ? 'codex-account-switch is-current' : 'codex-account-switch';
      switchButton.textContent = provider.active ? {text['claude_active']!r} : {text['claude_switch']!r};
      if (provider.active) {{
        switchButton.disabled = true;
      }} else {{
        switchButton.dataset.claudeSwitchName = provider.name || '';
      }}
      actions.appendChild(switchButton);
      row.appendChild(actions);
      if (provider.active) {{
        infoList.append(
          createInfoLine(
            {text['claude_settings_summary']!r},
            currentUiLanguage() === 'zh-CN'
              ? `默认模型 ${{settings.model || 'unknown'}} · 权限模式 ${{permissions.defaultMode || 'unknown'}} · 清理周期 ${{settings.cleanupPeriodDays || 'unknown'}} 天`
              : `model ${{settings.model || 'unknown'}} · mode ${{permissions.defaultMode || 'unknown'}} · cleanup ${{settings.cleanupPeriodDays || 'unknown'}}d`
          ),
          createInfoLine(
            {text['claude_context_strategy']!r},
            summarizeClaudeContext(provider)
          ),
          createInfoLine(
            {text['claude_timeout']!r},
            summarizeClaudeTimeout(provider)
          ),
          createInfoLine(
            {text['claude_subagent']!r},
            String((provider.env || {{}}).CLAUDE_CODE_SUBAGENT_MODEL || '')
              || (currentUiLanguage() === 'zh-CN' ? '未记录' : 'not recorded')
          ),
          createInfoLine(
            currentUiLanguage() === 'zh-CN' ? '配置健康' : 'config',
            formatConfigHealth(config)
          ),
          createInfoLine(
            {text['claude_extensions']!r},
            summarizeClaudeMcp(
              mcp.summary || (
                currentUiLanguage() === 'zh-CN'
                  ? `状态码 ${{mcp.exit_code ?? 'unknown'}}`
                  : `exit_code=${{mcp.exit_code ?? 'unknown'}}`
              )
            )
          ),
          createInfoLine(
            {text['claude_usage_note']!r},
            usage.note || {text['claude_unknown_usage']!r}
          )
        );
      }}
      claudeProviders.appendChild(row);
    }});
    if (!providers.length) {{
      claudeProviders.innerHTML = `<p class="meta">{text['not_recorded']}</p>`;
    }}
    updateClaudeSurfaceSummary(payload);

  }}

  async function refreshClaudeStatus() {{
    if (!claudeProviders) {{
      return;
    }}
    setPanelCacheState('claude', claudeLoaded ? 'refreshing' : 'cold');
    try {{
      const response = await fetch('/api/claude/status');
      const payload = await response.json();
      if (!response.ok) {{
        claudeProviders.innerHTML = `<p class="meta">${{payload.error || response.statusText}}</p>`;
        setPanelCacheState('claude', 'error');
        return;
      }}
      renderClaudeStatus(payload);
      writePanelCache(claudeCacheKey, payload);
      claudeLoaded = true;
      setPanelCacheState('claude', 'ready', payload.cached_at);
    }} catch (error) {{
      claudeProviders.innerHTML = `<p class="meta">${{String(error)}}</p>`;
      setPanelCacheState('claude', 'error');
    }}
  }}

  async function switchClaudeProvider(name) {{
    const targetName = String(name || '').trim();
    if (!targetName) {{
      return;
    }}
    setBusy(true);
    try {{
      const response = await fetch('/api/claude/switch', {{
        method: 'POST',
        headers: {{ 'content-type': 'application/json' }},
        body: JSON.stringify({{ name: targetName }})
      }});
      const payload = await response.json();
      setOutput(JSON.stringify(payload, null, 2));
      await refreshClaudeStatus();
    }} catch (error) {{
      setOutput(String(error));
    }} finally {{
      setBusy(false);
    }}
  }}

  async function optimizeClaudeConfig(apply) {{
    const provider = lastClaudePayload && lastClaudePayload.active_provider ? lastClaudePayload.active_provider : null;
    const providerName = provider && provider.name ? String(provider.name) : '';
    if (!providerName) {{
      setOutput({text['claude_no_active_provider']!r});
      return;
    }}
    setBusy(true);
    try {{
      const response = await fetch('/api/claude/optimize', {{
        method: 'POST',
        headers: {{ 'content-type': 'application/json' }},
        body: JSON.stringify({{ provider: providerName, apply: Boolean(apply) }})
      }});
      const payload = await response.json();
      setOutput(JSON.stringify(payload, null, 2));
      if (apply) {{
        await refreshClaudeStatus();
      }}
    }} catch (error) {{
      setOutput(String(error));
    }} finally {{
      setBusy(false);
    }}
  }}

  async function viewClaudeLocalFile(kind) {{
    const targetKind = String(kind || '').trim();
    if (!targetKind) {{
      return;
    }}
    setBusy(true);
    try {{
      const response = await fetch('/api/claude/file?kind=' + encodeURIComponent(targetKind));
      const payload = await response.json();
      if (!response.ok) {{
        setOutput(payload.error || response.statusText);
      }} else {{
        setOutput(`path: ${{payload.path}}\\n\\n${{payload.content}}`);
      }}
    }} catch (error) {{
      setOutput(String(error));
    }} finally {{
      setBusy(false);
    }}
  }}

  document.querySelectorAll('button[data-action]').forEach((button) => {{
    button.addEventListener('click', () => runAction(button.getAttribute('data-action'), button));
  }});
  document.querySelectorAll('button[data-ref]').forEach((button) => {{
    button.addEventListener('click', () => viewRef(button.getAttribute('data-ref')));
  }});
  historyList.addEventListener('click', (event) => {{
    const button = event.target.closest('button[data-history-index]');
    if (!button) {{
      return;
    }}
    const item = readHistory()[Number(button.dataset.historyIndex)];
    if (item) {{
      setOutput(item.output || '');
    }}
  }});
  document.querySelector('[data-clear-history]').addEventListener('click', () => {{
    writeHistory([]);
    renderHistory();
  }});
  document.querySelector('[data-refresh]').addEventListener('click', () => window.location.reload());
  document.querySelector('[data-codex-refresh]').addEventListener('click', () => refreshCodexStatus());
  document.querySelector('[data-codex-refresh-online]').addEventListener('click', () => refreshCodexStatusOnline());
  document.querySelector('[data-codex-usage]').addEventListener('click', () => window.open('https://chatgpt.com/codex/settings/usage', '_blank', 'noopener'));
  codexAccounts.addEventListener('click', (event) => {{
    const syncButton = event.target.closest('button[data-codex-sync-name]');
    if (syncButton) {{
      syncCodexActiveSnapshot(
        syncButton.getAttribute('data-codex-sync-name') || '',
        syncButton.getAttribute('data-confirm') || ''
      );
      return;
    }}
    const button = event.target.closest('button[data-codex-switch-name]');
    if (!button) {{
      return;
    }}
    switchCodexAccount(button.getAttribute('data-codex-switch-name') || '');
  }});
  document.querySelector('[data-claude-refresh]').addEventListener('click', () => refreshClaudeStatus());
  document.querySelector('[data-claude-optimize-preview]').addEventListener('click', () => optimizeClaudeConfig(false));
  document.querySelector('[data-claude-optimize-apply]').addEventListener('click', (event) => {{
    const message = event.currentTarget.getAttribute('data-confirm');
    if (message && !window.confirm(message)) {{
      return;
    }}
    optimizeClaudeConfig(true);
  }});
  document.querySelectorAll('button[data-claude-file]').forEach((button) => {{
    button.addEventListener('click', () => viewClaudeLocalFile(button.getAttribute('data-claude-file') || ''));
  }});
  claudeProviders.addEventListener('click', (event) => {{
    const button = event.target.closest('button[data-claude-switch-name]');
    if (!button) {{
      return;
    }}
    switchClaudeProvider(button.getAttribute('data-claude-switch-name') || '');
  }});
  document.querySelector('[data-feedback-refresh]').addEventListener('click', () => refreshFeedbackSummaryWithMode(true));
  const nextWorkRefreshButton = document.querySelector('[data-next-work-refresh]');
  if (nextWorkRefreshButton) {{
    nextWorkRefreshButton.addEventListener('click', () => refreshNextWorkSummaryWithMode(true));
  }}
  document.querySelectorAll('button[data-open-view]').forEach((button) => {{
    button.addEventListener('click', () => {{
      const selected = button.getAttribute('data-open-view');
      if (selected) {{
        activateView(selected);
      }}
    }});
  }});
  document.querySelectorAll('[data-view-tab]').forEach((button) => {{
    button.addEventListener('click', () => {{
      const selected = button.getAttribute('data-view-tab');
      if (selected) {{
        activateView(selected);
      }}
    }});
  }});
  if (targetAll) {{
    targetAll.addEventListener('change', () => syncTargetControls());
  }}
  targetOptions.forEach((item) => {{
    item.addEventListener('change', () => syncTargetControls());
  }});
  if (applyRemoval) {{
    applyRemoval.addEventListener('change', () => {{
      if (applyRemoval.checked && dryRun) {{
        dryRun.checked = false;
      }}
    }});
  }}
  if (dryRun) {{
    dryRun.addEventListener('change', () => {{
      if (dryRun.checked && applyRemoval) {{
        applyRemoval.checked = false;
      }}
    }});
  }}
  languageSelect.addEventListener('change', () => {{
    const next = new URL(window.location.href);
    next.searchParams.set('lang', languageSelect.value);
    window.location.href = next.toString();
  }});
  syncTargetControls();
  renderHistory();
  updateRuntimeSurfaceSummary();
  hydratePanelCache('codex', codexCacheKey);
  hydratePanelCache('claude', claudeCacheKey);
  hydratePanelCache('feedback', feedbackCacheKey);
  hydratePanelCache('next-work', nextWorkCacheKey);
  activateView('runtime');
  window.setTimeout(() => {{
    refreshCodexStatus();
    refreshClaudeStatus();
    refreshFeedbackSummary();
  }}, 120);
  window.setTimeout(() => {{
    refreshNextWorkSummary();
  }}, 80);
  document.addEventListener('visibilitychange', () => {{
    if (!document.hidden) {{
      maybeRefreshCodexStatusOnResume();
    }}
  }});
  window.addEventListener('focus', () => {{
    maybeRefreshCodexStatusOnResume();
  }});
  window.setInterval(() => {{
    maybeRefreshCodexStatusOnResume();
  }}, 60000);
}})();
</script>"""


def _state_class(value: str) -> str:
    normalized = value.lower()
    if normalized in {"failed", "blocked", "rejected", "missing", "denied"}:
        return "danger"
    if normalized in {"pending", "escalated", "warning", "warn", "advisory"}:
        return "warn"
    return ""


def _ui_text(language: str) -> dict[str, str]:
    normalized = "en" if language.lower().startswith("en") else "zh-CN"
    return _TRANSLATIONS[normalized]
