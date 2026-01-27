# elevator_controller.ino
# Controls elevator motors and limit switches (MicroPython)
# Ensures safe movement with hardware interlocks
# Publishes position and status via MQTT gateway (via UART placeholder)
# Interfaces: limit switches, motor driver, emergency stop

from machine import Pin, UART
import time

kMotorEnablePin = 25
kMotorDirectionPin = 26
kLimitTopPin = 33
kLimitBottomPin = 32
kEmergencyStopPin = 27

kMaxLevels = 3
kLevelTravelMs = 2500
kCommandTimeoutMs = 15000
kMotionStallMs = 5000

ELEVATOR_IDLE = 0
ELEVATOR_MOVING_UP = 1
ELEVATOR_MOVING_DOWN = 2
ELEVATOR_FAULT = 3

elevator_state = ELEVATOR_IDLE
current_level = 0
target_level = 0
last_move_ms = 0
last_progress_ms = 0

uart = UART(0, baudrate=115200)

motor_enable = Pin(kMotorEnablePin, Pin.OUT)
motor_direction = Pin(kMotorDirectionPin, Pin.OUT)
limit_top = Pin(kLimitTopPin, Pin.IN, Pin.PULL_UP)
limit_bottom = Pin(kLimitBottomPin, Pin.IN, Pin.PULL_UP)
emergency_stop = Pin(kEmergencyStopPin, Pin.IN, Pin.PULL_UP)


def publish_status(status):
    uart.write("elevator/status {}\n".format(status))


def publish_position():
    uart.write("elevator/position level={}\n".format(current_level))


def stop_motor():
    motor_enable.value(0)


def start_motor(new_state):
    global elevator_state, last_move_ms, last_progress_ms
    elevator_state = new_state
    motor_direction.value(1 if new_state == ELEVATOR_MOVING_UP else 0)
    motor_enable.value(1)
    last_move_ms = time.ticks_ms()
    last_progress_ms = last_move_ms


def start_move(requested_level):
    global target_level
    if requested_level < 0:
        requested_level = 0
    elif requested_level >= kMaxLevels:
        requested_level = kMaxLevels - 1

    target_level = requested_level
    if target_level == current_level:
        publish_status("already_at_level")
        return

    if target_level > current_level:
        start_motor(ELEVATOR_MOVING_UP)
        publish_status("moving_up")
    else:
        start_motor(ELEVATOR_MOVING_DOWN)
        publish_status("moving_down")


def read_command():
    if not uart.any():
        return None
    line = uart.readline()
    if not line:
        return None
    try:
        return line.decode().strip()
    except Exception:
        return None


def handle_command():
    global elevator_state
    command = read_command()
    if not command:
        return
    if command.startswith("LEVEL"):
        level_text = command[5:].strip()
        try:
            level = int(level_text)
        except ValueError:
            level = 0
        start_move(level)
    elif command == "UP":
        start_move(current_level + 1)
    elif command == "DOWN":
        start_move(current_level - 1)
    elif command == "STOP":
        elevator_state = ELEVATOR_IDLE
        stop_motor()
        publish_status("stopped")


def has_elapsed(start_ms, duration_ms):
    return time.ticks_diff(time.ticks_ms(), start_ms) >= duration_ms


def update_safety():
    global elevator_state
    if emergency_stop.value() == 0:
        elevator_state = ELEVATOR_FAULT
        stop_motor()
        publish_status("emergency_stop")


def update_motion():
    global current_level, elevator_state, last_move_ms, last_progress_ms
    if elevator_state not in (ELEVATOR_MOVING_UP, ELEVATOR_MOVING_DOWN):
        return

    hit_top = limit_top.value() == 0
    hit_bottom = limit_bottom.value() == 0

    if elevator_state == ELEVATOR_MOVING_UP and hit_top:
        current_level = kMaxLevels - 1
        last_progress_ms = time.ticks_ms()
    elif elevator_state == ELEVATOR_MOVING_DOWN and hit_bottom:
        current_level = 0
        last_progress_ms = time.ticks_ms()
    elif has_elapsed(last_move_ms, kLevelTravelMs):
        if elevator_state == ELEVATOR_MOVING_UP:
            current_level = min(current_level + 1, kMaxLevels - 1)
        else:
            current_level = max(current_level - 1, 0)
        last_move_ms = time.ticks_ms()
        last_progress_ms = last_move_ms

    if has_elapsed(last_progress_ms, kMotionStallMs):
        stop_motor()
        elevator_state = ELEVATOR_FAULT
        publish_status("fault_stall")
        return

    if (
        current_level == target_level
        or hit_top
        or hit_bottom
        or has_elapsed(last_move_ms, kCommandTimeoutMs)
    ):
        stop_motor()
        elevator_state = ELEVATOR_IDLE
        publish_position()
        publish_status("idle")


def setup():
    stop_motor()
    publish_status("ready")
    publish_position()


setup()
while True:
    handle_command()
    update_safety()
    update_motion()
    time.sleep_ms(50)
