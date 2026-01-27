# Documentation

## System Overview
The documentation folder contains architectural references, MQTT topic definitions,
validation checklists, and testing expectations. This material is the shared contract
between hardware, firmware, and software teams.

## Scope Breakdown
- **Pi**: Runtime and service expectations are documented here.
- **EX-CSB1/EX-RAIL**: Rail control expectations and safety notes are documented here.
- **Web app**: UI requirements and API expectations live here.
- **Python automation**: Service contracts and topic expectations live here.
- **Microcontrollers**: Firmware expectations and safety notes live here.
- **Sensors**: Sensor calibration and telemetry definitions live here.
- **Messaging**: MQTT topic hierarchy and QoS guidance live here.

## Control Flow
1. Architects update design docs in this folder.
2. Implementation teams reference docs when building services and firmware.
3. Changes flow back into updated documentation.

## Data Flow (authoritative sources)
- **Architecture**: `ARCHITECTURE.md` is authoritative.
- **Messaging**: `MQTT_TOPICS.md` is authoritative.
- **Safety**: `SAFETY.md` is authoritative.
- **Testing**: `TEST_PLAN.md` is authoritative.

## Startup & Runtime Behavior
- Docs are referenced during deployment and commissioning.
- Updates should land before any new hardware integration.

## Operational Philosophy
- Documentation is a living contract.
- Keep docs close to code and hardware.
- Prefer clarity over completeness in early scaffolds.

## Core References
- `ARCHITECTURE.md` - System overview and component boundaries.
- `MQTT_TOPICS.md` - Message bus topic hierarchy and QoS guidance.
- `SAFETY.md` - Safety procedures and expectations.
- `TEST_PLAN.md` - Testing scope and acceptance criteria.

## Missing Info for Further Development
- **Inputs**: Desired documentation owners and update cadence.
- **Outputs**: Expected deliverables for release documentation.
- **Actions**: Doc review and sign-off workflow.
- **Methods**: Versioning and change tracking approach.
