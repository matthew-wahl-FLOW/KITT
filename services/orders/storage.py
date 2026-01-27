# Document the purpose of the SQLite order storage module.
"""SQLite storage for order persistence.

Overview: Encapsulates SQLite access for creating and querying orders.
Details: Provides initialization, writes, and read-only queries.
"""

# Enable postponed evaluation so annotations can use forward references.
from __future__ import annotations

# Import JSON helpers for storing metadata in SQLite.
import json
# Import SQLite driver for lightweight embedded storage on the Pi.
import sqlite3
# Import context manager helper for safe connection lifecycle handling.
from contextlib import contextmanager
# Import datetime helpers for timestamps and rolling windows.
from datetime import datetime, timedelta, timezone
# Import Path for filesystem paths used by the database file.
from pathlib import Path
# Import typing helpers for structured data.
from typing import Any, Dict, Iterable, Iterator, List, Optional

# Import order models and allowed status values.
from services.orders.models import ALLOWED_STATUSES, OrderCreateRequest, OrderRecord

# Define the default database path under the services data directory.
DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "orders.db"

# Define the SQLite schema for order storage and indexing.
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


# Encapsulate SQLite-backed order storage for the backend and services.
class OrderStorage:
    # Describe the order storage class for maintainers.
    """SQLite-backed order storage."""

    # Initialize storage with an optional database path.
    def __init__(self, db_path: Path | None = None) -> None:
        # Use provided database path or fall back to the default location.
        self._db_path = db_path or DEFAULT_DB_PATH
        # Ensure the data directory exists so SQLite can create the file.
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        # Initialize the schema so tables are ready for reads and writes.
        self._initialize_schema()

    # Create database tables if they are missing.
    def _initialize_schema(self) -> None:
        # Open a connection and execute the schema definitions.
        with self._connect() as conn:
            # Execute schema statements to create tables and indexes.
            conn.executescript(SCHEMA_SQL)

    # Provide a managed SQLite connection.
    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        # Create a SQLite connection to the database file.
        conn = sqlite3.connect(self._db_path)
        try:
            # Yield the connection to the caller for queries.
            yield conn
            # Commit any pending changes once the caller finishes.
            conn.commit()
        finally:
            # Close the connection to release file handles.
            conn.close()

    # Expose the database path.
    @property
    def db_path(self) -> Path:
        # Describe the database path property.
        """Return the SQLite database path."""
        # Expose the database path for diagnostics and tests.
        return self._db_path

    # Create and persist a new order record.
    def create_order(self, request: OrderCreateRequest) -> OrderRecord:
        # Describe the order creation behavior.
        """Create a new order record."""
        # Capture the time the order is created for auditing and sorting.
        timestamp = datetime.now(timezone.utc)
        # Serialize metadata to JSON for storage in SQLite.
        metadata = json.dumps(request.metadata or {})
        # Open a connection to store the new order.
        with self._connect() as conn:
            # Insert the order into the database with default status requested.
            cursor = conn.execute(
                "INSERT INTO orders (timestamp, user_id, status, metadata) VALUES (?, ?, ?, ?)",
                (timestamp.isoformat(), request.user_id, "requested", metadata),
            )
            # Read back the generated order ID from SQLite.
            order_id = int(cursor.lastrowid)
        # Return the in-memory representation for immediate API response.
        return OrderRecord(
            # Provide the generated order ID to the caller.
            order_id=order_id,
            # Provide the creation timestamp for UI display.
            timestamp=timestamp,
            # Provide the user ID who placed the order.
            user_id=request.user_id,
            # Provide the initial status used by the orchestrator.
            status="requested",
            # Provide the metadata as a decoded dictionary.
            metadata=request.metadata or {},
        )

    # Update the status and metadata for an existing order.
    def update_order_status(
        self,
        order_id: int,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[OrderRecord]:
        # Describe the order update behavior.
        """Update the status (and optional metadata) for an order."""
        # Ensure the new status is one of the allowed values for safety.
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        # Fetch the current record so we can preserve existing values.
        existing = self.get_order(order_id)
        # Return None if the order does not exist in storage.
        if not existing:
            return None
        # Start with the current metadata values.
        new_metadata = existing.metadata
        # Replace metadata only if new metadata was provided.
        if metadata is not None:
            new_metadata = metadata
        # Open a connection to update the order.
        with self._connect() as conn:
            # Update the order status and metadata in SQLite.
            conn.execute(
                "UPDATE orders SET status = ?, metadata = ? WHERE id = ?",
                (status, json.dumps(new_metadata), order_id),
            )
        # Return the updated record for API responses and callers.
        return OrderRecord(
            # Preserve the existing order ID.
            order_id=existing.order_id,
            # Preserve the original timestamp.
            timestamp=existing.timestamp,
            # Preserve the original user ID.
            user_id=existing.user_id,
            # Use the updated status provided by the caller.
            status=status,
            # Use the updated metadata that was persisted.
            metadata=new_metadata,
        )

    # Fetch a single order by ID.
    def get_order(self, order_id: int) -> Optional[OrderRecord]:
        # Describe the order fetch behavior.
        """Fetch a single order by id."""
        # Query for the specific order ID in the database.
        rows = self._fetch_orders("SELECT * FROM orders WHERE id = ?", (order_id,))
        # Return the first row if present, otherwise return None.
        return rows[0] if rows else None

    # List recent orders in descending timestamp order.
    def list_orders(self, limit: int = 100) -> List[OrderRecord]:
        # Describe the history listing behavior.
        """Return recent orders."""
        # Fetch the most recent orders sorted by timestamp descending.
        return self._fetch_orders(
            "SELECT * FROM orders ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )

    # Count delivered orders across all time.
    def delivered_count(self) -> int:
        # Describe the delivered count behavior.
        """Return count of delivered orders (all time)."""
        # Open a connection to count delivered orders.
        with self._connect() as conn:
            # Count orders marked as delivered for reporting dashboards.
            cursor = conn.execute(
                "SELECT COUNT(*) FROM orders WHERE status = ?",
                ("delivered",),
            )
            # Read the count from the database result.
            result = cursor.fetchone()
        # Return zero if no rows exist yet.
        return int(result[0] if result else 0)

    # Count delivered orders since a given time.
    def delivered_count_since(self, since: datetime) -> int:
        # Describe the delivered count since behavior.
        """Return delivered count since the given timestamp (inclusive)."""
        # Open a connection to count delivered orders.
        with self._connect() as conn:
            # Count delivered orders since the provided start time.
            cursor = conn.execute(
                "SELECT COUNT(*) FROM orders WHERE status = ? AND timestamp >= ?",
                ("delivered", since.isoformat()),
            )
            # Read the count from the database result.
            result = cursor.fetchone()
        # Return zero if no rows exist in the interval.
        return int(result[0] if result else 0)

    # Run a query and convert rows to OrderRecord instances.
    def _fetch_orders(
        self,
        query: str,
        params: Iterable[Any],
    ) -> List[OrderRecord]:
        # Execute a read-only query and return the decoded order records.
        with self._connect() as conn:
            # Run the query with parameters to avoid SQL injection.
            cursor = conn.execute(query, params)
            # Fetch all rows from the result set.
            rows = cursor.fetchall()
        # Convert each row into an OrderRecord for callers.
        return [self._row_to_record(row) for row in rows]

    # Convert a SQLite row into an OrderRecord.
    @staticmethod
    def _row_to_record(row: sqlite3.Row | tuple) -> OrderRecord:
        # Unpack the SQLite row into fields by position.
        order_id, timestamp_raw, user_id, status, metadata_raw = row
        # Parse the stored ISO timestamp into a datetime.
        timestamp = datetime.fromisoformat(timestamp_raw)
        # Decode metadata JSON or fall back to an empty dict.
        metadata = json.loads(metadata_raw) if metadata_raw else {}
        # Return the reconstructed OrderRecord object.
        return OrderRecord(
            # Cast the ID to int for consistent typing.
            order_id=int(order_id),
            # Provide the parsed timestamp.
            timestamp=timestamp,
            # Provide the user ID as a string.
            user_id=str(user_id),
            # Provide the status as a string.
            status=str(status),
            # Provide the metadata dictionary.
            metadata=metadata,
        )


# Compute the start of the rolling 7-day window for weekly stats.
def rolling_week_start(now: datetime | None = None) -> datetime:
    # Describe the rolling week start behavior.
    """Return rolling 7-day window start in UTC."""
    # Use the provided time or default to the current UTC time.
    now_utc = now or datetime.now(timezone.utc)
    # Subtract seven days to get the rolling window start.
    return now_utc - timedelta(days=7)
