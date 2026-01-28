# Schematics

Overview: Index of hardware schematics.
Details: Notes schematic scope, usage, and revision handling.

This folder contains circuit schematics and wiring diagrams for the layout hardware.

## System Overview
Schematics define the authoritative electrical design for the layout. They capture
power distribution, controller interfaces, and sensor circuits used by Pi services and
microcontrollers.

## Scope Breakdown
- **Pi**: References wiring and sensor interfaces defined here.
- **EX-CSB1/EX-RAIL**: Track power distribution is defined here.
- **Web app**: UI status relies on electrical inputs documented here.
- **Python automation**: Services reference schematics for troubleshooting.
- **Microcontrollers**: IO pin mappings are documented here.
- **Sensors**: Sensor circuits are captured here.
- **Messaging**: MQTT topics reference sensor IDs defined here.

## Control Flow
1. Schematics are authored or updated in this folder.
2. Builds reference the latest schematic revision.
3. Wiring and firmware are updated to match schematic changes.

## Data Flow (authoritative sources)
- **Electrical design**: Schematic files in this folder are authoritative.
- **Pin mappings**: Sheet annotations define IO and connector mappings.
- **Power budgets**: Power distribution sheets are authoritative.

## Startup & Runtime Behavior
- Schematics guide hardware bring-up and diagnostics.
- Updates should accompany firmware changes.

## Operational Philosophy
- Treat schematics as the source of truth for electrical design.
- Review revisions before hardware changes.
- Keep diagrams aligned with as-built wiring.

## Contents
- Power distribution schematic (track power, accessory power).
- Controller interface schematic (microcontrollers, IO expanders).
- Sensor circuit schematic (block detection, RFID readers).

## Usage
- Open files in a PDF viewer or schematic editor.
- Use the same revision number in filenames as the hardware build notes.

## Missing Info
- Inputs: source files and tool versions used to generate the schematics.
- Outputs: published PDF names and their revision numbers.
- Actions: update process when circuits are changed or re-routed.
- Methods: review checklist for electrical safety and load limits.
