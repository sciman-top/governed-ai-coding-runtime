from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_PATH = ROOT / "rules" / "manifest.json"
DEFAULT_RULE_PATHS = {
    "codex": ROOT / "rules" / "global" / "codex" / "AGENTS.md",
    "claude": ROOT / "rules" / "global" / "claude" / "CLAUDE.md",
}
COMMON_SECTION_IDS = ["A", "C", "D"]
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
    "项目契约版本",
]
REQUIRED_PLATFORM_TOKENS = {
    "codex": [
        "## B. Codex 平台差异",
        ".codex/rules/*.rules",
        "project_doc_fallback_filenames",
        "codex debug prompt-input",
    ],
    "claude": [
        "## B. Claude 平台差异",
        ".claude/settings.json",
        ".claude/rules/",
        "CLAUDE.local.md",
        "@AGENTS.md",
        "/memory",
    ],
}
FORBIDDEN_TOKENS = ["Gemini", "GEMINI.md", ".gemini/"]
MAX_LINE_COUNT = 200


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json object required: {path}")
    return payload


def _extract_version(text: str) -> str | None:
    match = re.search(r"(?m)^\*\*版本\*\*:\s*([0-9][0-9A-Za-z_.-]*)\s*$", text)
    return match.group(1) if match else None


def _extract_project_contract_version(text: str) -> str | None:
    match = re.search(
        r"(?m)^\*\*项目契约版本\*\*:\s*([0-9][0-9A-Za-z_.-]*)\s*$",
        text,
    )
    return match.group(1) if match else None


def _normalize_section(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def _extract_common_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    matches = list(re.finditer(r"(?m)^## ([1A-D])(?:\.|\s).*$", text))
    for index, match in enumerate(matches):
        section_id = match.group(1)
        if section_id not in COMMON_SECTION_IDS:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[section_id] = _normalize_section(text[match.start() : end])
    return sections


def _display_rule_path(path: Path) -> str:
    resolved = path.resolve(strict=False)
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def verify(
    *,
    manifest_path: Path,
    rule_paths: dict[str, Path] | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path.resolve(strict=False)
    manifest = _load_json(manifest_path)
    entries = manifest.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("manifest.entries must be an array")

    failures: list[str] = []
    default_version = str(manifest.get("default_version") or "").strip()
    project_contract_version = str(manifest.get("project_contract_version") or "").strip()
    if not project_contract_version:
        failures.append("manifest project_contract_version must be a non-empty string")
    sync_script = (ROOT / "scripts" / "sync-agent-rules.py").read_text(encoding="utf-8")
    same_version_drift_protection = "blocked_same_version_drift" in sync_script

    managed_tools = [entry.get("tool") for entry in entries if isinstance(entry, dict)]
    if managed_tools != ["codex", "claude"]:
        failures.append(
            "manifest managed tools must be exactly ['codex', 'claude']; got "
            + json.dumps(managed_tools, ensure_ascii=False)
        )

    active_rule_paths = rule_paths or DEFAULT_RULE_PATHS
    rule_results: list[dict[str, Any]] = []
    common_sections_by_tool: dict[str, dict[str, str]] = {}
    for tool in ("codex", "claude"):
        path = active_rule_paths[tool].resolve(strict=False)
        if not path.exists():
            failures.append(f"missing rule file: {path}")
            continue
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            failures.append(f"{tool} rule must not contain a UTF-8 BOM")
        try:
            text = raw.decode("utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8")
        except UnicodeDecodeError:
            failures.append(f"{tool} rule must be UTF-8")
            continue

        version = _extract_version(text)
        rule_project_contract_version = _extract_project_contract_version(text)
        line_count = len(text.splitlines())
        missing_headings = [heading for heading in REQUIRED_SHARED_HEADINGS if heading not in text]
        missing_tokens = [token for token in REQUIRED_SHARED_TOKENS if token not in text]
        missing_platform_tokens = [
            token for token in REQUIRED_PLATFORM_TOKENS[tool] if token not in text
        ]
        forbidden_hits = [token for token in FORBIDDEN_TOKENS if token in text]
        common_sections = _extract_common_sections(text)
        common_sections_by_tool[tool] = common_sections

        if version != default_version:
            failures.append(f"{tool} rule version drift: expected {default_version}, got {version}")
        if rule_project_contract_version != project_contract_version:
            failures.append(
                f"{tool} project contract version drift: expected {project_contract_version}, "
                f"got {rule_project_contract_version}"
            )
        if line_count > MAX_LINE_COUNT:
            failures.append(f"{tool} rule exceeds concise budget: {line_count} > {MAX_LINE_COUNT}")
        if missing_headings:
            failures.append(f"{tool} rule missing headings: {', '.join(missing_headings)}")
        if missing_tokens:
            failures.append(f"{tool} rule missing shared tokens: {', '.join(missing_tokens)}")
        if missing_platform_tokens:
            failures.append(
                f"{tool} rule missing platform tokens: {', '.join(missing_platform_tokens)}"
            )
        if forbidden_hits:
            failures.append(
                f"{tool} rule contains out-of-scope tokens: {', '.join(forbidden_hits)}"
            )
        missing_common_sections = [
            section_id for section_id in COMMON_SECTION_IDS if section_id not in common_sections
        ]
        if missing_common_sections:
            failures.append(
                f"{tool} rule missing common sections: {', '.join(missing_common_sections)}"
            )

        common_payload = "".join(common_sections.get(item, "") for item in COMMON_SECTION_IDS)
        rule_results.append(
            {
                "tool": tool,
                "path": _display_rule_path(path),
                "version": version,
                "project_contract_version": rule_project_contract_version,
                "byte_count": len(raw),
                "line_count": line_count,
                "common_section_sha256": hashlib.sha256(
                    common_payload.encode("utf-8")
                ).hexdigest(),
                "missing_headings": missing_headings,
                "missing_shared_tokens": missing_tokens,
                "missing_platform_tokens": missing_platform_tokens,
                "forbidden_hits": forbidden_hits,
            }
        )

    common_sections_match = False
    if set(common_sections_by_tool) == {"codex", "claude"}:
        codex_sections = common_sections_by_tool["codex"]
        claude_sections = common_sections_by_tool["claude"]
        common_sections_match = all(
            codex_sections.get(section_id) == claude_sections.get(section_id)
            for section_id in COMMON_SECTION_IDS
        )
    if not common_sections_match:
        failures.append("Codex and Claude common section bodies (A/C/D) must match exactly")
    if not same_version_drift_protection:
        failures.append(
            "sync-agent-rules.py must keep blocked_same_version_drift fail-closed protection"
        )

    return {
        "status": "pass" if not failures else "fail",
        "manifest_path": str(manifest_path).replace("\\", "/"),
        "default_version": default_version,
        "project_contract_version": project_contract_version,
        "managed_tools": managed_tools,
        "common_sections": COMMON_SECTION_IDS,
        "common_sections_match": common_sections_match,
        "same_version_drift_protection": same_version_drift_protection,
        "rules": rule_results,
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify the managed Codex/Claude global rule family stays aligned."
    )
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST_PATH))
    parser.add_argument("--codex-rule-path", default=str(DEFAULT_RULE_PATHS["codex"]))
    parser.add_argument("--claude-rule-path", default=str(DEFAULT_RULE_PATHS["claude"]))
    args = parser.parse_args(argv)

    result = verify(
        manifest_path=Path(args.manifest_path),
        rule_paths={
            "codex": Path(args.codex_rule_path),
            "claude": Path(args.claude_rule_path),
        },
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
