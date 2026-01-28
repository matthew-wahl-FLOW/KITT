# elevator_controller.ino
# Controls elevator motors and limit switches (MicroPython)
# Ensures safe movement with hardware interlocks
# Publishes position and status via MQTT gateway (via UART placeholder)
# Interfaces: limit switches, motor driver, emergency stop

# Import GPIO and UART helpers from MicroPython.
from machine import Pin, UART
# Import time helpers for delays and tick tracking.
import time

# Define the GPIO pin that enables the elevator motor.
kMotorEnablePin = 25
# Define the GPIO pin that controls motor direction.
kMotorDirectionPin = 26
# Define the GPIO pin connected to the top limit switch.
kLimitTopPin = 33
# Define the GPIO pin connected to the bottom limit switch.
kLimitBottomPin = 32
# Define the GPIO pin connected to the emergency stop input.
kEmergencyStopPin = 27

# Define the number of elevator levels.
kMaxLevels = 3
# Define the travel time between levels.
kLevelTravelMs = 2500
# Define the maximum time to allow a command before faulting.
kCommandTimeoutMs = 15000
# Define the time without progress before faulting.
kMotionStallMs = 5000

# Define the idle state constant.
ELEVATOR_IDLE = 0
# Define the moving up state constant.
ELEVATOR_MOVING_UP = 1
# Define the moving down state constant.
ELEVATOR_MOVING_DOWN = 2
# Define the fault state constant.
ELEVATOR_FAULT = 3

# Track the current elevator state.
elevator_state = ELEVATOR_IDLE
# Track the current level index.
current_level = 0
# Track the requested target level.
target_level = 0
# Track the tick when the last move started.
last_move_ms = 0
# Track the tick when progress was last recorded.
last_progress_ms = 0

# Open a UART channel for MQTT gateway communication.
uart = UART(0, baudrate=115200)

# Configure the motor enable output pin.
motor_enable = Pin(kMotorEnablePin, Pin.OUT)
# Configure the motor direction output pin.
motor_direction = Pin(kMotorDirectionPin, Pin.OUT)
# Configure the top limit switch input pin.
limit_top = Pin(kLimitTopPin, Pin.IN, Pin.PULL_UP)
# Configure the bottom limit switch input pin.
limit_bottom = Pin(kLimitBottomPin, Pin.IN, Pin.PULL_UP)
# Configure the emergency stop input pin.
emergency_stop = Pin(kEmergencyStopPin, Pin.IN, Pin.PULL_UP)


# Publish a status string to the UART MQTT gateway.
def publish_status(status):
    # Write the status message to the serial output.
    uart.write("elevator/status {}\n".format(status))


# Publish the current level to the UART MQTT gateway.
def publish_position():
    # Write the current level message to the serial output.
    uart.write("elevator/position level={}\n".format(current_level))


# Stop the motor output.
def stop_motor():
    # Disable the motor drive output.
    motor_enable.value(0)


# Start the motor moving in a given direction.
def start_motor(new_state):
    # Allow updates to module-level state variables.
    global elevator_state, last_move_ms, last_progress_ms
    # Record the new elevator state.
    elevator_state = new_state
    # Set direction based on requested movement.
    motor_direction.value(1 if new_state == ELEVATOR_MOVING_UP else 0)
    # Enable the motor drive output.
    motor_enable.value(1)
    # Capture the start tick for timeouts.
    last_move_ms = time.ticks_ms()
    # Track progress time for stall detection.
    last_progress_ms = last_move_ms


# Start moving to a requested level.
def start_move(requested_level):
    # Allow updates to the target level variable.
    global target_level
    # Clamp requested levels below zero to the first level.
    if requested_level < 0:
        # Clamp negative requests to the lowest level.
        requested_level = 0
    # Clamp requested levels above max to the top level.
    elif requested_level >= kMaxLevels:
        # Clamp oversized requests to the top level index.
        requested_level = kMaxLevels - 1

    # Store the target level after clamping.
    target_level = requested_level
    # Exit if the elevator is already at the target level.
    if target_level == current_level:
        # Publish a status to indicate no movement is needed.
        publish_status("already_at_level")
        # Exit early because the elevator is already at the target.
        return

    # Start moving upward if the target is higher.
    if target_level > current_level:
        # Start the motor moving up.
        start_motor(ELEVATOR_MOVING_UP)
        # Publish the moving up status.
        publish_status("moving_up")
    # Start moving downward if the target is lower.
    else:
        # Start the motor moving down.
        start_motor(ELEVATOR_MOVING_DOWN)
        # Publish the moving down status.
        publish_status("moving_down")


# Read one command from the UART link.
def read_command():
    # Return early if no serial bytes are waiting.
    if not uart.any():
        # Return None when no bytes are waiting.
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


