# Document the purpose of this unit test module.
"""Unit tests for the RFID reader bridge (no hardware, no JMRI)."""

# Import unittest for the test framework.
import unittest

# Import the bridge module under test.
from services.pi_services import rfid_bridge as rb


# Provide a controllable clock for debounce tests.
class FakeClock:
    # Start the clock at a chosen time.
    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    # Return the current fake time.
    def __call__(self) -> float:
        return self.now


# Record every sink call so tests can check order and content.
class FakeSink:
    # Optionally fail memory writes to test error handling.
    def __init__(self, fail_memory: bool = False) -> None:
        self.calls = []
        self.fail_memory = fail_memory

    # Record a memory write, or raise if configured to fail.
    def set_memory(self, name: str, value: str) -> None:
        if self.fail_memory:
            raise rb.JmriError("memory unavailable")
        self.calls.append(("memory", name, value))

    # Record a sensor state change.
    def set_sensor(self, name: str, active: bool) -> None:
        self.calls.append(("sensor", name, active))


# Validate TAG line parsing.
class ParseTagLineTests(unittest.TestCase):
    # Accept a well-formed TAG line.
    def test_accepts_tag_line(self) -> None:
        self.assertEqual(rb.parse_tag_line("TAG 0A1B2C3D4E"), "0A1B2C3D4E")

    # Accept lowercase input and surrounding whitespace, returning uppercase.
    def test_accepts_lowercase_and_whitespace(self) -> None:
        self.assertEqual(rb.parse_tag_line("  tag 0a1b2c3d4e\r"), "0A1B2C3D4E")

    # Reject status lines, short and long IDs, non-hex characters, and empty input.
    def test_rejects_other_lines(self) -> None:
        for line in [
            "READY rfid_reader_mega",
            "ERR checksum",
            "TAG 0A1B",
            "TAG 0A1B2C3D4EFF",
            "TAG 0A1B2C3D4G",
            "TAG",
            "",
        ]:
            with self.subTest(line=line):
                self.assertIsNone(rb.parse_tag_line(line))


# Validate repeat-read suppression.
class TagDebouncerTests(unittest.TestCase):
    # The first read of a tag is always a new event.
    def test_first_read_accepted(self) -> None:
        debouncer = rb.TagDebouncer(1.5, clock=FakeClock(0.0))
        self.assertTrue(debouncer.accept("AAAA"))

    # A repeat within the hold window is suppressed.
    def test_repeat_within_hold_suppressed(self) -> None:
        clock = FakeClock(0.0)
        debouncer = rb.TagDebouncer(1.5, clock=clock)
        self.assertTrue(debouncer.accept("AAAA"))
        clock.now = 1.0
        self.assertFalse(debouncer.accept("AAAA"))

    # A card held in range keeps extending the window, so it yields one event.
    def test_held_tag_extends_window(self) -> None:
        clock = FakeClock(0.0)
        debouncer = rb.TagDebouncer(1.5, clock=clock)
        results = []
        for t in [0.0, 1.0, 2.0, 3.0]:
            clock.now = t
            results.append(debouncer.accept("AAAA"))
        self.assertEqual(results, [True, False, False, False])

    # The same tag after a gap longer than the hold window is a new event.
    def test_same_tag_after_gap_accepted(self) -> None:
        clock = FakeClock(0.0)
        debouncer = rb.TagDebouncer(1.5, clock=clock)
        self.assertTrue(debouncer.accept("AAAA"))
        clock.now = 5.0
        self.assertTrue(debouncer.accept("AAAA"))

    # A different tag is accepted immediately.
    def test_different_tag_accepted_immediately(self) -> None:
        clock = FakeClock(0.0)
        debouncer = rb.TagDebouncer(1.5, clock=clock)
        self.assertTrue(debouncer.accept("AAAA"))
        clock.now = 0.1
        self.assertTrue(debouncer.accept("BBBB"))


