#!/usr/bin/env python3
"""RFID reader bridge.

Reads "TAG <id>" lines from the Mega's USB serial port (firmware/arduino/rfid_reader_mega)
and reflects each read in JMRI: an internal memory holds the last tag ID, and an
internal sensor pulses ACTIVE for a moment.

JMRI remains the authority for layout state. This bridge only reports reads.

The JMRI JSON endpoints used by JsonJmriSink are assumptions until verified on your
JMRI version. Check them with curl (see jmri/rfid_reader_setup.md) before relying on
the JSON sink. Use --dry-run to exercise the serial path without JMRI.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Callable, Iterator, Optional, Protocol
from urllib.parse import quote

TAG_LINE_RE = re.compile(r"^TAG ([0-9A-F]{10})$")

# JMRI sensor states (jmri.Sensor): ACTIVE = 2, INACTIVE = 4.
JMRI_SENSOR_ACTIVE = 2
JMRI_SENSOR_INACTIVE = 4


class JmriError(Exception):
    """Raised when JMRI cannot be updated."""


def parse_tag_line(line: str) -> Optional[str]:
    """Return the 10-character uppercase tag ID for a TAG line, or None for anything else."""
    match = TAG_LINE_RE.match(line.strip().upper())
    return match.group(1) if match else None


class TagDebouncer:
    """Collapses repeat reads of the same tag while it stays in range."""

    def __init__(self, hold_seconds: float, clock: Callable[[], float] = time.monotonic) -> None:
        self._hold = hold_seconds
        self._clock = clock
        self._last_tag: Optional[str] = None
        self._last_seen: Optional[float] = None

    def accept(self, tag: str) -> bool:
        """Return True if this read is a new tag event, False if it is a repeat."""
        now = self._clock()
        repeat = (
            tag == self._last_tag
            and self._last_seen is not None
            and (now - self._last_seen) < self._hold
        )
        # Every read of a tag that is still present extends the hold window.
        self._last_tag = tag
        self._last_seen = now
        return not repeat


class JmriSink(Protocol):
    """Where tag events go. Implemented by LoggingSink and JsonJmriSink."""

    def set_memory(self, name: str, value: str) -> None: ...

    def set_sensor(self, name: str, active: bool) -> None: ...


class LoggingSink:
    """Dry-run sink: logs what would be sent to JMRI."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def set_memory(self, name: str, value: str) -> None:
        self._logger.info("DRY RUN memory %s = %s", name, value)

    def set_sensor(self, name: str, active: bool) -> None:
        self._logger.info("DRY RUN sensor %s = %s", name, "ACTIVE" if active else "INACTIVE")


