"""Unit tests for webapp API helper functions."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

API_PATH = Path(__file__).resolve().parents[2] / "webapp" / "backend" / "api.py"
SPEC = importlib.util.spec_from_file_location("webapp_api", API_PATH)
API = importlib.util.module_from_spec(SPEC)
if SPEC is None or SPEC.loader is None:
    raise ImportError("Unable to load webapp API module")
SPEC.loader.exec_module(API)


class TestWebappApiHelpers(unittest.TestCase):
    def test_load_json_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.json"
            payload = API._load_json(missing, {"staff": []})
            self.assertEqual(payload, {"staff": []})

    def test_update_leaderboard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "leaderboard.json"
            entries = API._update_leaderboard(path, "Alice", 2)
            self.assertEqual(entries[0]["name"], "Alice")
            self.assertEqual(entries[0]["count"], 2)

            entries = API._update_leaderboard(path, "Bob", 5)
            self.assertEqual(entries[0]["name"], "Bob")
            self.assertEqual(entries[0]["count"], 5)

            entries = API._update_leaderboard(path, "Alice", 4)
            self.assertEqual(entries[0]["name"], "Alice")
            self.assertEqual(entries[0]["count"], 6)

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(data["leaderboard"]), 2)


if __name__ == "__main__":
    unittest.main()
