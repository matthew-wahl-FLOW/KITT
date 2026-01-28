# Document the purpose of this unit test module.
# Define the module docstring for the webapp API tests.
"""Unit tests for webapp API helper functions."""

# Import utilities for dynamic module loading.
import importlib.util
# Import JSON utilities for test data validation.
import json
# Import tempfile to create isolated directories for test files.
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


# Validate helper functions used by the webapp backend.
class TestWebappApiHelpers(unittest.TestCase):
    # Verify the JSON loader returns defaults for missing files.
    def test_load_json_default(self) -> None:
        # Create a temporary directory for the missing file case.
        with tempfile.TemporaryDirectory() as temp_dir:
            # Build a missing file path inside the temp directory.
            missing = Path(temp_dir) / "missing.json"
            # Load JSON and verify the default payload is returned.
            payload = API._load_json(missing, {"staff": []})
            # Assert the default payload matches expectations.
            self.assertEqual(payload, {"staff": []})

    # Verify the leaderboard update logic.
    def test_update_leaderboard(self) -> None:
        # Create a temporary directory for leaderboard storage.
        with tempfile.TemporaryDirectory() as temp_dir:
            # Build the leaderboard file path.
            path = Path(temp_dir) / "leaderboard.json"
            # Create an entry for Alice and validate the result.
            entries = API._update_leaderboard(path, "Alice", 2)
            # Confirm Alice is first with the correct count.
            self.assertEqual(entries[0]["name"], "Alice")
            # Confirm Alice's count matches the increment.
            self.assertEqual(entries[0]["count"], 2)

            # Add Bob with a higher count to reorder the leaderboard.
            entries = API._update_leaderboard(path, "Bob", 5)
            # Confirm Bob is now leading.
            self.assertEqual(entries[0]["name"], "Bob")
            # Confirm Bob's count matches the increment.
            self.assertEqual(entries[0]["count"], 5)

            # Increment Alice again to move her count.
            entries = API._update_leaderboard(path, "Alice", 4)
            # Confirm Alice is back at the top.
            self.assertEqual(entries[0]["name"], "Alice")
            # Confirm Alice's total count reflects the new update.
            self.assertEqual(entries[0]["count"], 6)

            # Read back the stored JSON for verification.
            data = json.loads(path.read_text(encoding="utf-8"))
            # Assert the leaderboard has both entries stored.
            self.assertEqual(len(data["leaderboard"]), 2)


# Run the tests when executing this module directly.
if __name__ == "__main__":
    # Invoke unittest to run the test module.
    unittest.main()
