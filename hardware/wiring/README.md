# Wiring

Overview: Overview of layout wiring guidance.
Details: Summarizes wiring conventions and safety considerations.

Wiring guides and connection maps for the physical layout.

## System Overview
Wiring diagrams define how power, data, and sensor lines connect the layout. They
ensure the Pi, EX-CommandStation, microcontrollers, and sensors share a consistent
physical topology.

## Scope Breakdown
- **Pi**: Wiring guides cover Pi IO and power feeds.
- **EX-CSB1/EX-RAIL**: Track and accessory power wiring is specified here.
- **Web app**: UI status depends on wiring for sensors and outputs.
- **Python automation**: Wiring references support troubleshooting and maintenance.
- **Microcontrollers**: Wiring maps define UART, sensor, and actuator connections.
- **Sensors**: Wiring ensures sensor circuits match firmware expectations.
- **Messaging**: Sensor IDs align with MQTT topics from wiring docs.

## Control Flow
1. Wiring diagrams define the physical layout connections.
2. Installers wire the layout according to the diagrams.
3. Firmware and services use the documented IDs.

## Data Flow (authoritative sources)
- **Cable routes**: Wiring diagrams are authoritative.
- **Labeling**: Cable labels defined here are authoritative.
- **Connector pinouts**: Wiring diagrams are authoritative.

## Startup & Runtime Behavior
- Wiring validation occurs during commissioning.
- Updates should be reviewed before powering hardware.

## Operational Philosophy
- Maintain consistent labeling to simplify troubleshooting.
- Keep data wiring isolated from power runs.
- Validate wiring before firmware changes.

## Sections
- Track power bus routes and feeder drops.
- Accessory power bus for switches, signals, and lights.
- Data wiring for sensors, RFID readers, and control nodes.

## Conventions
- Red/black for track power, yellow/black for accessories.
- Label both ends of every cable with a durable tag.
- Keep low-voltage data wiring separated from track power runs.

## Missing Info
- Inputs: exact cable gauges and connector part numbers.
- Outputs: finalized wiring map with node IDs and cable labels.
- Actions: test procedure after wiring changes.
- Methods: grounding strategy and noise mitigation checklist.
