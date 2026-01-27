# Document the purpose of the webapp backend API module.
"""Webapp backend API scaffold.

Overview: Provides HTTP handlers for orders, staff, and train status.
Details: Minimal stdlib HTTP server with JSON responses and logging.

Missing info for further development:
- Inputs: Authentication mechanism, request schemas, user mapping.
- Outputs: Response schemas and error codes.
- Actions: MQTT publish/subscribe integration and state persistence.
- Methods: Authorization rules, rate limits, telemetry ingestion.
"""

# Enable postponed evaluation so annotations can use forward references.
from __future__ import annotations

# Import argparse for command-line argument parsing.
import argparse
# Import JSON utilities for request/response handling.
import json
# Import logging for server diagnostics.
import logging
# Import mimetypes for serving static assets.
import mimetypes
# Import sys for CLI exit handling.
import sys
# Import HTTPStatus for readable response codes.
from http import HTTPStatus
# Import HTTP server base classes.
from http.server import BaseHTTPRequestHandler, HTTPServer
# Import Path for filesystem paths.
from pathlib import Path
# Import typing helpers for JSON-like structures.
from typing import Any, Dict, List

# Attempt to import service modules from the installed package.
try:
    # Import the OrderService for order persistence.
    from services.orders.api import OrderService
    # Import MQTT topic helpers for response payloads.
    from services.utils import mqtt_topics
# Allow direct script execution by adjusting sys.path.
except ModuleNotFoundError:  # pragma: no cover - allow direct script execution
    # Resolve the repository root for local imports.
    REPO_ROOT = Path(__file__).resolve().parents[2]
    # Add the repo root to sys.path for module discovery.
    sys.path.append(str(REPO_ROOT))
    # Import the OrderService for order persistence.
    from services.orders.api import OrderService
    # Import MQTT topic helpers for response payloads.
    from services.utils import mqtt_topics

# Resolve the webapp directory for static asset lookup.
WEBAPP_DIR = Path(__file__).resolve().parents[1]
# Resolve the frontend asset directory.
FRONTEND_DIR = WEBAPP_DIR / "frontend"
# Resolve the data directory for JSON storage.
DATA_DIR = Path(__file__).resolve().parent / "data"
# Define the staff roster JSON file path.
STAFF_FILE = DATA_DIR / "staff_roster.json"
# Define the weekly leaderboard JSON file path.
WEEKLY_LEADERBOARD_FILE = DATA_DIR / "leaderboard_weekly.json"
# Define the all-time leaderboard JSON file path.
ALL_TIME_LEADERBOARD_FILE = DATA_DIR / "leaderboard_all_time.json"


# Store a shared OrderService instance for the API handler.
ORDER_SERVICE: OrderService | None = None


# Build an OrderService instance with optional DB path override.
def build_order_service(db_path: Path | None = None) -> OrderService:
    # Describe the service builder behavior.
    """Build an OrderService instance with optional DB path override."""
    # Return a service using the provided database path.
    return OrderService(db_path=db_path)


