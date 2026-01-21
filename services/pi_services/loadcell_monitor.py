#!/usr/bin/env python3
# // Monitors load cell readings for beer presence verification
# // Calibrates sensors on startup or via calibration topic
# // Publishes events: beer_loaded, beer_removed, weight_error
# // Interfaces: HX711 amplifier via microcontroller or direct ADC
#
# PSEUDOCODE:
# on_start(): load calibration, subscribe to calibration topic
# on_weight_read(value): apply calibration -> if threshold_crossed -> publish beer_loaded/beer_removed
# on_calibrate(cmd): run calibration routine and save offsets
