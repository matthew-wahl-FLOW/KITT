"""MQTT topic helpers.

Simple: Defines MQTT topic constants used across KITT services.
Technical: Provides topic templates and formatter helpers for shared MQTT routing.

Missing info for further development:
- Inputs: Broker host/port, retained/QoS rules per topic.
- Outputs: Canonical payload schemas for each topic.
- Actions: Topic lifecycle (retained cleanup, replay, backfill).
- Methods: Validation rules for IDs and payload versions.
"""

from __future__ import annotations

from typing import Dict

BASE = "kitt"

ORDER_NEW = f"{BASE}/order/new"
ORDER_STATUS = f"{BASE}/order/{{order_id}}/status"
ORDER_EVENT = f"{BASE}/order/{{order_id}}/event"

TRAIN_LOCATION = f"{BASE}/train/{{train_id}}/location"
TRAIN_STATUS = f"{BASE}/train/{{train_id}}/status"

SENSOR_STATE = f"{BASE}/sensor/{{sensor_id}}/state"
SENSOR_HEALTH = f"{BASE}/sensor/{{sensor_id}}/health"

JMRI_COMMAND = f"{BASE}/jmri/command/{{command}}"
JMRI_EVENT = f"{BASE}/jmri/event/{{event}}"

ALL_TOPICS = (
    ORDER_NEW,
    ORDER_STATUS,
    ORDER_EVENT,
    TRAIN_LOCATION,
    TRAIN_STATUS,
    SENSOR_STATE,
    SENSOR_HEALTH,
    JMRI_COMMAND,
    JMRI_EVENT,
)


def format_topic(template: str, **kwargs: str) -> str:
    """Format a topic template with identifiers."""
    return template.format(**kwargs)


def order_status_topic(order_id: str) -> str:
    """Return the topic for order status updates."""
    return format_topic(ORDER_STATUS, order_id=order_id)


def order_event_topic(order_id: str) -> str:
    """Return the topic for order events."""
    return format_topic(ORDER_EVENT, order_id=order_id)


def train_location_topic(train_id: str) -> str:
    """Return the topic for train location updates."""
    return format_topic(TRAIN_LOCATION, train_id=train_id)


def train_status_topic(train_id: str) -> str:
    """Return the topic for train status updates."""
    return format_topic(TRAIN_STATUS, train_id=train_id)


def sensor_state_topic(sensor_id: str) -> str:
    """Return the topic for sensor state updates."""
    return format_topic(SENSOR_STATE, sensor_id=sensor_id)


def sensor_health_topic(sensor_id: str) -> str:
    """Return the topic for sensor health updates."""
    return format_topic(SENSOR_HEALTH, sensor_id=sensor_id)


def jmri_command_topic(command: str) -> str:
    """Return the topic for JMRI commands."""
    return format_topic(JMRI_COMMAND, command=command)


def jmri_event_topic(event: str) -> str:
    """Return the topic for JMRI event updates."""
    return format_topic(JMRI_EVENT, event=event)


def topic_templates() -> Dict[str, str]:
    """Return a mapping of logical names to topic templates."""
    return {
        "ORDER_NEW": ORDER_NEW,
        "ORDER_STATUS": ORDER_STATUS,
        "ORDER_EVENT": ORDER_EVENT,
        "TRAIN_LOCATION": TRAIN_LOCATION,
        "TRAIN_STATUS": TRAIN_STATUS,
        "SENSOR_STATE": SENSOR_STATE,
        "SENSOR_HEALTH": SENSOR_HEALTH,
        "JMRI_COMMAND": JMRI_COMMAND,
        "JMRI_EVENT": JMRI_EVENT,
    }


__all__ = [
    "BASE",
    "ORDER_NEW",
    "ORDER_STATUS",
    "ORDER_EVENT",
    "TRAIN_LOCATION",
    "TRAIN_STATUS",
    "SENSOR_STATE",
    "SENSOR_HEALTH",
    "JMRI_COMMAND",
    "JMRI_EVENT",
    "ALL_TOPICS",
    "format_topic",
    "order_status_topic",
    "order_event_topic",
    "train_location_topic",
    "train_status_topic",
    "sensor_state_topic",
    "sensor_health_topic",
    "jmri_command_topic",
    "jmri_event_topic",
    "topic_templates",
]
