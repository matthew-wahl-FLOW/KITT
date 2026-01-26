// elevator_controller.ino
// // Controls elevator motors and limit switches
// // Ensures safe movement with hardware interlocks
// // Publishes position and status via MQTT gateway (via serial placeholder)
// // Interfaces: limit switches, motor driver, emergency stop

#include <Arduino.h>

const int kMotorEnablePin = 25;
const int kMotorDirectionPin = 26;
const int kLimitTopPin = 33;
const int kLimitBottomPin = 32;
const int kEmergencyStopPin = 27;

const int kMaxLevels = 3;
const unsigned long kLevelTravelMs = 2500;
const unsigned long kCommandTimeoutMs = 15000;
const unsigned long kMotionStallMs = 5000;

enum ElevatorState {
  ELEVATOR_IDLE,
  ELEVATOR_MOVING_UP,
  ELEVATOR_MOVING_DOWN,
  ELEVATOR_FAULT
};

ElevatorState elevatorState = ELEVATOR_IDLE;
int currentLevel = 0;
int targetLevel = 0;
unsigned long lastMoveMs = 0;
unsigned long lastProgressMs = 0;

void publishStatus(const char* status) {
  Serial.print("elevator/status ");
  Serial.println(status);
}

void publishPosition() {
  Serial.print("elevator/position level=");
  Serial.println(currentLevel);
}

void stopMotor() {
  digitalWrite(kMotorEnablePin, LOW);
}

void startMotor(ElevatorState newState) {
  elevatorState = newState;
  digitalWrite(kMotorDirectionPin, newState == ELEVATOR_MOVING_UP ? HIGH : LOW);
  digitalWrite(kMotorEnablePin, HIGH);
  lastMoveMs = millis();
  lastProgressMs = lastMoveMs;
}

void startMove(int requestedLevel) {
  if (requestedLevel < 0) {
    requestedLevel = 0;
  } else if (requestedLevel >= kMaxLevels) {
    requestedLevel = kMaxLevels - 1;
  }

  targetLevel = requestedLevel;
  if (targetLevel == currentLevel) {
    publishStatus("already_at_level");
    return;
  }

  if (targetLevel > currentLevel) {
    startMotor(ELEVATOR_MOVING_UP);
    publishStatus("moving_up");
  } else {
    startMotor(ELEVATOR_MOVING_DOWN);
    publishStatus("moving_down");
  }
}

void handleCommand() {
  if (!Serial.available()) {
    return;
  }
  String command = Serial.readStringUntil('\n');
  command.trim();
  if (command.startsWith("LEVEL")) {
    int level = command.substring(5).toInt();
    startMove(level);
  } else if (command == "UP") {
    startMove(currentLevel + 1);
  } else if (command == "DOWN") {
    startMove(currentLevel - 1);
  } else if (command == "STOP") {
    elevatorState = ELEVATOR_IDLE;
    stopMotor();
    publishStatus("stopped");
  }
}

void updateSafety() {
  if (digitalRead(kEmergencyStopPin) == LOW) {
    elevatorState = ELEVATOR_FAULT;
    stopMotor();
    publishStatus("emergency_stop");
  }
}

void updateMotion() {
  if (elevatorState != ELEVATOR_MOVING_UP && elevatorState != ELEVATOR_MOVING_DOWN) {
    return;
  }

  bool hitTop = digitalRead(kLimitTopPin) == LOW;
  bool hitBottom = digitalRead(kLimitBottomPin) == LOW;

  if (elevatorState == ELEVATOR_MOVING_UP && hitTop) {
    currentLevel = kMaxLevels - 1;
    lastProgressMs = millis();
  } else if (elevatorState == ELEVATOR_MOVING_DOWN && hitBottom) {
    currentLevel = 0;
    lastProgressMs = millis();
  } else if (millis() >= lastMoveMs + kLevelTravelMs) {
    if (elevatorState == ELEVATOR_MOVING_UP) {
      currentLevel = min(currentLevel + 1, kMaxLevels - 1);
    } else {
      currentLevel = max(currentLevel - 1, 0);
    }
    lastMoveMs = millis();
    lastProgressMs = lastMoveMs;
  }

  if (millis() >= lastProgressMs + kMotionStallMs) {
    stopMotor();
    elevatorState = ELEVATOR_FAULT;
    publishStatus("fault_stall");
    return;
  }

  if (currentLevel == targetLevel || hitTop || hitBottom ||
      millis() >= lastMoveMs + kCommandTimeoutMs) {
    stopMotor();
    elevatorState = ELEVATOR_IDLE;
    publishPosition();
    publishStatus("idle");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(kMotorEnablePin, OUTPUT);
  pinMode(kMotorDirectionPin, OUTPUT);
  pinMode(kLimitTopPin, INPUT_PULLUP);
  pinMode(kLimitBottomPin, INPUT_PULLUP);
  pinMode(kEmergencyStopPin, INPUT_PULLUP);
  stopMotor();
  publishStatus("ready");
  publishPosition();
}

void loop() {
  handleCommand();
  updateSafety();
  updateMotion();
  delay(50);
}
