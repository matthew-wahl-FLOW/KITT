#!/usr/bin/env python3
# Use env to locate the system's Python 3 interpreter when run as a script.
"""JMRI bridge service.

Overview: Logs incoming command intents destined for JMRI.
Details: Placeholder bridge that mirrors commands/events via logging only.

Missing info for further development:
- Inputs: JMRI connection details, command payload schema.
- Outputs: Event payload schema for train/turnout updates.
- Actions: Connection lifecycle, retry policies, idempotency.
- Methods: JMRI API integration specifics, error mapping.
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
# Simple record for a JMRI command payload.
class JmriCommand:
    """Represents a command to be sent to JMRI."""

    command: str
    target: str
    value: str


class JmriBridge:
    """Minimal JMRI bridge scaffold."""

    def __init__(self, logger: logging.Logger) -> None:
        # Store the logger for CLI output.
        self.logger = logger

    def handle_command(self, command: JmriCommand) -> None:
        """Log a placeholder command translation."""
        # Build the topic for the command and log the simulated dispatch.
        topic = mqtt_topics.jmri_command_topic(command.command)
        self.logger.info(
            "JMRI command received command=%s target=%s value=%s topic=%s",
            command.command,
            command.target,
            command.value,
            topic,
        )

    def publish_event(self, event: str, payload: str) -> None:
        """Log a placeholder event publish."""
        # Build the event topic and log the placeholder publish action.
        topic = mqtt_topics.jmri_event_topic(event)
        self.logger.info("JMRI event publish event=%s payload=%s topic=%s", event, payload, topic)


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI usage."""
    # Configure argument parser for command-line invocation.
    parser = argparse.ArgumentParser(description="KITT JMRI Bridge (scaffold)")
    # Accept placeholder inputs for one command and one event.
    parser.add_argument("--command", default="dispatch", help="Command name")
    parser.add_argument("--target", default="train-1", help="Command target")
    parser.add_argument("--value", default="start", help="Command value")
    parser.add_argument("--event", default="status", help="Event name")
    parser.add_argument("--payload", default="ok", help="Event payload")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    # Return the configured parser to the caller.
    return parser


def main(argv: List[str] | None = None) -> int:
    """Run the JMRI bridge scaffold."""
    # Parse CLI arguments or provided argv list.
    args = build_parser().parse_args(argv)
    # Initialize logging for stdout visibility in CLI runs.
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("kitt.jmri_bridge")

    # Instantiate the bridge and emit a placeholder command/event pair.
    bridge = JmriBridge(logger)
    bridge.handle_command(JmriCommand(command=args.command, target=args.target, value=args.value))
    bridge.publish_event(args.event, args.payload)
    # Exit cleanly for CLI integration.
    return 0


if __name__ == "__main__":
    # Execute the CLI entry point when run directly.
    sys.exit(main())
