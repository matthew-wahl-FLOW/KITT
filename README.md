
# KITT — Kokanee Integrated Transportation Team

High-level overview of the KITT automation system repository. Describes architecture layers, responsibilities, and repository layout.

KITT is a distributed automation system that coordinates a DCC‑controlled model railroad and multiple mechanical subsystems to deliver a can of Kokanee Lager from a mechanically cooled compartment to a defined human-accessible delivery point.

The system is designed around clear separation of concerns, deterministic control at the lowest possible layer, and offline-first operation.

This repository is the authoritative source for system architecture, deployment assets, and all software and firmware components.

---

## System Architecture Summary

KITT is composed of four primary layers:

1. **Rail Control (Real‑Time)**
2. **Automation & Orchestration**
3. **Distributed Mechanical Subsystems**
4. **User Interaction & Monitoring**

Each layer has a single responsibility and communicates only through explicit interfaces.

### Rail Control (EX‑CommandStation)

- Hardware: EX‑CSB1 + EX‑MotorShield8874
- Executes EX‑RAIL logic directly on the command station
- Sole authority for DCC track power and locomotive motion
- Provides deterministic, real‑time train control
- No external system performs time‑critical motor control

### Automation & Orchestration (Raspberry Pi)

- Hardware: Raspberry Pi 5
- Software:
  - Python services
  - JMRI
  - Local MQTT broker
- Responsibilities:
  - High‑level sequencing
  - Safety interlocks via state verification
  - Authorization of actions
- Does **not** directly control motors or servos
- Assumes no real‑time guarantees

### Distributed Mechanical Subsystems

- Implemented on dedicated microcontrollers (e.g., ESP32)
- Responsibilities:
  - Local motor/servo control
  - Limit switch enforcement
  - Sensor validation
  - Hardware safety interlocks
- Execute independent local state machines
- Accept high‑level commands only

### Communication Model

- Transport: local wired/wireless LAN
- Protocol: MQTT
- Characteristics:
  - Asynchronous
  - Decoupled
  - Observable
  - Offline-capable

The orchestrator never assumes success without explicit confirmation.

---

## Repository Structure

.github/     — Repository policies and automation (CI, checks)
deploy/      — OS-level installation assets (systemd, udev, installers)
docs/        — Architecture, design notes, and specifications
firmware/    — Microcontroller firmware for mechanical subsystems
hardware/    — Mechanical and electrical design artifacts
jmri/        — JMRI profiles, scripts, and layout logic
services/    — Raspberry Pi orchestration and support services
tests/       — Simulation, validation, and safety tests
webapp/      — User interface and monitoring components

## EX‑CSB1 / EX‑RAIL Production Skeleton

The minimal EX‑RAIL configuration for the command station lives in `kitt/ex-csb1/`:

- `myAutomation.ino` — deterministic EX‑RAIL macros (blocks, turnouts, routes, automations).
- `myConfig.h` — conservative command station configuration (no Wi‑Fi, offline‑first, safe boot).

### What Belongs in EX‑RAIL

- Real‑time, deterministic safety interlocks (block reservations, turnout alignment).
- Minimal routes/automations that must execute even if the Pi is offline.
- Safe defaults at boot (track power off until manually enabled).

### What Does NOT Belong in EX‑RAIL

- High‑level business logic, order workflows, or user intent sequencing.
- Networking, MQTT, database access, or Raspberry Pi service dependencies.
- Anything that can tolerate latency or requires external confirmation.

### Deployment (Compile + Flash)

This skeleton targets the current CommandStation‑EX production release (v5.x); adjust for older
releases as needed (e.g., power‑on behavior or file naming).

1. Copy `kitt/ex-csb1/myConfig.h` to `config.h` in the CommandStation‑EX sketch folder.
2. Copy `kitt/ex-csb1/myAutomation.ino` to `myAutomation.h` in the same folder.
3. Build and flash using the Arduino IDE or the EX‑Installer (recommended by DCC‑EX).

### Relationship to Raspberry Pi / JMRI

- EX‑RAIL is authoritative for real‑time track safety and motion.
- JMRI and Pi services provide orchestration and UI, but must assume the command station
  can run safely without them.
- EX‑RAIL scripts must remain deterministic and safe even when the Pi is offline.

### Key Directories Explained

#### `deploy/`
Canonical deployment definitions:
- systemd unit files
- udev rules
- MQTT configuration snippets
- install/uninstall scripts

Nothing in this directory runs directly; it must be explicitly installed into the OS.

#### `services/`
Python and supporting services that:
- Coordinate subsystems
- Enforce high-level safety logic
- Interface with JMRI and MQTT

These services authorize actions but never directly actuate hardware.

#### `jmri/`
JMRI configuration, panels, and scripts used for:
- Layout state
- Turnouts
- Sensors
- Integration with EX‑CommandStation

#### `firmware/`
Microcontroller code responsible for:
- Physical motion
- Sensor polling
- Hardware safety enforcement

Subsystems reject unsafe commands locally.

---

## Safety Model

- Hardware safety overrides software
- Microcontrollers enforce physical limits
- Loss of communication defaults to a safe state
- Trains cannot enter unsafe track sections
- Mechanical motion requires verified preconditions

No single software failure can trigger unsafe motion.

---

## Current Development Status

- Repository is under active architectural development
- Deployment and service scaffolding exists
- Hardware integration is phased
- System is designed to scale in layout size, complexity, and contributors

See `docs/` for detailed specifications.

---

## License

MIT License. See `LICENSE`.

---

## Missing Info for Further Development
- **Inputs**: Runtime configuration values and environment requirements.
- **Outputs**: Expected telemetry and reporting artifacts.
- **Actions**: Operational runbooks and deployment workflows.
- **Methods**: Release cadence and ownership model.
