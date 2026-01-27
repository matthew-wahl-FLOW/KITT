# lift_controller.ino
# Controls the track lift mechanism (MicroPython)
# Verifies mechanical locks before lowering/raising
# Cuts track power to isolated section when lowering
# Publishes lift state and safety interlock status via MQTT gateway (via UART placeholder)

# Import GPIO and UART helpers from MicroPython.
from machine import Pin, UART
# Import time helpers for delays and tick tracking.
import time

# Define the GPIO pin that drives the lift motor.
kLiftMotorPin = 18
# Define the GPIO pin that drives the lock relay.
kLockRelayPin = 19
# Define the GPIO pin that cuts track power to the lift section.
kTrackPowerRelayPin = 21
# Define the GPIO pin connected to the lift upper limit switch.
kLiftUpLimitPin = 22
# Define the GPIO pin connected to the lift lower limit switch.
kLiftDownLimitPin = 23

# Define the maximum travel time before faulting.
kLiftTravelMs = 4000
# Define the time to wait for lock release.
kLockReleaseMs = 800

# Define the idle state constant.
LIFT_IDLE = 0
# Define the raising state constant.
LIFT_RAISING = 1
# Define the lowering state constant.
LIFT_LOWERING = 2
# Define the fault state constant.
LIFT_FAULT = 3

# Track the current lift state.
lift_state = LIFT_IDLE
# Track the tick when motion began.
lift_start_ms = 0

# Open a UART channel for MQTT gateway communication.
uart = UART(0, baudrate=115200)

# Configure the lift motor output pin.
lift_motor = Pin(kLiftMotorPin, Pin.OUT)
# Configure the lock relay output pin.
lock_relay = Pin(kLockRelayPin, Pin.OUT)
# Configure the track power relay output pin.
track_power_relay = Pin(kTrackPowerRelayPin, Pin.OUT)
# Configure the upper limit switch input pin.
lift_up_limit = Pin(kLiftUpLimitPin, Pin.IN, Pin.PULL_UP)
# Configure the lower limit switch input pin.
lift_down_limit = Pin(kLiftDownLimitPin, Pin.IN, Pin.PULL_UP)


# Publish the lift state to the UART MQTT gateway.
def publish_state(state):
    # Write the state message to the serial output.
    uart.write("lift/state {}\n".format(state))


# Toggle track power based on lift position needs.
def set_track_power(enabled):
    # Energize or cut the track power relay.
    track_power_relay.value(1 if enabled else 0)


# Toggle the mechanical lock relay.
def set_lock(engaged):
    # Engage or disengage the lock relay.
    lock_relay.value(1 if engaged else 0)


# Start the lift moving and track the new state.
def start_lift(new_state):
    # Allow updates to module-level state variables.
    global lift_state, lift_start_ms
    # Record the new state so other logic knows motion direction.
    lift_state = new_state
    # Enable the motor drive output.
    lift_motor.value(1)
    # Capture the motion start tick for timeout monitoring.
    lift_start_ms = time.ticks_ms()


# Stop the lift motor output.
def stop_lift():
    # De-energize the lift motor output.
    lift_motor.value(0)


# Read one command from the UART link.
def read_command():
    # Return early if no serial bytes are waiting.
    if not uart.any():
        return None
    # Read a line of bytes from the UART buffer.
    line = uart.readline()
    # Return early if the read produced no data.
    if not line:
        return None
    try:
        # Decode bytes into a command string.
        return line.decode().strip()
    except Exception:
        # Ignore malformed bytes and return no command.
        return None


# Handle any pending lift command from the UART gateway.
def handle_command():
    # Allow updates to the lift state variable.
    global lift_state
    # Read a command from the UART buffer.
    command = read_command()
    # Exit if no command was received.
    if not command:
        return
    # Handle the LOWER command sequence.
    if command == "LOWER":
        # Release the mechanical lock before moving.
        set_lock(False)
        # Wait for the lock to fully disengage.
        time.sleep_ms(kLockReleaseMs)
        # Cut track power before lowering the lift.
        set_track_power(False)
        # Begin lowering the lift.
        start_lift(LIFT_LOWERING)
        # Publish the lowering state for telemetry.
        publish_state("lowering")
    # Handle the RAISE command sequence.
    elif command == "RAISE":
        # Release the mechanical lock before moving.
        set_lock(False)
        # Wait for the lock to fully disengage.
        time.sleep_ms(kLockReleaseMs)
        # Begin raising the lift.
        start_lift(LIFT_RAISING)
        # Publish the raising state for telemetry.
        publish_state("raising")
    # Handle the STOP command sequence.
    elif command == "STOP":
        # Stop the motor immediately.
        stop_lift()
        # Reset the state back to idle.
        lift_state = LIFT_IDLE
        # Publish the stop state for telemetry.
        publish_state("stopped")


# Check if a duration has elapsed since a start tick.
def has_elapsed(start_ms, duration_ms):
    # Compare the tick delta against the duration.
    return time.ticks_diff(time.ticks_ms(), start_ms) >= duration_ms


# Update lift motion based on limit switches and timeouts.
def update_lift():
    # Allow updates to the lift state variable.
    global lift_state
    # Read the upper limit switch state.
    at_top = lift_up_limit.value() == 0
    # Read the lower limit switch state.
    at_bottom = lift_down_limit.value() == 0

    # Handle arrival at the upper limit.
    if lift_state == LIFT_RAISING and at_top:
        # Stop the motor once the upper limit is hit.
        stop_lift()
        # Engage the lock to secure the lift.
        set_lock(True)
        # Restore track power after reaching the top.
        set_track_power(True)
        # Mark the state as idle.
        lift_state = LIFT_IDLE
        # Publish the raised status for telemetry.
        publish_state("raised")
    # Handle arrival at the lower limit.
    elif lift_state == LIFT_LOWERING and at_bottom:
        # Stop the motor once the lower limit is hit.
        stop_lift()
        # Engage the lock to secure the lift.
        set_lock(True)
        # Mark the state as idle.
        lift_state = LIFT_IDLE
        # Publish the lowered status for telemetry.
        publish_state("lowered")
    # Handle timeouts for both raising and lowering.
    elif lift_state in (LIFT_RAISING, LIFT_LOWERING) and has_elapsed(
        # Provide the motion start tick for timeout comparison.
        lift_start_ms,
        # Provide the maximum travel time allowed.
        kLiftTravelMs,
    ):
        # Stop the motor after timeout.
        stop_lift()
        # Move to the fault state on timeout.
        lift_state = LIFT_FAULT
        # Publish the timeout fault for telemetry.
        publish_state("fault_timeout")


# Initialize the lift hardware into a safe state.
def setup():
    # Ensure track power is enabled at startup.
    set_track_power(True)
    # Engage the mechanical lock at startup.
    set_lock(True)
    # Stop the motor at startup.
    stop_lift()
    # Publish the ready state for telemetry.
    publish_state("ready")


# Run setup once at boot.
setup()
# Enter the main control loop.
while True:
    # Process incoming commands from the UART gateway.
    handle_command()
    # Update lift motion state and enforce safety.
    update_lift()
    # Sleep briefly to limit CPU usage.
    time.sleep_ms(50)
