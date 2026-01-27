# KITT Deployment Assets (deploy/)

This directory contains **versioned deployment artifacts** and scripts that install
KITT onto a Raspberry Pi (or other Linux system) in a reproducible way.

Nothing in here is live by itself — it must be **installed** via `./install.sh`.

## System Overview
Deployment assets translate repository configuration into a runnable Pi system. This
scope owns systemd units, environment templates, and device rules that activate the
Python services, JMRI, and MQTT broker.

## Scope Breakdown
- **Pi**: Systemd units and environment files live here.
- **EX-CSB1/EX-RAIL**: Deployment ensures services start in the right order before
  talking to EX-RAIL via JMRI.
- **Web app**: Backend service is expected to run under systemd when deployed.
- **Python automation**: Orchestrator and sensor services are managed here.
- **Microcontrollers**: udev rules and serial device naming live here.
- **Sensors**: udev rules also cover sensor interfaces.
- **Messaging**: Mosquitto configuration snippets define MQTT broker runtime.

## Control Flow
1. Install scripts copy units, config, and env files into `/etc` and `/opt`.
2. `systemctl daemon-reload` registers service definitions.
3. Services start in dependency order (MQTT → JMRI → orchestrator → UI).

## Data Flow (authoritative sources)
- **Systemd units**: `deploy/systemd/system` is authoritative.
- **Environment templates**: `deploy/env` is authoritative.
- **Broker config**: `deploy/mosquitto` is authoritative.

## Startup & Runtime Behavior
- `install.sh` is idempotent and uses sudo for privileged operations.
- `uninstall.sh` removes installed units and optional runtime data.
- Services depend on the `kitt.target` aggregate unit.

## Operational Philosophy
- Keep deployment artifacts versioned alongside code.
- Prefer deterministic, repeatable install steps.
- Ensure services start only when dependencies are ready.

## What lives here

- `systemd/system/`: system services that should run at boot (e.g., orchestrator, JMRI).
- `udev/`: udev rules for persistent device names/permissions.
- `mosquitto/`: MQTT broker config snippets (optional).
- `env/`: example environment files (templates; real secrets should NOT be committed).
- `paths/`: suggested filesystem layout for app code and data.
- `install.sh`: idempotent installer; copies files into `/etc/...`, `/opt/...`, enables services.
- `uninstall.sh`: removes installed files/services (careful; destructive).

## Installation (future-real steps)

1. Customize `env/*.example` → create real files in `/etc/kitt/` before enabling services.
2. Run: `./deploy/install.sh`
3. Check: `systemctl status kitt-orchestrator.service` and `journalctl -u kitt-orchestrator -f`

## Uninstall

- Run: `./deploy/uninstall.sh` (this stops/disable services, removes files it installed)

## Conventions

- Systemd services are installed to: `/etc/systemd/system/`
- App code is placed at: `/opt/kitt/` (see `paths/kitt-layout.example`)
- Runtime data/logs: `/var/lib/kitt/` and `/var/log/kitt/`
- Environment files: `/etc/kitt/*.env` (never commit secrets)
