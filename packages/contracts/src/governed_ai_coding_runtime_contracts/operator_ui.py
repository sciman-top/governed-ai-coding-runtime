"""Local HTML renderer for the runtime operator surface."""

from html import escape
from pathlib import Path

from governed_ai_coding_runtime_contracts.runtime_status import RuntimeSnapshot


def render_runtime_snapshot_html(snapshot: RuntimeSnapshot) -> str:
    maintenance = "\n".join(
        [
            "<section class='policy-card'>",
            "<h2>Maintenance Policy Surface</h2>",
            f"<p><strong>Stage:</strong> {escape(snapshot.maintenance.stage)}</p>",
            _render_ref("Compatibility", snapshot.maintenance.compatibility_policy_ref),
            _render_ref("Upgrade", snapshot.maintenance.upgrade_policy_ref),
            _render_ref("Triage", snapshot.maintenance.triage_policy_ref),
            _render_ref("Deprecation", snapshot.maintenance.deprecation_policy_ref),
            _render_ref("Retirement", snapshot.maintenance.retirement_policy_ref),
            "</section>",
        ]
    )
    if not snapshot.tasks:
        body = "<p>No governed tasks recorded.</p>"
    else:
        cards = []
        for task in snapshot.tasks:
            cards.append(
                "\n".join(
                    [
                        "<article class='task-card'>",
                        f"<h2>{escape(task.task_id)}</h2>",
                        f"<p><strong>State:</strong> {escape(task.current_state)}</p>",
                        f"<p><strong>Goal:</strong> {escape(task.goal)}</p>",
                        f"<p><strong>Run:</strong> {escape(task.active_run_id or '')}</p>",
                        f"<p><strong>Workspace:</strong> {escape(task.workspace_root or '')}</p>",
                        _render_list("Artifacts", task.artifact_refs),
                        _render_list("Evidence", task.evidence_refs),
                        _render_list("Verification", task.verification_refs),
                        "</article>",
                    ]
                )
            )
        body = "\n".join(cards)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Governed Runtime Operator Surface</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f1e8;
      --card: #fffdf8;
      --ink: #1f2933;
      --line: #d8c9ad;
      --accent: #0f766e;
    }}
    body {{ margin: 0; font-family: Georgia, 'Times New Roman', serif; background: radial-gradient(circle at top, #fff7e8, var(--bg)); color: var(--ink); }}
    main {{ max-width: 980px; margin: 0 auto; padding: 40px 24px 80px; }}
    h1 {{ font-size: 2.4rem; margin-bottom: 0.3rem; }}
    .summary {{ color: #5b6470; margin-bottom: 24px; }}
    .task-card, .policy-card {{ background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 20px; margin-bottom: 16px; box-shadow: 0 10px 30px rgba(15, 118, 110, 0.08); }}
    h2 {{ margin-top: 0; color: var(--accent); }}
    ul {{ padding-left: 20px; }}
    code {{ font-family: Consolas, monospace; font-size: 0.92rem; }}
  </style>
</head>
<body>
  <main>
    <h1>Governed Runtime Operator Surface</h1>
    <p class="summary">Total tasks: {snapshot.total_tasks}</p>
    {maintenance}
    {body}
  </main>
</body>
</html>"""


def write_runtime_snapshot_html(snapshot: RuntimeSnapshot, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_runtime_snapshot_html(snapshot), encoding="utf-8")
    return output_path


def _render_list(title: str, values: list[str]) -> str:
    if not values:
        return f"<p><strong>{escape(title)}:</strong> none</p>"
    items = "".join(f"<li><code>{escape(value)}</code></li>" for value in values)
    return f"<div><strong>{escape(title)}:</strong><ul>{items}</ul></div>"


def _render_ref(title: str, value: str | None) -> str:
    return f"<p><strong>{escape(title)}:</strong> <code>{escape(value or 'missing')}</code></p>"
