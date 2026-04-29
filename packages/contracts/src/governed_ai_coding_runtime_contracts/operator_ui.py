"""Local HTML renderer for the runtime operator surface."""

from html import escape
from pathlib import Path

from governed_ai_coding_runtime_contracts.file_guard import atomic_write_text
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeSnapshot


_TRANSLATIONS = {
    "zh-CN": {
        "html_lang": "zh-CN",
        "title": "Governed Runtime 操作者面板",
        "runtime_root": "Runtime 根目录",
        "persistence": "持久化",
        "summary_aria": "Runtime 摘要",
        "tasks": "任务",
        "tasks_caption": "runtime task 记录",
        "approvals": "审批",
        "approvals_caption": "关联 approval refs",
        "verification": "验证",
        "verification_caption": "verification refs",
        "attachments": "接入仓",
        "fail_closed_caption": "fail-closed",
        "maintenance": "维护策略",
        "stage": "阶段",
        "compatibility": "兼容性",
        "upgrade": "升级",
        "triage": "分流",
        "deprecation": "弃用",
        "retirement": "退役",
        "no_tasks": "暂无 governed task 记录。",
        "no_attachments": "暂无已接入目标仓记录。",
        "task": "任务",
        "state": "状态",
        "goal": "目标",
        "outputs": "输出",
        "run": "运行",
        "workspace": "工作区",
        "interaction": "交互",
        "rollback": "回滚",
        "repo": "仓库",
        "adapter": "适配器",
        "diagnostics": "诊断",
        "binding": "绑定",
        "light_pack": "Light pack",
        "fail_closed": "Fail closed",
        "preference": "偏好",
        "gate_profile": "门禁 profile",
        "reason": "原因",
        "remediation": "修复建议",
        "missing": "缺失",
        "none": "无",
        "not_recorded": "未记录",
        "unknown_repo": "未知仓库",
        "actions": "操作",
        "settings": "设置",
        "language": "语言",
        "target": "目标仓",
        "all_targets": "全部目标仓",
        "mode": "验证模式",
        "parallelism": "目标并发",
        "fail_fast": "失败即停",
        "dry_run": "只预演",
        "milestone": "里程碑标签",
        "refresh": "刷新状态",
        "run": "执行",
        "command_output": "命令输出",
        "codex_console": "Codex 账号与配置",
        "codex_account": "账号",
        "codex_active": "当前",
        "codex_usage": "额度",
        "codex_usage_note": "额度数据源",
        "codex_switch": "切换",
        "codex_open_usage": "打开官方 Usage",
        "codex_refresh": "刷新 Codex 状态",
        "codex_unknown_usage": "未知；官方未提供稳定本地 API",
        "codex_config": "配置健康",
        "codex_login": "登录状态",
        "history": "执行历史",
        "no_history": "暂无执行历史。",
        "clear_history": "清空历史",
        "runtime_view": "Runtime",
        "codex_view": "Codex",
        "ready": "就绪",
        "running": "执行中",
        "static_snapshot": "静态快照",
        "targets_action": "列出目标仓",
        "readiness_action": "本仓 Readiness",
        "rules_dry_run_action": "规则漂移检查",
        "rules_apply_action": "同步规则文件",
        "governance_baseline_action": "下发治理基线",
        "daily_all_action": "运行 Daily",
        "apply_all_action": "全部功能应用",
        "view_ref": "查看",
        "confirm_mutating": "该操作可能修改规则文件、目标仓治理基线或运行证据。继续执行？",
        "interactive_required": "当前是静态快照；启动本地服务后可执行操作。",
    },
    "en": {
        "html_lang": "en",
        "title": "Governed Runtime Operator Surface",
        "runtime_root": "Runtime root",
        "persistence": "Persistence",
        "summary_aria": "Runtime Summary",
        "tasks": "Tasks",
        "tasks_caption": "runtime task records",
        "approvals": "Approvals",
        "approvals_caption": "linked approval refs",
        "verification": "Verification",
        "verification_caption": "verification refs",
        "attachments": "Attachments",
        "fail_closed_caption": "fail-closed",
        "maintenance": "Maintenance Policy Surface",
        "stage": "Stage",
        "compatibility": "Compatibility",
        "upgrade": "Upgrade",
        "triage": "Triage",
        "deprecation": "Deprecation",
        "retirement": "Retirement",
        "no_tasks": "No governed tasks recorded.",
        "no_attachments": "No attached target repos recorded.",
        "task": "Task",
        "state": "State",
        "goal": "Goal",
        "outputs": "Outputs",
        "run": "Run",
        "workspace": "Workspace",
        "interaction": "Interaction",
        "rollback": "Rollback",
        "repo": "Repo",
        "adapter": "Adapter",
        "diagnostics": "Diagnostics",
        "binding": "Binding",
        "light_pack": "Light pack",
        "fail_closed": "Fail closed",
        "preference": "Preference",
        "gate_profile": "Gate profile",
        "reason": "Reason",
        "remediation": "Remediation",
        "missing": "missing",
        "none": "none",
        "not_recorded": "not recorded",
        "unknown_repo": "unknown repo",
        "actions": "Actions",
        "settings": "Settings",
        "language": "Language",
        "target": "Target repo",
        "all_targets": "All targets",
        "mode": "Mode",
        "parallelism": "Target parallelism",
        "fail_fast": "Fail fast",
        "dry_run": "Dry run",
        "milestone": "Milestone tag",
        "refresh": "Refresh status",
        "run": "Run",
        "command_output": "Command output",
        "codex_console": "Codex Account and Config",
        "codex_account": "Account",
        "codex_active": "Active",
        "codex_usage": "Usage",
        "codex_usage_note": "Usage source",
        "codex_switch": "Switch",
        "codex_open_usage": "Open Usage",
        "codex_refresh": "Refresh Codex",
        "codex_unknown_usage": "Unknown; no stable local public API",
        "codex_config": "Config health",
        "codex_login": "Login status",
        "history": "Run history",
        "no_history": "No run history.",
        "clear_history": "Clear history",
        "runtime_view": "Runtime",
        "codex_view": "Codex",
        "ready": "Ready",
        "running": "Running",
        "static_snapshot": "Static snapshot",
        "targets_action": "List targets",
        "readiness_action": "Repo readiness",
        "rules_dry_run_action": "Rule drift check",
        "rules_apply_action": "Sync rules",
        "governance_baseline_action": "Apply governance baseline",
        "daily_all_action": "Run Daily",
        "apply_all_action": "Apply all features",
        "view_ref": "View",
        "confirm_mutating": "This action may modify rule files, target governance baseline, or runtime evidence. Continue?",
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
    script = _render_interactive_script(text, language=language) if interactive else ""
    runtime_root = snapshot.runtime_root or text["missing"]
    tabs = _render_view_tabs(text)
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
      --bg: #f7f9fb;
      --surface: #ffffff;
      --surface-muted: #eef3f7;
      --ink: #17202a;
      --muted: #5f6b7a;
      --line: #d7dde5;
      --accent: #0b6f6a;
      --warning: #a15c00;
      --danger: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "Segoe UI", Arial, sans-serif; background: var(--bg); color: var(--ink); font-size: 14px; }}
    main {{ width: 100%; max-width: 1560px; margin: 0 auto; padding: 16px 18px 32px; }}
    header {{ border-bottom: 1px solid var(--line); padding-bottom: 14px; margin-bottom: 14px; }}
    h1 {{ font-size: 1.5rem; line-height: 1.2; margin: 0 0 8px; }}
    h2 {{ font-size: 0.96rem; line-height: 1.3; margin: 0 0 10px; color: var(--ink); }}
    .meta-row {{ display: flex; flex-wrap: wrap; gap: 10px 18px; color: var(--muted); font-size: 0.92rem; }}
    .console-layout {{ display: grid; grid-template-columns: minmax(260px, 300px) minmax(0, 1fr); gap: 14px; align-items: start; }}
    .sidebar {{ position: sticky; top: 12px; display: grid; gap: 12px; align-self: start; }}
    .dashboard {{ min-width: 0; display: grid; gap: 14px; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }}
    .feedback-grid {{ display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.65fr); gap: 14px; align-items: start; }}
    .details-grid {{ display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr); gap: 14px; align-items: start; }}
    .metric {{ background: var(--surface); border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 6px; padding: 12px; min-width: 0; }}
    .metric span {{ display: block; color: var(--muted); font-size: 0.78rem; text-transform: uppercase; }}
    .metric strong {{ display: block; font-size: 1.32rem; margin: 3px 0; }}
    .metric small {{ display: block; color: var(--muted); overflow-wrap: anywhere; }}
    .section {{ min-width: 0; }}
    .table-wrap {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 720px; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: var(--surface-muted); color: #314253; font-size: 0.78rem; text-transform: uppercase; }}
    tr:last-child td {{ border-bottom: 0; }}
    .task-id {{ font-weight: 700; }}
    .state {{ font-weight: 700; color: var(--accent); }}
    .state.warn {{ color: var(--warning); }}
    .state.danger {{ color: var(--danger); }}
    .meta {{ color: var(--muted); font-size: 0.86rem; margin-top: 4px; overflow-wrap: anywhere; }}
    .empty-state {{ background: var(--surface); border: 1px dashed var(--line); border-radius: 6px; padding: 18px; color: var(--muted); }}
    .refs {{ display: grid; gap: 8px; }}
    .ref-title {{ display: block; color: var(--muted); font-size: 0.78rem; text-transform: uppercase; margin-bottom: 4px; }}
    ul {{ margin: 0; padding-left: 18px; }}
    li + li {{ margin-top: 4px; }}
    code {{ font-family: Consolas, "Liberation Mono", monospace; font-size: 0.9rem; overflow-wrap: anywhere; }}
    .policy-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }}
    .policy-item {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 10px; min-width: 0; }}
    .policy-label {{ display: block; color: var(--muted); font-size: 0.78rem; text-transform: uppercase; margin-bottom: 4px; }}
    .panel {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 12px; min-width: 0; }}
    .view-tabs {{ display: inline-flex; gap: 4px; background: var(--surface-muted); border: 1px solid var(--line); border-radius: 6px; padding: 4px; width: fit-content; max-width: 100%; }}
    .view-tab {{ border: 0; background: transparent; border-radius: 4px; padding: 7px 12px; }}
    .view-tab[aria-selected="true"] {{ background: var(--surface); color: var(--accent); box-shadow: 0 0 0 1px var(--line); font-weight: 700; }}
    .action-list {{ display: grid; gap: 8px; }}
    button, select, input {{ font: inherit; }}
    button {{ border: 1px solid var(--line); background: var(--surface); color: var(--ink); border-radius: 6px; padding: 8px 10px; cursor: pointer; text-align: left; }}
    button:hover {{ border-color: var(--accent); }}
    button.primary {{ background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 700; }}
    button.danger {{ border-color: #f2b8b5; color: var(--danger); }}
    button:disabled {{ cursor: not-allowed; opacity: 0.55; }}
    .setting-grid {{ display: grid; gap: 10px; }}
    label {{ display: grid; gap: 4px; color: var(--muted); font-size: 0.82rem; min-width: 0; }}
    select, input[type="number"], input[type="text"] {{ width: 100%; min-width: 0; max-width: 100%; border: 1px solid var(--line); border-radius: 6px; padding: 8px; color: var(--ink); background: #fff; }}
    .checkbox-row {{ display: flex; align-items: center; gap: 8px; color: var(--ink); }}
    .status-line {{ color: var(--muted); font-size: 0.86rem; min-height: 1.2rem; }}
    .output {{ min-height: 260px; max-height: 460px; overflow: auto; white-space: pre-wrap; background: #0f1720; color: #d9e2ec; border-radius: 6px; padding: 12px; }}
    .history-list {{ display: grid; gap: 8px; }}
    .history-item {{ width: 100%; min-width: 0; display: grid; gap: 2px; }}
    .history-item small {{ color: var(--muted); overflow-wrap: anywhere; }}
    .codex-toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 10px; }}
    .codex-toolbar select {{ width: min(100%, 260px); }}
    .codex-grid {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(280px, 0.8fr); gap: 12px; align-items: start; }}
    .codex-list {{ display: grid; gap: 8px; }}
    .codex-account {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 8px; border: 1px solid var(--line); border-radius: 6px; padding: 10px; }}
    .codex-account strong, .codex-account small {{ display: block; overflow-wrap: anywhere; }}
    .codex-badge {{ display: inline-flex; align-items: center; border: 1px solid var(--line); border-radius: 999px; padding: 2px 8px; color: var(--accent); font-size: 0.78rem; }}
    .ref-button {{ display: inline; padding: 0; border: 0; background: transparent; color: #0b5cad; text-align: left; font-family: Consolas, "Liberation Mono", monospace; font-size: 0.9rem; overflow-wrap: anywhere; }}
    .ref-button:hover {{ text-decoration: underline; }}
    @media (max-width: 820px) {{
      main {{ padding: 14px 12px 32px; }}
      .console-layout, .summary-grid, .policy-grid, .feedback-grid, .details-grid, .codex-grid, .codex-account {{ grid-template-columns: 1fr; }}
      .sidebar {{ position: static; }}
      .output {{ min-height: 220px; }}
      .table-wrap {{ overflow-x: visible; }}
      table, thead, tbody, tr, th, td {{ display: block; min-width: 0; width: 100%; }}
      thead {{ position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); }}
      tr {{ border-bottom: 1px solid var(--line); }}
      tr:last-child {{ border-bottom: 0; }}
      td {{ display: grid; grid-template-columns: 94px minmax(0, 1fr); gap: 10px; border-bottom: 1px solid var(--line); }}
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
        <div data-view-panel="runtime">
          {summary}
          {feedback}
          <div class="details-grid">
            {maintenance}
            {attachments}
          </div>
          {tasks}
        </div>
        <div data-view-panel="codex" hidden>
          {codex_panel}
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
            "</div>",
        ]
    )


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
    interaction = task.interaction_posture or text["not_recorded"]
    state_class = _state_class(task.current_state)
    return "\n".join(
        [
            "<tr>",
            f"<td data-label='{escape(text['task'])}'>",
            f"<div class='task-id'>{escape(task.task_id)}</div>",
            f"<div class='meta'>{escape(text['run'])}: <code>{escape(task.active_run_id or text['missing'])}</code></div>",
            f"<div class='meta'>{escape(text['workspace'])}: <code>{escape(task.workspace_root or text['missing'])}</code></div>",
            "</td>",
            f"<td data-label='{escape(text['state'])}'>",
            f"<div class='state {state_class}'>{escape(task.current_state)}</div>",
            f"<div class='meta'>{escape(text['interaction'])}: {escape(interaction)}</div>",
            f"<div class='meta'>{escape(text['rollback'])}: <code>{escape(task.rollback_ref or text['missing'])}</code></div>",
            "</td>",
            f"<td data-label='{escape(text['goal'])}'>{escape(task.goal)}</td>",
            f"<td data-label='{escape(text['outputs'])}'><div class='refs'>",
            _render_list(text["approvals"], task.approval_ids, text, interactive=interactive),
            _render_list("Artifacts", task.artifact_refs, text, interactive=interactive),
            _render_list("Evidence", task.evidence_refs, text, interactive=interactive),
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
    return "\n".join(
        [
            "<tr>",
            f"<td data-label='{escape(text['repo'])}'>",
            f"<div class='task-id'>{escape(attachment.repo_id or text['unknown_repo'])}</div>",
            f"<div class='meta'>{escape(text['binding'])}: <code>{escape(attachment.binding_id or text['missing'])}</code></div>",
            f"<div class='meta'>{escape(text['light_pack'])}: {_render_ref_value(attachment.light_pack_path, interactive=interactive)}</div>",
            "</td>",
            f"<td data-label='{escape(text['state'])}'>",
            f"<div class='state {state_class}'>{escape(attachment.binding_state)}</div>",
            f"<div class='meta'>{escape(text['fail_closed'])}: {str(attachment.fail_closed).lower()}</div>",
            "</td>",
            f"<td data-label='{escape(text['adapter'])}'>",
            f"<div>{escape(text['preference'])}: <code>{escape(attachment.adapter_preference or text['missing'])}</code></div>",
            f"<div class='meta'>{escape(text['gate_profile'])}: <code>{escape(attachment.gate_profile or text['missing'])}</code></div>",
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
    return "\n".join(
        [
            "<div class='policy-item'>",
            f"<span class='policy-label'>{escape(title)}</span>",
            f"<code>{escape(value or text['missing'])}</code>",
            "</div>",
        ]
    )


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

    action_items = [
        ("targets", text["targets_action"], "primary", ""),
        ("readiness", text["readiness_action"], "primary", ""),
        ("rules_dry_run", text["rules_dry_run_action"], "", ""),
        ("rules_apply", text["rules_apply_action"], "danger", text["confirm_mutating"]),
        ("governance_baseline_all", text["governance_baseline_action"], "danger", text["confirm_mutating"]),
        ("daily_all", text["daily_all_action"], "", ""),
        ("apply_all_features", text["apply_all_action"], "danger", text["confirm_mutating"]),
    ]
    buttons = []
    for action_id, label, class_name, confirm in action_items:
        class_attr = f" class='{class_name}'" if class_name else ""
        confirm_attr = f" data-confirm='{escape(confirm, quote=True)}'" if confirm else ""
        buttons.append(
            f"<button type='button'{class_attr} data-action='{escape(action_id)}'{confirm_attr}>{escape(label)}</button>"
        )
    target_choices = [("__all__", text["all_targets"])] + [(target, target) for target in target_options]
    target_select_options = "".join(
        f"<option value='{escape(value, quote=True)}'>{escape(label)}</option>"
        for value, label in target_choices
    )

    return "\n".join(
        [
            "<aside class='sidebar'>",
            "<section class='panel'>",
            f"<h2>{escape(text['actions'])}</h2>",
            "<div class='action-list'>",
            f"<button type='button' data-refresh='1'>{escape(text['refresh'])}</button>",
            *buttons,
            "</div>",
            "</section>",
            "<section class='panel'>",
            f"<h2>{escape(text['settings'])}</h2>",
            "<div class='setting-grid'>",
            f"<label>{escape(text['language'])}<select id='ui-language'><option value='zh-CN' {'selected' if language == 'zh-CN' else ''}>中文</option><option value='en' {'selected' if language == 'en' else ''}>English</option></select></label>",
            f"<label>{escape(text['target'])}<select id='ui-target'>{target_select_options}</select></label>",
            f"<label>{escape(text['mode'])}<select id='ui-mode'><option value='quick'>quick</option><option value='full'>full</option><option value='l1'>l1</option><option value='l2'>l2</option><option value='l3'>l3</option></select></label>",
            f"<label>{escape(text['parallelism'])}<input id='ui-parallelism' type='number' min='1' max='16' value='1'></label>",
            f"<label>{escape(text['milestone'])}<input id='ui-milestone' type='text' value='milestone'></label>",
            f"<label class='checkbox-row'><input id='ui-fail-fast' type='checkbox'> {escape(text['fail_fast'])}</label>",
            f"<label class='checkbox-row'><input id='ui-dry-run' type='checkbox'> {escape(text['dry_run'])}</label>",
            "</div>",
            "</section>",
            "</aside>",
        ]
    )


def _render_feedback(text: dict[str, str], *, interactive: bool) -> str:
    if not interactive:
        return ""
    return "\n".join(
        [
            "<section class='feedback-grid'>",
            "<div class='panel'>",
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
            f"<button type='button' data-codex-refresh='1'>{escape(text['codex_refresh'])}</button>",
            "<select id='codex-account-select' aria-label='Codex account'></select>",
            f"<button type='button' data-codex-switch='1'>{escape(text['codex_switch'])}</button>",
            f"<button type='button' data-codex-usage='1'>{escape(text['codex_open_usage'])}</button>",
            "</div>",
            "<div class='codex-grid'>",
            "<div>",
            f"<div class='status-line' id='codex-login'>{escape(text['codex_login'])}: {escape(text['not_recorded'])}</div>",
            "<div id='codex-accounts' class='codex-list'></div>",
            "</div>",
            "<div>",
            f"<div class='policy-item'><span class='policy-label'>{escape(text['codex_usage'])}</span><code id='codex-usage'>{escape(text['codex_unknown_usage'])}</code><div class='meta' id='codex-usage-note'>{escape(text['codex_usage_note'])}: unknown</div></div>",
            f"<div class='policy-item' style='margin-top: 10px;'><span class='policy-label'>{escape(text['codex_config'])}</span><div id='codex-config' class='meta'>{escape(text['not_recorded'])}</div></div>",
            "</div>",
            "</div>",
            "</section>",
        ]
    )


def _render_interactive_script(text: dict[str, str], *, language: str) -> str:
    return f"""
<script>
(() => {{
  const output = document.getElementById('ui-output');
  const status = document.getElementById('ui-status');
  const outputPanel = output.closest('.panel');
  const languageSelect = document.getElementById('ui-language');
  const target = document.getElementById('ui-target');
  const mode = document.getElementById('ui-mode');
  const parallelism = document.getElementById('ui-parallelism');
  const milestone = document.getElementById('ui-milestone');
  const failFast = document.getElementById('ui-fail-fast');
  const dryRun = document.getElementById('ui-dry-run');
  const historyList = document.getElementById('ui-history');
  const codexAccounts = document.getElementById('codex-accounts');
  const codexAccountSelect = document.getElementById('codex-account-select');
  const codexLogin = document.getElementById('codex-login');
  const codexUsage = document.getElementById('codex-usage');
  const codexUsageNote = document.getElementById('codex-usage-note');
  const codexConfig = document.getElementById('codex-config');
  const historyKey = 'governed-runtime-operator-history';
  let codexLoaded = false;

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

  function setBusy(isBusy) {{
    status.textContent = isBusy ? {text['running']!r} : {text['ready']!r};
    document.querySelectorAll('button[data-action]').forEach((button) => button.disabled = isBusy);
  }}

  async function runAction(action, button) {{
    const confirmMessage = button.getAttribute('data-confirm');
    if (confirmMessage && !window.confirm(confirmMessage)) {{
      return;
    }}
    setBusy(true);
    setOutput('');
    try {{
      const response = await fetch('/api/run', {{
        method: 'POST',
        headers: {{ 'content-type': 'application/json' }},
        body: JSON.stringify({{
          action,
          language: languageSelect.value,
          target: target.value,
          mode: mode.value,
          target_parallelism: Number(parallelism.value || 1),
          milestone_tag: milestone.value || 'milestone',
          fail_fast: failFast.checked,
          dry_run: dryRun.checked
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
        target: target.value,
        exit_code: payload.exit_code,
        elapsed_seconds: payload.elapsed_seconds,
        at: new Date().toLocaleString(),
        output: rendered
      }});
    }} catch (error) {{
      setOutput(String(error));
    }} finally {{
      setBusy(false);
    }}
  }}

  async function viewRef(path) {{
    setBusy(true);
    try {{
      const response = await fetch('/api/file?path=' + encodeURIComponent(path));
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

  function renderCodexStatus(payload) {{
    const accounts = Array.isArray(payload.accounts) ? payload.accounts : [];
    codexAccountSelect.innerHTML = '';
    codexAccounts.innerHTML = '';
    accounts.forEach((account) => {{
      const option = document.createElement('option');
      option.value = account.name;
      option.textContent = `${{account.active ? '* ' : ''}}${{account.name}} · ${{account.account_hash || 'unknown'}}`;
      option.selected = Boolean(account.active);
      codexAccountSelect.appendChild(option);

      const row = document.createElement('div');
      row.className = 'codex-account';
      const body = document.createElement('div');
      const name = document.createElement('strong');
      name.textContent = account.name;
      const meta = document.createElement('small');
      meta.className = 'meta';
      meta.textContent = `${{account.auth_mode || 'unknown'}} · ${{account.last_refresh || 'no refresh'}} · ${{account.account_hash || 'no account hash'}}`;
      body.append(name, meta);
      row.appendChild(body);
      if (account.active) {{
        const badge = document.createElement('span');
        badge.className = 'codex-badge';
        badge.textContent = {text['codex_active']!r};
        row.appendChild(badge);
      }}
      codexAccounts.appendChild(row);
    }});
    if (!accounts.length) {{
      codexAccounts.innerHTML = `<p class="meta">{text['not_recorded']}</p>`;
    }}

    const login = payload.login_status || {{}};
    codexLogin.textContent = `{text['codex_login']}: ${{login.summary || login.exit_code || 'unknown'}}`;
    const usage = payload.usage || {{}};
    const windows = Array.isArray(usage.windows) ? usage.windows.map((item) => `${{item.window}}=${{item.remaining ?? 'unknown'}}`).join(' · ') : {text['codex_unknown_usage']!r};
    codexUsage.textContent = windows || {text['codex_unknown_usage']!r};
    codexUsageNote.textContent = `{text['codex_usage_note']}: ${{usage.source || 'unknown'}}`;
    const config = payload.config || {{}};
    const failedChecks = Array.isArray(config.checks) ? config.checks.filter((check) => !check.ok).map((check) => check.key) : [];
    codexConfig.textContent = failedChecks.length ? `attention: ${{failedChecks.join(', ')}}` : (config.status || 'ok');
  }}

  async function refreshCodexStatus() {{
    if (!codexAccounts) {{
      return;
    }}
    try {{
      const response = await fetch('/api/codex/status');
      const payload = await response.json();
      if (!response.ok) {{
        codexAccounts.innerHTML = `<p class="meta">${{payload.error || response.statusText}}</p>`;
        return;
      }}
      renderCodexStatus(payload);
      codexLoaded = true;
    }} catch (error) {{
      codexAccounts.innerHTML = `<p class="meta">${{String(error)}}</p>`;
    }}
  }}

  async function switchCodexAccount() {{
    const name = codexAccountSelect.value;
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
  document.querySelector('[data-codex-switch]').addEventListener('click', () => switchCodexAccount());
  document.querySelector('[data-codex-usage]').addEventListener('click', () => window.open('https://chatgpt.com/codex/settings/usage', '_blank', 'noopener'));
  document.querySelectorAll('[data-view-tab]').forEach((button) => {{
    button.addEventListener('click', () => {{
      const selected = button.getAttribute('data-view-tab');
      document.querySelectorAll('[data-view-tab]').forEach((tab) => {{
        tab.setAttribute('aria-selected', String(tab === button));
      }});
      document.querySelectorAll('[data-view-panel]').forEach((panel) => {{
        panel.hidden = panel.getAttribute('data-view-panel') !== selected;
      }});
      if (selected === 'codex' && !codexLoaded) {{
        refreshCodexStatus();
      }}
    }});
  }});
  languageSelect.addEventListener('change', () => {{
    const next = new URL(window.location.href);
    next.searchParams.set('lang', languageSelect.value);
    window.location.href = next.toString();
  }});
  renderHistory();
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
