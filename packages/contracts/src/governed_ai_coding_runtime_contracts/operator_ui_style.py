"""CSS renderer for the runtime operator surface."""

from __future__ import annotations


def render_style_block() -> str:
    return f"""  <style>
    :root {{
      color-scheme: light;
      --bg: #f3f6f6;
      --bg-deep: #0b171b;
      --surface: #ffffff;
      --surface-raised: rgba(255, 255, 255, 0.965);
      --surface-muted: #edf3f3;
      --ink: #132126;
      --ink-strong: #071216;
      --muted: #5b6a71;
      --line: #cddadc;
      --line-strong: #a9bdc1;
      --accent: #08796f;
      --accent-strong: #034f49;
      --accent-soft: #e4f5f2;
      --gold: #a8751e;
      --gold-soft: #fff3da;
      --warning: #9a5b08;
      --danger: #b42318;
      --danger-soft: #fff0ee;
      --shadow-soft: 0 22px 56px rgba(7, 18, 22, 0.14);
      --shadow-card: 0 12px 30px rgba(10, 28, 34, 0.085);
      --shadow-tight: 0 1px 0 rgba(255, 255, 255, 0.88) inset, 0 1px 2px rgba(10, 28, 34, 0.045);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI Variable", "Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei", sans-serif;
      background:
        linear-gradient(90deg, rgba(9, 28, 33, 0.024) 1px, transparent 1px),
        linear-gradient(180deg, rgba(9, 28, 33, 0.024) 1px, transparent 1px),
        linear-gradient(180deg, #fbfcfb 0, #f7faf9 260px, var(--bg) 620px);
      background-size: 40px 40px, 40px 40px, auto;
      color: var(--ink);
      font-size: 14px;
      letter-spacing: 0;
    }}
    main {{ width: 100%; max-width: 1500px; margin: 0 auto; padding: 20px 20px 38px; }}
    header {{
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(236, 245, 243, 0.14);
      border-radius: 8px;
      padding: 22px 24px;
      margin-bottom: 16px;
      background:
        linear-gradient(90deg, rgba(255, 255, 255, 0.105), transparent 38%),
        repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.036) 0 1px, transparent 1px 16px),
        linear-gradient(135deg, #071216 0, #10282e 58%, #075b55 150%);
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
    h1 {{ font-size: 1.54rem; line-height: 1.18; margin: 0 0 9px; font-weight: 780; }}
    h2 {{ display: flex; align-items: center; gap: 8px; font-size: 0.98rem; line-height: 1.3; margin: 0 0 12px; color: var(--ink-strong); }}
    h2::before {{ content: ""; width: 4px; height: 1.05em; border-radius: 99px; background: linear-gradient(180deg, var(--gold), var(--accent)); box-shadow: 0 0 0 3px rgba(8, 121, 111, 0.08); }}
    h3 {{ margin: 0 0 10px; font-size: 0.95rem; line-height: 1.35; color: var(--ink-strong); }}
    .meta-row {{ display: flex; flex-wrap: wrap; gap: 10px 18px; color: var(--muted); font-size: 0.92rem; }}
    header .meta-row {{ color: #cfe1e2; }}
    header code {{ color: #ffffff; }}
    .console-layout {{ display: grid; grid-template-columns: minmax(292px, 336px) minmax(0, 1fr); gap: 18px; align-items: start; }}
    .sidebar {{ position: sticky; top: 14px; display: grid; gap: 12px; align-self: start; }}
    .dashboard {{ min-width: 0; display: grid; gap: 15px; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(165px, 1fr)); gap: 12px; margin-bottom: 4px; }}
    .feedback-grid {{ display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.65fr); gap: 14px; align-items: start; }}
    .runtime-shell {{ display: grid; grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.9fr); gap: 14px; align-items: start; }}
    .runtime-main, .runtime-side {{ display: grid; gap: 14px; min-width: 0; }}
    .runtime-main > *, .runtime-side > * {{ min-width: 0; }}
    .details-grid {{ display: grid; gap: 14px; align-items: start; }}
    .feedback-summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; margin-bottom: 12px; }}
    .feedback-shell {{ display: grid; grid-template-columns: minmax(320px, 0.9fr) minmax(420px, 1.1fr); gap: 14px; align-items: start; }}
    .feedback-column {{ display: grid; gap: 12px; min-width: 0; }}
    .feedback-list, .feedback-links, .feedback-latest-runs {{ display: grid; gap: 8px; }}
    .feedback-run {{ border: 1px solid var(--line); border-radius: 8px; padding: 11px 12px; background: linear-gradient(180deg, #ffffff, #f8fbfb); box-shadow: var(--shadow-tight); }}
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
    th {{ background: linear-gradient(180deg, #f3f7f7, #e8f0ef); color: #34464d; font-size: 0.76rem; text-transform: uppercase; }}
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
    .panel {{ background: var(--surface-raised); border: 1px solid var(--line); border-top: 3px solid #c2d2d6; border-radius: 8px; padding: 15px; min-width: 0; box-shadow: var(--shadow-card); backdrop-filter: blur(6px); }}
    .sidebar .panel {{ background: linear-gradient(180deg, rgba(255, 255, 255, 0.985), rgba(248, 251, 250, 0.965)); }}
    .output-panel {{ border-top-color: var(--gold); }}
    .surface-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 10px; }}
    .surface-card {{ display: grid; grid-template-rows: auto minmax(86px, 1fr) auto; gap: 10px; align-content: start; background: linear-gradient(180deg, #ffffff, #f8fbfb); border: 1px solid var(--line); border-radius: 8px; padding: 12px; min-width: 0; box-shadow: var(--shadow-tight); }}
    .surface-card.active {{ border-color: #acd9d2; background: linear-gradient(180deg, #eff9f6, #ffffff); box-shadow: 0 0 0 1px rgba(8, 121, 111, 0.08), var(--shadow-tight); }}
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
    .action-group-title {{ margin: 0; color: #42565d; font-size: 0.76rem; font-weight: 760; text-transform: uppercase; }}
    .foldout {{ border-top: 1px solid var(--line); margin-top: 12px; padding-top: 10px; }}
    .foldout > summary {{ cursor: pointer; color: var(--ink-strong); font-weight: 760; line-height: 1.4; list-style-position: inside; }}
    .foldout[open] > summary {{ margin-bottom: 9px; }}
    .shortcut-list {{ display: grid; gap: 9px; margin-top: 10px; }}
    .shortcut-item {{ display: grid; gap: 8px; min-width: 0; padding: 11px; border: 1px solid var(--line); border-radius: 8px; background: linear-gradient(180deg, #ffffff, #f8fbfb); box-shadow: var(--shadow-tight); }}
    .shortcut-item.recommended {{ border-color: #acd9d2; background: linear-gradient(180deg, #eff9f6, #ffffff); box-shadow: 0 0 0 1px rgba(8, 121, 111, 0.08), var(--shadow-tight); }}
    .shortcut-head {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; min-width: 0; }}
    .shortcut-title {{ font-weight: 760; color: var(--ink-strong); line-height: 1.35; }}
    .shortcut-command {{ display: block; min-width: 0; width: 100%; padding: 7px 8px; border: 1px solid #dfe9ea; border-radius: 6px; background: #f7fbfa; color: #20333a; overflow-wrap: anywhere; white-space: normal; }}
    .shortcut-item .meta {{ margin: 0; }}
    .shortcut-blocked {{ color: var(--warning); font-weight: 650; }}
    .shortcut-item button {{ text-align: center; min-height: 34px; }}
    button, select, input {{ font: inherit; }}
    button {{ border: 1px solid var(--line); background: linear-gradient(180deg, #ffffff, #f8fbfb); color: var(--ink); border-radius: 7px; padding: 9px 11px; cursor: pointer; text-align: left; transition: border-color 140ms ease, box-shadow 140ms ease, background 140ms ease; }}
    button:hover {{ border-color: var(--accent); box-shadow: 0 7px 16px rgba(8, 121, 111, 0.10); }}
    button.primary {{ background: linear-gradient(135deg, var(--accent), var(--accent-strong)); border-color: var(--accent-strong); color: #fff; font-weight: 760; box-shadow: 0 8px 18px rgba(3, 79, 73, 0.16); }}
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
        linear-gradient(180deg, #101d23, #071015);
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
    .codex-account {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px; align-items: start; border: 1px solid var(--line); border-radius: 8px; padding: 13px; background: linear-gradient(180deg, #ffffff, #f8fbfb); box-shadow: var(--shadow-tight); }}
    .codex-account-body {{ min-width: 0; display: grid; gap: 3px; }}
    .codex-account-actions {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-start; justify-content: flex-end; }}
    .codex-account strong, .codex-account small {{ display: block; overflow-wrap: anywhere; }}
    .codex-badge {{ display: inline-flex; align-items: center; align-self: start; border: 1px solid #bde0da; border-radius: 999px; padding: 4px 10px; color: var(--accent-strong); background: var(--accent-soft); font-size: 0.78rem; font-weight: 760; white-space: nowrap; }}
    .codex-account-switch {{ display: inline-flex; align-items: center; justify-content: center; min-width: 68px; min-height: 34px; padding: 8px 14px; border-radius: 7px; text-align: center; font-weight: 700; }}
    .codex-account-switch.is-current {{ border-color: #bde0da; color: var(--accent-strong); background: var(--accent-soft); }}
    .codex-account-switch.danger {{ border-color: #f0b8b8; color: #9f2020; background: #fff5f5; }}
    .codex-account-switch[disabled] {{ opacity: 1; cursor: default; box-shadow: none; transform: none; }}
    .claude-toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 12px; }}
    .claude-console-grid {{ display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(290px, 0.65fr); gap: 12px; align-items: start; }}
    .claude-summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }}
    .claude-summary-card {{ background: linear-gradient(180deg, #ffffff, #f8fbfb); border: 1px solid var(--line); border-radius: 8px; padding: 12px; min-width: 0; box-shadow: var(--shadow-tight); }}
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
      .dashboard {{ gap: 12px; }}
      .view-tabs {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); width: 100%; }}
      .view-tab {{ text-align: center; padding: 8px 7px; }}
      .feedback-preview {{ height: 300px; }}
      .info-list {{ grid-template-columns: 1fr; }}
      .sidebar {{ position: static; }}
      .output {{ min-height: 220px; }}
      .codex-account-actions {{ justify-content: flex-start; }}
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
  </style>"""
