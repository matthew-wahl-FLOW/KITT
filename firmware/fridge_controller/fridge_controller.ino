# fridge_controller.ino
# Controls fridge dispenser servo, peltier cooler, and fan logic (MicroPython)
# Subscribes to MQTT via serial gateway or onboard WiFi (placeholder)
# Publishes status: ready, dispensing, cooling, error
# Interfaces: servo, door sensor, dispense sensor, temp/humidity sensor, peltier relay, fan relay

from machine import Pin, UART
import math
import time

kServoPin = 14
kDoorSensorPin = 27
kDispenseSensorPin = 26
kPeltierRelayPin = 25
kFanRelayPin = 33

kTargetTempC = 3.0
kTempDeadbandC = 1.0
kDewpointMarginC = 1.0
kHumidityPercent = 55.0
kDispenseDurationMs = 1500

peltier_on = False
fan_on = False

uart = UART(0, baudrate=115200)

servo = Pin(kServoPin, Pin.OUT)
door_sensor = Pin(kDoorSensorPin, Pin.IN, Pin.PULL_UP)
dispense_sensor = Pin(kDispenseSensorPin, Pin.IN, Pin.PULL_UP)
peltier_relay = Pin(kPeltierRelayPin, Pin.OUT)
fan_relay = Pin(kFanRelayPin, Pin.OUT)


def fake_temperature_c():
    phase = (time.ticks_ms() % 20000) / 20000.0
    return kTargetTempC + 2.0 * math.sin(phase * 2.0 * math.pi)


def fake_humidity():
    phase = (time.ticks_ms() % 15000) / 15000.0
    return kHumidityPercent + 5.0 * math.cos(phase * 2.0 * math.pi)


def compute_dew_point(temp_c, humidity_percent):
    alpha = ((17.27 * temp_c) / (237.7 + temp_c)) + math.log(humidity_percent / 100.0)
    return (237.7 * alpha) / (17.27 - alpha)


def publish_telemetry(temp_c, humidity_percent, dew_point_c):
    uart.write(
        "fridge/telemetry temp_c={:.2f} humidity={:.1f} dewpoint_c={:.2f}\n".format(
            temp_c, humidity_percent, dew_point_c
        )
    )


def publish_status(status):
    uart.write("fridge/status {}\n".format(status))


def set_relay(relay, enabled):
    relay.value(1 if enabled else 0)


def update_cooling(temp_c, dew_point_c):
    global peltier_on, fan_on
    if temp_c > kTargetTempC + kTempDeadbandC:
        peltier_on = True
    elif temp_c < kTargetTempC - kTempDeadbandC:
        peltier_on = False

    if temp_c - dew_point_c <= kDewpointMarginC:
        fan_on = False
    else:
        fan_on = True

    set_relay(peltier_relay, peltier_on)
    set_relay(fan_relay, fan_on)


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


def handle_dispense():
    command = read_command()
    if not command:
        return
    if command != "DISPENSE":
        return

    door_closed = door_sensor.value() == 0
    if not door_closed:
        publish_status("error_door_open")
        return

    publish_status("dispensing")
    time.sleep_ms(kDispenseDurationMs)
    dispensed = dispense_sensor.value() == 0
    if dispensed:
        publish_status("done")
    else:
        publish_status("error_dispense_timeout")


def setup():
    set_relay(peltier_relay, False)
    set_relay(fan_relay, False)
    publish_status("ready")


setup()
while True:
    temp_c = fake_temperature_c()
    humidity = fake_humidity()
    dew_point_c = compute_dew_point(temp_c, humidity)
    update_cooling(temp_c, dew_point_c)
    publish_telemetry(temp_c, humidity, dew_point_c)
    handle_dispense()
    time.sleep_ms(1000)
