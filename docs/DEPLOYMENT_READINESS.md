# Deployment Readiness — KITT (Raspberry Pi 5)

This document is the deployment readiness guide for the KITT codebase. It is intended for
engineers commissioning a **fresh Raspberry Pi 5** (Raspberry Pi OS) and deploying all
runtime services (JMRI, Python orchestration, MQTT, and supporting hardware interfaces).

---

## 1) Architecture Overview

- **High-level description**: KITT coordinates a DCC‑controlled model railroad and
  mechanical subsystems (fridge, elevator, lift, sensors, RFID, load cells, cameras)
  to execute a delivery workflow.
- **Runs on the Raspberry Pi**:
  - Python orchestration services (train orchestrator, sensor gateway, load cell monitor)
  - JMRI (headless)
  - MQTT broker (optional local Mosquitto)
  - systemd for service supervision
- **Control/communication boundaries**:
  - **EX‑CSB1 / EX‑RAIL**: Real‑time DCC control and rail motion. This is authoritative
    for train movement.
  - **JMRI**: Layout state, turnout/sensor abstractions, JSON/Web interfaces. It bridges
    between Pi services and the command station.
  - **Python services**: High‑level orchestration, sequencing, safety checks, and sensor
    normalization. Services issue intents through MQTT/JMRI but do **not** directly
    control motors.
  - **Hardware subsystems (MCUs)**: Local actuator control, limit switch enforcement,
    safety interlocks. They accept high‑level commands and enforce physical safety.
- **Data flow (summary)**:
  - Webapp → MQTT → Orchestrator → JMRI → EX‑RAIL (dispatch intent)
  - Sensors/MCUs → MQTT → Sensor gateway/Orchestrator (state confirmation)

---

## 2) Outstanding Information to Be Confirmed (Checklist)

**Confirm before deployment:**

- [ ] Raspberry Pi hostname, static IP (if required), and network interface mapping
- [ ] MQTT broker host/port/credentials (local vs external broker)
- [ ] JMRI profile name and storage path
- [ ] JMRI JSON server and WebSocket ports (and authentication approach)
- [ ] EX‑CSB1 connection type (USB serial vs Wi‑Fi) and exact device path
- [ ] Serial device paths and persistent udev symlinks (e.g., `/dev/kitt/csb1-serial`)
- [ ] GPIO pin assignments for sensors, relays, and any direct Pi IO
- [ ] Sensor naming conventions (MQTT topic IDs, JMRI system/user names)
- [ ] Turnout and block identifiers in JMRI (system names like `LT1`, `IS12`, etc.)
- [ ] RFID reader interface type and device path
- [ ] Load cell ADC interface type and device path
- [ ] Camera device IDs (`/dev/video*`) or CSI camera config
- [ ] Power budget, wiring diagram, and emergency stop circuit specs
- [ ] Safe operating limits (lift travel, motor current limits, speed caps)
- [ ] Service user/group permissions (dialout, video, gpio, i2c, spi)

---

## 3) Outstanding Tasks Before Deployment

- **Software**
  - [ ] Finalize environment variables for all services (`/etc/kitt/kitt.env`)
  - [ ] Fill MQTT topic schemas and sensor/turnout mapping tables
  - [ ] Define JMRI profile and ensure scripts auto‑load on start
  - [ ] Implement/verify `ExecStart` commands in systemd unit files
  - [ ] Ensure logging locations and retention policy are defined
  - [ ] Confirm Python entry points for orchestrator and service modules
- **Configuration**
  - [ ] Populate udev rules in `deploy/udev/99-kitt-devices.rules`
  - [ ] Validate Mosquitto configuration if running local broker
  - [ ] Confirm network firewall rules (ports for MQTT/JMRI/Web)
- **Hardware validation**
  - [ ] Verify each sensor reports stable, calibrated values
  - [ ] Verify limit switches and safety interlocks for each actuator
  - [ ] Validate emergency stop wiring
- **Safety checks**
  - [ ] Dry‑run workflow (no beverage) with full sensor validation
  - [ ] Two‑person rule for live motion tests
  - [ ] Confirm safe shutdown procedure for all subsystems
