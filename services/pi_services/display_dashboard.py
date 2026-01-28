#!/usr/bin/env python3
# Use env to locate the system's Python 3 interpreter when run as a script.
# Start the module docstring for the display dashboard.
"""Pi dashboard display scaffold."""
# Summarize what the display dashboard provides.
# Overview: Streams live sensor readouts and MQTT chatter to a lightweight UI payload.
# Explain how the scaffold operates.
# Details: Simulates MQTT updates and prints display-ready JSON lines for a Pi renderer.
# Capture open questions for future development.
# Missing info for further development:
# Identify configuration inputs that are still required.
# - Inputs: MQTT broker credentials, sensor catalog, UI endpoint location.
# Identify display payload outputs that are still required.
# - Outputs: Websocket or HTTP push payload schema for the display.
# Identify operational actions that are still required.
# - Actions: Reconnect/backoff policy and persistence strategy.
# Identify implementation methods that are still required.
# - Methods: Rendering stack (Chromium kiosk, frame buffer, or HDMI).

# Enable postponed evaluation so annotations can use forward references.
from __future__ import annotations

# Import argparse for command-line argument parsing.
import argparse
# Import JSON utilities for serializing the UI payload.
import json
# Import logging for CLI visibility.
import logging
# Import random for simulated sensor values in the scaffold.
import random
# Import sys for CLI exit handling.
import sys
# Import dataclass utilities for structured payload entries.
from dataclasses import dataclass, asdict
# Import datetime helpers for timestamps on sensor values.
from datetime import datetime, timezone
# Import typing helper for list annotations.
from typing import List

# Import shared MQTT topic helpers for consistent topic construction.
from services.utils import mqtt_topics

# Define the base fridge temperature in Celsius for simulation.
TEMP_BASE_C = 3.0
# Define the total simulated temperature spread in Celsius.
TEMP_RANGE_C = 4.0
# Define the base humidity percentage used in simulation.
HUMIDITY_BASE = 52.0
# Define the total simulated humidity spread.
HUMIDITY_RANGE = 6.0


# Enable dataclass generation for sensor readings.
@dataclass
# Record a single sensor reading for the UI payload.
class SensorReading:
    # Describe the sensor reading dataclass for maintainers.
    """Represents a sensor reading for the display."""

    # Identify which sensor produced the reading.
    sensor_id: str
    # Store the formatted value for the display.
    value: str
    # Store the ISO timestamp of when the reading was updated.
    updated: str


# Enable dataclass generation for MQTT chatter.
@dataclass
# Record a single MQTT message for the UI chatter feed.
class MqttMessage:
    # Describe the MQTT message dataclass for maintainers.
    """Represents a MQTT chatter line."""

    # Store the MQTT topic that the message arrived on.
    topic: str
    # Store the payload text for display.
    payload: str
    # Store the timestamp for when the message was recorded.
    timestamp: str


# Assemble display payloads for the Raspberry Pi dashboard UI.
class DisplayDashboard:
    # Describe the display dashboard class for maintainers.
    """Builds the payload for the Pi display."""

    # Initialize the dashboard with a logger.
    def __init__(self, logger: logging.Logger) -> None:
        # Store the logger for CLI output.
        self.logger = logger
        # Initialize the list of latest sensor readings.
        self._readings: List[SensorReading] = []
        # Initialize the list of recent MQTT chatter messages.
        self._chatter: List[MqttMessage] = []

    # Update or insert a sensor reading.
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
            # Provide the log format string for sensor readings.
            "Sensor reading sensor_id=%s value=%s topic=%s",
            # Provide the sensor ID argument for the log.
            sensor_id,
            # Provide the sensor value argument for the log.
            value,
            # Provide the MQTT topic argument for the log.
            mqtt_topics.sensor_reading_topic(sensor_id),
            # Close the logger call.
        )

    # Add a chatter message to the feed.
    def add_chatter(self, topic: str, payload: str) -> None:
        # Build a chatter message with a timestamp.
        message = MqttMessage(
            # Provide the topic for the chatter message.
            topic=topic,
            # Provide the payload text for the chatter message.
            payload=payload,
            # Provide the timestamp for the chatter message.
            timestamp=datetime.now(timezone.utc).isoformat(),
            # Close the chatter message constructor.
        )
        # Prepend the chatter item and keep only the latest entries.
        self._chatter.insert(0, message)
        # Trim chatter to the most recent entries.
        self._chatter = self._chatter[:10]
        # Log the chatter for visibility in CLI mode.
        self.logger.info("MQTT chatter topic=%s payload=%s", topic, payload)

    # Build the dashboard payload for rendering.
    def build_payload(self) -> dict:
        # Describe the payload construction behavior.
        """Build the display payload."""
        # Assemble the payload dictionary for the display renderer.
        return {
            # Stamp the payload with the generation time.
            "generated_at": datetime.now(timezone.utc).isoformat(),
            # Include the latest sensor readings.
            "sensors": [asdict(reading) for reading in self._readings],
            # Include the recent MQTT chatter messages.
            "chatter": [asdict(message) for message in self._chatter],
            # Close the payload dictionary literal.
        }


