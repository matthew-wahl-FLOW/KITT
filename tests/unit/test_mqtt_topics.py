# Document the purpose of this unit test module.
"""Unit tests for MQTT topic helpers."""
# Summarize what the tests cover.
# Overview: Validates MQTT topic constants and formatting helpers.
# Explain how the tests are run.
# Details: Uses unittest to verify template contents and helper formatting.

# Import unittest for the test framework.
import unittest

# Import MQTT topic helpers from the services utilities package.
from services.utils import mqtt_topics


# Validate topic constants and formatting helpers.
class TestMqttTopics(unittest.TestCase):
    # Confirm static topic constants match expected patterns.
    def test_constants(self) -> None:
        # Confirm the new order topic ends with the expected suffix.
        self.assertTrue(mqtt_topics.ORDER_NEW.endswith("order/new"))
        # Confirm the train location template has a train placeholder.
        self.assertIn("{train_id}", mqtt_topics.TRAIN_LOCATION)
        # Confirm the sensor state template has a sensor placeholder.
        self.assertIn("{sensor_id}", mqtt_topics.SENSOR_STATE)
        # Confirm the sensor reading template has a sensor placeholder.
        self.assertIn("{sensor_id}", mqtt_topics.SENSOR_READING)
        # Confirm the JMRI command template has a command placeholder.
        self.assertIn("{command}", mqtt_topics.JMRI_COMMAND)

    # Confirm helper functions format topics correctly.
    def test_format_helpers(self) -> None:
        # Verify train location topics format with a train ID.
        self.assertEqual(
            # Provide the formatted train location topic under test.
            mqtt_topics.train_location_topic("train-9"),
            # Provide the expected formatted topic value.
            f"{mqtt_topics.BASE}/train/train-9/location",
            # Close the assertion call.
        )
        # Verify order status topics format with an order ID.
        self.assertEqual(
            # Provide the formatted order status topic under test.
            mqtt_topics.order_status_topic("order-5"),
            # Provide the expected formatted topic value.
            f"{mqtt_topics.BASE}/order/order-5/status",
            # Close the assertion call.
        )
        # Verify sensor health topics format with a sensor ID.
        self.assertEqual(
            # Provide the formatted sensor health topic under test.
            mqtt_topics.sensor_health_topic("sensor-1"),
            # Provide the expected formatted topic value.
            f"{mqtt_topics.BASE}/sensor/sensor-1/health",
            # Close the assertion call.
        )
        # Verify sensor reading topics format with a sensor ID.
        self.assertEqual(
            # Provide the formatted sensor reading topic under test.
            mqtt_topics.sensor_reading_topic("sensor-1"),
            # Provide the expected formatted topic value.
            f"{mqtt_topics.BASE}/sensor/sensor-1/reading",
            # Close the assertion call.
        )

    # Confirm the topic template mapping includes expected keys.
    def test_topic_templates(self) -> None:
        # Fetch the template mapping for validation.
        templates = mqtt_topics.topic_templates()
        # Confirm the new order topic template is present.
        self.assertEqual(templates["ORDER_NEW"], mqtt_topics.ORDER_NEW)
        # Confirm the JMRI event template is included.
        self.assertIn("JMRI_EVENT", templates)
        # Confirm the sensor reading template is included.
        self.assertIn("SENSOR_READING", templates)


# Run the tests when executing this module directly.
if __name__ == "__main__":
    # Invoke unittest to run the test module.
    unittest.main()
