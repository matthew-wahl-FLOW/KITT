#!/usr/bin/env python3
"""Sensor gateway service.

Simple: Normalizes sensor events into standard MQTT topics.
Technical: Placeholder gateway that logs normalization output.

Missing info for further development:
- Inputs: Raw sensor payload formats, validation rules.
- Outputs: Normalized payload schema and health status fields.
- Actions: Health check cadence and offline policy.
- Methods: MQTT subscription list and message acknowledgement behavior.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from typing import List

from services.utils import mqtt_topics


@dataclass
class SensorMessage:
    """Represents a raw sensor message."""

    sensor_id: str
    sensor_type: str
    value: str


class SensorGateway:
    """Minimal sensor gateway scaffold."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def normalize(self, message: SensorMessage) -> None:
        """Log a placeholder normalization action."""
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
        topic = mqtt_topics.sensor_health_topic(sensor_id)
        self.logger.info("Sensor health sensor_id=%s status=%s topic=%s", sensor_id, status, topic)


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI usage."""
    parser = argparse.ArgumentParser(description="KITT Sensor Gateway (scaffold)")
    parser.add_argument("--sensor-id", default="sensor-1", help="Sensor identifier")
    parser.add_argument("--sensor-type", default="ir", help="Sensor type")
    parser.add_argument("--value", default="active", help="Sensor value")
    parser.add_argument("--health", default="online", help="Health status")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser


def main(argv: List[str] | None = None) -> int:
    """Run the sensor gateway scaffold."""
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("kitt.sensor_gateway")

    gateway = SensorGateway(logger)
    gateway.normalize(
        SensorMessage(sensor_id=args.sensor_id, sensor_type=args.sensor_type, value=args.value)
    )
    gateway.publish_health(args.sensor_id, args.health)
    return 0


if __name__ == "__main__":
    sys.exit(main())
