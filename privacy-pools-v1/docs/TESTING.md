# Privacy Pools V1 — Testing

## Dependencies

Install with npm ci --ignore-scripts.

## Hardware integration tests

The existing npm test scripts interact with the Keycard
account adapter and may invoke physical card signing:

- test:hardware
- test:authorization
- test:transaction
- test:typed-data
- test:user-operation

Do not execute these tests in unattended CI.

Require explicit card authorization, controlled test
credentials, and verification of the selected reader.

Mocked RPC transports do not eliminate hardware access.

## Offline validation

JavaScript syntax checking with node --check is safe
without a physical Keycard.

## Publication policy

Never publish wallet secrets, seed phrases, pairing
credentials, or private key material.

Record physical and simulated test results separately.
