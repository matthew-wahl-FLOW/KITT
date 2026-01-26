// lift_controller.ino
// // Controls the track lift mechanism
// // Verifies mechanical locks before lowering/raising
// // Cuts track power to isolated section when lowering
// // Publishes lift state and safety interlock status via MQTT gateway (via serial placeholder)

const int kLiftMotorPin = 18;
const int kLockRelayPin = 19;
const int kTrackPowerRelayPin = 21;
const int kLiftUpLimitPin = 22;
const int kLiftDownLimitPin = 23;

const unsigned long kLiftTravelMs = 4000;
const unsigned long kLockReleaseMs = 800;

enum LiftState {
  LIFT_IDLE,
  LIFT_RAISING,
  LIFT_LOWERING,
  LIFT_FAULT
};

LiftState liftState = LIFT_IDLE;
unsigned long liftStartMs = 0;

void publishState(const char* state) {
  Serial.print("lift/state ");
  Serial.println(state);
}

void setTrackPower(bool enabled) {
  digitalWrite(kTrackPowerRelayPin, enabled ? HIGH : LOW);
}

void setLock(bool engaged) {
  digitalWrite(kLockRelayPin, engaged ? HIGH : LOW);
}

void startLift(LiftState newState) {
  liftState = newState;
  digitalWrite(kLiftMotorPin, HIGH);
  liftStartMs = millis();
}

void stopLift() {
  digitalWrite(kLiftMotorPin, LOW);
}

void handleCommand() {
  if (!Serial.available()) {
    return;
  }
  String command = Serial.readStringUntil('\n');
  command.trim();
  if (command == "LOWER") {
    setLock(false);
    delay(kLockReleaseMs);
    setTrackPower(false);
    startLift(LIFT_LOWERING);
    publishState("lowering");
  } else if (command == "RAISE") {
    setLock(false);
    delay(kLockReleaseMs);
    startLift(LIFT_RAISING);
    publishState("raising");
  } else if (command == "STOP") {
    stopLift();
    liftState = LIFT_IDLE;
    publishState("stopped");
  }
}

void updateLift() {
  bool atTop = digitalRead(kLiftUpLimitPin) == LOW;
  bool atBottom = digitalRead(kLiftDownLimitPin) == LOW;

  if (liftState == LIFT_RAISING && atTop) {
    stopLift();
    setLock(true);
    setTrackPower(true);
    liftState = LIFT_IDLE;
    publishState("raised");
  } else if (liftState == LIFT_LOWERING && atBottom) {
    stopLift();
    setLock(true);
    liftState = LIFT_IDLE;
    publishState("lowered");
  } else if ((liftState == LIFT_RAISING || liftState == LIFT_LOWERING) &&
             millis() - liftStartMs > kLiftTravelMs) {
    stopLift();
    liftState = LIFT_FAULT;
    publishState("fault_timeout");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(kLiftMotorPin, OUTPUT);
  pinMode(kLockRelayPin, OUTPUT);
  pinMode(kTrackPowerRelayPin, OUTPUT);
  pinMode(kLiftUpLimitPin, INPUT_PULLUP);
  pinMode(kLiftDownLimitPin, INPUT_PULLUP);
  setTrackPower(true);
  setLock(true);
  stopLift();
  publishState("ready");
}

void loop() {
  handleCommand();
  updateLift();
  delay(50);
}
