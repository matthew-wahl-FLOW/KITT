# KITT Deployment Assets (deploy/)

This directory contains **versioned deployment artifacts** and scripts that install
KITT onto a Raspberry Pi (or other Linux system) in a reproducible way.

Nothing in here is live by itself — it must be **installed** via `./install.sh`.

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

``
