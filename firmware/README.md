# Firmware

## System Overview
Firmware runs on microcontrollers that control actuators and enforce local safety
rules. Each firmware module owns its immediate hardware interface and publishes
telemetry or state updates to the Pi through UART-to-MQTT gateways.

## Scope Breakdown
- **Pi**: Receives telemetry and command acknowledgements.
- **EX-CSB1/EX-RAIL**: Provides DCC track power and must be protected by firmware
  interlocks (for example, lift power cut-offs).
- **Web app**: Consumes firmware state through MQTT for UI status.
- **Python automation**: Sends high-level commands and expects acknowledgements.
- **Microcontrollers**: Execute firmware logic for lift, fridge, elevator, and RFID.
- **Sensors**: Door switches, limit switches, load cells, and RFID readers feed
  microcontroller state machines.
- **Messaging**: UART/MQTT gateway topics transport telemetry and command intents.

## Control Flow
1. Microcontroller boots, initializes outputs, and publishes a ready status.
2. UART/MQTT gateway relays commands from the Pi to the firmware.
3. Firmware validates safety conditions and executes motion locally.
4. Status and telemetry events publish back to the Pi.

## Data Flow (authoritative sources)
- **Actuator state**: Firmware is authoritative for servo/motor state.
- **Sensor reads**: Raw sensor values are authoritative at the microcontroller.
- **Safety interlocks**: Firmware enforces final safety decisions.

## Startup & Runtime Behavior
- Firmware initializes outputs to safe defaults and starts a polling loop.
- Control loops are single-threaded and depend on periodic ticks.
- UART output provides telemetry for upstream MQTT relays.

## Operational Philosophy
- Keep safety decisions local to the hardware.
- Accept only high-level intents from the Pi.
- Fail safe when sensor feedback is missing.

## Responsibilities
- Actuator control (servos, motors).
- Sensor polling and debouncing.
- Hardware interlocks and safe-state handling.

## Runtime
Firmware is written for MicroPython-compatible microcontrollers (for example, ESP32-class boards).
Controller scripts live in the subsystem directories and keep the `.ino` names for legacy tooling,
but the contents are MicroPython modules that can be deployed as `main.py`.

## Missing Info for Further Development
- **Inputs**: Supported MCU targets, pin mappings, sensor calibration flows.
- **Outputs**: Telemetry payload schemas and error codes.
- **Actions**: Firmware update and rollback strategy.
- **Methods**: Toolchain selection and build pipeline.
