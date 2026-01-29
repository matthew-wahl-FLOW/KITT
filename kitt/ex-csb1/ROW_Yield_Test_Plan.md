# KITT – Right Of Way (ROW) Yield Test Plan

## Purpose

This document defines the formal test procedures used to verify
that **Right Of Way (ROW) yield behavior** is correctly enforced by
EXRAIL on the EX-CSB1 command station.

ROW yield is a **safety-critical feature** that ensures opposing trains
cannot occupy conflicting single-track blocks.

This test plan validates that:
- Conflicting routes are never permitted
- Freight trains yield correctly to the Kokanee delivery train
- Yield occurs only when necessary
- Normal operation resumes safely after clearance

---

## Scope

This document covers **EXRAIL firmware behavior only**.

It explicitly excludes:
- Raspberry Pi automation
- JMRI schedules or scripts
- Sound effects (horns, bells)
- Time-of-day logic
- Beer loading, elevators, or sensors

All tests are performed with:
- EXRAIL loaded on EX-CSB1
- Manual or JMRI throttle control
- No Pi automation running

---

## Definitions

### Sidings
- **BEER_LOADING** – Kokanee train default parking location
- **BEER_UNLOADING** – Delivery / lift siding
- **RIGHT_OF_WAY (ROW)** – Passing siding used for yielding

### Consists
- **Consist 1 (Kokanee Transport)**  
  Two SD40-2 locomotives, back-to-back  
  Absolute priority when active

- **Consist 2 (BCOL Freight)**  
  M420-A + M420-B, elephant style  
  Must yield to Kokanee train

---

## Preconditions (Required for All Tests)

- EXRAIL firmware compiled and flashed
- Block detection functioning correctly
- Turnouts respond reliably
- Trains are mechanically sound
- No Pi services running
- No automatic scheduling enabled

---

## Test 1 – Static Conflict Prevention

### Objective
Verify that EXRAIL prevents conflicting routes from being set.

### Setup
- Place BCOL Freight train on mainline block
- Kokanee train parked at BEER_LOADING siding
- ROW siding empty

### Procedure
1. Activate Freight mainline route
2. Attempt to activate Kokanee mainline route

### Expected Result
- Kokanee route is rejected or delayed
- No turnouts move into conflicting positions
- No unexpected train movement occurs

### Pass Criteria
- Conflicting routes cannot be active simultaneously

---

## Test 2 – Forced Yield to ROW

### Objective
Verify that freight is forced into ROW when Kokanee is dispatched.

### Setup
- Freight train running on mainline
- Kokanee train parked at BEER_LOADING
- ROW siding empty

### Procedure
1. Request Kokanee mainline route
2. Observe turnout and block behavior

### Expected Result
- Freight route to mainline is cancelled
- Turnouts align to ROW siding
- Freight enters ROW block
- Freight stops fully within ROW
- Kokanee route becomes active

### Pass Criteria
- Freight yields automatically and safely

---

## Test 3 – Late Yield (No Early Yield)

### Objective
Ensure freight does not yield unnecessarily.

### Setup
- Freight train running on mainline far from conflict
- Kokanee parked at BEER_LOADING
- No Kokanee route requested

### Procedure
1. Observe freight operation with no Kokanee dispatch
2. Request Kokanee route only when conflict is imminent

### Expected Result
- Freight continues uninterrupted until Kokanee is dispatched
- No early turnout movement
- Yield occurs only after Kokanee route request

### Pass Criteria
- Yield is delayed until required for safety

---

## Test 4 – Release After Kokanee Clears

### Objective
Verify ROW is released only after Kokanee clears conflict blocks.

### Setup
- Freight stopped in ROW siding
- Kokanee traversing mainline

### Procedure
1. Allow Kokanee to clear mainline conflict blocks
2. Observe block release and route availability

### Expected Result
- ROW block remains locked while Kokanee occupies conflict blocks
- After clearance:
  - ROW is released
  - Freight mainline route becomes available
  - Freight may resume operation

### Pass Criteria
- No premature release
- Freight resumes only when safe

---

## Failure Conditions (Must Never Occur)

- Head-on movement on single track
- Turnout thrown under a train
- Two trains occupying the same block
- Freight released before Kokanee clears
- Kokanee blocked by a yielded freight train

Any failure requires immediate halt and firmware review.

---

## Notes

- These tests must pass before enabling Pi or JMRI automation
- Repeat tests after any EXRAIL changes
- Document all failures with block and turnout states

---

## Revision History

- v1.0 – Initial ROW yield validation plan
