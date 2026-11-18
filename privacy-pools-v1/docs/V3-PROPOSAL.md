# Kohaku Key — V3 Technical Research Proposal

> **Historical proposal (November 2, 2026).** The scoped Privacy Pools V1 research was subsequently completed. See the [V3 final report](V3-FINAL-RESEARCH-REPORT.md) and [current project status](PROJECT-STATUS.md). RAILGUN remains a separate future research track.

## Hardware-Backed Privacy Credentials and Protocol Authorization

**Original status (November 2, 2026):** Proposed research — experiments not yet accepted.
**Created:** November 2, 2026.
**Prerequisites:** Frozen V2 Sepolia PoC [`kohaku-key-v2-sepolia-poc`](https://github.com/0xterricola/kohaku-cli/tree/kohaku-key-v2-sepolia-poc).
**Primary protocol:** Kohaku Privacy Pools integration. **Secondary track:** RAILGUN requirements mapping.

## 1. Problem statement

V2 proved that a physical Keycard can authorize an Ethereum account and execute a batched ERC-4337 transaction. That result is not a privacy credential system. Privacy Pools and RAILGUN may have non-Ethereum note, spending and viewing secrets, protocol-specific derivation rules and host-side zero-knowledge proving inputs.

V1 also found that the tested Keycard's native ECDSA is randomized; deriving persistent credentials directly from ordinary signature bytes is not a recoverable design. V3 seeks a **documented compatibility answer**, with implementation only after feasible primitives and recovery are verified.

## 2. Research objective and expected outcome

Determine whether existing hardware offers a **reproducible, recoverable and protocol-compatible** mechanism for privacy credential generation or for hardware authorization of a private-protocol operation. Identify exactly which secrets stay on card, which reach the host, and which must reach proving code.

A positive outcome is a narrowly scoped, reproducible testnet Privacy Pools proof of concept with explicit custody/recovery guarantees. A negative outcome is a complete compatibility report describing why a candidate primitive cannot satisfy the protocol, plus a separate assessment of useful transaction-authorization-only integration.

A successful V3 outcome does **not** require novel cryptography, a universal private wallet, mainnet activity, or support for all privacy protocols.

## 3. Scope and hypotheses

**H1 — Retail Keycard / applet 3.1 / EIP-1581.** Investigate restricted BIP-32 private-key export, deterministic key derivation, host exposure, domain separation and backup recovery. Exported private material is not hardware-isolated.

**H2 — Experimental card / applet 4.0 / BIP-85 and ECDH.** Independently evaluate deterministic entropy export and key agreement, including their cryptographic boundaries and recovery requirements.

**H3 — Privacy Pools integration.** Inspect the real Kohaku `EnvelopeSigner` contract and note-creation/recovery lifecycle. Define exact deterministic bytes, encodings, domain tags, wallet/account assumptions and compatibility tests before proposing an adapter.

**H4 — RAILGUN later.** Document spending, viewing, nullifier and proving requirements independently. Do not assume a public Ethereum signer, a BIP-85 output or an ECDH shared secret can replace those protocol keys.

## 4. Research approach

### Stage A — Protocol specification and threat-model inventory

Read Kohaku's actual current Privacy Pools implementation, including the `EnvelopeSigner` interface and note restore path. Create a data-flow table of every secret and derivation. Define threat assumptions, backup/recovery constraints and tests. Record the exact upstream commit studied.

**Gate A:** A precise credential contract and recovery oracle exist; otherwise implementation waits.

### Stage B — Isolated hardware experiments

Run applet 3.1 EIP-1581 and applet 4.0 BIP-85/ECDH investigations separately. Record capability queries, rejection cases, stable test vectors, cross-session/restart behavior, firmware version, and device recovery. Compare determinism without publishing secret outputs. Explicitly log whether the host learns candidate secret material.

**Gate B:** Supported hardware primitive and deterministic, versioned derivation established. No paper-only compatibility claims.

### Stage C — Privacy Pools compatibility adapter (conditional)

Use the existing `EnvelopeSigner` contract when feasible. Keep the current keystore unchanged. Compare actual SDK-generated note commitments and reconstructed credentials across sessions/restarts against known-good test vectors. Require explicit user consent and no real funds.

**Gate C:** Credentials recover exactly, SDK consumes them without special-case protocol changes, and backup/device-loss limitations are documented.

### Stage D — Controlled testnet privacy lifecycle (conditional)

Only after Gate C: test creation, restoration, shield/withdraw or equivalent supported testnet note operations with disposable values. Combine V2 hardware-backed public execution only where semantically correct. Independently verify resulting on-chain state and avoid revealing linkable secret artifacts in logs.

**Gate D:** At least one complete reproducible testnet privacy workflow with documented security and recovery boundaries; otherwise report why the gate remained closed.

### Stage E — RAILGUN feasibility report

Map its cryptographic key ownership and proof/witness boundaries on its own terms. Recommend pursue, partial authorization-only support, or defer. Do not describe it as implemented unless independently demonstrated.

## 5. Test and evidence requirements

For each candidate primitive record firmware/applet and transport version, hardware identity, key-selection scope, input/nonce/context encoding, deterministic comparison, host-visible output, exception behavior, backup reproduction and oracle compatibility. Use anonymized test vectors where revealing material is unsafe.

Test card absent, PIN failure, reconnect, changed context, wrong derivation path, invalid peer public keys (for ECDH), and incompatible protocol parameters. Never mistake deterministic output for secure key isolation or cross-device recoverability.

## 6. Deliverables

- Versioned Privacy Pools protocol and credential compatibility map.
- Applet 3.1 EIP-1581 derivation/export and risk report.
- Applet 4.0 BIP-85/ECDH capability and risk report.
- Reproducible, non-secret test fixtures and recovery evidence.
- Go/no-go decision for a protocol-compatible hardware adapter.
- Conditional Privacy Pools testnet experiment; separate RAILGUN feasibility report.
- Updated architecture, threat model, README and research findings.

## 7. Explicit exclusions

Mainnet funds, production keys, new note formats, custom hardware, a replacement generic keystore, protocol-specific ZK circuit modifications, unverified cross-device secret cloning, claims of trusted display, and claiming RAILGUN integration from Privacy Pools results.

Keycard Shell / air-gapped signing remains a separate future transport research track, not a V3 prerequisite.

## 8. Success and stopping rules

**Research complete** means all core feasibility questions have evidence and a documented go/no-go decision. **Implementation PoC complete** requires actual compatible protocol operation and verified recovery, not just a testnet hardware-signed outer transaction. If no hardware primitive can satisfy the protocol, report the limitation and stop rather than weakened recovery/security assumptions.

[Roadmap](V3-ROADMAP.md) | [Hardware compatibility](HARDWARE-COMPATIBILITY.md) | [Architecture](ARCHITECTURE.md) | [Threat model](THREAT-MODEL.md) | [V2 outcome](V2-OUTCOME.md)
