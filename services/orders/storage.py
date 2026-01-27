"""SQLite storage for order persistence.

Overview: Encapsulates SQLite access for creating and querying orders.
Details: Provides initialization, writes, and read-only queries.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional

from services.orders.models import ALLOWED_STATUSES, OrderCreateRequest, OrderRecord

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "orders.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL,
    metadata TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_timestamp ON orders(timestamp);
"""


class OrderStorage:
    """SQLite-backed order storage."""

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or DEFAULT_DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    @property
    def db_path(self) -> Path:
        """Return the SQLite database path."""
        return self._db_path

    def create_order(self, request: OrderCreateRequest) -> OrderRecord:
        """Create a new order record."""
        timestamp = datetime.now(timezone.utc)
        metadata = json.dumps(request.metadata or {})
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO orders (timestamp, user_id, status, metadata) VALUES (?, ?, ?, ?)",
                (timestamp.isoformat(), request.user_id, "requested", metadata),
            )
            order_id = int(cursor.lastrowid)
        return OrderRecord(
            order_id=order_id,
            timestamp=timestamp,
            user_id=request.user_id,
            status="requested",
            metadata=request.metadata or {},
        )

    def update_order_status(
        self,
        order_id: int,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[OrderRecord]:
        """Update the status (and optional metadata) for an order."""
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        existing = self.get_order(order_id)
        if not existing:
            return None
        new_metadata = existing.metadata
        if metadata is not None:
            new_metadata = metadata
        with self._connect() as conn:
            conn.execute(
                "UPDATE orders SET status = ?, metadata = ? WHERE id = ?",
                (status, json.dumps(new_metadata), order_id),
            )
        return OrderRecord(
            order_id=existing.order_id,
            timestamp=existing.timestamp,
            user_id=existing.user_id,
            status=status,
            metadata=new_metadata,
        )

    def get_order(self, order_id: int) -> Optional[OrderRecord]:
        """Fetch a single order by id."""
        rows = self._fetch_orders("SELECT * FROM orders WHERE id = ?", (order_id,))
        return rows[0] if rows else None

    def list_orders(self, limit: int = 100) -> List[OrderRecord]:
        """Return recent orders."""
        return self._fetch_orders(
            "SELECT * FROM orders ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )

    def delivered_count(self) -> int:
        """Return count of delivered orders (all time)."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM orders WHERE status = ?",
                ("delivered",),
            )
            result = cursor.fetchone()
        return int(result[0] if result else 0)

    def delivered_count_since(self, since: datetime) -> int:
        """Return delivered count since the given timestamp (inclusive)."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM orders WHERE status = ? AND timestamp >= ?",
                ("delivered", since.isoformat()),
            )
            result = cursor.fetchone()
        return int(result[0] if result else 0)

    def _fetch_orders(
        self,
        query: str,
        params: Iterable[Any],
    ) -> List[OrderRecord]:
        with self._connect() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        return [self._row_to_record(row) for row in rows]

    @staticmethod
    def _row_to_record(row: sqlite3.Row | tuple) -> OrderRecord:
        order_id, timestamp_raw, user_id, status, metadata_raw = row
        timestamp = datetime.fromisoformat(timestamp_raw)
        metadata = json.loads(metadata_raw) if metadata_raw else {}
        return OrderRecord(
            order_id=int(order_id),
            timestamp=timestamp,
            user_id=str(user_id),
            status=str(status),
            metadata=metadata,
        )


def rolling_week_start(now: datetime | None = None) -> datetime:
    """Return rolling 7-day window start in UTC."""
    now_utc = now or datetime.now(timezone.utc)
    return now_utc - timedelta(days=7)
