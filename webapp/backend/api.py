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
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List

from services.utils import mqtt_topics


class ApiHandler(BaseHTTPRequestHandler):
    """HTTP handler for the scaffold API."""

    server_version = "KITTApi/0.1"

    def do_GET(self) -> None:  # noqa: N802 - stdlib method name
        if self.path.rstrip("/") == "/trains":
            payload = {"trains": [{"id": "train-1", "status": "idle"}]}
            self._send_json(HTTPStatus.OK, payload)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        if self.path.rstrip("/") == "/order":
            payload = self._read_json()
            order_id = payload.get("order_id", "order-001")
            response = {
                "order_id": order_id,
                "topic": mqtt_topics.ORDER_NEW,
                "status": "accepted",
            }
            self._send_json(HTTPStatus.ACCEPTED, response)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def log_message(self, format: str, *args: object) -> None:
        logging.getLogger("kitt.webapp").info(format, *args)

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
