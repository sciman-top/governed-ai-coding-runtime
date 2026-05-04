from __future__ import annotations

import argparse
import json
from pathlib import Path

from lib.target_repo_managed_assets import inspect_managed_assets, load_json_object


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect target-repo managed asset ownership without modifying files.")
    parser.add_argument("--target-repo", required=True, help="Target repository root.")
    parser.add_argument("--baseline-path", default=str(DEFAULT_BASELINE_PATH), help="Governance baseline JSON path.")
    parser.add_argument(
        "--candidate-path",
        action="append",
        default=[],
        help="Repo-relative path to classify. Can be repeated. Defaults to known managed paths and managed roots.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    baseline_path = Path(args.baseline_path).resolve(strict=False)
    baseline = load_json_object(baseline_path)
    payload = inspect_managed_assets(
        target_repo=Path(args.target_repo),
        baseline=baseline,
        repo_root=ROOT,
        candidate_paths=list(args.candidate_path or []),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 2 if payload.get("status") == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
