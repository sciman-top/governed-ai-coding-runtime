"""Interactive JavaScript renderer for the runtime operator surface."""

from __future__ import annotations

def render_interactive_script(
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
  const nextWorkCacheKey = 'governed-runtime-operator-next-work';
  const surfaceOpenLabel = {text['open_surface']!r};
  const surfaceCurrentLabel = {text['surface_current']!r};
  const runtimeSurfaceSummaryTemplate = {text['surface_runtime_summary']!r};
  const runtimeSurfaceDetailTemplate = {text['surface_runtime_detail']!r};
  const runtimeSurfaceActionText = {text['surface_runtime_action']!r};
  const continuitySurfaceActionText = {text['surface_continuity_action']!r};
  const feedbackSurfaceActionText = {text['surface_feedback_action']!r};
  const managedRemovalActions = new Set(['cleanup_targets', 'uninstall_governance']);
  const defaultManagedRemovalActions = new Set(['apply_all_features']);
  let feedbackLoaded = false;
  let continuityLoaded = false;
  let nextWorkLoaded = false;
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
    const target = kind === 'feedback' ? feedbackCacheState : (kind === 'next-work' ? nextWorkCacheState : null);
    if (!target) {{
      return;
    }}
    const label = kind === 'feedback'
        ? {text['feedback_status']!r}
        : (currentUiLanguage() === 'zh-CN' ? 'next-work 状态' : 'next-work state');
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

  function hydratePanelCache(kind, key) {{
    const cached = readPanelCache(key);
    if (!cached) {{
      setPanelCacheState(kind, 'cold');
      return false;
    }}
    if (kind === 'feedback') {{
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
    const seen = new Set();
    const items = Array.isArray(lines)
      ? lines
          .map((item) => String(item || '').trim())
          .filter(Boolean)
          .filter((item) => {{
            if (seen.has(item)) {{
              return false;
            }}
            seen.add(item);
            return true;
          }})
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

  function updateFeedbackSurfaceSummary(payload) {{
    const summary = payload && payload.summary ? payload.summary : {{}};
    const firstRecommendation = payload && Array.isArray(payload.recommendations) && payload.recommendations.length
      ? String(payload.recommendations[0] || '').trim()
      : '';
    setSurfaceSummary('feedback', [
      currentUiLanguage() === 'zh-CN'
        ? `总状态 ${{formatFeedbackStatusLabel(payload && payload.status)}}`
        : `Overall ${{formatFeedbackStatusLabel(payload && payload.status)}}`,
      feedbackSurfaceActionText,
      firstRecommendation || feedbackSurfaceActionText,
    ]);
  }}

  function updateContinuitySurfaceSummary(payload) {{
    const count = payload && Number.isFinite(Number(payload.record_count)) ? Number(payload.record_count) : 0;
    setSurfaceSummary('continuity', [
      currentUiLanguage() === 'zh-CN' ? `记录 ${{count}}` : `Records ${{count}}`,
      currentUiLanguage() === 'zh-CN' ? '默认过滤 secret-blocked 项' : 'Secret-blocked records are filtered by default',
      continuitySurfaceActionText,
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
    if (selected === 'feedback' && !feedbackLoaded) {{
      hydratePanelCache('feedback', feedbackCacheKey);
    }}
    if (selected === 'continuity' && !continuityLoaded) {{
      refreshContinuityRecords();
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

  function currentUiLanguage() {{
    const lang = document.documentElement.lang || '';
    return lang.toLowerCase().startsWith('zh') ? 'zh-CN' : 'en-US';
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
    ].forEach((card) => {{
      const section = document.createElement('section');
      section.className = 'summary-card';
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

  function renderContinuitySummary(payload) {{
    if (!continuityRecords || !continuityJson || !continuityStatus) {{
      return;
    }}
    const records = Array.isArray(payload && payload.records) ? payload.records : [];
    continuityStatus.textContent = `{text['continuity_status']}: ${{payload && payload.status ? payload.status : 'unknown'}} · ${{records.length}}`;
    continuityRecords.innerHTML = '';
    records.forEach((record) => {{
      const section = document.createElement('section');
      section.className = 'summary-card';
      section.appendChild(createInfoLine(record.record_id || 'record', record.task_summary || ''));
      section.appendChild(createInfoLine({text['repo']!r}, record.repo_id || {text['not_recorded']!r}));
      section.appendChild(createInfoLine({text['adapter']!r}, `${{record.tool_family || ''}} · ${{record.provider_alias || ''}}`));
      section.appendChild(createInfoLine({text['continuity_class']!r}, record.continuity_class || {text['not_recorded']!r}));
      continuityRecords.appendChild(section);
    }});
    if (!records.length) {{
      continuityRecords.innerHTML = `<p class="meta">{text['continuity_empty']}</p>`;
    }}
    continuityJson.textContent = JSON.stringify(payload || {{}}, null, 2);
    updateContinuitySurfaceSummary(payload || {{}});
  }}

  async function refreshContinuityRecords() {{
    if (!continuityRecords) {{
      return;
    }}
    continuityStatus.textContent = `{text['continuity_status']}: {text['running']}`;
    try {{
      const response = await fetch('/api/continuity/search', {{ cache: 'no-store' }});
      const payload = await response.json();
      if (!response.ok) {{
        continuityStatus.textContent = `{text['continuity_status']}: ${{payload.error || response.statusText}}`;
        return;
      }}
      renderContinuitySummary(payload);
      continuityLoaded = true;
    }} catch (error) {{
      continuityStatus.textContent = `{text['continuity_status']}: ${{String(error)}}`;
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
      event.preventDefault();
    }});
  }}
    }});
  }}
      }}
    }});
  }}
  }});
  document.querySelector('[data-feedback-refresh]').addEventListener('click', () => refreshFeedbackSummaryWithMode(true));
  const continuityRefreshButton = document.querySelector('[data-continuity-refresh]');
  if (continuityRefreshButton) {{
    continuityRefreshButton.addEventListener('click', () => refreshContinuityRecords());
  }}
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
  hydratePanelCache('feedback', feedbackCacheKey);
  hydratePanelCache('next-work', nextWorkCacheKey);
  activateView('runtime');
  // Page load stays side-effect-light; process-backed probes run only after an explicit action.
}})();
</script>"""