# Handle HTTP requests for the scaffold API.
class ApiHandler(BaseHTTPRequestHandler):
    # Describe the API handler class for maintainers.
    """HTTP handler for the scaffold API."""

    # Identify the server version for HTTP responses.
    server_version = "KITTApi/0.1"

    # Handle HTTP GET requests for API endpoints and static assets.
    def do_GET(self) -> None:  # noqa: N802 - stdlib method name
        # Normalize the request path without query parameters.
        path = self.path.split("?", 1)[0].rstrip("/")
        # Attempt to serve frontend assets before API routes.
        if self._maybe_serve_frontend(path):
            return
        # Serve a placeholder train list.
        if path == "/trains":
            # Build a placeholder train payload.
            payload = {"trains": [{"id": "train-1", "status": "idle"}]}
            # Send the payload as JSON.
            self._send_json(HTTPStatus.OK, payload)
            return
        # Serve the staff roster file.
        if path == "/staff":
            # Send the staff roster as JSON.
            self._send_json(HTTPStatus.OK, _load_json(STAFF_FILE, {"staff": []}))
            return
        # Serve the weekly leaderboard file.
        if path == "/leaderboard/weekly":
            # Send the weekly leaderboard as JSON.
            self._send_json(
                HTTPStatus.OK,
                _load_json(WEEKLY_LEADERBOARD_FILE, {"leaderboard": []}),
            )
            return
        # Serve the all-time leaderboard file.
        if path in ("/leaderboard/all-time", "/leaderboard/all_time"):
            # Send the all-time leaderboard as JSON.
            self._send_json(
                HTTPStatus.OK,
                _load_json(ALL_TIME_LEADERBOARD_FILE, {"leaderboard": []}),
            )
            return
        # Serve order history from the order service.
        if path == "/orders":
            # Fetch the order service instance.
            service = self._order_service()
            # Serialize order history to dictionaries.
            history = [record.to_dict() for record in service.get_history()]
            # Send the order history as JSON.
            self._send_json(HTTPStatus.OK, {"orders": history})
            return
        # Serve order stats from the order service.
        if path == "/orders/stats":
            # Fetch the order service instance.
            service = self._order_service()
            # Send the stats payload as JSON.
            self._send_json(HTTPStatus.OK, service.get_stats())
            return
        # Respond with not found for unknown endpoints.
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    # Handle HTTP POST requests for API endpoints.
    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        # Normalize the request path without query parameters.
        path = self.path.split("?", 1)[0].rstrip("/")
        # Handle new order requests.
        if path == "/order":
            # Read the JSON payload from the request.
            payload = self._read_json()
            # Normalize the user identifier.
            user = str(payload.get("user", "unknown")).strip() or "unknown"
            # Extract metadata if provided.
            metadata = payload.get("metadata", {})
            # Fetch the order service instance.
            service = self._order_service()
            # Create the order in storage.
            order = service.create_order(user, metadata)
            # Build the response payload with the expected MQTT topic.
            response = {
                "order": order.to_dict(),
                "topic": mqtt_topics.ORDER_NEW,
                "status": "accepted",
            }
            # Respond with accepted status.
            self._send_json(HTTPStatus.ACCEPTED, response)
            return
        # Handle order status updates.
        if path == "/orders/status":
            # Read the JSON payload from the request.
            payload = self._read_json()
            try:
                # Parse the order ID into an integer.
                order_id = int(payload.get("order_id", 0))
            except (TypeError, ValueError):
                # Reject invalid order IDs.
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_order_id"})
                return
            # Extract the new status string.
            status = str(payload.get("status", ""))
            # Extract optional metadata payload.
            metadata = payload.get("metadata")
            try:
                # Apply the status update using the order service.
                updated = self._order_service().update_status(order_id, status, metadata)
            except ValueError:
                # Reject invalid status values.
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_status"})
                return
            # Respond with not found if the order does not exist.
            if updated is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "order_not_found"})
                return
            # Respond with the updated order payload.
            self._send_json(HTTPStatus.OK, {"order": updated.to_dict()})
            return
        # Handle staff roster updates.
        if path == "/staff":
            # Read the JSON payload from the request.
            payload = self._read_json()
            # Normalize the staff name.
            name = str(payload.get("name", "")).strip()
            # Reject empty names.
            if not name:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_name"})
                return
            # Load the existing roster file.
            roster = _load_json(STAFF_FILE, {"staff": []})
            # Extract the staff list from the roster.
            staff = roster.get("staff", [])
            # Add the name if it is not already present.
            if not any(entry.lower() == name.lower() for entry in staff):
                staff.append(name)
            # Store the updated staff list.
            roster["staff"] = staff
            # Persist the updated roster to disk.
            _write_json(STAFF_FILE, roster)
            # Respond with the updated roster.
            self._send_json(HTTPStatus.OK, roster)
            return
        # Handle leaderboard updates.
        if path == "/leaderboard/record":
            # Read the JSON payload from the request.
            payload = self._read_json()
            # Normalize the user name.
            user = str(payload.get("user", "")).strip()
            try:
                # Parse the quantity into an integer.
                quantity = int(payload.get("quantity", 0))
            except (TypeError, ValueError):
                # Default quantity to zero on parse failure.
                quantity = 0
            # Reject empty user or non-positive quantity.
            if not user or quantity <= 0:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_order"})
                return
            # Update the weekly leaderboard data.
            weekly = _update_leaderboard(WEEKLY_LEADERBOARD_FILE, user, quantity)
            # Update the all-time leaderboard data.
            all_time = _update_leaderboard(ALL_TIME_LEADERBOARD_FILE, user, quantity)
            # Respond with the updated leaderboards.
            self._send_json(HTTPStatus.OK, {"weekly": weekly, "all_time": all_time})
            return
        # Respond with not found for unknown endpoints.
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    # Redirect BaseHTTPRequestHandler logging through Python logging.
    def log_message(self, format: str, *args: object) -> None:
        # Route HTTP log messages through the logging module.
        logging.getLogger("kitt.webapp").info(format, *args)

    # Resolve the shared order service.
    def _order_service(self) -> OrderService:
        # Check if the HTTP server already carries an order service.
        if self.server is not None:
            # Read the order service attribute from the server.
            service = getattr(self.server, "order_service", None)
            # Return the service if present.
            if service:
                return service
        # Use the module-level singleton if no server service is set.
        global ORDER_SERVICE
        # Initialize the singleton if needed.
        if ORDER_SERVICE is None:
            ORDER_SERVICE = build_order_service()
        # Return the cached singleton.
        return ORDER_SERVICE

    # Serve frontend assets if requested.
    def _maybe_serve_frontend(self, path: str) -> bool:
        # Map the root path to the dashboard stub.
        if path in ("", "/"):
            request_path = "dashboard_stub.html"
        # Allow serving image assets from the images path.
        elif path.startswith("/images/"):
            request_path = path.lstrip("/")
        # Allow direct requests for the dashboard stub.
        elif path == "/dashboard_stub.html":
            request_path = "dashboard_stub.html"
        else:
            return False

        # Build the raw path for the requested asset.
        raw_path = FRONTEND_DIR / request_path
        # Reject symlinks to avoid directory traversal.
        if raw_path.is_symlink():
            return False
        # Resolve the file path to an absolute path.
        file_path = raw_path.resolve()
        try:
            # Ensure the resolved path is under the frontend directory.
            file_path.relative_to(FRONTEND_DIR)
        except ValueError:
            return False
        # Reject missing or non-file paths.
        if not file_path.exists() or not file_path.is_file():
            return False

        # Guess the content type for the response.
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        # Read the file contents as bytes.
        body = file_path.read_bytes()
        # Send an HTTP 200 response.
        self.send_response(HTTPStatus.OK.value)
        # Send the content type header.
        self.send_header("Content-Type", content_type)
        # Send the content length header.
        self.send_header("Content-Length", str(len(body)))
        # Finalize headers.
        self.end_headers()
        # Write the file content to the response body.
        self.wfile.write(body)
        # Indicate that a frontend asset was served.
        return True

    # Read JSON from the request body.
    def _read_json(self) -> Dict[str, Any]:
        # Read the Content-Length header to determine payload size.
        length = int(self.headers.get("Content-Length", "0"))
        # Return an empty payload if no content was provided.
        if length <= 0:
            return {}
        # Read the raw request body bytes.
        raw = self.rfile.read(length)
        try:
            # Decode and parse the JSON payload.
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            # Return an empty payload on parse failure.
            return {}

    # Send a JSON response payload.
    def _send_json(self, status: HTTPStatus, payload: Dict[str, object]) -> None:
        # Serialize the payload to a JSON byte string.
        body = json.dumps(payload).encode("utf-8")
        # Send the response status code.
        self.send_response(status.value)
        # Send the JSON content type header.
        self.send_header("Content-Type", "application/json")
        # Send the content length header.
        self.send_header("Content-Length", str(len(body)))
        # Finalize headers.
        self.end_headers()
        # Write the JSON response body.
        self.wfile.write(body)


