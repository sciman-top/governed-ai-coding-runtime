from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_TEMPLATE = ROOT / "schemas" / "examples" / "control-pack" / "minimum-governance-kernel.example.json"
GENERATED_PACK = ROOT / "schemas" / "control-packs" / "minimum-governance-kernel.control-pack.json"


def materialize_control_pack(*, repo_root: Path, apply: bool = False) -> dict:
    root = repo_root.resolve(strict=False)
    source_path = root / SOURCE_TEMPLATE.relative_to(ROOT)
    target_path = root / GENERATED_PACK.relative_to(ROOT)
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    written_files: list[str] = []
    if apply:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        written_files.append(target_path.relative_to(root).as_posix())

    return {
        "status": "pass",
        "mode": "apply" if apply else "dry_run",
        "source_template_ref": source_path.relative_to(root).as_posix(),
        "generated_pack_ref": target_path.relative_to(root).as_posix(),
        "mutation_allowed": apply,
        "guard": {
            "policy_auto_apply": False,
            "target_repo_sync": False,
            "push_or_merge": False,
            "fail_closed_if_missing": True,
        },
        "operation_count": 1,
        "operations": [
            {
                "operation": "write_runtime_consumable_control_pack",
                "path": target_path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "existing_file_behavior": "overwrite_from_source_template",
            }
        ],
        "written_files": written_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize runtime-consumable control packs from schema examples.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    result = materialize_control_pack(repo_root=Path(args.repo_root), apply=args.apply)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
