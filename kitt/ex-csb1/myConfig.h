/*
 * Minimal, conservative EX-CSB1 configuration for KITT.
 * Keep this file small and deterministic. No networking and no dynamic runtime features.
 */

// Required: EX-CSB1 base hardware.
#define MOTOR_SHIELD_TYPE EXCSB1

// Safety: track power stays OFF until manually enabled.
// Automation in myAutomation.ino also starts with POWEROFF.
#define STARTUP_DELAY 3000

// Disable WiFi/Ethernet to keep the command station offline-first and deterministic.
#define ENABLE_WIFI false
#define ENABLE_ETHERNET false

// Reduce memory use for EX-RAIL on smaller boards when needed.
// #define DISABLE_EEPROM

// Optional: conservative max current limit (mA). Adjust to your PSU and booster.
// #define MAX_CURRENT 2000

// Optional: align turnout commands with NMRA RCN-213 if required by layout wiring.
// #define DCC_TURNOUTS_RCN_213

// EX-RAIL is enabled by the presence of myAutomation.ino; no other config is required.
