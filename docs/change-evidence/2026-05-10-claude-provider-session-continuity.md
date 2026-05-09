# Claude Provider Session Continuity

- date: 2026-05-10
- rule_ids: R1, R2, R6, R8, E4
- risk: low
- current_landing: `scripts/lib/claude_local.py`, `scripts/claude-provider.py`, `scripts/claude-provider.ps1`, `tests/runtime/test_claude_local.py`
- target_home: `D:\CODE\governed-ai-coding-runtime` Claude local provider control surface
- rollback: revert this change with git; no user credential or live provider profile was modified

## Source Evidence

- Claude Code official session docs: sessions are saved locally and resumed with `claude --continue`, `claude --resume`, and `/resume`.
- Claude Code official architecture docs: session transcript files live under `~/.claude/projects/`, and each new session starts fresh unless resumed.
- Claude Agent SDK session storage docs: external stores mirror session entries, but Claude Code still writes local transcripts first.
- CCS / CC Switch community project docs: provider switchers manage profiles, env, base URLs, proxies, and optional shared context groups; these should not be treated as the same layer as Claude Code session transcripts.

## Changes

- Added `session_continuity_status()` to report Claude home, `CLAUDE_CONFIG_DIR`, `projects`, `sessions`, `history.jsonl`, and file-history anchors.
- Added `session_continuity` to `claude_status()` and provider switch results.
- Added `claude-provider continuity` CLI command and PowerShell wrapper support.
- Added the session continuity line to the 8770 Claude provider panel.
- Documented that GLM / DeepSeek provider switching should preserve the same Claude home unless context isolation is intentional.

## Verification

```text
python -m unittest tests.runtime.test_claude_local
Ran 11 tests in 15.399s
OK
```

```text
python scripts\claude-provider.py continuity
status=ok
claude_home=C:\Users\sciman\.claude
claude_config_dir_env=null
projects.jsonl_count=237
history.exists=true
provider_switch_policy=preserve_claude_home
```

```text
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
OK python-bytecode
OK python-import
```

```text
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
Completed 106 test files in 138.721s; failures=0
OK runtime-unittest
OK runtime-service-parity
OK runtime-service-wrapper-drift-guard
```

```text
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
OK functional-effectiveness
```

```text
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
OK adapter-posture-visible
WARN codex-capability-degraded
```

```text
python -m unittest tests.runtime.test_claude_local tests.runtime.test_operator_ui
Ran 18 tests
OK
```

```text
Browser verification
url=http://127.0.0.1:8770/?lang=zh-CN
action=Open Claude panel, refresh Claude status
visible_text=会话连续性
operator_ui_status=running, stale=false
```

## Compatibility

- Existing provider profile schema is unchanged.
- Existing `status`, `list`, `switch`, `delete`, `install`, and `optimize` commands remain compatible.
- The new check is read-only and does not print credentials.
