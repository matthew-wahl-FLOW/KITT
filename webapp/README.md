# Webapp

## System Overview
The webapp provides user-facing ordering and status monitoring. The backend scaffold
uses only the Python standard library and exposes placeholder HTTP endpoints. The
frontend includes a dashboard stub for the Pi display that renders live sensor
readouts and MQTT chatter using placeholder data streams.

## Scope Breakdown
- **Pi**: Hosts the backend API for local kiosk and operational monitoring.
- **EX-CSB1/EX-RAIL**: Exposed indirectly through train status endpoints.
- **Web app**: Frontend dashboard and order forms live here.
- **Python automation**: Order service and orchestration listen to webapp events.
- **Microcontrollers**: Their telemetry appears in the dashboard view.
- **Sensors**: Sensor data is surfaced through dashboard payloads.
- **Messaging**: MQTT topics provide the live data feed for UI updates.

## Control Flow
1. User submits an order via the webapp.
2. Backend records the order and publishes an MQTT order topic.
3. Orchestrator reads the order topic and drives downstream actions.
4. UI reads order history and stats from the backend API.

## Data Flow (authoritative sources)
- **Orders**: `services/orders` SQLite database is authoritative.
- **Staff roster**: `webapp/backend/data/staff_roster.json` is authoritative.
- **Leaderboards**: `webapp/backend/data/leaderboard_*.json` files are authoritative.
- **Live telemetry**: MQTT topics are authoritative for sensor and train status.

## Startup & Runtime Behavior
- Run `python webapp/backend/api.py` on the Pi or development host.
- Backend serves both API responses and the dashboard stub.
- JSON data files are created on demand in `webapp/backend/data/`.

## Operational Philosophy
- Provide a simple local UI that keeps operators informed.
- Avoid direct hardware control from the UI.
- Treat MQTT as the real-time telemetry bus.

## Backend
- `webapp/backend/api.py` runs a minimal HTTP server.
- Endpoints: `POST /order`, `GET /trains`, `GET /staff`, `POST /staff`,
  `GET /leaderboard/weekly`, `GET /leaderboard/all-time`, `POST /leaderboard/record`.
- Data files live in `webapp/backend/data/` for staff and leaderboard storage.

## Running Locally
```bash
python webapp/backend/api.py --host 127.0.0.1 --port 8080
```

## Missing Info for Further Development
- **Inputs**: Authentication provider, request schema for orders.
- **Outputs**: UI requirements and response formats.
- **Actions**: Integration with MQTT and persistence.
- **Methods**: Frontend framework choice and deployment targets.
