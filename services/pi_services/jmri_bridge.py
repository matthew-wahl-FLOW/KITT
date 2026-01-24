#!/usr/bin/env python3
"""JMRI bridge service.

Simple: Logs incoming command intents destined for JMRI.
Technical: Placeholder bridge that mirrors commands/events via logging only.

Missing info for further development:
- Inputs: JMRI connection details, command payload schema.
- Outputs: Event payload schema for train/turnout updates.
- Actions: Connection lifecycle, retry policies, idempotency.
- Methods: JMRI API integration specifics, error mapping.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from typing import List

from services.utils import mqtt_topics


@dataclass
class JmriCommand:
    """Represents a command to be sent to JMRI."""

    command: str
    target: str
    value: str


class JmriBridge:
    """Minimal JMRI bridge scaffold."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def handle_command(self, command: JmriCommand) -> None:
        """Log a placeholder command translation."""
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
        topic = mqtt_topics.jmri_event_topic(event)
        self.logger.info("JMRI event publish event=%s payload=%s topic=%s", event, payload, topic)


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI usage."""
    parser = argparse.ArgumentParser(description="KITT JMRI Bridge (scaffold)")
    parser.add_argument("--command", default="dispatch", help="Command name")
    parser.add_argument("--target", default="train-1", help="Command target")
    parser.add_argument("--value", default="start", help="Command value")
    parser.add_argument("--event", default="status", help="Event name")
    parser.add_argument("--payload", default="ok", help="Event payload")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser


def main(argv: List[str] | None = None) -> int:
    """Run the JMRI bridge scaffold."""
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("kitt.jmri_bridge")

    bridge = JmriBridge(logger)
    bridge.handle_command(JmriCommand(command=args.command, target=args.target, value=args.value))
    bridge.publish_event(args.event, args.payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
