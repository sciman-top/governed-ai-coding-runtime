"""Interactive JavaScript renderer for the runtime operator surface."""

from __future__ import annotations


def render_interactive_script(
    text: dict[str, str],
    *,
    language: str,
    total_tasks: int,
    approval_count: int,
    verification_count: int,
) -> str:
    return f"""
<script>
(() => {{
  const output = document.getElementById('ui-output');
  const status = document.getElementById('ui-status');
  const languageSelect = document.getElementById('ui-language');
  const mode = document.getElementById('ui-mode');
  const parallelism = document.getElementById('ui-parallelism');
  const milestone = document.getElementById('ui-milestone');
  const failFast = document.getElementById('ui-fail-fast');
  const dryRun = document.getElementById('ui-dry-run');
  const historyList = document.getElementById('ui-history');
  const feedbackStatus = document.getElementById('feedback-status');
  const feedbackCacheState = document.getElementById('feedback-cache-state');
  const feedbackGeneratedAt = document.getElementById('feedback-generated-at');
  const feedbackSummary = document.getElementById('feedback-summary');
  const feedbackDimensions = document.getElementById('feedback-dimensions');
  const feedbackRecommendations = document.getElementById('feedback-recommendations');
  const feedbackReportLink = document.getElementById('feedback-report-link');
  const feedbackGuideLink = document.getElementById('feedback-guide-link');
  const feedbackGuideLinkEn = document.getElementById('feedback-guide-link-en');
  const feedbackPreview = document.getElementById('feedback-preview');
  const selfEvolutionStatus = document.getElementById('self-evolution-status');
  const selfEvolutionCacheState = document.getElementById('self-evolution-cache-state');
  const selfEvolutionGeneratedAt = document.getElementById('self-evolution-generated-at');
  const selfEvolutionSummary = document.getElementById('self-evolution-summary');
  const selfEvolutionLanes = document.getElementById('self-evolution-lanes');
  const selfEvolutionReportLink = document.getElementById('self-evolution-report-link');
  const selfEvolutionJson = document.getElementById('self-evolution-json');
  const selfEvolutionPromotionStatus = document.getElementById('self-evolution-promotion-status');
  const selfEvolutionPromotionCacheState = document.getElementById('self-evolution-promotion-cache-state');
  const selfEvolutionPromotionGeneratedAt = document.getElementById('self-evolution-promotion-generated-at');
  const selfEvolutionPromotionSummary = document.getElementById('self-evolution-promotion-summary');
  const selfEvolutionPromotionLanes = document.getElementById('self-evolution-promotion-lanes');
  const selfEvolutionPromotionReportLink = document.getElementById('self-evolution-promotion-report-link');
  const selfEvolutionPromotionJson = document.getElementById('self-evolution-promotion-json');
  const continuityStatus = document.getElementById('continuity-status');
  const continuityRecords = document.getElementById('continuity-records');
  const continuityJson = document.getElementById('continuity-json');
  const nextWorkAction = document.getElementById('next-work-action');
  const nextWorkRecommendation = document.getElementById('next-work-recommendation');
  const nextWorkState = document.getElementById('next-work-state');
  const nextWorkWhy = document.getElementById('next-work-why');
  const nextWorkJson = document.getElementById('next-work-json');
  const nextWorkCacheState = document.getElementById('next-work-cache-state');
  const historyKey = 'governed-runtime-operator-history';
  const feedbackCacheKey = 'governed-runtime-operator-feedback-summary';
  const selfEvolutionCacheKey = 'governed-runtime-operator-self-evolution-recommendations';
  const selfEvolutionPromotionCacheKey = 'governed-runtime-operator-self-evolution-promotion';
  const nextWorkCacheKey = 'governed-runtime-operator-next-work';
  let lastNextWorkPayload = null;

  function currentUiLanguage() {{
    const lang = document.documentElement.lang || '';
    return lang.toLowerCase().startsWith('zh') ? 'zh-CN' : 'en-US';
  }}

  function readHistory() {{
    try {{
      const value = JSON.parse(window.localStorage.getItem(historyKey) || '[]');
      return Array.isArray(value) ? value : [];
    }} catch (_error) {{
      return [];
    }}
  }}

  function writeHistory(items) {{
    window.localStorage.setItem(historyKey, JSON.stringify(items.slice(0, 12)));
  }}

  function renderHistory() {{
    const items = readHistory();
    if (!historyList) {{
      return;
    }}
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
      detail.textContent = `${{item.elapsed_seconds}}s · ${{item.at}}`;
      button.append(title, detail);
      historyList.appendChild(button);
    }});
  }}

  function setBusy(isBusy) {{
    if (status) {{
      status.textContent = isBusy ? {text['running']!r} : {text['ready']!r};
    }}
    document.querySelectorAll('button[data-action]').forEach((button) => {{
      const action = button.getAttribute('data-action') || '';
      const blocked = lastNextWorkPayload && Array.isArray(lastNextWorkPayload.blocked_actions)
        ? lastNextWorkPayload.blocked_actions.includes(action)
        : false;
      button.disabled = isBusy || blocked;
    }});
  }}

  function setOutput(value) {{
    if (output) {{
      output.textContent = value || '';
    }}
  }}

  function setFeedbackPreview(value) {{
    if (feedbackPreview) {{
      feedbackPreview.textContent = value || '';
    }}
  }}

  function setPanelCacheState(target, label, state) {{
    if (!target) {{
      return;
    }}
    target.textContent = `${{label}}: ${{state}}`;
  }}

  function createInfoLine(label, value) {{
    const line = document.createElement('div');
    line.className = 'info-line';
    const labelEl = document.createElement('span');
    labelEl.className = 'info-label';
    labelEl.textContent = label;
    const valueEl = document.createElement('span');
    valueEl.className = 'info-value';
    valueEl.textContent = String(value || '');
    line.append(labelEl, valueEl);
    return line;
  }}

  function createRefButton(path, label, previewTarget) {{
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'ref-button';
    button.textContent = label;
    button.addEventListener('click', () => viewRef(path, previewTarget));
    return button;
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
        badge.textContent = isSelected ? {text['surface_current']!r} : {text['open_surface']!r};
      }}
      const button = card.querySelector('button[data-open-view]');
      if (button) {{
        button.disabled = isSelected;
        button.textContent = isSelected ? {text['surface_current']!r} : {text['open_surface']!r};
      }}
    }});
  }}

  function updateRuntimeSurfaceSummary() {{
    const target = document.querySelector('[data-surface-summary="runtime"]');
    if (!target) {{
      return;
    }}
    target.innerHTML = [
      {text['surface_runtime_summary']!r}
        .replace('{{tasks}}', String({total_tasks}))
        .replace('{{approvals}}', String({approval_count}))
        .replace('{{verification}}', String({verification_count})),
      {text['surface_runtime_detail']!r},
      {text['surface_runtime_action']!r},
    ].map((line) => `<p>${{line}}</p>`).join('');
  }}

  function updateSurfaceSummary(surface, lines) {{
    const target = document.querySelector(`[data-surface-summary="${{surface}}"]`);
    if (!target) {{
      return;
    }}
    target.innerHTML = (Array.isArray(lines) ? lines : []).filter(Boolean).map((line) => `<p>${{line}}</p>`).join('');
  }}

  function actionDisplayLabel(action) {{
    const labels = {{
      fast_feedback: {text['fast_feedback_action']!r},
      readiness: {text['readiness_action']!r},
      feedback_report: {text['feedback_report_action']!r},
      codex_guard_absence_check: {text['codex_guard_absence_action']!r},
      rules_dry_run: {text['rules_dry_run_action']!r},
      rules_apply: {text['rules_apply_action']!r},
      self_evolution_recommend: {text['self_evolution_recommend_action']!r},
      self_evolution_promotion_plan: {text['self_evolution_promotion_action']!r},
      evolution_review: {text['evolution_review_action']!r},
      experience_review: {text['experience_review_action']!r},
      evolution_materialize: {text['evolution_materialize_action']!r},
      core_principle_materialize: {text['core_principle_action']!r},
    }};
    return labels[action] || action || 'unknown';
  }}

  function syncNextWorkActionGuards() {{
    const blocked = new Set(Array.isArray(lastNextWorkPayload && lastNextWorkPayload.blocked_actions) ? lastNextWorkPayload.blocked_actions : []);
    const reason = String(lastNextWorkPayload && lastNextWorkPayload.why || '').trim();
    document.querySelectorAll('button[data-action]').forEach((button) => {{
      const action = button.getAttribute('data-action') || '';
      const note = document.querySelector(`[data-action-blocked="${{action}}"]`);
      const isBlocked = blocked.has(action);
      button.disabled = document.body.dataset.busy === '1' || isBlocked;
      if (note) {{
        note.textContent = isBlocked ? reason : '';
      }}
    }});
  }}

  function renderFeedbackSummary(payload) {{
    if (!feedbackStatus || !feedbackSummary || !feedbackDimensions || !feedbackRecommendations) {{
      return;
    }}
    feedbackStatus.textContent = `{text['feedback_status']}: ${{payload.status || 'unknown'}}`;
    if (feedbackGeneratedAt) {{
      feedbackGeneratedAt.textContent = `{text['feedback_generated_at']}: ${{payload.generated_at || {text['not_recorded']!r}}}`;
    }}
    feedbackSummary.innerHTML = '';
    feedbackSummary.appendChild(createInfoLine({text['feedback_status']!r}, payload.status || 'unknown'));
    feedbackSummary.appendChild(createInfoLine({text['feedback_summary_caption']!r}, `ok=${{payload.summary && payload.summary.dimensions_ok || 0}} attention=${{payload.summary && payload.summary.dimensions_attention || 0}} fail=${{payload.summary && payload.summary.dimensions_fail || 0}}`));
    feedbackDimensions.innerHTML = '';
    (payload.dimensions || []).forEach((item) => {{
      const pill = document.createElement('span');
      pill.className = `status-pill ${{String(item.status || '').toLowerCase()}}`;
      pill.textContent = `${{item.dimension_id}}: ${{item.status}}`;
      feedbackDimensions.appendChild(pill);
    }});
    feedbackRecommendations.innerHTML = '';
    if (Array.isArray(payload.recommendations) && payload.recommendations.length) {{
      const list = document.createElement('ul');
      payload.recommendations.forEach((item) => {{
        const li = document.createElement('li');
        li.textContent = String(item);
        list.appendChild(li);
      }});
      feedbackRecommendations.appendChild(list);
    }} else {{
      feedbackRecommendations.innerHTML = `<p class="meta">{text['feedback_empty']}</p>`;
    }}
    if (feedbackReportLink) {{
      feedbackReportLink.innerHTML = '';
      if (payload.report_path) {{
        feedbackReportLink.appendChild(createRefButton(payload.report_path, {text['feedback_open_report']!r}, 'feedback'));
      }} else {{
        feedbackReportLink.innerHTML = `<p class="meta">{text['feedback_report_missing']}</p>`;
      }}
    }}
    if (feedbackGuideLink) {{
      feedbackGuideLink.innerHTML = '';
      if (payload.guide_path) {{
        feedbackGuideLink.appendChild(createRefButton(payload.guide_path, {text['feedback_open_guide']!r}, 'feedback'));
      }}
    }}
    if (feedbackGuideLinkEn) {{
      feedbackGuideLinkEn.innerHTML = '';
      if ((document.documentElement.lang || '').toLowerCase().startsWith('en') && payload.guide_path_en) {{
        feedbackGuideLinkEn.appendChild(createRefButton(payload.guide_path_en, {text['feedback_open_guide_en']!r}, 'feedback'));
      }}
    }}
    updateSurfaceSummary('feedback', [
      (currentUiLanguage() === 'zh-CN' ? '总状态 ' : 'Overall ') + String(payload.status || 'unknown'),
      {text['surface_feedback_action']!r},
      Array.isArray(payload.recommendations) && payload.recommendations.length ? String(payload.recommendations[0]) : {text['surface_feedback_action']!r},
    ]);
    window.localStorage.setItem(feedbackCacheKey, JSON.stringify(payload));
    setPanelCacheState(feedbackCacheState, {text['feedback_status']!r}, {text['panel_cache_ready']!r});
  }}

  function renderSelfEvolutionRecommendations(payload) {{
    if (!selfEvolutionStatus || !selfEvolutionSummary || !selfEvolutionLanes || !selfEvolutionJson) {{
      return;
    }}
    selfEvolutionStatus.textContent = `{text['self_evolution_status']}: ${{payload.report_status || payload.status || 'unknown'}}`;
    if (selfEvolutionGeneratedAt) {{
      selfEvolutionGeneratedAt.textContent = `{text['self_evolution_generated_at']}: ${{payload.as_of || {text['not_recorded']!r}}}`;
    }}
    selfEvolutionSummary.innerHTML = '';
    selfEvolutionSummary.appendChild(createInfoLine({text['self_evolution_next_action']!r}, payload.recommended_next_action || 'unknown'));
    selfEvolutionSummary.appendChild(createInfoLine({text['self_evolution_selector']!r}, payload.selector_next_action || 'unknown'));
    selfEvolutionSummary.appendChild(createInfoLine({text['self_evolution_readiness']!r}, payload.readiness_overall_state || 'unknown'));
    selfEvolutionLanes.innerHTML = '';
    (payload.recommendations || []).forEach((item) => {{
      const section = document.createElement('section');
      section.className = 'summary-card';
      section.appendChild(createInfoLine(item.lane || 'lane', item.decision || 'unknown'));
      const meta = document.createElement('p');
      meta.className = 'meta';
      meta.textContent = item.title || item.reason || '';
      section.appendChild(meta);
      selfEvolutionLanes.appendChild(section);
    }});
    if (selfEvolutionReportLink) {{
      selfEvolutionReportLink.innerHTML = '';
      if (payload.report_path) {{
        selfEvolutionReportLink.appendChild(createRefButton(payload.report_path, {text['self_evolution_open_report']!r}, 'feedback'));
      }}
    }}
    selfEvolutionJson.textContent = JSON.stringify(payload || {{}}, null, 2);
    window.localStorage.setItem(selfEvolutionCacheKey, JSON.stringify(payload));
    setPanelCacheState(selfEvolutionCacheState, {text['self_evolution_status']!r}, {text['panel_cache_ready']!r});
  }}

  function renderSelfEvolutionPromotion(payload) {{
    if (!selfEvolutionPromotionStatus || !selfEvolutionPromotionSummary || !selfEvolutionPromotionLanes || !selfEvolutionPromotionJson) {{
      return;
    }}
    selfEvolutionPromotionStatus.textContent = `{text['self_evolution_promotion_status']}: ${{payload.report_status || payload.status || 'unknown'}}`;
    if (selfEvolutionPromotionGeneratedAt) {{
      selfEvolutionPromotionGeneratedAt.textContent = `{text['self_evolution_generated_at']}: ${{payload.as_of || {text['not_recorded']!r}}}`;
    }}
    selfEvolutionPromotionSummary.innerHTML = '';
    selfEvolutionPromotionSummary.appendChild(createInfoLine({text['self_evolution_promotion_stage']!r}, payload.promotion_stage || 'unknown'));
    selfEvolutionPromotionSummary.appendChild(createInfoLine({text['self_evolution_next_action']!r}, payload.recommended_next_action || 'unknown'));
    selfEvolutionPromotionSummary.appendChild(createInfoLine({text['self_evolution_selector']!r}, payload.selector_next_action || 'unknown'));
    selfEvolutionPromotionLanes.innerHTML = '';
    (payload.control_lanes || []).forEach((item) => {{
      const section = document.createElement('section');
      section.className = 'summary-card';
      section.appendChild(createInfoLine(item.lane || 'lane', item.status || 'unknown'));
      const meta = document.createElement('p');
      meta.className = 'meta';
      meta.textContent = item.reason || '';
      section.appendChild(meta);
      selfEvolutionPromotionLanes.appendChild(section);
    }});
    if (selfEvolutionPromotionReportLink) {{
      selfEvolutionPromotionReportLink.innerHTML = '';
      if (payload.report_path) {{
        selfEvolutionPromotionReportLink.appendChild(createRefButton(payload.report_path, {text['self_evolution_promotion_open_report']!r}, 'feedback'));
      }}
    }}
    selfEvolutionPromotionJson.textContent = JSON.stringify(payload || {{}}, null, 2);
    window.localStorage.setItem(selfEvolutionPromotionCacheKey, JSON.stringify(payload));
    setPanelCacheState(selfEvolutionPromotionCacheState, {text['self_evolution_promotion_status']!r}, {text['panel_cache_ready']!r});
  }}

  function renderContinuitySummary(payload) {{
    if (!continuityStatus || !continuityRecords || !continuityJson) {{
      return;
    }}
    const records = Array.isArray(payload.records) ? payload.records : [];
    continuityStatus.textContent = `{text['continuity_status']}: ${{payload.status || 'unknown'}} · ${{records.length}}`;
    continuityRecords.innerHTML = '';
    if (!records.length) {{
      continuityRecords.innerHTML = `<p class="meta">{text['continuity_empty']}</p>`;
    }} else {{
      records.forEach((record) => {{
        const section = document.createElement('section');
        section.className = 'summary-card';
        section.appendChild(createInfoLine(record.record_id || 'record', record.task_summary || ''));
        section.appendChild(createInfoLine({text['repo']!r}, record.repo_id || {text['not_recorded']!r}));
        section.appendChild(createInfoLine({text['continuity_class']!r}, record.continuity_class || {text['not_recorded']!r}));
        continuityRecords.appendChild(section);
      }});
    }}
    continuityJson.textContent = JSON.stringify(payload || {{}}, null, 2);
    updateSurfaceSummary('continuity', [
      (currentUiLanguage() === 'zh-CN' ? '记录 ' : 'Records ') + String(records.length),
      {text['surface_continuity_action']!r},
      currentUiLanguage() === 'zh-CN' ? '默认过滤 secret-blocked 项' : 'Secret-blocked records are filtered by default',
    ]);
  }}

  function renderNextWorkSummary(payload) {{
    lastNextWorkPayload = payload || {{}};
    if (nextWorkAction) {{
      nextWorkAction.textContent = String(payload.safe_next_action || payload.next_action || 'unknown');
    }}
    if (nextWorkRecommendation) {{
      nextWorkRecommendation.textContent = (currentUiLanguage() === 'zh-CN' ? 'AI 推荐: ' : 'AI recommended: ') + String(payload.safe_next_action || payload.next_action || 'unknown');
    }}
    if (nextWorkState) {{
      nextWorkState.textContent = (currentUiLanguage() === 'zh-CN' ? '状态: ' : 'Status: ') + String(payload.ui_status || 'unknown');
    }}
    if (nextWorkWhy) {{
      nextWorkWhy.textContent = String(payload.why || '');
    }}
    if (nextWorkJson) {{
      nextWorkJson.textContent = JSON.stringify(payload || {{}}, null, 2);
    }}
    window.localStorage.setItem(nextWorkCacheKey, JSON.stringify(payload));
    setPanelCacheState(nextWorkCacheState, 'next-work', {text['panel_cache_ready']!r});
    syncNextWorkActionGuards();
  }}

  async function refreshJson(url, renderer, cacheStateEl, cacheLabel) {{
    setPanelCacheState(cacheStateEl, cacheLabel, {text['panel_cache_refreshing']!r});
    const response = await fetch(url, {{ cache: 'no-store' }});
    const payload = await response.json();
    if (!response.ok) {{
      throw new Error(payload.error || response.statusText);
    }}
    renderer(payload);
    return payload;
  }}

  async function refreshFeedbackSummary(forceRefresh) {{
    try {{
      await refreshJson(forceRefresh ? '/api/feedback/summary?refresh=1' : '/api/feedback/summary', renderFeedbackSummary, feedbackCacheState, {text['feedback_status']!r});
    }} catch (error) {{
      if (feedbackStatus) {{
        feedbackStatus.textContent = `{text['feedback_status']}: ${{String(error)}}`;
      }}
      setPanelCacheState(feedbackCacheState, {text['feedback_status']!r}, {text['panel_cache_error']!r});
    }}
  }}

  async function refreshSelfEvolutionRecommendations(forceRefresh) {{
    try {{
      await refreshJson(forceRefresh ? '/api/self-evolution/recommendations?refresh=1' : '/api/self-evolution/recommendations', renderSelfEvolutionRecommendations, selfEvolutionCacheState, {text['self_evolution_status']!r});
    }} catch (error) {{
      if (selfEvolutionStatus) {{
        selfEvolutionStatus.textContent = `{text['self_evolution_status']}: ${{String(error)}}`;
      }}
      setPanelCacheState(selfEvolutionCacheState, {text['self_evolution_status']!r}, {text['panel_cache_error']!r});
    }}
  }}

  async function refreshSelfEvolutionPromotion(forceRefresh) {{
    try {{
      await refreshJson(forceRefresh ? '/api/self-evolution/promotion?refresh=1' : '/api/self-evolution/promotion', renderSelfEvolutionPromotion, selfEvolutionPromotionCacheState, {text['self_evolution_promotion_status']!r});
    }} catch (error) {{
      if (selfEvolutionPromotionStatus) {{
        selfEvolutionPromotionStatus.textContent = `{text['self_evolution_promotion_status']}: ${{String(error)}}`;
      }}
      setPanelCacheState(selfEvolutionPromotionCacheState, {text['self_evolution_promotion_status']!r}, {text['panel_cache_error']!r});
    }}
  }}

  async function refreshContinuityRecords() {{
    try {{
      await refreshJson('/api/continuity/search', renderContinuitySummary, null, '');
    }} catch (error) {{
      if (continuityStatus) {{
        continuityStatus.textContent = `{text['continuity_status']}: ${{String(error)}}`;
      }}
    }}
  }}

  async function refreshNextWorkSummary(forceRefresh) {{
    try {{
      await refreshJson(forceRefresh ? '/api/next-work?refresh=1' : '/api/next-work', renderNextWorkSummary, nextWorkCacheState, 'next-work');
    }} catch (error) {{
      if (nextWorkCacheState) {{
        nextWorkCacheState.textContent = String(error);
      }}
    }}
  }}

  async function runAction(action, button) {{
    const blocked = lastNextWorkPayload && Array.isArray(lastNextWorkPayload.blocked_actions)
      ? lastNextWorkPayload.blocked_actions.includes(action)
      : false;
    if (blocked) {{
      setOutput(String(lastNextWorkPayload.why || 'blocked by next-work'));
      return;
    }}
    const confirmMessage = button && button.getAttribute('data-confirm');
    if (confirmMessage && !window.confirm(confirmMessage)) {{
      return;
    }}
    document.body.dataset.busy = '1';
    setBusy(true);
    setOutput('');
    try {{
      const response = await fetch('/api/run', {{
        method: 'POST',
        headers: {{ 'content-type': 'application/json' }},
        body: JSON.stringify({{
          action,
          language: languageSelect ? languageSelect.value : {language!r},
          mode: mode ? mode.value : 'quick',
          target_parallelism: parallelism ? Number(parallelism.value || 1) : 1,
          milestone_tag: milestone ? milestone.value || 'milestone' : 'milestone',
          fail_fast: !!(failFast && failFast.checked),
          dry_run: !!(dryRun && dryRun.checked),
        }}),
      }});
      const payload = await response.json();
      const rendered = [
        `action: ${{payload.action || action}}`,
        `exit_code: ${{payload.exit_code}}`,
        `elapsed_seconds: ${{payload.elapsed_seconds}}`,
        '',
        payload.output || '',
      ].join('\\n');
      setOutput(rendered);
      writeHistory([{{
        action: payload.action || action,
        exit_code: payload.exit_code,
        elapsed_seconds: payload.elapsed_seconds,
        at: new Date().toLocaleString(),
        output: rendered,
      }}, ...readHistory()]);
      renderHistory();
      await refreshNextWorkSummary(true);
      await refreshSelfEvolutionRecommendations(true);
      await refreshSelfEvolutionPromotion(true);
    }} catch (error) {{
      setOutput(String(error));
    }} finally {{
      delete document.body.dataset.busy;
      setBusy(false);
    }}
  }}

  async function viewRef(path, previewTarget) {{
    try {{
      const response = await fetch('/api/file?path=' + encodeURIComponent(path));
      const payload = await response.json();
      if (!response.ok) {{
        throw new Error(payload.error || response.statusText);
      }}
      const rendered = `path: ${{payload.path}}\\n\\n${{payload.content}}`;
      if (previewTarget === 'feedback') {{
        setFeedbackPreview(rendered);
      }} else {{
        setOutput(rendered);
      }}
    }} catch (error) {{
      if (previewTarget === 'feedback') {{
        setFeedbackPreview(String(error));
      }} else {{
        setOutput(String(error));
      }}
    }}
  }}

  document.querySelectorAll('button[data-action]').forEach((button) => {{
    button.addEventListener('click', () => runAction(button.getAttribute('data-action') || '', button));
  }});
  document.querySelectorAll('button[data-open-view]').forEach((button) => {{
    button.addEventListener('click', () => activateView(button.getAttribute('data-open-view') || 'runtime'));
  }});
  document.querySelectorAll('[data-view-tab]').forEach((button) => {{
    button.addEventListener('click', () => activateView(button.getAttribute('data-view-tab') || 'runtime'));
  }});
  const clearHistoryButton = document.querySelector('[data-clear-history]');
  if (clearHistoryButton) {{
    clearHistoryButton.addEventListener('click', () => {{
      writeHistory([]);
      renderHistory();
    }});
  }}
  const refreshButton = document.querySelector('[data-refresh]');
  if (refreshButton) {{
    refreshButton.addEventListener('click', () => window.location.reload());
  }}
  const feedbackRefreshButton = document.querySelector('[data-feedback-refresh]');
  if (feedbackRefreshButton) {{
    feedbackRefreshButton.addEventListener('click', () => refreshFeedbackSummary(true));
  }}
  const selfEvolutionRefreshButton = document.querySelector('[data-self-evolution-refresh]');
  if (selfEvolutionRefreshButton) {{
    selfEvolutionRefreshButton.addEventListener('click', () => refreshSelfEvolutionRecommendations(true));
  }}
  const selfEvolutionPromotionRefreshButton = document.querySelector('[data-self-evolution-promotion-refresh]');
  if (selfEvolutionPromotionRefreshButton) {{
    selfEvolutionPromotionRefreshButton.addEventListener('click', () => refreshSelfEvolutionPromotion(true));
  }}
  const continuityRefreshButton = document.querySelector('[data-continuity-refresh]');
  if (continuityRefreshButton) {{
    continuityRefreshButton.addEventListener('click', () => refreshContinuityRecords());
  }}
  const nextWorkRefreshButton = document.querySelector('[data-next-work-refresh]');
  if (nextWorkRefreshButton) {{
    nextWorkRefreshButton.addEventListener('click', () => refreshNextWorkSummary(true));
  }}
  if (languageSelect) {{
    languageSelect.addEventListener('change', () => {{
      const next = new URL(window.location.href);
      next.searchParams.set('lang', languageSelect.value);
      window.location.href = next.toString();
    }});
  }}
  if (historyList) {{
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
  }}

  renderHistory();
  updateRuntimeSurfaceSummary();
  updateSurfaceSummary('continuity', [
    {text['surface_continuity_action']!r},
  ]);
  updateSurfaceSummary('feedback', [
    {text['surface_feedback_action']!r},
  ]);
  activateView('runtime');
  refreshFeedbackSummary(false);
  refreshSelfEvolutionRecommendations(false);
  refreshSelfEvolutionPromotion(false);
  refreshNextWorkSummary(false);
}})();
</script>"""
