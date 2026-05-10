# 2026-05-10 Codex history view pagination root cause

- rules: R1/R3/R4/R6/R8, E4/E6
- risk: low, read-only root-cause diagnosis after the previous cwd alias repair did not change the native App sidebar view
- landing: `scripts/codex-history-view-diagnose.py`, `tests/runtime/test_codex_history_view_diagnose.py`
- destination: distinguish real Codex history loss from native App `thread/list` pagination and repository grouping behavior

## Findings

- The previous cwd alias repair was useful for bucket consistency but was not the final root cause of the sparse native sidebar.
- `state_5.sqlite` still contains the target histories. For example, the canonical App-source rows include:
  - `D:\CODE\ClassroomToolkit`: latest visible-by-filter thread rank `64` in a `sourceKinds=["vscode"]`, `sortKey="updated_at"` global list.
  - `D:\CODE\skills-manager`: recent rows appear inside the first page.
  - `D:\CODE\github-toolkit`: recent rows appear inside the first page.
  - `D:\CODE\vps-ssh-launcher`: recent rows appear inside the first page.
- Including both `vscode` and `cli` source rows, `D:\CODE\ClassroomToolkit` has hundreds of local history rows; its latest row still ranks outside the native sidebar's first 50-row global recent page.
- The native App frontend does not use the `展开显示` / `Show more` control as a pagination fetch. The local bundled frontend code builds that button from already-loaded `threadKeys`: collapsed state renders `threadKeys.slice(0, maxItems)`, and clicking it only flips `expanded` via `onExpandedChange`.
- The frontend path that does fetch more recent rows is separate: `loadMoreRecentConversations()` calls `thread/list` with `cursor:this.nextRecentConversationCursor` and `limit:50`. The grouped `Show more` button is only an in-memory expansion control for rows already fetched into the sidebar store.
- App frontend constants observed in the local bundle:
  - recent chat section `maxItems`: `10`.
  - per-folder/project group `maxItems`: `5`.
  - first recent refresh/load page size: `50`.
- Direct `codex app-server --listen stdio://` calls showed:
  - default `thread/list` returned `25` rows and `nextCursor`.
  - `thread/list` with `limit=50` returned `50` rows and no `ClassroomToolkit` rows.
  - `thread/list` with `limit=150` or `limit=250` returned only `100` rows, proving the server caps a single page at `100`.
  - `thread/list` with `cwd="D:\CODE\ClassroomToolkit"` returned ClassroomToolkit rows immediately.
- Therefore restarting Codex App cannot make all repository history appear in the initial sidebar page. The root cause is global recent-history pagination plus grouped display, not missing transcript files, not provider bucket split, and not a stale Electron `Local Storage` cache.
- Therefore clicking `展开显示` can produce no visible change when the missing repository rows were never loaded into the sidebar's current page. This matches the user's post-restart observation.

## Commands

- `codex app-server --help`
- `codex app-server generate-ts --out C:\Users\sciman\.codex\tmp\app-server-ts`
- JSON-RPC stdio probe against `codex app-server --listen stdio://`:
  - `thread/list` with `{ "sortKey": "updated_at", "sortDirection": "desc", "sourceKinds": ["vscode"], "archived": false, "useStateDbOnly": true, "limit": 50 }`
  - `thread/list` with the same parameters and `limit` set to `150` and `250`
  - `thread/list` with `cwd` set to `D:\CODE\ClassroomToolkit`
- `python scripts/codex-history-view-diagnose.py --codex-home "$env:USERPROFILE\.codex" --target-cwd "D:\CODE\ClassroomToolkit" --target-cwd "D:\CODE\skills-manager" --target-cwd "D:\CODE\github-toolkit" --target-cwd "D:\CODE\vps-ssh-launcher"`
- `python scripts/codex-history-view-diagnose.py --codex-home C:\Users\sciman\.codex --target-cwd D:\CODE\ClassroomToolkit --target-cwd D:\CODE\skills-manager --target-cwd D:\CODE\github-toolkit --target-cwd D:\CODE\vps-ssh-launcher`
- `python scripts/codex-history-view-diagnose.py --codex-home C:\Users\sciman\.codex --source vscode --source cli --target-cwd D:\CODE\ClassroomToolkit --target-cwd D:\CODE\skills-manager --target-cwd D:\CODE\github-toolkit --target-cwd D:\CODE\vps-ssh-launcher`
- `python -m unittest tests.runtime.test_codex_history_view_diagnose -v`
- `python scripts/codex-history-view-diagnose.py --codex-home C:\Users\sciman\.codex --source vscode --source cli --target-cwd D:\CODE\ClassroomToolkit --target-cwd D:\CODE\skills-manager --target-cwd D:\CODE\github-toolkit --target-cwd D:\CODE\vps-ssh-launcher` on 2026-05-10 after the Windows console encoding fix.

