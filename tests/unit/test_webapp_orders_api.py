"""Unit tests for webapp order API helpers."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

API_PATH = Path(__file__).resolve().parents[2] / "webapp" / "backend" / "api.py"
SPEC = importlib.util.spec_from_file_location("webapp_api", API_PATH)
API = importlib.util.module_from_spec(SPEC)
if SPEC is None or SPEC.loader is None:
    raise ImportError("Unable to load webapp API module")
SPEC.loader.exec_module(API)


class TestWebappOrdersApi(unittest.TestCase):
    def test_order_service_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "orders.db"
            service = API.build_order_service(db_path)
            order = service.create_order("alice")
            self.assertEqual(order.user_id, "alice")
            stats = service.get_stats()
            self.assertEqual(stats["all_time_delivered"], 0)


if __name__ == "__main__":
    unittest.main()
