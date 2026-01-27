#!/usr/bin/env python3
# Use env to locate the system's Python 3 interpreter when run as a script.
"""Train orchestrator service.

Overview: Coordinates train movement requests and publishes command intents.
Details: Placeholder CLI service with logging for order/sensor events and routing.

Missing info for further development:
- Inputs: Order payload schema, sensor event schema, layout topology data.
- Outputs: Command payload schema for JMRI, telemetry payloads for UI.
- Actions: Route reservation lifecycle, lock acquisition, conflict resolution.
- Methods: State storage strategy, retry/backoff rules, safety interlocks.
"""

from __future__ import annotations
# Defer annotation evaluation to keep forward references simple.

# Standard library imports for CLI parsing, logging, and dataclass support.
import argparse
import logging
import sys
from dataclasses import dataclass, field
from typing import Dict, List

# Shared MQTT topic helpers for consistent topic construction.
from services.utils import mqtt_topics


@dataclass
# Simple record for tracking reservation metadata in memory.
class RouteReservation:
    """Represents a route reservation request."""

    # Core identifiers for the reservation request.
    order_id: str
    siding: str
    train_id: str
    # Mutable state for orchestration progress tracking.
    status: str = "pending"
    checkpoints: List[str] = field(default_factory=list)


class TrainOrchestrator:
    """Minimal orchestrator scaffold with in-memory state."""

    def __init__(self, logger: logging.Logger) -> None:
        # Hold a logger for structured output from CLI usage.
        self.logger = logger
        # Track reservations by order_id in memory for the scaffold.
        self._reservations: Dict[str, RouteReservation] = {}

    def handle_order(self, order_id: str, siding: str, train_id: str) -> RouteReservation:
        """Create a placeholder reservation and log intended actions."""
        # Create and store a reservation to model the orchestration workflow.
        reservation = RouteReservation(order_id=order_id, siding=siding, train_id=train_id)
        self._reservations[order_id] = reservation
        # Log the receipt of the order with the expected MQTT topic.
        self.logger.info(
            "Order received: order_id=%s siding=%s train_id=%s topic=%s",
            order_id,
            siding,
            train_id,
            mqtt_topics.ORDER_NEW,
        )
        # Log where a dispatch command would be published for JMRI.
        self.logger.info(
            "Publishing JMRI command placeholder on %s",
            mqtt_topics.jmri_command_topic("dispatch"),
        )
        return reservation

    def handle_sensor_update(self, sensor_id: str, state: str) -> None:
        """Log a placeholder sensor update."""
        # Log the sensor update and the normalized state topic.
        self.logger.info(
            "Sensor update: sensor_id=%s state=%s topic=%s",
            sensor_id,
            state,
            mqtt_topics.sensor_state_topic(sensor_id),
        )

    def list_reservations(self) -> List[RouteReservation]:
        """Return current reservations."""
        # Return a copy of the reservation list for callers.
        return list(self._reservations.values())


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI usage."""
    # Configure argument parser for command-line invocation.
    parser = argparse.ArgumentParser(description="KITT Train Orchestrator (scaffold)")
    # Accept input values that simulate an order and sensor update.
    parser.add_argument("--order-id", default="order-001", help="Order identifier")
    parser.add_argument("--siding", default="siding-a", help="Target siding")
    parser.add_argument("--train-id", default="train-1", help="Train identifier")
    parser.add_argument("--sensor-id", default="sensor-1", help="Sensor identifier")
    parser.add_argument("--sensor-state", default="occupied", help="Sensor state")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    # Return the configured parser to the caller.
    return parser


def main(argv: List[str] | None = None) -> int:
    """Run the orchestrator scaffold."""
    # Parse CLI arguments or provided argv list.
    args = build_parser().parse_args(argv)
    # Initialize logging for stdout visibility in CLI runs.
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("kitt.train_orchestrator")

    # Instantiate the orchestrator and simulate one order flow.
    orchestrator = TrainOrchestrator(logger)
    orchestrator.handle_order(args.order_id, args.siding, args.train_id)
    orchestrator.handle_sensor_update(args.sensor_id, args.sensor_state)

    # Summarize the in-memory reservations to show scaffold behavior.
    logger.info("Active reservations: %s", orchestrator.list_reservations())
    # Exit cleanly for CLI integration.
    return 0


if __name__ == "__main__":
    # Execute the CLI entry point when run directly.
    sys.exit(main())
