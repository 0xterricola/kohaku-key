# Kohaku Key — Project Status

**As of:** November 2, 2026
**Current phase:** V3 research definition
**Status authority:** This file and the root [README](../README.md); prior proposals and interim evidence are historical snapshots.

| Phase | Status | Accepted result | Primary evidence |
| --- | --- | --- | --- |
| V1 — Offline signing feasibility | Completed as offline prototype | Physical Keycard signing, viem account integration, 538 passing tests; randomized ECDSA cannot supply stable signature bytes | [V1 outcome](V1-OUTCOME.md) |
| V2 — Secure Sepolia execution | **Completed as proof of concept** | Physical EIP-1559 and two-call ERC-4337 execution via EIP-7702, confirmation, journaling and reconciliation; 647 tests | [V2 outcome](V2-OUTCOME.md), [testnet evidence](V2-TESTNET-RESULTS.md) |
| V3 — Privacy protocols | **Research proposed / not yet demonstrated** | Establish BIP-85 and ECDH capabilities, recovery and Privacy Pools compatibility; RAILGUN feasibility afterward | [V3 proposal](V3-PROPOSAL.md), [roadmap](V3-ROADMAP.md) |

## Frozen V2 checkpoint

- Research code lives in a separate fork: https://github.com/0xterricola/kohaku-cli
- Branch: `feat/v2-device-session`; commit: `b97685e`
- Annotated tag: `kohaku-key-v2-sepolia-poc`
- Verified transaction: https://sepolia.etherscan.io/tx/0xf243d837e507b6b1365b3f99424d40a7e8146648cf440cac1b3f65b7aeed3282
- Matching successful ERC-4337 event and on-chain EIP-7702 delegation verified; journal `confirmed`.
- 647 tests passing, TypeScript typecheck passed, build passed; clean tree at freeze.

The live demonstration and manual journal reconciliation were successful. Later automatic reconciliation was validated in mocked tests; a real forced-process-crash recovery exercise was not performed.

## Scope boundaries

The Ethereum account key remains on the physical device during hardware signing; this does **not** mean privacy note secrets or proof-generation material remain on hardware. Host-side transaction review is not a trusted device display. Testnet validation and a release tag do not imply production security, upstream merge, or official SDK distribution.

## Research dependencies and upstream work

Earlier Kohaku CLI contributions: [#67](https://github.com/kassandraoftroy/kohaku-cli/pull/67), [#68](https://github.com/kassandraoftroy/kohaku-cli/pull/68), [#69](https://github.com/kassandraoftroy/kohaku-cli/pull/69). The Keycard Go legacy parser investigation is [#20](https://github.com/keycard-tech/keycard-go/pull/20). Verify current upstream status before representing any as merged or released.

## Immediate next work

1. Establish protocol-specific Privacy Pools credential and recovery requirements.
2. Test actual applet 3.1 BIP-85 and applet 4.0 ECDH availability, outputs and repeatability.
3. Make a go/no-go decision on a recoverable adapter before any privacy pool funding.
4. Map RAILGUN requirements independently after the initial Privacy Pools feasibility result.
