# Kohaku Key V4 — Keycard Shell Architecture Draft

**Date:** November 4, 2026

**Status:** Feasibility research proposal. No Kohaku-specific Shell implementation verified as of November 5, 2026.

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

## V4 research tracks and checkpoints

V4 contains two complementary but independently evaluated research tracks.
Full Privacy Pools Groth16 proving on Shell is not a prerequisite for
credential integration.

### Track A — Privacy Pools credential integration

Goal: preserve the verified V3 Privacy Pools V1 credential and recovery
contract while reducing private material exposed to Kohaku CLI.

- A1: Confirm the documented Keycard 4.0 BIP-85 APDU contract.
- A2: Define ownership and cleanup of decrypted APDU and derived buffers.
- A3: Reproduce frozen V3 derivation using independent synthetic vectors.
- A4: Validate authenticated Keycard-to-Shell derivation and recovery.
- A5: Integrate Shell transport and approvals into Kohaku CLI.
- A6: Evaluate deposit, withdrawal, recovery and remaining host-secret exposure.

Each checkpoint must distinguish demonstrated isolation from intended
isolation. Host-side private witness generation remains an unresolved
security boundary, even when the BIP-85 root stays on Shell.

### Track B — Groth16 feasibility on Keycard Shell

Goal: determine which zero-knowledge cryptographic operations are
feasible within Shell's embedded memory and execution constraints.

- B1: Study the existing host test harness and CI conventions.
- B2: Select independently verified field and pairing test vectors.
- B3: Evaluate minimal Groth16 verification experiments.
- B4: Explore minimal proving configurations only when feasible.
- B5: Measure memory, execution time and embedded compatibility.
- B6: Document which capabilities, if any, are useful for Privacy Pools.

Full Privacy Pools proof generation is not claimed or targeted as an
initial Shell milestone.

### Research baseline and evidence policy

- Research repository: kohaku-key.
- Shell firmware worktree: keycard-shell-v4.
- Shell baseline: upstream/master at 7e38e45.
- V3 CLI compatibility reference: 9a2a285.
- Follow Keycard Shell AGENTS.md, CLAUDE.md and host-test conventions.
- Use synthetic, non-secret test vectors before physical hardware tests.
- Do not persist private keys, BIP-85 entropy, credentials or witnesses.
- Record successful and failed checkpoints without overstating results.
- Do not flash hardware or broadcast transactions during design review.

## First Shell proof of concept

First reproduce the V3 domain-separated credential derivation using synthetic test vectors. Then validate authenticated BIP-85 transport and secret-buffer cleanup on Shell. Computing Privacy Pools deposit precommitments entirely on Shell is a subsequent feasibility checkpoint.

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

V3 — Privacy Pools V1 has now demonstrated a mined Sepolia deposit, a hardware-signed partial withdrawal, independently recovered change-note credentials and a subsequent verified withdrawal simulation. These results provide the compatibility reference for V4. Shell-contained derivation, witness handling and Groth16 proving remain unverified.
