"""Local HTML renderer for the runtime operator surface."""

from html import escape
from pathlib import Path

from governed_ai_coding_runtime_contracts.file_guard import atomic_write_text
from governed_ai_coding_runtime_contracts.operator_ui_script import render_interactive_script
from governed_ai_coding_runtime_contracts.operator_ui_style import render_style_block
from governed_ai_coding_runtime_contracts.operator_ui_text import TRANSLATIONS
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeSnapshot


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
    script = render_interactive_script(
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
{render_style_block()}
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


def _state_class(value: str) -> str:
    normalized = value.lower()
    if normalized in {"failed", "blocked", "rejected", "missing", "denied"}:
        return "danger"
    if normalized in {"pending", "escalated", "warning", "warn", "advisory"}:
        return "warn"
    return ""


def _ui_text(language: str) -> dict[str, str]:
    normalized = "en" if language.lower().startswith("en") else "zh-CN"
    return TRANSLATIONS[normalized]
