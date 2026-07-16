from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "rules" / "global" / "source-manifest.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("source manifest must be a JSON object")
    return payload


def _repo_path(root: Path, raw_path: Any) -> Path:
    relative = Path(str(raw_path or "").strip())
    if not str(relative) or relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"repo-relative path required: {raw_path!r}")
    resolved = (root / relative).resolve(strict=False)
    try:
        resolved.relative_to(root.resolve(strict=False))
    except ValueError as exc:
        raise ValueError(f"path escapes repository root: {raw_path}") from exc
    return resolved


def _read_fragment(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM is not allowed: {path}")
    return raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def render_outputs(*, root: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    placeholder = str(manifest.get("placeholder") or "")
    if not placeholder:
        raise ValueError("manifest placeholder must be a non-empty string")
    shared_path = _repo_path(root, manifest.get("shared"))
    shared = _read_fragment(shared_path).rstrip("\n")
    if shared.count(placeholder) != 1:
        raise ValueError("shared source must contain the platform placeholder exactly once")

    outputs = manifest.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        raise ValueError("manifest outputs must be a non-empty array")

    rendered: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_outputs: set[Path] = set()
    for entry in outputs:
        if not isinstance(entry, dict):
            raise ValueError("output entries must be JSON objects")
        entry_id = str(entry.get("id") or "").strip()
        if not entry_id or entry_id in seen_ids:
            raise ValueError(f"invalid or duplicate output id: {entry_id or 'missing'}")
        preamble_path = _repo_path(root, entry.get("preamble"))
        platform_path = _repo_path(root, entry.get("platform"))
        output_path = _repo_path(root, entry.get("output"))
        if output_path in seen_outputs:
            raise ValueError(f"duplicate output path: {output_path}")
        preamble = _read_fragment(preamble_path).rstrip("\n")
        platform = _read_fragment(platform_path).rstrip("\n")
        content = preamble + "\n\n" + shared.replace(placeholder, platform) + "\n"
        rendered.append(
            {
                "id": entry_id,
                "output_path": output_path,
                "content": content.encode("utf-8"),
            }
        )
        seen_ids.add(entry_id)
        seen_outputs.add(output_path)
    return rendered


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode if path.exists() else 0o644
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build(*, root: Path, manifest_path: Path, write: bool) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    rendered = render_outputs(root=root, manifest=manifest)
    results: list[dict[str, Any]] = []
    for item in rendered:
        output_path = item["output_path"]
        expected = item["content"]
        actual = _read_fragment(output_path).encode("utf-8") if output_path.is_file() else None
        changed = actual != expected
        if changed and write:
            _atomic_write(output_path, expected)
        results.append(
            {
                "id": item["id"],
                "output": str(output_path.relative_to(root)).replace("\\", "/"),
                "status": "updated" if changed and write else "drift" if changed else "current",
                "expected_sha256": hashlib.sha256(expected).hexdigest(),
                "actual_sha256": hashlib.sha256(actual).hexdigest() if actual is not None else None,
            }
        )
    changed_count = sum(item["status"] in {"updated", "drift"} for item in results)
    return {
        "status": "applied" if write and changed_count else "pass" if not changed_count else "fail",
        "mode": "write" if write else "check",
        "manifest_path": str(manifest_path.resolve(strict=False)).replace("\\", "/"),
        "changed_count": changed_count,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build committed Codex and Claude global rules from canonical sources."
    )
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--check", action="store_true", help="Check outputs without writing.")
    parser.add_argument("--write", action="store_true", help="Atomically update drifted outputs.")
    args = parser.parse_args(argv)
    if args.check and args.write:
        parser.error("--check and --write are mutually exclusive")
    manifest_path = Path(args.manifest_path).resolve(strict=False)
    result = build(root=ROOT, manifest_path=manifest_path, write=args.write)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["status"] in {"pass", "applied"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
