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
    del target_options
    text = _ui_text(language)
    approval_count = sum(len(task.approval_ids) for task in snapshot.tasks)
    verification_count = sum(len(task.verification_refs) for task in snapshot.tasks)
    summary = "\n".join(
        [
            f"<section class='summary-grid' aria-label='{escape(text['summary_aria'])}'>",
            _render_metric(text["tasks"], str(snapshot.total_tasks), text["tasks_caption"]),
            _render_metric(text["approvals"], str(approval_count), text["approvals_caption"]),
            _render_metric(text["verification"], str(verification_count), text["verification_caption"]),
            _render_metric(text["stage"], _humanize_runtime_value(snapshot.maintenance.stage, language=text["html_lang"]), text["stage_metric_caption"]),
            "</section>",
        ]
    )
    maintenance = _render_maintenance(snapshot, text)
    tasks = _render_tasks(snapshot, text, interactive=interactive)
    actions = _render_actions(text, language=language, interactive=interactive)
    feedback = _render_feedback(text, interactive=interactive)
    continuity_panel = _render_continuity_panel(text, interactive=interactive)
    feedback_panel = _render_host_feedback_panel(text, interactive=interactive)
    script = (
        render_interactive_script(
            text,
            language=language,
            total_tasks=snapshot.total_tasks,
            approval_count=approval_count,
            verification_count=verification_count,
        )
        if interactive
        else ""
    )
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
              </div>
            </div>
          </div>
          {tasks}
        </div>
        <div data-view-panel="continuity" hidden>
          {continuity_panel}
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
            f"<button type='button' class='view-tab' role='tab' aria-selected='false' data-view-tab='continuity'>{escape(text['continuity_view'])}</button>",
            f"<button type='button' class='view-tab' role='tab' aria-selected='false' data-view-tab='feedback'>{escape(text['feedback_view'])}</button>",
            "</div>",
        ]
    )


