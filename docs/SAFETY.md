# Safety

Overview: Safety expectations for hardware and software operations.
Details: Defines hardware interlocks, procedures, and safety defaults.

## Overview
Safety in KITT relies on hardware interlocks and conservative software defaults. Hardware must
always be able to override software, and loss of communication must result in a safe state.

## Hardware Safety Checklist
- Emergency stop wiring is present and tested before live runs.
- Track power and lift power circuits are independently isolatable.
- Limit switches and sensor confirmations are verified for every actuator.

## Operational Procedures
- Two-person rule for live tests with the train or lift energized.
- Verify emergency stop access and announce live test start/end.
- Use a dry-run (no beverage) before any user-facing demo.

## Software Safety Expectations
- Commands require explicit confirmation from sensors where possible.
- Services must log all safety-related events.
- Any ambiguous sensor state defaults to STOP and alert.

## Missing Info for Further Development
- **Inputs**: Physical wiring diagrams and emergency stop circuit specs.
- **Outputs**: Required safety event logs and audit artifacts.
- **Actions**: Incident response flow, escalation, and reset procedure.
- **Methods**: Formal verification or validation approach for safety logic.
