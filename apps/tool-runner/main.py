from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.tool_runner import execute_governed_command


def main() -> int:
    parser = argparse.ArgumentParser(description="Tool-runner worker scaffold.")
    parser.add_argument("--command", required=True)
    parser.add_argument("--cwd", default=str(ROOT))
    args = parser.parse_args()

    result = execute_governed_command(command=args.command, cwd=args.cwd)
    print(
        json.dumps(
            {
                "command": result.command,
                "exit_code": result.exit_code,
                "output": result.output,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
