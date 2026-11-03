# V3-R1 — Keycard 3.1 EIP-1581 Public Derivation

**Status:** Physical public-derivation checkpoint passed.
**Hardware:** Retail Keycard, applet 3.1.
**Reader:** HID Global OMNIKEY 3x21.
**Date:** November 2, 2026.

## Objective

Validate EIP-1581 child-key derivation on physical
Keycard hardware without exporting private material.

## Test configuration

- Derivation: `m/43'/60'/1581'/0'/0`
- Interface: V2 native Go Keycard bridge
- Operation: `get-address`
- Export mode: `P2ExportKeyPublicOnly`
- Derivation mode: derive without make-current
- Authentication: interactive PIN through `/dev/tty`

## Physical results

### EIP-1581 public identity

Address:

`0xB916B4D7310bfE3f370f7b71Af95a84a5597f82f`

After removing and reinserting the card, the same
derivation path produced the same Ethereum address.

**Result: PASS**

### Original V2 account identity

Path: `m/44'/60'/0'/0/0`

Expected and observed address:

`0xB8A0f79E6d64c948E9F5ea32aD93647777915EBa`

**Result: PASS**

## Security boundaries

- No private-key export was performed.
- No signing or blockchain transaction was performed.
- No PIN was supplied through shell arguments or environment.
- The bridge requested public-only key material.
- The V2 Ethereum identity was unchanged.
- The current on-card derivation-path state was not independently inspected.

## Remaining R1 research

- Analyze private-export handling without exposing real
  credential material in terminal output or logs.
- Establish domain-separated Privacy Pools derivation.
- Validate deterministic private material with controlled fixtures.
- Evaluate host memory exposure and cleanup.
- Verify device-backup and note recovery separately.
- Test compatibility with the R0 Privacy Pools contract.

Public-key reproducibility does not establish deterministic
privacy secrets, backup recoverability, or hardware isolation.
