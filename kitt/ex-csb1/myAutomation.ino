// Minimal production EX-RAIL skeleton for EX-CSB1.
// Keep this file deterministic: no dynamic memory, no networking, no Pi/JMRI logic.
// EX-RAIL macros compile into static tables; edit IDs to match your layout plan.
// The IDs below align with the KITT layout scaffold (main loop, staging siding, delivery spur).

// ---- Track Sections (Blocks) -------------------------------------------------
// Blocks are logical reservations used by RESERVE/FREE to keep trains separated.
// Update IDs/descriptions to match your physical occupancy plan.

// These are logical blocks only; occupancy sensors are optional and configured elsewhere.
// There is intentionally no runtime sensor wiring here.
ALIAS(BLOCK_MAIN_LOOP, 1)
ALIAS(BLOCK_STAGING_SIDING, 2)
ALIAS(BLOCK_DELIVERY_SPUR, 3)

// ---- Sensors (Optional) -------------------------------------------------------
// Sensor IDs are VPINs. Update to match your wiring/JMRI table when used.
ALIAS(SENSOR_LOOP_EXIT, 40)
ALIAS(SENSOR_STAGING_EXIT, 41)
ALIAS(SENSOR_DELIVERY_EXIT, 42)

// ---- Turnouts ----------------------------------------------------------------
// Turnouts are declared so routes can set safe paths.
// First parameter is the EX-RAIL turnout ID; addr/subaddr are DCC accessory addresses.

TURNOUT(1, 100, 0, "Main loop to staging siding")
TURNOUT(2, 101, 0, "Staging siding to delivery spur")

// ---- Routes ------------------------------------------------------------------
// Routes are reusable, deterministic turnout alignments.

ROUTE(1, "Route: Main loop")
  // Main loop path: keep turnouts aligned to the loop.
  CLOSE(1)
  CLOSE(2)
DONE

ROUTE(2, "Route: Staging siding")
  // Staging path: diverge from the main loop, keep the spur closed.
  THROW(1)
  CLOSE(2)
DONE

ROUTE(3, "Route: Delivery spur")
  // Delivery path: diverge from the main loop and enter the spur.
  THROW(1)
  THROW(2)
DONE

// myAutomation.h — First automation test for loco 6313
// Optional manual trigger from Engine Driver / WiThrottle
ROUTE(101, "Noon Test (6313)")
  SENDLOCO(6313, 201)      // run sequence 201 on loco 6313
DONE

// The work sequence (lights + bell, horn×3, run 30 s at speed 25)
SEQUENCE(201)
  SETLOCO(6313)            // select loco

  // Lights (F0) and bell (F1) on
  FON(0)
  FON(1)
  DELAY(1500)

  // Horn (F2) three short blasts
  FON(2); DELAY(400); FOFF(2);
  DELAY(300);
  FON(2); DELAY(400); FOFF(2);
  DELAY(300);
  FON(2); DELAY(400); FOFF(2);

  // (Optional) stop the bell before moving; comment out to keep bell ringing
  FOFF(1)

// ---- Automation --------------------------------------------------------------
// Automations should only coordinate safe movement on the command station.
// They must not depend on Pi services or network messages.

AUTOMATION(10, "Interlock: main loop")
  // Reserve the main loop before setting the loop route.
  RESERVE(BLOCK_MAIN_LOOP)
  ROUTE(1)
  // Release only after the train clears the loop exit.
  AFTER(SENSOR_LOOP_EXIT)
  FREE(BLOCK_MAIN_LOOP)
DONE

AUTOMATION(20, "Interlock: staging siding")
  // Reserve the shared loop plus the staging block before entry.
  RESERVE(BLOCK_MAIN_LOOP)
  RESERVE(BLOCK_STAGING_SIDING)
  ROUTE(2)
  AFTER(SENSOR_STAGING_EXIT)
  FREE(BLOCK_STAGING_SIDING)
  FREE(BLOCK_MAIN_LOOP)
DONE

AUTOMATION(30, "Interlock: delivery spur")
  // Reserve the shared loop plus the delivery block before entry.
  RESERVE(BLOCK_MAIN_LOOP)
  RESERVE(BLOCK_DELIVERY_SPUR)
  ROUTE(3)
  AFTER(SENSOR_DELIVERY_EXIT)
  FREE(BLOCK_DELIVERY_SPUR)
  FREE(BLOCK_MAIN_LOOP)
DONE

// ---- Startup Safety ----------------------------------------------------------
// Startup keeps the track safe and predictable. Leave power off until manually enabled.

AUTOSTART
// POWEROFF
DONE
