from __future__ import annotations

import json
import os
import re
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from governed_ai_coding_runtime_contracts.file_guard import atomic_write_text, ensure_resolved_under


CONTINUITY_CLASSES = {"native_shared", "portable_shared", "referenced_only", "isolated_secret"}
DEFAULT_RETENTION_DAYS = 90
SECRET_PATTERNS = (
    re.compile(r"(?i)\b(api[_-]?key|secret|token|cookie|authorization)\b\s*[:=]\s*['\"]?[^'\"\s]{8,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{16,}"),
)


@dataclass(frozen=True)
class AgentContinuityRecord:
    record_id: str
    created_at: str
    updated_at: str
    tool_family: str
    surface: str
    repo_ref: dict[str, Any]
    continuity_class: str
    account_alias: str
    provider_alias: str
    task_summary: str
    evidence_refs: list[dict[str, Any]]
    handoff_refs: list[dict[str, Any]]
    memory_refs: list[dict[str, Any]]
    sensitivity: dict[str, Any]
    retention: dict[str, Any]
    rollback_ref: str
    model_alias: str = ""
    decisions: list[dict[str, Any]] | None = None
    changed_files: list[str] | None = None
    next_actions: list[str] | None = None
    native_refs: list[dict[str, Any]] | None = None
    config_summary: dict[str, Any] | None = None
    platform_na: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "record_id": self.record_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tool_family": self.tool_family,
            "surface": self.surface,
            "repo_ref": self.repo_ref,
            "continuity_class": self.continuity_class,
            "account_alias": self.account_alias,
            "provider_alias": self.provider_alias,
            "task_summary": self.task_summary,
            "evidence_refs": self.evidence_refs,
            "handoff_refs": self.handoff_refs,
            "memory_refs": self.memory_refs,
            "sensitivity": self.sensitivity,
            "retention": self.retention,
            "rollback_ref": self.rollback_ref,
        }
        if self.model_alias:
            payload["model_alias"] = self.model_alias
        if self.decisions is not None:
            payload["decisions"] = self.decisions
        if self.changed_files is not None:
            payload["changed_files"] = self.changed_files
        if self.next_actions is not None:
            payload["next_actions"] = self.next_actions
        if self.native_refs is not None:
            payload["native_refs"] = self.native_refs
        if self.config_summary is not None:
            payload["config_summary"] = self.config_summary
        if self.platform_na is not None:
            payload["platform_na"] = self.platform_na
        return payload


