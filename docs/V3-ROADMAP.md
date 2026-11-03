# Kohaku Key — V3 Research Roadmap

**Status:** Planned; no V3 capability validated as of November 2, 2026.
**Governing proposal:** [V3 technical proposal](V3-PROPOSAL.md). V2 remains frozen at the published PoC tag.

| Stage | Work | Exit evidence / decision |
| --- | --- | --- |
| **R0 — Requirements** | Inspect Kohaku Privacy Pools `EnvelopeSigner`, note creation, restore and proving flows | Exact secret/data-flow map, compatibility oracle, risk model |
| **R1 — Applet 3.1** | Investigate EIP-1581 restricted BIP-32 key export and deterministic privacy credential derivation | Host disclosure, recovery and compatibility evidence |
| **R2 — Applet 4.0** | Independently investigate native BIP-85 and ECDH on experimental card | Determinism, recovery, host exposure and security findings |
| **R3 — Privacy Pools feasibility** | Compare candidate outputs against real protocol credentials and backup recovery | Explicit go/no-go on an adapter and funded testnet note experiment |
| **R4 — Conditional prototype** | If R3 passes, implement minimal adapter and disposable testnet note lifecycle | Reproducible flow and independently verified restore / outcome |
| **R5 — RAILGUN mapping** | Inventory distinct viewing, spending, nullifier and proving requirements | Separate feasibility decision, not implied implementation |

## Non-negotiable gates

Do not start R4 without stable protocol-compatible credentials and tested restart/backup recovery. Never derive persistent notes from randomized ECDSA signatures. Do not publish credentials or note secrets. A hardware-signed Ethereum transaction is not evidence of private-note key custody.

## First three research questions

1. What are the exact inputs, outputs, lengths, determinism and recovery semantics required by Kohaku Privacy Pools' current `EnvelopeSigner` and note implementation?
2. Can applet 3.1 EIP-1581 derivation provide reproducible Privacy Pools inputs, and what secrets leave the card?
3. Can applet 4.0 BIP-85 or ECDH produce protocol-compatible, recoverable credentials?

Record findings with versioned evidence. A negative result can close an investigation but not justify inventing unverified hardware support.

## R0 contract evidence

[Privacy Pools credential and recovery contract](V3-R0-PRIVACY-POOLS-CONTRACT.md)

## R0 offline oracle checkpoint

Eight offline reference checks passed. Deterministic credential derivation was verified across new SDK manager instances. Full note-state rediscovery and hardware recovery remain open. See [R0 contract](V3-R0-PRIVACY-POOLS-CONTRACT.md).

## R1 public derivation checkpoint

Physical Keycard 3.1 EIP-1581 public derivation passed across reconnects. The original V2 Ethereum address was unchanged. Private export and credential recovery remain untested. See [R1 hardware evidence](V3-R1-EIP1581-PUBLIC-EVIDENCE.md).

## R1 deterministic derivation compatibility

Seven in-memory simulated secret-manager tests passed. The R0 regression suite also passed eight checks. This establishes SDK interface compatibility, not hardware-backed credential recovery. See [R1 compatibility evidence](V3-R1-SECRET-MANAGER-COMPAT.md).

## R2 hardware checkpoint

[R2 applet 4.0 hardware evidence](V3-R2-APPLET4-HARDWARE-EVIDENCE.md)

## R3 hardware credential checkpoint

[R3 physical credential evidence](V3-R3-HARDWARE-CREDENTIAL-EVIDENCE.md)

## R4 cold-start recovery checkpoint

[R4 cold-start recovery](V3-R4-COLD-RECOVERY.md)
