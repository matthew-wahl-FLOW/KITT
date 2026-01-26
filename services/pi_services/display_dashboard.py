#!/usr/bin/env python3
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

import argparse
import json
import logging
import random
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List

from services.utils import mqtt_topics

TEMP_BASE_C = 3.0
TEMP_RANGE_C = 4.0
HUMIDITY_BASE = 52.0
HUMIDITY_RANGE = 6.0


@dataclass
class SensorReading:
    """Represents a sensor reading for the display."""

    sensor_id: str
    value: str
    updated: str


@dataclass
class MqttMessage:
    """Represents a MQTT chatter line."""

    topic: str
    payload: str
    timestamp: str


class DisplayDashboard:
    """Builds the payload for the Pi display."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self._readings: List[SensorReading] = []
        self._chatter: List[MqttMessage] = []

    def update_reading(self, sensor_id: str, value: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        reading = SensorReading(sensor_id=sensor_id, value=value, updated=timestamp)
        self._readings = [r for r in self._readings if r.sensor_id != sensor_id]
        self._readings.insert(0, reading)
        self.logger.info(
            "Sensor reading sensor_id=%s value=%s topic=%s",
            sensor_id,
            value,
            mqtt_topics.sensor_reading_topic(sensor_id),
        )

    def add_chatter(self, topic: str, payload: str) -> None:
        message = MqttMessage(
            topic=topic,
            payload=payload,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._chatter.insert(0, message)
        self._chatter = self._chatter[:10]
        self.logger.info("MQTT chatter topic=%s payload=%s", topic, payload)

    def build_payload(self) -> dict:
        """Build the display payload."""
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sensors": [asdict(reading) for reading in self._readings],
            "chatter": [asdict(message) for message in self._chatter],
        }


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI usage."""
    parser = argparse.ArgumentParser(description="KITT Display Dashboard (scaffold)")
    parser.add_argument("--ticks", type=int, default=3, help="Number of update cycles")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser


def simulate_cycle(display: DisplayDashboard) -> None:
    """Generate a simulated update cycle."""
    temp_c = round(TEMP_BASE_C + random.random() * TEMP_RANGE_C, 2)
    humidity = round(HUMIDITY_BASE + random.random() * HUMIDITY_RANGE, 1)
    lift_state = random.choice(["raised", "lowered"])
    display.update_reading("fridge-temp", f"{temp_c} °C")
    display.update_reading("fridge-humidity", f"{humidity} %")
    display.update_reading("lift-state", lift_state)
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
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("kitt.display_dashboard")
    display = DisplayDashboard(logger)

    for _ in range(args.ticks):
        simulate_cycle(display)
        payload = display.build_payload()
        print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
