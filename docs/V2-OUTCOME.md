# Kohaku Key — V2 Outcome: Secure Hardware-Backed Ethereum Execution

**Status:** Completed as a Sepolia proof of concept (November 2, 2026).
**Tag:** [`kohaku-key-v2-sepolia-poc`](https://github.com/0xterricola/kohaku-cli/tree/kohaku-key-v2-sepolia-poc) at `b97685e`.
**Not claimed:** Production security, upstream merge, mainnet readiness, real forced-crash restart testing or privacy-credential isolation.

## Goal

Take V1's offline viem-compatible Keycard signer through an end-to-end physical testnet flow: reviewed transaction intent, secure device interaction, EIP-1559 execution, EIP-7702 authorization, two-call ERC-4337 UserOperation, confirmation, and conservative recovery.

## Acceptance and evidence

| Original V2 scope | Verified PoC outcome |
| --- | --- |
| Physical card identity, interactive PIN and signing | Physical retail Keycard used for real signing; expected address recovered |
| EIP-1559 execution on Sepolia | Confirmed in transaction `0x95a1180a5c24f295cfe3d582f189527ddc30a02b9a2af4319ceadba460d4939f` (block 12051290) |
| EIP-7702 delegation policy | Supported delegate verified; on-chain delegation installed and checked |
| Two reviewed ERC-4337 calls | Two zero-value calls, both signed through the physical card flow and executed in one UserOperation |
| Actual execution and receipts | Successful Sepolia transaction, matching EntryPoint event, correct sender and UserOperation hash |
| Journal and recovery | Journal persisted before send; actual record reconciled to `confirmed`; unknown outcomes block repeated same-hash submission |
| Automated reconciliation | Mock-tested in successful and failure scenarios after the live demonstration; **no physical crash/restart drill** |
| Regression and release checkpoint | **647 tests**, TypeScript typecheck/build pass; tag pushed and working tree clean |

## Chain evidence

- Owner: `0xB8A0f79E6d64c948E9F5ea32aD93647777915EBa`
- Implementation: `0xe6Cae83BdE06E4c305530e199D7217f42808555B`
- EntryPoint v0.8: `0x4337084D9E255Ff0702461CF8895CE9E3b5Ff108`
- UserOp: `0xea69d1531960e45aaf74709ee329a88545c6bb0f55abac820d150d3283f7e944`
- Tx: [`0xf243d837e507b6b1365b3f99424d40a7e8146648cf440cac1b3f65b7aeed3282`](https://sepolia.etherscan.io/tx/0xf243d837e507b6b1365b3f99424d40a7e8146648cf440cac1b3f65b7aeed3282)
- Block: `12052649`; `UserOperationEvent.success = true`; cost `418717528912422` wei.

## Security boundaries

The hardware signs host-provided digests. Host prompts, nonce/delegation checks and calldata/digest binding reduce accidental and some malicious changes but do not provide a trusted hardware screen. Privacy-note secrets and ZK proving are beyond V2. Unknown broadcasts must be reconciled before any manual retry; new nonces can produce distinct operations and require independent review.

## Conclusion

**V2's defined Sepolia proof-of-concept milestone was met.** Preserve the frozen tag and use [V3](V3-PROPOSAL.md) for separate privacy research. See [testnet results](V2-TESTNET-RESULTS.md) and the tagged CLI [release notes](https://github.com/0xterricola/kohaku-cli/blob/kohaku-key-v2-sepolia-poc/docs/KEYCARD-SEPOLIA-V2.md).
