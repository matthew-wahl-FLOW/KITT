# KITT
Kokanee Integrated Transportation Team - Autonomous Synchronized Railway Network with Integrated Robotic Beverage Distribution
# Beer Train Automation System

A fully automated model railroad system that delivers ice coldd kokanee via a dedicated DCC-controlled consist.

This project integrates Raspberry Pi 5, EX-CommandStation (CSB1), EX-RAIL, JMRI, Python, MQTT, and multiple microcontrollers to coordinate train movement, hardware automation, and user interaction.

---

## Project Objectives

- Operate multiple DCC locomotives simultaneously on a ~200 ft layout
- Designate a priority “beer train” with right-of-way handling
- Automate beer dispensing, loading, transport, and delivery
- Provide real-time monitoring of trains, switches, sensors, and hardware
- Enable ordering via web or desktop interface
- Track user consumption and system activity

---

## System Architecture Overview

### Control Layers

| Layer | Technology |
|-----|-----------|
| DCC / Track Control | EX-CSB1 + EX-MotorShield8874 |
| Train Automation | EX-RAIL |
| Layout Logic & Panels | JMRI |
| Orchestration & State Management | Python (Raspberry Pi 5) |
| Messaging | MQTT |
| Hardware Control | Microcontrollers (servo motors, sensors, load cells) |
| User Interface | Web / Desktop application |
| Vision | Camera mounted on beer train |

---

## Component Interaction Model

- EX-RAIL runs on the CSB1 and executes deterministic train movements
- JMRI manages turnouts, sensors, panels, and high-level layout state
- Python on the Raspberry Pi:
  - Orchestrates multi-step sequences
  - Validates safety and readiness conditions
  - Coordinates microcontrollers via MQTT
- MQTT provides asynchronous, decoupled communication between:
  - Python services
  - Microcontrollers
  - User interface components

---

## Major Subsystems

### Train Control
- Multiple locomotives running in opposing directions
- Siding-based yielding logic
- Priority routing for kokanee train by freight and passenger locomotives
- Priority routing for freight train by passenger locomotive

### Beer Dispensing and Loading
- Order initiation via authenticated user interface or RFID
- Refrigerator dispenser controlled by a microcontroller and servo
- Elevator lifts beer to track height
- Ramp transfers beer to flatcar
- Load cells confirm presence and removal of beer

### Lift Section
- Track section lowers to waist height for delivery
- Position sensors verify lift state
- Train movement interlocked with lift position

### Verification and Safety
- IR or optical sensors for precise train positioning
- RFID or identification system to verify the beer train
- Load cells to confirm beer handling events
- Hardware and software interlocks to prevent unsafe operation

---

## Repository Structure

