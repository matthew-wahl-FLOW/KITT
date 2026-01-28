# Services

## System Overview
The `services/` directory holds Raspberry Pi automation services and shared Python
libraries. These services coordinate the rail controller, sensors, and webapp without
controlling motors directly. They use MQTT to exchange intent and state between the Pi,
microcontrollers, and JMRI.

## Scope Breakdown
- **Pi**: Runs the Python scaffolds for orchestration, sensor normalization, load cell
  monitoring, dashboard output, and JMRI bridging.
- **EX-CSB1/EX-RAIL**: Receives high-level dispatch intent from the Pi and owns real-time
  train motion. Services only request actions through MQTT and JMRI.
- **Web app**: Serves orders, staff roster, and leaderboard updates that feed automation.
- **Python automation**: Orchestrator, sensor gateway, load cell monitor, and dashboard
  simulation live here.
- **Microcontrollers**: Consume MQTT/UART commands generated from these services.
- **Sensors**: Sensor gateway normalizes raw inputs into consistent MQTT topics.
- **Messaging**: All services assume MQTT is the shared bus for commands and telemetry.

## Control Flow
1. Webapp submits an order and publishes the `kitt/order/new` topic.
2. Train orchestrator receives the order intent and plans a route for EX-RAIL/JMRI.
3. Sensor gateway and load cell monitor publish normalized state topics.
4. Orchestrator updates order status and emits telemetry as checkpoints complete.

## Data Flow (authoritative sources)
- **Orders**: `services/orders` SQLite database is the authoritative source.
- **Train motion**: EX-CSB1/EX-RAIL remains authoritative for DCC commands.
- **Sensor state**: Sensor gateway output topics are authoritative for normalized state.
- **UI state**: Webapp reads from order service data and MQTT telemetry.

## Startup & Runtime Behavior
- Services are started via systemd units from `deploy/systemd/system`.
- Each service can run stand-alone for development.
- Services log to stdout for capture by journald.

## Operational Philosophy
- Services request actions but do not perform real-time control.
- Safety comes from verifying state before taking the next step.
- MQTT is treated as the contract between independent subsystems.

## Entry Points
- `pi_services/train_orchestrator.py` - Command orchestration scaffold.
- `pi_services/jmri_bridge.py` - JMRI command bridge scaffold.
- `pi_services/sensor_gateway.py` - Sensor normalization scaffold.
- `pi_services/loadcell_monitor.py` - Load cell monitoring scaffold.
- `pi_services/display_dashboard.py` - Pi display dashboard scaffold.

## Running Locally
Each module can be executed directly:

```bash
python services/pi_services/train_orchestrator.py
python services/pi_services/jmri_bridge.py
python services/pi_services/sensor_gateway.py
python services/pi_services/loadcell_monitor.py
python services/pi_services/display_dashboard.py
```

## Order Service (Persistent Storage)
The `services/orders` package provides a SQLite-backed order service used by the
webapp and automation services. It owns order persistence and derived stats.

### Usage
```python
from services.orders import OrderService

service = OrderService()
order = service.create_order("user-123", {"rfid": "tag-9"})
service.update_status(order.order_id, "in_progress")
stats = service.get_stats()
```

The SQLite database is stored at `services/data/orders.db` by default and is
initialized automatically on first use.

## Missing Info for Further Development
- **Inputs**: MQTT broker configuration, credentials, and payload schemas.
- **Outputs**: Telemetry ingestion requirements for orders and trains.
- **Actions**: Service orchestration (systemd) and restart policies.
- **Methods**: Logging, metrics, and tracing strategy.
