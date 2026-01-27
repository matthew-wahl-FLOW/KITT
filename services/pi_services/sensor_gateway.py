#!/usr/bin/env python3
# Use env to locate the system's Python 3 interpreter when run as a script.
"""Sensor gateway service.

Overview: Normalizes sensor events into standard MQTT topics.
Details: Placeholder gateway that logs normalization output.

Missing info for further development:
- Inputs: Raw sensor payload formats, validation rules.
- Outputs: Normalized payload schema and health status fields.
- Actions: Health check cadence and offline policy.
- Methods: MQTT subscription list and message acknowledgement behavior.
"""

from __future__ import annotations
# Defer annotation evaluation to keep forward references simple.

# Standard library imports for CLI parsing, logging, and dataclass support.
import argparse
import logging
import sys
from dataclasses import dataclass
from typing import List

# Shared MQTT topic helpers for consistent topic construction.
from services.utils import mqtt_topics


@dataclass
# Simple record for a raw sensor message payload.
class SensorMessage:
    """Represents a raw sensor message."""

    sensor_id: str
    sensor_type: str
    value: str


class SensorGateway:
    """Minimal sensor gateway scaffold."""

    def __init__(self, logger: logging.Logger) -> None:
        # Store the logger for CLI output.
        self.logger = logger

    def normalize(self, message: SensorMessage) -> None:
        """Log a placeholder normalization action."""
        # Build the normalized topic and log the placeholder action.
        topic = mqtt_topics.sensor_state_topic(message.sensor_id)
        self.logger.info(
            "Normalized sensor message sensor_id=%s type=%s value=%s topic=%s",
            message.sensor_id,
            message.sensor_type,
            message.value,
            topic,
        )

    def publish_health(self, sensor_id: str, status: str) -> None:
        """Log a placeholder health publish."""
        # Build the health topic and log the placeholder action.
        topic = mqtt_topics.sensor_health_topic(sensor_id)
        self.logger.info("Sensor health sensor_id=%s status=%s topic=%s", sensor_id, status, topic)


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI usage."""
    # Configure argument parser for command-line invocation.
    parser = argparse.ArgumentParser(description="KITT Sensor Gateway (scaffold)")
    # Accept placeholder inputs for one sensor message and health update.
    parser.add_argument("--sensor-id", default="sensor-1", help="Sensor identifier")
    parser.add_argument("--sensor-type", default="ir", help="Sensor type")
    parser.add_argument("--value", default="active", help="Sensor value")
    parser.add_argument("--health", default="online", help="Health status")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    # Return the configured parser to the caller.
    return parser


def main(argv: List[str] | None = None) -> int:
    """Run the sensor gateway scaffold."""
    # Parse CLI arguments or provided argv list.
    args = build_parser().parse_args(argv)
    # Initialize logging for stdout visibility in CLI runs.
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("kitt.sensor_gateway")

    # Instantiate the gateway and emit placeholder messages.
    gateway = SensorGateway(logger)
    gateway.normalize(
        SensorMessage(sensor_id=args.sensor_id, sensor_type=args.sensor_type, value=args.value)
    )
    gateway.publish_health(args.sensor_id, args.health)
    # Exit cleanly for CLI integration.
    return 0


if __name__ == "__main__":
    # Execute the CLI entry point when run directly.
    sys.exit(main())
