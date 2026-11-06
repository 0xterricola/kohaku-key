# Kohaku Key — Architecture and Trust Boundaries

**Updated:** November 5, 2026

**Status:** V1, V2 and V3 Privacy Pools V1 research milestones complete. V4 Shell isolation remains proposed.

## V1/V2 — Ethereum signing and execution

The tested flow is:

1. Kohaku CLI prepares transaction intent and validates chain, nonce, fees and delegation.
2. A viem-compatible Keycard interface requests physical signing.
3. The host recovers and verifies the signer and approved payload.
4. Submission follows explicit user authorization.
5. Ethereum receipts and events are checked and the operation journal is reconciled.

V2 demonstrated real EIP-1559 and EIP-7702/ERC-4337 execution on Sepolia.

Host-side approval is not a trusted device display.

## V3 — Privacy Pools V1 (verified)

The demonstrated architecture is:

1. **Keycard 4.0:** Authenticated BIP-85 entropy derivation.
2. **Go hardware bridge:** Volatile anonymous-pipe transfer of derived root material.
3. **Host credential provider:** Frozen, versioned HMAC derivation and Privacy Pools V1 legacy SecretManager integration.
4. **Host prover:** Private witness calculation, Groth16 proving and independent proof verification.
5. **Ethereum execution:** Physical Keycard signing, explicit broadcast approval and receipt verification.
6. **Recovery:** Fresh authenticated hardware sessions, change-note reconstruction and updated LeanIMT witness.
7. **Subsequent spendability:** A second verified proof and successful two-provider EVM simulation.

The BIP-85-derived root **enters host memory**. Credential derivation and proving are not hardware-contained.

The adapter is not automatically compatible with Kohaku's newer signature-derived note scheme or legacy HD-derived notes.

[Full V3 evidence](V3-FINAL-RESEARCH-REPORT.md)

## V3 — Additional protocols

Tornado Cash and RAILGUN have different credential, commitment, recovery and proving requirements.

Neither has a completed Keycard integration in this project.

## V4 — Proposed Shell isolation

The proposed architecture moves private credential derivation from the computer into Keycard Shell firmware.

The Keycard master seed would remain inside the secure element, while derived material would enter Shell RAM.

Shell firmware and MCU memory would become part of the trusted computing base.

Shell-contained witness generation and Groth16 proving have **not** been demonstrated.

## Verified trust boundaries

| Operation | Verified boundary | Remaining limitation |
| --- | --- | --- |
| Ethereum signing key | Held by Keycard during tested signing | No independent trusted transaction display |
| BIP-85 root | Derived by Keycard 4.0 | Exported into host memory in V3 |
| Note credentials | Reproduced across authenticated sessions | Host-based derivation |
| Groth16 witness | Calculated in host memory | No Shell-contained prover |
| Change-note recovery | Reconstructed from physical hardware | Versioned derivation and metadata must be preserved |
| Tornado Cash / RAILGUN | No hardware integration verified | Separate feasibility research |
| Keycard Shell | Proposed research target | Firmware isolation and computation limits unverified |

[Project status](PROJECT-STATUS.md) | [Security and recovery](SECURITY-AND-RECOVERY.md) | [Threat model](THREAT-MODEL.md)
