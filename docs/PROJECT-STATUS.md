# Kohaku Key — Project Status

Updated: November 2, 2026

## Overview

Kohaku Key is a hardware-signer integration project for
Kohaku CLI, using Keycard hardware and viem custom accounts.

The objective is to perform Ethereum signing without
exporting private keys or requiring Kohaku's software
mnemonic for hardware-backed transaction execution.

## Upstream contributions

### Keycard Go #20 — Fix commit verified; upstream inclusion needs recheck

https://github.com/keycard-tech/keycard-go/pull/20

Fixed legacy ECDSA signature buffer aliasing in
`types/signature.go` within `calculateV()`.

Original:

    rs := append(r, s...)

Fixed:

    rs := append(append([]byte{}, r...), s...)

A regression test reproduced corruption of the original
S component. The test failed before the fix and passed
afterward. The full Go test suite passed.

The fix was independently verified using physical Keycard
hardware: ECDSA verification and Ethereum address recovery
both succeeded.

Fix commit `c4cf5cc` exists in the upstream repository.
A November 2 public-source check showed PR #20 as open
and `develop/types/signature.go` retaining the old append
expression. Confirm the current upstream branch state
before asserting that the fix is included in a release.

### Kohaku CLI #67 — External viem signers

https://github.com/kassandraoftroy/kohaku-cli/pull/67

Introduces signer injection into Ethereum and EIP-7702
execution utilities while retaining the software-key path.

The refactor does not by itself enable hardware selection
in CLI commands.

### Kohaku CLI #68 — Keycard integration

https://github.com/kassandraoftroy/kohaku-cli/pull/68

Stacked on #67.

Adds a TypeScript Keycard-backed viem account, physical
hardware integration tests, and an offline Keycard mode
in `transact-raw`.

PR #68 hardware mode (extended by #69):

- `--signer keycard`
- EIP-1559 signing only
- Explicit chain ID, nonce, gas, and fee parameters
- Chain ID 31337 only
- One transaction per invocation
- No mnemonic unlock or private-key derivation
- No RPC or broadcast in the offline signing path

### Kohaku CLI #69 — Offline Simple7702 UserOperations

https://github.com/kassandraoftroy/kohaku-cli/pull/69

Stacked on #68, which depends on #67.

Implements `transact-raw --signer keycard --keycard-userop`
for two or more calls, with explicit nonce and gas parameters.

- Reuses the Keycard-backed viem account
- Encodes a Simple7702 batch through viem
- Signs an ERC-4337 UserOperation on physical Keycard
- Uses development chain 31337 only
- Does not unlock a software mnemonic
- Does not initialize RPC or bundler submission
- Does not broadcast or activate delegation
- Does not generate a delegation authorization in this CLI path

Physical two-call signing, signature recovery, chain-binding
verification, and the zero-RPC boundary were tested.

Incremental branch commits:
`9da4fdf`, `42b29e8`, `0fa841d`, `4c7aa87`.

## Tested hardware and software

- Retail Keycard, applet 3.1
- HID Global OMNIKEY 3x21 reader
- Keycard CLI 4.0.0, locally built with corrected SDK
- viem 2.55.19
- Node.js 22.23.4
- Ethereum derivation path: m/44'/60'/0'/0/0

Keycard Shell and newer applet versions have not been
validated in these experiments.

## Verified signing capabilities

| Capability | Result |
| --- | --- |
| Public-key and address discovery | PASS |
| EIP-191 UTF-8 message | PASS |
| EIP-191 raw-byte message | PASS |
| EIP-712 typed data | PASS |
| EIP-1559 serialized transaction | PASS |
| EIP-7702 authorization | PASS |
| Simple7702 ERC-4337 UserOperation | PASS (offline) |
| Kohaku CLI offline transaction command | PASS |
| Kohaku CLI offline Simple7702 batch command | PASS |
| Live transaction broadcast | NOT TESTED |
| Live bundler execution | NOT TESTED |

The Simple7702 UserOperation test exercised viem's
hardware-backed signing delegation offline. It is not yet
integrated into Kohaku CLI's live UserOperation submission.

## Validation

Kohaku CLI:

- 538 total regression tests passing
- 525 existing TypeScript tests plus 13 JavaScript tests
- Offline UserOperation signing and CLI safety regressions included
- TypeScript typecheck passing
- Production build passing
- Physical Keycard integration passing

CLI safety tests reject broadcasting, incompatible
software-wallet options, missing chain ID, and unknown
signer backends.

No network transaction was submitted.

## V1 acceptance status

The offline hardware-signing research milestone is complete.

The original V1 proposal required a successful
Keycard-signed Sepolia transaction broadcast.
That end-to-end acceptance criterion remains unmet.

The original Privacy Pools credential-recovery investigation
also did not establish deterministic signature-derived recovery.
Randomized native ECDSA prevents relying on signature bytes
as a persistent deterministic secret.

See [V1 Outcome](V1-OUTCOME.md) for the distinction
between completed prototype work and remaining acceptance.

## Repository structure

- `src/keycard-account.mjs`: research viem account adapter
- `scripts/verify-keycard-account.mjs`: EIP-191 tests
- `scripts/verify-keycard-typed-data.mjs`: EIP-712 tests
- `scripts/verify-keycard-transaction.mjs`: EIP-1559 tests
- `scripts/verify-keycard-authorization.mjs`: EIP-7702 tests
- `scripts/verify-keycard-user-operation.mjs`: Simple7702 tests
- `docs/EXPERIMENT-002.md`: SDK defect investigation
- `docs/V1-PROPOSAL.md`: original implementation proposal
- `docs/V1-OUTCOME.md`: verified V1 outcome and acceptance status

The Kohaku CLI TypeScript implementation lives in
the separate `0xterricola/kohaku-cli` fork.

## Next milestones

1. Address upstream review feedback on #67, #68, and #69.
2. Verify Keycard Go #20 inclusion in upstream branch and official release.
3. Replace environment-variable PIN handling.
4. Add informed transaction approval and device lifecycle safeguards.
5. Validate Keycard Shell independently.
6. Implement network-backed preparation, authorization, and delegation validation.
7. Verify testnet execution, receipt handling, and recovery before production use.
