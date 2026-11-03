# Kohaku Key — V1 Outcome: Offline Signing Feasibility

**Milestone:** Completed as an *offline hardware-signing prototype* (November 2, 2026).
**Historical qualification:** The original V1 plan also requested a live Sepolia transaction; that acceptance was deferred and demonstrated in V2. V1 results below are not being retroactively reclassified as live tests.

## Objective and method

Use a retail Keycard as a viem-compatible Ethereum signer while probing whether signatures could also yield reproducible Privacy Pools credentials. Verify signatures on host, run offline transaction and UserOperation tests, and preserve software-signing compatibility.

## Verified results

- Retail Keycard applet 3.1 through an HID OMNIKEY reader; account `m/44'/60'/0'/0/0`.
- EIP-191 messages, EIP-712 typed data, EIP-1559 transactions and EIP-7702 authorizations.
- Offline Simple7702 ERC-4337 UserOperation signing through Kohaku CLI.
- Signer recovery and payload validation without exporting the private key.
- V1 checkpoint `4c7aa87` on `feat/keycard-7702-userop`: **538 tests passing**, typecheck/build passing.

No online UserOperation was submitted during these **V1 offline** experiments.

## Privacy findings

Native ECDSA on the tested card uses a randomized nonce. Signature bytes are therefore not a stable credential-derivation source. Earlier experiments were also affected by a legacy SDK signature parser issue; the underlying nonce limitation remains. Deterministic Privacy Pools credential reconstruction was **not demonstrated**.

## Deferrals and later work

The V1 live-transaction objective, interactive PIN/device lifecycle and confirmed on-chain delegation were subsequently pursued under V2 and verified as a Sepolia proof of concept. Cross-device private-note recovery and on-device transaction display remain unresolved. See [V2 outcome](V2-OUTCOME.md) and [V3 proposal](V3-PROPOSAL.md).

## Upstream contribution references

[Kohaku CLI #67](https://github.com/kassandraoftroy/kohaku-cli/pull/67), [#68](https://github.com/kassandraoftroy/kohaku-cli/pull/68), [#69](https://github.com/kassandraoftroy/kohaku-cli/pull/69); [Keycard Go #20](https://github.com/keycard-tech/keycard-go/pull/20). Review and release status are separate from the local V1 outcome.
