// lift_controller.ino
// // Controls the track lift mechanism
// // Verifies mechanical locks before lowering/raising
// // Cuts track power to isolated section when lowering
// // Publishes lift state and safety interlock status via MQTT gateway
//
// PSEUDOCODE:
// setup(): init relays, locks, sensors; publish "lift/state"
// loop(): on command lower -> verify lock released -> cut track power -> lower -> publish "lift/lowered"
// on raise -> raise -> restore track power -> publish "lift/raised"