class JsonJmriSink:
    """Sends updates through the JMRI JSON server with HTTP PUT.

    Endpoint shapes are assumptions to verify on your JMRI version:
      PUT {base}/json/memory/{name}   body {"name": name, "value": value}
      PUT {base}/json/sensor/{name}   body {"name": name, "state": 2 | 4}
    """

    def __init__(self, base_url: str, timeout: float = 2.0) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout

    @staticmethod
    def memory_payload(name: str, value: str) -> dict:
        return {"name": name, "value": value}

    @staticmethod
    def sensor_payload(name: str, active: bool) -> dict:
        state = JMRI_SENSOR_ACTIVE if active else JMRI_SENSOR_INACTIVE
        return {"name": name, "state": state}

    def set_memory(self, name: str, value: str) -> None:
        self._put(f"/json/memory/{quote(name, safe='')}", self.memory_payload(name, value))

    def set_sensor(self, name: str, active: bool) -> None:
        self._put(f"/json/sensor/{quote(name, safe='')}", self.sensor_payload(name, active))

    def _put(self, path: str, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self._base + path,
            data=body,
            method="PUT",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                response.read()
        except (urllib.error.URLError, OSError) as exc:
            raise JmriError(f"PUT {path} failed: {exc}") from exc


class RfidBridge:
    """Turns TAG lines into JMRI memory and sensor updates."""

    def __init__(
        self,
        sink: JmriSink,
        sensor_name: str,
        memory_name: Optional[str],
        debouncer: TagDebouncer,
        pulse_seconds: float = 1.0,
        sleep: Callable[[float], None] = time.sleep,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._sink = sink
        self._sensor_name = sensor_name
        self._memory_name = memory_name
        self._debouncer = debouncer
        self._pulse = pulse_seconds
        self._sleep = sleep
        self._log = logger or logging.getLogger("kitt.rfid_bridge")

    def handle_line(self, line: str) -> Optional[str]:
        """Process one line from the reader. Returns the tag ID if it was a new read."""
        tag = parse_tag_line(line)
        if tag is None:
            if line.strip():
                self._log.debug("ignored reader line: %s", line.strip())
            return None
        if not self._debouncer.accept(tag):
            return None

        self._log.info("RFID read tag=%s", tag)
        if self._memory_name is not None:
            self._try("memory", lambda: self._sink.set_memory(self._memory_name, tag))
        self._try("sensor on", lambda: self._sink.set_sensor(self._sensor_name, True))
        try:
            self._sleep(self._pulse)
        finally:
            self._try("sensor off", lambda: self._sink.set_sensor(self._sensor_name, False))
        return tag

    def _try(self, what: str, action: Callable[[], None]) -> None:
        try:
            action()
        except JmriError as exc:
            self._log.error("JMRI %s update failed: %s", what, exc)


def open_serial_lines(path: str, baud: int) -> Iterator[str]:
    """Yield text lines from a serial device, configured as raw 8N1 with termios (stdlib)."""
    import termios  # Unix only; imported here so the module imports on other platforms

    speeds = {9600: termios.B9600, 115200: termios.B115200}
    if baud not in speeds:
        raise ValueError(f"unsupported baud rate {baud}")

    fd = os.open(path, os.O_RDONLY | os.O_NOCTTY)
    try:
        attrs = termios.tcgetattr(fd)
        attrs[0] = 0  # iflag: raw input
        attrs[1] = 0  # oflag: raw output
        attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL  # cflag: 8N1
        attrs[3] = 0  # lflag: non-canonical, no echo
        attrs[4] = speeds[baud]
        attrs[5] = speeds[baud]
        attrs[6][termios.VMIN] = 1
        attrs[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        termios.tcflush(fd, termios.TCIFLUSH)

        pending = b""
        while True:
            chunk = os.read(fd, 256)
            if not chunk:
                raise EOFError(f"{path} closed")
            pending += chunk
            while b"\n" in pending:
                raw, pending = pending.split(b"\n", 1)
                yield raw.decode("ascii", errors="replace").rstrip("\r")
    finally:
        os.close(fd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KITT RFID reader bridge (Mega -> JMRI)")
    parser.add_argument("--port", default="/dev/kitt/rfid0", help="reader serial device")
    parser.add_argument("--baud", type=int, default=115200, help="USB serial baud (Mega output)")
    parser.add_argument("--sensor", default="ISRFID1", help="JMRI internal sensor system name")
    parser.add_argument("--memory", default="IMRFIDLast", help="JMRI internal memory system name")
    parser.add_argument("--no-memory", action="store_true", help="do not update the tag memory")
    parser.add_argument("--jmri-url", default="http://127.0.0.1:12080", help="JMRI JSON server base URL")
    parser.add_argument("--hold-seconds", type=float, default=1.5, help="repeat-read window per tag")
    parser.add_argument("--pulse-seconds", type=float, default=1.0, help="how long the sensor stays ACTIVE")
    parser.add_argument("--dry-run", action="store_true", help="log instead of calling JMRI")
    parser.add_argument("--log-level", default="INFO", help="logging level")
    return parser


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=args.log_level.upper(), format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("kitt.rfid_bridge")

    sink: JmriSink = LoggingSink(logger) if args.dry_run else JsonJmriSink(args.jmri_url)
    bridge = RfidBridge(
        sink=sink,
        sensor_name=args.sensor,
        memory_name=None if args.no_memory else args.memory,
        debouncer=TagDebouncer(args.hold_seconds),
        pulse_seconds=args.pulse_seconds,
        logger=logger,
    )

    logger.info("Reading %s at %d baud (dry_run=%s)", args.port, args.baud, args.dry_run)
    try:
        for line in open_serial_lines(args.port, args.baud):
            if line.startswith(("READY", "ERR")):
                logger.info("reader: %s", line)
                continue
            bridge.handle_line(line)
    except KeyboardInterrupt:
        logger.info("stopping")
        return 0
    except (OSError, EOFError, ValueError) as exc:
        logger.error("serial port failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
