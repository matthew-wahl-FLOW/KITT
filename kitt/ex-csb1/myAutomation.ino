// Minimal production EX-RAIL skeleton for EX-CSB1.
// Keep this file deterministic: no dynamic memory, no networking, no Pi/JMRI logic.
// EX-RAIL macros compile into static tables; edit IDs to match your layout plan.

// ---- Track Sections (Blocks) -------------------------------------------------
// Blocks are logical reservations used by RESERVE/FREE to keep trains separated.
// Update IDs/descriptions to match your physical occupancy plan.

// These are logical blocks only; occupancy sensors are optional and configured elsewhere.
// There is intentionally no runtime sensor wiring here.
ALIAS(BLOCK_MAIN, 1)
ALIAS(BLOCK_SIDING, 2)

// ---- Sensors (Optional) -------------------------------------------------------
// Sensor IDs are VPINs. Update to match your wiring/JMRI table when used.
ALIAS(SENSOR_CROSSOVER_EXIT, 40)
ALIAS(SENSOR_SIDING_EXIT, 41)

// ---- Turnouts ----------------------------------------------------------------
// Turnouts are declared so routes can set safe paths.
// First parameter is the EX-RAIL turnout ID; addr/subaddr are DCC accessory addresses.

TURNOUT(1, 100, 0, "Mainline crossover")
TURNOUT(2, 101, 0, "Siding entry")

// ---- Routes ------------------------------------------------------------------
// Routes are reusable, deterministic turnout alignments.

ROUTE(1, "Route: Mainline")
  // Mainline path: both turnouts closed.
  CLOSE(1)
  CLOSE(2)
DONE

ROUTE(2, "Route: Siding")
  // Diverging path: throw both turnouts.
  THROW(1)
  THROW(2)
DONE

// ---- Automation --------------------------------------------------------------
// Automations should only coordinate safe movement on the command station.
// They must not depend on Pi services or network messages.

AUTOMATION(10, "Interlock: protect crossover")
  // Ensure route is clear before allowing movement into the shared crossover.
  RESERVE(BLOCK_MAIN)
  ROUTE(1)
  AFTER(SENSOR_CROSSOVER_EXIT) // release only after the train clears the block
  FREE(BLOCK_MAIN)
DONE

AUTOMATION(20, "Interlock: siding only if clear")
  // Non-blocking check: only set the siding route if the block is available.
  IFRESERVE(BLOCK_SIDING)
    ROUTE(2)
    AFTER(SENSOR_SIDING_EXIT)
    FREE(BLOCK_SIDING)
  ENDIF
DONE

// ---- Startup Safety ----------------------------------------------------------
// Startup keeps the track safe and predictable. Leave power off until manually enabled.

AUTOSTART
POWEROFF
DONE
