# Kohaku Key

**Independent research into hardware-backed Ethereum execution, recoverable privacy credentials and stronger hardware isolation.**

**Project status (November 5, 2026):** V1 hardware signing, V2 Sepolia execution and V3 Privacy Pools V1 research are complete within their defined scopes. V3 Tornado Cash and RAILGUN are separate future protocol tracks; V4 investigates Keycard Shell. See [current project status](docs/PROJECT-STATUS.md). This independent research does not imply upstream acceptance, a security audit or mainnet readiness.

## Executive summary

Kohaku Key explores a specific boundary: **what can a physical cryptographic device safely authorize or protect in an Ethereum wallet that supports privacy protocols?** Ethereum transaction signing is only the first layer. A useful privacy integration also needs a coherent answer for credential generation, note ownership, proof construction, backup, and recovery.

The project starts with existing Keycard hardware and the established Kohaku CLI and viem interfaces. It avoids designing a new wallet, inventing a privacy protocol, or claiming that a hardware-held Ethereum key automatically protects a privacy note. The long-term outcome is a **reusable, evidence-backed way to use hardware for Ethereum execution and—where the protocol permits it—reproducible privacy credentials**.

The work is organized into completed milestones and separate future research tracks:

| Phase | Question | Outcome or target |
| --- | --- | --- |
| **V1 — Hardware Signer Integration** | Can Keycard sign through a viem-compatible interface? | **Complete.** Physical signing and randomized ECDSA findings. |
| **V2 — Hardware Transaction Execution** | Can Keycard authorize real Sepolia transactions? | **Complete.** EIP-1559 and EIP-7702/ERC-4337 execution. |
| **V3 — Privacy Pools V1** | Can Keycard support recoverable privacy notes? | **Complete.** Deposit, withdrawal, recovered change note and second verified simulation. |
| **V3 — Tornado Cash** | Can hardware-derived credentials support Tornado notes? | **Planned.** |
| **V3 — RAILGUN** | Can hardware support RAILGUN's distinct key model? | **Future research.** |
| **V4 — Keycard Shell** | Can sensitive privacy operations be isolated from a computer? | **Planned feasibility research.** |

## Motivation

A standard hardware wallet protects an Ethereum private key against direct export. Privacy systems typically involve *different* secrets: note preimages, viewing keys, spending credentials, nullifier material, and proving inputs. Those secrets may be generated, derived, backed up, and used differently from the public Ethereum account key.

This creates three distinct questions:

1. **Authorization:** Can a card authorize the exact operation the user reviewed, without exporting the Ethereum signing key?
2. **Credential custody and recovery:** Can the same privacy credential be reproduced following application restart, device re-pairing, or supported backup recovery, without depending on randomized signatures?
3. **Privacy and proof boundary:** Which inputs and secrets remain on a device, which necessarily reach the host or prover, and what metadata can be correlated on-chain or over the network?

The project treats these as separate claims requiring separate evidence.

## Design principles

**Reuse the ecosystem.** Prefer viem account APIs, existing Keycard firmware interfaces, Kohaku's actual Privacy Pools integration and existing protocol keystores. Maintain compatibility with software-signing paths rather than replacing them.

**Measure before building.** Hardware and cryptographic API support must be demonstrated with actual firmware, reproducible vectors, and negative tests before a wallet integration is proposed.

**Keep review and signing separate.** The host prepares a structured operation; the user approves it; the card signs the digest; the CLI validates the resulting signature; submission and independent receipt verification follow. Host-side approval is not equivalent to an independent trusted-display check.

**Make recovery a prerequisite.** Never create persistent testnet privacy notes or promise cross-device recovery until deterministic derivation and note recovery have been independently demonstrated.

**Scope evidence precisely.** Testnet execution does not establish mainnet suitability. Ethereum signing-key isolation does not establish privacy-note key isolation, unlinkability, or safe ZK proving.

## System boundaries

```text
Kohaku CLI / Ethereum execution
  transaction intent -> chain/nonce/fee checks -> human review
      -> viem account -> Keycard bridge -> APDU signing
      -> signature verification -> bundler / Ethereum RPC
      -> on-chain receipt -> persistent operation journal

V3 — Privacy Pools V1 (verified)
  Keycard 4.0 -> BIP-85 -> volatile host credential derivation
      -> Privacy Pools V1 -> Groth16 -> Sepolia
      -> hardware recovery -> second proof simulation

V3 — Tornado Cash / RAILGUN (not implemented)
  independent credential, recovery and protocol research

V4 — Keycard Shell (planned)
  Shell-contained derivation and controlled outputs
  witness isolation and ZK proving remain unverified
```

The card, host, RPC, bundler, privacy SDK and proving system are separate trust boundaries. [Architecture](docs/ARCHITECTURE.md) and [Threat model](docs/THREAT-MODEL.md) define those boundaries in more detail.

## V1 — Hardware Signer Integration (complete)

**Objective:** Prove the signing backend and determine whether ordinary Keycard signatures can be used for recoverable privacy credentials.

**Evidence:** A retail Keycard with applet 3.1 and an OMNIKEY reader produced verifiable EIP-191, EIP-712, EIP-1559, EIP-7702, and Simple7702 ERC-4337 signatures through a viem-compatible signer. The V1 integration checkpoint passed **538 tests** with no RPC submission for the offline UserOperation test.

**Finding:** Native ECDSA uses randomized signing nonces. Therefore, identical message digests need not yield identical signature bytes; signature-byte-derived Privacy Pools credentials were not established. Do not claim recovery from this signing mechanism.

