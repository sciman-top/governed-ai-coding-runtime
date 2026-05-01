from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "docs" / "change-evidence" / "repo-map-context-artifact.json"


def main() -> int:
    build_repo_map_context_artifact = _load_builder()

    result = build_repo_map_context_artifact(
        repo_root=ROOT,
        strategy_path=ROOT / ".governed-ai" / "repo-map-context-shaping.json",
        output_path=OUTPUT_PATH,
    )

    errors: list[str] = []
    if result["decision"] == "retire":
        errors.append("repo-map artifact retired unexpectedly")
    for required in result["required_governance_files"]:
        if required not in result["selected_files"]:
            errors.append(f"missing required governance file: {required}")
    if result["metrics"]["file_selection_accuracy"] < 1.0:
        errors.append("file_selection_accuracy below 1.0")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _load_builder():
    script_path = ROOT / "scripts" / "build-repo-map-context-artifact.py"
    spec = importlib.util.spec_from_file_location("build_repo_map_context_artifact_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_repo_map_context_artifact


if __name__ == "__main__":
    raise SystemExit(main())