## Evidence

- `ThreadListParams` generated from the local app-server protocol declares `cursor`, optional `limit`, `sortKey`, `sortDirection`, `sourceKinds`, `cwd`, and `searchTerm`.
- `ThreadListResponse` declares `data`, `nextCursor`, and `backwardsCursor`.
- The live stdio probe returned `nextCursor=true` for all truncated pages.
- The native App user-data `Local Storage\leveldb` copy did not contain screenshot titles or target repo names, so the sparse view was not explained by a stale front-end storage cache.
- The new diagnostic script models the pagination boundary and reports whether each target is visible in the native first loaded page, visible in the maximum first page, or hidden until a next-cursor/cwd-filtered query.
- Live `vscode`-source diagnostic after the `Show more` investigation:
  - first native page (`limit=50`) has `0` `ClassroomToolkit` rows and `1` `vps-ssh-launcher` row.
  - first maximum page (`limit=100`) has `2` `ClassroomToolkit` rows.
  - `ClassroomToolkit` latest rank is `64`, diagnosis `hidden_until_native_recent_list_loads_a_larger_page`.
  - `skills-manager`, `github-toolkit`, and `vps-ssh-launcher` are visible in the native first page.
- Live `vscode+cli` diagnostic after the `Show more` investigation:
  - `ClassroomToolkit` total rows under that project root: `439`.
  - `ClassroomToolkit` latest rank is `67`, diagnosis `hidden_until_native_recent_list_loads_a_larger_page`.
- Live diagnostic evidence written during this investigation:
  - `C:\Users\sciman\.codex\tmp\codex-history-view-diagnose-live-vscode.json`
  - `C:\Users\sciman\.codex\tmp\codex-history-view-diagnose-live-vscode-cli.json`
- Fresh 2026-05-10 `vscode+cli` diagnostic after the output encoding hardening:
  - total loaded non-archived rows: `1307`.
  - first native page (`limit=50`) contains `0` `ClassroomToolkit` rows, `1` `skills-manager` row, `2` `github-toolkit` rows, and `1` `vps-ssh-launcher` row.
  - maximum observed first page (`limit=100`) contains `2` `ClassroomToolkit` rows.
  - `ClassroomToolkit`: `439` total rows, latest rank `69`, diagnosis `hidden_until_native_recent_list_loads_a_larger_page`.
  - `skills-manager`: `220` total rows, latest rank `19`, diagnosis `visible_in_initial_thread_list_page`.
  - `github-toolkit`: `23` total rows, latest rank `5`, diagnosis `visible_in_initial_thread_list_page`.
  - `vps-ssh-launcher`: `29` total rows, latest rank `27`, diagnosis `visible_in_initial_thread_list_page`.
- `scripts/codex-history-view-diagnose.py` now emits ASCII-safe JSON (`ensure_ascii=True`) so thread titles containing symbols do not fail under a Windows GBK console.

## Operator guidance

- In Codex App, the sidebar `展开显示` / `Show more` control should not be treated as "load all history"; it only expands already-loaded rows.
- First check the sidebar display mode menu and use `显示 -> 所有对话` instead of `相关` when available; that can remove relevance filtering, but it still does not guarantee that every older repository is loaded into the sidebar.
- Use repository/search-filtered history when an older repository is absent from the initial grouped sidebar. The app-server supports `cwd` and `searchTerm`, and direct `cwd="D:\CODE\ClassroomToolkit"` queries return rows immediately.
- Do not rewrite timestamps or create synthetic threads to force old repository histories into the first page; that would corrupt chronological semantics.
- Keep the cwd alias repair tool as a separate repair for path-bucket drift, but do not use it as proof that the native sidebar has loaded every repository's full history.

## Rollback

- Revert `scripts/codex-history-view-diagnose.py`, `tests/runtime/test_codex_history_view_diagnose.py`, and this evidence file from git history.
- No live Codex sqlite rows, auth files, provider config, Electron cache files, or transcript JSONL files were changed by this diagnosis.
