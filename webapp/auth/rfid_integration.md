# RFID Integration

Overview: Notes on RFID login integration.
Details: Defines tag mapping and security expectations.

RFID readers provide a quick login flow for operators using registered tags.

## Flow
- Reader scans tag ID and submits it to the webapp.
- Webapp maps tag ID to a user account and role.
- Session uses the same permissions as a password login.

## Mapping
- Store tag IDs alongside user profiles in the auth data store.
- Support one primary tag per user and optional secondary tags.

## Security
- Treat tag IDs as credentials; rotate if a tag is lost.
- Log tag scans for audit and troubleshooting.

## Missing Info
- Inputs: exact reader protocol and tag ID format.
- Outputs: audit log fields emitted per scan.
- Actions: user-facing flow for registering or revoking tags.
- Methods: rate limiting for repeated tag scans.
