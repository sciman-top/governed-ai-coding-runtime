import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

try:
    from fastapi.testclient import TestClient
except ModuleNotFoundError:
    TestClient = None


def _load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@unittest.skipIf(TestClient is None, "service extras not installed")
class HttpControlPlaneTests(unittest.TestCase):
    def test_health_endpoint_returns_status(self) -> None:
        module = _load_module("apps/control-plane/http_app.py", "http_control_plane")
        client = TestClient(module.create_app(repo_root=ROOT))

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_operator_endpoint_returns_adapter_events(self) -> None:
        module = _load_module("apps/control-plane/http_app.py", "http_control_plane_operator")
        client = TestClient(module.create_app(repo_root=ROOT))

        response = client.post("/operator", json={"action": "inspect_adapter_events", "task_id": "task-http"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("payload", response.json())
        self.assertIn("adapter_events", response.json()["payload"])

    def test_operator_adapter_events_flow_through_http_with_injected_sink(self) -> None:
        module = _load_module("apps/control-plane/http_app.py", "http_control_plane_e2e")

        class _Sink:
            def __init__(self):
                self.rows = [
                    {
                        "task_id": "task-http",
                        "event_type": "adapter_tool_call",
                        "payload": {"tool": "apply_patch"},
                    }
                ]

            def list_events(self, *, task_id: str):
                return [row for row in self.rows if row["task_id"] == task_id]

        client = TestClient(module.create_app(repo_root=ROOT, adapter_event_sink=_Sink()))
        response = client.post("/operator", json={"action": "inspect_adapter_events", "task_id": "task-http"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["payload"]["adapter_events"][0]["payload"]["tool"], "apply_patch")


if __name__ == "__main__":
    unittest.main()
