# Document the purpose of this unit test module.
"""Unit tests for order service storage and stats."""

# Allow future annotations for type hints in tests.
from __future__ import annotations

# Import sqlite3 for direct timestamp manipulation in tests.
import sqlite3
# Import tempfile to create isolated directories for test databases.
import tempfile
# Import unittest for the test framework.
import unittest
# Import datetime helpers for time window testing.
from datetime import datetime, timedelta, timezone
# Import Path for filesystem path management.
from pathlib import Path

# Import the OrderService API for business logic tests.
from services.orders.api import OrderService
# Import OrderStorage for storage-level setup.
from services.orders.storage import OrderStorage


# Validate OrderService behaviors and statistics.
class TestOrderService(unittest.TestCase):
    # Initialize temporary storage before each test.
    def setUp(self) -> None:
        # Create a temporary directory for the SQLite database.
        self.temp_dir = tempfile.TemporaryDirectory()
        # Build the database path inside the temp directory.
        self.db_path = Path(self.temp_dir.name) / "orders.db"
        # Create storage with the isolated database.
        self.storage = OrderStorage(db_path=self.db_path)
        # Create the service using the isolated storage layer.
        self.service = OrderService(storage=self.storage)

    # Clean up temporary storage after each test.
    def tearDown(self) -> None:
        # Clean up the temporary directory after each test.
        self.temp_dir.cleanup()

    # Verify order creation and status updates.
    def test_create_and_update_order(self) -> None:
        # Create a new order with metadata.
        order = self.service.create_order("alice", {"rfid": "tag-1"})
        # Assert that the order user is stored correctly.
        self.assertEqual(order.user_id, "alice")
        # Assert that the order begins in requested status.
        self.assertEqual(order.status, "requested")
        # Assert that metadata is persisted in the record.
        self.assertEqual(order.metadata["rfid"], "tag-1")

        # Update the order status to in_progress.
        updated = self.service.update_status(order.order_id, "in_progress")
        # Assert the update returned a record.
        self.assertIsNotNone(updated)
        # Assert the status now reflects the update.
        self.assertEqual(updated.status, "in_progress")

    # Verify weekly and all-time stats calculations.
    def test_stats_weekly_and_all_time(self) -> None:
        # Create a new order to include in stats.
        order = self.service.create_order("bob")
        # Mark the order as delivered to count in stats.
        self.service.update_status(order.order_id, "delivered")

        # Calculate stats for the current time window.
        week_stats = self.service.get_stats(now=datetime.now(timezone.utc))
        # Assert weekly delivered count includes the order.
        self.assertEqual(week_stats["weekly_delivered"], 1)
        # Assert all-time delivered count includes the order.
        self.assertEqual(week_stats["all_time_delivered"], 1)

        # Create a timestamp outside the rolling week.
        past_time = datetime.now(timezone.utc) - timedelta(days=10)
        # Manually update the order timestamp to the past.
        with sqlite3.connect(self.db_path) as conn:
            # Apply the timestamp update in SQLite.
            conn.execute("UPDATE orders SET timestamp = ? WHERE id = ?", (past_time.isoformat(), order.order_id))
            # Commit the update so it persists.
            conn.commit()

        # Fetch stats after the timestamp adjustment.
        stats = self.service.get_stats(now=datetime.now(timezone.utc))
        # Assert weekly delivered count excludes the older order.
        self.assertEqual(stats["weekly_delivered"], 0)
        # Assert all-time delivered count still includes the order.
        self.assertEqual(stats["all_time_delivered"], 1)

    # Verify that history is returned in descending timestamp order.
    def test_history_ordering(self) -> None:
        # Create the first order to establish ordering.
        first = self.service.create_order("carol")
        # Create the second order to appear first in history.
        second = self.service.create_order("dave")
        # Fetch the order history with a limit.
        history = self.service.get_history(limit=5)
        # Assert the most recent order appears first.
        self.assertEqual(history[0].order_id, second.order_id)
        # Assert the earliest order appears second.
        self.assertEqual(history[1].order_id, first.order_id)


# Run the tests when executing this module directly.
if __name__ == "__main__":
    # Invoke unittest to run the test module.
    unittest.main()
