# Provide module documentation for the orders package.
"""Order service package."""

# Import the public OrderService entry point for callers.
from services.orders.api import OrderService
# Import the OrderRecord model for consumers that need typed records.
from services.orders.models import OrderRecord

# Define the public API for the orders package.
__all__ = ["OrderService", "OrderRecord"]
