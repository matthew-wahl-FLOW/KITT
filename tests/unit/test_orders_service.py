"""Unit tests for order service storage and stats."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from services.orders.api import OrderService
from services.orders.storage import OrderStorage


class TestOrderService(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "orders.db"
        self.storage = OrderStorage(db_path=self.db_path)
        self.service = OrderService(storage=self.storage)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_and_update_order(self) -> None:
        order = self.service.create_order("alice", {"rfid": "tag-1"})
        self.assertEqual(order.user_id, "alice")
        self.assertEqual(order.status, "requested")
        self.assertEqual(order.metadata["rfid"], "tag-1")

        updated = self.service.update_status(order.order_id, "in_progress")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "in_progress")

    def test_stats_weekly_and_all_time(self) -> None:
        order = self.service.create_order("bob")
        self.service.update_status(order.order_id, "delivered")

        week_stats = self.service.get_stats(now=datetime.now(timezone.utc))
        self.assertEqual(week_stats["weekly_delivered"], 1)
        self.assertEqual(week_stats["all_time_delivered"], 1)

        past_time = datetime.now(timezone.utc) - timedelta(days=10)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE orders SET timestamp = ? WHERE id = ?",
                (past_time.isoformat(), order.order_id),
            )
            conn.commit()

        stats = self.service.get_stats(now=datetime.now(timezone.utc))
        self.assertEqual(stats["weekly_delivered"], 0)
        self.assertEqual(stats["all_time_delivered"], 1)

    def test_history_ordering(self) -> None:
        first = self.service.create_order("carol")
        second = self.service.create_order("dave")
        history = self.service.get_history(limit=5)
        self.assertEqual(history[0].order_id, second.order_id)
        self.assertEqual(history[1].order_id, first.order_id)


if __name__ == "__main__":
    unittest.main()
