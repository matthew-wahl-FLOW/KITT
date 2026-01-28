# Document the purpose of this unit test module.
"""Unit tests for webapp order API helpers."""

# Allow future annotations for type hints in tests.
from __future__ import annotations

# Import utilities for dynamic module loading.
import importlib.util
# Import tempfile to create isolated directories for test databases.
import tempfile
# Import unittest for the test framework.
import unittest
# Import Path for filesystem path management.
from pathlib import Path

# Resolve the backend API module path for direct import.
API_PATH = Path(__file__).resolve().parents[2] / "webapp" / "backend" / "api.py"
# Build an import specification for the backend API module.
SPEC = importlib.util.spec_from_file_location("webapp_api", API_PATH)
# Create a module object from the import specification.
API = importlib.util.module_from_spec(SPEC)
# Fail fast if the module cannot be loaded.
if SPEC is None or SPEC.loader is None:
    # Raise an import error so the test suite fails clearly.
    raise ImportError("Unable to load webapp API module")
# Execute the module so its symbols are available.
SPEC.loader.exec_module(API)


# Validate that the API can build an order service with overrides.
class TestWebappOrdersApi(unittest.TestCase):
    # Verify the order service uses the provided DB path.
    def test_order_service_override(self) -> None:
        # Create a temporary directory for the test database.
        with tempfile.TemporaryDirectory() as temp_dir:
            # Build a database path inside the temp directory.
            db_path = Path(temp_dir) / "orders.db"
            # Build an OrderService with the override path.
            service = API.build_order_service(db_path)
            # Create a placeholder order to confirm persistence works.
            order = service.create_order("alice")
            # Assert that the stored order has the expected user ID.
            self.assertEqual(order.user_id, "alice")
            # Fetch aggregate stats for the service.
            stats = service.get_stats()
            # Assert that no deliveries are recorded by default.
            self.assertEqual(stats["all_time_delivered"], 0)


# Run the tests when executing this module directly.
if __name__ == "__main__":
    # Invoke unittest to run the test module.
    unittest.main()
