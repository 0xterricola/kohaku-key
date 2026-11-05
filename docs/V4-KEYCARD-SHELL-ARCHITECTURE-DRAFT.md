# Kohaku Key V4 — Keycard Shell Architecture Draft

**Date:** November 4, 2026
**Status:** Research proposal. Not implemented.

## Goal

Move Privacy Pools credential derivation into Keycard Shell so the macOS host never receives the BIP-85 root or private Privacy Pools credential material.

V3 remains the cryptographic compatibility reference.

## Proposed trust boundaries

```text
Keycard 4.0 secure element
  - Master seed
  - BIP-85 root derivation
  - ECDSA transaction signing
         |
         | Authenticated internal smartcard interface
         v
Keycard Shell firmware
  - BIP-85 entropy in volatile Shell RAM
  - Exact V3-R3 HMAC derivation
  - Privacy Pools credential operations
  - Public precommitment and calldata construction
  - Transaction review and physical approval
  - Best-effort sensitive-buffer clearing
         |
         | Approved public outputs via QR or USB
         v
Kohaku CLI / macOS
  - Public blockchain synchronization
  - RPC calls
  - Broadcasting
  - Receipt verification
```

The root still leaves the secure element. Shell firmware and its memory become part of the trusted computing base.

## Existing firmware workflow

The Keycard maintainer has previously supplied custom Keycard Shell firmware during GapPGP/OpenPGP development.

This establishes a practical experimental firmware workflow, subject to maintainer approval for Kohaku-specific builds.

No Kohaku-specific Shell implementation has yet been verified.

## First Shell proof of concept

Reproduce the V3 Privacy Pools deposit precommitment on Shell without exposing BIP-85 entropy to macOS.

Implementation stages:

1. Add an internal Keycard 4.0 BIP-85 operation.
2. Port the frozen R3 HMAC derivation.
3. Match V3 deterministic credential vectors.
4. Implement SDK-compatible precommitment construction.
5. Display and approve public deposit parameters.
6. Export only explicitly approved public outputs.

The derivation domain, paths, credential identifiers, and deposit-index mapping must remain compatible with V3.

## Transaction signing

The Shell should validate and display the chain ID, entrypoint, asset, amount, nonce, fee parameters and digest before authorizing the card signature.

The host supplies transaction context but is not trusted to authorize signing.

## Withdrawal and ZK proving

Privacy Pools withdrawals require private witness construction and zero-knowledge proof generation.

Full native proof generation on Shell has not been demonstrated. Benchmark:

- Memory required for private witness construction
- Merkle-path processing
- Proving artifacts and working buffers
- Native proving execution time
- Sensitive-memory lifetime
- Recovery and failure handling

If proving cannot run securely inside Shell, the architecture needs a separate explicit trust-boundary decision. Moving private witnesses to macOS would weaken the intended isolation.

## Security requirements

- Master seed remains inside the secure element.
- BIP-85 entropy never reaches the host.
- Preserve V3-R3 recovery compatibility.
- Reject unexpected derivation paths and chain parameters.
- Review malicious host inputs, firmware authenticity, user confirmation and IPC framing.
- Do not treat deterministic test vectors as an end-to-end security proof.

## Relationship to V3

V3 should first establish an approved Sepolia deposit and independently recoverable note. Shell development can then use that evidence as its compatibility oracle.
