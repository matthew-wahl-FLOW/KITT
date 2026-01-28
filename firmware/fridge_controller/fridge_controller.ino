# fridge_controller.ino
# Controls fridge dispenser servo, peltier cooler, and fan logic (MicroPython)
# Subscribes to MQTT via serial gateway or onboard WiFi (placeholder)
# Publishes status: ready, dispensing, cooling, error
# Interfaces: servo, door sensor, dispense sensor, temp/humidity sensor, peltier relay, fan relay

# Import GPIO and UART helpers from MicroPython.
from machine import Pin, UART
# Import math helpers for temperature/humidity simulation.
import math
# Import time helpers for delays and tick tracking.
import time

# Define the GPIO pin that controls the dispenser servo.
kServoPin = 14
# Define the GPIO pin connected to the door sensor.
kDoorSensorPin = 27
# Define the GPIO pin connected to the dispense sensor.
kDispenseSensorPin = 26
# Define the GPIO pin that controls the peltier relay.
kPeltierRelayPin = 25
# Define the GPIO pin that controls the fan relay.
kFanRelayPin = 33

# Define the target temperature in Celsius.
kTargetTempC = 3.0
# Define the temperature deadband in Celsius.
kTempDeadbandC = 1.0
# Define the dew point margin in Celsius.
kDewpointMarginC = 1.0
# Define the simulated humidity percentage.
kHumidityPercent = 55.0
# Define the dispense duration in milliseconds.
kDispenseDurationMs = 1500

# Track whether the peltier relay is energized.
peltier_on = False
# Track whether the fan relay is energized.
fan_on = False

# Open a UART channel for MQTT gateway communication.
uart = UART(0, baudrate=115200)

# Configure the servo output pin.
servo = Pin(kServoPin, Pin.OUT)
# Configure the door sensor input pin.
door_sensor = Pin(kDoorSensorPin, Pin.IN, Pin.PULL_UP)
# Configure the dispense sensor input pin.
dispense_sensor = Pin(kDispenseSensorPin, Pin.IN, Pin.PULL_UP)
# Configure the peltier relay output pin.
peltier_relay = Pin(kPeltierRelayPin, Pin.OUT)
# Configure the fan relay output pin.
fan_relay = Pin(kFanRelayPin, Pin.OUT)


# Generate a simulated temperature value in Celsius.
def fake_temperature_c():
    # Compute a phase angle for the simulated temperature.
    phase = (time.ticks_ms() % 20000) / 20000.0
    # Return the simulated temperature value.
    return kTargetTempC + 2.0 * math.sin(phase * 2.0 * math.pi)


# Generate a simulated humidity value.
def fake_humidity():
    # Compute a phase angle for the simulated humidity.
    phase = (time.ticks_ms() % 15000) / 15000.0
    # Return the simulated humidity percentage.
    return kHumidityPercent + 5.0 * math.cos(phase * 2.0 * math.pi)


# Compute dew point in Celsius using temperature and humidity.
def compute_dew_point(temp_c, humidity_percent):
    # Calculate the dew point alpha term.
    alpha = ((17.27 * temp_c) / (237.7 + temp_c)) + math.log(humidity_percent / 100.0)
    # Return the dew point derived from the alpha term.
    return (237.7 * alpha) / (17.27 - alpha)


# Publish telemetry values via the UART MQTT gateway.
def publish_telemetry(temp_c, humidity_percent, dew_point_c):
    # Write the telemetry line with formatted values.
    uart.write(
        # Provide the formatted telemetry string for the UART gateway.
        "fridge/telemetry temp_c={:.2f} humidity={:.1f} dewpoint_c={:.2f}\n".format(
            # Provide the temperature argument for formatting.
            temp_c,
            # Provide the humidity argument for formatting.
            humidity_percent,
            # Provide the dew point argument for formatting.
            dew_point_c,
            # Close the format call arguments.
        )
        # Close the UART write call.
    )


