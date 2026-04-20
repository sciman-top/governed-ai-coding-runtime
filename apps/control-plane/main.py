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
    parser = argparse.ArgumentParser(description="Control-plane facade entrypoint.")
    parser.add_argument("--route", choices=["/session", "/operator", "/health"], default="/health")
    parser.add_argument("--payload-json", default="{}")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--task-root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve(strict=False)
    facade_module = _load_module(
        repo_root / "packages" / "agent-runtime" / "service_facade.py",
        "agent_runtime_service_facade",
    )
    app_module = _load_module(
        repo_root / "apps" / "control-plane" / "app.py",
        "control_plane_app",
    )
    tracer_module = _load_module(
        repo_root / "packages" / "observability" / "runtime_tracing.py",
        "runtime_tracing",
    )
    payload = json.loads(args.payload_json)
    tracer = tracer_module.RuntimeTracer()
    facade = facade_module.RuntimeServiceFacade(
        repo_root=repo_root,
        task_root=args.task_root,
        tracer=tracer,
    )
    app = app_module.ControlPlaneApplication(facade=facade)
    result = app.dispatch(route=args.route, payload=payload)
    result.setdefault("trace_event_count", len(tracer.events()))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
