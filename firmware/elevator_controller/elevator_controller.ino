// elevator_controller.ino
// // Controls elevator motors and limit switches
// // Ensures safe movement with hardware interlocks
// // Publishes position and status via MQTT gateway
// // Interfaces: limit switches, motor driver, emergency stop
//
// PSEUDOCODE:
// setup(): init pins, calibrate limits, publish "elevator/ready"
// loop(): listen for move_to_level commands -> check interlocks -> move motor until limit switch -> publish "elevator/position"
