# Services

## Overview
The `services/` directory contains the Python services that run on the Raspberry Pi. The
current implementations are minimal scaffolds using only the Python standard library.

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

## Missing Info for Further Development
- **Inputs**: MQTT broker configuration, credentials, and payload schemas.
- **Outputs**: Persistent state storage and telemetry requirements.
- **Actions**: Service orchestration (systemd) and restart policies.
- **Methods**: Logging, metrics, and tracing strategy.
