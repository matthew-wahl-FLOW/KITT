# Firmware

## Overview
Firmware runs on microcontrollers that control actuators and enforce local safety rules.
It publishes sensor telemetry and listens for high-level commands over MQTT.

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
