# Architecture

Simple: Summary of KITT system structure and responsibilities.
Technical: Describes components, data flow, and deployment boundaries.

## Overview
KITT is a distributed automation system for a model railroad delivery workflow. It separates
real-time motion control (command station + microcontrollers) from higher-level orchestration
services running on a Raspberry Pi, while the webapp provides user-facing ordering and status.

## Components
- **Raspberry Pi services**: Orchestrator, sensor gateway, load cell monitor, and JMRI bridge.
- **JMRI**: DCC control software connected to the command station.
- **Microcontrollers**: Local safety and actuator control for lift, gate, and sensor modules.
- **Webapp**: Simple HTTP API + UI for submitting orders and monitoring status.
- **MQTT broker**: Message bus between all components.

## Data Flow (Order)
1. User submits an order in the webapp.
2. Web API publishes `kitt/order/new`.
3. Train orchestrator reserves a route and emits a JMRI command intent.
4. JMRI bridge translates and delivers DCC commands to the layout.
5. Sensors report occupancy and load cell status back to MQTT.

## Deployment Notes
- The Raspberry Pi runs all Python services and the MQTT broker.
- Microcontrollers report sensor data and enforce local safety constraints.

## Missing Info for Further Development
- **Inputs**: Exact payload schemas, authentication model, layout topology data.
- **Outputs**: Canonical telemetry and event schema definitions.
- **Actions**: Recovery procedures, failover, and state reconciliation flows.
- **Methods**: State persistence mechanism and service discovery approach.
