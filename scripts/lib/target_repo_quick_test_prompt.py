from __future__ import annotations

from pathlib import Path
from typing import Any

from lib.target_repo_speed_profile import as_command_list


def build_quick_test_slice_prompt(*, target_repo: Path, profile: dict[str, Any]) -> str:
    test_commands = as_command_list(profile.get("test_commands"))
    contract_commands = as_command_list(profile.get("contract_commands"))
    invariant_commands = as_command_list(profile.get("invariant_commands"))
    full_test = test_commands[0]["command"] if test_commands else ""
    full_contract = contract_commands[0]["command"] if contract_commands else ""
    full_invariant = invariant_commands[0]["command"] if invariant_commands else ""
    return f"""# Quick Test Slice Recommendation Prompt

You are reviewing a target repository for a safe daily fast-test slice.

Target repo: `{target_repo}`
Repo id: `{profile.get("repo_id", "")}`
Primary language: `{profile.get("primary_language", "")}`
Full test command: `{full_test}`
Full contract command: `{full_contract}`
Full invariant command: `{full_invariant}`

Task:
1. Inspect the target repo test structure, markers/categories, and existing fast/smoke scripts.
2. Recommend a `quick_test_command` only if it is deterministic, materially faster than the full test command, and representative of daily coding risk.
3. Do not weaken full/release gates. The full test command must remain unchanged.
4. If no safe slice exists, emit `status=skip`.

Write this JSON to `.governed-ai/quick-test-slice.recommendation.json`:

```json
{{
  "schema_version": "1.0",
  "status": "ready",
  "quick_test_command": "<command>",
  "quick_test_reason": "<short reason>",
  "quick_test_timeout_seconds": 180
}}
```

Use this skip form when no safe slice is justified:

```json
{{
  "schema_version": "1.0",
  "status": "skip",
  "quick_test_reason": "No safe target-specific quick test slice found."
}}
```
"""
