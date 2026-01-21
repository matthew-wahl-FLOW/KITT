// fridge_controller.ino
// // Controls fridge dispenser servo and microcontroller logic
// // Subscribes to MQTT via serial gateway or onboard WiFi (placeholder)
// // Publishes status: ready, dispensing, error
// // Interfaces: servo, door sensor, dispense sensor, MQTT gateway
//
// PSEUDOCODE:
// setup(): init servo, sensors, comms; publish "fridge/ready"
// loop(): if dispense_command_received -> verify door closed -> run dispense sequence -> publish "fridge/dispensing" -> confirm dispense sensor -> publish "fridge/done" or "fridge/error"
