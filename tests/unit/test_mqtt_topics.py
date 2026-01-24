"""Unit tests for MQTT topic helpers.

Simple: Validates MQTT topic constants and formatting helpers.
Technical: Uses unittest to verify template contents and helper formatting.
"""

import unittest

from services.utils import mqtt_topics


class TestMqttTopics(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertTrue(mqtt_topics.ORDER_NEW.endswith("order/new"))
        self.assertIn("{train_id}", mqtt_topics.TRAIN_LOCATION)
        self.assertIn("{sensor_id}", mqtt_topics.SENSOR_STATE)
        self.assertIn("{command}", mqtt_topics.JMRI_COMMAND)

    def test_format_helpers(self) -> None:
        self.assertEqual(
            mqtt_topics.train_location_topic("train-9"),
            f"{mqtt_topics.BASE}/train/train-9/location",
        )
        self.assertEqual(
            mqtt_topics.order_status_topic("order-5"),
            f"{mqtt_topics.BASE}/order/order-5/status",
        )
        self.assertEqual(
            mqtt_topics.sensor_health_topic("sensor-1"),
            f"{mqtt_topics.BASE}/sensor/sensor-1/health",
        )

    def test_topic_templates(self) -> None:
        templates = mqtt_topics.topic_templates()
        self.assertEqual(templates["ORDER_NEW"], mqtt_topics.ORDER_NEW)
        self.assertIn("JMRI_EVENT", templates)


if __name__ == "__main__":
    unittest.main()
