"""Integration simulation scaffold for a train run.

Simple: Exercises orchestrator scaffolds with placeholder values.
Technical: Uses unittest to ensure basic interactions run without errors.

Missing info for further development:
- Inputs: Realistic sensor timelines and layout topology.
- Outputs: Expected command sequencing and state transitions.
- Actions: Simulated MQTT broker and message ordering.
- Methods: Assertions against telemetry streams and timing constraints.
"""

import logging
import unittest

from services.pi_services import train_orchestrator


class TestSimTrainRun(unittest.TestCase):
    def test_simulated_run(self) -> None:
        orchestrator = train_orchestrator.TrainOrchestrator(logging.getLogger("test"))
        reservation = orchestrator.handle_order("order-1", "siding-a", "train-1")
        orchestrator.handle_sensor_update("sensor-1", "occupied")
        self.assertEqual(reservation.order_id, "order-1")


if __name__ == "__main__":
    unittest.main()
