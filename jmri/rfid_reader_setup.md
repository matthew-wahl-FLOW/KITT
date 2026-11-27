# RFID Reader: JMRI Setup

Overview: Connects the Mega RFID reader (firmware/arduino/rfid_reader_mega) to JMRI through
the Pi bridge (services/pi_services/rfid_bridge.py).
Details: JMRI objects, JSON server checks, running the bridge, and troubleshooting.

The bridge reports each new tag read as:
- an internal **memory** holding the last tag ID, and
- an internal **sensor** that pulses ACTIVE for about one second.

Logix, Automat, or a panel can react to the sensor. The memory tells you which tag was read.

## 1. Create the JMRI objects

In PanelPro (or the headless profile):

1. **Sensor:** Tools > Tables > Sensors > Add. System name `ISRFID1` (internal sensor),
   user name `RFID Reader 1`.
2. **Memory:** Tools > Tables > Memories > Add. System name `IMRFIDLast` (internal memory),
   user name `RFID Last Tag`.

The names must match the bridge defaults (`--sensor ISRFID1`, `--memory IMRFIDLast`), or
pass your own names on the command line.

## 2. Check the JMRI JSON server

The bridge uses the JMRI JSON server (default `http://127.0.0.1:12080`). Its endpoints
vary between JMRI versions, so check them before running the bridge:

```bash
curl -s http://127.0.0.1:12080/json/sensor/ISRFID1
curl -s -X PUT -H 'Content-Type: application/json' \
  -d '{"name":"ISRFID1","state":2}' http://127.0.0.1:12080/json/sensor/ISRFID1
curl -s -X PUT -H 'Content-Type: application/json' \
  -d '{"name":"ISRFID1","state":4}' http://127.0.0.1:12080/json/sensor/ISRFID1
curl -s -X PUT -H 'Content-Type: application/json' \
  -d '{"name":"IMRFIDLast","value":"TEST"}' http://127.0.0.1:12080/json/memory/IMRFIDLast
```

- The sensor PUTs should change the state shown in the JMRI sensor table.
- If the **memory** PUT fails but the sensor PUTs work, run the bridge with `--no-memory`.
- If the **sensor** PUTs fail, do not run the bridge until this is fixed. Send the error
  output and your JMRI version, and the JSON sink will be updated to match.

## 3. Test without JMRI

```bash
python3 services/pi_services/rfid_bridge.py --port /dev/ttyUSB0 --dry-run
```

Hold a tag near the reader. You should see `RFID read tag=<id>` and
`DRY RUN sensor ISRFID1 = ACTIVE` / `INACTIVE` lines.

## 4. Run with JMRI

```bash
python3 services/pi_services/rfid_bridge.py --port /dev/kitt/rfid0 \
  --jmri-url http://127.0.0.1:12080 --sensor ISRFID1 --memory IMRFIDLast
```

Use `/dev/kitt/rfid0` after the udev rule is in place (see `deploy/udev/99-kitt-devices.rules`).
Stop with Ctrl+C.

## Troubleshooting

- **`serial port failed: ... closed`:** the Mega reset or was unplugged. Replug and restart.
  Opening the port can reset the Mega, so the bridge may see a `READY` line on startup.
- **`ERR checksum` / `ERR frame_length`:** the reader frame format or baud rate differs
  from the sketch assumption. See `firmware/arduino/rfid_reader_mega/README.md`.
- **No reads at all:** check the reader's power LED and wiring (VCC, GND, TX to pin 19),
  and hold the tag closer.
- **Sensor not changing in JMRI:** run the curl checks in section 2.
- **Same tag reads only once while held:** this is intended. Remove the tag for more than
  `--hold-seconds` (default 1.5) to get another event.
