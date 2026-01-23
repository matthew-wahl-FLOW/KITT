
# KITT — Kokanee Integrated Transportation Team

KITT is a distributed automation system that coordinates a DCC‑controlled model railroad and multiple mechanical subsystems to deliver a beverage from a refrigerator to a human-accessible delivery point.

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