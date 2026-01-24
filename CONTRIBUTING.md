# Contributing

## Overview
Thank you for contributing to KITT. Please keep changes small and focused, and follow the
project safety expectations.

## Branching and Reviews
- Use short-lived branches: `feature/*`, `fix/*`, `chore/*`.
- Open PRs against `main` and request at least one review.

## Coding Style
- Python: follow PEP 8 conventions.
- JavaScript: follow existing lint rules when present.
- Firmware: keep pin constants and safety limits explicit.

## Safety Rules
- No live tests without two-person sign-off and emergency stop access.
- Document any safety-impacting changes in the PR description.

## Tests
Run unit tests before opening a PR:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Missing Info for Further Development
- **Inputs**: Required tooling versions and local setup steps.
- **Outputs**: Release notes expectations.
- **Actions**: Code owners and escalation contacts.
- **Methods**: Documentation review process.
