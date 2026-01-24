# Webapp

## Overview
The webapp provides user-facing ordering and status monitoring. The backend scaffold uses
only the Python standard library and exposes placeholder HTTP endpoints.

## Backend
- `webapp/backend/api.py` runs a minimal HTTP server.
- Endpoints: `POST /order`, `GET /trains`.

## Running Locally
```bash
python webapp/backend/api.py --host 127.0.0.1 --port 8080
```

## Missing Info for Further Development
- **Inputs**: Authentication provider, request schema for orders.
- **Outputs**: UI requirements and response formats.
- **Actions**: Integration with MQTT and persistence.
- **Methods**: Frontend framework choice and deployment targets.