# Load a JSON file or fall back to defaults.
def _load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Read and parse JSON from disk.
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        # Return defaults if the file does not exist.
        return default
    except json.JSONDecodeError:
        # Return defaults if the JSON is malformed.
        return default


# Write a JSON payload to disk.
def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    # Ensure the parent directory exists.
    path.parent.mkdir(parents=True, exist_ok=True)
    # Serialize and write JSON to disk with indentation.
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# Update a leaderboard file and return the sorted leaderboard.
def _update_leaderboard(path: Path, user: str, quantity: int) -> List[Dict[str, Any]]:
    # Load the existing leaderboard data.
    data = _load_json(path, {"leaderboard": []})
    # Extract the leaderboard list.
    leaderboard = data.get("leaderboard", [])
    # Find an existing entry for the user.
    entry = next(
        (item for item in leaderboard if item.get("name", "").lower() == user.lower()),
        None,
    )
    # Update the existing entry if found.
    if entry:
        # Increment the count for the existing user.
        entry["count"] = int(entry.get("count", 0)) + quantity
    else:
        # Append a new entry for the user.
        leaderboard.append({"name": user, "count": quantity})
    # Sort the leaderboard in descending count order.
    leaderboard.sort(key=lambda item: int(item.get("count", 0)), reverse=True)
    # Store the updated leaderboard back into the payload.
    data["leaderboard"] = leaderboard
    # Persist the updated leaderboard to disk.
    _write_json(path, data)
    # Return the updated leaderboard list.
    return leaderboard


