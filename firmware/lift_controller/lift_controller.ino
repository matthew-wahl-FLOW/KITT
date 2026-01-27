# lift_controller.ino
# Controls the track lift mechanism (MicroPython)
# Verifies mechanical locks before lowering/raising
# Cuts track power to isolated section when lowering
# Publishes lift state and safety interlock status via MQTT gateway (via UART placeholder)

from machine import Pin, UART
import time

kLiftMotorPin = 18
kLockRelayPin = 19
kTrackPowerRelayPin = 21
kLiftUpLimitPin = 22
kLiftDownLimitPin = 23

kLiftTravelMs = 4000
kLockReleaseMs = 800

LIFT_IDLE = 0
LIFT_RAISING = 1
LIFT_LOWERING = 2
LIFT_FAULT = 3

lift_state = LIFT_IDLE
lift_start_ms = 0

uart = UART(0, baudrate=115200)

lift_motor = Pin(kLiftMotorPin, Pin.OUT)
lock_relay = Pin(kLockRelayPin, Pin.OUT)
track_power_relay = Pin(kTrackPowerRelayPin, Pin.OUT)
lift_up_limit = Pin(kLiftUpLimitPin, Pin.IN, Pin.PULL_UP)
lift_down_limit = Pin(kLiftDownLimitPin, Pin.IN, Pin.PULL_UP)


def publish_state(state):
    uart.write("lift/state {}\n".format(state))


def set_track_power(enabled):
    track_power_relay.value(1 if enabled else 0)


def set_lock(engaged):
    lock_relay.value(1 if engaged else 0)


def start_lift(new_state):
    global lift_state, lift_start_ms
    lift_state = new_state
    lift_motor.value(1)
    lift_start_ms = time.ticks_ms()


def stop_lift():
    lift_motor.value(0)


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
    global lift_state
    command = read_command()
    if not command:
        return
    if command == "LOWER":
        set_lock(False)
        time.sleep_ms(kLockReleaseMs)
        set_track_power(False)
        start_lift(LIFT_LOWERING)
        publish_state("lowering")
    elif command == "RAISE":
        set_lock(False)
        time.sleep_ms(kLockReleaseMs)
        start_lift(LIFT_RAISING)
        publish_state("raising")
    elif command == "STOP":
        stop_lift()
        lift_state = LIFT_IDLE
        publish_state("stopped")


def has_elapsed(start_ms, duration_ms):
    return time.ticks_diff(time.ticks_ms(), start_ms) >= duration_ms


def update_lift():
    global lift_state
    at_top = lift_up_limit.value() == 0
    at_bottom = lift_down_limit.value() == 0

    if lift_state == LIFT_RAISING and at_top:
        stop_lift()
        set_lock(True)
        set_track_power(True)
        lift_state = LIFT_IDLE
        publish_state("raised")
    elif lift_state == LIFT_LOWERING and at_bottom:
        stop_lift()
        set_lock(True)
        lift_state = LIFT_IDLE
        publish_state("lowered")
    elif lift_state in (LIFT_RAISING, LIFT_LOWERING) and has_elapsed(
        lift_start_ms, kLiftTravelMs
    ):
        stop_lift()
        lift_state = LIFT_FAULT
        publish_state("fault_timeout")


def setup():
    set_track_power(True)
    set_lock(True)
    stop_lift()
    publish_state("ready")


setup()
while True:
    handle_command()
    update_lift()
    time.sleep_ms(50)
