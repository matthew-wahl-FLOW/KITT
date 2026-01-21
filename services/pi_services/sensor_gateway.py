#!/usr/bin/env python3
# // Aggregates sensor data from microcontrollers
# // Receives MQTT telemetry from microcontrollers (IR, RFID, load cells)
# // Normalizes messages and republishes to standardized topics
# // Handles sensor health checks and watchdogs
#
# PSEUDOCODE:
# subscribe to raw sensor topics
# on_raw_message(msg): validate, normalize, publish to kitt/sensor/{id}/state
# health_check(): if sensor silent -> publish kitt/sensor/{id}/health = offline
