"""Order service API surface.

Overview: Provides business logic for creating and querying orders.
Details: Acts as the single source of truth for order state.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from services.orders.models import ALLOWED_STATUSES, OrderCreateRequest, OrderRecord
from services.orders.storage import OrderStorage, rolling_week_start


class OrderService:
    """Order service coordinating storage and domain logic."""

    def __init__(
        self,
        storage: OrderStorage | None = None,
        db_path: Path | None = None,
    ) -> None:
        self._storage = storage or OrderStorage(db_path)

    def create_order(self, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> OrderRecord:
        """Create a new order with requested status."""
        request = OrderCreateRequest(user_id=user_id, metadata=metadata or {})
        return self._storage.create_order(request)

    def update_status(
        self,
        order_id: int,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[OrderRecord]:
        """Update status for an order."""
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        return self._storage.update_order_status(order_id, status, metadata=metadata)

    def get_history(self, limit: int = 100) -> List[OrderRecord]:
        """Return recent order history."""
        return self._storage.list_orders(limit=limit)

    def get_stats(self, now: datetime | None = None) -> Dict[str, int]:
        """Return weekly and all-time delivered counts."""
        week_start = rolling_week_start(now)
        return {
            "weekly_delivered": self._storage.delivered_count_since(week_start),
            "all_time_delivered": self._storage.delivered_count(),
        }

    @property
    def db_path(self) -> str:
        """Return the underlying SQLite path."""
        return str(self._storage.db_path)