# Validate the line-to-JMRI flow.
class RfidBridgeTests(unittest.TestCase):
    # Build a bridge with a fake sink, a fake clock, and a recorded sleep.
    def _bridge(self, sink: FakeSink, memory: bool = True):
        sleeps = []
        clock = FakeClock(0.0)
        bridge = rb.RfidBridge(
            sink=sink,
            sensor_name="ISRFID1",
            memory_name="IMRFIDLast" if memory else None,
            debouncer=rb.TagDebouncer(1.5, clock=clock),
            pulse_seconds=1.0,
            sleep=sleeps.append,
        )
        return bridge, sleeps, clock

    # A new read sets the memory, pulses the sensor ACTIVE, then INACTIVE.
    def test_read_sets_memory_then_pulses_sensor(self) -> None:
        sink = FakeSink()
        bridge, sleeps, _ = self._bridge(sink)
        self.assertEqual(bridge.handle_line("TAG 0A1B2C3D4E"), "0A1B2C3D4E")
        self.assertEqual(
            sink.calls,
            [
                ("memory", "IMRFIDLast", "0A1B2C3D4E"),
                ("sensor", "ISRFID1", True),
                ("sensor", "ISRFID1", False),
            ],
        )
        self.assertEqual(sleeps, [1.0])

    # A repeat read produces no JMRI traffic.
    def test_repeat_read_is_ignored(self) -> None:
        sink = FakeSink()
        bridge, _, clock = self._bridge(sink)
        bridge.handle_line("TAG 0A1B2C3D4E")
        clock.now = 0.5
        self.assertIsNone(bridge.handle_line("TAG 0A1B2C3D4E"))
        self.assertEqual(len(sink.calls), 3)

    # Status and error lines are ignored.
    def test_non_tag_line_ignored(self) -> None:
        sink = FakeSink()
        bridge, _, _ = self._bridge(sink)
        self.assertIsNone(bridge.handle_line("READY rfid_reader_mega"))
        self.assertIsNone(bridge.handle_line("ERR checksum"))
        self.assertEqual(sink.calls, [])

    # A failed memory write is logged, and the sensor still pulses.
    def test_memory_failure_still_pulses_sensor(self) -> None:
        sink = FakeSink(fail_memory=True)
        bridge, _, _ = self._bridge(sink)
        self.assertEqual(bridge.handle_line("TAG 0A1B2C3D4E"), "0A1B2C3D4E")
        self.assertEqual(
            sink.calls,
            [("sensor", "ISRFID1", True), ("sensor", "ISRFID1", False)],
        )

    # With memory disabled, only the sensor is driven.
    def test_no_memory_mode_only_drives_sensor(self) -> None:
        sink = FakeSink()
        bridge, _, _ = self._bridge(sink, memory=False)
        bridge.handle_line("TAG 0A1B2C3D4E")
        self.assertEqual(
            sink.calls,
            [("sensor", "ISRFID1", True), ("sensor", "ISRFID1", False)],
        )

    # The sensor returns to INACTIVE even if the pause is interrupted.
    def test_sensor_reset_when_pause_raises(self) -> None:
        sink = FakeSink()

        # Simulate an interrupted pause.
        def interrupted(_seconds: float) -> None:
            raise RuntimeError("interrupted")

        bridge = rb.RfidBridge(
            sink=sink,
            sensor_name="ISRFID1",
            memory_name=None,
            debouncer=rb.TagDebouncer(1.5, clock=FakeClock(0.0)),
            pulse_seconds=1.0,
            sleep=interrupted,
        )
        with self.assertRaises(RuntimeError):
            bridge.handle_line("TAG 0A1B2C3D4E")
        self.assertEqual(sink.calls[-1], ("sensor", "ISRFID1", False))


# Validate the JSON sink request bodies (no network access).
class JsonJmriSinkPayloadTests(unittest.TestCase):
    # Active uses JMRI state 2.
    def test_sensor_active_payload(self) -> None:
        self.assertEqual(
            rb.JsonJmriSink.sensor_payload("ISRFID1", True),
            {"name": "ISRFID1", "state": 2},
        )

    # Inactive uses JMRI state 4.
    def test_sensor_inactive_payload(self) -> None:
        self.assertEqual(
            rb.JsonJmriSink.sensor_payload("ISRFID1", False),
            {"name": "ISRFID1", "state": 4},
        )

    # Memory payload carries the tag ID as the value.
    def test_memory_payload(self) -> None:
        self.assertEqual(
            rb.JsonJmriSink.memory_payload("IMRFIDLast", "0A1B2C3D4E"),
            {"name": "IMRFIDLast", "value": "0A1B2C3D4E"},
        )


# Run the tests when executing this module directly.
if __name__ == "__main__":
    unittest.main()