# Configure command-line arguments for the display dashboard scaffold.
def build_parser() -> argparse.ArgumentParser:
    # Describe the parser construction behavior.
    """Build argument parser for CLI usage."""
    # Configure argument parser for command-line invocation.
    parser = argparse.ArgumentParser(description="KITT Display Dashboard (scaffold)")
    # Accept placeholder inputs for the simulation loop.
    parser.add_argument("--ticks", type=int, default=3, help="Number of update cycles")
    # Accept the log level so operators can change verbosity.
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    # Return the configured parser to the caller.
    return parser


# Produce one simulated dashboard update cycle.
def simulate_cycle(display: DisplayDashboard) -> None:
    # Describe the simulation behavior.
    """Generate a simulated update cycle."""
    # Generate simulated sensor values for the display.
    temp_c = round(TEMP_BASE_C + random.random() * TEMP_RANGE_C, 2)
    # Generate a simulated humidity percentage.
    humidity = round(HUMIDITY_BASE + random.random() * HUMIDITY_RANGE, 1)
    # Choose a simulated lift state.
    lift_state = random.choice(["raised", "lowered"])
    # Update the in-memory readings with formatted values.
    display.update_reading("fridge-temp", f"{temp_c} °C")
    # Update the in-memory readings with formatted values.
    display.update_reading("fridge-humidity", f"{humidity} %")
    # Update the in-memory readings with formatted values.
    display.update_reading("lift-state", lift_state)
    # Emit chatter messages as if MQTT updates arrived.
    display.add_chatter(
        # Provide the MQTT topic for fridge temperature readings.
        mqtt_topics.sensor_reading_topic("fridge-temp"),
        # Provide the JSON payload for the temperature reading.
        json.dumps({"temp_c": temp_c}),
        # Close the chatter call.
    )
    # Emit chatter messages as if MQTT updates arrived.
    display.add_chatter(
        # Provide the MQTT topic for fridge humidity readings.
        mqtt_topics.sensor_reading_topic("fridge-humidity"),
        # Provide the JSON payload for the humidity reading.
        json.dumps({"humidity": humidity}),
        # Close the chatter call.
    )
    # Emit chatter messages as if MQTT updates arrived.
    display.add_chatter("kitt/lift/state", json.dumps({"state": lift_state}))


# Run the display dashboard scaffold as a CLI script.
def main(argv: List[str] | None = None) -> int:
    # Describe the CLI entry point behavior.
    """Run the display dashboard scaffold."""
    # Parse CLI arguments or provided argv list.
    args = build_parser().parse_args(argv)
    # Initialize logging for stdout visibility in CLI runs.
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    # Create a named logger for this service.
    logger = logging.getLogger("kitt.display_dashboard")
    # Create the dashboard scaffold.
    display = DisplayDashboard(logger)

    # Run the requested number of simulated cycles.
    for _ in range(args.ticks):
        # Generate and log simulated sensor updates.
        simulate_cycle(display)
        # Build the display payload for this cycle.
        payload = display.build_payload()
        # Print JSON payloads for the front-end renderer.
        print(json.dumps(payload))
    # Exit cleanly for CLI integration.
    return 0


# Execute the CLI entry point when run directly.
if __name__ == "__main__":
    # Exit with the status code from main.
    sys.exit(main())
