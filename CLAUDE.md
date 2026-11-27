# CLAUDE.md

Project facts for KITT (model-railroad beer delivery system). Verified from the repo.

## Tests
- Run unit tests with: `python -m unittest discover -s tests -p "test_*.py"`
- CI runs the same command on Python 3.11 (`.github/workflows/ci.yml`) with no pip install.
- Only files named `test_*.py` are discovered. `tests/integration/sim_train_run.py` is NOT run by CI.

## Dependencies
- `requirements.txt` is stdlib-only. Do not add third-party packages without asking first.

## Web backend
- `webapp/backend/api.py` uses the stdlib `http.server` (single-threaded).
- Run locally: `python webapp/backend/api.py --host 127.0.0.1 --port 8080`
- Frontend stub: `webapp/frontend/dashboard_stub.html`.
- Runtime JSON files are committed in `webapp/backend/data/` (staff roster, leaderboards).

## Orders
- Order persistence is SQLite in `services/orders/` (`OrderService` over `OrderStorage`).
- Default DB: `services/data/orders.db`. It is gitignored. Never commit it.

## Firmware
- Files in `firmware/*/*.ino` are MicroPython despite the extension. Do not compile them as Arduino C++.
- Files under `firmware/arduino/` are real Arduino C++ (for example `firmware/arduino/rfid_reader_mega/`). Compile them with `arduino-cli`, not MicroPython.

## Safety
- The system dispenses alcohol. Keep changes that touch dispensing or motion conservative.
- No live hardware tests without two-person sign-off and emergency-stop access (`CONTRIBUTING.md`).

## Git workflow
- Use short-lived branches: `feature/*`, `fix/*`, `chore/*`. Open PRs against `main`.