- **Test plans**
  - [ ] Execute unit tests and integration simulation tests
  - [ ] Execute hardware‑in‑the‑loop checklist (see `docs/TEST_PLAN.md`)
- **Fallback / recovery**
  - [ ] Define manual override procedure for each subsystem
  - [ ] Document rollback steps for JMRI profile changes
  - [ ] Backup MQTT configs and env files before go‑live

---

## 4) Fresh Raspberry Pi Setup

**Assumes Raspberry Pi OS Lite or Desktop, fresh install.**

1. **Enable SSH**
   - If using Raspberry Pi Imager: enable SSH in advanced settings.
   - Or create an empty file named `ssh` in the boot partition before first boot.
2. **Boot and log in**
   - `ssh pi@<pi-ip>` (or attach keyboard/monitor for first login).
3. **Update OS**
   - `sudo apt update`
   - `sudo apt -y full-upgrade`
   - `sudo reboot`
4. **Install required system packages**
   - `sudo apt -y install git curl jq python3 python3-venv python3-pip`
   - `sudo apt -y install openjdk-17-jre-headless`
   - `sudo apt -y install mosquitto mosquitto-clients` (if running local MQTT)
   - `sudo apt -y install sqlite3` (optional CLI tooling for order database inspection)
5. **Verify Python version**
   - `python3 --version` (expect 3.11 or newer per CI workflow)
6. **Optional: enable interfaces**
   - Use `sudo raspi-config` → Interface Options (I2C/SPI/Serial) as required.

---

## 5) Codebase Installation

1. **Clone the repository**
   - `git clone https://github.com/matthew-wahl-FLOW/KITT.git /opt/kitt`
2. **Directory layout expectation**
   - `/opt/kitt` holds the repo (`deploy/`, `services/`, `jmri/`, `webapp/`, etc.)
   - See `deploy/paths/kitt-layout.example` for the target filesystem layout.
3. **Create a Python virtual environment**
   - `cd /opt/kitt`
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
4. **Install Python dependencies**
   - Install runtime Python dependencies from the repository root:
     - `pip install -r requirements.txt`
   - Current services only use the standard library; the file is still provided
     to keep deployments consistent and future additions explicit.
5. **Environment files**
   - Create `/etc/kitt/kitt.env` and define:
     - MQTT host/port/credentials
     - JMRI JSON/WebSocket endpoints
     - Device paths (serial, RFID, load cells, camera)
   - Ensure `/etc/kitt/` is owned and readable by the service user (`pi`).

---

## 6) JMRI Headless Setup

1. **Install JMRI**
   - Download the latest stable JMRI for Linux (PanelPro) from jmri.org.
   - Extract to `/opt/jmri`.
2. **Create/verify JMRI profile**
   - Launch once with UI on a monitor (or VNC) to set up the profile.
   - Name the profile `KITT` (or update the systemd unit accordingly).
3. **Configure connection to EX‑CSB1**
   - If USB: select the serial port (e.g., `/dev/kitt/csb1-serial`).
   - If Wi‑Fi: configure the EX‑CommandStation IP/port.
4. **Enable JSON/Web services**
   - In JMRI preferences, enable the JSON server and WebSocket (record ports).
5. **Headless startup**
   - Verify the systemd unit (`deploy/systemd/system/kitt-jmri.service`) and set
     the correct `ExecStart` option for PanelPro.
6. **Verify JMRI is reachable**
   - From the Pi: `curl http://localhost:<json-port>/json/` (expect JSON response).

---

## 7) systemd Services

**Expected units (from `deploy/systemd/system/`):**

- `kitt.target`
  - **Purpose**: Aggregate target to start/stop all KITT services.
  - **Healthy**: `systemctl is-active kitt.target` → `active`.
- `kitt-mqtt.service`
  - **Purpose**: Optional local Mosquitto broker.
  - **Runs**: `mosquitto -c /etc/mosquitto/mosquitto.conf` (see `deploy/mosquitto`).
  - **Dependencies**: network‑online.
  - **Healthy**: broker listens on configured port; `mosquitto_sub` can connect.