# Publish a status string via the UART MQTT gateway.
def publish_status(status):
    # Write the status message to the serial output.
    uart.write("fridge/status {}\n".format(status))


# Toggle a relay output pin based on an enable value.
def set_relay(relay, enabled):
    # Energize or de-energize the relay.
    relay.value(1 if enabled else 0)


# Update cooling outputs based on temperature and dew point.
def update_cooling(temp_c, dew_point_c):
    # Allow updates to module-level relay state.
    global peltier_on, fan_on
    # Enable the peltier when above the target range.
    if temp_c > kTargetTempC + kTempDeadbandC:
        # Enable the peltier when temperature is above the deadband.
        peltier_on = True
    # Disable the peltier when below the target range.
    elif temp_c < kTargetTempC - kTempDeadbandC:
        # Disable the peltier when temperature is below the deadband.
        peltier_on = False

    # Disable the fan when near dew point to avoid condensation.
    if temp_c - dew_point_c <= kDewpointMarginC:
        # Disable the fan when too close to the dew point.
        fan_on = False
    # Enable the fan when safely above dew point.
    else:
        # Enable the fan when safely above the dew point.
        fan_on = True

    # Apply the peltier relay output.
    set_relay(peltier_relay, peltier_on)
    # Apply the fan relay output.
    set_relay(fan_relay, fan_on)


# Read one command from the UART link.
def read_command():
    # Return early if no serial bytes are waiting.
    if not uart.any():
        # Return None when no serial bytes are waiting.
        return None
    # Read a line of bytes from the UART buffer.
    line = uart.readline()
    # Return early if the read produced no data.
    if not line:
        # Return None when the UART read returns empty data.
        return None
    # Attempt to decode the UART line.
    try:
        # Decode bytes into a command string.
        return line.decode().strip()
    # Handle decode errors from malformed bytes.
    except Exception:
        # Ignore malformed bytes and return no command.
        return None


# Handle dispense commands and safety checks.
def handle_dispense():
    # Read the next command from the UART link.
    command = read_command()
    # Exit if no command was received.
    if not command:
        # Exit early when no command is available.
        return
    # Exit if the command is not a dispense request.
    if command != "DISPENSE":
        # Exit early when the command is not a dispense request.
        return

    # Check whether the door is closed before dispensing.
    door_closed = door_sensor.value() == 0
    # Reject the dispense if the door is open.
    if not door_closed:
        # Publish an error if the door is open.
        publish_status("error_door_open")
        # Exit early after reporting the error.
        return

    # Publish the dispensing status.
    publish_status("dispensing")
    # Wait for the dispense mechanism to complete.
    time.sleep_ms(kDispenseDurationMs)
    # Check the dispense sensor for completion.
    dispensed = dispense_sensor.value() == 0
    # Publish completion status if the dispense succeeded.
    if dispensed:
        # Publish the successful dispense status.
        publish_status("done")
    # Publish an error if dispense completion timed out.
    else:
        # Publish the timeout error status.
        publish_status("error_dispense_timeout")


# Initialize the fridge controller into a safe state.
def setup():
    # Disable the peltier relay at startup.
    set_relay(peltier_relay, False)
    # Disable the fan relay at startup.
    set_relay(fan_relay, False)
    # Publish the ready status for telemetry.
    publish_status("ready")


# Run setup once at boot.
setup()
# Enter the main control loop.
while True:
    # Generate a simulated temperature value.
    temp_c = fake_temperature_c()
    # Generate a simulated humidity value.
    humidity = fake_humidity()
    # Compute the dew point for cooling logic.
    dew_point_c = compute_dew_point(temp_c, humidity)
    # Update cooling outputs based on the telemetry.
    update_cooling(temp_c, dew_point_c)
    # Publish telemetry values for monitoring.
    publish_telemetry(temp_c, humidity, dew_point_c)
    # Handle dispense commands if received.
    handle_dispense()
    # Sleep between telemetry updates.
    time.sleep_ms(1000)
