# JMRI Bridge Configuration

Simple: Configuration guide for the JMRI bridge.
Technical: Notes connectivity, scripts, and mapping expectations.

jmri_bridge connects JMRI to MQTT and optional web services.

## Connection
- JMRI: connect via local JMRI JSON server or WebSocket API.
- MQTT: broker host and port should match the services stack.

## Script Hooks
- Use JMRI startup scripts to auto-load panels and register sensors.
- Keep script paths relative to the JMRI profile directory.

## Throttle Profiles
- Default throttle uses 128 speed steps.
- Match throttle profile to decoder settings to avoid jumps.

## Example Mapping
- JMRI sensor `S1` -> `kitt/sensor/s1/state`
- JMRI turnout `T4` -> `kitt/turnout/4/state`

## Missing Info
- Inputs: list of required config keys and where they are stored.
- Outputs: expected MQTT topics for all published objects.
- Actions: restart sequence when JMRI or MQTT reconnects.
- Methods: authentication approach for the JMRI JSON server.
