// rfid_reader_mega.ino
//
// Arduino Mega 2560 (Keystudio clone) reading a Seeed Grove 125 kHz RFID reader
// on Serial1 and reporting tag reads on USB serial for the Pi bridge
// (services/pi_services/rfid_bridge.py).
//
// Wiring (see README.md in this folder):
//   Reader VCC -> Mega 5V, reader GND -> Mega GND, reader TX -> Mega pin 19 (RX1).
//   The Mega is powered from the Pi's USB port. Nothing here connects to the
//   track, the EX-CSB1 DCC outputs, or any rail.
//
// USB serial output at 115200 baud:
//   READY rfid_reader_mega        once at boot
//   TAG 0A1B2C3D4E                one line per tag read (repeat reads debounced)
//   ERR <reason>                  malformed frame, ignored by the Pi bridge
//
// Reader frame (RDM6300-style; verify against your reader's datasheet):
//   STX (0x02) + 10 ASCII hex ID characters + 2 ASCII hex checksum characters + ETX (0x03)
//   checksum = XOR of the five ID bytes.

#include <string.h>

const unsigned long kUsbBaud = 115200;
const unsigned long kReaderBaud = 9600;     // verify against the reader datasheet
const unsigned long kRepeatHoldMs = 1500;   // same tag within this window is one read
const uint8_t kStx = 0x02;
const uint8_t kEtx = 0x03;
const uint8_t kIdChars = 10;
const uint8_t kChecksumChars = 2;
const uint8_t kPayloadChars = kIdChars + kChecksumChars;  // 12

static uint8_t frame[kPayloadChars];
static uint8_t frameLen = 0;
static bool inFrame = false;

static char lastTag[kIdChars + 1] = "";
static unsigned long lastSeenMs = 0;
static bool haveLast = false;

// Returns the value of one hex digit, or -1 if the character is not hex.
static int hexValue(uint8_t c) {
  if (c >= '0' && c <= '9') return c - '0';
  if (c >= 'A' && c <= 'F') return c - 'A' + 10;
  if (c >= 'a' && c <= 'f') return c - 'a' + 10;
  return -1;
}

// Validates a 12-character payload and writes the 10-character uppercase ID to outId.
// outId must have room for kIdChars + 1 bytes.
static bool decodeFrame(const uint8_t *data, char *outId) {
  uint8_t bytes[5];
  for (uint8_t i = 0; i < 5; i++) {
    int hi = hexValue(data[2 * i]);
    int lo = hexValue(data[2 * i + 1]);
    if (hi < 0 || lo < 0) return false;
    bytes[i] = (uint8_t)((hi << 4) | lo);
  }

  int ckHi = hexValue(data[10]);
  int ckLo = hexValue(data[11]);
  if (ckHi < 0 || ckLo < 0) return false;
  uint8_t expected = (uint8_t)((ckHi << 4) | ckLo);

  uint8_t x = 0;
  for (uint8_t i = 0; i < 5; i++) x ^= bytes[i];
  if (x != expected) return false;

  for (uint8_t i = 0; i < kIdChars; i++) {
    uint8_t c = data[i];
    if (c >= 'a' && c <= 'f') c = c - 'a' + 'A';
    outId[i] = (char)c;
  }
  outId[kIdChars] = '\0';
  return true;
}

// Reports a valid tag unless it is a repeat read of the tag seen moments ago.
// Every read of a tag that is still present extends the hold window, so a card
// held in range produces exactly one TAG line.
static void handleTag(const char *id) {
  unsigned long now = millis();
  bool repeat = haveLast && strcmp(id, lastTag) == 0 && (now - lastSeenMs) < kRepeatHoldMs;

  strcpy(lastTag, id);
  lastSeenMs = now;
  haveLast = true;

  if (!repeat) {
    Serial.print(F("TAG "));
    Serial.println(id);
  }
}

void setup() {
  Serial.begin(kUsbBaud);
  Serial1.begin(kReaderBaud);
  Serial.println(F("READY rfid_reader_mega"));
}

void loop() {
  while (Serial1.available() > 0) {
    uint8_t c = (uint8_t)Serial1.read();

    if (c == kStx) {
      inFrame = true;
      frameLen = 0;
      continue;
    }
    if (!inFrame) continue;

    if (c == kEtx) {
      inFrame = false;
      if (frameLen != kPayloadChars) {
        Serial.println(F("ERR frame_length"));
      } else {
        char id[kIdChars + 1];
        if (decodeFrame(frame, id)) {
          handleTag(id);
        } else {
          Serial.println(F("ERR checksum"));
        }
      }
      frameLen = 0;
      continue;
    }

    // Some reader variants add CR/LF; ignore them inside a frame.
    if (c == '\r' || c == '\n') continue;

    if (frameLen >= kPayloadChars) {
      inFrame = false;
      frameLen = 0;
      Serial.println(F("ERR frame_overflow"));
      continue;
    }
    frame[frameLen++] = c;
  }
}
