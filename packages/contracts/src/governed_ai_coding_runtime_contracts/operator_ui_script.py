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
      if (!account.active) {{
        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'codex-account-switch danger';
        deleteButton.textContent = {text['codex_delete']!r};
        deleteButton.dataset.codexDeleteName = account.name || account.file || '';
        deleteButton.dataset.confirm = {text['codex_delete_confirm']!r};
        actions.appendChild(deleteButton);
      }}
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

  async function deleteCodexAccount(name, confirmMessage) {{
    if (!name) {{
      return;
    }}
    if (confirmMessage && !window.confirm(confirmMessage)) {{
      return;
    }}
    setBusy(true);
    try {{
      const response = await fetch('/api/codex/delete', {{
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
      if (!provider.active) {{
        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'codex-account-switch danger';
        deleteButton.textContent = {text['claude_delete']!r};
        deleteButton.dataset.claudeDeleteName = provider.name || '';
        deleteButton.dataset.confirm = {text['claude_delete_confirm']!r};
        actions.appendChild(deleteButton);
      }}
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

  async function deleteClaudeProvider(name, confirmMessage) {{
    const targetName = String(name || '').trim();
    if (!targetName) {{
      return;
    }}
    if (confirmMessage && !window.confirm(confirmMessage)) {{
      return;
    }}
    setBusy(true);
    try {{
      const response = await fetch('/api/claude/delete', {{
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
    const deleteButton = event.target.closest('button[data-codex-delete-name]');
    if (deleteButton) {{
      deleteCodexAccount(
        deleteButton.getAttribute('data-codex-delete-name') || '',
        deleteButton.getAttribute('data-confirm') || ''
      );
      return;
    }}
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
    const deleteButton = event.target.closest('button[data-claude-delete-name]');
    if (deleteButton) {{
      deleteClaudeProvider(
        deleteButton.getAttribute('data-claude-delete-name') || '',
        deleteButton.getAttribute('data-confirm') || ''
      );
      return;
    }}
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

