"""Order domain models.

Overview: Defines order status values and the order record schema.
Details: Dataclasses are used for clean serialization between layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


ALLOWED_STATUSES = ("requested", "in_progress", "delivered", "cancelled")


@dataclass(frozen=True)
class OrderRecord:
    """Immutable order record stored in SQLite."""

    order_id: int
    timestamp: datetime
    user_id: str
    status: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the record for JSON responses."""
        timestamp = self.timestamp.astimezone(timezone.utc)
        return {
            "id": self.order_id,
            "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
            "user_id": self.user_id,
            "status": self.status,
            "metadata": self.metadata,
        }


@dataclass
class OrderCreateRequest:
    """Payload for new order creation."""

    user_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrderUpdateRequest:
    """Payload for updating an order status."""

    order_id: int
    status: str
    metadata: Optional[Dict[str, Any]] = None
