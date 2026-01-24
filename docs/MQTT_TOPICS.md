# MQTT Topics

Simple: Reference for KITT MQTT topic naming.
Technical: Lists topic hierarchy, QoS guidance, and retained message rules.

## Overview
This document defines the MQTT topic hierarchy for KITT. Topics are rooted at `kitt/` and
use scoped identifiers for orders, trains, sensors, and JMRI bridge commands/events.

## Core Topics
- `kitt/order/new` - New order submissions.
- `kitt/order/{order_id}/status` - Order status transitions.
- `kitt/order/{order_id}/event` - Order related events (load/unload, delivery steps).
- `kitt/train/{train_id}/location` - Train position updates.
- `kitt/train/{train_id}/status` - Train operational status.
- `kitt/sensor/{sensor_id}/state` - Normalized sensor state updates.
- `kitt/sensor/{sensor_id}/health` - Sensor health reports.
- `kitt/jmri/command/{command}` - High-level command intents.
- `kitt/jmri/event/{event}` - JMRI event updates.

## QoS and Retain Guidance
- Sensor telemetry: QoS 0 or 1, typically not retained.
- Command intents: QoS 1, not retained by default.
- Status topics: QoS 1, retained for last-known state.

## Missing Info for Further Development
- **Inputs**: ID naming conventions and payload schemas.
- **Outputs**: Required retained fields and snapshot formats.
- **Actions**: Replay policy and retained topic cleanup rules.
- **Methods**: Validation rules and versioning strategy.