def _render_workspace_overview(text: dict[str, str], *, interactive: bool) -> str:
    surfaces = [
        ("runtime", text["runtime_view"], text["runtime_surface_caption"], True),
        ("continuity", text["continuity_view"], text["continuity_surface_caption"], False),
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
            _surface_action_text(surface_id, text),
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


def _surface_action_text(surface_id: str, text: dict[str, str]) -> str:
    mapping = {
        "runtime": text["surface_runtime_action"],
        "continuity": text["surface_continuity_action"],
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


def _render_actions(text: dict[str, str], *, language: str, interactive: bool) -> str:
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
                ("codex_guard_absence_check", text["codex_guard_absence_action"], "", ""),
            ],
        ),
        (
            text["rule_actions"],
            False,
            [
                ("rules_dry_run", text["rules_dry_run_action"], "", ""),
                ("rules_apply", text["rules_apply_action"], "danger", text["confirm_mutating"]),
                ("self_evolution_recommend", text["self_evolution_recommend_action"], "", ""),
                ("self_evolution_promotion_plan", text["self_evolution_promotion_action"], "", ""),
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
            f"<label>{escape(text['mode'])}<select id='ui-mode'><option value='quick'>quick</option><option value='full'>full</option><option value='l1'>l1</option><option value='l2'>l2</option><option value='l3'>l3</option></select></label>",
            f"<label class='checkbox-row'><input id='ui-dry-run' type='checkbox'> {escape(text['dry_run'])}</label>",
            "<details class='foldout'>",
            f"<summary>{escape(text['advanced_settings'])}</summary>",
            f"<label>{escape(text['parallelism'])}<input id='ui-parallelism' type='number' min='1' max='16' value='1'></label>",
            f"<label>{escape(text['milestone'])}<input id='ui-milestone' type='text' value='milestone'></label>",
            f"<label class='checkbox-row'><input id='ui-fail-fast' type='checkbox'> {escape(text['fail_fast'])}</label>",
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
        ("feedback_report", text["shortcut_feedback"], text["shortcut_feedback_command"], text["shortcut_feedback_caption"], False),
        ("rules_dry_run", text["shortcut_rules"], text["shortcut_rules_command"], text["shortcut_rules_caption"], False),
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


def _render_continuity_panel(text: dict[str, str], *, interactive: bool) -> str:
    if not interactive:
        return "\n".join(
            [
                "<section class='panel'>",
                f"<h2>{escape(text['continuity_console'])}</h2>",
                f"<p class='meta'>{escape(text['interactive_required'])}</p>",
                "</section>",
            ]
        )
    return "\n".join(
        [
            "<section class='panel'>",
            f"<h2>{escape(text['continuity_console'])}</h2>",
            f"<p class='meta'>{escape(text['continuity_caption'])}</p>",
            "<div class='panel-toolbar'>",
            f"<button type='button' data-continuity-refresh='1'>{escape(text['continuity_refresh'])}</button>",
            "</div>",
            f"<div class='status-line' id='continuity-status'>{escape(text['continuity_status'])}: {escape(text['panel_cache_cold'])}</div>",
            "<div id='continuity-records' class='feedback-summary-grid'></div>",
            "<pre id='continuity-json' class='output'></pre>",
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
            "<div class='panel-toolbar'>",
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
            "<section class='panel self-evolution-panel'>",
            f"<h2>{escape(text['self_evolution_recommendations'])}</h2>",
            "<div class='panel-toolbar'>",
            f"<button type='button' data-self-evolution-refresh='1'>{escape(text['self_evolution_refresh'])}</button>",
            "</div>",
            f"<div class='status-line' id='self-evolution-status'>{escape(text['self_evolution_status'])}: {escape(text['self_evolution_loading'])}</div>",
            f"<div class='status-line' id='self-evolution-cache-state'>{escape(text['panel_cache_state'])}: {escape(text['panel_cache_cold'])}</div>",
            f"<div class='status-line' id='self-evolution-generated-at'>{escape(text['self_evolution_generated_at'])}: {escape(text['not_recorded'])}</div>",
            "<div id='self-evolution-summary' class='feedback-summary-grid'></div>",
            "<div id='self-evolution-lanes' class='self-evolution-lanes'></div>",
            "<div id='self-evolution-report-link' class='refs'></div>",
            "<details><summary>",
            escape(text["self_evolution_view_json"]),
            "</summary><pre id='self-evolution-json' class='output'></pre></details>",
            "</section>",
            "<section class='panel self-evolution-panel'>",
            f"<h2>{escape(text['self_evolution_promotion_title'])}</h2>",
            "<div class='panel-toolbar'>",
            f"<button type='button' data-self-evolution-promotion-refresh='1'>{escape(text['self_evolution_promotion_refresh'])}</button>",
            "</div>",
            f"<div class='status-line' id='self-evolution-promotion-status'>{escape(text['self_evolution_promotion_status'])}: {escape(text['self_evolution_promotion_loading'])}</div>",
            f"<div class='status-line' id='self-evolution-promotion-cache-state'>{escape(text['panel_cache_state'])}: {escape(text['panel_cache_cold'])}</div>",
            f"<div class='status-line' id='self-evolution-promotion-generated-at'>{escape(text['self_evolution_generated_at'])}: {escape(text['not_recorded'])}</div>",
            "<div id='self-evolution-promotion-summary' class='feedback-summary-grid'></div>",
            "<div id='self-evolution-promotion-lanes' class='self-evolution-lanes'></div>",
            "<div id='self-evolution-promotion-report-link' class='refs'></div>",
            "<details><summary>",
            escape(text["self_evolution_promotion_view_json"]),
            "</summary><pre id='self-evolution-promotion-json' class='output'></pre></details>",
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
        "quick": "快速",
        "full": "完整",
        "l1": "L1 基础",
        "l2": "L2 标准",
        "l3": "L3 深度",
    }
    if language == "zh-CN":
        return zh_map.get(lower, normalized)
    return normalized


def _ui_text(language: str) -> dict[str, str]:
    normalized = "en" if language.lower().startswith("en") else "zh-CN"
    return TRANSLATIONS[normalized]