# Provide an HTTP server that carries a shared OrderService.
class OrderHTTPServer(HTTPServer):
    # Describe the OrderHTTPServer class for maintainers.
    """HTTP server that carries a shared OrderService."""

    def __init__(
        self,
        server_address: tuple[str, int],
        RequestHandlerClass: type[BaseHTTPRequestHandler],
        order_service: OrderService,
    ) -> None:
        # Initialize the base HTTPServer.
        super().__init__(server_address, RequestHandlerClass)
        # Store the shared order service for handlers.
        self.order_service = order_service


# Build argument parser for CLI usage.
def build_parser() -> argparse.ArgumentParser:
    # Describe the parser construction behavior.
    """Build argument parser for CLI usage."""
    # Configure argument parser for command-line invocation.
    parser = argparse.ArgumentParser(description="KITT Web API (scaffold)")
    # Accept the host interface to bind.
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    # Accept the port to bind.
    parser.add_argument("--port", type=int, default=8080, help="Bind port")
    # Accept the log level so operators can change verbosity.
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    # Return the configured parser to the caller.
    return parser


# Run the API scaffold server.
def main(argv: List[str] | None = None) -> int:
    # Describe the CLI entry point behavior.
    """Run the API scaffold server."""
    # Parse CLI arguments or provided argv list.
    args = build_parser().parse_args(argv)
    # Initialize logging for stdout visibility in CLI runs.
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    # Build the order service for the server.
    order_service = build_order_service()
    # Create the HTTP server with the order service.
    server = OrderHTTPServer((args.host, args.port), ApiHandler, order_service)
    # Log the server address.
    logging.getLogger("kitt.webapp").info("Serving on http://%s:%s", args.host, args.port)
    try:
        # Serve requests until interrupted.
        server.serve_forever()
    except KeyboardInterrupt:
        # Log the shutdown event.
        logging.getLogger("kitt.webapp").info("Shutting down")
    finally:
        # Close the server socket.
        server.server_close()
    # Exit cleanly for CLI integration.
    return 0


# Execute the CLI entry point when run directly.
if __name__ == "__main__":
    # Exit with the status code from main.
    sys.exit(main())
