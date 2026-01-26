# JMRI Layout

Overview: Notes for managing JMRI layout files.
Details: Defines naming conventions and MQTT mappings for JMRI assets.

This directory stores JMRI layout files used by PanelPro, including panels and routes.

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
