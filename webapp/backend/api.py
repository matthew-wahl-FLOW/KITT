"""Webapp backend API scaffold.

Overview: Provides placeholder HTTP handlers for orders and train status.
Details: Minimal stdlib HTTP server with JSON responses and logging.

Missing info for further development:
- Inputs: Authentication mechanism, request schemas, user mapping.
- Outputs: Response schemas and error codes.
- Actions: MQTT publish/subscribe integration and state persistence.
- Methods: Authorization rules, rate limits, telemetry ingestion.
"""

from __future__ import annotations

import argparse
import json
import logging
import mimetypes
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List

try:
    from services.utils import mqtt_topics
except ModuleNotFoundError:  # pragma: no cover - allow direct script execution
    REPO_ROOT = Path(__file__).resolve().parents[2]
    sys.path.append(str(REPO_ROOT))
    from services.utils import mqtt_topics

WEBAPP_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = WEBAPP_DIR / "frontend"
DATA_DIR = Path(__file__).resolve().parent / "data"
STAFF_FILE = DATA_DIR / "staff_roster.json"
WEEKLY_LEADERBOARD_FILE = DATA_DIR / "leaderboard_weekly.json"
ALL_TIME_LEADERBOARD_FILE = DATA_DIR / "leaderboard_all_time.json"


def _load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _update_leaderboard(path: Path, user: str, quantity: int) -> List[Dict[str, Any]]:
    data = _load_json(path, {"leaderboard": []})
    leaderboard = data.get("leaderboard", [])
    entry = next(
        (item for item in leaderboard if item.get("name", "").lower() == user.lower()),
        None,
    )
    if entry:
        entry["count"] = int(entry.get("count", 0)) + quantity
    else:
        leaderboard.append({"name": user, "count": quantity})
    leaderboard.sort(key=lambda item: int(item.get("count", 0)), reverse=True)
    data["leaderboard"] = leaderboard
    _write_json(path, data)
    return leaderboard


class ApiHandler(BaseHTTPRequestHandler):
    """HTTP handler for the scaffold API."""

    server_version = "KITTApi/0.1"

    def do_GET(self) -> None:  # noqa: N802 - stdlib method name
        path = self.path.split("?", 1)[0].rstrip("/")
        if self._maybe_serve_frontend(path):
            return
        if path == "/trains":
            payload = {"trains": [{"id": "train-1", "status": "idle"}]}
            self._send_json(HTTPStatus.OK, payload)
            return
        if path == "/staff":
            self._send_json(HTTPStatus.OK, _load_json(STAFF_FILE, {"staff": []}))
            return
        if path == "/leaderboard/weekly":
            self._send_json(
                HTTPStatus.OK,
                _load_json(WEEKLY_LEADERBOARD_FILE, {"leaderboard": []}),
            )
            return
        if path in ("/leaderboard/all-time", "/leaderboard/all_time"):
            self._send_json(
                HTTPStatus.OK,
                _load_json(ALL_TIME_LEADERBOARD_FILE, {"leaderboard": []}),
            )
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        path = self.path.split("?", 1)[0].rstrip("/")
        if path == "/order":
            payload = self._read_json()
            order_id = payload.get("order_id", "order-001")
            user = payload.get("user", "unknown")
            response = {
                "order_id": order_id,
                "user": user,
                "topic": mqtt_topics.ORDER_NEW,
                "status": "accepted",
            }
            self._send_json(HTTPStatus.ACCEPTED, response)
            return
        if path == "/staff":
            payload = self._read_json()
            name = str(payload.get("name", "")).strip()
            if not name:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_name"})
                return
            roster = _load_json(STAFF_FILE, {"staff": []})
            staff = roster.get("staff", [])
            if not any(entry.lower() == name.lower() for entry in staff):
                staff.append(name)
            roster["staff"] = staff
            _write_json(STAFF_FILE, roster)
            self._send_json(HTTPStatus.OK, roster)
            return
        if path == "/leaderboard/record":
            payload = self._read_json()
            user = str(payload.get("user", "")).strip()
            try:
                quantity = int(payload.get("quantity", 0))
            except (TypeError, ValueError):
                quantity = 0
            if not user or quantity <= 0:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_order"})
                return
            weekly = _update_leaderboard(WEEKLY_LEADERBOARD_FILE, user, quantity)
            all_time = _update_leaderboard(ALL_TIME_LEADERBOARD_FILE, user, quantity)
            self._send_json(HTTPStatus.OK, {"weekly": weekly, "all_time": all_time})
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def log_message(self, format: str, *args: object) -> None:
        logging.getLogger("kitt.webapp").info(format, *args)

    def _maybe_serve_frontend(self, path: str) -> bool:
        if path in ("", "/"):
            request_path = "dashboard_stub.html"
        elif path.startswith("/images/"):
            request_path = path.lstrip("/")
        elif path == "/dashboard_stub.html":
            request_path = "dashboard_stub.html"
        else:
            return False

        file_path = (FRONTEND_DIR / request_path).resolve()
        if FRONTEND_DIR not in file_path.parents and file_path != FRONTEND_DIR:
            return False
        if not file_path.exists() or not file_path.is_file():
            return False

        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        body = file_path.read_bytes()
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return True

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _send_json(self, status: HTTPStatus, payload: Dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI usage."""
    parser = argparse.ArgumentParser(description="KITT Web API (scaffold)")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8080, help="Bind port")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser


def main(argv: List[str] | None = None) -> int:
    """Run the API scaffold server."""
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    server = HTTPServer((args.host, args.port), ApiHandler)
    logging.getLogger("kitt.webapp").info("Serving on http://%s:%s", args.host, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.getLogger("kitt.webapp").info("Shutting down")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
