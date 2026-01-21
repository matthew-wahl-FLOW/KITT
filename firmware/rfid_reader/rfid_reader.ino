// rfid_reader.ino
// // Reads RFID tags on locomotives and flat cars
// // Publishes tag reads and signal strength via MQTT gateway
// // Debounces reads and verifies tag identity before triggering actions
//
// PSEUDOCODE:
// setup(): init RFID module, serial/MQTT gateway
// loop(): poll tags -> if new_tag_detected -> debounce -> publish "rfid/{reader_id}/tag/{tag_id}"
