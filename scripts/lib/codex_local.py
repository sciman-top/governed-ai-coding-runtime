from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = {
    "model": "gpt-5.4",
    "model_reasoning_effort": "medium",
    "model_verbosity": "medium",
    "model_context_window": 128000,
    "model_auto_compact_token_limit": 96000,
    "sandbox_mode": "workspace-write",
    "approval_policy": "never",
    "web_search": "cached",
}
USAGE_DASHBOARD_URL = "https://chatgpt.com/codex/settings/usage"


@dataclass(frozen=True)
class CodexAuthProfile:
    name: str
    file: str
    active: bool
    auth_mode: str
    last_refresh: str
    account_hash: str
    sha256: str
    full_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "file": self.file,
            "active": self.active,
            "auth_mode": self.auth_mode,
            "last_refresh": self.last_refresh,
            "account_hash": self.account_hash,
            "sha256": self.sha256,
            "full_name": self.full_name,
        }


def codex_home(value: str | None = None) -> Path:
    raw = value or os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    path = Path(raw).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Codex home does not exist: {path}")
    return path.resolve()


def list_auth_profiles(home: Path | None = None) -> list[CodexAuthProfile]:
    home = codex_home(str(home) if home else None)
    active_path = home / "auth.json"
    active_hash = _short_file_hash(active_path) if active_path.exists() else ""
    candidates: list[Path] = []
    candidates.extend(sorted(home.glob("auth*.json")))
    profiles_dir = home / "auth-profiles"
    if profiles_dir.exists():
        candidates.extend(sorted(profiles_dir.glob("*.json")))
    unique = sorted({path.resolve() for path in candidates})
    return [_auth_profile_from_path(path, active_hash) for path in unique]


def active_auth_status(home: Path | None = None) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    active_path = home / "auth.json"
    if not active_path.exists():
        return {"status": "missing", "error": f"missing active auth: {active_path}"}
    profile = _auth_profile_from_path(active_path, _short_file_hash(active_path))
    return {"status": "ok", "active_profile": profile.to_dict()}


def switch_auth_profile(name: str, home: Path | None = None, *, dry_run: bool = False) -> dict[str, Any]:
    normalized_name = str(name or "").strip()
    if not normalized_name:
        return {"status": "error", "error": "missing auth profile name"}
    home = codex_home(str(home) if home else None)
    profiles = list_auth_profiles(home)
    matches = [
        profile
        for profile in profiles
        if profile.name == normalized_name or profile.file == normalized_name or profile.full_name == normalized_name
    ]
    if not matches:
        return {"status": "error", "error": f"unknown auth profile: {normalized_name}"}
    if len(matches) > 1:
        return {"status": "error", "error": f"ambiguous auth profile: {normalized_name}"}
    target = matches[0]
    active_path = home / "auth.json"
    if target.active:
        return {"status": "ok", "changed": False, "active_profile": target.to_dict()}
    if dry_run:
        return {"status": "ok", "changed": False, "dry_run": True, "target_profile": target.to_dict()}

    backup_path = backup_active_auth(home)
    shutil.copyfile(target.full_name, active_path)
    new_active = _auth_profile_from_path(active_path, _short_file_hash(active_path))
    return {
        "status": "ok",
        "changed": True,
        "backup_path": str(backup_path),
        "active_profile": new_active.to_dict(),
        "target_profile": target.to_dict(),
    }


def backup_active_auth(home: Path | None = None) -> Path:
    home = codex_home(str(home) if home else None)
    active_path = home / "auth.json"
    if not active_path.exists():
        raise FileNotFoundError(f"missing active auth: {active_path}")
    backup_dir = home / "auth-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = backup_dir / f"auth-{timestamp}.json"
    shutil.copyfile(active_path, backup_path)
    return backup_path


def codex_status(home: Path | None = None) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    payload: dict[str, Any] = {
        "codex_home": str(home),
        "auth": active_auth_status(home),
        "accounts": [profile.to_dict() for profile in list_auth_profiles(home)],
        "config": config_health(home),
        "usage": {
            "source": "unknown",
            "dashboard_url": USAGE_DASHBOARD_URL,
            "windows": [
                {"window": "5h", "remaining": None, "reset_at": None},
                {"window": "7d", "remaining": None, "reset_at": None},
            ],
            "note": "No stable public local API was detected for per-account Codex usage limits.",
        },
    }
    payload["login_status"] = _run_codex_login_status()
    return payload


def config_health(home: Path | None = None) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    config_path = home / "config.toml"
    if not config_path.exists():
        return {"status": "missing", "path": str(config_path), "checks": []}
    text = config_path.read_text(encoding="utf-8", errors="replace")
    checks = []
    for key, expected in DEFAULT_CONFIG.items():
        actual = _find_top_level_value(text, key)
        checks.append(
            {
                "key": key,
                "expected": expected,
                "actual": actual,
                "ok": str(actual) == str(expected),
            }
        )
    secret_hits = []
    for marker in ("ANTHROPIC_AUTH_TOKEN", "ctx7" + "sk", "sk-"):
        if marker in text:
            secret_hits.append(marker)
    return {
        "status": "ok" if all(check["ok"] for check in checks) and not secret_hits else "attention",
        "path": str(config_path),
        "checks": checks,
        "secret_like_markers": secret_hits,
    }


def install_account_switcher(home: Path | None = None, bin_dir: Path | None = None) -> dict[str, Any]:
    home = codex_home(str(home) if home else None)
    bin_dir = (bin_dir or (Path.home() / ".local" / "bin")).expanduser()
    scripts_dir = home / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / "scripts" / "codex-account.ps1"
    target = scripts_dir / "Switch-CodexAccount.ps1"
    shim = bin_dir / "codex-account.cmd"
    shutil.copyfile(source, target)
    shim.write_text(
        '@echo off\npwsh -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\\.codex\\scripts\\Switch-CodexAccount.ps1" %*\n',
        encoding="utf-8",
    )
    return {"status": "ok", "script": str(target), "shim": str(shim)}


def _auth_profile_from_path(path: Path, active_hash: str) -> CodexAuthProfile:
    payload = _read_auth_json(path)
    tokens = payload.get("tokens") if isinstance(payload.get("tokens"), dict) else {}
    account_id = str(tokens.get("account_id") or "")
    file_hash = _short_file_hash(path)
    return CodexAuthProfile(
        name=path.stem,
        file=path.name,
        active=file_hash == active_hash,
        auth_mode=str(payload.get("auth_mode") or ""),
        last_refresh=str(payload.get("last_refresh") or ""),
        account_hash=_short_string_hash(account_id) if account_id else "",
        sha256=file_hash,
        full_name=str(path),
    )


def _read_auth_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid auth JSON: {path}")
    return payload


def _short_file_hash(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest[:12]


def _short_string_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _find_top_level_value(text: str, key: str) -> Any:
    current_section = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line
            continue
        if current_section:
            continue
        prefix = f"{key} ="
        if line.startswith(prefix):
            value = line[len(prefix) :].strip()
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            try:
                return int(value)
            except ValueError:
                return value
    return None


def _run_codex_login_status() -> dict[str, Any]:
    codex_cmd = shutil.which("codex.cmd") or shutil.which("codex")
    if not codex_cmd:
        return {"exit_code": 127, "summary": "codex command not found"}
    try:
        completed = subprocess.run(
            [codex_cmd, "login", "status"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": 127, "summary": str(exc)}
    return {
        "exit_code": completed.returncode,
        "summary": "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part),
    }
