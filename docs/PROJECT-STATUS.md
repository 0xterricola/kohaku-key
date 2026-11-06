# Kohaku Key — Project Status

**Updated:** November 5, 2026

**Current phase:** V3 Privacy Pools V1 research completed. Additional V3 protocol integrations and V4 Shell feasibility remain separate research tracks.

This is the authoritative status document. The README summarizes current milestones; historical proposals and interim checkpoints retain their original research context.

## Milestone overview

| Track | Status | Result or objective |
| --- | --- | --- |
| **V1 — Hardware Signer Integration** | **Complete** | Physical Keycard signing through viem-compatible interfaces; randomized ECDSA behavior established |
| **V2 — Hardware Transaction Execution** | **Complete — Sepolia PoC** | Physical EIP-1559 and EIP-7702/ERC-4337 execution with approvals and receipt verification |
| **V3 — Privacy Pools V1** | **Complete — scoped research PoC** | Real deposit, Groth16 withdrawal, on-chain execution, fresh hardware recovery and second withdrawal simulation |
| **V3 — Tornado Cash** | **Planned** | Hardware-derived note credentials, deterministic recovery and Pedersen commitment compatibility |
| **V3 — RAILGUN** | **Future research** | Spending/viewing credentials, recovery and protocol-specific proving requirements |
| **V4 — Keycard Shell** | **Planned — feasibility PoC** | Shell-contained credential derivation, recovery and evaluation of ZK computation limits |

These milestones are independent research results, not claims of upstream acceptance, mainnet readiness or an independent security audit.

## V1 — Hardware Signer Integration

**Complete.**

A physical retail Keycard provided verifiable Ethereum signatures through a viem-compatible integration.

The V1 checkpoint included 538 passing tests. Native ECDSA signing was observed to use randomized nonces, making signature bytes unsuitable as a universally deterministic privacy-credential source.

[Verified V1 outcome](V1-OUTCOME.md)

## V2 — Hardware Transaction Execution

**Complete — Sepolia proof of concept.**

Physical Keycard hardware authorized Ethereum execution using EIP-1559, EIP-7702 and ERC-4337 workflows.

The implementation demonstrated guarded approval, transaction verification, controlled submission, receipt reconciliation and a frozen 647-test checkpoint.

- Implementation: `0xterricola/kohaku-cli`
- Frozen tag: `kohaku-key-v2-sepolia-poc`
- Checkpoint: `b97685e`
- [V2 outcome](V2-OUTCOME.md)
- [Sepolia results](V2-TESTNET-RESULTS.md)

The tested host approval flow is not a trusted hardware display. A real forced-crash recovery drill and compromised-host resistance were not demonstrated.

## V3 — Privacy Pools V1

**Complete — November 5, 2026.**

The research integrated a physical experimental Keycard running applet 4.0 with Privacy Pools V1 using BIP-85 and a versioned credential adapter.

### Verified lifecycle

1. A real **0.002 Sepolia ETH deposit** created a **0.00198 ETH** note after the protocol fee.
2. Hardware-recovered credentials generated an independently verified Groth16 withdrawal proof.
3. The physical Keycard signed an approved **0.00099 ETH partial withdrawal**, confirmed on Sepolia.
4. Fresh authenticated Keycard sessions independently recovered the resulting change note.
5. An updated LeanIMT witness verified the change note against on-chain state.
6. A second Groth16 withdrawal proof was independently verified and accepted in simulation by two RPC providers.

The second withdrawal was **not signed or broadcast**. The remaining 0.00099 ETH note was not spent by that simulation.

**Primary evidence:** [V3 — Privacy Pools V1 final research report](V3-FINAL-RESEARCH-REPORT.md).

**Implementation:** `kohaku-cli`, branch `research/v3-r5e5b9k-deposit-integration`, checkpoint `9a2a285`.

**Published report checkpoint:** `58d8579` in `kohaku-key`.

### Compatibility boundaries

The research used a versioned BIP-85/HMAC credential adapter with the Privacy Pools V1 legacy `SecretManager`.

It does not automatically reproduce the newer signature-derived `SignatureSecretManager` credentials or legacy HD-derived wallet credentials.

The BIP-85 root entered host memory. Credential reconstruction, private witness generation and Groth16 proving also occurred on the host.

The demonstrated direct withdrawal exposed account linkage. The research establishes V1 interoperability and recovery, not unlinkability or resistance to a compromised host.

## V3 — Tornado Cash

**Planned.**

Start with synthetic, offline experiments covering hardware-backed note derivation, independent recovery, Pedersen commitments and compatibility with the actual Tornado Cash SDK.

No Tornado Cash deposit, withdrawal or hardware-backed note lifecycle has been demonstrated in this project.

## V3 — RAILGUN

**Future research.**

Investigate RAILGUN's distinct spending/viewing credentials, key derivation, note lifecycle, recovery and proving boundary.

Privacy Pools results do not establish RAILGUN compatibility.

## V4 — Keycard Shell

**Planned — feasibility research.**

Investigate whether Keycard-to-Shell communication can keep BIP-85-derived credential material out of computer memory.

Reproduce the frozen V3 credential contract inside Shell, then evaluate private witness construction and native Groth16 proving against the actual hardware limits.

No Kohaku-specific Shell credential implementation or Shell-generated Groth16 proof has been verified.

[Shell architecture draft](V4-KEYCARD-SHELL-ARCHITECTURE-DRAFT.md)

## Transaction and upstream evidence references

- **V2 Sepolia ERC-4337 execution:** [Verified transaction](https://sepolia.etherscan.io/tx/0xf243d837e507b6b1365b3f99424d40a7e8146648cf440cac1b3f65b7aeed3282).
- **V3 Sepolia deposit and withdrawal:** Transaction hashes, block numbers, amounts and cryptographic verification are documented in the [final research report](V3-FINAL-RESEARCH-REPORT.md).
- **Earlier Kohaku CLI contributions:** [PR #67](https://github.com/kassandraoftroy/kohaku-cli/pull/67), [PR #68](https://github.com/kassandraoftroy/kohaku-cli/pull/68) and [PR #69](https://github.com/kassandraoftroy/kohaku-cli/pull/69).
- **Keycard Go parser investigation:** [PR #20](https://github.com/keycard-tech/keycard-go/pull/20).

Upstream merge and release status must be verified separately; these references do not imply acceptance.

## Repository responsibilities

- **kohaku-key:** Research design, architecture, security analysis, hardware experiments and evidence.
- **kohaku-cli:** Executable integrations, transactions, Groth16 proving and regression tests.
- **kohaku-sdk-research:** Supporting protocol SDK and credential research.

Historical proposals and dated checkpoints must not override the results in this document.

## Security and release status

**Research proof of concept.**

No independent security audit, universal hardware compatibility, approved upstream release or supported mainnet deployment is asserted.

[Architecture](ARCHITECTURE.md) | [Hardware compatibility](HARDWARE-COMPATIBILITY.md) | [Security and recovery](SECURITY-AND-RECOVERY.md) | [Threat model](THREAT-MODEL.md)
