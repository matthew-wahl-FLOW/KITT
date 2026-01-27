#!/usr/bin/env python3
# Use env to locate the system's Python 3 interpreter when run as a script.
"""Pi dashboard display scaffold.

Overview: Streams live sensor readouts and MQTT chatter to a lightweight UI payload.
Details: Simulates MQTT updates and prints display-ready JSON lines for a Pi renderer.

Missing info for further development:
- Inputs: MQTT broker credentials, sensor catalog, UI endpoint location.
- Outputs: Websocket or HTTP push payload schema for the display.
- Actions: Reconnect/backoff policy and persistence strategy.
- Methods: Rendering stack (Chromium kiosk, frame buffer, or HDMI).
"""

from __future__ import annotations
# Defer annotation evaluation to keep forward references simple.

# Standard library imports for CLI parsing, JSON output, and time handling.
import argparse
import json
import logging
import random
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List

# Shared MQTT topic helpers for consistent topic construction.
from services.utils import mqtt_topics

# Temperature and humidity defaults used for simulated readings.
TEMP_BASE_C = 3.0
TEMP_RANGE_C = 4.0
HUMIDITY_BASE = 52.0
HUMIDITY_RANGE = 6.0


@dataclass
# Record a single sensor reading for the UI payload.
class SensorReading:
    """Represents a sensor reading for the display."""

    sensor_id: str
    value: str
    updated: str


@dataclass
# Record a single MQTT message for the UI chatter feed.
class MqttMessage:
    """Represents a MQTT chatter line."""

    topic: str
    payload: str
    timestamp: str


class DisplayDashboard:
    """Builds the payload for the Pi display."""

    def __init__(self, logger: logging.Logger) -> None:
        # Store the logger and initialize in-memory lists.
        self.logger = logger
        self._readings: List[SensorReading] = []
        self._chatter: List[MqttMessage] = []

    def update_reading(self, sensor_id: str, value: str) -> None:
        # Timestamp each reading to show freshness in the UI.
        timestamp = datetime.now(timezone.utc).isoformat()
        # Construct a new reading object for the sensor.
        reading = SensorReading(sensor_id=sensor_id, value=value, updated=timestamp)
        # Replace any previous reading from the same sensor.
        self._readings = [r for r in self._readings if r.sensor_id != sensor_id]
        # Insert the latest reading at the top for display.
        self._readings.insert(0, reading)
        # Log the update with the normalized MQTT topic.
        self.logger.info(
            "Sensor reading sensor_id=%s value=%s topic=%s",
            sensor_id,
            value,
            mqtt_topics.sensor_reading_topic(sensor_id),
        )

    def add_chatter(self, topic: str, payload: str) -> None:
        # Build a chatter message with a timestamp.
        message = MqttMessage(
            topic=topic,
            payload=payload,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        # Prepend the chatter item and keep only the latest entries.
        self._chatter.insert(0, message)
        self._chatter = self._chatter[:10]
        # Log the chatter for visibility in CLI mode.
        self.logger.info("MQTT chatter topic=%s payload=%s", topic, payload)

    def build_payload(self) -> dict:
        """Build the display payload."""
        # Assemble the payload dictionary for the display renderer.
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sensors": [asdict(reading) for reading in self._readings],
            "chatter": [asdict(message) for message in self._chatter],
        }


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI usage."""
    # Configure argument parser for command-line invocation.
    parser = argparse.ArgumentParser(description="KITT Display Dashboard (scaffold)")
    # Accept placeholder inputs for the simulation loop.
    parser.add_argument("--ticks", type=int, default=3, help="Number of update cycles")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    # Return the configured parser to the caller.
    return parser


def simulate_cycle(display: DisplayDashboard) -> None:
    """Generate a simulated update cycle."""
    # Generate simulated sensor values for the display.
    temp_c = round(TEMP_BASE_C + random.random() * TEMP_RANGE_C, 2)
    humidity = round(HUMIDITY_BASE + random.random() * HUMIDITY_RANGE, 1)
    lift_state = random.choice(["raised", "lowered"])
    # Update the in-memory readings with formatted values.
    display.update_reading("fridge-temp", f"{temp_c} °C")
    display.update_reading("fridge-humidity", f"{humidity} %")
    display.update_reading("lift-state", lift_state)
    # Emit chatter messages as if MQTT updates arrived.
    display.add_chatter(
        mqtt_topics.sensor_reading_topic("fridge-temp"),
        json.dumps({"temp_c": temp_c}),
    )
    display.add_chatter(
        mqtt_topics.sensor_reading_topic("fridge-humidity"),
        json.dumps({"humidity": humidity}),
    )
    display.add_chatter("kitt/lift/state", json.dumps({"state": lift_state}))


def main(argv: List[str] | None = None) -> int:
    """Run the display dashboard scaffold."""
    # Parse CLI arguments or provided argv list.
    args = build_parser().parse_args(argv)
    # Initialize logging for stdout visibility in CLI runs.
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("kitt.display_dashboard")
    # Create the dashboard scaffold.
    display = DisplayDashboard(logger)

    # Run the requested number of simulated cycles.
    for _ in range(args.ticks):
        simulate_cycle(display)
        payload = display.build_payload()
        # Print JSON payloads for the front-end renderer.
        print(json.dumps(payload))
    # Exit cleanly for CLI integration.
    return 0


if __name__ == "__main__":
    # Execute the CLI entry point when run directly.
    sys.exit(main())
