#!/usr/bin/env python3
"""Train orchestrator service.

Simple: Coordinates train movement requests and publishes command intents.
Technical: Placeholder CLI service with logging for order/sensor events and routing.

Missing info for further development:
- Inputs: Order payload schema, sensor event schema, layout topology data.
- Outputs: Command payload schema for JMRI, telemetry payloads for UI.
- Actions: Route reservation lifecycle, lock acquisition, conflict resolution.
- Methods: State storage strategy, retry/backoff rules, safety interlocks.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field
from typing import Dict, List

from services.utils import mqtt_topics


@dataclass
class RouteReservation:
    """Represents a route reservation request."""

    order_id: str
    siding: str
    train_id: str
    status: str = "pending"
    checkpoints: List[str] = field(default_factory=list)


class TrainOrchestrator:
    """Minimal orchestrator scaffold with in-memory state."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self._reservations: Dict[str, RouteReservation] = {}

    def handle_order(self, order_id: str, siding: str, train_id: str) -> RouteReservation:
        """Create a placeholder reservation and log intended actions."""
        reservation = RouteReservation(order_id=order_id, siding=siding, train_id=train_id)
        self._reservations[order_id] = reservation
        self.logger.info(
            "Order received: order_id=%s siding=%s train_id=%s topic=%s",
            order_id,
            siding,
            train_id,
            mqtt_topics.ORDER_NEW,
        )
        self.logger.info(
            "Publishing JMRI command placeholder on %s",
            mqtt_topics.jmri_command_topic("dispatch"),
        )
        return reservation

    def handle_sensor_update(self, sensor_id: str, state: str) -> None:
        """Log a placeholder sensor update."""
        self.logger.info(
            "Sensor update: sensor_id=%s state=%s topic=%s",
            sensor_id,
            state,
            mqtt_topics.sensor_state_topic(sensor_id),
        )

    def list_reservations(self) -> List[RouteReservation]:
        """Return current reservations."""
        return list(self._reservations.values())


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI usage."""
    parser = argparse.ArgumentParser(description="KITT Train Orchestrator (scaffold)")
    parser.add_argument("--order-id", default="order-001", help="Order identifier")
    parser.add_argument("--siding", default="siding-a", help="Target siding")
    parser.add_argument("--train-id", default="train-1", help="Train identifier")
    parser.add_argument("--sensor-id", default="sensor-1", help="Sensor identifier")
    parser.add_argument("--sensor-state", default="occupied", help="Sensor state")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser


def main(argv: List[str] | None = None) -> int:
    """Run the orchestrator scaffold."""
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("kitt.train_orchestrator")

    orchestrator = TrainOrchestrator(logger)
    orchestrator.handle_order(args.order_id, args.siding, args.train_id)
    orchestrator.handle_sensor_update(args.sensor_id, args.sensor_state)

    logger.info("Active reservations: %s", orchestrator.list_reservations())
    return 0


if __name__ == "__main__":
    sys.exit(main())
