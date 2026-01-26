// fridge_controller.ino
// // Controls fridge dispenser servo, peltier cooler, and fan logic
// // Subscribes to MQTT via serial gateway or onboard WiFi (placeholder)
// // Publishes status: ready, dispensing, cooling, error
// // Interfaces: servo, door sensor, dispense sensor, temp/humidity sensor, peltier relay, fan relay

#include <Arduino.h>
#include <math.h>

const int kServoPin = 14;
const int kDoorSensorPin = 27;
const int kDispenseSensorPin = 26;
const int kPeltierRelayPin = 25;
const int kFanRelayPin = 33;

const float kTargetTempC = 3.0;
const float kTempDeadbandC = 1.0;
const float kDewpointMarginC = 1.0;
const float kHumidityPercent = 55.0;
const unsigned long kDispenseDurationMs = 1500;

bool peltierOn = false;
bool fanOn = false;

float fakeTemperatureC() {
  float phase = (millis() % 20000) / 20000.0;
  return kTargetTempC + 2.0 * sin(phase * 2.0 * PI);
}

float fakeHumidity() {
  float phase = (millis() % 15000) / 15000.0;
  return kHumidityPercent + 5.0 * cos(phase * 2.0 * PI);
}

float computeDewPoint(float tempC, float humidityPercent) {
  float alpha = ((17.27 * tempC) / (237.7 + tempC)) + log(humidityPercent / 100.0);
  return (237.7 * alpha) / (17.27 - alpha);
}

void publishTelemetry(float tempC, float humidityPercent, float dewPointC) {
  Serial.print("fridge/telemetry temp_c=");
  Serial.print(tempC, 2);
  Serial.print(" humidity=");
  Serial.print(humidityPercent, 1);
  Serial.print(" dewpoint_c=");
  Serial.println(dewPointC, 2);
}

void publishStatus(const char* status) {
  Serial.print("fridge/status ");
  Serial.println(status);
}

void setRelay(int pin, bool enabled) {
  digitalWrite(pin, enabled ? HIGH : LOW);
}

void updateCooling(float tempC, float dewPointC) {
  if (tempC > kTargetTempC + kTempDeadbandC) {
    peltierOn = true;
  } else if (tempC < kTargetTempC - kTempDeadbandC) {
    peltierOn = false;
  }

  if (tempC - dewPointC <= kDewpointMarginC) {
    fanOn = false;
  } else {
    fanOn = true;
  }

  setRelay(kPeltierRelayPin, peltierOn);
  setRelay(kFanRelayPin, fanOn);
}

void handleDispense() {
  if (!Serial.available()) {
    return;
  }
  String command = Serial.readStringUntil('\n');
  command.trim();
  if (command != "DISPENSE") {
    return;
  }

  bool doorClosed = digitalRead(kDoorSensorPin) == LOW;
  if (!doorClosed) {
    publishStatus("error_door_open");
    return;
  }

  publishStatus("dispensing");
  delay(kDispenseDurationMs);
  bool dispensed = digitalRead(kDispenseSensorPin) == LOW;
  if (dispensed) {
    publishStatus("done");
  } else {
    publishStatus("error_dispense_timeout");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(kServoPin, OUTPUT);
  pinMode(kDoorSensorPin, INPUT_PULLUP);
  pinMode(kDispenseSensorPin, INPUT_PULLUP);
  pinMode(kPeltierRelayPin, OUTPUT);
  pinMode(kFanRelayPin, OUTPUT);
  setRelay(kPeltierRelayPin, false);
  setRelay(kFanRelayPin, false);
  publishStatus("ready");
}

void loop() {
  float tempC = fakeTemperatureC();
  float humidity = fakeHumidity();
  float dewPointC = computeDewPoint(tempC, humidity);
  updateCooling(tempC, dewPointC);
  publishTelemetry(tempC, humidity, dewPointC);
  handleDispense();
  delay(1000);
}
