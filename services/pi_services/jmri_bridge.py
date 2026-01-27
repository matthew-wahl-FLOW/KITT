#!/usr/bin/env python3
# Use env to locate the system's Python 3 interpreter when run as a script.
# Provide module-level context for the JMRI bridge service.
"""JMRI bridge service.

Overview: Logs incoming command intents destined for JMRI.
Details: Placeholder bridge that mirrors commands/events via logging only.

Missing info for further development:
- Inputs: JMRI connection details, command payload schema.
- Outputs: Event payload schema for train/turnout updates.
- Actions: Connection lifecycle, retry policies, idempotency.
- Methods: JMRI API integration specifics, error mapping.
"""

# Enable postponed evaluation so annotations can use forward references.
from __future__ import annotations

# Import argparse for command-line argument parsing.
import argparse
# Import logging for CLI output visibility.
import logging
# Import sys for CLI exit handling.
import sys
# Import dataclass to define structured command payloads.
from dataclasses import dataclass
# Import typing helper for list annotations.
from typing import List

# Import MQTT topic helpers to build JMRI-related topics.
from services.utils import mqtt_topics


# Enable dataclass generation for command payloads.
@dataclass
# Simple record for a JMRI command payload.
class JmriCommand:
    # Describe the JMRI command dataclass for maintainers.
    """Represents a command to be sent to JMRI."""

    # Store the command name such as dispatch or stop.
    command: str
    # Store the target identifier such as train or turnout.
    target: str
    # Store the command value such as start or thrown.
    value: str


# Provide a scaffold service that would connect to JMRI.
class JmriBridge:
    # Describe the JMRI bridge class for maintainers.
    """Minimal JMRI bridge scaffold."""

    # Initialize the bridge with a logger.
    def __init__(self, logger: logging.Logger) -> None:
        # Store the logger for CLI output.
        self.logger = logger

    # Handle a command by logging and formatting its topic.
    def handle_command(self, command: JmriCommand) -> None:
        # Describe the command handling behavior.
        """Log a placeholder command translation."""
        # Build the topic for the command and log the simulated dispatch.
        topic = mqtt_topics.jmri_command_topic(command.command)
        # Log the command details so operators can trace intent.
        self.logger.info(
            "JMRI command received command=%s target=%s value=%s topic=%s",
            command.command,
            command.target,
            command.value,
            topic,
        )

    # Publish a placeholder event from JMRI.
    def publish_event(self, event: str, payload: str) -> None:
        # Describe the event publishing behavior.
        """Log a placeholder event publish."""
        # Build the event topic and log the placeholder publish action.
        topic = mqtt_topics.jmri_event_topic(event)
        # Log the event so downstream services can see the expected output.
        self.logger.info("JMRI event publish event=%s payload=%s topic=%s", event, payload, topic)


# Build an argument parser for the CLI scaffold.
def build_parser() -> argparse.ArgumentParser:
    # Describe the parser construction behavior.
    """Build argument parser for CLI usage."""
    # Configure argument parser for command-line invocation.
    parser = argparse.ArgumentParser(description="KITT JMRI Bridge (scaffold)")
    # Accept placeholder inputs for one command and one event.
    parser.add_argument("--command", default="dispatch", help="Command name")
    # Accept a target identifier for the placeholder command.
    parser.add_argument("--target", default="train-1", help="Command target")
    # Accept a value for the placeholder command.
    parser.add_argument("--value", default="start", help="Command value")
    # Accept a placeholder event name.
    parser.add_argument("--event", default="status", help="Event name")
    # Accept a placeholder event payload.
    parser.add_argument("--payload", default="ok", help="Event payload")
    # Accept the log level so operators can control verbosity.
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    # Return the configured parser to the caller.
    return parser


# Run the JMRI bridge scaffold from the CLI.
def main(argv: List[str] | None = None) -> int:
    # Describe the CLI entry point behavior.
    """Run the JMRI bridge scaffold."""
    # Parse CLI arguments or provided argv list.
    args = build_parser().parse_args(argv)
    # Initialize logging for stdout visibility in CLI runs.
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    # Create a named logger for this service.
    logger = logging.getLogger("kitt.jmri_bridge")

    # Instantiate the bridge and emit a placeholder command/event pair.
    bridge = JmriBridge(logger)
    # Send the placeholder command into the bridge.
    bridge.handle_command(JmriCommand(command=args.command, target=args.target, value=args.value))
    # Publish a placeholder event for downstream listeners.
    bridge.publish_event(args.event, args.payload)
    # Exit cleanly for CLI integration.
    return 0


# Run the CLI entry point when this module is executed directly.
if __name__ == "__main__":
    # Exit with the status code from main.
    sys.exit(main())
