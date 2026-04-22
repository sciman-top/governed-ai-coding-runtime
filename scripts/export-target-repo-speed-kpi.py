from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.target_repo_speed_kpi import export_target_repo_speed_kpi
from governed_ai_coding_runtime_contracts.file_guard import atomic_write_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Export target-repo speed KPI snapshots from run evidence.")
    parser.add_argument(
        "--runs-root",
        default=str(ROOT / "docs" / "change-evidence" / "target-repo-runs"),
        help="Directory containing target-repo run JSON files.",
    )
    parser.add_argument("--window-kind", choices=["latest", "rolling"], default="latest")
    parser.add_argument("--window-size", type=int, default=10)
    parser.add_argument("--output", help="Optional output file path. Defaults to runs-root/kpi-<window-kind>.json.")
    args = parser.parse_args()

    snapshot = export_target_repo_speed_kpi(
        target_repo_runs_root=args.runs_root,
        window_kind=args.window_kind,
        window_size=args.window_size,
    )
    payload = snapshot.to_dict()
    output_path = Path(args.output) if args.output else Path(args.runs_root) / f"kpi-{args.window_kind}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(output_path, json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output_path.resolve(strict=False)), "record_count": snapshot.record_count}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
