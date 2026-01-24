#!/usr/bin/env python3
"""Load cell monitor service.

Simple: Tracks load cell readings to verify beverage presence.
Technical: Placeholder monitor with calibration state and logging output.

Missing info for further development:
- Inputs: Raw ADC readings, sampling rate, calibration payloads.
- Outputs: Event payload schemas for load/unload/errors.
- Actions: Calibration workflow, alert escalation.
- Methods: Smoothing/filtering, hardware interface details.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from typing import List

from services.utils import mqtt_topics


@dataclass
class Calibration:
    """Calibration parameters for a load cell."""

    offset: float
    scale: float


class LoadCellMonitor:
    """Minimal load cell monitor scaffold."""

    def __init__(self, calibration: Calibration, logger: logging.Logger) -> None:
        self.calibration = calibration
        self.logger = logger

    def apply_calibration(self, raw_value: float) -> float:
        """Apply calibration to a raw value."""
        return (raw_value - self.calibration.offset) * self.calibration.scale

    def handle_weight(self, raw_value: float) -> None:
        """Log a placeholder weight event."""
        calibrated = self.apply_calibration(raw_value)
        topic = mqtt_topics.order_event_topic("loadcell")
        self.logger.info("Weight reading raw=%s calibrated=%s topic=%s", raw_value, calibrated, topic)

    def calibrate(self, offset: float, scale: float) -> None:
        """Update calibration values."""
        self.calibration = Calibration(offset=offset, scale=scale)
        self.logger.info("Calibration updated offset=%s scale=%s", offset, scale)


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI usage."""
    parser = argparse.ArgumentParser(description="KITT Load Cell Monitor (scaffold)")
    parser.add_argument("--raw", type=float, default=12.3, help="Raw load cell reading")
    parser.add_argument("--offset", type=float, default=0.0, help="Calibration offset")
    parser.add_argument("--scale", type=float, default=1.0, help="Calibration scale")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser


def main(argv: List[str] | None = None) -> int:
    """Run the load cell monitor scaffold."""
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("kitt.loadcell_monitor")

    monitor = LoadCellMonitor(Calibration(offset=args.offset, scale=args.scale), logger)
    monitor.handle_weight(args.raw)
    return 0


if __name__ == "__main__":
    sys.exit(main())
