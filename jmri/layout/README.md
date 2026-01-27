# JMRI Layout

Overview: Notes for managing JMRI layout files.
Details: Defines naming conventions and MQTT mappings for JMRI assets.

This directory stores JMRI layout files used by PanelPro, including panels and routes.

## System Overview
JMRI layout files define the authoritative rail hardware model, including sensors,
turnouts, and logic used by EX-CommandStation. These assets feed the Pi's automation
services via MQTT topics and the JMRI bridge.

## Scope Breakdown
- **Pi**: JMRI runs headless on the Pi and publishes layout state.
- **EX-CSB1/EX-RAIL**: JMRI assets mirror EX-RAIL logic and DCC addresses.
- **Web app**: UI uses layout state for train status displays.
- **Python automation**: Orchestrator subscribes to JMRI topics.
- **Microcontrollers**: Receive commands derived from JMRI layout events.
- **Sensors**: JMRI sensors define occupancy and detector mapping.
- **Messaging**: MQTT topics map JMRI sensors and turnout commands.

## Control Flow
1. PanelPro loads layout files from this directory.
2. JMRI publishes sensor and turnout state to MQTT.
3. Orchestrator consumes state updates and issues new commands.

## Data Flow (authoritative sources)
- **Layout definitions**: XML files in this directory are authoritative.
- **Sensor state**: JMRI produces the authoritative mapping to MQTT.
- **Turnout state**: JMRI is authoritative for turnout positions.

## Startup & Runtime Behavior
- Load the layout file in PanelPro at startup.
- Maintain stable file names to keep mappings consistent.
- Use headless PanelPro for runtime automation.

## Operational Philosophy
- Keep JMRI layouts versioned with the repo.
- Treat JMRI as the source of truth for rail topology.
- Use MQTT for all layout state propagation.

## Importing
- Open PanelPro and load the layout file from this folder.
- Keep file names stable so JMRI scripts and jmri_bridge mappings do not drift.

## Naming Conventions
- Sensors: `S<id>` (block occupancy, detectors).
- Turnouts: `T<id>` (switch machines).
- Routes/Logix: `L<id>` for grouped actions.

## MQTT Mapping
- Sensors publish to `kitt/sensor/<id>/state`.
- Turnout commands subscribe to `kitt/turnout/<id>/command` using JMRI state strings.

## Missing Info
- Inputs: definitive list of layout files that should be loaded per environment.
- Outputs: confirmed topic prefixes for all JMRI objects (signals, lights, blocks).
- Actions: process for validating layout changes before deploying to the layout PC.
- Methods: exact mapping rules for non-sensor accessories (signals, memories).
