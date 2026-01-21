# // Centralized MQTT topic definitions and conventions
# // Example topic hierarchy: kitt/{subsystem}/{component}/{event}
# // Export constants for use by services and firmware documentation
#
# # PSEUDOCODE (Python constants):
# BASE = "kitt"
# ORDER_NEW = f"{BASE}/order/new"
# TRAIN_LOCATION = f"{BASE}/train/{{train_id}}/location"
# SENSOR_STATE = f"{BASE}/sensor/{{sensor_id}}/state"
# JMRI_COMMAND = f"{BASE}/jmri/command/{{command}}"