# Handle any pending elevator command from the UART gateway.
def handle_command():
    # Allow updates to the elevator state variable.
    global elevator_state
    # Read a command from the UART buffer.
    command = read_command()
    # Exit if no command was received.
    if not command:
        # Exit early when no command is available.
        return
    # Handle numeric level commands prefixed with LEVEL.
    if command.startswith("LEVEL"):
        # Extract the level portion of the command.
        level_text = command[5:].strip()
        # Attempt to parse the requested level number.
        try:
            # Convert the level text into an integer.
            level = int(level_text)
        # Default to zero on invalid integer input.
        except ValueError:
            # Default to level zero on parse failure.
            level = 0
        # Begin moving to the requested level.
        start_move(level)
    # Handle single-step up commands.
    elif command == "UP":
        # Start moving to the next higher level.
        start_move(current_level + 1)
    # Handle single-step down commands.
    elif command == "DOWN":
        # Start moving to the next lower level.
        start_move(current_level - 1)
    # Handle stop commands.
    elif command == "STOP":
        # Set the state back to idle.
        elevator_state = ELEVATOR_IDLE
        # Stop the motor output.
        stop_motor()
        # Publish the stopped status.
        publish_status("stopped")


# Check if a duration has elapsed since a start tick.
def has_elapsed(start_ms, duration_ms):
    # Compare the tick delta against the duration.
    return time.ticks_diff(time.ticks_ms(), start_ms) >= duration_ms


# Enforce safety interlocks like emergency stop.
def update_safety():
    # Allow updates to the elevator state variable.
    global elevator_state
    # Trip into fault if emergency stop is active.
    if emergency_stop.value() == 0:
        # Mark the elevator as faulted.
        elevator_state = ELEVATOR_FAULT
        # Stop the motor output.
        stop_motor()
        # Publish the emergency stop status.
        publish_status("emergency_stop")


# Update elevator motion state and stop when needed.
def update_motion():
    # Allow updates to module-level state variables.
    global current_level, elevator_state, last_move_ms, last_progress_ms
    # Exit early if the elevator is not moving.
    if elevator_state not in (ELEVATOR_MOVING_UP, ELEVATOR_MOVING_DOWN):
        # Exit early when the elevator is not moving.
        return

    # Read the top limit switch state.
    hit_top = limit_top.value() == 0
    # Read the bottom limit switch state.
    hit_bottom = limit_bottom.value() == 0

    # Handle hitting the top limit while moving up.
    if elevator_state == ELEVATOR_MOVING_UP and hit_top:
        # Set the current level to the top floor.
        current_level = kMaxLevels - 1
        # Update the progress timer.
        last_progress_ms = time.ticks_ms()
    # Handle hitting the bottom limit while moving down.
    elif elevator_state == ELEVATOR_MOVING_DOWN and hit_bottom:
        # Set the current level to the ground floor.
        current_level = 0
        # Update the progress timer.
        last_progress_ms = time.ticks_ms()
    # Handle elapsed travel time between levels.
    elif has_elapsed(last_move_ms, kLevelTravelMs):
        # Increment or decrement the level based on direction.
        if elevator_state == ELEVATOR_MOVING_UP:
            # Increment the level while clamping to the top.
            current_level = min(current_level + 1, kMaxLevels - 1)
        # Handle downward motion between levels.
        else:
            # Decrement the level while clamping to the bottom.
            current_level = max(current_level - 1, 0)
        # Reset the move timer for the next level.
        last_move_ms = time.ticks_ms()
        # Update the progress timer after movement.
        last_progress_ms = last_move_ms

    # Fault if there has been no progress for too long.
    if has_elapsed(last_progress_ms, kMotionStallMs):
        # Stop the motor output.
        stop_motor()
        # Move to the fault state.
        elevator_state = ELEVATOR_FAULT
        # Publish the stall fault status.
        publish_status("fault_stall")
        # Exit early after handling the stall fault.
        return

    # Stop motion if the target is reached or a limit/timeout triggers.
    if (
        # Check if the elevator reached the target level.
        current_level == target_level
        # Check if the top limit switch was hit.
        or hit_top
        # Check if the bottom limit switch was hit.
        or hit_bottom
        # Check if the command timed out.
        or has_elapsed(last_move_ms, kCommandTimeoutMs)
        # Close the stop condition tuple.
    ):
        # Stop the motor output.
        stop_motor()
        # Return to the idle state.
        elevator_state = ELEVATOR_IDLE
        # Publish the final position.
        publish_position()
        # Publish the idle status.
        publish_status("idle")


# Initialize the elevator hardware into a safe state.
def setup():
    # Stop the motor at startup.
    stop_motor()
    # Publish the ready status for telemetry.
    publish_status("ready")
    # Publish the initial position for telemetry.
    publish_position()


# Run setup once at boot.
setup()
# Enter the main control loop.
while True:
    # Process incoming commands from the UART gateway.
    handle_command()
    # Enforce emergency stop interlocks.
    update_safety()
    # Update motion state and stop when needed.
    update_motion()
    # Sleep briefly to limit CPU usage.
    time.sleep_ms(50)
