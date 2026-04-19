from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


def _load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        msg = f"unable to load module: {path}"
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description="Workflow worker scaffold.")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--metadata-db", default=".runtime/service/metadata.db")
    parser.add_argument("--task-id", default="workflow-heartbeat")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve(strict=False)
    persistence = _load_module(repo_root / "packages" / "agent-runtime" / "persistence.py", "agent_runtime_persistence")
    store = persistence.SqliteMetadataStore(repo_root / args.metadata_db)
    record = store.upsert(
        namespace="workflow_worker",
        key=args.task_id,
        payload={"status": "heartbeat", "worker": "workflow-worker"},
    )
    print(json.dumps({"namespace": record.namespace, "key": record.key, "updated_at": record.updated_at}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
