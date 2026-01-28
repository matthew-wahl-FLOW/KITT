# Provide module-level documentation for MQTT topic helpers.
"""MQTT topic helpers."""
# Summarize what the MQTT topic module provides.
# Overview: Defines MQTT topic constants used across KITT services.
# Explain how the module supports shared routing.
# Details: Provides topic templates and formatter helpers for shared MQTT routing.
# Capture open questions for future development.
# Missing info for further development:
# Identify required broker configuration inputs.
# - Inputs: Broker host/port, retained/QoS rules per topic.
# Identify required payload schema outputs.
# - Outputs: Canonical payload schemas for each topic.
# Identify required topic lifecycle actions.
# - Actions: Topic lifecycle (retained cleanup, replay, backfill).
# Identify required validation methods.
# - Methods: Validation rules for IDs and payload versions.

# Enable postponed evaluation so annotations can use forward references.
from __future__ import annotations

# Import typing support for the topic template mapping.
from typing import Dict

# Define the shared MQTT topic prefix for all KITT messages.
BASE = "kitt"

# Define the topic for new order announcements from the backend.
ORDER_NEW = f"{BASE}/order/new"
# Define the topic template for order status updates.
ORDER_STATUS = f"{BASE}/order/{{order_id}}/status"
# Define the topic template for order event history messages.
ORDER_EVENT = f"{BASE}/order/{{order_id}}/event"

# Define the topic template for train location updates from layout sensors.
TRAIN_LOCATION = f"{BASE}/train/{{train_id}}/location"
# Define the topic template for train status updates such as idle or moving.
TRAIN_STATUS = f"{BASE}/train/{{train_id}}/status"

# Define the topic template for sensor state changes like occupied/free.
SENSOR_STATE = f"{BASE}/sensor/{{sensor_id}}/state"
# Define the topic template for sensor health pings for safety monitoring.
SENSOR_HEALTH = f"{BASE}/sensor/{{sensor_id}}/health"
# Define the topic template for raw sensor reading values.
SENSOR_READING = f"{BASE}/sensor/{{sensor_id}}/reading"

# Define the topic template for commands sent toward JMRI.
JMRI_COMMAND = f"{BASE}/jmri/command/{{command}}"
# Define the topic template for events published from JMRI.
JMRI_EVENT = f"{BASE}/jmri/event/{{event}}"

# Collect all static topic templates for validation and inspection.
ALL_TOPICS = (
    # Include the new order topic in the known list.
    ORDER_NEW,
    # Include the order status template in the known list.
    ORDER_STATUS,
    # Include the order event template in the known list.
    ORDER_EVENT,
    # Include the train location template in the known list.
    TRAIN_LOCATION,
    # Include the train status template in the known list.
    TRAIN_STATUS,
    # Include the sensor state template in the known list.
    SENSOR_STATE,
    # Include the sensor health template in the known list.
    SENSOR_HEALTH,
    # Include the sensor reading template in the known list.
    SENSOR_READING,
    # Include the JMRI command template in the known list.
    JMRI_COMMAND,
    # Include the JMRI event template in the known list.
    JMRI_EVENT,
    # Close the tuple of known topics.
)


# Format a template by injecting identifiers for specific topics.
def format_topic(template: str, **kwargs: str) -> str:
    # Describe the format behavior.
    """Format a topic template with identifiers."""
    # Substitute identifiers into the topic template string.
    return template.format(**kwargs)


# Build the topic for order status updates using a specific order ID.
def order_status_topic(order_id: str) -> str:
    # Describe the order status topic behavior.
    """Return the topic for order status updates."""
    # Fill in the order ID placeholder for the status topic.
    return format_topic(ORDER_STATUS, order_id=order_id)


# Build the topic for order events using a specific order ID.
def order_event_topic(order_id: str) -> str:
    # Describe the order event topic behavior.
    """Return the topic for order events."""
    # Fill in the order ID placeholder for the event topic.
    return format_topic(ORDER_EVENT, order_id=order_id)


# Build the topic for train location updates using a train ID.
def train_location_topic(train_id: str) -> str:
    # Describe the train location topic behavior.
    """Return the topic for train location updates."""
    # Fill in the train ID placeholder for the location topic.
    return format_topic(TRAIN_LOCATION, train_id=train_id)


# Build the topic for train status updates using a train ID.
def train_status_topic(train_id: str) -> str:
    # Describe the train status topic behavior.
    """Return the topic for train status updates."""
    # Fill in the train ID placeholder for the status topic.
    return format_topic(TRAIN_STATUS, train_id=train_id)


