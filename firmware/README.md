# Firmware

## Overview
Firmware runs on microcontrollers that control actuators and enforce local safety rules.
It publishes sensor telemetry and listens for high-level commands over MQTT.

## Responsibilities
- Actuator control (servos, motors).
- Sensor polling and debouncing.
- Hardware interlocks and safe-state handling.

## Missing Info for Further Development
- **Inputs**: Supported MCU targets, pin mappings, sensor calibration flows.
- **Outputs**: Telemetry payload schemas and error codes.
- **Actions**: Firmware update and rollback strategy.
- **Methods**: Toolchain selection and build pipeline.
