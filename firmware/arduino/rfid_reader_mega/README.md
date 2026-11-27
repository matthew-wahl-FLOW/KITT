# RFID Reader (Arduino Mega)

Arduino C++ sketch for an Arduino Mega 2560 (Keystudio clone) reading a Seeed Grove
125 kHz RFID reader. It reports tag reads over USB serial to the Pi bridge
(`services/pi_services/rfid_bridge.py`).

This folder is Arduino C++. It is not MicroPython. The `firmware/*/*.ino` files
elsewhere in `firmware/` are MicroPython.

## Wiring

| Reader (Grove) | Mega                          | Notes                          |
|----------------|-------------------------------|--------------------------------|
| VCC            | 5V                            | Reader power from the Mega     |
| GND            | GND                           | Common ground with the Mega only |
| TX             | pin 19 (RX1)                  | Serial1 receive                |
| RX             | not connected                 | Read-only use                  |

- Power the Mega from the Pi's USB port. Do not connect the Mega's GND to the track,
  to the EX-CSB1 DCC outputs, or to any rail.
- The MEGA Sensor Shield v1.3 may have only 3-pin headers. Use a Grove-to-jumper cable
  and wire VCC, GND, and TX to the matching pins. Check the labels on your board.

## Frame format

Assumed (RDM6300-style, common for 125 kHz Grove readers): 9600 baud, frame
`STX (0x02) + 10 ASCII hex ID characters + 2 ASCII hex checksum characters + ETX (0x03)`,
where the checksum is the XOR of the five ID bytes. Verify against your reader's
datasheet and the echo test below. If your reader differs, change `kReaderBaud` and
`decodeFrame()`.

## Output (USB serial, 115200 baud)

```
READY rfid_reader_mega
TAG 0A1B2C3D4E
ERR checksum
```

## Build and flash

Using arduino-cli on the Pi (install it first, or use the Arduino IDE on another machine):

```bash
arduino-cli core install arduino:avr
arduino-cli compile --fqbn arduino:avr:mega:cpu=atmega2560 firmware/arduino/rfid_reader_mega
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:mega:cpu=atmega2560 firmware/arduino/rfid_reader_mega
```

The port may be `/dev/ttyACM0` or `/dev/ttyUSB0`. Check with `ls /dev/ttyACM* /dev/ttyUSB*`
before and after plugging the Mega in.

## Echo test (before connecting JMRI)

1. Flash the sketch.
2. Open the serial port at 115200 baud and hold a tag near the reader:

```bash
stty -F /dev/ttyUSB0 115200 raw -echo && cat /dev/ttyUSB0
```

You should see `READY rfid_reader_mega` once, then `TAG <id>` each time a tag is read.
If you see only `ERR` lines, the reader's baud rate or frame format differs from the
assumption above. Send me the raw output and I will adjust the sketch.