- `kitt-jmri.service`
  - **Purpose**: Headless JMRI (PanelPro).
  - **Runs**: `/opt/jmri/PanelPro --no-splash --profile KITT` (or custom script).
  - **Dependencies**: `kitt-mqtt.service`, network‑online.
  - **Healthy**: JSON/WebSocket endpoints reachable, logs show profile loaded.
- `kitt-orchestrator.service`
  - **Purpose**: Python orchestration layer.
  - **Runs**: Python entry point under `/opt/kitt/src/orchestrator` (to be set).
  - **Dependencies**: `kitt-mqtt.service`.
  - **Healthy**: heartbeat topics emitted, no restart loops.
- `kitt-health.service`
  - **Purpose**: Health/heartbeat publisher.
  - **Runs**: Python health module (to be set).
  - **Dependencies**: `kitt-orchestrator.service`.
  - **Healthy**: retained health payload published at interval.
- `kitt-camera.service`
  - **Purpose**: Optional camera streaming process.
  - **Runs**: Camera streamer module (to be set).
  - **Dependencies**: network‑online.
  - **Healthy**: stream reachable or MQTT status online.

**Common service commands:**

- Enable all: `sudo systemctl enable kitt.target`
- Start all: `sudo systemctl start kitt.target`
- Stop all: `sudo systemctl stop kitt.target`
- Status: `systemctl --no-pager --full status <service>`
- Logs: `journalctl -u <service> -f`

---

## 8) Running the System

- **“Running” means**:
  - systemd services are active (MQTT, JMRI, orchestrator, health)
  - MQTT topics show live telemetry and commands
  - JMRI is connected to the command station
- **Auto‑start at boot**:
  - `kitt.target` is enabled; it pulls in dependent units.
- **Manual execution (debugging)**:
  - Activate venv: `source /opt/kitt/.venv/bin/activate`
  - Run directly:
    - `python services/pi_services/train_orchestrator.py`
    - `python services/pi_services/jmri_bridge.py`
    - `python services/pi_services/sensor_gateway.py`
    - `python services/pi_services/loadcell_monitor.py`
- **Debug vs production**
  - Use env flags in `/etc/kitt/kitt.env` (e.g., `KITT_ENV=dev|prod`).
  - In dev mode, allow stdout logging and reduced safety interlocks only in a
    non‑live environment.

---

## 9) Validation & Smoke Tests

**Checklist after install:**

- [ ] `systemctl is-active kitt.target` is `active`
- [ ] `systemctl is-active kitt-jmri.service` is `active`
- [ ] JMRI JSON server reachable (`curl http://localhost:<port>/json/`)
- [ ] MQTT broker reachable (`mosquitto_sub -t kitt/# -v`)
- [ ] Orchestrator emits heartbeat topics (verify via MQTT)
- [ ] EX‑CSB1 connected and JMRI reports a live connection
- [ ] Turnout commands issued from JMRI move hardware as expected
- [ ] Sensors publish stable state updates to `kitt/sensor/<id>/state`
- [ ] Load cells report readings and calibration is confirmed
- [ ] Train can be dispatched in a controlled loop with emergency stop ready

---

## 10) Failure Modes & Recovery

- **Service crash**: systemd restarts the service per unit policy (`Restart=...`).
- **JMRI unavailable**:
  - Orchestrator should halt new dispatches and mark system unsafe.
  - Restart JMRI: `sudo systemctl restart kitt-jmri.service`
- **MQTT broker down**:
  - Services will fail to connect; recover broker first.
  - If using local broker: `sudo systemctl restart kitt-mqtt.service`
- **Sensor uncertainty**:
  - Default to STOP; block new actions until state is confirmed.
- **Safe stop**:
  - `sudo systemctl stop kitt.target`
  - Remove track power and actuator power if needed.
- **Recover without reboot**:
  - Restart specific services in dependency order:
    - `sudo systemctl restart kitt-mqtt.service`
    - `sudo systemctl restart kitt-jmri.service`
    - `sudo systemctl restart kitt-orchestrator.service`
    - `sudo systemctl restart kitt-health.service`

**Risks / Assumptions**:
- This guide assumes all hardware is wired to safety specifications and that
  microcontrollers enforce local limits. Any missing interlocks are a deployment blocker.
