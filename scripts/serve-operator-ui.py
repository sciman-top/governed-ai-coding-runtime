from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.operator_ui import write_runtime_snapshot_html
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeStatusStore


def main() -> int:
    output = ROOT / ".runtime" / "artifacts" / "operator-ui" / "index.html"
    snapshot = RuntimeStatusStore(ROOT / ".runtime" / "tasks", ROOT).snapshot()
    written = write_runtime_snapshot_html(snapshot, output)
    payload = {
        "maintenance_stage": snapshot.maintenance.stage,
        "output_path": written.relative_to(ROOT).as_posix(),
        "total_tasks": snapshot.total_tasks,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