# Build the topic for sensor state updates using a sensor ID.
def sensor_state_topic(sensor_id: str) -> str:
    # Describe the sensor state topic behavior.
    """Return the topic for sensor state updates."""
    # Fill in the sensor ID placeholder for the state topic.
    return format_topic(SENSOR_STATE, sensor_id=sensor_id)


# Build the topic for sensor health updates using a sensor ID.
def sensor_health_topic(sensor_id: str) -> str:
    # Describe the sensor health topic behavior.
    """Return the topic for sensor health updates."""
    # Fill in the sensor ID placeholder for the health topic.
    return format_topic(SENSOR_HEALTH, sensor_id=sensor_id)


# Build the topic for sensor reading updates using a sensor ID.
def sensor_reading_topic(sensor_id: str) -> str:
    # Describe the sensor reading topic behavior.
    """Return the topic for sensor reading updates."""
    # Fill in the sensor ID placeholder for the reading topic.
    return format_topic(SENSOR_READING, sensor_id=sensor_id)


# Build the topic for JMRI command requests using a command name.
def jmri_command_topic(command: str) -> str:
    # Describe the JMRI command topic behavior.
    """Return the topic for JMRI commands."""
    # Fill in the command placeholder for the JMRI command topic.
    return format_topic(JMRI_COMMAND, command=command)


# Build the topic for JMRI event updates using an event name.
def jmri_event_topic(event: str) -> str:
    # Describe the JMRI event topic behavior.
    """Return the topic for JMRI event updates."""
    # Fill in the event placeholder for the JMRI event topic.
    return format_topic(JMRI_EVENT, event=event)


# Provide a dictionary of topic templates keyed by logical name.
def topic_templates() -> Dict[str, str]:
    # Describe the topic template mapping behavior.
    """Return a mapping of logical names to topic templates."""
    # Return the mapping so callers can inspect or validate topics.
    return {
        # Expose the new order topic template.
        "ORDER_NEW": ORDER_NEW,
        # Expose the order status template.
        "ORDER_STATUS": ORDER_STATUS,
        # Expose the order event template.
        "ORDER_EVENT": ORDER_EVENT,
        # Expose the train location template.
        "TRAIN_LOCATION": TRAIN_LOCATION,
        # Expose the train status template.
        "TRAIN_STATUS": TRAIN_STATUS,
        # Expose the sensor state template.
        "SENSOR_STATE": SENSOR_STATE,
        # Expose the sensor health template.
        "SENSOR_HEALTH": SENSOR_HEALTH,
        # Expose the sensor reading template.
        "SENSOR_READING": SENSOR_READING,
        # Expose the JMRI command template.
        "JMRI_COMMAND": JMRI_COMMAND,
        # Expose the JMRI event template.
        "JMRI_EVENT": JMRI_EVENT,
        # Close the topic template mapping literal.
    }


# Export the public API for importers in other modules.
__all__ = [
    # Publish the base topic prefix constant.
    "BASE",
    # Publish the new order topic constant.
    "ORDER_NEW",
    # Publish the order status template constant.
    "ORDER_STATUS",
    # Publish the order event template constant.
    "ORDER_EVENT",
    # Publish the train location template constant.
    "TRAIN_LOCATION",
    # Publish the train status template constant.
    "TRAIN_STATUS",
    # Publish the sensor state template constant.
    "SENSOR_STATE",
    # Publish the sensor health template constant.
    "SENSOR_HEALTH",
    # Publish the sensor reading template constant.
    "SENSOR_READING",
    # Publish the JMRI command template constant.
    "JMRI_COMMAND",
    # Publish the JMRI event template constant.
    "JMRI_EVENT",
    # Publish the tuple of all topic templates.
    "ALL_TOPICS",
    # Publish the generic topic formatter helper.
    "format_topic",
    # Publish the helper for order status topics.
    "order_status_topic",
    # Publish the helper for order event topics.
    "order_event_topic",
    # Publish the helper for train location topics.
    "train_location_topic",
    # Publish the helper for train status topics.
    "train_status_topic",
    # Publish the helper for sensor state topics.
    "sensor_state_topic",
    # Publish the helper for sensor health topics.
    "sensor_health_topic",
    # Publish the helper for sensor reading topics.
    "sensor_reading_topic",
    # Publish the helper for JMRI command topics.
    "jmri_command_topic",
    # Publish the helper for JMRI event topics.
    "jmri_event_topic",
    # Publish the helper that returns all templates.
    "topic_templates",
    # Close the __all__ export list.
]
