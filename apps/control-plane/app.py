"""Control-plane application wiring for service-shaped runtime APIs."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Any


def _load_route(path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        msg = f"unable to load route module: {path}"
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class ControlPlaneApplication:
    def __init__(self, *, facade: Any) -> None:
        self._facade = facade
        routes_dir = Path(__file__).resolve().parent / "routes"
        self._session_route = _load_route(routes_dir / "session.py", "control_plane_session_route")
        self._operator_route = _load_route(routes_dir / "operator.py", "control_plane_operator_route")

    def dispatch(self, *, route: str, payload: dict | None = None) -> dict:
        body = dict(payload or {})
        normalized_route = route.strip().lower()
        if normalized_route == "/session":
            return self._session_route.handle_session_route(self._facade, body)
        if normalized_route == "/operator":
            return self._operator_route.handle_operator_route(self._facade, body)
        if normalized_route == "/health":
            return self._facade.health()
        msg = f"unsupported route: {route}"
        raise ValueError(msg)
