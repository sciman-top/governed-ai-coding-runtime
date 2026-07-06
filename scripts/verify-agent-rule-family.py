from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_PATH = ROOT / "rules" / "manifest.json"
RULE_PATHS = {
    "codex": ROOT / "rules" / "global" / "codex" / "AGENTS.md",
    "claude": ROOT / "rules" / "global" / "claude" / "CLAUDE.md",
}
REQUIRED_SHARED_HEADINGS = [
    "## 1. 阅读指引",
    "## A. 共性基线",
    "### A.1 三层职责",
    "### A.2 执行与输出",
    "### A.3 强制规则 R1-R8",
    "### A.4 N/A 口径",
    "### A.5 治理演进 E1-E6",
    "### A.6 澄清协议",
    "### A.7 规则最小化与升级路径",
    "## B.",
    "## C. 项目级承接契约",
    "## D. 维护校验清单",
]
REQUIRED_SHARED_TOKENS = [
    "默认中文沟通、中文解释、中文汇报",
    "build -> test -> contract/invariant -> hotspot",
    "Global Rule -> Repo Action",
]
REQUIRED_PLATFORM_TOKENS = {
    "codex": [
        "## B. Codex 平台差异",
        ".codex/rules/*.rules",
        "project_doc_fallback_filenames",
    ],
    "claude": [
        "## B. Claude 平台差异",
        ".claude/settings.json",
        "CLAUDE.local.md",
        "@AGENTS.md",
    ],
}
FORBIDDEN_TOKENS = {
    "codex": ["Gemini", "GEMINI.md", ".gemini/"],
    "claude": ["Gemini", "GEMINI.md", ".gemini/"],
}
MAX_LINE_COUNT = 220


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json object required: {path}")
    return payload


def _extract_version(text: str) -> str | None:
    patterns = (
        r"GlobalUser/(?:AGENTS|CLAUDE|GEMINI)\.md v([0-9][0-9A-Za-z_.-]*)",
        r"\*\*版本\*\*:\s*([0-9][0-9A-Za-z_.-]*)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _heading_signature(text: str) -> list[str]:
    signature: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not (line.startswith("## ") or line.startswith("### ")):
            continue
        line = re.sub(r"Codex|Claude|Gemini", "<tool>", line)
        line = re.sub(r"AGENTS|CLAUDE|GEMINI", "<rule>", line)
        signature.append(line)
    return signature


def verify(*, manifest_path: Path) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    entries = manifest.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("manifest.entries must be an array")

    failures: list[str] = []
    default_version = str(manifest.get("default_version") or "").strip()
    sync_script = (ROOT / "scripts" / "sync-agent-rules.py").read_text(encoding="utf-8")

    managed_tools = [entry.get("tool") for entry in entries if isinstance(entry, dict)]
    if managed_tools != ["codex", "claude"]:
        failures.append(
            "manifest managed tools must be exactly ['codex', 'claude']; got "
            + json.dumps(managed_tools, ensure_ascii=False)
        )

    rule_results: list[dict[str, Any]] = []
    shared_signature: list[str] | None = None
    for tool, path in RULE_PATHS.items():
        if not path.exists():
            failures.append(f"missing rule file: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        version = _extract_version(text)
        line_count = len(text.splitlines())
        missing_headings = [heading for heading in REQUIRED_SHARED_HEADINGS if heading not in text]
        missing_tokens = [token for token in REQUIRED_SHARED_TOKENS if token not in text]
        missing_platform_tokens = [token for token in REQUIRED_PLATFORM_TOKENS[tool] if token not in text]
        forbidden_hits = [token for token in FORBIDDEN_TOKENS[tool] if token in text]
        signature = _heading_signature(text)

        if version != default_version:
            failures.append(f"{tool} rule version drift: expected {default_version}, got {version}")
        if line_count > MAX_LINE_COUNT:
            failures.append(f"{tool} rule exceeds concise budget: {line_count} > {MAX_LINE_COUNT}")
        if missing_headings:
            failures.append(f"{tool} rule missing headings: {', '.join(missing_headings)}")
        if missing_tokens:
            failures.append(f"{tool} rule missing shared tokens: {', '.join(missing_tokens)}")
        if missing_platform_tokens:
            failures.append(f"{tool} rule missing platform tokens: {', '.join(missing_platform_tokens)}")
        if forbidden_hits:
            failures.append(f"{tool} rule contains out-of-scope tokens: {', '.join(forbidden_hits)}")

        if shared_signature is None:
            shared_signature = signature
        elif signature != shared_signature:
            failures.append(f"{tool} heading skeleton drifted from the shared family signature")

        rule_results.append(
            {
                "tool": tool,
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "version": version,
                "line_count": line_count,
                "heading_count": len(signature),
                "missing_headings": missing_headings,
                "missing_shared_tokens": missing_tokens,
                "missing_platform_tokens": missing_platform_tokens,
                "forbidden_hits": forbidden_hits,
            }
        )

    if "blocked_same_version_drift" not in sync_script:
        failures.append("sync-agent-rules.py must keep blocked_same_version_drift fail-closed protection")

    return {
        "status": "pass" if not failures else "fail",
        "manifest_path": str(manifest_path.resolve(strict=False)).replace("\\", "/"),
        "default_version": default_version,
        "managed_tools": managed_tools,
        "same_version_drift_protection": "blocked_same_version_drift" in sync_script,
        "rules": rule_results,
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the managed Codex/Claude global rule family stays aligned.")
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST_PATH))
    args = parser.parse_args(argv)

    result = verify(manifest_path=Path(args.manifest_path))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