def audit_agent_continuity(
    *,
    repo_root: Path | str,
    codex_home: Path | str | None = None,
    claude_home: Path | str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    timestamp = _timestamp(now)
    root = Path(repo_root).expanduser().resolve()
    records = [
        build_codex_continuity_record(repo_root=root, codex_home=codex_home, now=timestamp),
        build_claude_continuity_record(repo_root=root, claude_home=claude_home, now=timestamp),
        build_claude_desktop_boundary_record(repo_root=root, now=timestamp),
    ]
    return {
        "status": "ok",
        "schema": "agent-continuity-record",
        "record_count": len(records),
        "records": [record.to_dict() for record in records],
    }


@dataclass(frozen=True)
class ContinuityIndexWriteResult:
    record_id: str
    record_ref: str
    index_ref: str
    status: str = "written"

    def to_dict(self) -> dict[str, str]:
        return {
            "status": self.status,
            "record_id": self.record_id,
            "record_ref": self.record_ref,
            "index_ref": self.index_ref,
        }


class LocalAgentContinuityIndex:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).expanduser().resolve(strict=False)
        self.records_root = self.root / "records"
        self.index_path = self.root / "index.json"
        self.root.mkdir(parents=True, exist_ok=True)
        self.records_root.mkdir(parents=True, exist_ok=True)

    def write_record(self, record: AgentContinuityRecord | dict[str, Any]) -> ContinuityIndexWriteResult:
        payload = record.to_dict() if isinstance(record, AgentContinuityRecord) else dict(record)
        validate_portable_continuity_record(payload)
        record_id = _required_string(payload.get("record_id"), "record_id")
        record_path = self.records_root / f"{_safe_component(record_id)}.json"
        ensure_resolved_under(record_path, self.root, field_name="record_path")
        atomic_write_text(record_path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        index = self._load_index()
        entry = _index_entry(payload, record_path.relative_to(self.root).as_posix())
        entries = [item for item in index["records"] if item.get("record_id") != record_id]
        entries.append(entry)
        index["records"] = sorted(entries, key=lambda item: item["record_id"])
        index["updated_at"] = _timestamp()
        atomic_write_text(self.index_path, json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        return ContinuityIndexWriteResult(
            record_id=record_id,
            record_ref=record_path.relative_to(self.root).as_posix(),
            index_ref=self.index_path.relative_to(self.root).as_posix(),
        )

    def search(
        self,
        *,
        repo_id: str | None = None,
        tool_family: str | None = None,
        account_alias: str | None = None,
        provider_alias: str | None = None,
        include_expired: bool = False,
        include_secret_blocked: bool = False,
        now: datetime | str | None = None,
    ) -> dict[str, Any]:
        timestamp = _timestamp(now)
        index = self._load_index()
        matches: list[dict[str, Any]] = []
        for entry in index["records"]:
            if repo_id and entry.get("repo_id") != repo_id:
                continue
            if tool_family and entry.get("tool_family") != tool_family:
                continue
            if account_alias and entry.get("account_alias") != account_alias:
                continue
            if provider_alias and entry.get("provider_alias") != provider_alias:
                continue
            if not include_expired and _is_expired(entry.get("expires_at"), timestamp):
                continue
            if not include_secret_blocked and entry.get("secret_blocked"):
                continue
            matches.append(entry)
        return {
            "status": "ok",
            "index_kind": "agent_continuity_index",
            "record_count": len(matches),
            "records": matches,
        }

    def _load_index(self) -> dict[str, Any]:
        if not self.index_path.exists():
            return {
                "index_kind": "agent_continuity_index",
                "schema": "agent-continuity-record",
                "created_at": _timestamp(),
                "updated_at": _timestamp(),
                "records": [],
            }
        payload = _read_json(self.index_path)
        if payload.get("index_kind") != "agent_continuity_index" or not isinstance(payload.get("records"), list):
            raise ValueError("agent continuity index is malformed")
        return payload


def validate_portable_continuity_record(payload: dict[str, Any]) -> None:
    for field in (
        "record_id",
        "tool_family",
        "surface",
        "continuity_class",
        "account_alias",
        "provider_alias",
        "task_summary",
        "rollback_ref",
    ):
        _required_string(payload.get(field), field)
    if payload.get("continuity_class") not in CONTINUITY_CLASSES:
        raise ValueError("continuity_class is invalid")
    sensitivity = payload.get("sensitivity")
    if not isinstance(sensitivity, dict):
        raise ValueError("sensitivity is required")
    if sensitivity.get("contains_secret_material") is True or sensitivity.get("redaction_status") == "blocked":
        raise ValueError("continuity records containing blocked secret material cannot be written")
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if _contains_secret_like_text(serialized):
        raise ValueError("continuity record contains secret-like material")


def _index_entry(payload: dict[str, Any], record_ref: str) -> dict[str, Any]:
    repo_ref = payload.get("repo_ref") if isinstance(payload.get("repo_ref"), dict) else {}
    sensitivity = payload.get("sensitivity") if isinstance(payload.get("sensitivity"), dict) else {}
    retention = payload.get("retention") if isinstance(payload.get("retention"), dict) else {}
    return {
        "record_id": payload["record_id"],
        "record_ref": record_ref,
        "repo_id": _string_value(repo_ref.get("repo_id")),
        "tool_family": payload["tool_family"],
        "surface": payload["surface"],
        "continuity_class": payload["continuity_class"],
        "account_alias": payload["account_alias"],
        "provider_alias": payload["provider_alias"],
        "task_summary": payload["task_summary"],
        "sensitivity_level": sensitivity.get("level") or "private",
        "secret_blocked": sensitivity.get("contains_secret_material") is True or sensitivity.get("redaction_status") == "blocked",
        "expires_at": retention.get("expires_at"),
        "updated_at": payload.get("updated_at"),
    }


def build_codex_continuity_record(
    *,
    repo_root: Path,
    codex_home: Path | str | None = None,
    now: datetime | str | None = None,
) -> AgentContinuityRecord:
    timestamp = _timestamp(now)
    home = _resolve_home(codex_home, "CODEX_HOME", ".codex")
    repo_ref = _repo_ref(repo_root)
    if home is None or not home.exists():
        return _platform_na_record(
            record_id="codex-continuity-missing",
            now=timestamp,
            tool_family="codex",
            surface="codex-cli",
            repo_ref=repo_ref,
            reason="Codex home is not present.",
            alternative="Run after Codex App or Codex CLI has created the configured home.",
            evidence_link=str(home) if home else "CODEX_HOME",
        )

    config_path = home / "config.toml"
    config = _read_toml(config_path)
    history = config.get("history") if isinstance(config.get("history"), dict) else {}
    profiles = config.get("profiles") if isinstance(config.get("profiles"), dict) else {}
    model_provider = _string_value(config.get("model_provider")) or "openai"
    model = _string_value(config.get("model"))
    sqlite_home = _string_value(config.get("sqlite_home"))
    log_dir = _string_value(config.get("log_dir"))
    state_path = home / "state_5.sqlite"
    sessions_dir = home / "sessions"
    launcher_names = [
        "codex-shared.cmd",
        "codex-shared-exec.cmd",
        "codex-shared-resume.cmd",
        "codex-shared-app.cmd",
    ]
    launcher_dir = home.parent / ".local" / "bin"
    existing_launchers = [name for name in launcher_names if (launcher_dir / name).exists()]
    decisions = [
        {
            "summary": "Codex continuity is native within one shared Codex home and portable across hosts only through classified records.",
            "evidence_ref": "docs/change-evidence/2026-05-08-codex-shared-history-local-optimize.md",
        }
    ]
    next_actions = []
    if history.get("persistence") != "save-all":
        next_actions.append("Set [history] persistence to save-all before claiming shared Codex history.")
    if sqlite_home and _same_path(Path(sqlite_home).expanduser(), home) is False:
        next_actions.append("Align sqlite_home with the shared Codex home or record intentional isolation.")

    return AgentContinuityRecord(
        record_id="codex-shared-home",
        created_at=timestamp,
        updated_at=timestamp,
        tool_family="codex",
        surface="codex-cli",
        repo_ref=repo_ref,
        continuity_class="native_shared",
        account_alias=_account_alias_from_codex_home(home),
        provider_alias=model_provider,
        model_alias=model,
        task_summary="Read-only Codex shared-home continuity posture for App, CLI, and exec launchers.",
        decisions=decisions,
        changed_files=[],
        next_actions=next_actions,
        evidence_refs=[
            _ref("file", "docs/change-evidence/2026-05-08-codex-shared-history-local-optimize.md", "Codex shared-history apply evidence"),
            _ref("file", str(config_path), "Codex config path"),
        ],
        handoff_refs=[],
        memory_refs=[],
        native_refs=[
            _native_ref("codex", "config", str(config_path), "host_owned"),
            _native_ref("codex", "sqlite", str(state_path), "host_owned"),
            _native_ref("codex", "transcript", str(sessions_dir), "referenced_only"),
        ],
        config_summary={
            "history_persistence": history.get("persistence"),
            "sqlite_home": sqlite_home,
            "log_dir": log_dir,
            "state_sqlite_exists": state_path.exists(),
            "sessions_jsonl_count": _count_files(sessions_dir, "*.jsonl"),
            "profile_names": sorted(str(key) for key in profiles.keys()),
            "shared_launchers_present": existing_launchers,
        },
        sensitivity=_sensitivity(level="private", cross_account="requires_explicit_request"),
        retention=_retention(timestamp),
        rollback_ref="Ignore this generated record or rerun the read-only audit after restoring Codex config backups.",
    )


def build_claude_continuity_record(
    *,
    repo_root: Path,
    claude_home: Path | str | None = None,
    now: datetime | str | None = None,
) -> AgentContinuityRecord:
    timestamp = _timestamp(now)
    home = _resolve_home(claude_home, "CLAUDE_CONFIG_DIR", ".claude")
    repo_ref = _repo_ref(repo_root)
    if home is None or not home.exists():
        return _platform_na_record(
            record_id="claude-continuity-missing",
            now=timestamp,
            tool_family="claude",
            surface="claude-code-cli",
            repo_ref=repo_ref,
            reason="Claude home is not present.",
            alternative="Run after Claude Code has created the configured home.",
            evidence_link=str(home) if home else "CLAUDE_CONFIG_DIR",
        )

    settings = _read_json(home / "settings.json")
    provider_profiles = _read_json(home / "provider-profiles.json")
    active_provider = _first_string(provider_profiles.get("active")) if isinstance(provider_profiles, dict) else ""
    if not active_provider:
        active_provider = _provider_from_settings(settings)
    projects_dir = home / "projects"
    sessions_dir = home / "sessions"
    history_path = home / "history.jsonl"
    file_history_dir = home / "file-history"

    return AgentContinuityRecord(
        record_id="claude-shared-home",
        created_at=timestamp,
        updated_at=timestamp,
        tool_family="claude",
        surface="claude-code-cli",
        repo_ref=repo_ref,
        continuity_class="native_shared",
        account_alias="claude-local",
        provider_alias=active_provider or "unknown-provider",
        task_summary="Read-only Claude Code continuity posture anchored in one Claude home.",
        decisions=[
            {
                "summary": "Claude provider switching should preserve the same Claude home unless isolation is intentional.",
                "evidence_ref": "docs/change-evidence/2026-05-10-claude-provider-session-continuity.md",
            }
        ],
        changed_files=[],
        next_actions=[],
        evidence_refs=[
            _ref("file", "docs/change-evidence/2026-05-10-claude-provider-session-continuity.md", "Claude continuity evidence"),
            _ref("file", str(home / "settings.json"), "Claude settings path"),
        ],
        handoff_refs=[],
        memory_refs=[],
        native_refs=[
            _native_ref("claude", "config", str(home / "settings.json"), "host_owned"),
            _native_ref("claude", "transcript", str(projects_dir), "referenced_only"),
            _native_ref("claude", "jsonl", str(history_path), "referenced_only"),
        ],
        config_summary={
            "claude_home": str(home),
            "claude_config_dir_env": os.environ.get("CLAUDE_CONFIG_DIR") or None,
            "projects_exists": projects_dir.exists(),
            "projects_jsonl_count": _count_files(projects_dir, "*.jsonl"),
            "sessions_jsonl_count": _count_files(sessions_dir, "*.jsonl"),
            "history_exists": history_path.exists(),
            "file_history_exists": file_history_dir.exists(),
            "provider_switch_policy": "preserve_claude_home",
        },
        sensitivity=_sensitivity(level="private", cross_account="requires_explicit_request"),
        retention=_retention(timestamp),
        rollback_ref="Ignore this generated record or rerun the read-only audit after restoring Claude settings/provider profiles.",
    )


def build_claude_desktop_boundary_record(
    *,
    repo_root: Path,
    now: datetime | str | None = None,
) -> AgentContinuityRecord:
    timestamp = _timestamp(now)
    return AgentContinuityRecord(
        record_id="claude-desktop-boundary",
        created_at=timestamp,
        updated_at=timestamp,
        tool_family="claude-desktop",
        surface="claude-desktop-chat",
        repo_ref=_repo_ref(repo_root),
        continuity_class="referenced_only",
        account_alias="claude-desktop-local",
        provider_alias="claude-desktop",
        task_summary="Claude Desktop native chat history is not treated as a shared writable continuity store.",
        decisions=[
            {
                "summary": "Desktop history can be referenced or handed off through supported export/transfer flows, not merged into Codex or Claude Code native stores.",
                "evidence_ref": "docs/plans/agent-continuity-and-shared-context-plan.md",
            }
        ],
        changed_files=[],
        next_actions=["Use portable handoff records for cross-host continuity instead of mutating Claude Desktop private state."],
        evidence_refs=[_ref("file", "docs/plans/agent-continuity-and-shared-context-plan.md", "Continuity boundary plan")],
        handoff_refs=[],
        memory_refs=[],
        native_refs=[],
        sensitivity=_sensitivity(level="private", cross_account="requires_explicit_request"),
        retention=_retention(timestamp),
        rollback_ref="Remove or ignore this boundary record; no Desktop state is modified.",
        platform_na={
            "applies": True,
            "reason": "Claude Desktop native chat history is host-owned and not a supported shared writable state root for this runtime.",
            "alternative_verification": "Use exported or transferred context as referenced-only input and create portable handoff records.",
            "evidence_link": "docs/plans/agent-continuity-and-shared-context-plan.md",
            "expires_at": _future_timestamp(timestamp),
        },
    )


def _platform_na_record(
    *,
    record_id: str,
    now: str,
    tool_family: str,
    surface: str,
    repo_ref: dict[str, Any],
    reason: str,
    alternative: str,
    evidence_link: str,
) -> AgentContinuityRecord:
    return AgentContinuityRecord(
        record_id=record_id,
        created_at=now,
        updated_at=now,
        tool_family=tool_family,
        surface=surface,
        repo_ref=repo_ref,
        continuity_class="referenced_only",
        account_alias=f"{tool_family}-unknown",
        provider_alias="unknown-provider",
        task_summary=f"{tool_family} continuity surface unavailable.",
        evidence_refs=[],
        handoff_refs=[],
        memory_refs=[],
        native_refs=[],
        sensitivity=_sensitivity(level="private", cross_account="blocked"),
        retention=_retention(now),
        rollback_ref="No rollback required; no host state was modified.",
        platform_na={
            "applies": True,
            "reason": reason,
            "alternative_verification": alternative,
            "evidence_link": evidence_link,
            "expires_at": _future_timestamp(now),
        },
    )


def _resolve_home(value: Path | str | None, env_name: str, default_name: str) -> Path | None:
    raw = value or os.environ.get(env_name) or str(Path.home() / default_name)
    try:
        return Path(raw).expanduser().resolve()
    except OSError:
        return None


def _repo_ref(repo_root: Path) -> dict[str, Any]:
    return {"repo_id": repo_root.name, "path": str(repo_root)}


def _timestamp(value: datetime | str | None = None) -> str:
    if isinstance(value, str):
        return value
    current = value or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _future_timestamp(value: str, days: int = DEFAULT_RETENTION_DAYS) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return (parsed + timedelta(days=days)).astimezone(UTC).isoformat().replace("+00:00", "Z")


def _retention(now: str) -> dict[str, Any]:
    return {
        "expires_at": _future_timestamp(now),
        "retirement_policy": "Retire or refresh when source evidence, account/provider aliases, or host storage boundaries become stale.",
        "audit_history_preserved": True,
    }


def _sensitivity(*, level: str, cross_account: str) -> dict[str, Any]:
    return {
        "level": level,
        "cross_account_injection": cross_account,
        "contains_secret_material": False,
        "redaction_status": "not_needed",
    }


def _ref(kind: str, ref: str, summary: str) -> dict[str, str]:
    return {"kind": kind, "ref": ref, "summary": summary}


def _native_ref(owner: str, kind: str, ref: str, storage_policy: str) -> dict[str, str]:
    return {"owner": owner, "kind": kind, "ref": ref, "storage_policy": storage_policy}


def _read_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("rb") as handle:
            payload = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _count_files(root: Path, pattern: str) -> int:
    if not root.exists():
        return 0
    try:
        return sum(1 for path in root.rglob(pattern) if path.is_file())
    except OSError:
        return 0


def _string_value(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _first_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _provider_from_settings(settings: dict[str, Any]) -> str:
    env = settings.get("env")
    if isinstance(env, dict):
        base_url = _first_string(env.get("ANTHROPIC_BASE_URL"))
        if "bigmodel" in base_url:
            return "bigmodel-glm"
        if "deepseek" in base_url:
            return "deepseek-v4"
    return "unknown-provider"


def _account_alias_from_codex_home(home: Path) -> str:
    auth_path = home / "auth.json"
    return "codex-active-auth" if auth_path.exists() else "codex-no-active-auth"


def _same_path(left: Path, right: Path) -> bool | None:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return None


def _contains_secret_like_text(value: str) -> bool:
    return any(pattern.search(value) for pattern in SECRET_PATTERNS)


def _required_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _safe_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return cleaned or "record"


def _is_expired(value: Any, now: str) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        expires_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
        current = datetime.fromisoformat(now.replace("Z", "+00:00"))
    except ValueError:
        return False
    return expires_at <= current
