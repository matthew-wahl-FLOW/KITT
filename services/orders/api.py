# Document the purpose of the order service API module.
"""Order service API surface.

Overview: Provides business logic for creating and querying orders.
Details: Acts as the single source of truth for order state.
"""

# Enable postponed evaluation so annotations can use forward references.
from __future__ import annotations

# Import datetime for stats window calculations.
from datetime import datetime
# Import Path for optional storage overrides.
from pathlib import Path
# Import typing helpers for structured data.
from typing import Any, Dict, List, Optional

# Import order models and storage helpers for persistence.
from services.orders.models import ALLOWED_STATUSES, OrderCreateRequest, OrderRecord
# Import storage layer and rolling window helper for stats.
from services.orders.storage import OrderStorage, rolling_week_start


# Coordinate order creation, updates, and stats for the web backend.
class OrderService:
    # Describe the order service class for maintainers.
    """Order service coordinating storage and domain logic."""

    # Initialize the order service with storage overrides.
    def __init__(
        self,
        storage: OrderStorage | None = None,
        db_path: Path | None = None,
    ) -> None:
        # Use provided storage or create a new SQLite-backed storage layer.
        self._storage = storage or OrderStorage(db_path)

    # Create a new order record.
    def create_order(self, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> OrderRecord:
        # Describe the order creation behavior.
        """Create a new order with requested status."""
        # Build a request object that captures metadata for persistence.
        request = OrderCreateRequest(user_id=user_id, metadata=metadata or {})
        # Store the order and return the persisted record.
        return self._storage.create_order(request)

    # Update order status and metadata.
    def update_status(
        self,
        order_id: int,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[OrderRecord]:
        # Describe the status update behavior.
        """Update status for an order."""
        # Reject unknown statuses to keep state transitions valid.
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        # Delegate to storage and return the updated record if found.
        return self._storage.update_order_status(order_id, status, metadata=metadata)

    # Fetch recent order history.
    def get_history(self, limit: int = 100) -> List[OrderRecord]:
        # Describe the history retrieval behavior.
        """Return recent order history."""
        # Return a list of recent orders for dashboards and audits.
        return self._storage.list_orders(limit=limit)

    # Fetch weekly and all-time delivery stats.
    def get_stats(self, now: datetime | None = None) -> Dict[str, int]:
        # Describe the stats retrieval behavior.
        """Return weekly and all-time delivered counts."""
        # Compute the rolling week start based on the provided time.
        week_start = rolling_week_start(now)
        # Return counts used by UI leaderboards.
        return {
            # Provide the count for the rolling week window.
            "weekly_delivered": self._storage.delivered_count_since(week_start),
            # Provide the total delivered count for all time.
            "all_time_delivered": self._storage.delivered_count(),
        }

    # Expose the database path for diagnostics.
    @property
    def db_path(self) -> str:
        # Describe the database path property.
        """Return the underlying SQLite path."""
        # Return the database path as a string for diagnostics.
        return str(self._storage.db_path)
