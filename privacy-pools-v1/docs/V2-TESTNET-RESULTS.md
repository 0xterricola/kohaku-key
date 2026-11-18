# Kohaku Key — V2 Testnet Evidence

**Status:** Confirmed on Ethereum Sepolia (chain ID 11155111).
**Evidence source:** Physical Keycard execution logs, independent receipt/Event verification, and local reconciliation.
**Implementation:** `0xterricola/kohaku-cli` tag `kohaku-key-v2-sepolia-poc` at `b97685e`.

## Device and architecture

- Physical retail Keycard (applet 3.1) and HID OMNIKEY reader; native Keycard bridge and interactive PIN.
- Ethereum account `0xB8A0f79E6d64c948E9F5ea32aD93647777915EBa`, derivation `m/44'/60'/0'/0/0`.
- Target implementation `0xe6Cae83BdE06E4c305530e199D7217f42808555B`.
- ERC-4337 EntryPoint v0.8 `0x4337084D9E255Ff0702461CF8895CE9E3b5Ff108`.
- Sepolia JSON-RPC: PublicNode; bundler used through Kohaku CLI's configured execution pipeline.

## Experiment A — EIP-1559 physical signing and broadcast

- Status: confirmed on Sepolia.
- Transaction: `0x95a1180a5c24f295cfe3d582f189527ddc30a02b9a2af4319ceadba460d4939f`.
- Block: `12051290`.
- From account: `0xB8A0f79E6d64c948E9F5ea32aD93647777915EBa`.
- Physical signing and subsequent receipt verification succeeded in the V2 development record. This document does not invent unrecorded gas or recipient fields.

## Experiment B — Two-call EIP-7702/ERC-4337 execution

- Status: **independently verified successful execution**.
- Calls: `0x000000000000000000000000000000000000dEaD` and `0x000000000000000000000000000000000000bEEF`, each with empty calldata and zero transferred wei.
- Pending EOA nonce before delegation: `1`.
- UserOperation nonce: `33087497432550682333706331357184`.
- Physical Keycard signed EIP-7702 authorization and ERC-4337 UserOperation after separate explicit approvals.
- UserOperation: `0xea69d1531960e45aaf74709ee329a88545c6bb0f55abac820d150d3283f7e944`.
- Transaction: [`0xf243d837e507b6b1365b3f99424d40a7e8146648cf440cac1b3f65b7aeed3282`](https://sepolia.etherscan.io/tx/0xf243d837e507b6b1365b3f99424d40a7e8146648cf440cac1b3f65b7aeed3282).
- Transaction block `12052649`, receipt `success`, matching EntryPoint event `success = true`.
- EIP-7702 delegation code verified against the expected implementation address.
- Gas limit displayed before submission: `435421`; maximum fee approved: `502911256306263` wei.
- Actual UserOperation gas cost: `418717528912422` wei (not the maximum displayed fee).

## Recovery and lifecycle validation

- A journal record for this exact UserOperation was durably written to `~/.kohaku-cli/keycard-sepolia-userops` before broadcasting with directory permissions `0700` and file `0600`.
- The journal originally recorded `outcome-unknown` and was independently reconciled from the matching on-chain receipt/event to `confirmed`.
- Duplicate **same-hash** submissions, wrong event sender/hash, reverted execution and wrong chain are covered by regression tests.
- Automatic post-success reconciliation and reconciliation-failure behavior were added and validated with mocked receipts **after** the physical demonstration.
- A real forced process crash/restart was not performed; no claim of cross-nonce duplicate prevention is made.

## Validation checkpoint

- Implementation commit `b97685e`.
- **647 tests passed**, 0 failed; TypeScript typecheck and production build passed.
- Final milestone tag published, repository clean and synchronized.

Do not attach PINs, secret material, private note data, raw credentials or signing-key backups to public issue discussions.