**Boundary:** The original V1 proposal also anticipated live Sepolia execution. That criterion was not completed during the offline V1 milestone and was subsequently satisfied in V2. V1's historical results are not retroactively rewritten.

Read [V1 outcome](docs/V1-OUTCOME.md), [original V1 proposal](docs/V1-PROPOSAL.md), and [experimental findings](docs/RESEARCH-FINDINGS.md).

## V2 — Hardware Transaction Execution (complete)

**Objective:** Use one physical Keycard to sign an EIP-1559 transaction and execute a two-call EIP-7702 / ERC-4337 UserOperation with intentional user approval, verified receipts and recoverable submission state.

**Result: demonstrated.** A physical Keycard signed the EIP-7702 authorization and ERC-4337 operation. The two-call UserOperation succeeded on Sepolia; the EntryPoint event and installed delegation were independently checked. The journal was reconciled to `confirmed` and later integration tests verified automatic reconciliation and failure handling without sending transactions again.

**Release evidence:**

- Frozen implementation tag: [`kohaku-key-v2-sepolia-poc`](https://github.com/0xterricola/kohaku-cli/tree/kohaku-key-v2-sepolia-poc)
- Final implementation commit: `b97685e` on `0xterricola/kohaku-cli:feat/v2-device-session`
- Regression tests: **647 passing**, TypeScript typecheck and build passing at the tagged checkpoint
- Verified Sepolia transaction: [`0xf243d837…aeed3282`](https://sepolia.etherscan.io/tx/0xf243d837e507b6b1365b3f99424d40a7e8146648cf440cac1b3f65b7aeed3282)
- UserOperation hash: `0xea69d1531960e45aaf74709ee329a88545c6bb0f55abac820d150d3283f7e944`
- Block: `12052649`; actual UserOperation gas cost: `418717528912422` wei
- Implementation evidence: [`docs/KEYCARD-SEPOLIA-V2.md`](https://github.com/0xterricola/kohaku-cli/blob/kohaku-key-v2-sepolia-poc/docs/KEYCARD-SEPOLIA-V2.md)

**Security scope:** Card PIN entry and identity checks, two distinct signature approvals, chain/nonce/delegation validation, calldata binding, final submission approval, journal-first transmission and receipt reconciliation were exercised. A malicious host, trusted on-device display, real crash/restart recovery and production audit remain outside the demonstrated guarantees.

Read [V2 outcome](docs/V2-OUTCOME.md), [testnet evidence](docs/V2-TESTNET-RESULTS.md), and [V2 security model](docs/V2-SECURITY-MODEL.md).

## V3 — Privacy Pools V1 (complete)

Physical Keycard 4.0 BIP-85 credentials supported a real Sepolia deposit, independently verified Groth16 withdrawal, hardware-signed partial withdrawal, fresh change-note recovery and a second verified withdrawal simulation.

The second withdrawal was not broadcast. The BIP-85 root and private proving inputs entered host memory; this does not demonstrate host isolation or withdrawal unlinkability.

**Evidence:** [V3 — Privacy Pools V1 final research report](docs/V3-FINAL-RESEARCH-REPORT.md).

## V3 — Additional privacy protocols

**Tornado Cash (planned):** Hardware-derived note credentials, independent recovery and Pedersen commitment verification, starting with offline tests.

**RAILGUN (future):** Separate spending/viewing credentials, recovery and proving feasibility. Privacy Pools compatibility cannot be assumed.

## V4 — Keycard Shell (planned)

Evaluate Shell-contained credential derivation, stateless recovery and private computation limits. Shell-isolated witnesses and Groth16 proving remain unverified.

[Shell architecture draft](docs/V4-KEYCARD-SHELL-ARCHITECTURE-DRAFT.md).

## Repositories and collaboration

- **Research and roadmap:** [`0xterricola/kohaku-key`](https://github.com/0xterricola/kohaku-key) — experiment records, architecture, findings and proposals.
- **Implementation fork:** [`0xterricola/kohaku-cli`](https://github.com/0xterricola/kohaku-cli) — the tagged V2 proof of concept and integration tests.
- **Upstream project:** [`kassandraoftroy/kohaku-cli`](https://github.com/kassandraoftroy/kohaku-cli) — integration decisions belong to upstream maintainers.
- **Prior staged contributions:** [#67](https://github.com/kassandraoftroy/kohaku-cli/pull/67), [#68](https://github.com/kassandraoftroy/kohaku-cli/pull/68), [#69](https://github.com/kassandraoftroy/kohaku-cli/pull/69). Their current review/merge state must be checked separately.

This repository does not assume the V2 feature branch has been accepted upstream. Research can proceed independently, with focused, reviewable contributions proposed when appropriate.

## Documentation and reproducibility

[Documentation index](docs/DOCUMENTATION-INDEX.md) | [Current project status](docs/PROJECT-STATUS.md) | [Hardware compatibility](docs/HARDWARE-COMPATIBILITY.md) | [Research findings](docs/RESEARCH-FINDINGS.md) | [Reproducibility](docs/REPRODUCIBILITY.md) | [Security and recovery](docs/SECURITY-AND-RECOVERY.md)

No PINs, mnemonics, private keys, private notes, or credential material belong in this repository. Preserve the original V1/V2 plans as historical decisions; use outcome and status documents for current claims.

## Research checkpoints

- [V3 research checkpoint — November 4, 2026](docs/V3-2026-11-04-RESEARCH-CHECKPOINT.md)
- [Keycard Shell architecture draft](docs/V4-KEYCARD-SHELL-ARCHITECTURE-DRAFT.md)
