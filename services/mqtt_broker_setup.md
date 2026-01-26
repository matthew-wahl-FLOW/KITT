# MQTT Broker Setup

Overview: Minimal Mosquitto setup guide for KITT services.
Details: Notes install steps, configuration, and policy expectations.

Setup notes for running Mosquitto on a Raspberry Pi for the services stack.

## Install
- `sudo apt update`
- `sudo apt install mosquitto mosquitto-clients`
- `sudo systemctl enable --now mosquitto`

## Configuration
- Enable persistence for retained state and client sessions.
- Use a dedicated config file under `/etc/mosquitto/conf.d/`.
- Define a listener on the local network interface.

## Auth and TLS
- Use a password file for basic auth on non-local networks.
- Add TLS certificates if the broker is exposed beyond the LAN.

## Policy
- Limit retained messages to state topics.
- Keep a short connection timeout for offline devices.

## Missing Info
- Inputs: exact broker hostnames, ports, and credentials.
- Outputs: list of required MQTT topics for services.
- Actions: backup and restore process for broker data.
- Methods: certificate rotation and renewal procedure.
